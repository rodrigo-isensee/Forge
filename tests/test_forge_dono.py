"""0.44.1: a conversa com o dono e entre sessões no disco (`bin/forge_dono.py`, pelo `bin/forge-check`): resposta por código
curto (O4), fala do dono literal (S2), recado entre sessões (S8) e pausa por limite de uso com retomada (X1)."""
import argparse
import contextlib
import datetime
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from test_selo_e_entrega import PEDIDO as PEDIDO_DO_SELO, Repositorio  # noqa: E402
from test_voltas import FORGE_CHECK, Raiz  # noqa: E402

PERGUNTA = ('# p\n\n## Decisões do usuário (registro literal)\nPERGUNTA AO DONO (2026-11-09 10:00): duas questões → '
            '"1a) usar a fila [recomendada] [reversível] 1b) usar o banco 2a) arquivar a branch velha [recomendada] [irreversível] 2b) manter"\n')
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
        self.assertTrue(any(l.startswith("pergunta: 2) 2a) arquivar") for l in linhas), linhas)
        cod, linhas, _ = self.resposta("2a, aprovo")
        self.assertEqual(cod, 0, linhas)
        self.assertEqual(linhas[:2], ["resposta: 1 -> 1a: usar a fila [recomendada] [reversível]",
                                      "resposta: 2 -> 2a: arquivar a branch velha [recomendada] [irreversível]"])

    def test_palavra_solta_so_escolhe_a_marcada_reversivel(self):
        """O4 (review da 0.44.1): a marca vale com ou sem acento e em qualquer caixa; sem marca, a palavra solta não escolhe; o código
        explícito escolhe sempre."""
        sys.path.insert(0, str(Path(FORGE_CHECK).parent))
        from forge_dono import ler_resposta, opcoes_da_pergunta  # noqa: PLC0415
        for literal in ("1a) force push na main [recomendada] [irreversivel] 1b) manter",
                        "1a) force push na main [recomendada] [IRREVERSÍVEL] 1b) manter",
                        "1a) apagar a branch main [recomendada] 1b) manter"):
            for palavra in ("aprovo", "ok"):
                with self.subTest(literal=literal, palavra=palavra):
                    escolhas, ambiguas = ler_resposta(opcoes_da_pergunta(literal), palavra)
                    self.assertEqual(escolhas, {})
                    self.assertTrue(ambiguas)
                    self.assertEqual("é irreversível" in ambiguas[0], "[recomendada] 1b)" not in literal, ambiguas)
            self.assertEqual(ler_resposta(opcoes_da_pergunta(literal), "1a"), ({1: "a"}, []))
        self.assertEqual(ler_resposta(opcoes_da_pergunta("1a) fila [recomendada] [Reversivel] 1b) banco"), "ok"), ({1: "a"}, []))

    def test_ambigua_volta_como_pergunta(self):
        for texto, motivo in (("pode", "`pode` fora do vocabulário"), ("1c", "o código 1c não existe"), ("3a", "o código 3a não existe"),
                              ("1a 1b", "duas opções para a questão 1"), ("", "nenhuma questão respondida")):
            with self.subTest(texto):
                cod, linhas, _ = self.resposta(texto)
                self.assertEqual(cod, 1, linhas)
                self.assertIn(motivo, linhas[0])
                self.assertIn("volta ao dono como pergunta", linhas[0])

    def test_sem_recomendada_unica_a_palavra_solta_nao_vale(self):
        self.gravar("docs/pedidos/xpto.md", PERGUNTA.replace(" [recomendada] [reversível] 1b)", " 1b)"))
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

    def test_nao_grava_atraves_de_link(self):
        """X1 (review da 0.44.1): `.forge/pausa.json` (ou `.forge`) como link não leva a gravação para o alvo."""
        alvo = self.tmp / "alvo.txt"
        alvo.write_text("intacto\n", encoding="utf-8")
        (self.tmp / ".forge").mkdir(exist_ok=True)
        (self.tmp / ".forge" / "pausa.json").symlink_to(alvo)
        self.assertEqual(self.rodar("pausa", "--gravar", "--retoma-em", self.hora(30), "--onde", "x")[0], 2)
        self.assertEqual(alvo.read_text(encoding="utf-8"), "intacto\n")
        (self.tmp / ".forge" / "pausa.json").unlink()
        (self.tmp / ".forge").rename(self.tmp / "forge-real")
        (self.tmp / ".forge").symlink_to(self.tmp / "forge-real")
        self.assertEqual(self.rodar("pausa", "--gravar", "--retoma-em", self.hora(30), "--onde", "x")[0], 2)
        self.assertFalse((self.tmp / "forge-real" / "pausa.json").exists())

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


# ---- 0.45.7 (E6, E7 e E8; desenho docs/arquitetura/v0457-camadas.md): a recomendação de corte leva a origem, a decisão em códigos
# contra a recomendada leva `revertida=` e toda decisão leva `--confere`; o `brief selar` recusa a decisão posterior à entrada sem
# conferência ou com `nao-passa` sem pergunta e resposta do dono. ----


fc = SourceFileLoader("forge_check_camadas_dono", str(FORGE_CHECK)).load_module()
dono = fc.modulo_do_dono()

