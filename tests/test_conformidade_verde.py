"""S8 (versao-037 E7): o hook `conformidade` barra escrita na prova da suíte (`.verde`, `.dirigida`, `.novo`) e deixa a leitura
(casos de abuso e corpus de legítimos de docs/security/ameacas/versao-037.md, E7). Pastas temporárias só deste teste."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

RAIZ = Path(__file__).resolve().parent.parent


class ProvaDaSuite(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="forge-s8-")))
        self.proj, self.d, self.verde = self.tmp / "proj", self.tmp / "forge-1000", self.tmp / "forge-1000/forge-suite-1000.verde"
        (self.proj / ".forge").mkdir(parents=True)
        (self.proj / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        self.d.mkdir()
        (self.tmp / "s").symlink_to(self.verde)  # link simbólico para a prova (C-2, nome resolvido)
        subprocess.run(["git", "init", "-q", str(self.proj)], check=True, env=sem_manutencao(self.env()))

    def env(self, **extra):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_")) and k != "CLAUDE_PROJECT_DIR"}
        return {**env, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "XDG_RUNTIME_DIR": str(self.d), **extra}

    def rodar(self, ferramenta, entrada, papel="forge:node-backend", **extra):
        dados = {"tool_name": ferramenta, "tool_input": entrada, "hook_event_name": "PreToolUse", "agent_type": papel}
        return subprocess.run([sys.executable, str(RAIZ / "hooks" / "conformidade.py")], input=json.dumps(dados),
                              cwd=self.proj, env=self.env(**extra), capture_output=True, text=True, timeout=120)

    def recusa(self, r, caso):
        self.assertEqual(r.returncode, 2, f"{caso}: {r.stderr}")
        self.assertRegex(r.stderr, "R-VERIFY.*só é gravada pelo pre-push.*pre-push --suite", caso)
        self.assertNotIn("--no-verify", r.stderr, caso)

    def test_escrita_na_prova_recusa(self):
        v, d = str(self.verde), str(self.d)
        for papel in ("forge:node-backend", "forge:tech-lead", "forge:qa-engineer", None):
            self.recusa(self.rodar("Write", {"file_path": v, "content": "x"}, papel), f"Write ({papel})")
        self.recusa(self.rodar("Write", {"file_path": v, "content": "x"}, None, CLAUDE_PROJECT_DIR=str(RAIZ)), "sessão")
        self.recusa(self.rodar("Edit", {"file_path": f"{v}.novo", "old_string": "a", "new_string": "b"}), "Edit")
        self.recusa(self.rodar("Write", {"file_path": str(self.tmp / "s"), "content": "x"}), "Write por link")
        (self.d / "forge-suite-1000.dirigida").symlink_to(self.tmp / "outro")  # C-2: o nome literal, não só o resolvido
        self.recusa(self.rodar("Write", {"file_path": f"{d}/forge-suite-1000.dirigida", "content": "x"}), "nome literal")
        for c in ('printf x >> "$XDG_RUNTIME_DIR/forge-suite-1000.verde"', f"echo x >> {self.tmp}/s",
                  'echo x > "/tmp/forge-$(id -u)/forge-suite-$(id -u).verde"', f"echo x > {d}/forge-suite-*.verde",
                  f"cp a {d}/forge-suite-1000.dirigida", f"mv x {v}.novo", f"tee -a {v}", f"dd if=/dev/zero of={v}",
                  f"sed -i s/a/b/ {v}", f"ln {v} /tmp/h", f"ln -s {v} /tmp/h2", f"cp -l {v} /tmp/h", f"rm -f {v}",
                  f"python3 -c \"open('{v}','a').write('x')\"", f"python3 - <<'FIM'\nopen('{v}', 'w')\nFIM",
                  f"TMPDIR=/tmp/x bash -c 'echo y > /tmp/x/forge-1000/forge-suite-1000.verde'"):
            self.recusa(self.rodar("Bash", {"command": c}), c)
        (self.proj / ".forge" / "perfil").write_text("iniciante\n", encoding="utf-8")
        self.recusa(self.rodar("Write", {"file_path": str(self.verde), "content": "x"}), "iniciante")

    def test_leitura_trava_e_fila_passam(self):
        v, d = str(self.verde), str(self.d)
        for c in (f"cat {v}", f"tail -n 3 {v}", f"grep -c . {v}", f"wc -l {v}", f"ls -l {d}/", f"stat {v}",
                  f"cp {v} {self.tmp}/copia", f"python3 -c \"print(open('{v}').read())\"",
                  f"cat > docs-x.md <<'FIM'\ncite {v}\nFIM", f"echo x > {d}/forge-suite-1000.lock",
                  f"touch {d}/forge-suite-1000.fila/.nova-5 {d}/forge-suite-1000.fila/1-5", f"rm -f {d}/forge-suite-1000.lock",
                  f"echo x > {d}/forge-suite-1000.verde.lock"):
            r = self.rodar("Bash", {"command": c})
            self.assertEqual(r.returncode, 0, f"{c}: {r.stderr}")
        r = self.rodar("Write", {"file_path": str(self.proj / "tests" / "test_x.py"), "content": f"# {v}\n"})
        self.assertEqual(r.returncode, 0, r.stderr)
