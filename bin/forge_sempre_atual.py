"""FORGE-SEMPRE-ATUAL (v047, diretriz 30, ADR 0017): o núcleo que mantém o plugin do Forge na última versão publicada.

Desenho em `docs/arquitetura/forge-sempre-atual.md` (seções 1 a 5, 8 e 10). Chamado só pelo atalho do dono e pelo postStart do
container (`bin/forge-sempre-atual --gatilho atalho|poststart`), nunca de dentro do Claude. Fluxo de uma rodada:
  1. estado em `~/.claude/plugins/data/forge-forge/forge/sempre-atual/` (pasta 0700, recusa link simbólico);
  2. escopos de `claude plugin list --json`; escopo ocupado (sessão tmux, agente vigente com `claude` vivo, trava `pesado`, suíte,
     integração) ou em dúvida (leitura que falha, /proc incoerente) é adiado e registrado;
  3. alvo = a maior tag `vX.Y.Z` (ou a fixação vigente); o catálogo é fixado nele por `marketplace add <url>#v<alvo> --scope user`
     sobre o existente (nunca `marketplace remove`), e só com o `ref` lido igual ao alvo vem o `plugin update` de cada escopo;
  4. checagem de início (C-INI) da versão instalada quando difere da última boa; reprovada, volta à última boa pelo mesmo mecanismo,
     grava a fixação automática e deixa o aviso pendente;
  5. com o plugin acima do `.forge/versao` da `origin/develop`, prepara a branch local `forge/upgrade-<v>` numa worktree temporária.
A ferramenta não faz `git push`, não chama `gh`, não encerra processo nem sessão, não grava `settings.json` nem
`known_marketplaces.json` (só a CLI grava), não usa `GH_TOKEN` e não chama o modelo. Falha de qualquer passo vira `falhou:<etapa>`
no registro e a rodada termina limpa: o atalho abre o Claude de qualquer jeito.
"""
import argparse
import fcntl
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import forge_versoes as fv

ESTADO = ("plugins", "data", "forge-forge", "forge", "sempre-atual")
PROC = "/proc"
ORCAMENTO_PADRAO = 60
LIMITE_JSON = 1024 * 1024
LINHAS_DO_REGISTRO = 500
PRAZO_CINI = 30
PRAZO_LEITURA = 10
PRAZO_REDE = 15
RESUMO_MAX = 160
GATILHOS = ("atalho", "poststart")
CASCA = ("project", "local")
# O que os filhos herdam (lista positiva, AR-3): o necessário para achar programa, casa e pasta temporária, falar português, passar
# por proxy e certificado da rede e usar o agente de chave do dono num remoto ssh. O resto, GH_TOKEN e qualquer segredo, fica de fora.
HERDA = frozenset({"HOME", "PATH", "TMPDIR", "USER", "LOGNAME", "LANG", "LANGUAGE", "TERM", "SSH_AUTH_SOCK", "SSL_CERT_FILE", "SSL_CERT_DIR",
                   "CURL_CA_BUNDLE", "NODE_EXTRA_CA_CERTS", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY", "http_proxy",
                   "https_proxy", "all_proxy", "no_proxy"})
HERDA_PREFIXO = ("LC_", "XDG_")
TAG = re.compile(r"v(\d+)\.(\d+)\.(\d+)")
VERSAO = re.compile(r"(\d+)\.(\d+)\.(\d+)")
SCRIPTS_SH = ("scripts/jarvis", "scripts/jarvis-forge", "scripts/preparar-estacao.sh", "bin/forge")
# A trava da suíte do Forge é por usuário (`.githooks/pre-push`, R-TETO): quem a confere é a cópia instalada que roda esta
# ferramenta, nunca o arquivo da pasta de um projeto, que um agente pode gravar (ADR 0017 item 9, SEG-1).
GANCHO_DA_SUITE = Path(__file__).resolve().parent.parent / ".githooks" / "pre-push"
# Os `git` que a ferramenta roda num repositório (o do projeto, o temporário da origem da tag, o `forge-upgrade`) não rodam hook.
SEM_HOOKS = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.hooksPath", "GIT_CONFIG_VALUE_0": os.devnull}

# Lê o estado dos agentes com o código da versão ativa (S3 e S4); só leitura, num processo à parte e com prazo.
LEITOR_DE_AGENTES = r'''import json, sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import agentes
raiz, agora = Path(sys.argv[2]), time.time()
hook = agentes.Hook("agentes")
hook.raiz = raiz
caminho = agentes.arquivo_de_estado(raiz)
n = 0
if caminho is not None and Path(caminho).exists():
    estado = json.loads(Path(caminho).read_text(encoding="utf-8"))
    n = len(agentes.vigentes(estado["agentes"], agora, hook.expira_s()))
if agentes.e_clone_do_forge(raiz):
    pasta = agentes.pasta_de_estado_do_clone(raiz)
else:
    pasta = hook.copia_principal() / ".forge" / "run"
trava = {}
if pasta is not None and (pasta / "pesado.json").exists():
    texto = (pasta / "pesado.json").read_text(encoding="utf-8")
    trava = json.loads(texto) if texto.strip() else None
    trava = {} if trava is None else trava
desde = trava.get("desde")
pesado = isinstance(desde, (int, float)) and agora - desde < agentes.TRAVA_S and bool(agentes.pid_vivo(trava.get("pid"), trava.get("inicio")))
print(json.dumps({"n": n, "pesado": pesado}))
'''


class Prazo(Exception):
    """O orçamento da rodada acabou."""


class EstadoRecusado(Exception):
    """A pasta de estado não é segura (link simbólico, outro dono, não é pasta)."""


def versao_tupla(texto):
    achou = VERSAO.fullmatch(str(texto).strip()) if isinstance(texto, str) else None
    return tuple(int(x) for x in achou.groups()) if achou else None


def versao_texto(tupla):
    return ".".join(str(n) for n in tupla)


