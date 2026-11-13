"""Pre-push do modelo de projeto. E18 PREPUSH-SO-DOCS: pula o pre-push.local só quando todo arquivo enviado é docs/** ou .md;
F2 (versao-047, E2a): o pre-push.local roda num grupo próprio, e só esse grupo recebe sinal;
F1 (versao-047, E1a): uma checagem do projeto por vez por usuário e máquina.

Cada teste roda o hook de verdade num repositório descartável, num grupo novo criado pelo teste (G-6).
"""
import fcntl
import json
import os
import shutil
import stat
import subprocess
import signal
import tempfile
import sys
import time
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / "templates" / "projeto" / ".githooks" / "pre-push"
ZERO = "0" * 40
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from apoio_sandbox import exigir  # noqa: E402  (ENVIO-DO-SANDBOX: pula só no sandbox fora do CI)
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
AMBIENTE["FORGE_PREPUSH_SUITE"] = "afetados"  # ENVIO-LEVE: o padrão do hook não roda teste; estes testes exercitam o plano dos afetados
AMBIENTE.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
PULO = "só docs/** e .md; lint e typecheck pulados"


def matar_se_vivo(pid):
    """Limpeza: o processo pode já ter saído (corrida vista no runner do GitHub)."""
    try:
        os.kill(pid, 9)
    except ProcessLookupError:
        pass


class Repo(unittest.TestCase):
    def setUp(self):
        self.dir, self.fora = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir, True)
        self.addCleanup(shutil.rmtree, self.fora, True)
        self.amb = dict(AMBIENTE, HOME=str(self.fora), XDG_RUNTIME_DIR=str(self.fora), TMPDIR=str(self.fora))
        self.git("init", "-q", "-b", "base")
        (self.dir / ".githooks").mkdir()
        shutil.copy(HOOK, self.dir / ".githooks" / "pre-push")
        local = self.dir / ".githooks" / "pre-push.local"
        local.write_text('#!/usr/bin/env bash\necho rodou >> "$(dirname "$0")/../marca"\n')
        local.chmod(local.stat().st_mode | stat.S_IXUSR)
        self.escreve("README.txt", "x")
        self.base = self.commit("base")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.dir), *args], env=AMBIENTE, capture_output=True, text=True, check=True).stdout.strip()

    def escreve(self, nome, texto="x"):
        p = self.dir / nome
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto)

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def envia(self, linhas, ambiente=None):
        r = subprocess.run([str(self.dir / ".githooks" / "pre-push"), "origin", "x"], input="".join(linhas),
                           cwd=self.dir, env=ambiente or self.amb, capture_output=True, text=True, start_new_session=True)
        return r, (self.dir / "marca").exists()

    def ref(self, local, remoto, nome="refs/heads/f"):
        return f"{nome} {local} {nome} {remoto}\n"

    def muda_e_envia(self, arquivos):
        for a in arquivos:
            self.escreve(a)
        novo = self.commit("muda")
        return self.envia([self.ref(novo, self.base)])

    def pula(self, arquivos):
        r, marca = self.muda_e_envia(arquivos)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(marca)
        self.assertIn(PULO, r.stdout)

    def roda(self, arquivos):
        r, marca = self.muda_e_envia(arquivos)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(marca)
        self.assertNotIn(PULO, r.stdout)


