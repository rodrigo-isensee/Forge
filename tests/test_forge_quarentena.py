"""BP1 Q1: o formato e o leitor puro da quarentena (`bin/forge_quarentena.py`). A data é sempre injetada: nenhum teste lê o relógio."""
import datetime
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "bin"))
import forge_quarentena as q  # noqa: E402

D = datetime.date


def entrada(nome="tests.test_a.A.test_x", **mudar):
    e = {"teste": nome, "classe": "carga", "cartao": "FLAKY-1", "prova": "local:3/20", "desde": "2026-11-20",
         "prazo": "2026-11-27", "autorizacao": "A-10"}
    e.update(mudar)
    return e


class Carregar(unittest.TestCase):
    def ler(self, texto):
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "q.json"
            if texto is not None:
                arq.write_text(texto, encoding="utf-8")
            return q.carregar(arq)

    def test_o_arquivo_do_repositorio_nasce_vazio(self):
        self.assertEqual(q.carregar(RAIZ / "tests" / "quarentena.json"), ([], []))

    def test_le_as_entradas(self):
        self.assertEqual(self.ler(json.dumps({"entradas": [entrada()]})), ([entrada()], []))

    def test_ausente_ilegivel_e_fora_do_formato_nao_deixam_entrada(self):
        for texto in (None, "{", "[]", '{"entradas": 1}', '{"entradas": [1]}'):
            with self.subTest(texto=texto):
                entradas, erros = self.ler(texto)
                self.assertEqual(entradas, [])
                self.assertEqual(len(erros), 1)

    def test_chave_repetida_em_qualquer_nivel_nao_deixa_entrada(self):
        base = json.dumps({"entradas": [entrada()]})
        repetida_na_entrada = base.replace('"autorizacao": "A-10"', '"autorizacao": "A-10", "autorizacao": "A-99"')
        repetida_no_topo = base[:-1] + ', "entradas": []}'
        for texto in (repetida_na_entrada, repetida_no_topo):
            with self.subTest(texto=texto):
                entradas, erros = self.ler(texto)
                self.assertEqual(entradas, [])
                self.assertTrue(any("chave repetida" in m for m in erros))

    def test_link_simbolico_nao_e_seguido(self):
        with tempfile.TemporaryDirectory() as d:
            alvo, link = Path(d) / "outro.json", Path(d) / "q.json"
            alvo.write_text(json.dumps({"entradas": [entrada()]}), encoding="utf-8")
            link.symlink_to(alvo)
            self.assertEqual(q.carregar(alvo), ([entrada()], []))
            entradas, erros = q.carregar(link)
        self.assertEqual(entradas, [])
        self.assertEqual(len(erros), 1)

    def test_json_aninhado_fundo_devolve_erro_sem_quebrar(self):
        fundo = "[" * 30000 + "]" * 30000
        self.assertLess(len(fundo), q.TETO_BYTES)
        for texto in (fundo, '{"entradas": ' + fundo + "}"):
            with self.subTest(tamanho=len(texto)):
                entradas, erros = self.ler(texto)
                self.assertEqual(entradas, [])
                self.assertEqual(len(erros), 1)
                self.assertIn("ilegível", erros[0])

    def test_aninhamento_medido_pelo_leitor_no_teto_de_json_raso(self):
        # 64 níveis ({ e [) passam ao formato; 65 são ilegíveis por conta do leitor, sem depender do RecursionError do python
        def aninhado(niveis):
            return '{"entradas": ' + "[" * (niveis - 1) + "]" * (niveis - 1) + "}"
        self.assertEqual(self.ler(aninhado(64)), ([], ["quarentena: `entradas` não é uma lista de objetos"]))
        entradas, erros = self.ler(aninhado(65))
        self.assertEqual(entradas, [])
        self.assertEqual(len(erros), 1)
        self.assertIn("ilegível", erros[0])

    def test_arquivo_acima_do_teto_nao_e_lido(self):
        vazio = '{"entradas": []}'
        no_teto = vazio + " " * (q.TETO_BYTES - len(vazio))
        self.assertEqual(self.ler(no_teto), ([], []))
        entradas, erros = self.ler(no_teto + " ")
        self.assertEqual(entradas, [])
        self.assertTrue(any("acima de" in m for m in erros))


