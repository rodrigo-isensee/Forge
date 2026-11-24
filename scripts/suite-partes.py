#!/usr/bin/env python3
"""Forge: uma parte da suíte em paralelo, sobre o mecanismo de `scripts/suite-paralela.py` (D4), sem mudá-lo.

Uso: python3 scripts/suite-partes.py --modulos M[,M...]
     python3 scripts/suite-partes.py --parte K/N
     python3 scripts/suite-partes.py --somar-pulados N PASTA
     python3 scripts/suite-partes.py --duas-partes
  --modulos M   roda só esses módulos de tests/ (os testes afetados de um envio; `evals.test_x` é o de um pacote,
                tests/evals/test_x.py) em até 4 processos: a mesma regra de
                N, a mesma LPT sobre tests/pesos-d4.json, os mesmos filhos (`suite-paralela.py --processo`) e a mesma
                guarda de completude, aqui contra o discover desses módulos. Não pega a trava: quem chama (o pre-push)
                já a tem.
  --parte K/N   (só no CI, com CI definido) a parte K de N da suíte inteira. As UNIDADES da suíte (as do
                `suite-paralela.planejar`: `módulo`, `módulo.Classe` ou `módulo.Classe.teste`, conforme as chaves de
                tests/pesos-d4.json) são divididas em N partes por LPT sobre os pesos (a mesma árvore dá a mesma divisão
                em todos os jobs); entram também os módulos dos pacotes de tests/, que o discover acha e o
                suite-paralela ainda não divide. Falha fechada (CI-RAPIDO, S9): a divisão cobre toda unidade uma vez só,
                todo teste do discover da suíte inteira cai numa unidade da divisão (por ID) e a parte roda exatamente
                os IDs do discover que são dela. Com as N partes verdes, a suíte inteira passou; o job agregador do CI
                (`bateria`, `bateria (python 3.14)`, `checagem rápida (push na develop...)`) exige as N. Com
                FORGE_SUITE_PULADOS=<arquivo>, a parte verde grava nele os pulados dela (T3: `{"parte": "K/N",
                "pulados": n, "pulados_ids": [...]}`). Com GITHUB_ACTIONS=true, a parte verde grava o tempo de cada
                unidade em anotação do check run (`::notice title=forge-tempos K/N ...`, só nomes de unidade e
                segundos), que `scripts/pesos-do-ci.py` lê pela API.
                Com GITHUB_ACTIONS=true, a parte vermelha imprime uma anotação `::error title=forge-suite parte K/N::...`
                com o tipo, o ID e o local de cada teste que caiu (as causas tipadas do suite-paralela) e os erros da
                guarda: a causa fica legível nas anotações do check run, sem abrir o log.
  --somar-pulados N PASTA  (o agregador do CI) soma os pulados das N partes gravados em PASTA (`*.json`, um por parte,
                K de 1 a N uma vez só) e compara com `teto_pulados` de tests/config.json, com a conta do suite-paralela
                (T3). Falha fechada: parte faltando, repetida, de outro N, arquivo ilegível ou teto ilegível reprova.
  --duas-partes (à mão, E4.1 da 0.45.7, R-TETO) a suíte inteira em 2 partes (`--parte 1/2` e `--parte 2/2`): em paralelo
                só com folga na hora (load1 < nproc e memória disponível acima do piso, `piso_memoria_gb`, padrão 2
                GB); sem folga, ou sem medida, uma depois da outra. Verde só com as duas verdes.
Só biblioteca padrão. A última linha é `OK` (ou `OK (skipped=N)`) ou `FAILED (...)`, como no `unittest`.
"""
import collections
import importlib.machinery
import importlib.util
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PARALELA = RAIZ / "scripts" / "suite-paralela.py"
PARTE = re.compile(r"([1-9][0-9]?)/([1-9][0-9]?)")
UNIDADE_SEGURA = re.compile(r"[A-Za-z0-9_.]{1,200}")  # S6: só isto sai em anotação (nada de `::`, quebra de linha, `%`)
LIMITE_DA_ANOTACAO = 12000  # caracteres da mensagem de cada anotação (o GitHub aceita 64 KB)
MAXIMO_DE_ANOTACOES = 8  # o GitHub guarda 10 por passo
LIMITE_DE_CAUSAS = 30  # as causas que entram na anotação de falha (o resto fica no log)
TITULO_SEGURO = re.compile(r"[A-Za-z0-9 /_.-]{1,40}")  # o título de um comando de workflow não leva `:` nem `,`
NOME_DE_MODULO = re.compile(r"(?:[a-z0-9_]+\.)*test[a-z0-9_]*")  # `evals.test_x` é tests/evals/test_x.py (pacote)


