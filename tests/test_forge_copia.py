"""bin/forge-copia: a cópia de trabalho só nasce dentro de ~/.forge-contrib; fora dela, recusa."""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

BIN = Path(__file__).resolve().parent.parent / "bin" / "forge-copia"


class Base(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.home = Path(t.name).resolve() / "home"
        self.pasta = self.home / ".forge-contrib"
        self.pasta.mkdir(parents=True)
        self.fora = Path(t.name).resolve() / "fora"
        self.fora.mkdir()
        self.env = sem_manutencao({**os.environ, "HOME": str(self.home), "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"})
        self.origem = self.pasta / "origem"
        self.git(self.pasta, "init", "-q", "-b", "develop", str(self.origem))
        self.git(self.origem, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "i")
        self.git(self.origem, "remote", "add", "origin", str(self.origem))  # sem remoto, o git nem tentaria rastrear
        self.git(self.origem, "update-ref", "refs/remotes/origin/develop", "HEAD")

    def git(self, cwd, *a):
        return subprocess.run(["git", *a], cwd=cwd, env=self.env, capture_output=True, text=True, check=True)

    def copia(self, *a, cwd=None):
        return subprocess.run(["python3", "-I", str(BIN), *a], cwd=cwd or self.origem, env=self.env, capture_output=True, text=True)

    def branch_de(self, d):
        return self.git(d, "branch", "--show-current").stdout.strip()


class Cria(Base):
    def test_clone_dentro_cria_branch_a_partir_da_base_sem_rastreio(self):
        d = self.pasta / "c1"
        r = self.copia("clone", str(d), "--branch", "melhoria/x", "--origem", str(self.origem))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.branch_de(d), "melhoria/x")
        self.assertEqual(self.git(d, "rev-parse", "HEAD").stdout, self.git(d, "rev-parse", "origin/develop").stdout)
        cfg = subprocess.run(["git", "config", "--get", "branch.melhoria/x.remote"], cwd=d, env=self.env, capture_output=True)
        self.assertNotEqual(cfg.returncode, 0)  # --no-track: sem upstream

    def test_clone_com_base_que_nao_existe_falha_com_1(self):
        r = self.copia("clone", str(self.pasta / "c3"), "--branch", "melhoria/x", "--origem", str(self.origem), "--base", "origin/nada")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertFalse((self.pasta / "c3").exists(), "COPIA-BASE: a cópia sem base não fica na branch padrão")
        self.assertIn("apaguei a cópia", r.stderr)

    def commit_em(self, branch):
        """Commit novo na origem, na branch dada (criada se falta); devolve o sha."""
        self.git(self.origem, "switch", "-q", "-C", branch)
        self.git(self.origem, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", branch)
        return self.git(self.origem, "rev-parse", "HEAD").stdout.strip()

    def test_clone_que_nasce_na_main_aceita_base_sem_origin(self):
        dev = self.git(self.origem, "rev-parse", "develop").stdout.strip()
        main = self.commit_em("main")  # a origem fica na main: o clone nasce nela e `develop` local não existe
        d = self.pasta / "c4"
        r = self.copia("clone", str(d), "--branch", "melhoria/x", "--origem", str(self.origem), "--base", "develop")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.branch_de(d), "melhoria/x")
        head = self.git(d, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(head, dev)
        self.assertNotEqual(head, main)

    def test_branch_que_ja_existe_no_remoto_parte_do_head_dela(self):
        remoto = self.commit_em("melhoria/x")
        self.git(self.origem, "switch", "-q", "develop")
        d = self.pasta / "c5"
        r = self.copia("clone", str(d), "--branch", "melhoria/x", "--origem", str(self.origem))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.branch_de(d), "melhoria/x")
        self.assertEqual(self.git(d, "rev-parse", "HEAD").stdout.strip(), remoto)
        self.assertIn("já existe no remoto", r.stderr)
        cfg = subprocess.run(["git", "config", "--get", "branch.melhoria/x.remote"], cwd=d, env=self.env, capture_output=True)
        self.assertNotEqual(cfg.returncode, 0)  # --no-track: sem upstream

    def test_branch_do_remoto_com_base_curta_nasce_no_head_dela_e_diz_o_sha(self):
        """v0481 E14.33: origem na main, --base develop e a branch já no remoto: nasce no head remoto e diz o sha."""
        remoto = self.commit_em("melhoria/y")
        self.commit_em("main")
        d = self.pasta / "c8"
        r = self.copia("clone", str(d), "--branch", "melhoria/y", "--origem", str(self.origem), "--base", "develop")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.git(d, "rev-parse", "HEAD").stdout.strip(), remoto)
        self.assertIn(f"criei melhoria/y em {remoto} (de origin/melhoria/y)", r.stderr)

    def test_clone_pela_base_diz_o_sha_dela(self):
        dev = self.git(self.origem, "rev-parse", "develop").stdout.strip()
        self.commit_em("main")  # o clone nasce na main: `develop` só existe como origin/develop
        r = self.copia("clone", str(self.pasta / "c9"), "--branch", "melhoria/z", "--origem", str(self.origem), "--base", "develop")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"criei melhoria/z em {dev} (de origin/develop)", r.stderr)

    def test_base_curta_que_nao_resolve_falha_fechado_sem_clone(self):
        d = self.pasta / "c10"
        r = self.copia("clone", str(d), "--branch", "melhoria/x", "--origem", str(self.origem), "--base", "nada")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertFalse(d.exists(), "base que não resolve: o clone não fica")
        self.assertNotIn("forge-copia: criei", r.stderr)

    def test_clone_que_falha_sai_1_antes_de_procurar_a_base(self):
        r = self.copia("clone", str(self.pasta / "c7"), "--branch", "melhoria/x", "--origem", str(self.fora / "nada"))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertNotIn("não criei", r.stderr)

    def test_switch_que_falha_apaga_a_copia(self):
        d = self.pasta / "c6"
        r = self.copia("clone", str(d), "--branch", "develop", "--origem", str(self.origem))  # `develop` já existe no clone
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertFalse(d.exists())
        self.assertIn("o git switch falhou a partir de origin/develop", r.stderr)  # FORGE-COPIA-MENSAGEM: a ref tentada

    def test_mensagem_sem_ponto_cita_as_refs_tentadas_sem_origin_duplicado(self):
        r = self.copia("clone", str(self.pasta / "m2"), "--branch", "melhoria/x", "--origem", str(self.origem), "--base", "origin/nada")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("nenhuma destas refs existe no clone: origin/melhoria/x, origin/nada;", r.stderr)
        self.assertNotIn("origin/origin/", r.stderr)
        r = self.copia("clone", str(self.pasta / "m3"), "--branch", "melhoria/x", "--origem", str(self.origem), "--base", "nada")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("refs existe no clone: origin/melhoria/x, nada, origin/nada;", r.stderr)

    def test_worktree_dentro_cria_a_branch(self):
        d = self.pasta / "wt" / "w1"
        r = self.copia("worktree", str(d), "--branch", "melhoria/w", "--base", "origin/develop")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.branch_de(d), "melhoria/w")
        cfg = subprocess.run(["git", "config", "--get", "branch.melhoria/w.remote"], cwd=d, env=self.env, capture_output=True)
        self.assertNotEqual(cfg.returncode, 0)  # --no-track: sem upstream