class Validar(unittest.TestCase):
    hoje = D(2026, 11, 21)

    def erros(self, *entradas):
        return q.validar(list(entradas), self.hoje)

    def test_entrada_certa_nao_tem_erro(self):
        self.assertEqual(self.erros(entrada()), [])

    def test_campo_faltando(self):
        for campo in q.CAMPOS:
            with self.subTest(campo=campo):
                e = entrada()
                del e[campo]
                self.assertTrue(any(f"falta `{campo}`" in m for m in self.erros(e)))

    def test_classe_fora_da_lista(self):
        self.assertTrue(any("classe" in m for m in self.erros(entrada(classe="sorte"))))

    def test_data_fora_de_aaaa_mm_dd(self):
        for desde in ("20/11/2026", "2026-13-01", "2026-11-2", "20261120", 20261120):
            with self.subTest(desde=desde):
                self.assertTrue(any("AAAA-MM-DD" in m for m in self.erros(entrada(desde=desde))))

    def test_prazo_de_ate_sete_dias_e_nao_antes_de_desde(self):
        self.assertEqual(self.erros(entrada(prazo="2026-11-20")), [])
        self.assertEqual(self.erros(entrada(prazo="2026-11-27")), [])
        self.assertTrue(any("7 dias" in m for m in self.erros(entrada(prazo="2026-11-28"))))
        self.assertTrue(any("7 dias" in m for m in self.erros(entrada(prazo="2026-11-19"))))

    def test_desde_no_futuro_e_erro(self):
        self.assertEqual(self.erros(entrada(desde="2026-11-21", prazo="2026-11-28")), [])
        futura = entrada(desde="2026-11-22", prazo="2026-11-29")
        self.assertTrue(any("no futuro" in m for m in self.erros(futura)))
        self.assertEqual(q.ativas([futura], self.hoje), [])

    def test_teste_e_o_id_de_um_teste_so(self):
        for bom in ("tests.test_a.A.test_x", "t.A.test", "tests.sub.test_a.TestA.test_x_1"):
            with self.subTest(bom=bom):
                self.assertEqual(self.erros(entrada(bom)), [])
        ruins = ("tests.*", "tests", "tests.test_a", "tests.test_a.A", ["tests.test_a.A.test_x"], 1,
                 "tests.test_a.A.test_x tests.test_b", "tests/test_a.A.test_x", "tests.test_a.A.test_x*", "tests.a.A.test_١")
        for ruim in ruins:
            with self.subTest(ruim=ruim):
                self.assertTrue(any("id de um teste" in m for m in self.erros(entrada(ruim))))

    def test_teste_repetido_e_erro(self):
        outra = entrada(desde="2026-11-21", prazo="2026-11-28")
        self.assertEqual(self.erros(entrada(), entrada("t.A.test_y")), [])
        self.assertTrue(any("repetido" in m for m in self.erros(entrada(), outra)))

    def test_autorizacao_so_a_n(self):
        for ok in ("OK do dono", "A-", "C-A-3", "A-1x"):
            with self.subTest(ok=ok):
                self.assertTrue(any("autorizacao" in m for m in self.erros(entrada(autorizacao=ok))))

    def test_autorizacao_so_com_digito_ascii(self):
        # QUARENTENA-DIGITO-ASCII: `\d` casava dígito Unicode ("A-١", "A-５"); só [0-9] vale, na entrada e na prorrogação.
        for ok in ("A-\u0661", "A-\uff15", "A-1\u0662"):
            with self.subTest(ok=ok):
                self.assertTrue(any("autorizacao" in m for m in self.erros(entrada(autorizacao=ok))))
                e = entrada(prorrogacao={"prazo": "2026-12-04", "autorizacao": ok})
                self.assertTrue(any("OK novo" in m for m in self.erros(e)))

    def test_prorrogacao_unica_de_ate_sete_dias_com_ok_novo(self):
        self.assertEqual(self.erros(entrada(prorrogacao={"prazo": "2026-12-04", "autorizacao": "A-11"})), [])

    def test_prorrogacao_fora_do_prazo(self):
        for novo in ("2026-11-27", "2026-12-05", "tarde"):
            with self.subTest(novo=novo):
                e = entrada(prorrogacao={"prazo": novo, "autorizacao": "A-11"})
                self.assertTrue(any("prorrogação fora" in m for m in self.erros(e)))

    def test_prorrogacao_sem_ok_novo(self):
        for ok in ("A-10", "A-", None):
            with self.subTest(ok=ok):
                e = entrada(prorrogacao={"prazo": "2026-12-04", "autorizacao": ok})
                self.assertTrue(any("OK novo" in m for m in self.erros(e)))

    def test_prorrogacao_que_nao_e_objeto(self):
        self.assertTrue(any("objeto" in m for m in self.erros(entrada(prorrogacao="2026-12-04"))))

    def test_no_maximo_tres_entradas_ativas(self):
        tres = [entrada(f"t.A.test_{i}") for i in range(3)]
        self.assertEqual(q.validar(tres, self.hoje), [])
        self.assertTrue(any("mais de 3" in m for m in q.validar(tres + [entrada("t.A.test_3")], self.hoje)))

    def test_vencida_nao_conta_no_teto(self):
        vencida = entrada("t.A.test_velha", desde="2026-11-01", prazo="2026-11-08")
        tres = [entrada(f"t.A.test_{i}") for i in range(3)]
        self.assertEqual(q.validar(tres + [vencida], self.hoje), [])


class AtivasEVencidas(unittest.TestCase):
    def test_vale_ate_o_prazo_inclusive(self):
        e = entrada()
        self.assertEqual(q.ativas([e], D(2026, 11, 27)), [e])
        self.assertEqual(q.ativas([e], D(2026, 11, 28)), [])

    def test_vencida_sai_sozinha_e_aparece_nas_vencidas(self):
        e = entrada()
        self.assertEqual(q.vencidas([e], D(2026, 11, 27)), [])
        self.assertEqual(q.vencidas([e], D(2026, 11, 28)), [e])

    def test_prorrogacao_estende_a_validade(self):
        e = entrada(prorrogacao={"prazo": "2026-12-04", "autorizacao": "A-11"})
        self.assertEqual(q.ativas([e], D(2026, 12, 4)), [e])
        self.assertEqual(q.ativas([e], D(2026, 12, 5)), [])
        self.assertEqual(q.vencidas([e], D(2026, 12, 5)), [e])

    def test_com_erro_nao_exclui_nada_de_ativas_nem_de_vencidas(self):
        boa, ruim = entrada(), entrada("t.A.test_ruim", cartao="")
        self.assertEqual(q.ativas([boa, ruim], D(2026, 11, 21)), [])
        self.assertEqual(q.vencidas([boa, ruim], D(2026, 12, 21)), [])

    def test_o_leitor_nao_tem_padrao_de_data(self):
        with self.assertRaises(TypeError):
            q.ativas([])


if __name__ == "__main__":
    unittest.main()
