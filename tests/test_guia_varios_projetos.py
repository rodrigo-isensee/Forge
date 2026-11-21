"""MP9 (v0478 E24.1, diretriz 35): o guia "vários projetos" no README e no modelo de projeto traz cada parte do desenho
(uma janela por projeto no modo auto, teto em partes iguais com `peso` opcional, escape da trava de memória só com um projeto,
um bot de Telegram com o nome do projeto, `forge-status --maquina`) e o comando de `peso` pronto para colar."""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TITULO = "## Vários projetos na mesma máquina"
COMANDO_PESO = "jq '.peso = 2' .forge/config.json > .forge/config.novo && mv .forge/config.novo .forge/config.json"
PARTES = ("--permission-mode auto", "partes iguais", COMANDO_PESO, "FORGE_CARGA_LIVRE=1", "só vale com um projeto ativo",
          "[<projeto>]", "forge-status --maquina")


def secao(texto, titulo):
    """O trecho do README do título até o próximo `## `; vazio se o título não existe."""
    m = re.search(rf"^{re.escape(titulo)}\n(.*?)(?=^## |\Z)", texto, re.S | re.M)
    return m.group(1) if m else ""


class GuiaVariosProjetos(unittest.TestCase):
    def test_readme_tem_a_secao_com_cada_parte(self):
        trecho = secao((RAIZ / "README.md").read_text(encoding="utf-8"), TITULO)
        self.assertGreater(len(trecho), 200, f"README sem a seção {TITULO!r}")
        for parte in PARTES + ("Projeto: <nome>", "uma janela por projeto"):
            with self.subTest(parte=parte):
                self.assertIn(parte.lower(), trecho.lower())

    def test_modelo_de_projeto_traz_o_resumo_e_aponta_o_guia(self):
        modelo = (RAIZ / "templates" / "projeto" / "CLAUDE.md").read_text(encoding="utf-8")
        trecho = secao(modelo, "## Sessão")
        for parte in PARTES + (TITULO.removeprefix("## "),):
            with self.subTest(parte=parte):
                self.assertIn(parte, trecho)

    def test_peso_do_guia_cabe_na_faixa_do_hook(self):
        """O valor do exemplo vale no hook: fora da faixa o `peso` volta a 1 e o comando não faria nada."""
        import importlib.util
        import sys
        sys.path.insert(0, str(RAIZ / "hooks"))
        try:
            import agentes  # noqa: F401  o mapa do forge-testes liga hooks/agentes.py a quem o importa
            spec = importlib.util.spec_from_file_location("agentes_mp9", RAIZ / "hooks" / "agentes.py")
            agentes = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(agentes)
        finally:
            sys.path.remove(str(RAIZ / "hooks"))
        self.assertEqual(agentes.peso_valido(2), 2)
        self.assertEqual(agentes.PESO_MAXIMO, 10, "o guia diz 'até 10': atualize o README e o modelo junto")

    def test_secao_ausente_e_acusada(self):
        self.assertEqual(secao("# x\n## Outra\ntexto\n", TITULO), "")


if __name__ == "__main__":
    unittest.main()
