"""0.45.7 (E6, E7 e E8; desenho docs/arquitetura/v0457-camadas.md): a recomendação de corte leva a origem (`anotar --tipo pergunta` e
`decisoes --resposta`), a decisão em códigos contra a recomendada leva `revertida=` e toda decisão leva `--confere`; o `brief selar`
recusa a decisão posterior à entrada sem conferência ou com `nao-passa` sem pergunta e resposta do dono. Sem rede."""
import argparse
import contextlib
import datetime
import hashlib
import io
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

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ / "bin" / "forge-check"
fc = SourceFileLoader("forge_check_camadas_dono", str(FORGE_CHECK)).load_module()
dono = fc.modulo_do_dono()

PEDIDO = "# p\n\n## Decisões do usuário (registro literal)\nDECISÃO DO DONO (2026-01-01 10:00): \"A\".\n\n## Histórico\n- 2026-01-01 09:00: aberto\n"
CAMPOS = "origem: relatório do agente que corrigiu o CI da 0.45.4 · procurado: docs/qa/, tests/ · seguir: perde a recusa · não seguir: mantém o custo"
CORTE_SEM = "1a) descartar a recusa do bin/forge_apoio_testes.py como link [recomendada] [reversível] · 1b) manter a recusa [reversível]"
CORTE_OK = f"1a) descartar a recusa do bin/forge_apoio_testes.py como link [recomendada] [reversível] · {CAMPOS} · 1b) manter a recusa [reversível]"
RAIZES = ("cortar", "descartar", "afrouxar", "retirar", "remover", "apagar", "aposentar", "abandonar")


def pergunta(literal):
    return f"PERGUNTA AO DONO (2026-01-02 10:00): \"{literal}\"\n"


class Base(unittest.TestCase):
    """Uma raiz de projeto sem nada do Forge: só docs/pedidos/p.md (o mesmo `anotar` vale no Forge e em todo projeto)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-camadas-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.arq = self.tmp / "docs" / "pedidos" / "p.md"
        self.arq.parent.mkdir(parents=True)
        self.arq.write_text(PEDIDO, encoding="utf-8")

    def com_pergunta(self, literal):
        self.arq.write_text(PEDIDO.replace("\n\n## Histórico", "\n" + pergunta(literal) + "\n## Histórico"), encoding="utf-8")

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


class TravaDeOrigem(Base):  # E6
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
        sem = "1a) deixar o teste de lado [recomendada] [corte] · 1b) seguir com ele"
        self.recusa("pergunta", sem)
        linhas, rc = self.anotar("pergunta", sem.replace("[corte]", f"[corte] · {CAMPOS}"))
        self.assertEqual(rc, 0, linhas)

    def test_cada_raiz_do_lexico_com_acento_e_caixa(self):  # CT-E6-14
        casos = [f"1a) {r} o teste [recomendada] · 1b) manter" for r in RAIZES]
        casos += [f"1a) {r} [recomendada] · 1b) manter" for r in ("Descartar o teste", "REMOVÊ-LO", "retirá-la", "Afrouxá-la")]
        self.assertGreaterEqual(len(casos), 8)
        for literal in casos:
            with self.subTest(literal=literal):
                self.assertTrue(dono.recusa_de_corte(dono.opcoes_da_pergunta(literal)), literal)

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


class RecomendacaoRevertida(Base):  # E7
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

    def test_codigos_que_nao_se_leem_sao_recusados(self):
        self.com_pergunta(CORTE_OK)
        self.assertIn("decisoes --resposta", self.recusa("decisao", "1a 1c", confere="mede"))
        self.arq.write_text(PEDIDO, encoding="utf-8")
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


class ConfereNoAnotar(Base):  # E8
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

    def test_nao_passa_imprime_o_modelo_da_pergunta(self):  # CT-E8-12
        linhas, rc = self.anotar("decisao", "corte o teste", confere="nao-passa")
        self.assertEqual(rc, 0, linhas)
        modelo = linhas[-1]
        for campo in ("alternativa:", "[recomendada]", "origem:", "procurado:", "seguir:", "não seguir:", 'seguir a decisão "corte o teste"'):
            self.assertIn(campo, modelo)

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


if __name__ == "__main__":
    unittest.main()