def maior_tag(saida):
    """A maior versão `vX.Y.Z` (tupla) de uma saída de `git ls-remote --tags`; rc, nome solto e pré-lançamento não contam."""
    achadas = []
    for linha in saida.splitlines():
        _, _, ref = linha.partition("\t")
        achou = TAG.fullmatch(ref.strip().removeprefix("refs/tags/"))
        if achou:
            achadas.append(tuple(int(x) for x in achou.groups()))
    return max(achadas) if achadas else None


def resumo(texto):
    """Uma linha curta e sem segredo: credencial em URL e token de forma conhecida saem, controle vira espaço."""
    texto = re.sub(r"://[^/@\s]*@", "://", str(texto))
    texto = re.sub(r"\b(gh[pousr]_|github_pat_|sk-)[A-Za-z0-9_]{6,}", "***", texto)
    texto = re.sub(r"[\x00-\x1f\x7f]+", " ", texto).strip()
    return texto[:RESUMO_MAX]


def hoje():
    return time.strftime("%Y-%m-%d")


def ambiente_dos_filhos():
    """O ambiente de todo subprocesso: só o que `HERDA` permite (SEG-3: nem GH_TOKEN nem qualquer outro segredo, nem GIT_*)."""
    env = {k: v for k, v in os.environ.items() if k in HERDA or k.startswith(HERDA_PREFIXO)}
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def dentro(pasta, raiz):
    pasta, raiz = os.path.realpath(pasta), os.path.realpath(raiz)
    return pasta == raiz or pasta.startswith(raiz.rstrip(os.sep) + os.sep)


def raiz_git(cwd):
    """A pasta mais próxima, de cwd para cima, com `.git`; sem ela, o próprio cwd."""
    atual = Path(cwd)
    for pasta in [atual, *list(atual.parents)[:40]]:
        if (pasta / ".git").exists():
            return str(pasta)
    return str(atual)


# Processos (S2 e S6) ---------------------------------------------------------------------------
def proc_coerente():
    """O /proc é o do nosso namespace de pid: `/proc/self` é o nosso pid e o nosso `comm` lê. Fora disso (outro namespace)
    nada do que ele mostra serve de prova de que não há `claude` vivo (decisão do Jarvis, desenho seção 3: na dúvida, adia)."""
    try:
        return os.readlink(f"{PROC}/self") == str(os.getpid()) and bool(Path(f"{PROC}/{os.getpid()}/comm").read_text().strip())
    except OSError:
        return False


def pids_do_proc():
    """Os pids listados no /proc. Função à parte só para o lançador dos testes (`tests/sem_claude_ancestral.py`) a trocar
    pela leitura que vê só os descendentes do teste: as outras partes da suíte rodam ao mesmo tempo e têm `forge-fechar`
    e `claude` falsos vivos, que não são do mundo do teste."""
    return [n for n in os.listdir(PROC) if n.isdigit()]


def processos_de_interesse():
    """{"claude": [cwd...], "fechar": [cwd...], "duvida": bool}: os processos do mesmo usuário que importam. `duvida` quando o
    /proc é incoerente ou o `cwd` de um desses processos não se lê (um que sumiu no meio da leitura não conta como dúvida)."""
    achados = {"claude": [], "fechar": [], "duvida": False}
    if not proc_coerente():
        achados["duvida"] = True
        return achados
    try:
        nomes = pids_do_proc()
    except OSError:
        achados["duvida"] = True
        return achados
    for n in nomes:
        try:
            if os.stat(f"{PROC}/{n}").st_uid != os.getuid():
                continue
            comm = Path(f"{PROC}/{n}/comm").read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            continue
        if comm not in ("claude", "forge-fechar", "gh"):
            continue
        try:
            cwd = os.readlink(f"{PROC}/{n}/cwd")
            linha = Path(f"{PROC}/{n}/cmdline").read_bytes().split(b"\0") if comm == "gh" else []
        except FileNotFoundError:
            continue
        except OSError:
            achados["duvida"] = True
            continue
        if comm == "claude":
            achados["claude"].append(cwd)
        elif comm == "forge-fechar" or (comm == "gh" and b"pr" in linha and b"merge" in linha):
            achados["fechar"].append(cwd)
    return achados