def carregar_paralela(caminho=PARALELA):
    """O `suite-paralela.py` como módulo (o nome do arquivo tem hífen): as funções dele são o mecanismo."""
    carregador = importlib.machinery.SourceFileLoader("suite_paralela", str(caminho))
    spec = importlib.util.spec_from_loader("suite_paralela", carregador)
    modulo = importlib.util.module_from_spec(spec)
    carregador.exec_module(modulo)
    return modulo


def ler_parte(texto):
    """(K, N) de `K/N`, com 1 <= K <= N; ValueError fora disso."""
    achado = PARTE.fullmatch(texto or "")
    if not achado or not 1 <= int(achado.group(1)) <= int(achado.group(2)):
        raise ValueError(f"--parte espera K/N com 1 <= K <= N (veio '{texto}')")
    return int(achado.group(1)), int(achado.group(2))


def modulo_do_id(ident, nomes):
    """O módulo de `nomes` dono do ID (`test_x.Classe.teste`, `evals.test_x.Classe.teste`): o prefixo mais longo; None
    se nenhum (falha de carga, pasta sem pacote)."""
    partes = ident.split(".")
    for i in range(len(partes) - 1, 0, -1):
        if ".".join(partes[:i]) in nomes:
            return ".".join(partes[:i])
    return None


def fora_da_divisao(total, nomes):
    """IDs do discover cujo módulo não está em `nomes` (falha de carga, por exemplo): nenhuma parte o rodaria."""
    conjunto = set(nomes)
    return sorted(i for i in total if modulo_do_id(i, conjunto) is None)


def todos_os_modulos(sp):
    """Os módulos da raiz de tests/ (os do suite-paralela) mais os dos pacotes de tests/ (pasta com __init__.py, que o
    discover também acha), estes pelo nome com ponto."""
    nomes = set(sp.modulos())
    base = sp.RAIZ / sp.TESTES
    for p in base.rglob("test*.py"):
        pastas = p.parent.relative_to(base).parts
        if not pastas or not all(x.isidentifier() for x in (*pastas, p.stem)):
            continue
        if all((base / Path(*pastas[:i + 1]) / "__init__.py").is_file() for i in range(len(pastas))):
            nomes.add(".".join((*pastas, p.stem)))
    return sorted(nomes)


def para_o_filho(nomes, todos):
    """(nomes do filho, erros). O filho do suite-paralela acha o módulo pelo nome do arquivo (`discover` com o padrão
    `<nome>.py`): o de pacote vai pelo último nome, que tem de ser único entre todos os módulos (falha fechada)."""
    contagem = collections.Counter(m.rsplit(".", 1)[-1] for m in todos)
    erros = [f"nome de arquivo repetido em tests/ e nos pacotes dela: {m}" for m in nomes
             if contagem[m.rsplit(".", 1)[-1]] > 1]
    return [m.rsplit(".", 1)[-1] for m in nomes], erros


def arquivo_do_modulo(sp, nome):
    return sp.RAIZ / sp.TESTES / (nome.replace(".", "/") + ".py")


def unidade_do_id(sp, ident, nomes, pesos, chaves=None):
    """A unidade do plano dona do ID (`módulo`, `módulo.Classe` ou `módulo.Classe.teste`), pela mesma regra do
    `suite-paralela.planejar`; None se nenhum módulo da divisão é dono dele."""
    modulo = modulo_do_id(ident, nomes)
    if modulo is None:
        return None
    chaves = {} if chaves is None else chaves
    if modulo not in chaves:
        chaves[modulo] = sp.separadas(modulo, pesos)
    return sp.unidade_do_teste(ident, chaves[modulo], modulo) if chaves[modulo] else modulo


