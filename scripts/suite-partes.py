#!/usr/bin/env python3
"""Forge: uma parte da suíte em paralelo, sobre o mecanismo de `scripts/suite-paralela.py` (D4), sem mudá-lo.

Uso: python3 scripts/suite-partes.py --modulos M[,M...]
     python3 scripts/suite-partes.py --parte K/N
     python3 scripts/suite-partes.py --somar-pulados N PASTA
  --modulos M   roda só esses módulos de tests/ (os testes afetados de um envio; `evals.test_x` é o de um pacote,
                tests/evals/test_x.py) em até 4 processos: a mesma regra de
                N, a mesma LPT sobre tests/pesos-d4.json, os mesmos filhos (`suite-paralela.py --processo`) e a mesma
                guarda de completude, aqui contra o discover desses módulos. Não pega a trava: quem chama (o pre-push)
                já a tem.
  --parte K/N   (só no CI, com CI definido) a parte K de N da suíte inteira. Os módulos de tests/ são divididos em N
                partes por LPT sobre os pesos (a mesma árvore dá a mesma divisão em todos os jobs); entram também os
                módulos dos pacotes de tests/, que o discover acha e o suite-paralela ainda não divide. Falha fechada: a
                divisão cobre todo módulo uma vez só, todo teste do discover da suíte inteira cai num módulo da
                divisão e a parte roda exatamente os IDs do discover que são dela. Com as N partes verdes, a suíte
                inteira passou; o job agregador do CI (`bateria`, `bateria (python 3.14)`) exige as N. Com
                FORGE_SUITE_PULADOS=<arquivo>, a parte verde grava nele os pulados dela (T3: `{"parte": "K/N",
                "pulados": n, "pulados_ids": [...]}`).
  --somar-pulados N PASTA  (o agregador do CI) soma os pulados das N partes gravados em PASTA (`*.json`, um por parte,
                K de 1 a N uma vez só) e compara com `teto_pulados` de tests/config.json, com a conta do suite-paralela
                (T3). Falha fechada: parte faltando, repetida, de outro N, arquivo ilegível ou teto ilegível reprova.
Só biblioteca padrão. A última linha é `OK` (ou `OK (skipped=N)`) ou `FAILED (...)`, como no `unittest`.
"""
import collections
import importlib.machinery
import importlib.util
import json
import os
import re
import shutil
import signal
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PARALELA = RAIZ / "scripts" / "suite-paralela.py"
PARTE = re.compile(r"([1-9][0-9]?)/([1-9][0-9]?)")
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


def esperado_da_parte(total, parte):
    """O multiconjunto de IDs do discover inteiro que pertence aos módulos da parte."""
    conjunto = set(parte)
    return collections.Counter({i: c for i, c in total.items() if modulo_do_id(i, conjunto) is not None})


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


def dividir(sp, nomes, n):
    """(partes, erros): os módulos em `n` partes pela LPT do suite-paralela, conferidas como partição."""
    partes = sp.repartir(nomes, sp.ler_pesos(), n)
    erros = sp.conferir_particao(nomes, partes)
    if len(partes) != n:
        erros.append(f"{len(nomes)} módulos não dão {n} partes não vazias")
    return partes, erros


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


def rodar(sp, nomes, esperado, rotulo, todos=None, publicar=None):
    """Roda `nomes` em processos (a regra de N do suite-paralela) e confere a completude contra `esperado`; verde, chama
    `publicar(relatorios)` (os pulados da parte, T3)."""
    os.chdir(sp.RAIZ)
    inicio = time.monotonic()
    carga, memoria, total_gb = sp.medir_carga()
    try:
        n, origem = sp.numero_de_processos(os.environ, os.cpu_count(), carga, memoria, total_gb)
    except ValueError as e:
        return falhar(str(e), rotulo="configuração")
    pesos = sp.ler_pesos()
    partes = sp.repartir(nomes, pesos, min(n, len(nomes)))
    erros = sp.conferir_particao(nomes, partes)
    filhos_nomes = []
    for parte in partes:
        convertida, repetidos = para_o_filho(parte, todos or nomes)
        filhos_nomes.append(convertida)
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
        sp.lancar(filhos_nomes, pasta, filhos)
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
    if not codigo and publicar:
        publicar(relatorios)
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
    partes, erros = dividir(sp, nomes, n)
    total = sp.ids(sp.descobrir())
    fora = fora_da_divisao(total, nomes)
    if fora:
        erros.append(f"{len(fora)} teste(s) do discover fora dos módulos da divisão: {', '.join(fora[:5])}")
    if erros:
        return falhar("; ".join(erros))
    parte = partes[k - 1]
    print(f"suite-partes: parte {k}/{n}: {', '.join(parte)}", file=sys.stderr, flush=True)
    destino = environ.get("FORGE_SUITE_PULADOS")
    publicar = (lambda relatorios: gravar_pulados(sp, destino, k, n, relatorios)) if destino else None
    return rodar(sp, parte, esperado_da_parte(total, parte), f"parte {k}/{n}", nomes, publicar)


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
    environ = os.environ if environ is None else environ
    if argv[:1] == ["--somar-pulados"] and len(argv) == 3:
        return somar_pulados(carregar_paralela(), argv[1], argv[2])
    if len(argv) != 2 or argv[0] not in ("--modulos", "--parte"):
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    sp = carregar_paralela()
    if argv[0] == "--modulos":
        return por_modulos(sp, argv[1])
    return por_parte(sp, argv[1], environ)


if __name__ == "__main__":
    sys.exit(main())
