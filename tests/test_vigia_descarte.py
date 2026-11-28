"""HOOK-PARADA-CONTA-REDIRECAO (v048 E12.3): o `contorno` do vigia não conta a redireção de descritor para /dev/null
(`2>/dev/null`) como escrita nem como alvo, e segue acusando a escrita no alvo barrado com ela no fim do comando.
O fixture `tests/hooks/vigia/descarte-dev-null-nao-conta.json` cobre o hook de ponta a ponta."""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "hooks"))
import vigia  # noqa: E402

R = "/r"


def uso(nome, entrada, regra=None):
    perfil = {"nome": nome, **vigia.perfil_da_chamada(nome, entrada, R)}
    return {**perfil, "regra": regra} if regra else perfil


def bash(comando, regra=None):
    return uso("Bash", {"command": comando}, regra)


WRITE_BARRADO = uso("Write", {"file_path": "/r/.git/config"}, "R-CONFORMIDADE")


class DescarteNaoConta(unittest.TestCase):
    def test_ler_o_alvo_barrado_com_2_dev_null_nao_e_contorno(self):
        for comando in ("cat .git/config 2>/dev/null", "cat .git/config 2> /dev/null", "cat .git/config >/dev/null",
                        "cat .git/config &>/dev/null", "cat .git/config 2>>/dev/null; true", "(cat .git/config 2>/dev/null)"):
            with self.subTest(comando=comando):
                self.assertFalse(vigia.eh_contorno(bash(comando), WRITE_BARRADO))

    def test_dev_null_nao_e_alvo_comum_entre_duas_chamadas(self):
        barrado = bash("cp a docs/x.md 2>/dev/null", "R-CONFORMIDADE")
        for comando in ("python3 tools/y.py 2>/dev/null", "python3 tools/y.py 2> /dev/null"):
            with self.subTest(comando=comando):
                self.assertEqual(vigia.perfil_da_chamada("Bash", {"command": comando}, R)["alvo"], ["/r/tools/y.py"])
                self.assertFalse(vigia.eh_contorno(bash(comando), barrado))


class EscritaNoAlvoSegueContando(unittest.TestCase):
    def test_escrita_no_alvo_barrado_com_2_dev_null_no_fim_e_contorno(self):
        for comando in ("cp a .git/config 2>/dev/null", "echo x > .git/config 2>/dev/null",
                        "tee .git/config </dev/null >/dev/null"):
            with self.subTest(comando=comando):
                self.assertTrue(vigia.eh_contorno(bash(comando), WRITE_BARRADO))

    def test_dev_null_colado_a_outra_grafia_segue_contando_como_escrita(self):
        for comando in ("echo x >/dev/null'.git/config'", "echo x >/dev/null.git/config .git/config"):
            with self.subTest(comando=comando):
                self.assertIn(">", vigia.perfil_da_chamada("Bash", {"command": comando}, R)["verbos"])

    def test_redirecao_colada_a_palavra_anterior_fica(self):
        self.assertIn(">", vigia.perfil_da_chamada("Bash", {"command": "cat .git/config x>/dev/null"}, R)["verbos"])


if __name__ == "__main__":
    unittest.main()