class Rodada:
    def __init__(self, gatilho, projeto=None, orcamento=ORCAMENTO_PADRAO):
        self.gatilho = gatilho
        self.projeto = os.path.realpath(projeto) if projeto and os.path.isdir(projeto) else None
        self.fim = time.monotonic() + float(orcamento)
        self.casa = fv.casa()
        self.env = ambiente_dos_filhos()
        self.neutro = None
        self.claude_bin = None
        self.estado = {}
        self.estado_existia = False
        self.pasta = None
        self.escopos = []
        self.res = {}  # chave do escopo -> {"antes", "depois", "resultado"}
        self.extras = []  # linhas fora de escopo (modelo, sem claude)
        self.url = None
        self.alvo = None
        self.mensagem = []

    # Estado ------------------------------------------------------------------------------------
    def abrir_estado(self):
        base = self.casa / ".claude" / "plugins"
        if not base.is_dir():
            return False
        atual = base
        for nome in ESTADO[1:]:
            atual = atual / nome
            try:
                st = os.lstat(atual)
            except FileNotFoundError:
                os.mkdir(atual, 0o700)
                continue
            if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid():
                raise EstadoRecusado(f"{atual} não é uma pasta própria (link simbólico, outro dono ou arquivo); nada foi gravado")
        os.chmod(atual, 0o700)
        self.pasta = atual
        texto = fv._ler_limitado(atual / "estado.json", LIMITE_JSON)
        try:
            dados = json.loads(texto) if texto is not None else None
        except ValueError:
            dados = None
        self.estado_existia = isinstance(dados, dict)
        self.estado = dados if isinstance(dados, dict) else {}
        for chave, tipo in (("bom", dict), ("adiamentos", dict)):
            if not isinstance(self.estado.get(chave), tipo):
                self.estado[chave] = tipo()
        return True

    def travar(self):
        fd = os.open(self.pasta / ".trava", os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(fd)
            return None
        return fd

    def salvar_estado(self):
        if self.pasta is None:
            return
        tmp = self.pasta / f".estado.json.{os.getpid()}"
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(self.estado, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.pasta / "estado.json")

    def gravar_registro(self):
        if self.pasta is None:
            return
        carimbo = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        linhas = []
        for e in self.escopos:
            r = self.res.get(e["chave"])
            if r:
                linhas.append((e["escopo"], e["projeto"] or "-", r["antes"], r["depois"], r["resultado"]))
        linhas += self.extras
        if not linhas:
            return
        caminho = self.pasta / "registro.log"
        novas = "".join("\t".join([carimbo, self.gatilho, *[resumo(c) or "-" for c in l]]) + "\n" for l in linhas)
        fd = os.open(caminho, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as f:
            f.write(novas)
        texto = fv._ler_limitado(caminho, 4 * LIMITE_JSON)
        if texto is not None and texto.count("\n") > LINHAS_DO_REGISTRO:
            tmp = self.pasta / f".registro.log.{os.getpid()}"
            tmp.write_text("".join(l + "\n" for l in texto.splitlines()[-LINHAS_DO_REGISTRO:]), encoding="utf-8")
            os.chmod(tmp, 0o600)
            os.replace(tmp, caminho)

    # Subprocessos ----------------------------------------------------------------------------
    def restante(self):
        return self.fim - time.monotonic()

    def rodar(self, argv, cwd, cap, extra=None):
        """(rc, saída). rc None: passou do prazo do passo (o filho foi morto); -1: não deu para iniciar. O prazo geral esgotado
        levanta `Prazo`. A saída vai para um arquivo, para um neto vivo nunca prender a leitura. `extra`: variáveis a somar ao
        ambiente dos filhos (só as da própria ferramenta, como `SEM_HOOKS`)."""
        restante = self.restante()
        if restante <= 0:
            raise Prazo()
        limite = min(cap, restante)
        with tempfile.TemporaryFile() as saida:
            try:
                p = subprocess.Popen(argv, cwd=cwd, env={**self.env, **(extra or {})}, stdin=subprocess.DEVNULL, stdout=saida, stderr=subprocess.STDOUT,
                                     start_new_session=True)
            except OSError as erro:
                return -1, str(erro)
            try:
                p.wait(timeout=limite)
            except subprocess.TimeoutExpired:
                p.kill()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
                if limite >= restante:
                    raise Prazo()
                return None, "prazo do passo"
            saida.seek(0)
            texto = saida.read(65536).decode("utf-8", errors="replace").strip()
        return p.returncode, texto

    def achar_claude(self):
        for pasta in self.env.get("PATH", "").split(os.pathsep):
            if pasta and os.path.isabs(pasta):
                achado = os.path.join(pasta, "claude")
                if os.path.isfile(achado) and os.access(achado, os.X_OK):
                    return achado
        local = self.casa / ".local" / "bin" / "claude"
        return str(local) if local.is_file() and os.access(local, os.X_OK) else None

    def bash(self):
        """O bash do PATH dos filhos ou, sem ele (o PATH de teste só com dublês), o do sistema."""
        return shutil.which("bash", path=self.env.get("PATH", "")) or "/bin/bash"

    def claude(self, args, cwd=None, cap=60):
        return self.rodar([self.claude_bin, *args], cwd or self.neutro, cap)

    def git_rede(self, args):
        return self.rodar(["git", "-c", "protocol.allow=never", "-c", "protocol.https.allow=always", *args], self.neutro, PRAZO_REDE,
                          SEM_HOOKS)

    # Leituras da CLI (só leitura) ----------------------------------------------------------------
    def listar(self):
        """Os escopos do `forge@forge`, ou None (a falha fica registrada em todos os resultados)."""
        rc, saida = self.claude(["plugin", "list", "--json"], cap=30)
        try:
            dados = json.loads(saida) if rc == 0 else None
        except ValueError:
            dados = None
        if not isinstance(dados, list):
            self.extras.append(("-", "-", "-", "-", "falhou:lista:" + resumo(saida or "sem resposta")))
            self.mensagem.append(("falhou", "lista"))
            return None
        escopos = []
        for item in dados:
            if not (isinstance(item, dict) and item.get("id") == fv.PLUGIN and item.get("scope") in ("user", "project", "local")):
                continue
            projeto = item.get("projectPath") if isinstance(item.get("projectPath"), str) else ""
            if item["scope"] in CASCA and not projeto:
                continue
            versao = str(item.get("version", ""))
            escopos.append({"escopo": item["scope"], "projeto": projeto, "versao": versao, "install": str(item.get("installPath", "")),
                            "sha": str(item.get("gitCommitSha", "")), "chave": f"{item['scope']}|{projeto}"})
        return escopos

    def ref_atual(self):
        texto = fv._ler_limitado(self.casa / ".claude" / "plugins" / "known_marketplaces.json", LIMITE_JSON)
        try:
            ref = json.loads(texto)["forge"]["source"].get("ref")
        except (TypeError, ValueError, KeyError, AttributeError):
            return None
        return ref if isinstance(ref, str) else None

    def instalacao(self, caminho):
        """O caminho (como a CLI o deu) se é uma pasta do Forge no cache do plugin, não órfã; senão None (SEG-1)."""
        try:
            real = Path(caminho).resolve(strict=True)
        except (OSError, ValueError, RuntimeError):
            return None
        raiz = fv.raiz_do_cache(self.casa)
        if raiz is None or not caminho or not os.path.isabs(caminho) or not fv.pasta_do_forge_valida(real, raiz):
            return None
        return None if (real / ".orphaned_at").exists() else caminho

    def definir(self, e, resultado, depois=None):
        self.res[e["chave"]] = {"antes": e["versao"] or "-", "depois": depois or e["versao"] or "-", "resultado": resultado}

    def falhar(self, escopos, etapa, texto=""):
        resultado = f"falhou:{etapa}" + (f":{resumo(texto)}" if texto else "")
        for e in escopos:
            if e["chave"] not in self.res:
                self.definir(e, resultado)
        self.mensagem.append(("falhou", etapa))

    # Ocupação (seção 3) ------------------------------------------------------------------------
    def sessao_tmux(self):
        """True (aberta), False (não) ou None (dúvida) para `jarvis-<projeto>`."""
        if not self.projeto:
            return False
        nome = "jarvis-" + re.sub(r"[.:]", "_", os.path.basename(self.projeto))
        rc, _ = self.rodar(["tmux", "has-session", "-t", nome], self.neutro, PRAZO_LEITURA)
        return {0: True, 1: False, -1: False}.get(rc)

    def agentes(self, raiz):
        """(n de agentes vigentes, trava pesado viva) com o código da versão ativa; None se não deu para conferir."""
        hooks = Path(__file__).resolve().parent.parent / "hooks"
        rc, saida = self.rodar([sys.executable, "-I", "-c", LEITOR_DE_AGENTES, str(hooks), raiz], self.neutro, PRAZO_LEITURA)
        try:
            dados = json.loads(saida.splitlines()[-1]) if rc == 0 else None
            return int(dados["n"]), bool(dados["pesado"])
        except (ValueError, KeyError, IndexError, TypeError):
            return None

    def suite(self):
        """True (rodando), False (livre) ou None (dúvida) pelo `.githooks/pre-push --status` da cópia instalada (`GANCHO_DA_SUITE`);
        nenhum arquivo da pasta do projeto é executado. Sem o arquivo, o bash sai com 127: dúvida."""
        bash = self.bash()
        rc, _ = self.rodar([bash, str(GANCHO_DA_SUITE), "--status"], self.neutro, PRAZO_LEITURA)
        return {0: True, 1: False}.get(rc)

    def motivo_de_ocupacao(self, raiz, procs):
        """Por que a raiz está ocupada, ou None se está livre."""
        if any(dentro(c, raiz) for c in procs["fechar"]):
            return "integracao"
        if not any(dentro(c, raiz) for c in procs["claude"]):
            return None
        lido = self.agentes(raiz)
        if lido is None:
            return "duvida:leitura-dos-agentes"
        if lido[0] > 0:
            return "agentes"
        if lido[1]:
            return "pesado"
        suite = self.suite()
        if suite is None:
            return "duvida:suite"
        return "suite" if suite else None

    def ocupacao(self, escopos):
        """Marca `adiado:<motivo>` nos escopos ocupados ou em dúvida. Devolve as chaves dos escopos adiados."""
        sessao = self.sessao_tmux()
        procs = processos_de_interesse()
        proprios = [e["projeto"] for e in escopos if e["escopo"] in CASCA]
        adiados = {}
        for e in escopos:
            motivo = None
            cobre_o_aberto = e["escopo"] == "user" or (self.projeto and e["projeto"] and dentro(self.projeto, e["projeto"]))
            if sessao is None and cobre_o_aberto:
                motivo = "duvida:tmux"
            elif sessao and cobre_o_aberto:
                motivo = "sessao-tmux"
            elif procs["duvida"]:
                motivo = "duvida:proc"
            elif e["escopo"] in CASCA:
                motivo = self.motivo_de_ocupacao(e["projeto"], procs)
            else:
                raizes = sorted({raiz_git(c) for c in procs["claude"] if not any(dentro(c, p) for p in proprios)})
                for raiz in raizes:
                    motivo = self.motivo_de_ocupacao(raiz, procs)
                    if motivo:
                        break
                if not motivo and any(not any(dentro(c, p) for p in proprios) for c in procs["fechar"]):
                    motivo = "integracao"
            if motivo:
                adiados[e["chave"]] = e
                self.definir(e, f"adiado:{motivo}")
        return adiados

    def contar_adiamentos(self, avaliados, adiados):
        """Adiamentos seguidos por escopo, com a data do primeiro, para o aviso do doutor não ficar mudo."""
        contagem = self.estado["adiamentos"]
        com_adiamento = {e["escopo"] for e in adiados.values()}
        for escopo in com_adiamento:
            atual = contagem.get(escopo) if isinstance(contagem.get(escopo), dict) else {}
            contagem[escopo] = {"n": int(atual.get("n", 0) or 0) + 1, "desde": atual.get("desde") or hoje()}
        for escopo in {e["escopo"] for e in avaliados} - com_adiamento:
            contagem.pop(escopo, None)

    # Alvo, catálogo e atualização (seções 2 e 5) ---------------------------------------------------
    def ancora(self):
        """A pasta do Forge de onde vem o código e a URL: a do escopo do usuário; sem ele, a de maior versão instalada."""
        usuario = [e for e in self.escopos if e["escopo"] == "user"]
        candidatas = usuario or sorted(self.escopos, key=lambda e: versao_tupla(e["versao"]) or (0,), reverse=True)
        return self.instalacao(candidatas[0]["install"]) if candidatas else None

    def url_do_catalogo(self):
        ancora = self.ancora()
        if ancora is None:
            return None
        texto = fv._ler_limitado(Path(ancora) / ".claude-plugin" / "plugin.json", fv.LIMITE_PLUGIN_JSON)
        try:
            url = json.loads(texto).get("repository")
        except (TypeError, ValueError, AttributeError):
            return None
        return url if fv.url_valida(url) else None

    def fixacao_valida(self):
        fix = self.estado.get("fixacao")
        if not isinstance(fix, dict) or fix.get("motivo") not in ("volta-automatica", "dono") or versao_tupla(fix.get("para")) is None:
            self.estado.pop("fixacao", None)
            return None
        if fix["motivo"] == "volta-automatica" and versao_tupla(fix.get("de")) is None:
            self.estado.pop("fixacao", None)
            return None
        return fix

    def fixacao_legada(self, ref):
        """Catálogo com `ref`, sem estado e com o `versoes.log` do `forge atualizar`: se a versão do `ref` não aparece como
        `plugin_depois`, a fixação é do dono (na dúvida, do dono). Sem o log, ninguém fixou: é só o `ref` de passagem."""
        versao = versao_tupla((ref or "").removeprefix("v"))
        log = fv._ler_limitado(self.casa / ".local" / "state" / "forge" / "versoes.log", LIMITE_JSON)
        if self.estado_existia or versao is None or not log or not log.strip():
            return None
        depois = {l.split("\t")[3].strip() for l in log.splitlines() if l.count("\t") >= 3}
        if versao_texto(versao) in depois:
            return None
        return {"motivo": "dono", "de": versao_texto(versao), "para": versao_texto(versao), "desde": hoje()}

    def calcular_alvo(self, livres, ref):
        """(alvo tupla, mais nova tupla, fixação) ou None quando a falha já foi registrada."""
        rc, saida = self.git_rede(["ls-remote", "--symref", "--", self.url, "HEAD"])
        if rc != 0:
            self.falhar(livres, "prazo" if rc is None else "rede", saida)
            return None
        achou = re.search(r"^ref: (\S+)\s+HEAD", saida, re.M)
        if not achou or achou.group(1) != "refs/heads/main":
            self.falhar(livres, "branch-padrao", achou.group(1) if achou else "sem HEAD simbólico")
            return None
        rc, saida = self.git_rede(["ls-remote", "--tags", "--refs", "--", self.url, "refs/tags/v*"])
        if rc != 0:
            self.falhar(livres, "prazo" if rc is None else "rede", saida)
            return None
        ultima = maior_tag(saida)
        if ultima is None:
            self.falhar(livres, "sem-tag")
            return None
        fix = self.fixacao_valida()
        if fix is None and "fixacao" not in self.estado:
            legada = self.fixacao_legada(ref)
            if legada:
                self.estado["fixacao"] = fix = legada
        if fix and fix["motivo"] == "volta-automatica" and ultima > versao_tupla(fix["de"]):
            self.estado.pop("fixacao", None)
            fix = None
        return (versao_tupla(fix["para"]) if fix else ultima), ultima, fix

    def tag_na_main(self, tag):
        """(True, "") só com o commit da `tag` ancestral da `main` do remoto (ADR 0017: a tag `v*` só nasce da `main`). Busca só
        os commits (`--filter=tree:0`, sem outras tags) num repositório vazio da pasta neutra; o que não der para conferir
        reprova (falha fechada)."""
        repo = tempfile.mkdtemp(prefix="origem-", dir=self.neutro)
        rc, saida = self.rodar(["git", "init", "-q", "--bare", repo], self.neutro, PRAZO_LEITURA, SEM_HOOKS)
        if rc != 0:
            return False, "init: " + saida
        rc, saida = self.git_rede(["-C", repo, "fetch", "-q", "--filter=tree:0", "--no-tags", "--", self.url,
                                   "+refs/heads/main:refs/forge/main", f"+refs/tags/{tag}:refs/tags/{tag}"])
        if rc != 0:
            return False, "prazo" if rc is None else "busca: " + saida
        rc, _ = self.rodar(["git", "-C", repo, "merge-base", "--is-ancestor", f"refs/tags/{tag}", "refs/forge/main"], self.neutro,
                           PRAZO_LEITURA, SEM_HOOKS)
        if rc != 0:
            return False, f"o commit da {tag} não está na main" if rc == 1 else "não deu para conferir a main"
        return True, ""

    def origem_conferida(self, tag, escopos):
        """A `tag` só vale com o commit dela na `main`; senão `falhou:origem-da-tag` e nada muda."""
        ok, motivo = self.tag_na_main(tag)
        if not ok:
            self.falhar(escopos, "origem-da-tag", motivo)
        return ok

    def catalogo(self, tag, escopos):
        """`marketplace add <url>#<tag> --scope user` sobre o existente; True só com o `ref` lido igual à tag."""
        rc, saida = self.claude(["plugin", "marketplace", "add", f"{self.url}#{tag}", "--scope", "user"], cap=120)
        if rc != 0:
            self.falhar(escopos, "prazo" if rc is None else "add", saida)
            return False
        if self.ref_atual() != tag:
            self.falhar(escopos, "catalogo", f"o ref lido não é {tag}")
            return False
        return True

    def atualizar_escopo(self, e):
        cwd = self.neutro if e["escopo"] == "user" else e["projeto"]
        return self.claude(["plugin", "update", fv.PLUGIN, "--scope", e["escopo"]], cwd=cwd)

    def atualizar(self, livres):
        """Avanço (ou fixação): devolve os escopos que mudaram de versão (chave -> versão de antes)."""
        self.url = self.url_do_catalogo()
        if self.url is None:
            self.falhar(livres, "url", "repository do plugin.json ativo ausente ou fora de https")
            return {}
        ref = self.ref_atual()
        calculo = self.calcular_alvo(livres, ref)
        if calculo is None:
            return {}
        alvo, ultima, fix = calculo
        self.alvo = alvo
        if fix and fix["motivo"] == "dono" and ultima > alvo:
            if fix.get("avisada") != versao_texto(ultima):
                fix["avisada"] = versao_texto(ultima)
                self.estado["aviso"] = {"texto": f"O Forge {versao_texto(ultima)} saiu, mas a versão está fixada na {versao_texto(alvo)} "
                                                 "(fixação sua); a atualização automática respeita a fixação.", "avisado": False}
            for e in livres:
                if versao_tupla(e["versao"]) == alvo:
                    self.definir(e, "adiado:fixado-pelo-dono")
        pendentes = []
        for e in livres:
            if e["chave"] in self.res:
                continue
            atual = versao_tupla(e["versao"])
            if atual == alvo:
                continue
            if atual is not None and atual > alvo and not fix:
                self.definir(e, "adiado:instalada-mais-nova-que-a-publicada")
                continue
            pendentes.append(e)
        if not pendentes:
            return {}
        tag = "v" + versao_texto(alvo)
        if not self.origem_conferida(tag, pendentes):
            return {}
        if ref != tag and not self.catalogo(tag, pendentes):
            return {}
        for e in pendentes:
            rc, saida = self.atualizar_escopo(e)
            if rc != 0:
                self.falhar([e], "prazo" if rc is None else "update", saida)
        novos = self.listar()
        if novos is None:
            self.falhar(pendentes, "lista")
            return {}
        por_chave = {n["chave"]: n for n in novos}
        mudaram = {}
        for e in pendentes:
            if e["chave"] in self.res:
                continue
            novo = por_chave.get(e["chave"])
            if novo is None or versao_tupla(novo["versao"]) != alvo:
                self.falhar([e], "update", f"esperava {versao_texto(alvo)}, achou {novo['versao'] if novo else 'nada'}")
                continue
            mudaram[e["chave"]] = e["versao"]
            e.update(versao=novo["versao"], install=novo["install"], sha=novo["sha"])
        return mudaram

    # Checagem de início (seção 4) -------------------------------------------------------------
    def problemas_do_doutor(self, pasta, projeto):
        """(lista de problemas, conclusivo). Sem `forge-doutor` na pasta, nada a comparar."""
        doutor = Path(pasta) / "bin" / "forge-doutor"
        if not doutor.is_file():
            return [], True
        rc, saida = self.rodar([str(doutor), "--rapido", projeto], self.neutro, PRAZO_CINI)
        if rc is None:
            return [], False
        if rc == 0:
            return [], True
        return [l[2:].strip() for l in saida.splitlines() if l.startswith("- ")] or [saida or "o doutor terminou com erro"], True

    def cini(self, e, bom, completa=True):
        """(True, "") passou; (False, item) reprovou; (None, motivo) sem conclusão (prazo). Tudo local, sem rede nem token.
        `completa` (há última boa para comparar): inclui o `validate` da CLI e a comparação do doutor com o da versão anterior."""
        novo = self.instalacao(e["install"])
        if novo is None:
            return False, "pasta do plugin ausente ou fora do cache"
        texto = fv._ler_limitado(Path(novo) / ".claude-plugin" / "plugin.json", fv.LIMITE_PLUGIN_JSON)
        try:
            if not isinstance(json.loads(texto), dict):
                raise ValueError
        except (TypeError, ValueError):
            return False, "manifesto do plugin inválido"
        fim = time.monotonic() + PRAZO_CINI
        if completa:
            rc, saida = self.claude(["plugin", "validate", novo], cap=max(fim - time.monotonic(), 1))
            if rc is None:
                return None, "prazo da checagem"
            if rc != 0:
                return False, "validate do manifesto: " + resumo(saida)
        for sub in ("hooks", "bin"):
            for arq in sorted((Path(novo) / sub).glob("*.py"))[:200]:
                codigo = fv._ler_limitado(arq, 4 * LIMITE_JSON)
                try:
                    if codigo is None:
                        raise ValueError
                    compile(codigo, str(arq), "exec", dont_inherit=True)
                except (SyntaxError, ValueError, RecursionError, MemoryError):
                    return False, f"{sub}/{arq.name} não compila"
        bash = self.bash()
        for rel in SCRIPTS_SH:
            if (Path(novo) / rel).is_file():
                rc, _ = self.rodar([bash, "-n", str(Path(novo) / rel)], self.neutro, max(fim - time.monotonic(), 1))
                if rc is None:
                    return None, "prazo da checagem"
                if rc != 0:
                    return False, f"{rel} com erro de sintaxe"
        base = self.instalacao((bom or {}).get("installPath", "")) if completa and bom else None
        if base and base != novo:
            projeto = e["projeto"] if e["projeto"] and os.path.isdir(e["projeto"]) else (self.projeto or self.neutro)
            antes, ok1 = self.problemas_do_doutor(base, projeto)
            depois, ok2 = self.problemas_do_doutor(novo, projeto)
            if not (ok1 and ok2):
                return None, "prazo da checagem"
            novos = [p for p in depois if p not in antes]
            if novos:
                return False, "o doutor aponta problema novo: " + resumo(novos[0])[:80]
        return True, ""

    def registrar_boa(self, e):
        self.estado["bom"][e["chave"]] = {"versao": e["versao"], "gitCommitSha": e["sha"], "installPath": e["install"],
                                          "data": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    def checar(self, candidatos, mudaram):
        """C-INI de cada escopo cuja versão difere da última boa; devolve (reprovados com última boa, reprovados sem ela)."""
        com_boa, sem_boa = [], []
        for e in candidatos:
            if e["chave"] in self.res and not self.res[e["chave"]]["resultado"].startswith("em_dia"):
                continue
            bom = self.estado["bom"].get(e["chave"])
            bom = bom if isinstance(bom, dict) else None
            if bom and bom.get("versao") == e["versao"]:
                continue
            ok, item = self.cini(e, bom, completa=bool(bom))
            if ok:
                self.registrar_boa(e)
            elif ok is None:
                self.falhar([e], "checagem", item)
                self.res[e["chave"]]["resultado"] = f"falhou:checagem:{item}"
            elif bom:
                com_boa.append((e, bom, item))
            else:
                sem_boa.append((e, item))
        for e, item in sem_boa:
            self.definir(e, f"falhou:sem-ultima-boa:{resumo(item)}")
            self.estado["aviso"] = {"texto": f"A {e['versao']} instalada falhou na checagem de início ({item}) e não há versão boa "
                                             f"anterior registrada para voltar; o Forge segue na {e['versao']}.", "avisado": False}
            self.mensagem.append(("sem-ultima-boa", e["versao"]))
        return com_boa

    def voltar(self, reprovados):
        """Volta à última boa pelo mesmo mecanismo do avanço; grava a fixação antes de mexer no catálogo."""
        de = versao_texto(max(versao_tupla(e["versao"]) for e, _, _ in reprovados))
        para = versao_texto(max(versao_tupla(b["versao"]) or (0,) for _, b, _ in reprovados))
        item = reprovados[0][2]
        escopos = [e for e, _, _ in reprovados]
        self.estado["fixacao"] = {"motivo": "volta-automatica", "de": de, "para": para, "desde": hoje()}
        self.salvar_estado()
        desceram = []
        if self.url and self.origem_conferida(f"v{para}", escopos) and self.catalogo(f"v{para}", escopos):
            for e in escopos:
                rc, saida = self.atualizar_escopo(e)
                if rc != 0:
                    self.falhar([e], "prazo" if rc is None else "update", saida)
                    self.res.pop(e["chave"], None)
            novos = self.listar()
            for n in novos or []:
                alvo = next((e for e in escopos if e["chave"] == n["chave"]), None)
                if alvo is not None and n["versao"] == para:
                    voltou, _ = self.cini({**alvo, **n}, None, completa=True)
                    if voltou:
                        alvo.update(versao=n["versao"], install=n["install"], sha=n["sha"])
                        desceram.append(alvo)
        else:
            self.res = {k: v for k, v in self.res.items() if k not in {e["chave"] for e in escopos}}
        ficaram = [e for e in escopos if e not in desceram]
        for e in desceram:
            self.res[e["chave"]] = {"antes": de, "depois": para, "resultado": "voltou"}
        for e in ficaram:
            self.res[e["chave"]] = {"antes": de, "depois": e["versao"], "resultado": "volta-falhou"}
        if not ficaram:
            self.estado["aviso"] = {"texto": f"A {de} falhou na checagem de início ({item}); o Forge voltou à {para} e fica nela "
                                             "até sair versão maior. Nada a fazer.", "avisado": False}
            self.mensagem.append(("voltou", de, para))
            return
        comandos = [f"claude plugin marketplace add {self.url or '<url do Forge>'}#v{para} --scope user"]
        for e in ficaram:
            onde = "" if e["escopo"] == "user" else f" (na pasta {e['projeto']})"
            comandos.append(f"claude plugin update forge@forge --scope {e['escopo']}{onde}")
        self.estado["aviso"] = {"texto": f"A {de} falhou na checagem de início ({item}) e o Forge não conseguiu voltar à {para} sozinho. "
                                         "Para voltar à mão, rode no terminal: " + "; depois ".join(comandos) + ".", "avisado": False}
        self.mensagem.append(("volta-falhou", de, para))

    # Arquivos do modelo no projeto (seção 6) ------------------------------------------------------
    def git_do_projeto(self, args, cap=PRAZO_REDE):
        return self.rodar(["git", "-C", self.projeto, "-c", f"core.hooksPath={os.devnull}", *args], self.neutro, cap)

    def modelo(self, mudaram):
        """Branch local `forge/upgrade-<v>` por worktree temporária, sem `push`, sem `gh` e sem tocar a cópia de trabalho.
        O escopo que cobre o projeto é o de projeto ou local dele; o do usuário só quando acabou de subir nesta rodada (sem
        isso, toda abertura de qualquer pasta tentaria a branch)."""
        cobre = [e for e in self.escopos if e["escopo"] in CASCA and e["projeto"] and os.path.realpath(e["projeto"]) == self.projeto]
        usuario = [x for x in self.escopos if x["escopo"] == "user" and x["chave"] in mudaram]
        e = (cobre or usuario or [None])[0]
        if e is None or self.res.get(e["chave"], {}).get("resultado") not in ("em_dia", "atualizado"):
            return
        bom = self.estado["bom"].get(e["chave"])
        versao = versao_tupla(e["versao"])
        install = self.instalacao(e["install"])
        if not (isinstance(bom, dict) and bom.get("versao") == e["versao"]) or versao is None or install is None:
            return
        if self.git_do_projeto(["remote", "get-url", "origin"], PRAZO_LEITURA)[0] != 0:
            return
        rc, saida = self.git_do_projeto(["fetch", "--quiet", "--no-tags", "origin", "develop"])
        if rc != 0:
            return self.extra_modelo("fetch: " + saida)
        rc, atual = self.git_do_projeto(["show", "origin/develop:.forge/versao"], PRAZO_LEITURA)
        modelo = versao_tupla(atual) if rc == 0 else None
        if modelo is None or versao <= modelo:
            return
        ramo = f"forge/upgrade-{e['versao']}"
        if self.git_do_projeto(["rev-parse", "--verify", "-q", f"refs/heads/{ramo}"], PRAZO_LEITURA)[0] == 0:
            return
        rc, saida = self.git_do_projeto(["ls-remote", "--exit-code", "--heads", "origin", ramo])
        if rc == 0:
            return
        if rc != 2:
            return self.extra_modelo("ls-remote: " + saida)
        tmp = tempfile.mkdtemp(prefix="forge-modelo-")
        falha = None
        try:
            rc, saida = self.git_do_projeto(["worktree", "add", "--detach", tmp, "origin/develop"])
            if rc != 0:
                return self.extra_modelo("worktree: " + saida)
            rc, saida = self.rodar([str(Path(install) / "bin" / "forge-upgrade"), tmp, "--base", "origin/develop"], tmp, 120, SEM_HOOKS)
            if rc != 0:
                falha = "forge-upgrade: " + (saida or "sem saída")
            else:
                self.mensagem.append(("modelo", ramo))
        finally:
            self.git_do_projeto(["worktree", "remove", "--force", tmp], PRAZO_LEITURA)
            shutil.rmtree(tmp, ignore_errors=True)
            self.git_do_projeto(["worktree", "prune"], PRAZO_LEITURA)
            if falha:  # com a worktree fora, a branch que ficou pela metade sai: a abertura seguinte tenta de novo
                self.git_do_projeto(["branch", "-D", ramo], PRAZO_LEITURA)
        if falha:
            self.extra_modelo(falha)

    def extra_modelo(self, texto):
        self.extras.append(("modelo", self.projeto, "-", "-", "falhou:modelo:" + resumo(texto)))

    # Fluxo -------------------------------------------------------------------------------------
    def fluxo(self):
        self.claude_bin = self.achar_claude()
        if self.claude_bin is None:
            self.extras.append(("-", "-", "-", "-", "falhou:sem-claude"))
            self.mensagem.append(("falhou", "sem-claude"))
            return
        escopos = self.listar()
        if not escopos:
            return
        self.escopos = escopos
        for e in escopos:
            if e["escopo"] in CASCA and not os.path.isdir(e["projeto"]):
                self.definir(e, "pulado:projeto-ausente")
        ativos = [e for e in escopos if e["chave"] not in self.res]
        adiados = self.ocupacao(ativos)
        self.contar_adiamentos(ativos, adiados)
        livres = [e for e in ativos if e["chave"] not in adiados]
        if not livres:
            return
        mudaram = self.atualizar(livres)
        com_boa = self.checar([e for e in livres if e["chave"] not in self.res or e["chave"] in mudaram or
                               self.res[e["chave"]]["resultado"] == "em_dia"], mudaram)
        for e in livres:
            if e["chave"] in mudaram:
                if e["chave"] not in self.res:  # a checagem sem conclusão ou sem última boa já deu o resultado do escopo
                    self.definir(e, "atualizado", depois=e["versao"])
                    self.res[e["chave"]]["antes"] = mudaram[e["chave"]]
                self.mensagem.append(("atualizado", mudaram[e["chave"]], e["versao"], e))
            elif e["chave"] not in self.res:
                self.definir(e, "em_dia")
        if com_boa:
            self.voltar([(e, b, i) for e, b, i in com_boa])
        if self.gatilho == "atalho" and self.projeto:
            self.modelo(mudaram)

    def linha(self):
        """Uma linha no máximo para o terminal, ou nada quando tudo está em dia."""
        for tipo, *resto in self.mensagem:
            if tipo == "voltou":
                return f"Forge: {resto[0]} falhou na checagem; voltou à {resto[1]}"
            if tipo == "volta-falhou":
                return f"Forge: {resto[0]} falhou na checagem e a volta falhou; o Jarvis mostra o aviso"
        for tipo, *resto in self.mensagem:
            if tipo == "falhou":
                versoes = sorted({e["versao"] for e in self.escopos if e["versao"]})
                seguindo = f"; segue na {versoes[0]}" if versoes else ""
                return "Forge: sem rede" + seguindo if resto[0] in ("rede", "prazo") else f"Forge: não atualizou ({resto[0]})" + seguindo
        atualizados = [m for m in self.mensagem if m[0] == "atualizado"]
        if atualizados:
            onde = ", ".join(dict.fromkeys("usuário" if m[3]["escopo"] == "user" else os.path.basename(m[3]["projeto"]) for m in atualizados))
            return f"Forge: {atualizados[0][1]} -> {atualizados[0][2]} ({onde})"
        if any(r["resultado"].startswith("adiado:") for r in self.res.values()):
            return "Forge: atualização adiada (trabalho em curso)"
        return None

    def executar(self):
        try:
            if not self.abrir_estado():
                return 0
        except (EstadoRecusado, OSError) as erro:
            print(f"Forge: {resumo(erro)}", file=sys.stderr)
            return 1
        trava = self.travar()
        if trava is None:
            return 0
        try:
            self.neutro = tempfile.mkdtemp(prefix="forge-sempre-atual-")
            try:
                self.fluxo()
            except Prazo:
                self.falhar([e for e in self.escopos if e["chave"] not in self.res], "prazo", "orçamento da rodada esgotado")
                if not self.escopos:
                    self.extras.append(("-", "-", "-", "-", "falhou:prazo"))
            except Exception as erro:  # a rodada nunca cai: o atalho abre o Claude de qualquer jeito
                self.falhar([e for e in self.escopos if e["chave"] not in self.res], "interno", f"{type(erro).__name__}: {erro}")
                if not self.escopos:
                    self.extras.append(("-", "-", "-", "-", f"falhou:interno:{resumo(f'{type(erro).__name__}: {erro}')}"))
            for gravar in (self.salvar_estado, self.gravar_registro):
                try:
                    gravar()
                except OSError as erro:
                    print(f"Forge: não gravei o estado ({resumo(erro)})", file=sys.stderr)
            linha = self.linha()
            if linha:
                print(resumo(linha))
            return 0
        finally:
            shutil.rmtree(self.neutro or "", ignore_errors=True)
            os.close(trava)


def _com_estado(mudar, espera=10.0):
    """Abre o estado da ferramenta com a trava e chama `mudar(rodada)`; (deu certo, motivo). Para `forge atualizar --fixar`, `forge
    voltar-versao` e a soltura da fixação do dono (ADR 0017, item 11): só esses gravam a fixação `dono`. Espera a rodada do atalho."""
    rodada = Rodada("atalho")
    try:
        if not rodada.abrir_estado():
            return False, "a pasta de estado do Forge não existe (o plugin ainda não foi instalado por este usuário)"
    except (EstadoRecusado, OSError) as erro:
        return False, resumo(erro)
    fim = time.monotonic() + espera
    trava = rodada.travar()
    while trava is None and time.monotonic() < fim:
        time.sleep(0.2)
        trava = rodada.travar()
    if trava is None:
        return False, "outra atualização do Forge está rodando agora"
    try:
        mudar(rodada)
        rodada.salvar_estado()
        return True, ""
    except OSError as erro:
        return False, resumo(erro)
    finally:
        os.close(trava)


def fixar_como_dono(versao):
    """Grava `fixacao={motivo: dono}` na versão: a abertura seguinte do atalho respeita e não sobe nem desce sozinha."""
    if versao_tupla(versao) is None:
        return False, f"versão inválida: {versao}"
    texto = versao_texto(versao_tupla(versao))

    def mudar(rodada):
        rodada.estado["fixacao"] = {"motivo": "dono", "de": texto, "para": texto, "desde": hoje()}
    return _com_estado(mudar)


def soltar_fixacao_do_dono():
    """O dono atualizou de propósito (`forge atualizar`): a fixação dele cai; a automática (volta) segue as regras dela."""
    def mudar(rodada):
        fix = rodada.estado.get("fixacao")
        if isinstance(fix, dict) and fix.get("motivo") == "dono":
            rodada.estado.pop("fixacao", None)
    return _com_estado(mudar)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="forge-sempre-atual", description="Mantém o plugin do Forge na última versão (só atalho e postStart).")
    ap.add_argument("--gatilho", required=True, choices=GATILHOS)
    ap.add_argument("--projeto")
    ap.add_argument("--orcamento", type=float, default=ORCAMENTO_PADRAO, help="segundos para a rodada inteira (padrão 60)")
    args = ap.parse_args(argv)
    if fv.dentro_do_claude():
        print("forge-sempre-atual: roda só no atalho do dono e no início do container, nunca de dentro do Claude. Não mudei nada.",
              file=sys.stderr)
        return 2
    return Rodada(args.gatilho, args.projeto, args.orcamento).executar()


if __name__ == "__main__":
    sys.exit(main())