class Revisao(Base):
    """COPIA-REVISAO: o clone do revisor nasce no head remoto da branch, sem upstream e sem cair na base."""

    def test_clone_de_revisao_parte_do_head_remoto_sem_upstream(self):
        self.git(self.origem, "switch", "-q", "-c", "melhoria/r")
        self.git(self.origem, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "r")
        remoto = self.git(self.origem, "rev-parse", "HEAD").stdout.strip()
        self.git(self.origem, "switch", "-q", "develop")
        d = self.pasta / "x-rev"
        r = self.copia("clone", str(d), "--branch", "melhoria/r", "--origem", str(self.origem), "--revisao")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.branch_de(d), "melhoria/r")
        self.assertEqual(self.git(d, "rev-parse", "HEAD").stdout.strip(), remoto)
        cfg = subprocess.run(["git", "config", "--get", "branch.melhoria/r.remote"], cwd=d, env=self.env, capture_output=True)
        self.assertNotEqual(cfg.returncode, 0)

    def test_branch_fora_do_remoto_nao_cai_na_base(self):
        d = self.pasta / "y-rev"
        r = self.copia("clone", str(d), "--branch", "melhoria/nao-existe", "--origem", str(self.origem), "--revisao")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertFalse(d.exists())
        self.assertIn("nenhuma destas refs existe no clone: origin/melhoria/nao-existe;", r.stderr)
        self.assertNotIn("origin/develop", r.stderr)

    def test_worktree_de_revisao_e_recusada(self):
        d = self.pasta / "wt" / "w-rev"
        r = self.copia("worktree", str(d), "--branch", "melhoria/w", "--revisao")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("--revisao é só do clone", r.stderr)
        self.assertFalse(d.exists())


class Recusa(Base):
    def recusado(self, destino, *extra):
        r = self.copia("worktree", str(destino), "--branch", "melhoria/z", "--base", "origin/develop", *extra)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("recusado", r.stderr)
        return r

    def test_fora_da_pasta(self):
        self.recusado(self.fora / "w")
        self.assertFalse((self.fora / "w").exists())

    def test_com_ponto_ponto_mesmo_voltando_para_dentro(self):
        self.recusado(f"{self.pasta}/x/../y")

    def test_por_link_simbolico(self):
        (self.pasta / "atalho").symlink_to(self.fora)
        self.recusado(self.pasta / "atalho" / "w")
        self.assertFalse((self.fora / "w").exists())

    def test_a_propria_pasta_liberada(self):
        self.recusado(self.pasta)

    def test_prefixo_parecido_nao_vale(self):
        irmao = self.home / ".forge-contrib-outro"
        irmao.mkdir()
        self.recusado(irmao / "w")

    def test_a_pasta_liberada_vazia_tambem_e_recusada(self):
        vazia = self.home / ".forge-contrib"
        for item in list(vazia.iterdir()):
            item.rename(self.fora / item.name)
        r = self.copia("worktree", str(vazia), "--branch", "melhoria/z", cwd=self.fora / "origem")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("própria pasta", r.stderr)

    def test_destino_ocupado(self):
        (self.pasta / "ocupado").mkdir()
        (self.pasta / "ocupado" / "a").write_text("x")
        self.recusado(self.pasta / "ocupado")

    def test_branch_ou_base_com_cara_de_opcao(self):
        r = self.copia("worktree", str(self.pasta / "w"), "--branch=--detach", "--base", "origin/develop")
        self.assertEqual(r.returncode, 2, r.stderr)
        r = self.copia("worktree", str(self.pasta / "w"), "--branch", "melhoria/q", "--base=--orphan")
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_clone_sem_origem(self):
        r = self.copia("clone", str(self.pasta / "c"), "--branch", "melhoria/q")
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_origem_com_cara_de_opcao(self):
        r = self.copia("clone", str(self.pasta / "c"), "--branch", "melhoria/q", "--origem=--upload-pack=x")
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_nome_de_branch_invalido(self):
        r = self.copia("worktree", str(self.pasta / "w"), "--branch", "a..b")
        self.assertEqual(r.returncode, 2, r.stderr)