class PrePushSoDocs(Repo):
    def test_pula_so_docs(self):
        self.pula(["docs/a.md"])

    def test_pula_so_readme(self):
        self.pula(["README.md"])

    def test_pula_dentro_de_docs_qualquer_extensao(self):
        self.pula(["docs/sub/x.ts"])

    def test_pula_md_em_qualquer_pasta(self):
        self.pula(["src/a.md", "docs/b.md"])

    def test_pula_nome_com_espaco(self):
        self.pula(["docs/a b.md"])

    def test_roda_github(self):
        self.roda([".github/x.yml"])

    def test_roda_github_md(self):
        self.roda([".github/x.md"])

    def test_roda_codigo(self):
        self.roda(["src/a.ts"])

    def test_roda_docs_mais_codigo(self):
        self.roda(["docs/a.md", "src/a.ts"])

    def test_roda_caixa_e_sufixo_enganosos(self):
        for nome in ("a.MD", "a.md.ts", "docsx/a.txt", "docsx/a.ts", "Docs/a.ts"):
            with self.subTest(nome):
                self.roda([nome])
                (self.dir / "marca").unlink()
                self.base = self.git("rev-parse", "HEAD")

    def test_roda_docs_como_arquivo(self):
        self.roda(["docs"])

    def test_roda_outras_extensoes_de_texto(self):
        self.roda(["LICENSE", "a.txt", "img.png"])

    def test_renome_de_codigo_para_docs_roda(self):
        self.escreve("src/a.ts", "conteudo longo o bastante para o git ver renome\n" * 5)
        self.base = self.commit("codigo")
        self.git("mv", "src/a.ts", "docs-a.ts")
        (self.dir / "docs").mkdir(exist_ok=True)
        self.git("mv", "docs-a.ts", "docs/a.ts")
        novo = self.commit("renomeia")
        r, marca = self.envia([self.ref(novo, self.base)])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(marca)

    def test_remocao_de_codigo_roda(self):
        self.escreve("src/a.ts")
        self.base = self.commit("codigo")
        self.git("rm", "-q", "src/a.ts")
        novo = self.commit("remove")
        self.assertTrue(self.envia([self.ref(novo, self.base)])[1])

    def test_duas_refs_uma_docs_outra_codigo_roda(self):
        self.escreve("docs/a.md")
        so_docs = self.commit("docs")
        self.git("checkout", "-q", "-b", "outra", self.base)
        self.escreve("src/a.ts")
        codigo = self.commit("codigo")
        r, marca = self.envia([self.ref(so_docs, self.base, "refs/heads/a"), self.ref(codigo, self.base, "refs/heads/b")])
        # PREPUSH-REFS (v0457): duas branches no mesmo envio recusam antes do plano
        self.assertEqual((r.returncode, "mais de uma branch" in r.stderr, marca), (1, True, False), r.stderr)

    def test_duas_refs_so_docs_pulam(self):
        self.escreve("docs/a.md")
        a = self.commit("a")
        self.git("checkout", "-q", "-b", "outra", self.base)
        self.escreve("README.md")
        b = self.commit("b")
        r, marca = self.envia([self.ref(a, self.base, "refs/heads/a"), self.ref(b, self.base, "refs/heads/b")])
        self.assertFalse(marca)
        self.assertEqual((r.returncode, "mais de uma branch" in r.stderr), (1, True), r.stderr)  # PREPUSH-REFS

    def test_branch_nova_roda(self):
        self.escreve("docs/a.md")
        novo = self.commit("docs")
        self.assertTrue(self.envia([self.ref(novo, ZERO)])[1])

    def test_apagar_ref_roda(self):
        self.assertTrue(self.envia([self.ref(ZERO, self.base)])[1])

    def test_apagar_ref_com_outra_so_docs_roda(self):
        self.escreve("docs/a.md")
        novo = self.commit("docs")
        marca = self.envia([self.ref(novo, self.base, "refs/heads/a"), self.ref(ZERO, self.base, "refs/heads/b")])[1]
        self.assertTrue(marca)

    def test_tag_roda(self):
        self.escreve("docs/a.md")
        novo = self.commit("docs")
        self.assertTrue(self.envia([self.ref(novo, self.base, "refs/tags/v1")])[1])

    def test_diff_sem_arquivo_roda(self):
        self.assertTrue(self.envia([self.ref(self.base, self.base)])[1])

    def test_objeto_ausente_roda(self):
        self.escreve("docs/a.md")
        novo = self.commit("docs")
        r, marca = self.envia([self.ref(novo, "1" * 40)])
        self.assertTrue(marca or r.returncode != 0)
        self.assertNotIn(PULO, r.stdout)

    def test_git_falso_que_falha_roda(self):
        self.escreve("docs/a.md")
        novo = self.commit("docs")
        falso = self.dir / "falso"
        falso.mkdir()
        real = shutil.which("git")
        g = falso / "git"
        g.write_text(f'#!/usr/bin/env bash\n[ "$1" = diff ] && exit 1\nexec {real} "$@"\n')
        g.chmod(0o755)
        amb = dict(self.amb, PATH=f"{falso}:{AMBIENTE['PATH']}")
        r, marca = self.envia([self.ref(novo, self.base)], amb)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(marca)

    def test_diff_usa_os_commits_e_nao_a_arvore(self):
        self.escreve("docs/a.md")
        novo = self.commit("docs")
        self.escreve("src/sujo.ts")
        self.git("add", "src/sujo.ts")
        r, marca = self.envia([self.ref(novo, self.base)])
        self.assertFalse(marca)
        self.assertIn(PULO, r.stdout)

    def test_sem_variavel_que_pule(self):
        self.escreve("src/a.ts")
        novo = self.commit("codigo")
        for nome in ("FORGE_PREPUSH_SO_DOCS", "SKIP_PREPUSH_LOCAL", "FORGE_SO_DOCS"):
            amb = dict(self.amb, **{nome: "1"})
            self.assertTrue(self.envia([self.ref(novo, self.base)], amb)[1], nome)
            (self.dir / "marca").unlink()

    def test_main_segue_bloqueada(self):
        self.escreve("docs/a.md")
        novo = self.commit("docs")
        r, marca = self.envia([self.ref(novo, self.base, "refs/heads/main")])
        self.assertEqual(r.returncode, 1)
        self.assertFalse(marca)

    def test_pre_push_local_que_falha_continua_barrando(self):
        self.escreve("src/a.ts")
        novo = self.commit("codigo")
        (self.dir / ".githooks" / "pre-push.local").write_text("#!/usr/bin/env bash\nexit 1\n")
        r, _ = self.envia([self.ref(novo, self.base)])
        self.assertEqual(r.returncode, 1)


