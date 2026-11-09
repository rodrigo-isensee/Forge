"""0.44.1: a conversa com o dono e entre sessões no disco (`bin/forge_dono.py`, pelo `bin/forge-check`): resposta por código
curto (O4), fala do dono literal (S2), recado entre sessões (S8) e pausa por limite de uso com retomada (X1)."""
import datetime
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from test_voltas import FORGE_CHECK, Raiz  # noqa: E402

PERGUNTA = ('# p\n\n## Decisões do usuário (registro literal)\nPERGUNTA AO DONO (2026-11-09 10:00): duas questões → '
            '"1a) usar a fila [recomendada] 1b) usar o banco 2a) apagar a branch velha [recomendada] [irreversível] 2b) manter"\n')
VERSAO = json.loads((Path(FORGE_CHECK).parent.parent / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]


class Resposta(Raiz):  # O4
    def setUp(self):
        super().setUp()
        self.gravar("docs/pedidos/xpto.md", PERGUNTA)

    def resposta(self, texto):
        return self.rodar("decisoes", "--pedido", "xpto", "--resposta", texto)

    def test_codigos_curtos_viram_as_opcoes_da_pergunta(self):
        cod, linhas, _ = self.resposta("1B 2b")
        self.assertEqual(cod, 0, linhas)
        self.assertEqual(linhas[:2], ["resposta: 1 -> 1b: usar o banco", "resposta: 2 -> 2b: manter"])
        self.assertIn("forge-check anotar --pedido xpto --tipo decisao", linhas[-1])

    def test_codigo_parcial_deixa_a_outra_pendente(self):
        cod, linhas, _ = self.resposta("1a")
        self.assertEqual(cod, 0)
        self.assertIn("resposta: 2 -> sem resposta: segue pendente", linhas)

    def test_palavra_solta_aprova_a_recomendada_e_nunca_a_irreversivel(self):
        cod, linhas, _ = self.resposta("aprovo")
        self.assertEqual(cod, 1, linhas)
        self.assertIn("a questão 2 é irreversível", linhas[0])
        self.assertTrue(any(l.startswith("pergunta: 2) 2a) apagar") for l in linhas), linhas)
        cod, linhas, _ = self.resposta("2a, aprovo")
        self.assertEqual(cod, 0, linhas)
        self.assertEqual(linhas[:2], ["resposta: 1 -> 1a: usar a fila [recomendada]",
                                      "resposta: 2 -> 2a: apagar a branch velha [recomendada] [irreversível]"])

    def test_ambigua_volta_como_pergunta(self):
        for texto, motivo in (("pode", "`pode` fora do vocabulário"), ("1c", "o código 1c não existe"), ("3a", "o código 3a não existe"),
                              ("1a 1b", "duas opções para a questão 1"), ("", "nenhuma questão respondida")):
            with self.subTest(texto):
                cod, linhas, _ = self.resposta(texto)
                self.assertEqual(cod, 1, linhas)
                self.assertIn(motivo, linhas[0])
                self.assertIn("volta ao dono como pergunta", linhas[0])

    def test_sem_recomendada_unica_a_palavra_solta_nao_vale(self):
        self.gravar("docs/pedidos/xpto.md", PERGUNTA.replace(" [recomendada] 1b)", " 1b)"))
        cod, linhas, _ = self.resposta("sim 2b")
        self.assertEqual(cod, 1)
        self.assertIn("a questão 1 não tem uma recomendada só", linhas[0])

    def test_sem_pergunta_com_opcoes_ou_sem_pedido_nao_le(self):
        self.gravar("docs/pedidos/vazio.md", "# p\n")
        self.assertEqual(self.rodar("decisoes", "--pedido", "vazio", "--resposta", "1a")[0], 2)
        self.assertEqual(self.rodar("decisoes", "--pedido", "nao-existe", "--resposta", "1a")[0], 2)

    def test_vale_a_ultima_pergunta(self):
        self.gravar("docs/pedidos/xpto.md", PERGUNTA + 'PERGUNTA AO DONO (2026-11-09 11:00): "1a) sim 1b) não"\n')
        self.assertEqual(self.resposta("2b")[0], 1)
        self.assertEqual(self.resposta("1b")[1][0], "resposta: 1 -> 1b: não")


class Fala(Raiz):  # S2
    def setUp(self):
        super().setUp()
        self.gravar("docs/pedidos/xpto.md", "# p\n")

    def test_grava_literal_com_sha256_e_le_conferindo(self):
        texto = "Pode fazer a fila,\nmas sem apagar nada."
        cod, linhas, _ = self.rodar("pedido", "fala", "--gravar", "--pedido", "xpto", "--texto", texto)
        self.assertEqual(cod, 0, linhas)
        sha = hashlib.sha256(texto.encode()).hexdigest()
        self.assertTrue(linhas[0].endswith(f"sha256 {sha}"))
        falas = list((self.tmp / "docs" / "pedidos" / "xpto").glob("fala-*.md"))
        self.assertEqual(len(falas), 1)
        conteudo = falas[0].read_text(encoding="utf-8")
        self.assertIn(f"Sha256: {sha}\n", conteudo)
        self.assertIn("não amplia autorização", conteudo)
        self.assertTrue(conteudo.endswith("\n\n" + texto + "\n"))
        self.assertEqual((self.tmp / "docs" / "pedidos" / "xpto.md").read_text(encoding="utf-8"), "# p\n", "o pedido não muda")
        cod, linhas, _ = self.rodar("pedido", "fala", "--ler", "--pedido", "xpto")
        self.assertEqual(cod, 0)
        self.assertIn("íntegra", linhas[0])
        self.assertEqual(linhas[1:3], ["> Pode fazer a fila,", "> mas sem apagar nada."])
        falas[0].write_text(conteudo.replace("sem apagar", "apagando"), encoding="utf-8")
        cod, linhas, _ = self.rodar("pedido", "fala", "--ler", "--pedido", "xpto")
        self.assertEqual(cod, 1)
        self.assertIn("ADULTERADA", linhas[0])

    def test_segunda_fala_nao_sobrescreve_e_recusas_nao_gravam(self):
        for _ in range(2):
            self.assertEqual(self.rodar("pedido", "fala", "--gravar", "--pedido", "xpto", "--texto", "sim")[0], 0)
        self.assertEqual(len(list((self.tmp / "docs" / "pedidos" / "xpto").glob("fala-*.md"))), 2)
        self.assertEqual(self.rodar("pedido", "fala", "--gravar", "--pedido", "xpto", "--texto", "  ")[0], 2)
        self.assertEqual(self.rodar("pedido", "fala", "--gravar", "--pedido", "xpto", "--texto", "x" * 70000)[0], 2)
        self.assertEqual(self.rodar("pedido", "fala", "--gravar", "--pedido", "../x", "--texto", "sim")[0], 2)
        cod, linhas, _ = self.rodar("pedido", "fala", "--ler", "--pedido", "xpto")
        self.assertEqual((cod, linhas[-1][:30]), (0, "pedido fala: 2 fala(s), 0 adul"))

    def test_pasta_da_fala_que_e_link_recusa(self):
        (self.tmp / "fora").mkdir()
        (self.tmp / "docs" / "pedidos" / "xpto").symlink_to(self.tmp / "fora")
        cod, linhas, _ = self.rodar("pedido", "fala", "--gravar", "--pedido", "xpto", "--texto", "sim")
        self.assertEqual(cod, 2, linhas)
        self.assertEqual(list((self.tmp / "fora").iterdir()), [])


class Recado(Raiz):  # S8
    def setUp(self):
        super().setUp()
        self.outra = self.tmp / "outra-sessao"
        self.outra.mkdir()

    def confirmar(self, *extra, raiz=None):
        return self.rodar("recado", "--confirmar", *extra) if raiz is None else self._rodar_em(raiz, "recado", "--confirmar", *extra)

    def _rodar_em(self, raiz, *args):
        import subprocess
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(raiz), *args], capture_output=True, text=True,
                           env=dict(os.environ, HOME=str(self.tmp / "home")))
        return r.returncode, r.stdout.splitlines(), r.stderr

    def test_grava_com_cabecalho_e_so_a_sessao_de_destino_confirma(self):
        cod, linhas, _ = self.rodar("recado", "--para", str(self.outra), "--texto", "suba a 0.44.1 depois da suíte")
        self.assertEqual(cod, 0, linhas)
        arq = next((self.outra / ".forge" / "recados").glob("recado-*.md"))
        texto = arq.read_text(encoding="utf-8")
        for campo in (f"Para: {os.path.realpath(self.outra)}", f"Versao: {VERSAO}",
                      "Sha256: " + hashlib.sha256("suba a 0.44.1 depois da suíte".encode()).hexdigest()):
            self.assertIn(campo + "\n", texto)
        cod, linhas, _ = self._rodar_em(self.outra, "recado", "--confirmar")
        self.assertEqual(cod, 0, linhas)
        self.assertEqual(linhas[-1], "> suba a 0.44.1 depois da suíte")
        (self.tmp / ".forge" / "recados").mkdir(parents=True)
        (self.tmp / ".forge" / "recados" / arq.name).write_text(texto, encoding="utf-8")
        cod, linhas, _ = self.confirmar(arq.name)
        self.assertEqual(cod, 1)
        self.assertIn("sessão errada", linhas[0])

    def test_versao_defasada_ou_texto_adulterado_recusa(self):
        self.rodar("recado", "--para", str(self.outra), "--texto", "x")
        arq = next((self.outra / ".forge" / "recados").glob("recado-*.md"))
        texto = arq.read_text(encoding="utf-8")
        arq.write_text(texto.replace(f"Versao: {VERSAO}", "Versao: 0.1.0"), encoding="utf-8")
        cod, linhas, _ = self._rodar_em(self.outra, "recado", "--confirmar", arq.name)
        self.assertEqual(cod, 1)
        self.assertIn("versão defasada", linhas[0])
        self.assertNotIn("sessão errada", linhas[0])
        arq.write_text(texto.replace("\n\nx\n", "\n\ny\n"), encoding="utf-8")
        cod, linhas, _ = self._rodar_em(self.outra, "recado", "--confirmar", arq.name)
        self.assertEqual((cod, "texto adulterado" in linhas[0], "versão" in linhas[0]), (1, True, False))

    def test_confirmar_pelo_nome_le_esse_recado_e_nao_o_mais_novo(self):
        for texto in ("primeiro", "segundo"):
            self.assertEqual(self._rodar_em(self.outra, "recado", "--para", str(self.outra), "--texto", texto)[0], 0)
        nomes = sorted(p.name for p in (self.outra / ".forge" / "recados").glob("recado-*.md"))
        self.assertEqual(self._rodar_em(self.outra, "recado", "--confirmar")[1][-1], "> segundo")
        self.assertEqual(self._rodar_em(self.outra, "recado", "--confirmar", nomes[0])[1][-1], "> primeiro")
        self.assertEqual(self._rodar_em(self.outra, "recado", "--confirmar", "nao-existe.md")[0], 2)

    def test_sem_recado_ou_destino_invalido(self):
        self.assertEqual(self.confirmar()[0], 2)
        self.assertEqual(self.rodar("recado", "--para", str(self.tmp / "nao-existe"), "--texto", "x")[0], 2)
        self.assertEqual(self.rodar("recado", "--para", str(self.outra), "--texto", "")[0], 2)


