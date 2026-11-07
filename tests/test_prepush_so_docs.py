"""Pre-push do modelo de projeto. E18 PREPUSH-SO-DOCS: pula o pre-push.local só quando todo arquivo enviado é docs/** ou .md;
F2 (versao-047, E2a): o pre-push.local roda num grupo próprio, e só esse grupo recebe sinal;
F1 (versao-047, E1a): uma checagem do projeto por vez por usuário e máquina.

Cada teste roda o hook de verdade num repositório descartável, num grupo novo criado pelo teste (G-6).
"""
import fcntl
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
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
AMBIENTE.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
PULO = "só docs/** e .md; lint e typecheck pulados"


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
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(marca)

    def test_duas_refs_so_docs_pulam(self):
        self.escreve("docs/a.md")
        a = self.commit("a")
        self.git("checkout", "-q", "-b", "outra", self.base)
        self.escreve("README.md")
        b = self.commit("b")
        r, marca = self.envia([self.ref(a, self.base, "refs/heads/a"), self.ref(b, self.base, "refs/heads/b")])
        self.assertFalse(marca)
        self.assertIn(PULO, r.stdout)

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

    def le(self, nome):
        self.assertTrue(ate((self.dir / nome).exists), nome)
        time.sleep(0.2)
        return [int(x) for x in (self.dir / nome).read_text().split()]

    def fim(self, p):
        try:
            return p.wait(timeout=30), p.stderr.read()
        except subprocess.TimeoutExpired:
            self.fail("o hook não saiu em 30 s")

    def interrompe(self):
        p = self.lanca()
        etapa = self.le("etapa")[0]
        time.sleep(1)
        p.send_signal(signal.SIGTERM)
        rc, err = self.fim(p)
        self.assertEqual(rc, 1)
        self.assertIn("checagem interrompida; o envio foi barrado", err)
        self.assertIn(self.le("irmao")[0], vivos())
        return etapa

    def test_etapa_em_grupo_proprio_e_saida_repassada(self):
        for saida, esperado in ((0, 0), (3, 1)):
            with self.subTest(saida):
                self.etapa(f"exit {saida}")
                p = self.lanca()
                self.assertEqual(self.fim(p)[0], esperado)
                pid, pgid = self.le("etapa")
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
        self.assertTrue(ate(lambda: filho not in vivos()))

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
        self.assertEqual(sorted(f[1].count("aguardando a vez por até 1200 s") for f in fins), [0, 1, 1, 1])

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
        self.addCleanup(os.kill, int((self.fora / "pid").read_text()), 9)
        self.assertEqual(self.fim(self.lanca(dict(self.amb, FORGE_PREPUSH_ESPERA="1")))[0], 0)

    def test_xdg_com_escrita_alheia_recua_para_o_home(self):
        self.fora.chmod(0o777)
        self.assertEqual(self.fim(self.lanca())[0:3:2], (0, True))
        pasta = self.fora / ".local" / "state" / "forge"
        self.assertEqual((self.trava.exists(), (pasta / self.trava.name).exists(), pasta.stat().st_mode & 0o777), (False, True, 0o700))

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


if __name__ == "__main__":
    unittest.main()