def vivos():
    """PID -> PGID dos processos vivos, sem os zumbis (o PID 1 do contêiner pode não colher os órfãos)."""
    v = {}
    for p in Path("/proc").glob("[0-9]*"):
        try:
            c = (p / "stat").read_text().rsplit(")", 1)[1].split()
        except OSError:
            continue
        if c[0] != "Z":
            v[int(p.name)] = int(c[2])
    return v


def ate(cond, prazo=10):
    fim = time.monotonic() + prazo
    while not cond() and time.monotonic() < fim:
        time.sleep(0.1)
    return cond()


class GrupoDaEtapa(Repo):
    """Hook e irmão num grupo novo do teste (G-6); HOME, XDG_RUNTIME_DIR e TMPDIR na pasta de fora do teste."""
    def setUp(self):
        super().setUp()
        self.escreve("src/a.ts")
        self.novo = self.commit("codigo")

    def etapa(self, corpo):
        (self.dir / ".githooks" / "pre-push.local").write_text(
            f'#!/usr/bin/env bash\necho $$ $(ps -o pgid= -p $$) > "$(dirname "$0")/../etapa"\nexec >/dev/null 2>&1\n{corpo}\n')

    def lanca(self):
        p = subprocess.Popen([shutil.which("bash"), "-c", "sleep 60 >/dev/null 2>&1 & echo $! > irmao; exec .githooks/pre-push origin x"],
                             cwd=self.dir, env=self.amb, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, start_new_session=True)
        self.addCleanup(subprocess.run, ["kill", "-KILL", "--", f"-{p.pid}"], stderr=subprocess.DEVNULL)
        p.stdin.write(self.ref(self.novo, self.base))
        p.stdin.close()
        return p

    def le(self, nome, quer=1):
        """Espera o arquivo ter `quer` números inteiros (a etapa anota "pid pgid" só quando o grupo existe), não uma janela fixa."""

        def campos():
            try:
                return [int(x) for x in (self.dir / nome).read_text().split()]
            except (OSError, ValueError):
                return []
        self.assertTrue(ate(lambda: len(campos()) >= quer, 30), nome)
        return campos()[:quer]

    def fim(self, p):
        try:
            return p.wait(timeout=30), p.stderr.read()
        except subprocess.TimeoutExpired:
            self.fail("o hook não saiu em 30 s")

    @staticmethod
    def vigia(hook, etapa, irmao):
        """O hook já passou da partida da etapa e dorme no laço de vigia: tem um filho `sleep` que não é a etapa nem o irmão (o irmão também vira filho do hook após o exec)."""
        for pid in vivos():
            try:
                stat = Path(f"/proc/{pid}/stat").read_text()
            except OSError:
                continue
            nome, resto = stat.split("(", 1)[1].rsplit(")", 1)
            if nome == "sleep" and pid not in (etapa, irmao) and int(resto.split()[1]) == hook:
                return True
        return False

    def interrompe(self):
        exigir(self, "proc")
        p = self.lanca()
        irmao = self.le("irmao")[0]
        etapa = self.le("etapa")[0]
        self.assertTrue(ate(lambda: self.vigia(p.pid, etapa, irmao), 30), "o hook não chegou ao laço de vigia")
        p.send_signal(signal.SIGTERM)
        rc, err = self.fim(p)
        self.assertEqual(rc, 1)
        self.assertIn("checagem interrompida; o envio foi barrado", err)
        self.assertIn(irmao, vivos())
        return etapa

    def test_etapa_em_grupo_proprio_e_saida_repassada(self):
        exigir(self, "proc")
        for saida, esperado in ((0, 0), (3, 1)):
            with self.subTest(saida):
                self.etapa(f"exit {saida}")
                p = self.lanca()
                self.assertEqual(self.fim(p)[0], esperado)
                pid, pgid = self.le("etapa", 2)
                self.assertEqual(pgid, pid)
                self.assertNotEqual(pgid, p.pid)
                (self.dir / "etapa").unlink()

    def test_term_no_hook_encerra_o_grupo_e_poupa_o_irmao(self):
        self.etapa("sleep 60 & exec sleep 60")
        etapa = self.interrompe()
        self.assertTrue(ate(lambda: etapa not in vivos().values()))

    def test_filho_deixado_pela_etapa_nao_sobrevive(self):
        self.etapa('sleep 60 & echo $! > "$(dirname "$0")/../filho"')
        self.assertEqual(self.fim(self.lanca())[0], 0)
        filho = self.le("filho")[0]
        self.assertTrue(ate(lambda: filho not in vivos(), 30))

    def test_grupo_nao_criado_ou_pgid_ilegivel_sinaliza_so_a_etapa(self):
        falso = self.dir / "falso"
        falso.mkdir()
        (falso / "bash").write_text(f"#!/bin/sh\nexec {shutil.which('bash')} -c 'set() {{ [ \"$1\" = -m ] || builtin set \"$@\"; }}; . \"$0\"' \"$@\"\n")
        self.amb["PATH"] = f"{falso}:{self.amb['PATH']}"
        for corpo in ("echo $$", ""):
            with self.subTest(corpo):
                (falso / "ps").write_text(f"#!/bin/sh\n{corpo}\n")
                for f in falso.iterdir():
                    f.chmod(0o755)
                self.etapa("exec sleep 60")
                etapa = self.interrompe()
                self.assertTrue(ate(lambda: etapa not in vivos()))
                for nome in ("etapa", "irmao"):
                    (self.dir / nome).unlink()


