"""M7: o doutor avisa quando a sessão roda uma versão do Forge menor que a instalada (só aviso), sem mandar `claude plugin update`."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_atualizar import ATUALIZAR, Base as BaseAtualizar  # noqa: E402
from test_doutor import Base, VERSAO  # noqa: E402

AVISO = "está instalado, mas esta sessão roda a"


class SessaoDefasada(Base):
    def carregar(self, versao):
        pasta = self.tmp / "carregada"
        (pasta / ".claude-plugin").mkdir(parents=True)
        (pasta / ".claude-plugin" / "plugin.json").write_text(json.dumps({"version": versao}), encoding="utf-8")
        self.env["CLAUDE_PLUGIN_ROOT"] = str(pasta)

    def instalar(self, versao):
        self.escrever_home(".claude/plugins/installed_plugins.json",
                           json.dumps({"version": 2, "plugins": {"forge@forge": [{"scope": "user", "version": versao}]}}))

    def test_instalada_maior_que_a_carregada_avisa_para_reabrir(self):
        self.carregar("0.0.1")
        self.instalar(VERSAO)
        r = self.doutor("--rapido")
        self.assertEqual(r.returncode, 1)
        self.assertIn(f"O Forge {VERSAO} {AVISO} 0.0.1: feche e abra a sessão", r.stdout)
        self.assertNotIn("claude plugin update", r.stdout)

    def test_sessao_em_dia_fica_em_silencio(self):
        self.carregar(VERSAO)
        self.instalar(VERSAO)
        r = self.doutor("--rapido")
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_instalada_menor_ou_formato_estranho_nao_avisa(self):
        self.carregar(VERSAO)
        self.instalar("0.0.1")
        self.assertNotIn(AVISO, self.doutor("--rapido").stdout)
        self.escrever_home(".claude/plugins/installed_plugins.json", json.dumps({"plugins": {"forge@forge": "lixo"}}))
        self.assertNotIn(AVISO, self.doutor("--rapido").stdout)

    def test_plugin_realmente_desatualizado_ainda_manda_atualizar(self):
        self.carregar("0.0.1")
        self.instalar("0.0.1")
        self.escrever(".forge/versao", VERSAO + "\n")
        r = self.doutor("--rapido")
        self.assertIn("claude plugin update", r.stdout)
        self.assertNotIn(AVISO, r.stdout)


class SaidaDoAtualizar(BaseAtualizar):
    def test_caminho_feliz_cita_o_comando_para_voltar_e_o_aviso_da_sessao(self):
        self.publicar("9.9.0")
        codigo, saida = self.rodar(ATUALIZAR, respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        self.assertIn("Para voltar: forge voltar-versao", saida)
        self.assertIn("esta sessão roda a", saida)


if __name__ == "__main__":
    unittest.main()