def esperado_por_unidade(sp, total, nomes, pesos):
    """{unidade: multiconjunto de IDs do discover inteiro que são dela}; a guarda de completude por ID da divisão por
    unidade (CI-RAPIDO, S9). O ID sem módulo na divisão fica fora (`fora_da_divisao` o aponta)."""
    nomes = set(nomes)
    chaves, saida = {}, collections.defaultdict(collections.Counter)
    for ident, quantos in total.items():
        unidade = unidade_do_id(sp, ident, nomes, pesos, chaves)
        if unidade is not None:
            saida[unidade][ident] += quantos
    return dict(saida)


def dividir_por_unidade(sp, nomes, n):
    """(partes, plano, erros): as unidades do plano (as do suite-paralela, pelos pesos) em `n` partes pela LPT, conferidas
    como partição. `plano` é {unidade: (módulo, posições)}; `partes`, listas de unidades."""
    pesos = sp.ler_pesos()
    plano = sp.planejar(nomes, pesos, lambda nome: [t.id() for t in sp.achatar(sp.suite_do_modulo(nome))])
    unidades = sorted(plano)
    partes = sp.repartir(unidades, pesos, n)
    erros = sp.conferir_particao(unidades, partes)
    if len(partes) != n:
        erros.append(f"{len(unidades)} unidades não dão {n} partes não vazias")
    return partes, plano, erros


def completude_da_divisao(sp, total, nomes, plano, partes, pesos=None):
    """Erros da guarda por ID: todo ID do discover cai numa unidade do plano, toda unidade do plano tem testes no discover
    e as partes juntas cobrem exatamente as unidades do plano uma vez (a soma dos esperados é o discover inteiro). `pesos` são
    os que definem as unidades (padrão: os do arquivo)."""
    por_unidade = esperado_por_unidade(sp, total, nomes, sp.ler_pesos() if pesos is None else pesos)
    erros = []
    sem_plano = sorted(set(por_unidade) - set(plano))
    if sem_plano:
        erros.append(f"{len(sem_plano)} unidade(s) do discover fora do plano: {', '.join(sem_plano[:5])}")
    sem_teste = sorted(set(plano) - set(por_unidade))
    if sem_teste:
        erros.append(f"{len(sem_teste)} unidade(s) do plano sem teste no discover: {', '.join(sem_teste[:5])}")
    cobertas = collections.Counter()
    for parte in partes:
        for unidade in parte:
            cobertas += por_unidade.get(unidade, collections.Counter())
    if cobertas != total:
        erros.append("as partes não cobrem os IDs do discover uma vez cada")
    return erros, por_unidade


def escapar_dado(texto):
    """O escape do dado de um comando de workflow (`%`, CR e LF), por segurança: a mensagem já só tem o alfabeto seguro."""
    return texto.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def anotacoes_de_tempos(parte, python, duracoes):
    """As linhas `::notice` com o tempo de cada unidade da parte (JSON de uma linha por bloco; sem `::` possível, porque o nome só tem `[A-Za-z0-9_.]`). Só entram nome de unidade
    no alfabeto seguro e segundos finitos e não negativos; o resto é descartado (S6). Sem unidade válida ou com mais
    blocos que o limite de anotações do passo, devolve []."""
    itens = sorted((k, round(float(v), 1)) for k, v in (duracoes or {}).items()
                   if isinstance(k, str) and UNIDADE_SEGURA.fullmatch(k) and type(v) in (int, float)
                   and math.isfinite(v) and v >= 0)
    blocos, atual, tamanho = [], {}, 0
    for nome, seg in itens:
        custo = len(nome) + len(str(seg)) + 6
        if atual and tamanho + custo > LIMITE_DA_ANOTACAO:
            blocos.append(atual)
            atual, tamanho = {}, 0
        atual[nome] = seg
        tamanho += custo
    if atual:
        blocos.append(atual)
    if not blocos or len(blocos) > MAXIMO_DE_ANOTACOES or not re.fullmatch(r"[0-9]{1,2}/[0-9]{1,2}", parte) \
            or not re.fullmatch(r"3\.[0-9]{1,2}", python):
        return []
    linhas = []
    for i, bloco in enumerate(blocos, 1):
        mensagem = json.dumps({"v": 1, "parte": parte, "python": python, "bloco": [i, len(blocos)], "t": bloco},
                              separators=(",", ":"))
        linhas.append(f"::notice title=forge-tempos {parte} bloco {i}/{len(blocos)}::{escapar_dado(mensagem)}")
    return linhas