class Instalar(Base):
    """--instalar com stack falsa (pacote em raiz temporária, sem rede): roda o comando declarado dentro da cópia."""

    def pacote(self, spec, detecta_em=None):
        raiz = self.fora / "raiz"
        (raiz / "bin").mkdir(parents=True)
        (raiz / "bin" / "forge-copia").write_text(BIN.read_text())
        (raiz / "bin" / "forge_disco.py").write_text((BIN.parent / "forge_disco.py").read_text())
        (raiz / "stacks" / "falsa").mkdir(parents=True)
        (raiz / "stacks" / "falsa" / "instalar.json").write_text(spec if isinstance(spec, str) else json.dumps(spec))
        self.bin = raiz / "bin" / "forge-copia"
        if detecta_em:
            (self.origem / detecta_em).write_text("x")
            self.git(self.origem, "add", detecta_em)
            self.git(self.origem, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "d")
            self.git(self.origem, "update-ref", "refs/remotes/origin/develop", "HEAD")

    def roda(self, destino, *extra):
        return subprocess.run(["python3", "-I", str(self.bin), "clone", str(destino), "--branch", "melhoria/i", "--origem", str(self.origem), *extra],
                              cwd=self.origem, env=self.env, capture_output=True, text=True)

    def test_roda_o_comando_declarado_dentro_da_copia(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "pwd > instalado.txt"]]}, "marca.txt")
        d = self.pasta / "i1"
        r = self.roda(d, "--instalar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(Path((d / "instalado.txt").read_text().strip()).resolve(), d.resolve())

    def test_sem_pasta_de_stacks_avisa_e_sai_0(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "touch instalado.txt"]]}, "marca.txt")
        shutil.rmtree(self.bin.parent.parent / "stacks")
        r = self.roda(self.pasta / "i9", "--instalar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nenhuma stack detectada", r.stderr)

    def test_pacote_sem_instalar_json_e_ignorado(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "touch instalado.txt"]]}, "marca.txt")
        (self.bin.parent.parent / "stacks" / "sem").mkdir()
        r = self.roda(self.pasta / "i10", "--instalar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.pasta / "i10" / "instalado.txt").exists())

    def test_worktree_tambem_instala(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "touch instalado.txt"]]}, "marca.txt")
        d = self.pasta / "wt" / "i8"
        r = subprocess.run(["python3", "-I", str(self.bin), "worktree", str(d), "--branch", "melhoria/i8", "--instalar"],
                           cwd=self.origem, env=self.env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((d / "instalado.txt").exists())

    def test_sem_a_opcao_nao_instala(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "touch instalado.txt"]]}, "marca.txt")
        self.assertEqual(self.roda(self.pasta / "i2").returncode, 0)
        self.assertFalse((self.pasta / "i2" / "instalado.txt").exists())

    def test_stack_nao_detectada_avisa_e_sai_0(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "touch instalado.txt"]]})
        r = self.roda(self.pasta / "i3", "--instalar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nenhuma stack detectada", r.stderr)
        self.assertFalse((self.pasta / "i3" / "instalado.txt").exists())

    def test_comando_que_falha_sai_1_e_diz_qual(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "exit 3"]]}, "marca.txt")
        r = self.roda(self.pasta / "i4", "--instalar")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("rc=3", r.stderr)

    def test_comando_ausente_sai_1_com_mensagem(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["gerenciador-que-nao-existe", "install"]]}, "marca.txt")
        r = self.roda(self.pasta / "i5", "--instalar")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("indisponível", r.stderr)

    def test_falha_interrompe_os_comandos_seguintes(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "exit 1"], ["sh", "-c", "touch depois.txt"]]}, "marca.txt")
        self.roda(self.pasta / "i6", "--instalar")
        self.assertFalse((self.pasta / "i6" / "depois.txt").exists())

    def test_spec_invalida_sai_1(self):
        for spec in ("nao e json", {"detecta": ["marca.txt"], "comandos": ["sh -c touch x"]}, {"comandos": []},
                     {"detecta": "marca.txt", "comandos": [["sh", "-c", "true"]]}):
            self.pacote(spec, "marca.txt")
            r = self.roda(self.pasta / "i7", "--instalar")
            self.assertEqual(r.returncode, 1, r.stderr)
            self.assertIn("inválido", r.stderr)
            shutil.rmtree(self.pasta / "i7", ignore_errors=True)
            shutil.rmtree(self.fora / "raiz")

    def test_nao_afrouxa_a_recusa_de_pasta(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "touch instalado.txt"]]}, "marca.txt")
        r = self.roda(self.fora / "c", "--instalar")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertFalse((self.fora / "c").exists())

    def test_instalacao_roda_sem_credencial_no_ambiente(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "env > ambiente.txt"]]}, "marca.txt")
        cred = {n: "f" for n in ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN", "GIT_ASKPASS", "SSH_AUTH_SOCK")}
        self.env.update({**cred, "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "user.name", "GIT_CONFIG_VALUE_0": "v"})
        d = self.pasta / "i11"
        r = self.roda(d, "--instalar")
        self.assertEqual(r.returncode, 0, r.stderr)
        nomes = {l.split("=", 1)[0] for l in (d / "ambiente.txt").read_text().splitlines()}
        self.assertIn("HOME", nomes)
        for n in (*cred, "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0"):
            self.assertNotIn(n, nomes)

    def test_instalacao_tira_config_injetada_e_nomes_de_segredo(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", "env > ambiente.txt"]]}, "marca.txt")
        falsas = ("GIT_CONFIG_PARAMETERS", "FOO_TOKEN", "bar_secret_x", "MEU_PASSWORD", "TOKEN")
        self.env.update({n: "f" for n in falsas}, MINHA_VAR="ok", GIT_CONFIG_PARAMETERS="'user.name'='f'")  # formato válido do git
        d = self.pasta / "i13"
        self.assertEqual(self.roda(d, "--instalar").returncode, 0)
        nomes = {l.split("=", 1)[0] for l in (d / "ambiente.txt").read_text().splitlines()}
        self.assertIn("MINHA_VAR", nomes)
        for n in falsas:
            self.assertNotIn(n, nomes)

    def test_ambiente_da_instalacao_mantem_o_resto(self):
        self.pacote({"detecta": ["marca.txt"], "comandos": [["sh", "-c", 'echo "$MINHA_VAR" > v.txt']]}, "marca.txt")
        self.env["MINHA_VAR"] = "ok"
        d = self.pasta / "i12"
        self.assertEqual(self.roda(d, "--instalar").returncode, 0)
        self.assertEqual((d / "v.txt").read_text().strip(), "ok")

    def test_pacotes_reais_declaram_instalar_valido(self):
        stacks = list((BIN.parent.parent / "stacks").iterdir())
        self.assertGreaterEqual(len(stacks), 2)
        for stack in stacks:
            spec = json.loads((stack / "instalar.json").read_text())
            self.assertIsInstance(spec["detecta"], list, stack.name)
            self.assertTrue(spec["detecta"] and spec["comandos"], stack.name)
            self.assertTrue(all(isinstance(c, list) and c and all(isinstance(x, str) for x in c) for c in spec["comandos"]), stack.name)

    def test_todo_instalar_json_usa_modo_congelado_ou_hash_e_detecta_o_lockfile(self):
        for stack in (BIN.parent.parent / "stacks").iterdir():
            spec = json.loads((stack / "instalar.json").read_text())
            self.assertTrue(all("lock" in f for f in spec["detecta"]), f"{stack.name}: detecta tem de apontar o lockfile")
            instala = [c for c in spec["comandos"] if "install" in c]
            self.assertTrue(instala, stack.name)
            for c in instala:
                if c[0] == "pnpm" or c[0] == "npm":
                    self.assertTrue("--frozen-lockfile" in c or c[:2] == ["npm", "ci"], f"{stack.name}: {c}")
                else:
                    self.assertTrue("--no-deps" in c or "--require-hashes" in c, f"{stack.name}: {c}")
                    if "-r" in c:
                        self.assertIn("--require-hashes", c, stack.name)
                        self.assertIn("--no-deps", c, stack.name)
                    else:
                        self.assertIn("--no-deps", c, stack.name)  # pacote local sem resolver dependência


def disco(usado, livre):
    return shutil._ntuple_diskusage(usado + livre, usado, livre)


class Disco(unittest.TestCase):
    """MP6: disco falso (shutil.disk_usage trocado no processo), sem encher disco de verdade; o git do clone também é falso."""

    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.home = Path(t.name).resolve()
        (self.home / ".forge-contrib").mkdir()
        self.mod = SourceFileLoader("forge_copia_teste", str(BIN)).load_module()
        self.gits = []
        for alvo in (mock.patch.dict(os.environ, {"HOME": str(self.home)}),
                     mock.patch.object(self.mod, "git", lambda *a, cwd=None: self.gits.append(a) or 0),
                     mock.patch.object(self.mod, "ponto_de_partida", lambda *a: "origin/develop")):  # o clone falso não tem refs
            alvo.start()
            self.addCleanup(alvo.stop)

    def copiar(self, uso):
        erro = io.StringIO()
        with mock.patch("shutil.disk_usage", **uso), redirect_stderr(erro):
            rc = self.mod.main(["clone", str(self.home / ".forge-contrib" / "c"), "--branch", "melhoria/q", "--origem", "o"])
        return rc, erro.getvalue()

    def test_acima_do_limiar_recusa_e_manda_limpar_sem_chamar_o_git(self):
        rc, erro = self.copiar({"return_value": disco(91, 9)})
        self.assertEqual((rc, self.gits), (2, []), erro)
        self.assertIn("91% de uso, acima de 90%", erro)
        self.assertIn("--limpar", erro)

    def test_no_limiar_cria(self):
        rc, erro = self.copiar({"return_value": disco(90, 10)})
        self.assertEqual(rc, 0, erro)
        self.assertEqual(self.gits[0][0], "clone")

    def test_disco_ilegivel_recusa(self):
        rc, erro = self.copiar({"side_effect": OSError("sem statvfs")})
        self.assertEqual((rc, self.gits), (2, []), erro)
        self.assertIn("não consegui medir o disco", erro)

    def test_disco_sem_espaco_ocupavel_conta_como_cheio(self):
        rc, erro = self.copiar({"return_value": disco(0, 0)})
        self.assertEqual((rc, self.gits), (2, []), erro)

    def test_destino_novo_mede_o_pai_que_existe(self):
        medidos = []
        rc, erro = self.copiar({"side_effect": lambda p: medidos.append(p) or disco(1, 99)})
        self.assertEqual((rc, medidos), (0, [str(self.home / ".forge-contrib")]), erro)

    def test_o_limiar_mora_so_no_forge_disco(self):
        self.assertEqual(self.mod.LIMIAR_DISCO, 90)
        for nome in ("forge-copia", "forge-placar"):
            self.assertNotRegex((BIN.parent / nome).read_text(), r"\b90\s*%|>\s*90\b")


GH_ESTADOS = ('#!/bin/sh\n[ -f "$GH_FALHA" ] && exit 1\ncase "$*" in *isCrossRepository*) ;; *) exit 1 ;; esac\n'
              'cat "$GH_ESTADOS" 2>/dev/null\nexit 0\n')  # linhas "<estado> <isCrossRepository>", como o --jq do forge-copia


class Limpar(Base):
    """LIMPEZA-AO-FIM-DO-ITEM: `forge-copia limpar` apaga a cópia do item acabado (PR fechado, mesclado ou `vazio: sim`), só limpa e com tudo
    na origem; o `gh` falso, no PATH, devolve os estados do arquivo GH_ESTADOS (sem rede, R-CUSTO)."""
    def setUp(self):
        super().setUp()
        fal = self.home.parent / "falsos"
        fal.mkdir()
        (fal / "gh").write_text(GH_ESTADOS)
        (fal / "gh").chmod(0o755)
        self.estados = self.home.parent / "estados"
        self.env.update(PATH=f"{fal}:{os.environ['PATH']}", GH_ESTADOS=str(self.estados), GH_FALHA=str(self.home.parent / "gh-falha"))
        self.estados.write_text("CLOSED false\n")

    def clone(self):
        d = self.pasta / "wt" / "c1"
        self.assertEqual(self.copia("clone", str(d), "--branch", "melhoria/x", "--origem", str(self.origem)).returncode, 0)
        return d

    def fica(self, d, motivo):
        r = self.copia("limpar", str(d))
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(motivo, r.stderr)
        self.assertTrue(d.is_dir())

    def test_clone_de_pr_fechado_sem_merge_e_apagado(self):
        d = self.clone()
        r = self.copia("limpar", str(d))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(d.exists())

    def test_worktree_de_pr_fechado_sai_e_a_branch_fica(self):
        d = self.pasta / "wt" / "w1"
        self.assertEqual(self.copia("worktree", str(d), "--branch", "melhoria/w").returncode, 0)
        r = self.copia("limpar", str(d))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(d.exists())
        self.assertNotIn(str(d), self.git(self.origem, "worktree", "list").stdout)
        self.assertEqual(self.git(self.origem, "branch", "--list", "melhoria/w").stdout.strip(), "melhoria/w")

    def test_copia_suja_fica(self):
        d = self.clone()
        (d / "novo").write_text("x\n")
        (self.home.parent / "gh-falha").write_text("")  # a cópia suja fica antes de qualquer consulta ao gh
        self.fica(d, "mudança ou arquivo novo")

    def test_worktree_suja_fica(self):
        d = self.pasta / "wt" / "w2"
        self.copia("worktree", str(d), "--branch", "melhoria/w2")
        (d / "novo").write_text("x\n")
        self.fica(d, "mudança ou arquivo novo")

    def test_stash_fica(self):
        d = self.clone()
        (d / "s").write_text("x\n")
        self.git(d, "add", "s")
        self.git(d, "-c", "user.name=t", "-c", "user.email=t@t", "stash", "-q")
        self.fica(d, "stash")

    def test_commit_fora_da_origem_fica(self):
        d = self.clone()
        self.git(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "local")
        self.fica(d, "commit fora da origem")

    def test_worktree_com_commit_fora_da_origem_fica(self):
        d = self.pasta / "wt" / "w3"
        self.copia("worktree", str(d), "--branch", "melhoria/w3")
        self.git(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "local")
        self.fica(d, "commit fora da origem")

    def test_clone_com_worktree_ligada_fica(self):
        d = self.clone()
        self.git(d, "worktree", "add", "-q", "-b", "outra", str(self.pasta / "wt" / "lig"), "origin/develop")
        self.fica(d, "worktree ligada")

    def test_pr_aberto_fica(self):
        self.estados.write_text("CLOSED false\nOPEN false\n")
        self.fica(self.clone(), "PR aberto")

    def test_pr_fechado_de_fork_com_o_mesmo_nome_nao_encerra_o_item(self):
        self.estados.write_text("CLOSED true\n")  # A1: o PR fechado vem de fork; a branch tem commit e não há `vazio: sim`
        d = self.clone()
        (d / "so-na-branch").write_text("x\n")
        self.git(d, "add", "so-na-branch")
        self.git(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "b")
        self.git(d, "push", "-q", "origin", "melhoria/x")
        self.fica(d, "vazio: sim")

    def test_escrita_durante_a_consulta_ao_gh_fica(self):
        d = self.clone()
        mod = SourceFileLoader("forge_copia_corrida", str(BIN)).load_module()

        def escreve(*_):  # A2: alguém escreve na cópia enquanto o gh responde
            (d / "novo").write_text("x\n")

        erro = io.StringIO()
        with mock.patch.dict(os.environ, {"HOME": str(self.home)}), mock.patch.object(mod, "fim_do_item", side_effect=escreve), \
                redirect_stderr(erro):
            rc = mod.main(["limpar", str(d)])
        self.assertEqual(rc, 2, erro.getvalue())
        self.assertIn("mudou durante a consulta ao gh", erro.getvalue())
        self.assertTrue((d / "novo").is_file())

    def test_gh_que_falha_fica(self):
        (self.home.parent / "gh-falha").write_text("")
        self.fica(self.clone(), "gh pr list")

    def test_sem_pr_e_sem_vazio_sim_fica(self):
        self.estados.write_text("")
        d = self.clone()
        (d / "so-na-branch").write_text("x\n")
        self.git(d, "add", "so-na-branch")
        self.git(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "b")
        self.git(d, "push", "-q", "origin", "melhoria/x")
        self.fica(d, "vazio: sim")

    def test_sem_pr_com_vazio_sim_e_apagado(self):
        self.estados.write_text("")
        d = self.clone()
        quem = ("-c", "user.name=t", "-c", "user.email=t@t")
        for repo, msg in ((self.origem, "na develop"), (d, "na branch")):
            (repo / "f").write_text("igual\n")
            self.git(repo, "add", "f")
            self.git(repo, *quem, "commit", "-q", "-m", msg)
        self.git(d, "push", "-q", "origin", "melhoria/x")
        self.git(d, "fetch", "-q", "origin")
        r = self.copia("limpar", str(d))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(d.exists())

    def test_fora_da_pasta_ou_a_propria_pasta(self):
        fora = self.fora / "c"  # cópia limpa e de PR fechado, só que fora da pasta liberada
        self.git(self.fora, "clone", "-q", str(self.origem), str(fora))
        self.git(fora, "switch", "-q", "-c", "melhoria/f")
        for alvo in (fora, self.pasta):
            with self.subTest(alvo=alvo):
                r = self.copia("limpar", str(alvo))
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("fica fora de", r.stderr)
                self.assertTrue(alvo.is_dir())

    def test_pasta_que_nao_e_raiz_de_copia_fica(self):
        d = self.clone()
        (d / "sub").mkdir()
        self.fica(d / "sub", "raiz de uma cópia git")

    def test_head_solto_fica(self):
        d = self.clone()
        self.git(d, "switch", "-q", "--detach")
        self.fica(d, "não está numa branch")

    def test_criar_sem_branch_e_recusado(self):
        r = self.copia("clone", str(self.pasta / "c9"), "--origem", str(self.origem))
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("pede --branch", r.stderr)

    def test_base_com_cara_de_opcao_e_recusada(self):
        d = self.clone()
        r = self.copia("limpar", str(d), "--base=--x")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("base começa com", r.stderr)
        self.assertTrue(d.is_dir())

    def test_worktree_travada_fica_com_codigo_1(self):
        d = self.pasta / "wt" / "w4"
        self.copia("worktree", str(d), "--branch", "melhoria/w4")
        self.git(self.origem, "worktree", "lock", str(d))
        r = self.copia("limpar", str(d))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertTrue(d.is_dir())

    def test_rm_que_falha_sai_1_e_diz(self):
        d = self.clone()
        mod = SourceFileLoader("forge_copia_limpar", str(BIN)).load_module()
        erro = io.StringIO()
        with mock.patch.dict(os.environ, {"HOME": str(self.home)}), mock.patch.object(mod, "fim_do_item", return_value=None), \
                mock.patch.object(mod.shutil, "rmtree", side_effect=OSError(13, "negado")), redirect_stderr(erro):
            rc = mod.main(["limpar", str(d)])
        self.assertEqual(rc, 1, erro.getvalue())
        self.assertIn("não consegui apagar", erro.getvalue())
        self.assertTrue(d.is_dir())


class Projeto(Base):
    """MODELO-COPIAS-EM-PASTA-PROPRIA: num projeto (.forge/config.json, sem .claude-plugin/), a cópia é um clone em <projeto>/.forge/wt,
    gravável no sandbox dele e fora do git por um .gitignore `*`; o projeto não usa ~/.forge-contrib (R-LIMITES); o Forge segue nela."""
    def repo(self, pasta, *marcas):
        pasta.mkdir()
        self.git(pasta, "init", "-q", "-b", "develop")
        for m in marcas:
            (pasta / m).parent.mkdir(parents=True, exist_ok=True)
            (pasta / m).write_text("{}\n")
        self.git(pasta, "add", "-A")
        self.git(pasta, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "i")
        self.git(pasta, "remote", "add", "origin", str(pasta))
        self.git(pasta, "update-ref", "refs/remotes/origin/develop", "HEAD")
        return pasta

    def setUp(self):
        super().setUp()
        self.proj = self.repo(self.fora / "proj", ".forge/config.json")
        self.wt = self.proj / ".forge" / "wt"

    def clonar(self, destino, cwd=None, branch="melhoria/p"):
        return self.copia("clone", str(destino), "--branch", branch, "--origem", str(self.proj), cwd=cwd or self.proj)

    def test_clone_fica_em_forge_wt_e_fora_do_git_do_projeto(self):
        r = self.clonar(self.wt / "i1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.branch_de(self.wt / "i1"), "melhoria/p")
        self.assertEqual((self.wt / ".gitignore").read_text(), "*\n")
        self.assertEqual(self.git(self.proj, "status", "--porcelain").stdout, "")

    def test_projeto_recusa_a_pasta_do_forge(self):
        r = self.clonar(self.pasta / "wt" / "p1")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("fica fora de", r.stderr)
        self.assertFalse((self.pasta / "wt" / "p1").exists())

    def test_de_dentro_de_uma_copia_vale_a_pasta_do_projeto(self):
        self.assertEqual(self.clonar(self.wt / "i1").returncode, 0)
        r = self.clonar(self.wt / "i2", cwd=self.wt / "i1", branch="melhoria/q")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.wt / "i1" / ".forge" / "wt").exists())

    def test_gitignore_que_ja_existe_nao_e_tocado(self):
        self.wt.mkdir(parents=True)
        (self.wt / ".gitignore").write_text("x\n")
        self.assertEqual(self.clonar(self.wt / "i1").returncode, 0)
        self.assertEqual((self.wt / ".gitignore").read_text(), "x\n")

    def versionar_link(self, caminho, alvo):
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.symlink_to(alvo)
        self.git(self.proj, "add", "-A")
        self.git(self.proj, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "link")

    def test_s1_forge_wt_como_link_para_a_pasta_do_forge_e_recusado(self):
        (self.pasta / "wt").mkdir()
        self.versionar_link(self.wt, self.pasta / "wt")
        r = self.clonar(self.wt / "x")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("fica fora de", r.stderr)
        self.assertEqual(list((self.pasta / "wt").iterdir()), [])

    def test_s2_gitignore_link_solto_e_recusado_sem_gravar_fora(self):
        alvo = self.fora / "alvo_fora"
        self.versionar_link(self.wt / ".gitignore", alvo)
        r = self.clonar(self.wt / "i1")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("link simbólico", r.stderr)
        self.assertFalse(alvo.exists())
        self.assertFalse((self.wt / "i1").exists())

    def test_o_forge_segue_com_a_pasta_do_home(self):
        forge = self.repo(self.fora / "forge", ".forge/config.json", ".claude-plugin/plugin.json")
        r = self.clonar(forge / ".forge" / "wt" / "f1", cwd=forge)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertEqual(self.clonar(self.pasta / "wt" / "f2", cwd=forge).returncode, 0)
        self.assertFalse((self.pasta / ".gitignore").exists())
        self.assertFalse((forge / ".forge" / "wt").exists())

    def test_fora_de_git_vale_a_pasta_do_home(self):
        solta = self.fora / "solta"
        (solta / ".forge").mkdir(parents=True)
        (solta / ".forge" / "config.json").write_text("{}\n")
        self.env["GIT_CEILING_DIRECTORIES"] = str(self.fora)
        r = self.clonar(self.pasta / "wt" / "s1", cwd=solta)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_limpar_apaga_a_copia_do_projeto(self):
        fal = self.home.parent / "falsos"
        fal.mkdir()
        (fal / "gh").write_text(GH_ESTADOS)
        (fal / "gh").chmod(0o755)
        (self.home.parent / "estados").write_text("CLOSED false\n")
        self.env.update(PATH=f"{fal}:{os.environ['PATH']}", GH_ESTADOS=str(self.home.parent / "estados"), GH_FALHA=str(fal / "nao"))
        self.assertEqual(self.clonar(self.wt / "c1").returncode, 0)
        r = self.copia("limpar", str(self.wt / "c1"), cwd=self.proj)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.wt / "c1").exists())


PEDIDO_DO_BRIEF = ("---\nid: {id}\n---\n# Pedido P\n\n## Escopo\n- E1. X · `confirmado`\n\n## Etapas\n- E1.1 (dev-exemplo): o recurso X.\n\n"
                   "## Decisões do usuário (registro literal)\nDECISÃO DO DONO (2026-01-01): \"A\".\n")


class BriefSugereACopia(unittest.TestCase):
    """CLONE-NOME-UNICO (E172.7): o `brief gerar` sugere a cópia só do agente (branch e papel), livre na hora; e BRIEF-PEDIDO-ID-CRU:
    o `id:` do pedido fora da forma sai como PREENCHER (ia cru, com crase, ao `comece por` e às `decisões:`), e o selo recusa PREENCHER."""

    def setUp(self):
        from test_pre_envio_brief import fc
        self.fc = fc
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.tmp = Path(t.name).resolve()
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.raiz = self.tmp / "repo"
        (self.raiz / "docs" / "pedidos").mkdir(parents=True)
        ambiente = mock.patch.dict(os.environ, {"HOME": str(self.home)})
        ambiente.start()
        self.addCleanup(ambiente.stop)

    def sugerida(self, forge, branch="melhoria/x", papel="tech-lead", raiz=None):
        with mock.patch.object(self.fc, "e_o_forge", return_value=forge):
            return self.fc.copia_sugerida(raiz or self.raiz, branch, papel)

    def gerar(self, id_="p", branch="melhoria/x", etapa="codigo"):
        (self.raiz / "docs" / "pedidos" / "p.md").write_text(PEDIDO_DO_BRIEF.format(id=id_), encoding="utf-8")
        fc = self.fc
        with mock.patch.object(fc, "e_o_forge", return_value=True), mock.patch.object(fc, "pareceres_da_etapa", return_value=[]), \
                mock.patch.object(fc, "estado_da_branch", return_value=([], [])), mock.patch.object(fc, "pr_da_branch", return_value=({}, None)), \
                mock.patch.object(fc, "portao_na_branch", return_value=(None, None)), \
                mock.patch.object(fc, "base_sha_real", return_value="b" * 40), redirect_stderr(io.StringIO()):
            return fc.montar_brief(self.raiz, "p", "forge:dev-exemplo", branch, "develop", etapa=etapa, cobre="E1.1")

    def test_no_forge_o_nome_leva_branch_e_papel_na_pasta_das_copias(self):
        self.assertEqual(self.sugerida(True), str(self.home / ".forge-contrib" / "wt" / "x-tech-lead"))

    def test_nome_tomado_sugere_o_seguinte_livre(self):
        tomada = self.home / ".forge-contrib" / "wt" / "x-tech-lead"
        tomada.mkdir(parents=True)
        (tomada / "a").write_text("")
        self.assertEqual(self.sugerida(True), str(tomada) + "-2")

    def test_papeis_diferentes_na_mesma_branch_tem_copias_diferentes(self):
        self.assertNotEqual(self.sugerida(True, papel="qa"), self.sugerida(True, papel="tech-lead"))

    def test_no_projeto_a_pasta_e_a_do_projeto_tambem_de_dentro_de_uma_copia(self):
        esperado = str(self.raiz / ".forge" / "wt" / "x-qa")
        self.assertEqual(self.sugerida(False, papel="qa"), esperado)
        self.assertEqual(self.sugerida(False, papel="qa", raiz=self.raiz / ".forge" / "wt" / "outra"), esperado)

    def test_branch_ou_papel_fora_da_forma_nao_sugere(self):
        self.assertIsNone(self.sugerida(True, branch="-x"))
        self.assertIsNone(self.sugerida(True, branch="melhoria/a..b"))
        self.assertIsNone(self.sugerida(True, papel="Tech`lead"))
        self.assertIsNone(self.sugerida(True, papel=None))

    def test_sem_o_forge_copia_ao_lado_nao_sugere(self):
        with mock.patch.object(self.fc, "PLUGIN", self.tmp):
            self.assertIsNone(self.sugerida(True))

    def test_brief_gerado_traz_a_copia_sugerida(self):
        saida, rc, erros = self.gerar()
        self.assertEqual(rc, 0, erros)
        copia = self.home / ".forge-contrib" / "wt" / "x-dev-exemplo"
        self.assertIn(f"- cópia só sua (novo) (CLONE-NOME-UNICO): `{copia}`, criada com `forge-copia clone {copia} --branch melhoria/x "
                      "--papel dev-exemplo` e o --origem do repositório (no Forge, worktree no lugar de clone); nunca a cópia de outro agente", saida.split("## Ler", 1)[1].split("\n## ", 1)[0])

    def test_brief_de_parecer_cria_o_clone_de_revisao(self):
        """COPIA-REVISAO (A1 do review do #889): o portão parte do head remoto da branch, pelo `--revisao`, sem git clone à mão."""
        copia = self.home / ".forge-contrib" / "wt" / "x-dev-exemplo"
        for etapa in ("review", "seguranca", "qa"):
            with self.subTest(etapa):
                saida, rc, erros = self.gerar(etapa=etapa)
                self.assertEqual(rc, 0, erros)
                ler = saida.split("## Ler", 1)[1].split("\n## ", 1)[0]
                self.assertIn(f"`forge-copia clone {copia} --branch melhoria/x --papel dev-exemplo --revisao` e o --origem do repositório "
                              "(o head remoto da branch, nunca git clone à mão)", ler)
                self.assertNotIn("worktree no lugar de clone", ler)
        self.assertNotIn("--revisao", self.gerar(etapa="codigo")[0])

    def test_brief_sem_a_linha_com_caminho_fora_da_forma(self):
        os.environ["HOME"] = str(self.tmp / "com espaço")
        saida, rc, erros = self.gerar()
        self.assertEqual(rc, 0, erros)
        self.assertNotIn("CLONE-NOME-UNICO", saida)

    def test_brief_de_parecer_sem_a_linha_com_caminho_fora_da_forma(self):
        """COPIA-REVISAO (A1 da segurança do #892): o ramo de revisão também recusa o caminho fora da forma de shell."""
        os.environ["HOME"] = str(self.tmp / "com espaço")
        for etapa in ("review", "seguranca", "qa"):
            with self.subTest(etapa):
                saida, rc, erros = self.gerar(etapa=etapa)
                self.assertEqual(rc, 0, erros)
                self.assertNotIn("CLONE-NOME-UNICO", saida)
                self.assertNotIn("--revisao", saida)

    def test_brief_sem_branch_nao_sugere_copia(self):
        saida, rc, erros = self.gerar(branch=None)
        self.assertEqual(rc, 0, erros)
        self.assertNotIn("CLONE-NOME-UNICO", saida)

    def test_id_do_pedido_com_crase_nao_vai_cru_ao_brief(self):
        saida, rc, erros = self.gerar(id_="p`rm")
        self.assertEqual(rc, 0, erros)
        self.assertNotIn("p`rm", saida)
        self.assertIn(f"- comece por `forge-check proximo {self.fc.PREENCHER} --etapa E1.1`", saida)
        self.assertIn(f"- decisões: pedido {self.fc.PREENCHER} até ", saida)

    def test_id_do_pedido_com_hifen_no_inicio_nao_vira_opcao(self):
        for id_ in ("--lote", "-h"):
            with self.subTest(id_=id_):
                saida, rc, erros = self.gerar(id_=id_)
                self.assertEqual(rc, 0, erros)
                self.assertNotIn(f"proximo {id_}", saida)
                self.assertIn(f"- comece por `forge-check proximo {self.fc.PREENCHER} --etapa E1.1`", saida)


# v048 E4.1: a origem local clona do remoto dela (FORGE-COPIA-ORIGEM-LOCAL), a worktree parte da branch remota e desfaz a branch
# que criou quando falha (FORGE-COPIA-FALHA-SEM-DESFAZER) e o clone D2 nasce destacado na base (FORGE-COPIA-D2).
AUTOR = ("-c", "user.name=t", "-c", "user.email=t@t")


class Comum(Base):
    def commit(self, repo, branch, msg):
        """Commit novo em `repo`, na branch dada (criada se falta); devolve o sha."""
        self.git(repo, "switch", "-q", "-C", branch)
        self.git(repo, *AUTOR, "commit", "-q", "--allow-empty", "-m", msg)
        return self.git(repo, "rev-parse", "HEAD").stdout.strip()

    def head(self, d):
        return self.git(d, "rev-parse", "HEAD").stdout.strip()

    def tem_ref(self, repo, ref):
        return self.git(repo, "for-each-ref", ref).stdout.strip() != ""


class OrigemLocal(Comum):
    """O repositório principal não faz fetch no sandbox: a develop dele fica velha e a branch remota falta nele."""

    def setUp(self):
        super().setUp()
        self.remoto = self.fora / "remoto"
        self.git(self.fora, "clone", "-q", str(self.origem), str(self.remoto))
        self.dev_remota = self.commit(self.remoto, "develop", "nova no remoto")
        self.branch_remota = self.commit(self.remoto, "melhoria/r", "r")
        self.git(self.remoto, "switch", "-q", "develop")
        self.git(self.origem, "remote", "set-url", "origin", str(self.remoto))

    def test_pasta_local_clona_da_url_do_remoto_e_parte_da_develop_dele(self):
        d = self.pasta / "o1"
        r = self.copia("clone", str(d), "--branch", "melhoria/x", "--origem", str(self.origem))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(d), self.dev_remota)
        self.assertIn("clono do remoto origin dela", r.stderr)

    def test_branch_so_no_remoto_parte_do_head_remoto(self):
        d = self.pasta / "o2"
        r = self.copia("clone", str(d), "--branch", "melhoria/r", "--origem", str(self.origem))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(d), self.branch_remota)

    def test_url_relativa_vale_a_partir_da_origem(self):
        self.git(self.origem, "remote", "set-url", "origin", "../../../fora/remoto")
        d = self.pasta / "o3"
        r = self.copia("clone", str(d), "--branch", "melhoria/x", "--origem", str(self.origem), cwd=self.fora)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(d), self.dev_remota)

    def test_pasta_local_sem_remoto_origin_e_recusada(self):
        self.git(self.origem, "remote", "remove", "origin")
        d = self.pasta / "o4"
        r = self.copia("clone", str(d), "--branch", "melhoria/x", "--origem", str(self.origem))
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("pasta local sem remoto origin", r.stderr)
        self.assertFalse(d.exists())


