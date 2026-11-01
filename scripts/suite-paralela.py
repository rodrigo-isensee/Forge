#!/usr/bin/env python3
"""Forge: a suíte inteira (`python3 -m unittest discover -s tests`) dividida em até 4 processos (D4, R-TETO).

Uso: python3 scripts/suite-paralela.py
Chamado pelo `.githooks/pre-push` e pelo CI. Só biblioteca padrão; nada de rede nem de custo (R-CUSTO).

- Divisão por módulo (`tests/test*.py`), por LPT sobre os pesos de `tests/pesos-d4.json` (módulo -> segundos);
  peso ausente vale a mediana. O peso só equilibra: nunca decide o que roda. A mesma árvore dá a mesma divisão.
- Processos: N = min(4, nproc); com carga alta (load de 1 min >= 0,8 x nproc ou memória disponível no piso), 2.
  FORGE_SUITE_PROCS fixa N de 1 a 4; fora disso o script recusa (falha fechada).
- Cada processo roda com `nice`, num grupo de processos próprio e com um TMPDIR próprio (modo 700), apagado ao fim.
- Guarda de completude (falha fechada): a soma e a união (multiconjunto) dos IDs que os processos rodaram têm de
  ser iguais às do `discover` da suíte inteira; processo que sai com código diferente de 0, morre por sinal, roda
  zero testes ou não deixa o relatório reprova. Também reprova se a árvore de trabalho (`git status`) ou o
  `.git/config` comum mudarem durante a suíte.
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
- FORGE_SUITE_MEDIR=1 regrava `tests/pesos-d4.json` com as durações da execução, se tudo passou.
A última linha é `OK` (ou `OK (skipped=N)`) ou `FAILED (...)`, como no `unittest`.
"""
import collections
import datetime
import fcntl
import hashlib
import json
import os
import shutil
import signal
import statistics
import subprocess
import sys
import tempfile
import threading
import time
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
LIMITE_LENTAS, LIMITE_SEM_PESO, LIMITE_SEM_DURACAO = 10, 20, 20  # o resumo do CI é curto (N-CI, C-11)


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
    """Os módulos de teste da raiz de `tests/`; a guarda de completude confere esta lista contra o `discover`."""
    return sorted(p.stem for p in (RAIZ / TESTES).glob("test*.py") if p.stem.isidentifier())


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


def processo(entrada, saida):
    os.nice(10)
    threading.Thread(target=vigiar_pai, args=(os.getppid(),), daemon=True).start()
    nomes = json.loads(Path(entrada).read_text(encoding="utf-8"))
    verbosidade = 2 if os.environ.get("GITHUB_ACTIONS") == "true" else 1
    resultado = Resultado(unittest.runner._WritelnDecorator(sys.stderr), True, verbosidade)
    duracoes = {}
    resultado.startTestRun()
    try:
        for nome in nomes:
            inicio = time.monotonic()
            descobrir(f"{nome}.py").run(resultado)
            duracoes[nome] = round(time.monotonic() - inicio, 1)
    finally:
        resultado.stopTestRun()
    resultado.printErrors()
    sys.stderr.write(f"\nRan {resultado.testsRun} tests\n")
    relatorio = {"ids": resultado.ids, "rodados": resultado.testsRun, "falhas": len(resultado.failures),
                 "erros": len(resultado.errors), "pulados": len(resultado.skipped),
                 "esperados": len(resultado.expectedFailures), "inesperados": len(resultado.unexpectedSuccesses),
                 "ok": resultado.wasSuccessful(), "duracoes": duracoes}
    Path(saida).write_text(json.dumps(relatorio), encoding="utf-8")
    return 0 if resultado.wasSuccessful() else 1


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


def lancar(partes, pasta, filhos):
    """Lança um processo por parte; cada um entra em `filhos` assim que nasce (o sinal pode chegar no meio)."""
    env_base = dict(os.environ)
    for i, parte in enumerate(partes, 1):
        tmp = pasta / f"p{i}"
        tmp.mkdir(mode=0o700)
        (pasta / f"p{i}.entrada.json").write_text(json.dumps(parte), encoding="utf-8")
        log = (pasta / f"p{i}.log").open("w", encoding="utf-8")
        env = dict(env_base, TMPDIR=str(tmp))
        try:
            filhos.append(subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), "--processo", str(pasta / f"p{i}.entrada.json"),
                 str(pasta / f"p{i}.saida.json")], cwd=RAIZ, env=env, stdin=subprocess.DEVNULL, stdout=log,
                stderr=subprocess.STDOUT, start_new_session=True))
        finally:
            log.close()


