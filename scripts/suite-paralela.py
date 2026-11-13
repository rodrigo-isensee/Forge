#!/usr/bin/env python3
"""Forge: a suíte inteira (`python3 -m unittest discover -s tests`) dividida em até 4 processos (D4, R-TETO).

Uso: python3 scripts/suite-paralela.py
Chamado pelo `.githooks/pre-push` e pelo CI. Só biblioteca padrão; nada de rede nem de custo (R-CUSTO).

- Divisão por unidade, por LPT sobre os pesos de `tests/pesos-d4.json` (unidade -> segundos); peso ausente vale a
  mediana. A unidade é o módulo (`tests/test*.py`, e `pacote.test_x` para `tests/pacote/test_x.py` de um pacote com
  `__init__.py`; nome de arquivo repetido entre a raiz e um pacote reprova a divisão); uma chave `módulo.Classe` ou `módulo.Classe.teste` nos pesos tira
  esses testes do módulo para uma unidade própria (o módulo pesado se divide entre os processos), e o resto do módulo
  segue como a unidade `módulo`. O peso só equilibra: nunca decide o que roda. A mesma árvore dá a mesma divisão.
- Processos: N = min(4, nproc); com carga alta (load de 1 min >= 0,8 x nproc ou memória disponível no piso), 2.
  FORGE_SUITE_PROCS fixa N de 1 a 4; fora disso o script recusa (falha fechada).
- Cada processo roda com `nice`, num grupo de processos próprio e com um TMPDIR próprio (modo 700), apagado ao fim.
- Guarda de completude (falha fechada): a soma e a união (multiconjunto) dos IDs que os processos rodaram têm de
  ser iguais às do `discover` da suíte inteira; processo que sai com código diferente de 0, morre por sinal, roda
  zero testes ou não deixa o relatório reprova. Também reprova se a árvore de trabalho (`git status`) ou o
  `.git/config` comum mudarem durante a suíte.
- Tempo ao vivo: cada unidade que termina deixa no stderr, com flush, `suite-paralela: unidade <nome> <s> s (processo N)`;
  no SIGTERM/SIGINT/SIGHUP saem `suite-paralela: rodando <nome> há <s> s (processo N)` das que não terminaram (job cortado
  por timeout deixa evidência por módulo). Só informa: o veredito, a ordem e a saída final não mudam.
- SIGTERM, SIGINT e SIGHUP encerram o grupo de cada processo e apagam os TMPDIR; a saída é diferente de 0.
- Uma suíte por vez (R-TETO, SUITE-FILA-JUSTA): o pre-push chama o script já com a trava e passa o caminho dela em
  FORGE_SUITE_TRAVA; o script confere que a trava está presa e anotada pelo hook (o pid nela). Chamado à mão,
  sem a variável, ele se executa de novo por `.githooks/pre-push --suite`, que pega a mesma trava e a mesma fila.
- Reuso (K6): ao fechar verde, grava em `$(git rev-parse --git-common-dir)/forge-suite-verde` o hash da árvore
  testada (`git ls-tree -r HEAD` sem os `*.md` de parecer direto em `docs/reviews/`, `docs/qa/`, `docs/devops/`,
  `docs/security/` e `changelog.d/`: `_modelo`, README e subpastas entram; arquivo com skip-worktree ou
  assume-unchanged não dá hash; o carimbo só grava se o hash no fim for o do começo)
  e a versão do Python. Chamado à mão, antes da trava e da fila, com árvore limpa e o mesmo hash e Python, imprime
  `suite: reusa <hash> de <hora>` e `OK` e sai com 0 sem rodar. Qualquer diferença, árvore suja ou carimbo ausente
  ou ilegível roda a suíte (falha fechada). FORGE_SUITE_SEM_REUSO=1 força a execução; com CI definido sempre roda.
- No CI (`GITHUB_STEP_SUMMARY`), o resumo do passo traz as unidades mais lentas, a soma, a maior unidade, o desequilíbrio
  e os módulos sem peso (só informa: nunca reprova, nem muda a divisão). O título de cada `::group::` traz os módulos.
- FORGE_SUITE_MEDIR=1 regrava `tests/pesos-d4.json` com as durações de cada unidade da execução, se tudo passou.
- Teto de pulados (T3): só no CI (GITHUB_ACTIONS=true), mais pulados que `teto_pulados` de `tests/config.json` (inteiro
  >= 0; ausente, de outro tipo ou ilegível reprova) é `FAILED`, antes de regravar pesos e carimbo; fora do CI só avisa.
  Na suíte em partes (`scripts/suite-partes.py --parte`), cada parte publica os pulados e o agregador do CI soma.
A última linha é `OK` (ou `OK (skipped=N)`) ou `FAILED (...)`, como no `unittest`.
"""
import collections
import datetime
import fcntl
import hashlib
import json
import os
import re
import shutil
import signal
import stat
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TESTES = "tests"
PESOS = RAIZ / TESTES / "pesos-d4.json"
TETO = 4
CARGA_MAX, PISO_GB, PISO_FRACAO = 0.8, 1.0, 0.15
SINAIS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)
ESPERA_TERMINO_S = 10
HOOK = RAIZ / ".githooks" / "pre-push"
FORA_DO_HASH = ("docs/reviews/", "docs/qa/", "docs/devops/", "docs/security/", "changelog.d/")
CARIMBO = "forge-suite-verde"
REGISTRO_PASTA, REGISTRO = ".forge-contrib", "suite-vermelha.jsonl"  # fora do git (L32)
LIMITE_REGISTRO, LINHAS_LIDAS = 50, 2000
# O7 (0.44.1): a causa tipada de cada teste que cai (o diagnóstico lê o tipo, não o log inteiro); valores cortados e sem segredo
TETO_DA_SAIDA, TETO_DO_VALOR = 4000, 160  # caracteres do traceback acima dos quais a causa é `saida-grande`; de esperado e obtido
SEGREDO = re.compile(r"(?i)(?:gh[pousr]_\w{20,}|github_pat_\w{20,}|glpat-[\w-]{20,}|sk-[\w-]{20,}|AKIA[0-9A-Z]{16}|xox[abpr]-[\w-]{10,}"
                     r"|\b(?:token|senha|password|secret|segredo|api[_-]?key|chave)\b\s*[:=]\s*\S+)")
