"""Item 62 (OK-1): o doutor avisa, só pela presença do nome, que a sessão pode cobrar por token (R-CUSTO).

Arquivo próprio do item, para o commit dele se reverter sozinho. Usa a `Base` do `test_doutor` (HOME, git e `gh` falsos, sem rede).
"""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_doutor as td  # noqa: E402
from ambiente_git import SINAIS_DE_CUSTO  # noqa: E402

HOOK = td.HOOK


class Custo(td.Base):
    """Item 62 (OK-1): o doutor avisa, só pela presença do nome, que a sessão pode cobrar por token (R-CUSTO). Nunca mostra o valor."""
    MARCADOR = "MARCADOR-X9"

    def todas_as_saidas(self, r):
        """stdout, stderr, o cache do hook e o erros.log: tudo o que poderia carregar um valor."""
        partes = [r.stdout, r.stderr]
        for arq in (self.proj / ".forge/run").glob("*"):
            if arq.is_file():
                partes.append(arq.read_text(encoding="utf-8", errors="replace"))
        return "\n".join(partes)

    def test_nome_do_login_por_token_no_ambiente_avisa_sem_mostrar_o_valor(self):
        for nome in SINAIS_DE_CUSTO:
            with self.subTest(nome=nome):
                r = self.doutor("--rapido", env={**self.env, nome: self.MARCADOR})
                self.assertEqual(r.returncode, 1)
                self.assertIn("R-CUSTO", r.stdout)
                self.assertIn(nome, r.stdout)
                self.assertNotIn(self.MARCADOR, self.todas_as_saidas(r))

    def test_variavel_vazia_ou_so_espaco_conta_como_ausente(self):
        for valor in ("", "   "):
            r = self.doutor("--rapido", env={**self.env, "ANTHROPIC_AUTH_TOKEN": valor})
            self.assertEqual((r.returncode, r.stdout), (0, ""), repr(valor))

    def test_api_key_helper_no_settings_do_usuario_avisa_e_nao_e_executado(self):
        sentinela = self.tmp / "sentinela"
        (self.bin / "ajudante").write_text(f"#!/bin/sh\ntouch {sentinela}\n", encoding="utf-8")
        (self.bin / "ajudante").chmod(0o755)
        self.escrever_home(".claude/settings.json", json.dumps({"sandbox": {"enabled": True}, "apiKeyHelper": str(self.bin / "ajudante")}))
        r = self.doutor("--rapido")
        self.assertEqual(r.returncode, 1)
        self.assertIn("apiKeyHelper", r.stdout)
        self.assertNotIn("ajudante", r.stdout)
        self.assertFalse(sentinela.exists())

    def test_api_key_helper_vazio_conta_como_ausente(self):
        self.escrever_home(".claude/settings.json", json.dumps({"sandbox": {"enabled": True}, "apiKeyHelper": ""}))
        r = self.doutor("--rapido")
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_nome_no_bloco_env_do_settings_do_projeto_avisa_sem_mostrar_o_valor(self):
        self.escrever(".claude/settings.json", json.dumps({"agent": "forge:jarvis", "enabledPlugins": {"forge@forge": True},
                                                          "env": {"CLAUDE_CODE_USE_VERTEX": self.MARCADOR}}))
        r = self.doutor("--rapido")
        self.assertEqual(r.returncode, 1)
        self.assertIn("CLAUDE_CODE_USE_VERTEX", r.stdout)
        self.assertNotIn(self.MARCADOR, self.todas_as_saidas(r))

    def test_nome_no_settings_local_do_projeto_avisa(self):
        self.escrever(".claude/settings.local.json", json.dumps({"env": {"ANTHROPIC_AUTH_TOKEN": self.MARCADOR}}))
        r = self.doutor("--rapido")
        self.assertIn("ANTHROPIC_AUTH_TOKEN", r.stdout)
        self.assertNotIn(self.MARCADOR, r.stdout)

    def test_settings_com_formato_estranho_nao_derruba_e_as_outras_fontes_ainda_valem(self):
        self.escrever(".claude/settings.local.json", "{ truncado")
        self.escrever(".claude/settings.json", json.dumps({"agent": "forge:jarvis", "enabledPlugins": {"forge@forge": True}, "env": [1]}))
        for valor in ("[]", "null", '{"env": 3, "apiKeyHelper": null}', '{"env": null}'):
            self.escrever(".claude/settings.local.json", valor)
            r = self.doutor("--rapido")
            self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""), valor)
        self.escrever(".claude/settings.local.json", "{ truncado")
        r = self.doutor("--rapido", env={**self.env, "CLAUDE_CODE_USE_BEDROCK": "1"})
        self.assertIn("CLAUDE_CODE_USE_BEDROCK", r.stdout)

    def test_settings_gigante_ou_que_nao_e_arquivo_regular_e_ignorado_no_prazo(self):
        grande = '{"apiKeyHelper": "x", "lixo": "' + "a" * (5 * 1024 * 1024) + '"}'
        self.escrever(".claude/settings.local.json", grande)
        r = self.doutor("--rapido")
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        alvo = self.proj / ".claude/settings.local.json"
        alvo.unlink()
        os.mkfifo(alvo)  # um pipe sem escritor: ler travaria para sempre
        r = self.doutor("--rapido")
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_sem_nenhum_dos_nomes_fica_em_silencio(self):
        r = self.doutor("--rapido")
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_o_aviso_diz_que_pode_cobrar_e_nunca_afirma(self):
        r = self.doutor("--rapido", env={**self.env, "ANTHROPIC_AUTH_TOKEN": "x"})
        self.assertIn("pode estar cobrando", r.stdout)

    def test_o_hook_do_inicio_da_sessao_grava_o_problema_no_cache_sem_o_valor(self):
        env = {**self.env, "CLAUDE_CODE_USE_VERTEX": self.MARCADOR}
        entrada = {"hook_event_name": "SessionStart", "session_id": "s1", "cwd": str(self.proj)}
        r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(entrada), env=env, cwd=self.proj,
                           capture_output=True, text=True, timeout=30)
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        cache = (self.proj / ".forge/run/doutor").read_text(encoding="utf-8")
        self.assertIn("CLAUDE_CODE_USE_VERTEX", cache)
        self.assertNotIn(self.MARCADOR, cache)
        erros = self.proj / ".forge/run/erros.log"
        self.assertNotIn(self.MARCADOR, erros.read_text(encoding="utf-8") if erros.exists() else "")


if __name__ == "__main__":
    unittest.main()