PEDIDO_CAMADAS = "# p\n\n## Decisões do usuário (registro literal)\nDECISÃO DO DONO (2026-01-01 10:00): \"A\".\n\n## Histórico\n- 2026-01-01 09:00: aberto\n"
CAMPOS = "origem: relatório do agente que corrigiu o CI da 0.45.4 · procurado: docs/qa/, tests/ · seguir: perde a recusa · não seguir: mantém o custo"
CORTE_SEM = "1a) descartar a recusa do bin/forge_apoio_testes.py como link [recomendada] [reversível] · 1b) manter a recusa [reversível]"
CORTE_OK = f"1a) descartar a recusa do bin/forge_apoio_testes.py como link [recomendada] [reversível] · {CAMPOS} · 1b) manter a recusa [reversível]"
RAIZES = ("cortar", "descartar", "afrouxar", "retirar", "remover", "apagar", "aposentar", "abandonar", "desligar")


def pergunta(literal):
    return f"PERGUNTA AO DONO (2026-01-02 10:00): \"{literal}\"\n"


class BaseCamadas(unittest.TestCase):
    """Uma raiz de projeto sem nada do Forge: só docs/pedidos/p.md (o mesmo `anotar` vale no Forge e em todo projeto)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-camadas-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.arq = self.tmp / "docs" / "pedidos" / "p.md"
        self.arq.parent.mkdir(parents=True)
        self.arq.write_text(PEDIDO_CAMADAS, encoding="utf-8")

    def com_pergunta(self, literal):
        self.arq.write_text(PEDIDO_CAMADAS.replace("\n\n## Histórico", "\n" + pergunta(literal) + "\n## Histórico"), encoding="utf-8")

    def sha(self):
        return hashlib.sha256(self.arq.read_bytes()).hexdigest()

    def anotar(self, tipo, literal, contexto=None, confere=None):
        try:
            return fc.cmd_anotar(self.tmp, "p", tipo, literal, contexto, False, confere)
        except Exception as erro:  # noqa: BLE001 - recusar é sair com rc 2 e a mensagem, nunca quebrar
            self.fail(f"anotar levantou {erro!r}")

    def recusa(self, tipo, literal, contexto=None, confere=None):
        """Anota esperando rc 2 com o pedido idêntico byte a byte; devolve a saída."""
        antes = self.sha()
        linhas, rc = self.anotar(tipo, literal, contexto, confere)
        self.assertEqual(rc, 2, linhas)
        self.assertEqual(self.sha(), antes, linhas)
        self.assertIn("nada gravado", linhas[0])
        return linhas[0]

    def ultima(self):
        return self.arq.read_text(encoding="utf-8").split("\n## Histórico")[0].rstrip("\n").split("\n")[-1]

    def rodar(self, *args):
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.tmp / "home"), "LANG": "C.UTF-8"}
        r = subprocess.run([sys.executable, "-I", str(FORGE_CHECK), "--raiz", str(self.tmp), *args], capture_output=True, text=True,
                           env=env, timeout=120)
        return r.returncode, r.stdout + r.stderr


class TravaDeOrigem(BaseCamadas):  # E6
    def test_corte_recomendado_sem_campos_e_recusado_sem_gravar(self):  # CT-E6-10, o caso do pre-push da v0456
        motivo = self.recusa("pergunta", CORTE_SEM)
        for campo in ("`origem:`", "`procurado:`", "`seguir:`", "`não seguir:`"):
            self.assertIn(campo, motivo)

    def test_cada_campo_faltando_e_citado(self):  # CT-E6-11
        partes = CAMPOS.split(" · ")
        for i, nome in enumerate(("origem", "procurado", "seguir", "não seguir")):
            with self.subTest(falta=nome):
                literal = CORTE_OK.replace(CAMPOS, " · ".join(partes[:i] + partes[i + 1:]))
                self.assertIn(f"sem `{nome}:`", self.recusa("pergunta", literal))

    def test_campo_vazio_vale_como_ausente(self):  # M-E6-5
        self.assertIn("sem `seguir:`", self.recusa("pergunta", CORTE_OK.replace("seguir: perde a recusa", "seguir: ")))

    def test_corte_com_os_quatro_campos_grava_a_linha_com_a_origem(self):  # CT-E6-01
        linhas, rc = self.anotar("pergunta", CORTE_OK)
        self.assertEqual(rc, 0, linhas)
        self.assertIn("origem: relatório do agente que corrigiu o CI da 0.45.4", self.ultima())

    def test_origem_nao_achada_pede_dois_lugares(self):  # CT-E6-03, CT-E6-12
        um = CORTE_OK.replace("origem: relatório do agente que corrigiu o CI da 0.45.4", "origem: não achada").replace("docs/qa/, tests/", "docs/")
        self.assertIn("2 lugares", self.recusa("pergunta", um))
        self.assertIn("2 lugares", self.recusa("pergunta", um.replace("procurado: docs/", "procurado: docs/, ;")))  # pedaço vazio não conta
        linhas, rc = self.anotar("pergunta", um.replace("procurado: docs/", "procurado: docs/, tests/"))
        self.assertEqual(rc, 0, linhas)

    def test_cada_forma_de_referencia_vale(self):  # CT-E6-05
        for ref in ("docs/x.md", "v0457:42", "FILA-27", "ERRO-JARVIS-103", "ADR 0009", "relatório v0457-tech-lead-19"):
            with self.subTest(ref=ref):
                literal = CORTE_OK.replace("relatório do agente que corrigiu o CI da 0.45.4", ref)
                self.assertEqual(dono.recusa_de_corte(dono.opcoes_da_pergunta(literal)), [])

    def test_recomendada_sem_corte_passa_sem_campos(self):  # CT-E6-02, CT-E6-15
        linhas, rc = self.anotar("pergunta", "1a) manter o prazo [recomendada] [reversível] · 1b) adiar")
        self.assertEqual(rc, 0, linhas)
        linhas, rc = self.anotar("pergunta", "1a) manter a recusa [recomendada] · 1b) remover a recusa")
        self.assertEqual(rc, 0, linhas)  # o corte só na opção não recomendada
        self.recusa("pergunta", "1a) manter a recusa · 1b) remover a recusa [recomendada]")
        linhas, rc = self.anotar("pergunta", "1a) manter a recusa [recomendada] · não seguir: remove a recusa · 1b) remover")
        self.assertEqual(rc, 0, linhas)  # o léxico vale fora dos campos de origem

    def test_marca_corte_sem_verbo_do_lexico(self):  # CT-E6-04, CT-E6-13
        sem = "1a) pular o teste [recomendada] [corte] · 1b) seguir com ele"
        linhas, rc = self.anotar("pergunta", sem.replace(" [corte]", ""))
        self.assertEqual(rc, 0, linhas)  # sem verbo do léxico e sem a marca, não é corte
        self.recusa("pergunta", sem)
        linhas, rc = self.anotar("pergunta", sem.replace("[corte]", f"[corte] · {CAMPOS}"))
        self.assertEqual(rc, 0, linhas)

    def test_cada_raiz_do_lexico_com_acento_e_caixa(self):  # CT-E6-14, pelo `anotar`
        casos = [f"1a) {r} o teste [recomendada] · 1b) manter" for r in RAIZES]
        casos += [f"1a) {r} [recomendada] · 1b) manter" for r in ("Descartar o teste", "REMOVÊ-LO", "retirá-la", "Afrouxá-la",
                                                                  "deixar o teste de lado", "Deixá-lo de lado", "DESLIGÁ-LO")]
        self.assertGreaterEqual(len(casos), 10)
        for literal in casos:
            with self.subTest(literal=literal):
                self.assertIn("recomendação de corte sem", self.recusa("pergunta", literal))

    def test_o_que_nao_e_corte_passa_sem_campos(self):  # pré-QA risco 6: lista negativa do léxico
        casos = ["responder com cortesia", "Cortesia ao dono", "manter a regra irremovível", "deixar o prazo como está"]
        self.assertGreaterEqual(len(casos), 4)
        for texto in casos:
            with self.subTest(texto=texto):
                linhas, rc = self.anotar("pergunta", f"1a) {texto} [recomendada] · 1b) mudar")
                self.assertEqual(rc, 0, linhas)

    def test_campos_no_contexto_nao_valem(self):  # CT-E6-18
        self.recusa("pergunta", CORTE_SEM, contexto=CAMPOS)

    def test_resposta_a_pergunta_antiga_de_corte_volta_como_pergunta(self):  # CT-E6-16
        self.com_pergunta(CORTE_SEM)
        rc, saida = self.rodar("decisoes", "--pedido", "p", "--resposta", "1a")
        self.assertEqual(rc, 1, saida)
        self.assertIn("volta ao dono como pergunta", saida)
        self.assertIn("recomendação de corte sem", self.recusa("decisao", "1a", confere="mede"))
        rc, saida = self.rodar("decisoes", "--pedido", "p", "--resposta", "1b")  # PQ-A2: escolher a outra é do dono
        self.assertEqual(rc, 0, saida)
        self.com_pergunta(CORTE_OK)
        rc, saida = self.rodar("decisoes", "--pedido", "p", "--resposta", "1a")
        self.assertEqual(rc, 0, saida)

    def test_decisao_copia_a_origem_da_opcao_escolhida(self):  # CT-E6-17
        self.com_pergunta(CORTE_OK)
        linhas, rc = self.anotar("decisao", "1a", confere="mede")
        self.assertEqual(rc, 0, linhas)
        self.assertIn("; origem=relatório do agente que corrigiu o CI da 0.45.4", self.ultima())
        self.assertNotIn("revertida=", self.ultima())


class RecomendacaoRevertida(BaseCamadas):  # E7
    def test_escolha_contra_a_recomendada_leva_a_marca(self):  # CT-E7-01, CT-E7-02
        self.com_pergunta(CORTE_OK)
        linhas, rc = self.anotar("decisao", "1b", confere="seguro")
        self.assertEqual(rc, 0, linhas)
        self.assertTrue(self.ultima().endswith(f"confere=seguro; forge={fc.versao_da_propria_copia()}; revertida=1b-contra-1a"), self.ultima())
        self.assertIn(dono.MARCA_REVERTIDA, linhas[-1])
        linhas, rc = self.anotar("decisao", "1a", confere="seguro")
        self.assertEqual(rc, 0, linhas)
        self.assertNotIn("revertida=", self.ultima())

    def test_duas_questoes_com_letras_iguais(self):  # CT-E7-03
        self.com_pergunta("1a) fila [recomendada] 1b) banco 2a) manter 2b) mudar [recomendada]")
        linhas, rc = self.anotar("decisao", "1a 2a", confere="mede")
        self.assertEqual(rc, 0, linhas)
        self.assertTrue(self.ultima().endswith("revertida=2a-contra-2b"), self.ultima())

    def test_prosa_e_recomendada_ambigua_ficam_sem_marca(self):  # CT-E7-04, CT-E7-08
        self.com_pergunta(CORTE_OK)
        linhas, rc = self.anotar("decisao", "pode seguir com a outra", confere="mede")
        self.assertEqual(rc, 0, linhas)
        self.assertNotIn("revertida=", self.ultima())
        for literal in ("1a) fila 1b) banco", "1a) fila [recomendada] 1b) banco [recomendada]"):
            with self.subTest(literal=literal):
                self.assertEqual(dono.divergencia(dono.opcoes_da_pergunta(literal), {1: "b"}), {})

    def test_origem_copiada_nao_abre_atributo(self):  # `_valor`: a origem da pergunta não injeta chave na marca
        self.com_pergunta(CORTE_OK.replace("relatório do agente que corrigiu o CI da 0.45.4", "a;b=c|d" + "x" * 200))
        linhas, rc = self.anotar("decisao", "1a", confere="mede")
        self.assertEqual(rc, 0, linhas)
        atributos = dono.atributos_da_linha(self.ultima())
        self.assertEqual(set(atributos), {"confere", "forge", "origem"}, self.ultima())
        self.assertEqual(atributos["origem"], ("a b c d" + "x" * 200)[:160])

    def test_codigos_que_nao_se_leem_sao_recusados(self):
        self.com_pergunta(CORTE_OK)
        self.assertIn("decisoes --resposta", self.recusa("decisao", "1a 1c", confere="mede"))
        self.arq.write_text(PEDIDO_CAMADAS, encoding="utf-8")
        self.assertIn("PERGUNTA AO DONO", self.recusa("decisao", "1a", confere="mede"))

    def test_marca_escrita_a_mao_e_recusada(self):  # CT-E7-06, CT-E8-16
        for campo, valor in (("literal", "1b · atributos: revertida=1b-contra-1a"), ("contexto", "revertida=1b-contra-1a"),
                             ("contexto", "ｒevertida =1b"), ("contexto", "confere=mede"), ("literal", "ok origem=x"),
                             ("contexto", "forge=9.9.9")):
            with self.subTest(campo=campo, valor=valor):
                literal, contexto = (valor, None) if campo == "literal" else ("sim", valor)
                self.assertIn("só a ferramenta grava", self.recusa("decisao", literal, contexto, confere="mede"))
        self.assertIn("só a ferramenta grava", self.recusa("pergunta", "1a) x [recomendada] confere=mede 1b) y"))
        self.assertIn("U+200B", self.recusa("decisao", "sim", "re\u200bvertida=1b", confere="mede"))  # o invisível cai antes
        self.assertIsNotNone(dono.recusa_da_forja("con\u200bfere=mede"))  # e a forja o ignora mesmo assim
        linhas, rc = self.anotar("historico", "a linha leva confere=mede como texto")
        self.assertEqual(rc, 0, linhas)  # o Histórico não leva marca do dono


class ConfereNoAnotar(BaseCamadas):  # E8
    def test_decisao_sem_confere_ou_com_valor_fora_do_vocabulario(self):  # CT-E8-10, CT-E8-11 (PQ-A1: `RAPIDO` é recusado)
        for confere in (None, "", " ", "talvez", "RAPIDO", "rapido "):
            with self.subTest(confere=confere):
                self.recusa("decisao", "sim", confere=confere)
        self.recusa("ordem", "faça", confere="mede")
        rc, saida = self.rodar("anotar", "--pedido", "p", "--tipo", "decisao", "--literal", "sim")
        self.assertEqual(rc, 2, saida)

    def test_cada_criterio_e_gravado(self):  # CT-E8-01
        for confere in ("rapido", "seguro", "barato", "mede", "nao-passa"):
            with self.subTest(confere=confere):
                linhas, rc = self.anotar("decisao", "sim", confere=confere)
                self.assertEqual(rc, 0, linhas)
                self.assertIn(f"atributos: confere={confere}; forge=", self.ultima())

    def test_nao_passa_imprime_o_modelo_da_pergunta(self):  # CT-E8-12: a alternativa é o texto da [recomendada]
        self.com_pergunta("1a) manter o prazo [recomendada] [reversível] · 1b) adiar 2a) fila 2b) banco [recomendada]")
        linhas, rc = self.anotar("decisao", "1b", confere="nao-passa")
        self.assertEqual(rc, 0, linhas)
        modelo = linhas[-1]
        for campo in ("1a) alternativa: manter o prazo [recomendada] · origem:", "procurado:", "seguir:", "não seguir:",
                      '1b) seguir a decisão "1b"'):
            self.assertIn(campo, modelo)
        self.assertNotIn("banco", modelo)  # só a questão que o literal responde
        linhas, rc = self.anotar("decisao", "corte o teste", confere="nao-passa")
        self.assertEqual(rc, 0, linhas)
        self.assertIn("alternativa: manter o prazo; banco [recomendada]", linhas[-1])  # em prosa, a de cada questão
        self.arq.write_text(PEDIDO_CAMADAS, encoding="utf-8")
        linhas, rc = self.anotar("decisao", "corte o teste", confere="nao-passa")
        self.assertEqual(rc, 0, linhas)
        self.assertIn("alternativa: <a do Jarvis: a última pergunta não tem [recomendada]>", linhas[-1])

    def test_sem_o_modulo_do_dono_nada_e_gravado(self):
        original = fc.modulo_do_dono
        fc.modulo_do_dono = lambda: None
        try:
            self.assertIn("forge_dono.py ausente", self.recusa("decisao", "sim", confere="mede"))
        finally:
            fc.modulo_do_dono = original

    def test_pela_linha_de_comando(self):
        rc, saida = self.rodar("anotar", "--pedido", "p", "--tipo", "decisao", "--confere", "barato", "--literal", "sim")
        self.assertEqual(rc, 0, saida)
        self.assertIn("confere=barato", self.ultima())


def decisao(quando, literal, confere=None, prefixo=""):
    marca = f" · atributos: confere={confere}; forge=0.45.7" if confere is not None else ""
    return f"{prefixo}DECISÃO DO DONO ({quando}): \"{literal}\"{marca}"


class Pendencias(unittest.TestCase):  # E8: a regra que o selar aplica, linha a linha
    ENTRADA = datetime.datetime(2026, 11, 12, 0, 0)

    def pendentes(self, *linhas):
        try:
            return [n for n, _ in dono.pendencias_da_conferencia("\n".join(linhas), fc.e_linha_de_decisao, self.ENTRADA)]
        except Exception as erro:  # noqa: BLE001 - linha sem data ou fora da forma não quebra o selar
            self.fail(f"pendencias levantou {erro!r}")

    def test_tabela(self):
        casos = [
            ("antiga sem confere", [decisao("2026-11-11 23:59", "a")], []),
            ("na entrada sem confere", [decisao("2026-11-12 00:00", "a")], [1]),
            ("mesmo dia, depois da hora", [decisao("2026-11-12 08:00", "a")], [1]),
            ("só a data, sem hora", ["- 2026-11-12: DECISÃO DO DONO: a"], [1]),
            ("confere vazio", [decisao("2030-01-01 10:00", "a", "")], [1]),
            ("confere fora do vocabulário", [decisao("2030-01-01 10:00", "a", "talvez")], [1]),
            ("cada critério passa", [decisao("2030-01-01 10:00", c, c) for c in dono.CRITERIOS], []),
            ("nao-passa sem resposta", [decisao("2030-01-01 10:00", "a", "nao-passa")], [1]),
            ("nao-passa, pergunta e resposta", [decisao("2030-01-01 10:00", "a", "nao-passa"), pergunta("1a) x [recomendada] 1b) a").strip(),
                                                decisao("2030-01-01 10:05", "1b", "mede")], []),
            ("resposta antes da pergunta", [decisao("2030-01-01 10:00", "a", "nao-passa"), decisao("2030-01-01 10:01", "b", "mede"),
                                            pergunta("1a) x 1b) a").strip()], [1]),
            ("pergunta respondida com nao-passa", [decisao("2030-01-01 10:00", "a", "nao-passa"), pergunta("1a) x 1b) a").strip(),
                                                   decisao("2030-01-01 10:05", "1b", "nao-passa")], [1, 3]),
            ("resposta de uma pergunta anterior", [pergunta("1a) x 1b) y").strip(), decisao("2030-01-01 10:00", "a", "nao-passa"),
                                                   decisao("2030-01-01 10:05", "1b", "mede")], [2]),
            ("citada no meio não é decisão", ["texto que cita DECISÃO DO DONO (2030-01-01 10:00) sem abrir a linha"], []),
            ("sem data não trava", ["DECISÃO DO DONO: sem data"], []),
            ("confere no texto, sem a marca", ['DECISÃO DO DONO (2030-01-01 10:00): ok; confere=mede'], [1]),
        ]
        self.assertGreaterEqual(len(casos), 6)
        for nome, linhas, esperado in casos:
            with self.subTest(nome):
                self.assertEqual(self.pendentes(*linhas), esperado)

    def test_o_motivo_diz_o_que_falta(self):
        linhas = [decisao("2030-01-01 10:00", "a"), decisao("2030-01-01 10:01", "b", "nao-passa")]
        motivos = [m for _, m in dono.pendencias_da_conferencia("\n".join(linhas), fc.e_linha_de_decisao, self.ENTRADA)]
        self.assertEqual(motivos, ["sem `confere=`", "`confere=nao-passa` sem pergunta e resposta do dono depois"])

    def test_linha_de_plugin_antigo_depois_da_entrada_pende(self):  # pré-QA risco 1
        """O plugin sem a E8 grava a decisão sem a marca; depois da entrada ela pende até pergunta e resposta com critério,
        porque a marca só nasce da ferramenta (a diretriz 9 vale para a decisão nova e para a antiga)."""
        antiga = 'DECISÃO DO DONO (2026-11-13 09:00): paráfrase → "regra B"'
        self.assertEqual(self.pendentes(antiga), [1])
        self.assertEqual(self.pendentes(antiga, decisao("2026-11-13 09:05", "outra", "mede")), [1])  # outra decisão não a resolve
        self.assertEqual(self.pendentes(antiga, pergunta("1a) regra C [recomendada] 1b) regra B").strip(),
                                        decisao("2026-11-13 09:10", "1b", "mede")), [])

    def test_decisao_sem_data_nunca_trava(self):  # pré-QA risco 2: sem data, não se sabe se é anterior à entrada
        for linha in ("DECISÃO DO DONO: sem data", '- DECISÃO DO DONO → "x"', "DECISÃO DO DONO, registrada depois (2030-01-01 10:00): x",
                      "DECISÃO DO DONO (ontem): x · atributos: confere=nao-passa"):
            with self.subTest(linha=linha):
                self.assertEqual(self.pendentes(linha), [])

    def test_a_entrada_e_uma_constante_com_hora(self):  # PQ-A3
        self.assertEqual(dono.ENTRADA_DA_CONFERENCIA, self.ENTRADA)


class SelarConfere(Repositorio):  # E8 no `brief selar`, numa raiz de projeto com git
    def com_decisoes(self, *linhas, pedido=PEDIDO_DO_SELO):
        (self.proj / "docs" / "briefs" / "exemplo-node-backend-1.md").unlink(missing_ok=True)  # o brief seguinte nasce do pedido novo
        return self.gravar("docs/pedidos/exemplo.md", pedido.replace("\n\n## Histórico", "\n" + "\n".join(linhas) + "\n\n## Histórico"))

    def test_nao_passa_sem_resposta_barra_e_a_resposta_libera(self):  # CT-E8-13, CT-E8-03
        self.com_decisoes(decisao("2030-01-01 10:00", "regra B", "nao-passa"))
        self.brief()
        rc, saida = self.selar()
        self.assertEqual(rc, 1, saida)
        self.assertIn("decisões: docs/pedidos/exemplo.md:16 `confere=nao-passa` sem pergunta e resposta do dono depois", saida)
        self.com_decisoes(decisao("2030-01-01 10:00", "regra B", "nao-passa"), pergunta("1a) regra C [recomendada] 1b) regra B").strip(),
                          decisao("2030-01-01 10:10", "1b", "mede") + "; revertida=1b-contra-1a")
        self.brief()
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)

    def test_sem_confere_barra_e_a_antiga_passa(self):  # CT-E8-14, CT-E8-04
        self.com_decisoes(decisao("2030-01-01 10:00", "regra B"))
        self.brief()
        rc, saida = self.selar()
        self.assertEqual(rc, 1, saida)
        self.assertIn("decisões: docs/pedidos/exemplo.md:16 sem `confere=`", saida)
        self.com_decisoes(decisao("2026-11-11 23:59", "regra B"))
        self.brief()
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)

    def test_decisao_posterior_com_criterio_passa(self):  # CT-E8-02
        self.com_decisoes(decisao("2030-01-01 10:00", "regra B", "mede"))
        self.brief()
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)

    def test_linha_de_plugin_antigo_barra_o_selar(self):  # pré-QA risco 1
        self.com_decisoes('DECISÃO DO DONO (2026-11-13 09:00): paráfrase → "regra B"')
        self.brief()
        rc, saida = self.selar()
        self.assertEqual(rc, 1, saida)
        self.assertIn("decisões: docs/pedidos/exemplo.md:16 sem `confere=`", saida)

    def test_sem_o_modulo_do_dono_o_selar_reprova(self):
        self.brief()
        original, fc.modulo_do_dono = fc.modulo_do_dono, lambda: None
        a = argparse.Namespace(arquivo=["docs/briefs/exemplo-node-backend-1.md"], pedido="exemplo", destino=None, sem_selar=False,
                               ref=None, parecer=None)
        saida = io.StringIO()
        try:
            with contextlib.redirect_stdout(saida), unittest.mock.patch.dict(os.environ, self.env, clear=True):
                rc = fc.cmd_brief_selar(self.proj, a)
        except Exception as erro:  # noqa: BLE001 - sem o módulo, o selar reprova com a mensagem, sem quebrar
            self.fail(f"selar levantou {erro!r}")
        finally:
            fc.modulo_do_dono = original
        self.assertEqual(rc, 1, saida.getvalue())
        self.assertIn("forge_dono.py ausente", saida.getvalue())

    def test_fonte_citada_tambem_e_conferida(self):  # CT-E8-15
        self.gravar("docs/pedidos/outro.md", "# outro\n\n" + decisao("2030-01-01 10:00", "regra de lá") + "\n")
        self.com_decisoes('DECISÃO DO DONO (2026-01-01 10:02): "vale docs/pedidos/outro.md".')
        self.brief()
        rc, saida = self.selar()
        self.assertEqual(rc, 1, saida)
        self.assertIn("decisões: docs/pedidos/outro.md:3 sem `confere=`", saida)


class ModeloDeProjeto(SelarConfere):  # CT-E6-19, CT-E7-10, CT-E8-18: as três camadas numa raiz copiada de templates/projeto
    def setUp(self):
        super().setUp()
        shutil.copytree(Path(FORGE_CHECK).resolve().parent.parent / "templates" / "projeto", self.proj, dirs_exist_ok=True)
        self.assertTrue((self.proj / ".forge" / "config.json").is_file())
        self.gravar("docs/pedidos/exemplo.md", PEDIDO_DO_SELO)
        self.git("add", "-A")
        self.commit("modelo do projeto")

    def rodar(self, *args):
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.home), "LANG": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_CONFIG_GLOBAL": os.devnull}
        r = subprocess.run([sys.executable, "-I", str(FORGE_CHECK), "--raiz", str(self.proj), *map(str, args)], capture_output=True,
                           text=True, env=env, timeout=300)
        return r.returncode, r.stdout + r.stderr

    def brief(self, **opcoes):
        """O modelo traz `docs/engineering/achados-recorrentes.md`, que pede ao Jarvis as demais leituras no `## Ler`."""
        arq = super().brief(**opcoes)
        texto = arq.read_text(encoding="utf-8")
        self.assertIn("- PREENCHER: demais leituras do destino", texto)
        arq.write_text(texto.replace("- PREENCHER: demais leituras do destino (propostas, arquivos)\n", ""), encoding="utf-8")
        return arq

    def anotar(self, tipo, literal, *extra):
        return self.rodar("anotar", "--pedido", "exemplo", "--tipo", tipo, "--literal", literal, *extra)

    def test_trava_de_origem(self):  # CT-E6-10, CT-E6-01
        antes = self.pedido()
        rc, saida = self.anotar("pergunta", CORTE_SEM)
        self.assertEqual((rc, self.pedido()), (2, antes), saida)
        rc, saida = self.anotar("pergunta", CORTE_OK)
        self.assertEqual(rc, 0, saida)
        self.assertIn("origem: relatório do agente que corrigiu o CI da 0.45.4", self.pedido())

    def test_recomendacao_revertida(self):  # CT-E7-01
        self.assertEqual(self.anotar("pergunta", CORTE_OK)[0], 0)
        rc, saida = self.anotar("decisao", "1b", "--confere", "seguro")
        self.assertEqual(rc, 0, saida)
        self.assertIn("revertida=1b-contra-1a", self.pedido())

    def test_decisao_sem_confere(self):  # CT-E8-10; CT-E8-13 e CT-E8-02 vêm herdados do SelarConfere, nesta raiz
        antes = self.pedido()
        rc, saida = self.anotar("decisao", "sim")
        self.assertEqual((rc, self.pedido()), (2, antes), saida)


class PerguntasAbertas(unittest.TestCase):  # diretriz 29 (FOCO-NAS-DECISOES, v047 E1.135): `cmd_abertas`, só leitura
    QUADRO = ("# Quadro\n\n## Pronto\n| ID | Cartão | Pedido | Responsável | Entrou | Na coluna desde | Obs. |\n|---|---|---|---|---|---|---|\n"
              "| FORA-DO-PAINEL | não é do dono | docs/pedidos/a.md | dono | 2026-11-01 | 2026-11-01 | — |\n\n"
              "## Aguardando o dono (PA-6: ação · comando · destrava · desde)\n"
              "| ID | Cartão | Pedido | Responsável | Entrou | Na coluna desde | Obs. |\n|---|---|---|---|---|---|---|\n"
              "| TOKEN-X | decidir o token · recomendação A: o bot · ação: responder | docs/pedidos/b.md | dono | 2026-11-02 | 2026-11-02T08:30-0300 | — |\n")

    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.raiz)
        (self.raiz / "docs" / "pedidos").mkdir(parents=True)
        sys.path.insert(0, str(Path(FORGE_CHECK).parent))
        self.addCleanup(sys.path.remove, str(Path(FORGE_CHECK).parent))
        import forge_dono  # noqa: PLC0415
        self.dono = forge_dono

    def pedido(self, nome, *linhas):
        (self.raiz / "docs" / "pedidos" / f"{nome}.md").write_text("# p\n\n## Decisões\n" + "\n".join(linhas) + "\n", encoding="utf-8")

    def abertas(self):
        linhas, rc = self.dono.cmd_abertas(self.raiz)
        self.assertEqual(rc, 0, linhas)
        return linhas

    def test_aberta_sai_com_pedido_hora_pergunta_e_recomendada(self):
        self.pedido("a", 'PERGUNTA AO DONO (2026-11-03 10:00): contexto → "1a) usar a fila [recomendada] [reversível] 1b) usar o banco"')
        self.assertEqual(self.abertas(), ["aberta: outro | a | 2026-11-03 10:00 | 1a) usar a fila [recomendada] [reversível] 1b) usar o "
                                          "banco | recomendada: 1a) usar a fila", "abertas: total=1"])

    def test_respondida_sai_e_decisao_anterior_nao_responde(self):
        self.pedido("a", 'PERGUNTA AO DONO (2026-11-03 10:00): → "pode A?"', "DECISÃO DO DONO (2026-11-03 10:00): sim",
                    'PERGUNTA AO DONO (2026-11-03 11:00): → "pode B? Recomendação: não, espera a C"',
                    "DECISÃO DO DONO (2026-11-03 10:30): a outra")
        self.assertEqual(self.abertas(), ["aberta: outro | a | 2026-11-03 11:00 | pode B? Recomendação: não, espera a C | "
                                          "recomendada: não, espera a C", "abertas: total=1"])

    def test_painel_do_quadro_entra_e_o_resto_do_quadro_nao(self):
        (self.raiz / "KANBAN.md").write_text(self.QUADRO, encoding="utf-8")
        self.assertEqual(self.abertas(), ["aberta: outro | b | 2026-11-02 08:30 | TOKEN-X: decidir o token · recomendação A: o bot · "
                                          "ação: responder | recomendada: A: o bot", "abertas: total=1"])

    def test_sem_pendencia_uma_linha(self):
        self.pedido("a", 'PERGUNTA AO DONO (2026-11-03 10:00): → "pode?"', "DECISÃO DO DONO (2026-11-04 09:00): pode")
        self.assertEqual(self.abertas(), ["Não há decisão sua pendente"])

    def test_ordem_por_peso_e_depois_a_mais_antiga(self):
        self.pedido("a", 'PERGUNTA AO DONO (2026-11-05 10:00): → "muda o escopo da 0.48?"',
                    'PERGUNTA AO DONO (2026-11-06 10:00): → "apaga a branch velha? irreversível"',
                    'PERGUNTA AO DONO (2026-11-01 10:00): → "renomeia o cartão?"',
                    'PERGUNTA AO DONO (2026-11-07 10:00): → "assina o serviço pago?"',
                    'PERGUNTA AO DONO (2026-11-02 10:00): → "tira o item do escopo?"')
        pesos = [(l.split(" | ")[0], l.split(" | ")[2]) for l in self.abertas()[:-1]]
        self.assertEqual(pesos, [("aberta: irreversível", "2026-11-06 10:00"), ("aberta: dinheiro", "2026-11-07 10:00"),
                                 ("aberta: escopo", "2026-11-02 10:00"), ("aberta: escopo", "2026-11-05 10:00"),
                                 ("aberta: outro", "2026-11-01 10:00")])

    def test_formas_do_registro_com_prefixo_aspas_e_sem_parenteses(self):
        self.pedido("a", '- 2026-11-03 09:00: PERGUNTA AO DONO: quem faz a E1.6?', '- 2026-11-03 09:30: DECISÃO DO DONO "A" no H1',
                    'PERGUNTA AO DONO (2026-11-03 ~10h15): → "pode C?"', 'DECISÃO DO DONO 2026-11-03 10:20: "sim"',
                    'PERGUNTA AO DONO (2026-11-04 08:00): → "pode D?"')
        self.pedido("b", '- 2026-11-05 07:00: PERGUNTA AO DONO: com prefixo e sem decisão?')
        self.assertEqual([l.split(" | ")[1:4] for l in self.abertas()[:-1]],
                         [["a", "2026-11-04 08:00", "pode D?"], ["b", "2026-11-05 07:00", "com prefixo e sem decisão?"]])

    def test_pergunta_longa_sai_cortada_numa_linha(self):
        self.pedido("a", 'PERGUNTA AO DONO (2026-11-03 10:00): → "' + "palavra " * 40 + '"')
        pergunta = self.abertas()[0].split(" | ")[3]
        self.assertEqual((len(pergunta), pergunta[-1]), (200, "…"))

    def test_cartao_sem_data_sai_com_traco(self):
        (self.raiz / "KANBAN.md").write_text(self.QUADRO.replace("2026-11-02T08:30-0300", "sem data"), encoding="utf-8")
        self.assertEqual(self.abertas()[0].split(" | ")[2], "—")

    def test_link_e_arquivo_ilegivel_ficam_fora(self):
        fora = self.raiz / "fora.md"
        fora.write_text('PERGUNTA AO DONO (2026-11-03 10:00): → "de fora"\n' + self.QUADRO, encoding="utf-8")
        (self.raiz / "docs" / "pedidos" / "link.md").symlink_to(fora)
        (self.raiz / "KANBAN.md").symlink_to(fora)
        (self.raiz / "docs" / "pedidos" / "ruim.md").write_bytes(b"PERGUNTA AO DONO (2026-11-03 10:00): \xff\n")
        self.assertEqual(self.abertas(), ["abertas: aviso: ruim.md ilegível (UnicodeDecodeError); fora da lista",
                                          "Não há decisão sua pendente"])


if __name__ == "__main__":
    unittest.main()