def descricao_da_causa(causa):
    """`tipo id local` (e o esperado e o obtido, já cortados e redigidos pelo suite-paralela) de uma causa tipada."""
    texto = " ".join(str(causa[c]) for c in ("tipo", "id", "local") if causa.get(c))
    return texto + (f" (esperado {causa['esperado']}, obtido {causa.get('obtido')})" if "esperado" in causa else "")


def anotacao_de_falha(rotulo, causas, erros):
    """A linha `::error` da parte vermelha, com os testes que caíram (tipo, ID e local de cada causa tipada do
    suite-paralela) e os erros da guarda, para a causa ficar legível nas anotações do check run (o log pode não estar ao
    alcance). `[]` sem causa nem erro. Uma linha só (quebra e `%` escapados, `escapar_dado`)."""
    itens = [descricao_da_causa(c) for c in list(causas or ())[:LIMITE_DE_CAUSAS]] + [str(e) for e in erros or ()]
    if not itens:
        return []
    titulo = rotulo if TITULO_SEGURO.fullmatch(rotulo or "") else "suite"
    return [f"::error title=forge-suite {titulo}::{escapar_dado('; '.join(itens))[:LIMITE_DA_ANOTACAO]}"]


def emitir_falha(environ, rotulo, causas, erros):
    """No Actions (GITHUB_ACTIONS=true), imprime a anotação de falha da parte; fora dele não imprime nada."""
    if environ.get("GITHUB_ACTIONS") == "true":
        for linha in anotacao_de_falha(rotulo, causas, erros):
            print(linha, flush=True)


PISO_PADRAO_GB = 2.0  # o mesmo padrão do hook `agentes` (R-TETO)


def piso_de_memoria(config):
    """O piso de memória livre em GB (`piso_memoria_gb`); inválido, ausente, não positivo ou booleano vale o padrão."""
    valor = config.get("piso_memoria_gb") if isinstance(config, dict) else None
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not valor > 0:
        return PISO_PADRAO_GB
    return float(valor)


def ha_folga(carga, memoria, nproc, piso):
    """R-TETO: 2 partes em paralelo só com load1 < nproc e memória livre acima do piso; sem medida, não há folga."""
    if None in (carga, memoria, nproc) or not nproc:
        return False
    return carga < nproc and memoria > piso


