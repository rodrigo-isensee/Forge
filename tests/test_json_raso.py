"""JSON-PROFUNDO-PY314 (v0478 E44.1): o teto de aninhamento de hooks/_json_raso.py, a fonte única dos leitores de controle
(estado dos hooks e catraca), e a cópia do bin/forge-placar respondem igual, caractere a caractere; bytes contam como o
`json.loads` os decodifica."""
import sys
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "hooks"))
import _json_raso  # noqa: E402

placar = SourceFileLoader("forge_placar_json_raso", str(RAIZ / "bin" / "forge-placar")).load_module()

CASOS = (("", False), ("[]", False), ("[" * 64 + "]" * 64, False), ("[" * 65, True), ("{" * 65, True),
         ("[]" * 100, False), ('"' + "[" * 100 + '"', False), (r'"\"' + "[" * 100 + '"', False),
         (r'"\\"' + "[" * 65, True), ('{"a": ' * 64 + "1" + "}" * 64, False), ('{"a": ' * 65 + "1" + "}" * 65, True),
         ("[" * 64 + "]" + "[", False), ("[" * 200000, True))


class TetoComum(unittest.TestCase):
    def test_as_duas_copias_respondem_igual(self):
        self.assertEqual(_json_raso.TETO_ANINHAMENTO, placar.TETO_ANINHAMENTO)
        self.assertEqual(_json_raso.TETO_ANINHAMENTO, 64)
        for texto, esperado in CASOS:
            with self.subTest(texto=texto[:20], tamanho=len(texto)):
                self.assertIs(_json_raso.fundo_demais(texto), esperado)
                self.assertIs(placar.fundo_demais(texto), esperado)

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