class TravaDaChecagem(Repo):
    def setUp(self):
        super().setUp()
        self.escreve("src/a.ts")
        self.linhas = [self.ref(self.commit("codigo"), self.base)]
        self.trava = self.fora / f"forge-prepush-{os.getuid()}.lock"

    def lanca(self, amb=None):
        (self.fora / "entrada").write_text("".join(self.linhas))
        with open(self.fora / "entrada") as entrada:
            return subprocess.Popen([str(self.dir / ".githooks" / "pre-push"), "origin", "x"], cwd=self.dir, env=amb or self.amb,
                                    stdin=entrada, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                    start_new_session=True)

    def fim(self, p):
        try:
            _, err = p.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, 9)
            p.communicate()
            self.fail("o hook não saiu em 20 s")
        return p.returncode, err, (self.dir / "marca").exists()

    def barra(self, amb=None, texto=""):
        rc, err, marca = self.fim(self.lanca(amb))
        self.assertEqual((rc, marca, texto in err), (1, False, True), err)

    def test_quatro_envios_nunca_se_sobrepoem_e_avisam_uma_vez(self):
        (self.dir / ".githooks" / "pre-push.local").write_text("#!/usr/bin/env bash\n" + 'echo i >> "$(dirname "$0")/../log"; sleep 1; echo o >> "$(dirname "$0")/../log"\n')
        fins = [self.fim(p) for p in [self.lanca() for _ in range(4)]]
        self.assertEqual((self.dir / "log").read_text().split(), ["i", "o"] * 4)
        self.assertEqual([f[0] for f in fins], [0] * 4, fins)
        avisos = [[linha for linha in f[1].splitlines() if "aguardando a vez" in linha] for f in fins]
        self.assertEqual(sorted(bool(a) for a in avisos), [False] + [True] * 3)
        self.assertFalse([a for a in avisos if any(x == y for x, y in zip(a, a[1:]))], "aviso repetido sem N mudar")

    def test_espera_estourada_barra_sem_rodar(self):
        with open(self.trava, "w") as t:
            fcntl.flock(t, fcntl.LOCK_EX)
            self.barra(dict(self.amb, FORGE_PREPUSH_ESPERA="1"), "a vez não chegou em 1 s")

    def test_espera_invalida_recusa(self):
        for v in ("0", "abc", "", "0012", "1234567", f"a[$(touch {self.fora}/S)]"):
            with self.subTest(v):
                self.barra(dict(self.amb, FORGE_PREPUSH_ESPERA=v), "FORGE_PREPUSH_ESPERA")
        self.assertFalse((self.fora / "S").exists())

    def test_trava_nao_passa_para_a_etapa(self):
        (self.dir / ".githooks" / "pre-push.local").write_text("#!/usr/bin/env bash\n" + f'setsid sleep 300 >/dev/null 2>&1 & echo $! > {self.fora}/pid\n')
        self.assertEqual(self.fim(self.lanca())[0], 0)
        self.addCleanup(matar_se_vivo, int((self.fora / "pid").read_text()))
        self.assertEqual(self.fim(self.lanca(dict(self.amb, FORGE_PREPUSH_ESPERA="1")))[0], 0)
        fila = self.trava.with_suffix(".fila")
        self.assertTrue(fila.is_dir(), "a fila não nasceu")
        self.assertEqual(list(fila.iterdir()), [])

    def test_xdg_com_escrita_alheia_recua_para_o_home(self):
        self.fora.chmod(0o777)
        self.assertEqual(self.fim(self.lanca())[0:3:2], (0, True))
        pasta = self.fora / ".local" / "state" / "forge"
        self.assertEqual((self.trava.exists(), (pasta / self.trava.name).exists(), pasta.exists() and pasta.stat().st_mode & 0o777), (False, True, 0o700))

    def test_pasta_de_outro_dono_recua_ou_e_recusada(self):
        xdg = Path(tempfile.mkdtemp(dir=self.fora))
        xdg.chmod(0o700)
        if os.geteuid() == 0:
            exigir(self, "chown")
            os.chown(xdg, 65534, 65534)
        else:
            xdg = Path("/")  # do root e sem escrita alheia: só o dono a recusa
        self.assertEqual(self.fim(self.lanca(dict(self.amb, XDG_RUNTIME_DIR=str(xdg))))[0:3:2], (0, True))
        pasta = self.fora / ".local" / "state" / "forge"
        self.assertEqual(((xdg / self.trava.name).exists(), (pasta / self.trava.name).exists()), (False, True))
        if os.geteuid() == 0:
            (pasta / self.trava.name).unlink()
            (self.dir / "marca").unlink()
            os.chown(pasta, 65534, 65534)
            self.barra({k: v for k, v in self.amb.items() if k != "XDG_RUNTIME_DIR"}, "recusada")
            self.assertFalse((pasta / self.trava.name).exists())

    def test_pasta_do_home_link_ou_775_recusada(self):
        amb = {k: v for k, v in self.amb.items() if k != "XDG_RUNTIME_DIR"}
        pasta, alvo = self.fora / ".local" / "state" / "forge", Path(tempfile.mkdtemp(dir=self.fora))
        pasta.parent.mkdir(parents=True)
        pasta.symlink_to(alvo)
        self.barra(amb, "recusada")
        self.assertEqual(list(alvo.iterdir()), [])
        pasta.unlink()
        pasta.mkdir()
        pasta.chmod(0o775)
        self.barra(amb, "recusada")

    def test_trava_link_pasta_ou_alheia_recusada(self):
        sentinela = self.fora / "sentinela"
        sentinela.write_text("intacta")
        self.trava.symlink_to(sentinela)
        self.barra(texto="link")
        self.assertEqual(sentinela.read_text(), "intacta")
        self.trava.unlink()
        self.trava.mkdir()
        self.barra(texto="não abriu")
        if os.geteuid() == 0:
            self.trava.rmdir()
            self.trava.touch()
            exigir(self, "chown")
            os.chown(self.trava, 65534, 65534)
            self.barra(texto="não é do próprio usuário")

    def test_sem_flock_roda_com_aviso_e_flock_que_falha_barra(self):
        sem = self.fora / "sem"
        sem.mkdir()
        for n in ("bash", "git", "dirname", "mktemp", "rm", "id", "find", "mkdir"):
            (sem / n).symlink_to(shutil.which(n))
        rc, err, marca = self.fim(self.lanca(dict(self.amb, PATH=str(sem))))
        self.assertEqual((rc, marca, "sem flock" in err), (0, True, True), err)
        (self.dir / "marca").unlink()
        (sem / "flock").write_text("#!/bin/sh\nexit 2\n")
        (sem / "flock").chmod(0o755)
        self.barra(dict(self.amb, PATH=str(sem)))

    def test_so_docs_nao_abre_a_trava(self):
        self.base = self.git("rev-parse", "HEAD")
        self.pula(["docs/a.md"])
        self.assertFalse(self.trava.exists())