def por_duas_partes(sp, environ, lancar=None):
    """A suíte inteira em 2 partes (`--parte K/2`, filhos com CI=1 como o CI): paralelas com folga, senão em série. O
    código é 0 só com as duas verdes."""
    try:
        config = json.loads((sp.RAIZ / ".forge" / "config.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        config = {}
    carga, memoria, _ = sp.medir_carga()
    paralelo = ha_folga(carga, memoria, os.cpu_count(), piso_de_memoria(config))
    modo = ("em série", "paralelo")[paralelo]
    print(f"suite-partes: 2 partes {modo} (load1 {carga}, {memoria} GB livres, {os.cpu_count()} núcleos).",
          file=sys.stderr, flush=True)
    filho_env = {**environ, "CI": "1"}
    filho_env.pop("FORGE_SUITE_PULADOS", None)
    comandos = [[sys.executable, "-I", str(Path(__file__).resolve()), "--parte", f"{k}/2"] for k in (1, 2)]
    lancar = lancar or (lambda cmd: subprocess.Popen(cmd, env=filho_env))
    codigos = []
    if paralelo:
        codigos = [p.wait() for p in [lancar(c) for c in comandos]]
    else:
        for comando in comandos:
            codigos.append(lancar(comando).wait())
            if codigos[-1]:
                break
    return 0 if codigos and not any(codigos) and len(codigos) == 2 else 1


def falhar(motivo, codigo=1, rotulo="divisão"):
    print(f"suite-partes: {motivo}.", file=sys.stderr)
    print(f"FAILED ({rotulo})")
    return codigo


def veredito(relatorios, erros):
    """(linha final, código) com as mesmas contas do suite-paralela."""
    falhas = sum(rel["falhas"] for rel in relatorios if rel)
    erros_t = sum(rel["erros"] for rel in relatorios if rel)
    pulados = sum(rel["pulados"] for rel in relatorios if rel)
    if erros or falhas or erros_t:
        for erro in erros:
            print(f"suite-partes: {erro}", file=sys.stderr)
        detalhes = [f"failures={falhas}"] * bool(falhas) + [f"errors={erros_t}"] * bool(erros_t) \
            + [f"skipped={pulados}"] * bool(pulados) + ["guarda=" + str(len(erros))] * bool(erros)
        return f"FAILED ({', '.join(detalhes)})", 1
    return (f"OK (skipped={pulados})" if pulados else "OK"), 0


def rodar(sp, nomes, esperado, rotulo, todos=None, publicar=None, plano=None, anotar=None, falhou=None):
    """Roda `nomes` em processos (a regra de N do suite-paralela) e confere a completude contra `esperado`; verde, chama
    `publicar(relatorios)` (os pulados da parte, T3) e `anotar(relatorios)` (os tempos por unidade); vermelha, `falhou(causas, erros)` (a anotação `::error` com os testes que caíram). Com `plano` ({unidade:
    (módulo, posições)}), as unidades são as dele; sem, as de `planejar(nomes)`."""
    os.chdir(sp.RAIZ)
    inicio = time.monotonic()
    carga, memoria, total_gb = sp.medir_carga()
    try:
        n, origem = sp.numero_de_processos(os.environ, os.cpu_count(), carga, memoria, total_gb)
    except ValueError as e:
        return falhar(str(e), rotulo="configuração")
    pesos = sp.ler_pesos()
    # A3 (0.43.2): as unidades separadas nos pesos (`módulo.Classe`) vão a processos próprios, como no suite-paralela
    if plano is None:
        plano = sp.planejar(nomes, pesos, lambda nome: [t.id() for t in sp.achatar(sp.suite_do_modulo(nome))])
    unidades = sorted(plano)
    partes = sp.repartir(unidades, pesos, min(n, len(unidades)))
    erros = sp.conferir_particao(unidades, partes)
    filhos_nomes = []
    for parte in partes:
        inteiros = [u for u in parte if plano[u][1] is None]
        convertida, repetidos = para_o_filho(inteiros, todos or nomes)
        filhos_nomes.append(sorted(convertida + [u for u in parte if plano[u][1] is not None]))
        erros += repetidos
    if erros:
        return falhar("; ".join(erros))
    print(f"suite-partes: {rotulo}: {sum(esperado.values())} testes em {len(nomes)} módulos, {len(partes)} processos "
          f"({origem}).", file=sys.stderr, flush=True)
    antes = sp.estado_da_arvore()
    pasta = Path(tempfile.mkdtemp(prefix="forge-partes-"))
    filhos = []
    anteriores = {s: signal.signal(s, sp.ao_sinal) for s in sp.SINAIS}
    try:
        sp.lancar(filhos_nomes, pasta, filhos, plano)
        duracoes = sp.esperar(filhos, inicio)
        for s, h in anteriores.items():
            signal.signal(s, h)
        relatorios = [sp.ler_relatorio(pasta / f"p{i}.saida.json") for i in range(1, len(filhos) + 1)]
        erros, linhas = sp.resumir(partes, filhos, relatorios, duracoes, pasta)
        executado = collections.Counter(i for rel in relatorios if rel for i in rel["ids"])
        erros += sp.conferir_completude(esperado, executado)
        erros += sp.conferir_arvore(antes, sp.estado_da_arvore())
    except sp.Interrompido as e:
        for s in sp.SINAIS:
            signal.signal(s, signal.SIG_IGN)
        sp.encerrar(filhos)
        print(f"suite-partes: interrompida pelo sinal {e.numero}; os processos foram encerrados.", file=sys.stderr)
        print("FAILED (interrompida)")
        return 128 + e.numero
    finally:
        shutil.rmtree(pasta, ignore_errors=True)
    segundos = time.monotonic() - inicio
    rodados = sum(rel["rodados"] for rel in relatorios if rel)
    print(f"\nRan {rodados} tests in {segundos:.3f}s ({len(partes)} processos, {rotulo})\n")
    linha, codigo = veredito(relatorios, erros)
    causas = sp.imprimir_causas(filhos, relatorios)  # O7 (0.44.1): a causa tipada também no plano dirigido do pre-push
    if codigo and falhou:
        falhou(causas, erros)
    if not codigo and publicar:
        publicar(relatorios)
    if not codigo and anotar:
        anotar(relatorios)
    print(linha)
    sp.publicar_no_ci(linha, linhas, partes, relatorios, duracoes, pesos, rodados, segundos)
    return codigo


def por_modulos(sp, texto):
    nomes = sorted(set(texto.split(","))) if texto else []
    invalidos = [m for m in nomes if not NOME_DE_MODULO.fullmatch(m) or not arquivo_do_modulo(sp, m).is_file()]
    if not nomes or invalidos:
        return falhar(f"--modulos: módulo sem arquivo em tests/ ou fora do padrão: {', '.join(invalidos) or '(vazio)'}",
                      2, "uso")
    os.chdir(sp.RAIZ)
    todos = todos_os_modulos(sp)
    esperado = collections.Counter()
    for nome in nomes:
        achados = sp.ids(sp.descobrir(f"{nome.rsplit('.', 1)[-1]}.py"))
        esperado += collections.Counter({i: c for i, c in achados.items() if modulo_do_id(i, {nome})})
    return rodar(sp, nomes, esperado, "afetados", todos)


def por_parte(sp, texto, environ):
    if not environ.get("CI"):
        return falhar("--parte só roda no CI (CI definido); à mão, a suíte inteira é scripts/suite-paralela.py", 2, "uso")
    try:
        k, n = ler_parte(texto)
    except ValueError as e:
        return falhar(str(e), 2, "uso")
    os.chdir(sp.RAIZ)
    nomes = todos_os_modulos(sp)
    partes, plano, erros = dividir_por_unidade(sp, nomes, n)
    total = sp.ids(sp.descobrir())
    fora = fora_da_divisao(total, nomes)
    if fora:
        erros.append(f"{len(fora)} teste(s) do discover fora dos módulos da divisão: {', '.join(fora[:5])}")
    faltas, por_unidade = completude_da_divisao(sp, total, nomes, plano, partes)
    erros += faltas
    if erros:
        emitir_falha(environ, f"parte {k}/{n}", [], erros)
        return falhar("; ".join(erros))
    parte = partes[k - 1]
    print(f"suite-partes: parte {k}/{n}: {', '.join(parte)}", file=sys.stderr, flush=True)
    destino = environ.get("FORGE_SUITE_PULADOS")
    publicar = (lambda relatorios: gravar_pulados(sp, destino, k, n, relatorios)) if destino else None
    anotar = (lambda relatorios: anotar_tempos(k, n, relatorios)) if environ.get("GITHUB_ACTIONS") == "true" else None
    falhou = lambda causas, erros: emitir_falha(environ, f"parte {k}/{n}", causas, erros)  # noqa: E731
    esperado = sum((por_unidade[u] for u in parte), collections.Counter())
    modulos_da_parte = sorted({plano[u][0] for u in parte})
    return rodar(sp, modulos_da_parte, esperado, f"parte {k}/{n}", nomes, publicar, {u: plano[u] for u in parte}, anotar,
                 falhou)


def anotar_tempos(k, n, relatorios):
    """Os tempos por unidade da parte K/N em anotação do check run (a fonte de `scripts/pesos-do-ci.py`)."""
    versao = f"{sys.version_info.major}.{sys.version_info.minor}"
    duracoes = {u: v for rel in relatorios if rel for u, v in rel.get("duracoes", {}).items()}
    for linha in anotacoes_de_tempos(f"{k}/{n}", versao, duracoes):
        print(linha, flush=True)


def gravar_pulados(sp, destino, k, n, relatorios):
    """T3: os pulados da parte K/N em `destino`, para o agregador do CI somar (`--somar-pulados`)."""
    ids = sp.pulados_ids(relatorios)
    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    Path(destino).write_text(json.dumps({"parte": f"{k}/{n}", "pulados": len(ids), "pulados_ids": ids}),
                             encoding="utf-8")
    print(f"suite-partes: parte {k}/{n}: {len(ids)} pulado(s) gravado(s) para o agregador.", file=sys.stderr)


def ler_um_pulado(arquivo, n):
    """(K, pulados, ids) de um arquivo de parte; ValueError se ilegível, de outro N ou com a contagem errada."""
    try:
        dado = json.loads(arquivo.read_text(encoding="utf-8"))
        k, n_lido = ler_parte(dado["parte"])
        quantos, lista = dado["pulados"], dado["pulados_ids"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise ValueError(f"{arquivo.name} ilegível") from e
    if n_lido != n or type(quantos) is not int or not isinstance(lista, list) or quantos != len(lista) \
            or not all(isinstance(i, str) for i in lista):
        raise ValueError(f"{arquivo.name}: parte de outro N ou com a contagem inválida")
    return k, quantos, lista


def ler_pulados(pasta, n):
    """(soma, ids, erros) dos `*.json` de `pasta`: um por parte K/N, K de 1 a N uma vez só (falha fechada)."""
    vistos, soma, ids, erros = set(), 0, [], []
    for arquivo in sorted(Path(pasta).glob("*.json")) if Path(pasta).is_dir() else []:
        try:
            k, quantos, lista = ler_um_pulado(arquivo, n)
        except ValueError as e:
            erros.append(str(e))
            continue
        if k in vistos:
            erros.append(f"{arquivo.name}: parte {k}/{n} repetida")
            continue
        vistos.add(k)
        soma += quantos
        ids += lista
    faltam = sorted(set(range(1, n + 1)) - vistos)
    if faltam:
        erros.append(f"faltam os pulados da(s) parte(s) {', '.join(map(str, faltam))} de {n}")
    return soma, sorted(ids), erros


def somar_pulados(sp, texto_n, pasta):
    """T3 no agregador: a soma dos pulados das N partes contra `teto_pulados`; a última linha é OK ou FAILED."""
    if not re.fullmatch(r"[1-9][0-9]?", texto_n or ""):
        return falhar(f"--somar-pulados espera N de 1 a 99 (veio '{texto_n}')", 2, "uso")
    soma, ids, erros = ler_pulados(pasta, int(texto_n))
    if erros:
        return falhar("; ".join(erros), rotulo="pulados das partes")
    linha = sp.comparar_teto(soma, [sp.neutro(i) for i in ids], sp.ler_teto(), [], "suite-partes")
    print(linha or (f"OK (skipped={soma})" if soma else "OK"))
    return 1 if linha else 0


def main(argv=None, environ=None):
    argv = sys.argv[1:] if argv is None else argv
    # cópia antes do discover: um módulo de teste que mexe no os.environ no import (o test_catraca.py tira GITHUB_ACTIONS)
    # não pode calar as anotações da parte (CI-ANOTACAO-CALADA, E137.2)
    environ = dict(os.environ) if environ is None else environ
    if argv[:1] == ["--somar-pulados"] and len(argv) == 3:
        return somar_pulados(carregar_paralela(), argv[1], argv[2])
    if argv == ["--duas-partes"]:
        return por_duas_partes(carregar_paralela(), environ)
    if len(argv) != 2 or argv[0] not in ("--modulos", "--parte"):
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    sp = carregar_paralela()
    if argv[0] == "--modulos":
        return por_modulos(sp, argv[1])
    return por_parte(sp, argv[1], environ)


if __name__ == "__main__":
    sys.exit(main())
