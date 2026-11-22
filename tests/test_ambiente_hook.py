"""E2.54, ordem do dono: o hook `ambiente` (SessionStart) confere o ambiente do container ao abrir e põe as linhas `falta:` no contexto.

Sem rede: `gh` falso, HOME descartável e FORGE_PERSISTENTE apontando para uma pasta do teste (o "/workspaces" do container).
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / "hooks" / "ambiente.py"


def git(cwd, *args):
    env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
    return subprocess.run(["git", "-C", str(cwd), *args], env=env, capture_output=True, text=True, check=True)


class AmbienteNoSessionStart(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.persist, self.home, self.bin = self.tmp / "workspaces", self.tmp / "home", self.tmp / "bin"
        for d in (self.persist, self.home, self.bin):
            d.mkdir()
        self.marcas = self.tmp / "marcas"
        self.marcas.mkdir()
        self.forge = self.persist / "Forge"
        (self.forge / ".claude-plugin").mkdir(parents=True)
        (self.forge / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "forge"}))
        git(self.forge, "init", "-q")
        self.proj = self.persist / "proj"
        (self.proj / ".forge").mkdir(parents=True)
        (self.proj / ".forge" / "versao").write_text("0.0.0\n")
        (self.proj / ".devcontainer").mkdir()
        (self.proj / ".devcontainer" / "devcontainer.json").write_text("{}")
        git(self.proj, "init", "-q")
        self.gh_ok(False)

    def gh_ok(self, logado):
        gh = self.bin / "gh"
        gh.write_text(f"#!/bin/sh\nexit {0 if logado else 1}\n")
        gh.chmod(0o755)

    def ambiente_em_ordem(self, raiz):
        """Link da área, login e core.hooksPath no lugar."""
        real = self.persist / ".forge-contrib"
        real.mkdir(exist_ok=True)
        if not (self.home / ".forge-contrib").is_symlink():
            (self.home / ".forge-contrib").symlink_to(real)
        git(raiz, "config", "core.hooksPath", ".githooks")
        self.gh_ok(True)
        claude = self.home / ".local/bin/claude"  # E119.1: o Claude Code atual mora em ~/.local/bin
        claude.parent.mkdir(parents=True, exist_ok=True)
        claude.write_text("#!/bin/sh\nexit 0\n")
        claude.chmod(0o755)

    def rodar(self, cwd, evento="SessionStart", persistente=None, hook=HOOK):
        env = {**os.environ, "HOME": str(self.home), "PATH": f"{self.bin}:{os.environ['PATH']}",
               "FORGE_PERSISTENTE": str(persistente or self.persist)}
        r = subprocess.run(["python3", "-s", "-E", str(hook)], input=json.dumps({"hook_event_name": evento, "cwd": str(cwd)}),
                           env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        return r.stdout

    def test_forge_faltando_poe_as_linhas_falta_com_o_comando_exato_no_contexto(self):
        saida = self.rodar(self.forge)
        preparo = f"bash {self.forge}/scripts/preparar-estacao.sh --container"
        self.assertTrue(saida.startswith("Forge, ambiente do container incompleto"), saida)
        self.assertIn("Jarvis: dê ao dono, na 1ª mensagem, o comando exato", saida)
        self.assertIn("falta: gh sem login", saida)
        self.assertIn(f"falta: link {self.home}/.forge-contrib -> {self.persist}/.forge-contrib ausente ou sem destino: rode {preparo}", saida)
        self.assertIn(f"falta: core.hooksPath de {self.forge} não é .githooks: rode {preparo}", saida)

    def test_projeto_com_devcontainer_usa_o_verificar_do_modelo(self):
        saida = self.rodar(self.proj)
        self.assertIn(f"falta: core.hooksPath de {self.proj} não é .githooks: rode bash {self.proj}/.devcontainer/preparar-ambiente.sh", saida)

    def test_ambiente_em_ordem_fica_em_silencio(self):
        for raiz in (self.forge, self.proj):
            with self.subTest(raiz=raiz.name):
                self.ambiente_em_ordem(raiz)
                self.assertEqual(self.rodar(raiz), "")

    def test_so_o_sessionstart_dentro_do_container_e_com_devcontainer(self):
        self.assertEqual(self.rodar(self.forge, evento="Stop"), "")
        self.assertEqual(self.rodar(self.forge, persistente=self.tmp / "outro"), "", "fora do container")
        (self.proj / ".devcontainer" / "devcontainer.json").unlink()
        self.assertEqual(self.rodar(self.proj), "", "projeto sem devcontainer não adotou o preparo")

    def test_nunca_roda_o_script_do_work_tree(self):
        """R-SEGURANCA (B2 da 0.43.1): o hook roda como o usuário, fora do sandbox; o script vem do plugin, não do que o agente edita."""
        for raiz, script in ((self.forge, "scripts/preparar-estacao.sh"), (self.proj, ".devcontainer/preparar-ambiente.sh")):
            (raiz / script).parent.mkdir(parents=True, exist_ok=True)
            (raiz / script).write_text(f'#!/bin/bash\necho x > "{self.marcas}/{raiz.name}"\necho "falta: forjado"\nexit 1\n')
            saida = self.rodar(raiz)
            self.assertNotIn("forjado", saida)
            self.assertIn("falta: ", saida)
        self.assertEqual(list(self.marcas.iterdir()), [])

    def bash_falso(self, saida, rc):
        """`bash` falso no PATH: marca que rodou, imprime `saida` e sai com `rc` (o hook chama `bash` pelo PATH)."""
        bash = self.bin / "bash"
        bash.write_text(f'#!/bin/sh\necho x > "{self.marcas}/bash"\nprintf \'%s\\n\' {saida}\nexit {rc}\n')
        bash.chmod(0o755)

    def test_so_as_linhas_falta_entram_no_contexto(self):
        self.bash_falso("ruido 'falta: a' ' falta: b'", 1)
        self.assertEqual(self.rodar(self.forge).splitlines()[1:], ["falta: a"])

    def test_verificar_sem_o_codigo_1_fica_em_silencio(self):
        for rc in (0, 2, 127):
            with self.subTest(rc=rc):
                self.bash_falso("'falta: a'", rc)
                self.assertEqual(self.rodar(self.forge), "")

    def test_script_ausente_no_plugin_fica_em_silencio_sem_rodar_bash(self):
        plugin = self.tmp / "plugin" / "hooks"
        plugin.mkdir(parents=True)
        for nome in ("ambiente.py", "_comum.py"):
            (plugin / nome).write_bytes((HOOK.parent / nome).read_bytes())
        self.bash_falso("'falta: a'", 1)
        self.assertEqual(self.rodar(self.forge, hook=plugin / "ambiente.py"), "")
        self.assertEqual(list(self.marcas.iterdir()), [])

    def test_hooks_json_registra_o_ambiente_no_sessionstart(self):
        d = json.loads((RAIZ / "hooks/hooks.json").read_text(encoding="utf-8"))
        comandos = [h["args"][-1].rsplit("/", 1)[-1] for g in d["hooks"]["SessionStart"] for h in g["hooks"]]
        self.assertIn("ambiente.py", comandos)
        self.assertNotIn("ambiente.py", [h["args"][-1].rsplit("/", 1)[-1] for g in d["hooks"]["Stop"] for h in g["hooks"]])


if __name__ == "__main__":
    unittest.main()
