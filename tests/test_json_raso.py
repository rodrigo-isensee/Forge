"""JSON-PROFUNDO-PY314 (v0478 E44.1): o teto de aninhamento de hooks/_json_raso.py (a fonte, lida pelo estado dos hooks) e as
cópias da catraca (tests/catraca.py, que não carrega código de fora) e do bin/forge-placar (script solto) respondem igual,
caractere a caractere; bytes contam como o `json.loads` os decodifica."""
import importlib.util
import sys
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))  # a catraca importa os apoios de tests/
sys.path.insert(0, str(AQUI.parent / "hooks"))
import _json_raso  # noqa: E402


def carregar(nome, caminho):
    loader = SourceFileLoader(nome, str(caminho))
    modulo = importlib.util.module_from_spec(importlib.util.spec_from_loader(nome, loader))
    loader.exec_module(modulo)
    return modulo


catraca = carregar("catraca_json_raso", AQUI / "catraca.py")
placar = carregar("forge_placar_json_raso", AQUI.parent / "bin" / "forge-placar")
COPIAS = {"hooks/_json_raso.py": _json_raso, "tests/catraca.py": catraca, "bin/forge-placar": placar}

CASOS = (("", False), ("[]", False), ("[" * 64 + "]" * 64, False), ("[" * 65, True), ("{" * 65, True),
         ("[]" * 100, False), ('"' + "[" * 100 + '"', False), (r'"\"' + "[" * 100 + '"', False),
         (r'"\\"' + "[" * 65, True), ('{"a": ' * 64 + "1" + "}" * 64, False), ('{"a": ' * 65 + "1" + "}" * 65, True),
         ("[" * 64 + "]" + "[", False), ("{}" * 65, False), ("[" * 200000, True))


class TetoComum(unittest.TestCase):
    def test_as_copias_respondem_igual(self):
        for nome, copia in COPIAS.items():
            with self.subTest(copia=nome):
                self.assertEqual(copia.TETO_ANINHAMENTO, 64)
            for texto, esperado in CASOS:
                with self.subTest(copia=nome, texto=texto[:20], tamanho=len(texto)):
                    self.assertIs(copia.fundo_demais(texto), esperado)

    def test_bytes_contam_como_o_json_os_decodifica(self):
        """O estado dos hooks é lido em bytes: UTF-8, 16 e 32 (a detecção do `json`) contam igual ao texto; o que não decodifica
        sobe a quem chama, que já recusa o ilegível."""
        for texto, esperado in CASOS[:12]:
            for codificacao in ("utf-8", "utf-16-le", "utf-32-be"):
                with self.subTest(texto=texto[:20], codificacao=codificacao):
                    self.assertIs(_json_raso.fundo_demais(texto.encode(codificacao)), esperado)
        self.assertIs(_json_raso.fundo_demais(bytearray(b"[" * 65)), True)
        with self.assertRaises(UnicodeDecodeError):
            _json_raso.fundo_demais(b"[\xff\xfe\xfd")


if __name__ == "__main__":
    unittest.main()
