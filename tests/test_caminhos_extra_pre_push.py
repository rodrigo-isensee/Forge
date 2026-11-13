"""0.45.6 (review v0454, A2): as mesmas entradas em `_comum.caminhos_extra` e na conferência do `.githooks/pre-push` do modelo
de projeto (só leitura) dão as mesmas pastas aceitas e a mesma quantidade de avisos; as duas cópias da regra não se afastam."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PRE_PUSH = RAIZ / "templates" / "projeto" / ".githooks" / "pre-push"
INICIO, FIM = "python3 -I -c '", "' \"$cfg\")\""


def conferencia_do_modelo():
    texto = PRE_PUSH.read_text(encoding="utf-8")
    inicio = texto.index(INICIO) + len(INICIO)
    return texto[inicio:texto.index(FIM, inicio)]


def comum():
    if str(RAIZ / "hooks") not in sys.path:
        sys.path.insert(0, str(RAIZ / "hooks"))
    import _comum
    return _comum


class CaminhosExtraIgualAoPrePush(unittest.TestCase):
    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp(prefix="forge-ce-")).resolve()
        self.addCleanup(shutil.rmtree, self.raiz, ignore_errors=True)
        (self.raiz / ".forge").mkdir()
        self.real = self.raiz / "real"
        self.real.mkdir()
        (self.raiz / "link").symlink_to(self.real)
        (self.raiz / "arquivo").write_text("x", encoding="utf-8")
        self.cfg = self.raiz / ".forge" / "config.json"

    def no_modelo(self):
        p = subprocess.run([sys.executable, "-I", "-c", conferencia_do_modelo(), str(self.cfg)],
                           capture_output=True, text=True, env={}, check=True)
        return [x for x in p.stdout.strip().split(":") if x], len(p.stderr.splitlines())

    def confere(self, texto):
        self.cfg.write_text(texto, encoding="utf-8")
        pastas, avisos = comum().caminhos_extra(self.raiz)
        modelo_pastas, modelo_avisos = self.no_modelo()
        self.assertEqual(pastas, modelo_pastas, texto)
        self.assertEqual(len(avisos), modelo_avisos, texto)
        return pastas

    def test_a_conferencia_do_modelo_foi_achada(self):
        self.assertIn("realpath", conferencia_do_modelo())

    def test_entradas_boas_e_ruins_dao_as_mesmas_pastas(self):
        r = str(self.real)
        casos = {
            "boa": [r],
            "barra_final": [r + "/"],
            "relativa": ["real"],
            "com_dois_pontos": [r + ":/usr/bin"],
            "com_ponto_ponto": [str(self.real / ".." / "real")],
            "com_ponto": [str(self.real / ".")],
            "por_link": [str(self.raiz / "link")],
            "inexistente": [str(self.raiz / "nao-existe")],
            "arquivo": [str(self.raiz / "arquivo")],
            "controle": [r + "\n"],
            "nao_texto": [1, None, ["x"]],
            "mistura": ["real", r, str(self.raiz / "link"), r + "/"],
            "vazia": [],
            "chave_sem_lista": r,
            "chave_nula": None,
        }
        for nome, valor in casos.items():
            with self.subTest(nome):
                import json
                self.confere(json.dumps({"caminhos_extra": valor}))
        self.assertEqual(self.confere('{"caminhos_extra": ["%s"]}' % r), [r])

    def test_config_ilegivel_ou_sem_objeto_da_o_mesmo_resultado(self):
        for texto in ("{", "[]", "[1]", '"x"', "{}"):
            with self.subTest(texto):
                self.confere(texto)


if __name__ == "__main__":
    unittest.main()