class Worktree(Comum):
    def test_branch_que_ja_existe_no_remoto_parte_do_head_dela(self):
        remoto = self.commit(self.origem, "outra", "remota")
        self.git(self.origem, "switch", "-q", "develop")
        self.git(self.origem, "update-ref", "refs/remotes/origin/melhoria/w", remoto)
        d = self.pasta / "wt" / "w1"
        r = self.copia("worktree", str(d), "--branch", "melhoria/w")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(d), remoto)
        self.assertIn("já existe no remoto", r.stderr)

    def test_worktree_que_falha_apaga_a_branch_que_criou(self):
        (self.pasta / "arq").write_text("x")
        r = self.copia("worktree", str(self.pasta / "arq" / "w"), "--branch", "melhoria/w")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertFalse(self.tem_ref(self.origem, "refs/heads/melhoria/w"), "a branch criada pela worktree que falhou não fica")
        self.assertIn("apaguei a branch melhoria/w", r.stderr)

    def test_branch_que_ja_existia_fica_quando_a_worktree_falha(self):
        self.git(self.origem, "branch", "melhoria/w", "develop")
        r = self.copia("worktree", str(self.pasta / "wt" / "w2"), "--branch", "melhoria/w")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertTrue(self.tem_ref(self.origem, "refs/heads/melhoria/w"), "só a branch nova sai; a que já existia fica")

    def test_base_que_nao_existe_sai_1_com_as_refs_tentadas(self):
        r = self.copia("worktree", str(self.pasta / "wt" / "w3"), "--branch", "melhoria/w", "--base", "nada")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("nenhuma destas refs existe no clone: origin/melhoria/w, nada, origin/nada", r.stderr)
        self.assertFalse(self.tem_ref(self.origem, "refs/heads/melhoria/w"))