class FilaDaChecagem(Repo):
    lanca, fim, barra = TravaDaChecagem.lanca, TravaDaChecagem.fim, TravaDaChecagem.barra

    def setUp(self):
        super().setUp()
        self.escreve("src/a.ts")
        self.linhas = [self.ref(self.commit("codigo"), self.base)]
        self.trava, self.fila = (self.fora / f"forge-prepush-{os.getuid()}.{x}" for x in ("lock", "fila"))
        (self.dir / ".githooks" / "pre-push.local").write_text('#!/usr/bin/env bash\necho "${ORDEM-0}" >> "$(dirname "$0")/../marca"; sleep "${DORME-0}"\n')

    def viva(self, nome):
        self.fila.mkdir(mode=0o700, exist_ok=True)
        f = open(self.fila / nome, "w")
        self.addCleanup(f.close)
        fcntl.flock(f, fcntl.LOCK_EX)

    def roda_sozinho(self, amb=None):
        rc, err, marca = self.fim(self.lanca(dict(amb or self.amb, FORGE_PREPUSH_ESPERA="3")))
        self.assertEqual((rc, marca), (0, True), err)
        return err

    def test_tres_esperam_em_ordem_de_chegada_contando_quem_esta_na_frente(self):
        ps = []
        with open(self.trava, "w") as t:
            fcntl.flock(t, fcntl.LOCK_EX)
            for k in range(3):
                ps.append(self.lanca(dict(self.amb, ORDEM=str(k), DORME="2")))
                for _ in range(100):
                    if len(list(self.fila.glob("[0-9]*-[0-9]*"))) > k:
                        break
                    time.sleep(0.1)
        fins = [self.fim(p) for p in ps]
        self.assertEqual([f[0] for f in fins], [0] * 3, fins)
        self.assertEqual((self.dir / "marca").read_text().split(), ["0", "1", "2"])
        avisos = [[linha.split("(")[1].split(")")[0] for linha in f[1].splitlines() if "aguardando a vez" in linha] for f in fins]
        self.assertEqual(avisos, [["0 na frente"], ["1 na frente", "0 na frente"], ["2 na frente", "1 na frente", "0 na frente"]])
        self.assertEqual(list(self.fila.iterdir()), [])

    def test_senha_morta_sai_e_a_propria_nao_conta(self):
        self.fila.mkdir(mode=0o700)
        (self.fila / "1-1").touch()
        self.roda_sozinho()
        self.assertEqual(list(self.fila.iterdir()), [])

    def test_senha_viva_na_frente_espera_ate_o_prazo(self):
        self.viva("1-1")
        self.barra(dict(self.amb, FORGE_PREPUSH_ESPERA="2"), "(1 na frente)")
        self.assertTrue((self.fila / "1-1").exists())

    def test_nome_fora_do_formato_ou_link_nao_conta_nem_vai_ao_terminal(self):
        self.viva("0\x1b]0;x\x07-1")
        self.viva("alvo")
        (self.fila / "1-2").symlink_to(self.fila / "alvo")
        err = self.roda_sozinho()
        self.assertFalse(set(err) & {"\x1b", "\x07"}, err)

    def test_pasta_da_fila_link_ou_775_espera_so_pela_trava(self):
        alvo = Path(tempfile.mkdtemp(dir=self.fora))
        self.fila.symlink_to(alvo)
        self.assertIn("só pela trava", self.roda_sozinho())
        self.assertEqual(list(alvo.iterdir()), [])
        (self.dir / "marca").unlink()
        self.fila.unlink()
        self.fila.mkdir(mode=0o700)
        self.fila.chmod(0o775)
        self.assertIn("só pela trava", self.roda_sozinho())

    def test_senha_morta_no_destino_da_fila_link_fica(self):
        alvo = Path(tempfile.mkdtemp(dir=self.fora))
        alvo.chmod(0o700)
        (alvo / "1-1").touch()
        self.fila.symlink_to(alvo)
        self.assertIn("só pela trava", self.roda_sozinho())
        self.assertEqual([f.name for f in alvo.iterdir()], ["1-1"])

    def test_senha_que_nao_nasce_espera_so_pela_trava_sem_sobra(self):
        falso = self.fora / "bin"
        falso.mkdir()
        (falso / "flock").write_text(f'#!/bin/sh\n[ "$*" = "-n 8" ] && exit 1\nexec {shutil.which("flock")} "$@"\n')
        (falso / "flock").chmod(0o755)
        self.assertIn("não foi criada", self.roda_sozinho(dict(self.amb, PATH=f"{falso}:{AMBIENTE['PATH']}")))
        self.assertEqual(list(self.fila.iterdir()), [])