LOCAL_DO_TESTE = re.compile(r'File "[^"]*/(tests/[^"]+)", line (\d+)')
COMPARACAO = re.compile(r"^AssertionError: (.*?) != (.*)$", re.M)
TESTE_DE_TEMPO = re.compile(r"tempo|prazo|relogio|hora|duracao|timeout|espera", re.I)
LIMITE_LENTAS, LIMITE_SEM_PESO, LIMITE_SEM_DURACAO = 10, 20, 20  # o resumo do CI é curto (N-CI, C-11)
LIMITE_CAIDOS = 30  # QA-1: os testes que caíram no resumo do CI; o resto fica no log do passo
CONFIG, LIMITE_PULADOS = RAIZ / TESTES / "config.json", 20  # teto de pulados (T3)


class Interrompido(Exception):
    def __init__(self, numero):
        super().__init__(numero)
        self.numero = numero


def achatar(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from achatar(item)
        else:
            yield item


def descobrir(pattern="test*.py"):
    """A mesma descoberta do `python3 -m unittest discover -s tests`, a partir da raiz."""
    return unittest.TestLoader().discover(TESTES, pattern=pattern)


def ids(suite):
    return collections.Counter(t.id() for t in achatar(suite))


def modulos():
    """Os módulos de teste da raiz de `tests/` e os dos pacotes dela (pasta com `__init__.py` em todo nível, que o
    `discover` também acha), estes pelo nome com ponto (`evals.test_x`); a guarda de completude confere esta lista
    contra o `discover`."""
    base = RAIZ / TESTES
    nomes = []
    for p in base.rglob("test*.py"):
        partes = (*p.parent.relative_to(base).parts, p.stem)
        if all(x.isidentifier() for x in partes) and all(
                (base / Path(*partes[:i + 1]) / "__init__.py").is_file() for i in range(len(partes) - 1)):
            nomes.append(".".join(partes))
    return sorted(nomes)


def nomes_de_arquivo_repetidos(nomes):
    """Os módulos cujo nome de arquivo se repete entre a raiz de `tests/` e os pacotes: o `discover` do módulo da raiz
    (padrão `<nome>.py`) acharia também o do pacote, e o teste rodaria duas vezes (falha fechada)."""
    contagem = collections.Counter(m.rsplit(".", 1)[-1] for m in nomes)
    return sorted(m for m in nomes if contagem[m.rsplit(".", 1)[-1]] > 1)


def suite_do_modulo(nome):
    """Os testes do módulo `nome` como no `discover` da suíte inteira (os mesmos IDs): o da raiz pelo padrão
    `<nome>.py`; o de pacote (`pacote.test_x`) pelo `discover` na pasta do pacote, com `tests/` como raiz."""
    if "." not in nome:
        return descobrir(f"{nome}.py")
    pacote, arquivo = nome.rsplit(".", 1)
    return unittest.TestLoader().discover(str(Path(TESTES, *pacote.split("."))), pattern=f"{arquivo}.py",
                                          top_level_dir=TESTES)


def ler_pesos(caminho=PESOS):
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(dados, dict):
        return {}
    return {k: float(v) for k, v in dados.items() if isinstance(k, str) and isinstance(v, (int, float)) and v >= 0}


def repartir(nomes, pesos, n):
    """LPT determinística: o módulo mais pesado primeiro, no processo mais leve (empate: menor índice e nome)."""
    conhecidos = [pesos[m] for m in nomes if m in pesos]
    mediana = statistics.median(conhecidos) if conhecidos else 1.0
    partes = [[] for _ in range(n)]
    cargas = [0.0] * n
    for nome in sorted(nomes, key=lambda m: (-pesos.get(m, mediana), m)):
        i = min(range(n), key=lambda k: (cargas[k], k))
        partes[i].append(nome)
        cargas[i] += pesos.get(nome, mediana)
    return [sorted(p) for p in partes if p]


def separadas(nome, pesos):
    """As chaves de `pesos` que tiram testes do módulo `nome` para uma unidade própria: `nome.Classe` ou
    `nome.Classe.teste` (o prefixo do ID do teste no `discover`)."""
    return sorted(k for k in pesos if k.startswith(nome + "."))


def unidade_do_teste(ident, chaves, nome):
    """A chave mais longa de `chaves` que é o ID ou um prefixo dele (até um ponto); sem nenhuma, o próprio módulo."""
    casadas = [k for k in chaves if ident == k or ident.startswith(k + ".")]
    return max(casadas, key=len) if casadas else nome


def planejar(nomes, pesos, ids_do_modulo):
    """As unidades da divisão: {unidade: (módulo, posições)}, com posições None para o módulo inteiro. Só o módulo com
    chave separada nos pesos é aberto (`ids_do_modulo(nome)` dá os IDs na ordem do `discover`); cada teste vai para a
    unidade da chave mais longa que casa com o ID, e o que sobra fica na unidade do módulo. Unidade sem teste não entra."""
    plano = {}
    for nome in nomes:
        chaves = separadas(nome, pesos)
        if not chaves:
            plano[nome] = (nome, None)
            continue
        por_unidade = {}
        for posicao, ident in enumerate(ids_do_modulo(nome)):
            por_unidade.setdefault(unidade_do_teste(ident, chaves, nome), []).append(posicao)
        for unidade, posicoes in sorted(por_unidade.items()):
            plano[unidade] = (nome, posicoes)
    return plano


def conferir_particao(nomes, partes):
    """Toda parte vem da lista, nenhum módulo em duas partes e nenhum de fora."""
    vistos = [m for p in partes for m in p]
    erros = []
    repetidos = sorted(m for m, c in collections.Counter(vistos).items() if c > 1)
    if repetidos:
        erros.append(f"módulo em mais de um processo: {', '.join(repetidos)}")
    faltam = sorted(set(nomes) - set(vistos))
    if faltam:
        erros.append(f"módulo fora da divisão: {', '.join(faltam)}")
    sobram = sorted(set(vistos) - set(nomes))
    if sobram:
        erros.append(f"módulo desconhecido na divisão: {', '.join(sobram)}")
    return erros


def conferir_completude(esperado, executado):
    """Multiconjunto dos IDs rodados igual ao do `discover`: mesma soma e mesma união."""
    erros = []
    if sum(executado.values()) != sum(esperado.values()):
        erros.append(f"soma diferente: o discover acha {sum(esperado.values())} testes e os processos rodaram "
                     f"{sum(executado.values())}")
    ausentes = esperado - executado
    if ausentes:
        lista = ", ".join(sorted(ausentes)[:5]) + (" ..." if len(ausentes) > 5 else "")
        erros.append(f"{sum(ausentes.values())} teste(s) ausente(s) da execução: {lista}")
    extras = executado - esperado
    if extras:
        lista = ", ".join(sorted(extras)[:5]) + (" ..." if len(extras) > 5 else "")
        erros.append(f"{sum(extras.values())} teste(s) rodado(s) a mais que o discover: {lista}")
    return erros


def medir_carga():
    """(load de 1 min, GB disponíveis, GB totais) de /proc, ou None em cada um que não der para ler."""
    carga = memoria = total = None
    try:
        carga = float(Path("/proc/loadavg").read_text(encoding="utf-8").split()[0])
    except (OSError, ValueError, IndexError):
        pass
    try:
        campos = dict(linha.split(":", 1) for linha in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines()
                      if ":" in linha)
        memoria = int(campos["MemAvailable"].split()[0]) / 1024 / 1024
        total = int(campos["MemTotal"].split()[0]) / 1024 / 1024
    except (OSError, ValueError, KeyError, IndexError):
        pass
    return carga, memoria, total


def carga_alta(carga, memoria, total, nproc):
    """A mesma conta do hook `agentes` (R-TETO); sem medida, nunca é carga alta."""
    if None in (carga, memoria, total, nproc):
        return False
    return carga >= CARGA_MAX * nproc or memoria <= max(PISO_GB, PISO_FRACAO * total)


def numero_de_processos(environ, nproc, carga, memoria, total):
    """(N, origem). ValueError se FORGE_SUITE_PROCS vier fora de 1..TETO."""
    fixo = environ.get("FORGE_SUITE_PROCS", "")
    if fixo:
        if not fixo.isdigit() or not 1 <= int(fixo) <= TETO:
            raise ValueError(f"FORGE_SUITE_PROCS deve ser um inteiro de 1 a {TETO} (veio '{fixo}')")
        return int(fixo), "FORGE_SUITE_PROCS"
    base = max(1, min(TETO, nproc or 1))
    if carga_alta(carga, memoria, total, nproc):
        return min(2, base), f"carga alta (load {carga:.1f} de {nproc} núcleos, {memoria:.1f} GB disponíveis)"
    return base, f"min({TETO}, nproc={nproc})"


# Processo filho -------------------------------------------------------------------------------------------------

class Resultado(unittest.TextTestResult):
    """Anota o ID de cada teste iniciado (como o `testsRun` conta)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ids = []

    def startTest(self, test):  # noqa: N802 - nome do unittest
        self.ids.append(test.id())
        super().startTest(test)


def vigiar_pai(pai):
    """Pai morto (SIGKILL no orquestrador): o filho encerra o próprio grupo em vez de seguir órfão."""
    while True:
        time.sleep(1)
        if os.getppid() != pai:
            os.killpg(0, signal.SIGKILL)


def suite_da_unidade(unidade):
    """O módulo inteiro (texto: o nome) ou só os testes das posições dele ({"unidade", "modulo", "posicoes"}), na ordem
    do `discover`; numa suíte só, para o `unittest` rodar uma vez o setUpModule e o setUpClass da unidade."""
    if isinstance(unidade, str):
        return suite_do_modulo(unidade)
    testes = list(achatar(suite_do_modulo(unidade["modulo"])))
    return unittest.TestSuite(testes[i] for i in unidade["posicoes"] if i < len(testes))


def processo(entrada, saida):
    os.nice(10)
    threading.Thread(target=vigiar_pai, args=(os.getppid(),), daemon=True).start()
    unidades = json.loads(Path(entrada).read_text(encoding="utf-8"))
    verbosidade = 2 if os.environ.get("GITHUB_ACTIONS") == "true" else 1
    resultado = Resultado(unittest.runner._WritelnDecorator(sys.stderr), True, verbosidade)
    duracoes = {}
    tempos = open(f"{saida}.tempos", "a", encoding="utf-8", buffering=1)  # o orquestrador lê ao vivo (tempo por unidade)
    resultado.startTestRun()
    try:
        for unidade in unidades:
            nome = unidade if isinstance(unidade, str) else unidade["unidade"]
            tempos.write(f"inicio\t{nome}\t{time.time():.3f}\n")
            inicio = time.monotonic()
            suite_da_unidade(unidade).run(resultado)
            duracoes[nome] = round(time.monotonic() - inicio, 1)
            tempos.write(f"fim\t{nome}\t{duracoes[nome]:.1f}\n")
    finally:
        resultado.stopTestRun()
        tempos.close()
    resultado.printErrors()
    sys.stderr.write(f"\nRan {resultado.testsRun} tests\n")
    caidos = sorted({getattr(t, "test_case", t).id() for t, _ in resultado.failures + resultado.errors})
    relatorio = {"ids": resultado.ids, "caidos": caidos, "rodados": resultado.testsRun, "falhas": len(resultado.failures),
                 "erros": len(resultado.errors), "pulados": len(resultado.skipped),
                 "pulados_ids": [t.id() for t, _ in resultado.skipped],
                 "esperados": len(resultado.expectedFailures), "inesperados": len(resultado.unexpectedSuccesses),
                 "ok": resultado.wasSuccessful(), "duracoes": duracoes,
                 "causas": [causa_da_falha(getattr(t, "test_case", t).id(), texto)
                            for t, texto in (resultado.failures + resultado.errors)[:LIMITE_REGISTRO]]}
    Path(saida).write_text(json.dumps(relatorio), encoding="utf-8")
    return 0 if resultado.wasSuccessful() else 1


def redigir(texto):
    """O7: o valor sem segredo (token, chave, `senha=`...), sem controle e cortado em TETO_DO_VALOR."""
    return neutro(SEGREDO.sub("[redigido]", texto))[:TETO_DO_VALOR]


def causa_da_falha(ident, traceback_):
    """O7: {id, tipo, local?, obtido?, esperado?} do teste que caiu. Tipo: `timeout`, `saida-grande` (traceback acima de
    TETO_DA_SAIDA), `teste-de-tempo` (asserção num teste de nome de tempo ou prazo), `assercao` ou `erro`. O `local` é o
    último quadro em tests/; obtido e esperado vêm do `X != Y` do assertEqual (o primeiro é o obtido), redigidos."""
    causa = {"id": neutro(ident)}
    locais = LOCAL_DO_TESTE.findall(traceback_)
    if locais:
        causa["local"] = neutro(f"{locais[-1][0]}:{locais[-1][1]}")
    if "TimeoutExpired" in traceback_ or "timed out" in traceback_:
        causa["tipo"] = "timeout"
    elif len(traceback_) > TETO_DA_SAIDA:
        causa["tipo"] = "saida-grande"
    elif "AssertionError" in traceback_:
        causa["tipo"] = "teste-de-tempo" if TESTE_DE_TEMPO.search(ident) else "assercao"
    else:
        causa["tipo"] = "erro"
    comparacao = COMPARACAO.search(traceback_)
    if comparacao:
        causa["obtido"], causa["esperado"] = redigir(comparacao.group(1)), redigir(comparacao.group(2))
    return causa


def causas_da_suite(filhos, relatorios):
    """O7: as causas dos relatórios mais `sinal` por processo morto por sinal (esse não deixa relatório)."""
    causas = [{"id": f"processo-{i}", "tipo": "sinal", "sinal": -p.returncode} for i, p in enumerate(filhos, 1) if p.returncode < 0]
    return causas + [c for rel in relatorios if rel for c in rel.get("causas", ())][:LIMITE_REGISTRO]


def imprimir_causas(filhos, relatorios):
    """O7: uma linha `suite-paralela: causa tipo=... id=...` por causa, no stderr (também o `suite-partes` a usa); devolve as causas."""
    causas = causas_da_suite(filhos, relatorios)
    for causa in causas:
        print(f"suite-paralela: causa tipo={causa['tipo']} " + " ".join(f"{k}={v}" for k, v in causa.items() if k != "tipo"),
              file=sys.stderr)
    return causas


# Reuso por árvore (K6) --------------------------------------------------------------------------------------------

def _git(raiz, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", *args], cwd=raiz, capture_output=True, env=env)


def fora_do_hash(caminho):
    """Só o parecer e o fragmento de changelog: `*.md` direto nas pastas de FORA_DO_HASH, sem `_modelo` nem README."""
    pasta, _, nome = caminho.rpartition("/")
    return f"{pasta}/" in FORA_DO_HASH and nome.endswith(".md") and not nome.startswith("_") and nome != "README.md"


def hash_da_arvore(raiz):
    """Hash dos objetos do git de HEAD sem os pareceres e os fragmentos de changelog (`fora_do_hash`); None com a
    árvore suja, com arquivo skip-worktree ou assume-unchanged (o `git status` não os vê) ou erro."""
    status = _git(raiz, "status", "--porcelain", "--untracked-files=all")
    lista = _git(raiz, "ls-tree", "-r", "-z", "HEAD")
    marcas = _git(raiz, "ls-files", "-v", "-z")
    if status.returncode != 0 or status.stdout.strip() or lista.returncode != 0 or not lista.stdout \
            or marcas.returncode != 0 or any(m[:1].islower() or m[:1] == b"S" for m in marcas.stdout.split(b"\0") if m):
        return None
    resumo = hashlib.sha256()
    for entrada in lista.stdout.split(b"\0"):
        caminho = entrada.partition(b"\t")[2].decode("utf-8", "surrogateescape")
        if entrada and not fora_do_hash(caminho):
            resumo.update(entrada + b"\0")
    return resumo.hexdigest()


def caminho_do_carimbo(raiz):
    r = _git(raiz, "rev-parse", "--git-common-dir")
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return (Path(raiz) / r.stdout.decode().strip()) / CARIMBO


def gravar_carimbo(raiz, hash_arvore, python=None):
    """Grava o carimbo (atomicamente); sem hash ou sem lugar, não grava."""
    destino = caminho_do_carimbo(raiz)
    if not hash_arvore or destino is None:
        return
    dados = {"hash": hash_arvore, "python": python or sys.version,
             "hora": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")}
    try:
        temporario = destino.with_name(f"{CARIMBO}.{os.getpid()}")
        temporario.write_text(json.dumps(dados), encoding="utf-8")
        os.replace(temporario, destino)
    except OSError:
        pass


def reuso(raiz, environ, python=None):
    """(hash, hora) se há carimbo verde da mesma árvore e do mesmo Python; None em qualquer outro caso."""
    if environ.get("CI") or environ.get("FORGE_SUITE_SEM_REUSO") == "1":
        return None
    atual = hash_da_arvore(raiz)
    destino = caminho_do_carimbo(raiz)
    if atual is None or destino is None:
        return None
    try:
        dados = json.loads(destino.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(dados, dict) or dados.get("hash") != atual or dados.get("python") != (python or sys.version):
        return None
    return atual, str(dados.get("hora", "?"))


# Orquestrador ---------------------------------------------------------------------------------------------------

def estado_da_arvore():
    """(`git status --porcelain`, texto do `.git/config` comum): a suíte não pode mudar nenhum dos dois."""
    sys.path.insert(0, str(RAIZ / TESTES))
    import guarda_git  # noqa: E402 - módulo de apoio da própria suíte
    r = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=RAIZ, capture_output=True,
                       text=True, env=guarda_git.sem_manutencao({k: v for k, v in os.environ.items()
                                                                 if not k.startswith("GIT_")}))
    return (r.returncode, r.stdout), guarda_git.ler(guarda_git.config_comum(RAIZ))


def conferir_arvore(antes, depois):
    sys.path.insert(0, str(RAIZ / TESTES))
    import guarda_git  # noqa: E402
    erros = []
    if antes[0] != depois[0]:
        erros.append("a árvore de trabalho mudou durante a suíte (git status):\n" + depois[0][1])
    dif = guarda_git.diferenca(antes[1], depois[1])
    if dif:
        erros.append("o .git/config comum mudou durante a suíte:\n" + dif)
    return erros


def ao_sinal(numero, _frame):
    raise Interrompido(numero)


def encerrar(filhos):
    """TERM no grupo de cada filho, espera e, se preciso, KILL; nunca toca processo de fora destes grupos."""
    for p in filhos:
        if p.poll() is None:
            try:
                os.killpg(p.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    limite = time.monotonic() + ESPERA_TERMINO_S
    for p in filhos:
        try:
            p.wait(timeout=max(0.1, limite - time.monotonic()))
        except subprocess.TimeoutExpired:
            pass
    for p in filhos:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        p.wait()


def entrada_do_processo(parte, plano):
    """O que o processo recebe: o nome, para o módulo inteiro, ou a unidade com o módulo e as posições dos testes."""
    entrada = []
    for unidade in parte:
        modulo, posicoes = plano.get(unidade, (unidade, None))
        entrada.append(unidade if posicoes is None else {"unidade": unidade, "modulo": modulo, "posicoes": posicoes})
    return entrada


def lancar(partes, pasta, filhos, plano=None):
    """Lança um processo por parte; cada um entra em `filhos` assim que nasce (o sinal pode chegar no meio)."""
    env_base = dict(os.environ)
    for i, parte in enumerate(partes, 1):
        tmp = pasta / f"p{i}"
        tmp.mkdir(mode=0o700)
        (pasta / f"p{i}.entrada.json").write_text(json.dumps(entrada_do_processo(parte, plano or {})), encoding="utf-8")
        log = (pasta / f"p{i}.log").open("w", encoding="utf-8")
        env = dict(env_base, TMPDIR=str(tmp))
        try:
            filhos.append(subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), "--processo", str(pasta / f"p{i}.entrada.json"),
                 str(pasta / f"p{i}.saida.json")], cwd=RAIZ, env=env, stdin=subprocess.DEVNULL, stdout=log,
                stderr=subprocess.STDOUT, start_new_session=True))
        finally:
            log.close()


class TemposAoVivo:
    """Lê `p<i>.saida.json.tempos` (escrito pelos filhos) e imprime, no stderr e com flush, uma linha por unidade que
    termina; `rodando()` diz as que ainda não terminaram. Só informa: não entra no veredito nem na saída final."""

    def __init__(self, pasta, quantos):
        self.arquivos = [pasta / f"p{i}.saida.json.tempos" for i in range(1, quantos + 1)]
        self.posicao = [0] * quantos
        self.abertas = [{} for _ in range(quantos)]

    def atualizar(self):
        for i, arquivo in enumerate(self.arquivos):
            try:
                with arquivo.open("rb") as f:
                    f.seek(self.posicao[i])
                    novo = f.read()
            except OSError:
                continue
            completo = novo.rpartition(b"\n")[0]
            if not completo:
                continue
            for bruta in completo.split(b"\n"):  # a posição avança a cada linha tratada: um sinal no meio não a perde
                tipo, _, resto = bruta.decode("utf-8", "replace").partition("\t")
                nome, _, valor = resto.partition("\t")
                if tipo == "inicio":
                    self.abertas[i][nome] = valor
                elif tipo == "fim":
                    self.abertas[i].pop(nome, None)
                    self.informar(f"suite-paralela: unidade {nome} {valor} s (processo {i + 1})")
                self.posicao[i] += len(bruta) + 1

    @staticmethod
    def informar(texto):
        try:
            print(texto, file=sys.stderr, flush=True)
        except OSError:  # stderr quebrado (pipe fechado, sem terminal): só informa, não derruba a suíte
            pass

    def rodando(self):
        agora, saida = time.time(), []
        for i, abertas in enumerate(self.abertas):
            for nome, desde in abertas.items():
                try:
                    saida.append((nome, agora - float(desde), i + 1))
                except ValueError:
                    continue
        return sorted(saida, key=lambda x: -x[1])

    def imprimir_rodando(self):
        self.atualizar()
        for nome, segundos, i in self.rodando():
            self.informar(f"suite-paralela: rodando {nome} há {segundos:.1f} s (processo {i})")


def esperar(filhos, inicio, tempos=None):
    """Espera todos; devolve o tempo de parede de cada um, contado do início da suíte."""
    fim = [None] * len(filhos)
    while None in fim:
        if tempos:
            tempos.atualizar()
        for i, p in enumerate(filhos):
            if fim[i] is None and p.poll() is not None:
                fim[i] = time.monotonic() - inicio
        time.sleep(0.2)
    for p in filhos:  # um a um, pelo pid: o código de saída de cada filho conta, não o do último
        p.wait()
    if tempos:
        tempos.atualizar()
    return fim


def ler_relatorio(caminho):
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return dados if isinstance(dados, dict) and isinstance(dados.get("ids"), list) else None


def resumir(partes, filhos, relatorios, duracoes, pasta):
    """Imprime os logs (os que falharam primeiro) e o resumo por processo; devolve os erros por processo."""
    erros, linhas = [], []
    ordem = sorted(range(len(partes)), key=lambda i: (filhos[i].returncode == 0 and bool(relatorios[i]), i))
    no_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    for i in ordem:
        if no_ci:
            print(f"::group::processo {i + 1} ({', '.join(partes[i])})", flush=True)
        else:
            print(f"--- processo {i + 1} ({', '.join(partes[i])}) ---", flush=True)
        print((pasta / f"p{i + 1}.log").read_text(encoding="utf-8", errors="replace").rstrip(), flush=True)
        if no_ci:
            print("::endgroup::", flush=True)
    for i, (parte, p, rel) in enumerate(zip(partes, filhos, relatorios), 1):
        rodados = rel["rodados"] if rel else 0
        linhas.append(f"processo {i}: rc {p.returncode}, {rodados} testes, {duracoes[i - 1]:.1f} s, "
                      f"{len(parte)} unidades")
        if p.returncode != 0:
            causa = f"morto pelo sinal {-p.returncode}" if p.returncode < 0 else f"saiu com {p.returncode}"
            erros.append(f"processo {i} {causa}")
        elif rel is None:
            erros.append(f"processo {i} não deixou o relatório")
        elif rodados == 0:
            erros.append(f"processo {i} rodou zero testes")
    print("\n" + "\n".join(linhas), flush=True)
    return erros, linhas


def lista_curta(nomes, limite):
    return ", ".join(nomes[:limite]) + (f" e mais {len(nomes) - limite}" if len(nomes) > limite else "")


def testes_que_cairam(relatorios):
    """QA-1: as linhas do resumo com os IDs que caíram (falha ou erro), sem a mensagem; cada ID cortado em 200 caracteres,
    só imprimíveis e sem crase (não fecha o código do Markdown), até LIMITE_CAIDOS e a contagem do resto."""
    caidos = sorted({str(i) for rel in relatorios if rel for i in rel.get("caidos", ()) or ()})
    if not caidos:
        return []
    linhas = ["", f"#### Testes que caíram ({len(caidos)})"]
    linhas += ["- `" + "".join(c for c in i[:200] if c.isprintable() and c != "`") + "`" for i in caidos[:LIMITE_CAIDOS]]
    if len(caidos) > LIMITE_CAIDOS:
        linhas.append(f"- e mais {len(caidos) - LIMITE_CAIDOS} (a lista inteira está no log do passo)")
    return linhas


def montar_resumo(veredito, linhas, partes, relatorios, duracoes, pesos, total, segundos):
    """O texto do resumo do passo (Markdown): só nomes de unidade e números, nunca portão. O veredito vem primeiro; a
    execução reprovada não leva as linhas da medida e não vale para o orçamento (N-CI, C-7, C-9 a C-12)."""
    n = len(partes)
    nomes = {m for parte in partes for m in parte}
    texto = [f"### Suíte do Forge: {veredito}: {total} testes em {segundos:.1f} s ({n} processos)", ""]
    texto += [f"- {linha}" for linha in linhas]
    unidades = {k: float(v) for rel in relatorios if rel and isinstance(rel.get("duracoes"), dict)
                for k, v in rel["duracoes"].items() if k in nomes and isinstance(v, (int, float)) and v >= 0}
    sem_duracao = sorted(nomes - set(unidades))
    if sem_duracao:
        texto.append(f"- sem duração: {lista_curta(sem_duracao, LIMITE_SEM_DURACAO)}")
    if veredito.startswith("FAILED"):
        texto.append("- execução reprovada: não vale para o orçamento")
        texto += testes_que_cairam(relatorios)
        return "\n".join(texto) + "\n"
    media = sum(duracoes) / n
    desequilibrio = max(duracoes) - media
    lentas = sorted(unidades.items(), key=lambda par: (-par[1], par[0]))
    texto += ["", f"#### Dez unidades mais lentas (de {len(unidades)})"]
    texto += [f"- {nome}: {seg:.1f} s" for nome, seg in lentas[:LIMITE_LENTAS]]
    soma = sum(unidades.values())
    texto.append(f"- soma das unidades: {soma:.1f} s; soma ÷ {n} processos: {soma / n:.1f} s")
    if lentas:
        texto.append(f"- maior unidade: {lentas[0][0]} ({lentas[0][1]:.1f} s)")
    texto.append(f"- desequilíbrio: {desequilibrio:.1f} s ({desequilibrio / (media or 1) * 100:.0f}% da média dos processos)")
    sem_peso = sorted(nomes - set(pesos))
    if sem_peso:
        texto.append(f"- sem peso em {PESOS.relative_to(RAIZ)}: {lista_curta(sem_peso, LIMITE_SEM_PESO)}")
    return "\n".join(texto) + "\n"


def publicar_no_ci(*dados):
    """Acrescenta o resumo ao passo do CI. Roda depois do veredito impresso: qualquer erro daqui vira a linha
    `resumo indisponível` e não muda o código de saída (N-CI, C-6)."""
    destino = os.environ.get("GITHUB_STEP_SUMMARY")
    if not destino:
        return
    try:
        texto = montar_resumo(*dados)
        with open(destino, "a", encoding="utf-8") as f:
            f.write(texto)
    except Exception as e:  # noqa: BLE001 - o resumo é informativo; o veredito já saiu
        print(f"suite-paralela: resumo indisponível ({type(e).__name__})", file=sys.stderr)


def pasta_do_registro():
    """`~/.forge-contrib/` se já existe como pasta do próprio usuário, sem link e sem escrita de outros; senão None (a
    suíte não cria a pasta nem escreve onde não deve: L32, C-32a)."""
    pasta = Path.home() / REGISTRO_PASTA
    try:
        info = pasta.lstat()
    except OSError:
        return None
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o022:
        return None
    return pasta


def registrar_vermelha(relatorios, carga, memoria, causas=()):
    """Suíte vermelha: acrescenta ao registro fora do git uma linha com a carga e os testes que caíram, cada um com a
    taxa (vezes em que caiu / suíte vermelhas registradas). Só ids e números, nunca a mensagem da falha (C-32b); a exceção são
    as causas tipadas (O7, 0.44.1): tipo, local e o esperado e obtido do assertEqual, cortados e com segredos redigidos.
    Roda depois do veredito impresso: qualquer erro daqui vira uma linha em stderr e não muda o código de saída (C-32a)."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return
    try:
        pasta = pasta_do_registro()
        if pasta is None:
            return
        caidos = sorted({i for rel in relatorios if rel is not None for i in rel.get("caidos", ())})[:LIMITE_REGISTRO]
        caidos = ["".join(c for c in str(i)[:200] if c.isprintable()) for i in caidos]
        arquivo = pasta / REGISTRO
        antes = collections.Counter()
        vermelhas = 0
        try:
            if not arquivo.is_symlink():
                for linha in arquivo.read_text(encoding="utf-8").splitlines()[-LINHAS_LIDAS:]:
                    vermelhas += 1
                    antes.update(t["id"] for t in json.loads(linha).get("testes", ()))
        except (OSError, ValueError, KeyError, TypeError):
            pass
        registro = {"quando": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "carga": carga, "memoria_gb": None if memoria is None else round(memoria, 1),
                    "vermelhas": vermelhas + 1,
                    "testes": [{"id": i, "vezes": antes[i] + 1, "de": vermelhas + 1} for i in caidos],
                    "causas": list(causas)[:LIMITE_REGISTRO]}
        fd = os.open(arquivo, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    except Exception as e:  # noqa: BLE001 - o registro é informativo; o veredito já saiu
        print(f"suite-paralela: registro indisponível ({type(e).__name__})", file=sys.stderr)


def gravar_pesos(relatorios):
    pesos = ler_pesos()
    for rel in relatorios:
        pesos.update(rel["duracoes"])
    vivos = set(modulos())
    pesos = {k: round(v, 1) for k, v in sorted(pesos.items())
             if k in vivos or any(k.startswith(m + ".") for m in vivos)}
    PESOS.write_text(json.dumps(pesos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def dividir(todos, pesos, n):
    """Planeja as unidades e as reparte em até `n` processos. Devolve (plano, nomes, partes, erros da divisão)."""
    plano = planejar(todos, pesos, lambda nome: [t.id() for t in achatar(suite_do_modulo(nome))])
    nomes = sorted(plano)
    partes = repartir(nomes, pesos, min(n, max(1, len(nomes))))
    erros = conferir_particao(nomes, partes)
    repetidos = nomes_de_arquivo_repetidos(todos)
    if repetidos:
        erros.append(f"nome de arquivo repetido em tests/ e nos pacotes dela: {', '.join(repetidos)}")
    return plano, nomes, partes, erros


def rodar_partes(partes, plano, inicio, esperado, antes):
    """Lança os processos, espera e junta os relatórios numa pasta temporária. Devolve (filhos, relatórios, erros, linhas,
    durações). No sinal, encerra os processos, avisa e repassa o `Interrompido`."""
    pasta = Path(tempfile.mkdtemp(prefix="forge-suite-"))
    filhos = []
    tempos = TemposAoVivo(pasta, len(partes))
    anteriores = {s: signal.signal(s, ao_sinal) for s in SINAIS}
    try:
        lancar(partes, pasta, filhos, plano)
        duracoes = esperar(filhos, inicio, tempos)
        for s, h in anteriores.items():
            signal.signal(s, h)
        relatorios = [ler_relatorio(pasta / f"p{i}.saida.json") for i in range(1, len(filhos) + 1)]
        erros, linhas = resumir(partes, filhos, relatorios, duracoes, pasta)
        executado = collections.Counter(i for rel in relatorios if rel for i in rel["ids"])
        erros += conferir_completude(esperado, executado)
        erros += conferir_arvore(antes, estado_da_arvore())
        return filhos, relatorios, erros, linhas, duracoes
    except Interrompido as e:
        for s in SINAIS:
            signal.signal(s, signal.SIG_IGN)
        encerrar(filhos)
        tempos.imprimir_rodando()  # depois de encerrar: se o stderr quebrou, nenhum filho fica vivo; os arquivos ainda existem
        print(f"suite-paralela: interrompida pelo sinal {e.numero}; os processos da suíte foram encerrados.",
              file=sys.stderr)
        print("FAILED (interrompida)")
        raise
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


def decidir_veredito(relatorios, erros, linhas, hash_arvore, pulados):
    """Veredito e código da rodada: vermelho com falha, erro ou guarda; senão o teto de pulados, e só então o verde."""
    falhas = sum(rel["falhas"] for rel in relatorios if rel)
    erros_t = sum(rel["erros"] for rel in relatorios if rel)
    if erros or falhas or erros_t:
        for erro in erros:
            print(f"suite-paralela: {erro}", file=sys.stderr)
        detalhes = [f"failures={falhas}"] * bool(falhas) + [f"errors={erros_t}"] * bool(erros_t) \
            + [f"skipped={pulados}"] * bool(pulados) + ["guarda=" + str(len(erros))] * bool(erros)
        return f"FAILED ({', '.join(detalhes)})", 1
    # o teto antes de fechar_verde: estourado não regrava pesos nem carimbo (T3)
    veredito = conferir_teto(relatorios, pulados, linhas)
    return (veredito, 1) if veredito else (fechar_verde(relatorios, hash_arvore, pulados), 0)


def orquestrar():
    os.chdir(RAIZ)
    inicio = time.monotonic()
    carga, memoria, total_gb = medir_carga()
    try:
        n, origem = numero_de_processos(os.environ, os.cpu_count(), carga, memoria, total_gb)
    except ValueError as e:
        print(f"suite-paralela: {e}.", file=sys.stderr)
        print("FAILED (configuração)")
        return 1
    esperado = ids(descobrir())
    total = sum(esperado.values())
    pesos = ler_pesos()
    plano, nomes, partes, erros = dividir(modulos(), pesos, n)
    if erros or not nomes:
        print("suite-paralela: " + ("; ".join(erros) or "nenhum módulo de teste em tests/") + ".", file=sys.stderr)
        print("FAILED (divisão)")
        return 1
    print(f"suite-paralela: {total} testes em {len(modulos())} módulos ({len(nomes)} unidades), {len(partes)} processos "
          f"({origem}).",
          file=sys.stderr, flush=True)
    antes = estado_da_arvore()
    hash_arvore = hash_da_arvore(RAIZ)
    try:
        filhos, relatorios, erros, linhas, duracoes = rodar_partes(partes, plano, inicio, esperado, antes)
    except Interrompido as e:
        return 128 + e.numero
    segundos = time.monotonic() - inicio
    rodados = sum(rel["rodados"] for rel in relatorios if rel)
    print(f"\nRan {rodados} tests in {segundos:.3f}s ({len(partes)} processos)\n")
    pulados = sum(rel["pulados"] for rel in relatorios if rel)
    veredito, codigo = decidir_veredito(relatorios, erros, linhas, hash_arvore, pulados)
    causas = imprimir_causas(filhos, relatorios)
    print(veredito)
    publicar_no_ci(veredito, linhas, partes, relatorios, duracoes, pesos, rodados, segundos)
    if codigo:
        registrar_vermelha(relatorios, carga, memoria, causas)
    return codigo


def ler_teto(caminho=CONFIG):
    """`teto_pulados` de tests/config.json, inteiro de verdade e >= 0; None se falta, tem outro tipo ou o arquivo não lê
    (falha fechada: None nunca vale como "sem teto")."""
    try:
        teto = json.loads(Path(caminho).read_text(encoding="utf-8")).get("teto_pulados")
    except (OSError, ValueError, AttributeError):
        return None
    return teto if type(teto) is int and teto >= 0 else None


def neutro(texto):
    """Id de teste para o resumo e o log: sem caracteres de controle e de formato, `|`, crase nem `::`; cortado."""
    texto = "".join(c for c in str(texto)[:200] if unicodedata.category(c) not in ("Cc", "Cf", "Co", "Cs"))
    return texto.replace("|", " ").replace("`", " ").replace("::", ": ")


def pulados_ids(relatorios):
    """Os ids pulados de todos os relatórios, neutros e ordenados."""
    return sorted(neutro(i) for rel in relatorios if rel for i in rel.get("pulados_ids", ()))


def comparar_teto(pulados, ids, teto, linhas, quem="suite-paralela"):
    """"" ou o veredito FAILED de `pulados` contra `teto` (None: ilegível); acima do teto, os ids (até 20) vão às linhas
    do resumo. O agregador das partes (`suite-partes.py --somar-pulados`) usa a mesma conta."""
    if teto is None:
        print(f"{quem}: teto_pulados ausente ou inválido em {TESTES}/config.json.", file=sys.stderr)
        return "FAILED (teto de pulados ilegível)"
    if pulados > teto:
        linhas.append(f"pulados acima do teto: {lista_curta(ids, LIMITE_PULADOS)}")
        print(f"{quem}: {linhas[-1]}", file=sys.stderr)
        return f"FAILED (skipped={pulados} acima do teto {teto})"
    if pulados < teto:
        print(f"{quem}: o teto de pulados pode cair para {pulados}", file=sys.stderr)
    return ""


def conferir_teto(relatorios, pulados, linhas):
    """T3: "" ou o veredito FAILED do teto de pulados. Só reprova no CI, onde a contagem é a do runner (localmente o
    root pula os testes de permissão)."""
    teto = ler_teto()
    if os.environ.get("GITHUB_ACTIONS") != "true":
        print(f"suite-paralela: pulados {pulados} (teto {'ilegível' if teto is None else teto}; só reprova no CI).",
              file=sys.stderr)
        return ""
    return comparar_teto(pulados, pulados_ids(relatorios), teto, linhas)


def fechar_verde(relatorios, hash_arvore, pulados):
    """O que só vale depois do veredito verde (pesos regravados, carimbo K6); devolve a linha do veredito."""
    if os.environ.get("FORGE_SUITE_MEDIR") == "1":
        gravar_pesos(relatorios)
        print(f"suite-paralela: pesos regravados em {PESOS.relative_to(RAIZ)}.", file=sys.stderr)
    if hash_da_arvore(RAIZ) == hash_arvore:  # commit no meio da suíte: o carimbo seria de outra árvore
        gravar_carimbo(RAIZ, hash_arvore)
    return f"OK (skipped={pulados})" if pulados else "OK"


def conferir_trava(caminho, donos):
    """"" se a trava `caminho` está presa e anotada por um dos `donos` (o hook que chamou o script ou, no modo
    `--suite`, o próprio processo, que tomou o lugar do hook); senão, o motivo."""
    trava = Path(caminho)
    try:
        if trava.is_symlink() or not trava.is_file() or trava.stat().st_uid != os.getuid():
            return f"{caminho} não é um arquivo do próprio usuário"
        anotado = trava.read_text(encoding="utf-8", errors="replace").split()[:2]
        if len(anotado) != 2 or anotado[0] != "pid" or anotado[1] not in {str(d) for d in donos}:
            return f"a trava {caminho} não é do processo que chamou o script"
        with trava.open("rb") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return ""
            fcntl.flock(f, fcntl.LOCK_UN)
            return f"a trava {caminho} não está presa"
    except OSError as e:
        return f"não consegui conferir a trava {caminho}: {e}"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) == 3 and argv[0] == "--processo":
        return processo(argv[1], argv[2])
    if argv:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    caminho = os.environ.get("FORGE_SUITE_TRAVA")
    if not caminho:
        igual = reuso(RAIZ, os.environ)
        if igual:
            print(f"suite: reusa {igual[0]} de {igual[1]}")
            print("OK")
            return 0
    if not caminho:  # à mão: pela mesma trava e pela mesma fila do pre-push
        if not os.access(HOOK, os.X_OK):
            print(f"suite-paralela: sem {HOOK.relative_to(RAIZ)} para pegar a trava da suíte (R-TETO).", file=sys.stderr)
            print("FAILED (trava)")
            return 1
        os.chdir(RAIZ)
        sys.stdout.flush()
        os.execv(str(HOOK), [str(HOOK), "--suite"])
    motivo = conferir_trava(caminho, (os.getppid(), os.getpid()))
    if motivo:
        print(f"suite-paralela: FORGE_SUITE_TRAVA: {motivo}; a suíte não roda sem a trava (R-TETO).", file=sys.stderr)
        print("FAILED (trava)")
        return 1
    return orquestrar()


if __name__ == "__main__":
    sys.exit(main())