class D2(Comum):
    def test_clone_d2_nasce_destacado_na_develop_sem_branch(self):
        self.commit(self.origem, "main", "main")  # o clone nasce na main: a develop só existe como origin/develop
        dev = self.git(self.origem, "rev-parse", "develop").stdout.strip()
        d = self.pasta / "d2"
        r = self.copia("clone", str(d), "--origem", str(self.origem), "--d2")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(d), dev)
        self.assertEqual(self.branch_de(d), "", "o clone D2 fica destacado")
        self.assertIn(f"criei o clone D2 destacado em {dev} (de origin/develop)", r.stderr)

    def test_branch_remota_chamada_none_nao_desvia_o_d2(self):
        dev = self.git(self.origem, "rev-parse", "develop").stdout.strip()
        self.commit(self.origem, "None", "none")
        self.git(self.origem, "switch", "-q", "develop")
        d = self.pasta / "d2n"
        r = self.copia("clone", str(d), "--origem", str(self.origem), "--d2")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.head(d), dev)

    def test_d2_sem_a_base_apaga_o_clone(self):
        d = self.pasta / "d2b"
        r = self.copia("clone", str(d), "--origem", str(self.origem), "--d2", "--base", "origin/nada")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertFalse(d.exists())
        self.assertIn("não criei o clone D2: nenhuma destas refs existe no clone: origin/nada;", r.stderr)

    def test_d2_com_branch_revisao_ou_worktree_e_recusado(self):
        for extra in (["clone", "--origem", str(self.origem), "--branch", "melhoria/x"],
                      ["clone", "--origem", str(self.origem), "--revisao"], ["worktree"]):
            with self.subTest(extra=extra):
                d = self.pasta / "d2r"
                r = self.copia(extra[0], str(d), *extra[1:], "--d2")
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("--d2 é só do clone", r.stderr)
                self.assertFalse(d.exists())

    def test_d2_em_destino_ocupado_sugere_nome_unico(self):
        (self.pasta / "d2").mkdir()
        (self.pasta / "d2" / "x").write_text("x")
        r = self.copia("clone", str(self.pasta / "d2"), "--origem", str(self.origem), "--d2")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(f"use o nome único {self.pasta / 'd2-2'}", r.stderr)


if __name__ == "__main__":
    unittest.main()