class EnvioDeCodigo(Repo):
    """Base das classes abaixo: um envio com código (não cai no "só docs"), lançado como na TravaDaChecagem."""
    lanca, fim, barra = TravaDaChecagem.lanca, TravaDaChecagem.fim, TravaDaChecagem.barra

    def setUp(self):
        super().setUp()
        self.escreve("src/a.ts")
        self.linhas = [self.ref(self.commit("codigo"), self.base)]
        self.trava = self.fora / f"forge-prepush-{os.getuid()}.lock"


class LimiteDaEtapa(EnvioDeCodigo):
    """F2 (E2b): FORGE_PREPUSH_TIMEOUT encerra a checagem com os filhos e barra; o prazo conta do início da etapa."""
    def local(self, corpo):
        (self.dir / ".githooks" / "pre-push.local").write_text(f'#!/usr/bin/env bash\ncd "$(dirname "$0")/.."\n{corpo}\n')

    def test_estouro_encerra_com_os_filhos_e_barra(self):
        exigir(self, "proc")
        self.local("sleep 300 & echo $! > filho; sleep 300")
        rc, err, _ = self.fim(self.lanca(dict(self.amb, FORGE_PREPUSH_TIMEOUT="2")))
        self.assertEqual(rc, 1)
        self.assertIn("passou de 2 s e foi encerrada com os filhos", err)
        filho = int((self.dir / "filho").read_text())
        self.assertTrue(ate(lambda: filho not in vivos()))

    def test_limite_invalido_recusa(self):
        for v in ("0", "x", "", "-5", "1234567"):
            with self.subTest(v):
                self.barra(dict(self.amb, FORGE_PREPUSH_TIMEOUT=v), "FORGE_PREPUSH_TIMEOUT")

    def test_espera_na_trava_nao_conta_no_limite(self):
        self.local("sleep 0.5; echo rodou > marca")
        with open(self.trava, "w") as t:
            fcntl.flock(t, fcntl.LOCK_EX)
            p = self.lanca(dict(self.amb, FORGE_PREPUSH_TIMEOUT="2", FORGE_PREPUSH_ESPERA="20"))
            time.sleep(3)
        rc, err, marca = self.fim(p)
        self.assertEqual((rc, marca), (0, True), err)