def esperar(filhos, inicio):
    """Espera todos; devolve o tempo de parede de cada um, contado do início da suíte."""
    fim = [None] * len(filhos)
    while None in fim:
        for i, p in enumerate(filhos):
            if fim[i] is None and p.poll() is not None:
                fim[i] = time.monotonic() - inicio
        time.sleep(0.2)
    for p in filhos:  # um a um, pelo pid: o código de saída de cada filho conta, não o do último
        p.wait()
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
                      f"{len(parte)} módulos")
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


def gravar_pesos(relatorios):
    pesos = ler_pesos()
    for rel in relatorios:
        pesos.update(rel["duracoes"])
    vivos = set(modulos())
    pesos = {k: round(v, 1) for k, v in sorted(pesos.items()) if k in vivos}
    PESOS.write_text(json.dumps(pesos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
    nomes = modulos()
    pesos = ler_pesos()
    partes = repartir(nomes, pesos, min(n, max(1, len(nomes))))
    erros = conferir_particao(nomes, partes)
    if erros or not nomes:
        print("suite-paralela: " + ("; ".join(erros) or "nenhum módulo de teste em tests/") + ".", file=sys.stderr)
        print("FAILED (divisão)")
        return 1
    print(f"suite-paralela: {total} testes em {len(nomes)} módulos, {len(partes)} processos ({origem}).",
          file=sys.stderr, flush=True)
    antes = estado_da_arvore()
    hash_arvore = hash_da_arvore(RAIZ)
    pasta = Path(tempfile.mkdtemp(prefix="forge-suite-"))
    filhos = []
    anteriores = {s: signal.signal(s, ao_sinal) for s in SINAIS}
    try:
        lancar(partes, pasta, filhos)
        duracoes = esperar(filhos, inicio)
        for s, h in anteriores.items():
            signal.signal(s, h)
        relatorios = [ler_relatorio(pasta / f"p{i}.saida.json") for i in range(1, len(filhos) + 1)]
        erros, linhas = resumir(partes, filhos, relatorios, duracoes, pasta)
        executado = collections.Counter(i for rel in relatorios if rel for i in rel["ids"])
        erros += conferir_completude(esperado, executado)
        erros += conferir_arvore(antes, estado_da_arvore())
    except Interrompido as e:
        for s in SINAIS:
            signal.signal(s, signal.SIG_IGN)
        encerrar(filhos)
        print(f"suite-paralela: interrompida pelo sinal {e.numero}; os processos da suíte foram encerrados.",
              file=sys.stderr)
        print("FAILED (interrompida)")
        return 128 + e.numero
    finally:
        shutil.rmtree(pasta, ignore_errors=True)
    segundos = time.monotonic() - inicio
    rodados = sum(rel["rodados"] for rel in relatorios if rel)
    print(f"\nRan {rodados} tests in {segundos:.3f}s ({len(partes)} processos)\n")
    falhas = sum(rel["falhas"] for rel in relatorios if rel)
    erros_t = sum(rel["erros"] for rel in relatorios if rel)
    pulados = sum(rel["pulados"] for rel in relatorios if rel)
    if erros or falhas or erros_t:
        for erro in erros:
            print(f"suite-paralela: {erro}", file=sys.stderr)
        detalhes = [f"failures={falhas}"] * bool(falhas) + [f"errors={erros_t}"] * bool(erros_t) \
            + [f"skipped={pulados}"] * bool(pulados) + ["guarda=" + str(len(erros))] * bool(erros)
        veredito, codigo = f"FAILED ({', '.join(detalhes)})", 1
    else:
        veredito, codigo = fechar_verde(relatorios, hash_arvore, pulados), 0
    print(veredito)
    publicar_no_ci(veredito, linhas, partes, relatorios, duracoes, pesos, rodados, segundos)
    return codigo


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
