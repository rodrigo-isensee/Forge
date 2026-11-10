"""QA do L09 (E15 BRIEF-MENSAGEM-LIMPA, R-BRIEF): ponta a ponta, o `forge-check brief mensagem` real alimenta o hook
`hooks/agentes.py` real. Biblioteca padrão, sem rede."""
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from test_erros_no_brief import BRIEF, FORGE_CHECK, Base  # noqa: E402
from test_agentes_hash_brief import HOOKS, LANCADOR, PRAZO_GIT  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class MensagemAteOHook(Base):
    def setUp(self):
        super().setUp()
        self.gravar("docs/briefs/xpto-tech-lead-1.md", BRIEF.format(tipo="Tipo: codigo", extra=""))
        subprocess.run(["git", "init", "-q"], cwd=self.tmp, check=True, env=sem_manutencao(dict(os.environ, HOME=str(self.tmp))))
        (self.tmp / ".forge").mkdir(exist_ok=True)
        (self.tmp / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")
        proc = self.tmp / "proc"
        proc.mkdir()
        (proc / "loadavg").write_text("0.1 0.1 0.1\n", encoding="utf-8")
        (proc / "meminfo").write_text("MemTotal: 16777216 kB\nMemFree: 1 kB\nMemAvailable: 8388608 kB\n", encoding="utf-8")
        self.n = 0

    def mensagem(self):
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), "brief", "mensagem", "--arquivo",
                            "docs/briefs/xpto-tech-lead-1.md", "--pedido", "xpto"], capture_output=True,
                           env=dict(os.environ, HOME=str(self.tmp / "home")))
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.decode()

    def hook(self, prompt):
        self.n += 1
        entrada = {"hook_event_name": "PreToolUse", "tool_name": "Agent", "session_id": "s", "cwd": str(self.tmp),
                   "tool_input": {"subagent_type": "forge:conferente", "description": f"q{self.n}", "prompt": prompt}}
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_")) and k != "CLAUDE_PROJECT_DIR"}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, FORGE_PROC=str(self.tmp / "proc"), FORGE_NPROC="8",
                   HOME=str(self.tmp / "home"))
        return subprocess.run([sys.executable, "-c", LANCADOR, str(HOOKS), str(HOOKS / "agentes.py"), PRAZO_GIT],
                              input=json.dumps(entrada), cwd=self.tmp, env=sem_manutencao(env), capture_output=True,
                              text=True, timeout=120)

    def test_mensagem_real_passa_no_hook_e_traz_hash_e_bytes_do_arquivo(self):  # E15: o caminho feliz de ponta a ponta
        msg = self.mensagem()
        self.assertEqual(msg.splitlines()[0], "modo: brief")
        self.assertRegex(msg, r"(?m)^Brief-sha256: [0-9a-f]{64}   Bytes: \d+$")
        self.assertNotIn("<<<BRIEF", msg)
        r = self.hook(msg)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_lembrete_antes_do_modo_hash_ausente_ou_adulterado_sao_recusados(self):  # E15: a forma que o hook cobra
        msg = self.mensagem()
        sem_hash = "\n".join(l for l in msg.splitlines() if not l.startswith("Brief-sha256:")) + "\n"
        adulterado = re.sub(r"[0-9a-f]{64}", "0" * 64, msg, count=1)
        for nome, prompt in (("lembrete antes", "jarvis-recorrente: forma em 2 briefs\n" + msg), ("sem hash", sem_hash),
                             ("hash errado", adulterado)):
            with self.subTest(nome):
                r = self.hook(prompt)
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn("R-BRIEF", r.stderr)

    def test_dois_blocos_sem_separador_sao_recusados_pelo_hook_e_a_regra_do_conferente_diz_como(self):  # E15: fronteira hook x agente
        msg = self.mensagem()
        r = self.hook(msg + "modo: entrega\nArquivo: /x/docs/briefs/q.md\n")  # a forma curta não tem `<<<BRIEF`: 2 `Arquivo:` no cabeçalho
        self.assertEqual(r.returncode, 2, r.stderr)
        regra = (Path(__file__).resolve().parent.parent / "agents" / "conferente.md").read_text(encoding="utf-8")
        self.assertIn("Uma mensagem, um bloco: brief e entrega vão em mensagens separadas.", regra)
        self.assertIn("hash diferente de `Brief-sha256:` é `forma: brief diferente do arquivo`", regra)


class TextoDaSkill(unittest.TestCase):  # UM-BRIEF (versao-075 UN-1, adendo 7): o mapa leva skills/ a este módulo
    def test_skill_manda_uma_mensagem_por_brief(self):
        texto = (Path(__file__).resolve().parent.parent / "skills/briefs-e-conferencia/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("com a mensagem de `forge-check brief mensagem`", texto)
        self.assertNotIn("`--arquivo a b`", texto)


if __name__ == "__main__":
    unittest.main()