class Pausa(Raiz):  # X1
    def hora(self, minutos):
        return (datetime.datetime.now() + datetime.timedelta(minutes=minutos)).strftime("%Y-%m-%dT%H:%M")

    def test_grava_onde_parou_e_so_retoma_quando_a_cota_renova(self):
        cod, linhas, _ = self.rodar("pausa", "--gravar", "--retoma-em", self.hora(30), "--onde", "selar o brief do E2", "--pedido", "xpto")
        self.assertEqual(cod, 0, linhas)
        dados = json.loads((self.tmp / ".forge" / "pausa.json").read_text(encoding="utf-8"))
        self.assertEqual((dados["onde"], dados["pedido"], dados["motivo"]), ("selar o brief do E2", "xpto", "limite de uso (Q1)"))
        cod, linhas, _ = self.rodar("pausa", "--retomar")
        self.assertEqual(cod, 1)
        self.assertIn("ainda não renovou", linhas[0])
        dados["retoma_em"] = self.hora(-1)
        (self.tmp / ".forge" / "pausa.json").write_text(json.dumps(dados), encoding="utf-8")
        cod, linhas, _ = self.rodar("pausa", "--retomar")
        self.assertEqual(cod, 0)
        self.assertEqual(linhas, ["pausa: cota renovada; retome: selar o brief do E2", "pausa: próximo passo: `forge-check proximo xpto`"])
        self.assertFalse((self.tmp / ".forge" / "pausa.json").exists(), "a pausa retomada não vale de novo")
        self.assertEqual(self.rodar("pausa", "--retomar")[1], ["pausa: nenhuma pausa gravada em .forge/pausa.json"])

    def test_esperar_retoma_sozinho_na_hora(self):
        alvo = (datetime.datetime.now() + datetime.timedelta(seconds=2)).isoformat(timespec="seconds")
        self.gravar(".forge/pausa.json", json.dumps({"retoma_em": alvo, "onde": "seguir"}))
        cod, linhas, _ = self.rodar("pausa", "--retomar", "--esperar")
        self.assertEqual(cod, 0)
        self.assertEqual(linhas, ["pausa: cota renovada; retome: seguir"])

    def test_hora_curta_e_recusas(self):
        cod, _, _ = self.rodar("pausa", "--gravar", "--retoma-em", "23:59", "--onde", "x")
        self.assertEqual(cod, 0)
        for args in (("--retoma-em", "amanhã", "--onde", "x"), ("--retoma-em", self.hora(10), "--onde", " "),
                     ("--retoma-em", self.hora(60 * 30), "--onde", "x")):
            with self.subTest(args):
                self.assertEqual(self.rodar("pausa", "--gravar", *args)[0], 2)

    def test_horario_de_hh_mm_passado_e_amanha(self):
        sys.path.insert(0, str(Path(FORGE_CHECK).parent))
        import forge_dono
        agora = datetime.datetime(2026, 11, 9, 12, 0).astimezone()
        self.assertEqual(forge_dono.horario("13:00", agora).date(), agora.date())
        self.assertEqual(forge_dono.horario("11:00", agora).date(), agora.date() + datetime.timedelta(days=1))
        self.assertEqual(forge_dono.horario("12:00", agora).date(), agora.date() + datetime.timedelta(days=1))


if __name__ == "__main__":
    unittest.main()