class AncestralMorto(EnvioDeCodigo):
    """F3: kill -9 em quem pediu o envio encerra a checagem com os filhos (A3), sem sinal para quem não é dela (A5)."""
    def test_kill_9_no_agente_encerra_a_checagem_e_o_hook(self):
        exigir(self, "proc")
        (self.dir / ".githooks" / "pre-push.local").write_text(
            '#!/usr/bin/env bash\ncd "$(dirname "$0")/.."\nsleep 300 & echo $$ $PPID $(ps -o pgid= -p $$) > etapa; sleep 300\n')
        (self.fora / "entrada").write_text("".join(self.linhas))
        intermediario = subprocess.Popen(
            [sys.executable, "-c", "import subprocess, sys; subprocess.run(sys.argv[1:])", shutil.which("bash"), "-c",
             f'.githooks/pre-push origin x < {self.fora}/entrada; echo fim'],
            cwd=self.dir, env=self.amb, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.addCleanup(subprocess.run, ["kill", "-KILL", "--", f"-{intermediario.pid}"], stderr=subprocess.DEVNULL)
        irmao = subprocess.Popen(["sleep", "60"], start_new_session=True)
        self.addCleanup(irmao.kill)
        self.assertTrue(ate((self.dir / "etapa").exists))
        time.sleep(0.3)
        etapa, hook, pgid = (int(x) for x in (self.dir / "etapa").read_text().split())
        time.sleep(1.5)
        self.assertIn(hook, vivos(), "com o agente vivo, nada é encerrado")
        intermediario.kill()
        intermediario.wait()
        self.assertTrue(ate(lambda: pgid not in vivos().values() and hook not in vivos(), prazo=30))
        self.assertIsNone(irmao.poll())

    def test_pid_reusado_conta_como_ancestral_morto(self):
        exigir(self, "proc")
        funcoes = subprocess.run(["sed", "-n", "/^inicio_de() {/,/^}/p;/^ancestral_morto() {/,/^}/p", str(HOOK)],
                                 capture_output=True, text=True, check=True).stdout
        roteiro = funcoes + 'inicio_de $$; ancestrais=("$$ $st_inicio"); ancestral_morto && echo morto || echo vivo\n' \
            'ancestrais=("$$ 1"); ancestral_morto && echo morto || echo vivo\n'
        saida = subprocess.run([shutil.which("bash"), "-c", roteiro], capture_output=True, text=True).stdout.split()
        self.assertEqual(saida, ["vivo", "morto"])


class PrioridadeDaEtapa(EnvioDeCodigo):
    """F4: a checagem roda com nice 10 a mais (e ionice de melhor esforço quando funciona); normal tira os prefixos."""
    def nice_da_etapa(self, amb=None):
        (self.dir / ".githooks" / "pre-push.local").write_text(
            '#!/usr/bin/env bash\nread -r l < /proc/self/stat; set -- ${l##*) }; echo "${17}" > "$(dirname "$0")/../nice"\n')
        rc, err, _ = self.fim(self.lanca(amb))
        self.assertEqual(rc, 0, err)
        return int((self.dir / "nice").read_text())

    def test_nice_baixo_por_padrao_e_normal_desliga(self):
        base = os.nice(0)
        self.assertEqual(self.nice_da_etapa(), min(base + 10, 19))
        self.assertEqual(self.nice_da_etapa(dict(self.amb, FORGE_PREPUSH_PRIORIDADE="normal")), base)

    def test_ionice_que_falha_nao_impede_a_checagem(self):
        falso = self.fora / "falso"
        falso.mkdir()
        (falso / "ionice").write_text("#!/bin/sh\nexit 1\n")
        (falso / "ionice").chmod(0o755)
        self.assertEqual(self.nice_da_etapa(dict(self.amb, PATH=f"{falso}:{self.amb['PATH']}")), min(os.nice(0) + 10, 19))


class ListaDosArquivos(EnvioDeCodigo):
    """F5: FORGE_PREPUSH_ARQUIVOS aponta a lista (NUL) dos arquivos mudados pelo envio; sem base clara, não existe."""
    def setUp(self):
        super().setUp()
        (self.dir / ".githooks" / "pre-push.local").write_text(
            '#!/usr/bin/env bash\ncd "$(dirname "$0")/.."\nif [ -n "${FORGE_PREPUSH_ARQUIVOS+x}" ]; then tr "\\0" "\\n" < "$FORGE_PREPUSH_ARQUIVOS" > lista;'
            ' echo "$FORGE_PREPUSH_ARQUIVOS" > caminho; else echo TUDO > lista; fi\n')

    def envia_e_le(self, linhas):
        self.linhas = linhas
        rc, err, _ = self.fim(self.lanca())
        self.assertEqual(rc, 0, err)
        return sorted((self.dir / "lista").read_text().split("\n")[:-1])

    def test_so_os_arquivos_mudados_sem_os_apagados(self):
        self.escreve("src/velho.ts")
        antes = self.commit("velho")
        self.escreve("src/novo arquivo.ts")
        (self.dir / "src" / "velho.ts").unlink()
        self.escreve("docs/a.md")
        novo = self.commit("muda")
        self.assertEqual(self.envia_e_le([self.ref(novo, antes)]), ["docs/a.md", "src/novo arquivo.ts"])
        self.assertFalse(Path((self.dir / "caminho").read_text().strip()).exists(), "a lista ficou para trás")

    def test_sem_base_clara_olha_tudo(self):
        self.escreve("src/a.ts")
        novo = self.commit("codigo")
        self.assertEqual(self.envia_e_le([self.ref(novo, ZERO)]), ["TUDO"])
        self.assertEqual(self.envia_e_le([self.ref(novo, self.base, "refs/tags/v1")]), ["TUDO"])


class CaminhosExtra(Repo):
    """0.45.3: a chave opcional `caminhos_extra` do .forge/config.json soma pastas ao fim do PATH da checagem (o agente novo do
    piloto abria sem pnpm e travava no pre-push); vale a pasta absoluta, real (sem link), sem `:` e existente."""

    FERRAMENTA = "ferramenta-do-projeto-x"

    def setUp(self):
        super().setUp()
        self.pasta = (self.fora / "ferramentas").resolve()
        self.pasta.mkdir()
        exe = self.pasta / self.FERRAMENTA
        exe.write_text("#!/bin/sh\nexit 0\n")
        exe.chmod(0o755)
        local = self.dir / ".githooks" / "pre-push.local"
        local.write_text(f'#!/usr/bin/env bash\ncommand -v {self.FERRAMENTA} >> "$(dirname "$0")/../marca" || echo ausente >> "$(dirname "$0")/../marca"\n')
        (self.dir / ".forge").mkdir()

    def envia_com(self, config):
        (self.dir / ".forge" / "config.json").write_text(config if isinstance(config, str) else json.dumps(config))
        self.escreve("src/a.ts", str(time.time()))
        r, _ = self.envia([self.ref(self.commit("codigo"), self.base)])
        self.assertEqual(r.returncode, 0, r.stderr)
        return (self.dir / "marca").read_text().splitlines()[-1], r.stderr

    def test_pasta_valida_entra_no_path_da_checagem(self):
        achado, erro = self.envia_com({"caminhos_extra": [str(self.pasta)]})
        self.assertEqual(achado, str(self.pasta / self.FERRAMENTA))
        self.assertNotIn("caminhos_extra", erro)

    def test_sem_a_chave_o_path_nao_muda_e_nada_avisa(self):
        achado, erro = self.envia_com({"pesados": []})
        self.assertEqual(achado, "ausente")
        self.assertNotIn("caminhos_extra", erro)

    def test_pasta_relativa_com_dois_pontos_link_ou_inexistente_fica_de_fora_com_aviso(self):
        link = self.fora / "atalho"
        link.symlink_to(self.pasta)
        casos = {"relativa": "ferramentas", "dois pontos": f"{self.pasta}:/bin", "link": str(link),
                 "ponto-ponto": f"{self.pasta}/../ferramentas", "inexistente": str(self.fora / "nao-existe"), "nao-texto": 7}
        for nome, valor in casos.items():
            with self.subTest(caso=nome):
                achado, erro = self.envia_com({"caminhos_extra": [valor]})
                self.assertEqual(achado, "ausente")
                self.assertIn("pre-push: aviso: caminhos_extra:", erro)
                self.assertIn("ignorada", erro)

    def test_chave_que_nao_e_lista_ou_json_ilegivel_avisa_e_o_envio_segue(self):
        for config in ({"caminhos_extra": str(self.pasta)}, "{nao e json", "[1, 2]"):
            with self.subTest(config=config):
                achado, erro = self.envia_com(config)
                self.assertEqual(achado, "ausente")
                self.assertIn("pre-push: aviso: caminhos_extra:", erro)

    def test_uma_pasta_ruim_nao_derruba_a_boa(self):
        achado, erro = self.envia_com({"caminhos_extra": ["relativa", str(self.pasta)]})
        self.assertEqual(achado, str(self.pasta / self.FERRAMENTA))
        self.assertIn("ignorada", erro)


if __name__ == "__main__":
    unittest.main()
