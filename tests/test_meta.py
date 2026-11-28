"""S4 (0.44.2): `forge-check meta --armar|--desarmar|--estado` grava o objetivo onde o hook de Stop (hooks/meta.py) o lê
(fixtures em tests/hooks/meta)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")


class Meta(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-meta-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        subprocess.run(["git", "init", "-q", str(self.tmp)], check=True, env=sem_manutencao())
        (self.tmp / ".forge").mkdir()

    def rodar(self, *args):
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.tmp), "meta", *args], capture_output=True, text=True,
                           env=dict(os.environ, HOME=str(self.tmp / "home")))
        return r.returncode, r.stdout

    def test_armar_grava_no_run_do_hook_e_desarmar_tira(self):
        rc, out = self.rodar("--armar", "p1", "--checagem", "python3 -m unittest tests.x", "--checagem", "true")
        self.assertEqual(rc, 0, out)
        meta = json.loads((self.tmp / ".forge" / "run" / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual((meta["pedido"], meta["armado"], meta["checagens"]), ("p1", True, [["python3", "-m", "unittest", "tests.x"], ["true"]]))
        self.assertIn("armado=True", self.rodar("--estado")[1])
        self.assertEqual(self.rodar("--desarmar")[0], 0)
        self.assertEqual(self.rodar("--estado")[0], 1)

    def test_sem_checagem_ou_pedido_invalido_recusa(self):
        self.assertEqual(self.rodar("--armar", "p1")[0], 2)
        self.assertEqual(self.rodar("--armar", "../x", "--checagem", "true")[0], 2)
        self.assertEqual(self.rodar("--armar", "p1", "--checagem", "'aberta")[0], 2)
        self.assertFalse((self.tmp / ".forge" / "run" / "meta.json").exists())


class Jargao(unittest.TestCase):
    def test_lista_vem_da_tabela_do_modo_iniciante(self):
        sys.path.insert(0, str(RAIZ / "hooks"))
        try:
            import meta  # noqa: PLC0415
        finally:
            sys.path.pop(0)
        self.assertEqual(set(meta.jargao()), {"pull request", "PR", "branch", "merge", "mesclar", "commit", "repositório", "hook", "CI",
                                              "deploy"})

    def test_ultima_mensagem_com_texto_do_assistente(self):
        sys.path.insert(0, str(RAIZ / "hooks"))
        try:
            import meta  # noqa: PLC0415
        finally:
            sys.path.pop(0)
        ferramenta = {"type": "tool_use", "name": "Bash", "input": {}}
        linhas = [{"type": "assistant", "message": {"content": [{"type": "text", "text": "velha"}]}},
                  {"type": "user", "message": {"content": "oi"}},
                  {"type": "assistant", "message": {"content": [ferramenta, {"type": "text", "text": "nova"}]}},
                  {"type": "user", "message": {"content": [{"type": "text", "text": "do dono"}]}},
                  {"type": "assistant", "message": {"content": [ferramenta]}}]
        with tempfile.TemporaryDirectory() as pasta:
            arq = Path(pasta) / "t.jsonl"
            arq.write_text("\n".join(json.dumps(l) for l in linhas) + "\n", encoding="utf-8")
            self.assertEqual(meta.ultima_mensagem(str(arq)), "nova")

    def test_medida_que_falha_nao_troca_o_stop(self):
        sys.path.insert(0, str(RAIZ / "hooks"))
        try:
            import meta  # noqa: PLC0415
        finally:
            sys.path.pop(0)
        chamado = []

        class Falso:
            def campo(self, *_):
                return "/x"

            def projeto(self, *_a, **_k):
                return Path("/x")

            def cwd(self):
                return Path("/x")

            def registrar_erro(self, erro):
                chamado.append(erro)

        original_medir, original_meta = meta.medir_mensagem, meta.avaliar_meta
        meta.medir_mensagem = lambda hook, raiz: (_ for _ in ()).throw(RuntimeError("medida"))
        meta.avaliar_meta = lambda hook, raiz: chamado.append("meta")
        try:
            try:
                meta.principal(type("H", (Falso,), {"campo": lambda self, *c: "Stop"})())
            except RuntimeError:
                chamado.append("escapou")
        finally:
            meta.medir_mensagem, meta.avaliar_meta = original_medir, original_meta
        self.assertEqual(chamado[0], "meta", "a decisão do Stop vem antes da medida (E2.237)")
        self.assertIsInstance(chamado[1], RuntimeError, "a falha da medida vai ao erros.log e não escapa")
        self.assertEqual(len(chamado), 2)

    def test_stop_bloqueado_ainda_mede_e_sai_com_2(self):
        """E2.237: bloquear sai do processo; a medida roda depois da decisão, e o código 2 não muda."""
        sys.path.insert(0, str(RAIZ / "hooks"))
        try:
            import meta  # noqa: PLC0415
        finally:
            sys.path.pop(0)
        chamado = []

        class Falso:
            def campo(self, *_):
                return "Stop"

            def projeto(self, *_a, **_k):
                return Path("/x")

            def cwd(self):
                return Path("/x")

        original_medir, original_meta = meta.medir_mensagem, meta.avaliar_meta
        meta.medir_mensagem = lambda hook, raiz: chamado.append(("medida", raiz))
        meta.avaliar_meta = lambda hook, raiz: sys.exit(2)
        try:
            with self.assertRaises(SystemExit) as saida:
                meta.principal(Falso())
        finally:
            meta.medir_mensagem, meta.avaliar_meta = original_medir, original_meta
        self.assertEqual(saida.exception.code, 2)
        self.assertEqual(chamado, [("medida", Path("/x"))], "a medida recebe a raiz (idioma do dono, SIEG-G4)")


def importar_meta():
    sys.path.insert(0, str(RAIZ / "hooks"))
    try:
        import meta  # noqa: PLC0415
    finally:
        sys.path.pop(0)
    return meta


class JargaoPorClasse(unittest.TestCase):
    """E7.4 (v047): S6 conta por classe os termos sem explicação (diretriz 31); um caso que conta e um que passa por classe."""

    CASOS = {"etapa": ("Terminei a E7.4 hoje.", "Subi a versão 0.47.1 hoje."),
             "commit": ("Está no e13aed85 agora.", "Uma decade defaced inteira."),
             "regra": ("Vale a R-MAIN aqui.", "Vale o R-2 aqui."),
             "cartao": ("O VISAO-DE-FOCO andou.", "A Visão-de-foco andou."),
             "ferramenta": ("Rode forge-check e git push e gh pr.", "O forge vai bem e o git é seu."),
             "caminho": ("Mudei hooks/meta.py ontem.", "Mudei o arquivo e/ou a pasta docs/.")}

    def setUp(self):
        self.meta = importar_meta()

    def test_cada_classe_conta_o_termo_e_deixa_passar_o_parecido(self):
        for classe, (conta, passa) in self.CASOS.items():
            with self.subTest(classe=classe):
                self.assertEqual(self.meta.classes_de_jargao(conta).get(classe, 0), 3 if classe == "ferramenta" else 1)
                self.assertEqual(self.meta.classes_de_jargao(passa), {})

    def test_termo_explicado_nao_conta(self):
        self.assertEqual(self.meta.classes_de_jargao("A E7.1 (a etapa de desenho) acabou."), {})
        self.assertEqual(self.meta.classes_de_jargao("Sabe o que é a E7.1? É o desenho."), {})
        self.assertEqual(self.meta.classes_de_jargao("A E7.1 acabou. Isto (o resto) não explica."), {"etapa": 1})

    def test_bloco_de_codigo_e_citacao_nao_contam_e_crase_conta(self):
        cerca = "`" * 3
        self.assertEqual(self.meta.classes_de_jargao(f"{cerca}\ngit push origin x\n{cerca}\n> A E1.2 citada."), {})
        self.assertEqual(self.meta.classes_de_jargao(f"{cerca}\ngit x\n{cerca}\nA E1.2 depois do bloco."), {"etapa": 1})
        self.assertEqual(self.meta.classes_de_jargao("Rode `forge doutor` agora."), {"ferramenta": 1})
        self.assertEqual(self.meta.classes_de_jargao(f"{cerca}\nfim\ngit push origin x\n{cerca}"), {}, "linha do bloco não fecha")

    def test_cerca_de_til_e_fechada_pela_mesma_cerca(self):
        """E2.237 (review A2): ~~~ abre bloco; dentro dela, ``` não fecha nem reabre."""
        crases = "`" * 3
        self.assertEqual(self.meta.classes_de_jargao("~~~\ngit push origin x\n~~~\n> A E1.2 citada."), {})
        self.assertEqual(self.meta.classes_de_jargao("~~~\ngit x\n~~~\nA E1.2 depois do bloco."), {"etapa": 1})
        self.assertEqual(self.meta.classes_de_jargao(f"~~~\n{crases}\nA E1.2 dentro.\n~~~"), {})
        self.assertEqual(self.meta.classes_de_jargao(f"~~~\n{crases}\n~~~\nA E1.2 depois."), {"etapa": 1})

    def test_etapa_no_fim_da_frase_conta(self):
        """E2.237 (review A1): o ponto final não esconde a etapa; a versão de três números não é etapa."""
        self.assertEqual(self.meta.classes_de_jargao("Terminei a E7.4."), {"etapa": 1})
        self.assertEqual(self.meta.classes_de_jargao("Terminei a E7.4.\nE a E7.5!"), {"etapa": 2})
        self.assertEqual(self.meta.classes_de_jargao("Subi a E7.4.1 hoje."), {})

    def test_regra_de_duas_letras_conta_e_uma_letra_nao(self):
        """E2.351: o ID de regra de duas letras (R-QA) conta; uma letra só ou minúscula não é ID de regra."""
        self.assertEqual(self.meta.classes_de_jargao("Segue o R-QA na entrega."), {"regra": 1})
        self.assertEqual(self.meta.classes_de_jargao("Vale o R-X e o R-Qa aqui."), {})

    def test_o_que_e_longe_do_termo_nao_explica(self):
        """E2.237: o "o que é" só vale na janela antes do termo (o custo não cresce com a mensagem)."""
        longe = "Sabe o que é" + " palavra" * 40 + " a E7.1 hoje"
        self.assertEqual(self.meta.classes_de_jargao(longe), {"etapa": 1})

    def test_medida_le_so_o_teto_e_marca_cortado(self):
        """E2.237 (segurança A1 a A4): a medida inteira lê só TETO_DA_MEDIDA caracteres e marca o corte."""
        teto = self.meta.TETO_DA_MEDIDA
        texto = "a " * (teto // 2) + "R-MAIN commit hoje"
        gravado = self.medir(texto)
        self.assertEqual((gravado["caracteres"], gravado["cortado"], gravado["classes"], gravado["jargao"]),
                         (len(texto), True, {}, []))
        curto = self.medir("Fiz a E7.4.")
        self.assertEqual((curto["cortado"], curto["classes"]), (False, {"etapa": 1}))

    def test_mensagem_adversaria_de_200_kb_mede_em_tempo_limitado(self):
        """E2.237 (segurança S1 a S4): as entradas que levavam de 36 s a mais de 300 s ficam abaixo de 5 s de CPU."""
        for texto in ("E1.1 " * 40000, "AB" * 50000 + "-" + "A-" * 50000 + "a", "R-MAIN " * 29000):
            with self.subTest(inicio=texto[:6]):
                inicio = time.process_time()
                self.medir(texto)
                self.assertLess(time.process_time() - inicio, 5)

    def medir(self, texto):
        with tempfile.TemporaryDirectory() as pasta:
            hook = type("Hook", (), {"campo": lambda self, chave: {"last_assistant_message": texto}.get(chave),
                                     "run": lambda self: Path(pasta), "iniciante": lambda self: False})()
            self.meta.medir_mensagem(hook)
            return json.loads((Path(pasta) / "mensagens.jsonl").read_text(encoding="utf-8"))

    def test_mensagem_do_evento_vence_o_transcrito_e_o_termo_nao_vai_ao_disco(self):
        with tempfile.TemporaryDirectory() as pasta:
            arq = Path(pasta) / "t.jsonl"
            linha = {"type": "assistant", "message": {"content": [{"type": "text", "text": "velha com R-MAIN"}]}}
            arq.write_text(json.dumps(linha) + "\n", encoding="utf-8")
            entrada = {"transcript_path": str(arq), "last_assistant_message": "Fiz a E7.4 no e13aed85."}

            class Hook:
                def campo(self, chave):
                    return entrada.get(chave)

                def run(self):
                    return Path(pasta)

                def iniciante(self):
                    return False

            self.meta.medir_mensagem(Hook())
            entrada["last_assistant_message"] = ""
            self.meta.medir_mensagem(Hook())
            gravado = (Path(pasta) / "mensagens.jsonl").read_text(encoding="utf-8")
        linhas = [json.loads(l) for l in gravado.splitlines()]
        self.assertEqual(len(linhas), 2, "a mensagem do evento vazia cai para o transcrito e é medida")
        primeira, segunda = linhas
        self.assertEqual(primeira["classes"], {"etapa": 1, "commit": 1})
        self.assertEqual(segunda["classes"], {"regra": 1}, "sem a mensagem do evento, cai para o transcrito")
        for termo in ("E7.4", "e13aed85", "R-MAIN"):
            self.assertNotIn(termo, gravado)


class IdiomaDoDono(unittest.TestCase):
    """SIEG-G4 (v047, E2.683): a medida acusa mensagem ao dono em outro idioma; o idioma do dono vem do .forge/config.json."""

    PT = "Terminei a etapa e não ficou pendência; está tudo verde e você já pode ver."
    EN = "I finished the step and it is ready; you can check the branch now."
    ES = "Hecho. El cambio quedó bien y usted puede ver los detalles cuando hay tiempo."

    def setUp(self):
        self.meta = importar_meta()
        self.raiz = Path(tempfile.mkdtemp(prefix="forge-idioma-"))
        self.addCleanup(shutil.rmtree, self.raiz, ignore_errors=True)

    def configurar(self, config):
        (self.raiz / ".forge").mkdir(exist_ok=True)
        (self.raiz / ".forge" / "config.json").write_text(json.dumps(config), encoding="utf-8")

    def medir(self, texto, raiz):
        with tempfile.TemporaryDirectory() as pasta:
            hook = type("Hook", (), {"campo": lambda self, chave: {"last_assistant_message": texto}.get(chave),
                                     "run": lambda self: Path(pasta), "iniciante": lambda self: False})()
            self.meta.medir_mensagem(hook, raiz)
            linha = json.loads((Path(pasta) / "mensagens.jsonl").read_text(encoding="utf-8"))
        return linha["idioma"], linha["idioma_do_dono"], linha["outro_idioma"]

    def test_sem_configuracao_o_dono_fala_portugues_e_ingles_e_acusado(self):
        self.assertEqual(self.medir(self.PT, None), ("pt", "pt", False))
        self.assertEqual(self.medir(self.EN, None), ("en", "pt", True))
        self.assertEqual(self.medir(self.EN, self.raiz), ("en", "pt", True), "raiz sem .forge/config.json")
        self.configurar({"pesados": []})
        self.assertEqual(self.medir(self.ES, self.raiz), ("es", "pt", True), "config sem a chave")
        self.configurar(["en"])
        self.assertEqual(self.medir(self.EN, self.raiz), ("en", "pt", True), "config que não é objeto")

    def test_idioma_vem_da_configuracao_do_projeto(self):
        self.configurar({"idioma_do_dono": "en"})
        self.assertEqual(self.medir(self.EN, self.raiz), ("en", "en", False))
        self.assertEqual(self.medir(self.PT, self.raiz), ("pt", "en", True))

    def test_idioma_sem_lista_nao_mede_nem_acusa(self):
        self.configurar({"idioma_do_dono": "fr"})
        self.assertEqual(self.medir(self.PT, self.raiz), ("pt", None, False))
        self.configurar({"idioma_do_dono": ["pt"]})
        self.assertEqual(self.medir(self.EN, self.raiz), ("en", None, False))

    def test_mensagem_curta_mista_ou_em_codigo_fica_sem_idioma_e_nao_e_acusada(self):
        cerca = "`" * 3
        for texto in ("Feito: git push.", "Feito, não ficou nada.", "the and is não que uma", f"Pronto.\n{cerca}\n{self.EN}\n{cerca}\n> {self.EN}"):
            with self.subTest(texto=texto[:20]):
                self.assertEqual(self.medir(texto, None), (None, "pt", False))

    def test_listas_de_palavras_sao_disjuntas(self):
        listas = list(self.meta.PALAVRAS_DO_IDIOMA.values())
        self.assertGreaterEqual(len(listas), 3)
        for i, uma in enumerate(listas):
            for outra in listas[i + 1:]:
                self.assertEqual(uma & outra, frozenset())


class NotasEntreFerramentas(unittest.TestCase):
    """E25.1 (v0478, 0.47.9): o idioma vale também para as notas entre chamadas de ferramenta da rodada (desde a última fala
    do dono); a nota de outro idioma conta em `notas_em_outro_idioma` e acende `outro_idioma`."""

    PT = "Terminei a etapa e não ficou pendência; está tudo verde e você já pode ver."
    EN = "I finished the step and it is ready; you can check the branch now."

    def setUp(self):
        self.meta = importar_meta()
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-notas-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    @staticmethod
    def nota(texto, **extra):
        return {"type": "assistant", **extra, "message": {"content": [{"type": "text", "text": texto},
                                                                     {"type": "tool_use", "name": "Bash", "input": {}}]}}

    @staticmethod
    def dono(texto):
        return {"type": "user", "message": {"content": texto}}

    def transcrito(self, registros, nome="t.jsonl"):
        caminho = self.tmp / nome
        caminho.write_text("".join((r if isinstance(r, str) else json.dumps(r, separators=(",", ":"))) + "\n"
                                   for r in registros), encoding="utf-8")
        return caminho

    def medir(self, registros, final=None, raiz=None, nome="t.jsonl"):
        campos = {"last_assistant_message": final or self.PT, "transcript_path": str(self.transcrito(registros, nome))}
        run = self.tmp / "run"
        run.mkdir(exist_ok=True)
        (run / "mensagens.jsonl").unlink(missing_ok=True)
        self.erros = []
        hook = type("Hook", (), {"campo": lambda _s, chave: campos.get(chave), "run": lambda _s: run,
                                 "iniciante": lambda _s: False, "registrar_erro": lambda _s, erro: self.erros.append(erro)})()
        self.meta.medir_mensagem(hook, raiz)
        linha = json.loads((run / "mensagens.jsonl").read_text(encoding="utf-8"))
        return linha.get("notas_em_outro_idioma"), linha.get("outro_idioma")

    def test_nota_em_outro_idioma_na_rodada_acusa(self):
        self.assertEqual(self.medir([self.dono("oi"), self.nota(self.EN), self.nota(self.PT)]), (1, True))

    def test_controle_notas_no_idioma_do_dono_nao_acusam(self):
        self.assertEqual(self.medir([self.dono("oi"), self.nota(self.PT), self.nota(self.PT)]), (0, False))

    def test_nota_de_rodada_anterior_nao_conta(self):
        """A fala do dono fecha a rodada: a nota em inglês antes dela não é desta mensagem."""
        self.assertEqual(self.medir([self.nota(self.EN), self.dono("continue"), self.nota(self.PT)]), (0, False))

    def test_nota_de_subagente_nao_conta(self):
        self.assertEqual(self.medir([self.dono("oi"), self.nota(self.EN, isSidechain=True)]), (0, False))

    def test_mensagem_final_no_transcrito_nao_conta_como_nota(self):
        final = {"type": "assistant", "message": {"content": [{"type": "text", "text": self.EN}]}}
        self.assertEqual(self.medir([self.dono("oi"), final], final=self.EN), (0, True))

    def test_nota_curta_fica_sem_idioma_e_nao_conta(self):
        self.assertEqual(self.medir([self.dono("oi"), self.nota("Done."), self.nota("Ok, merged.")]), (0, False))

    def test_linha_ilegivel_nao_interrompe_a_rodada(self):
        self.assertEqual(self.medir([self.dono("oi"), self.nota(self.EN), '{"type":"assistant", quebrado']), (1, True))

    def test_dono_sem_lista_nao_mede_notas(self):
        (self.tmp / ".forge").mkdir()
        (self.tmp / ".forge" / "config.json").write_text(json.dumps({"idioma_do_dono": "fr"}), encoding="utf-8")
        self.assertEqual(self.medir([self.dono("oi"), self.nota(self.EN)], raiz=self.tmp), (0, False))

    def test_resultado_de_ferramenta_nem_se_decodifica(self):
        """Custo: a linha de resultado de ferramenta (a maior do transcrito) é pulada antes do json.loads."""
        resultado = {"type": "user", "toolUseResult": {}, "message": {"content": [{"type": "tool_result", "content": "z" * 50}]}}
        caminho = self.transcrito([self.dono("oi"), self.nota(self.EN), resultado])
        with mock.patch.object(self.meta.json, "loads", wraps=json.loads) as loads:
            self.assertEqual(len(self.meta.notas_da_rodada(str(caminho), self.PT)[0]), 1)
        self.assertFalse([c for c in loads.call_args_list if "tool_result" in c.args[0]])

    def test_registro_fora_da_forma_e_pulado_sem_erro(self):
        """Transcrito com mensagem, conteúdo ou bloco fora da forma e sem mensagem final: a nota boa ainda é lida."""
        registros = [self.dono("oi"), self.nota(self.EN), {"type": "assistant", "message": "texto solto"},
                     {"type": "assistant", "message": {"content": None}}, {"type": "assistant", "message": {"content": ["solto"]}},
                     '["assistant", "registro que não é objeto"]']
        self.assertEqual(self.meta.notas_da_rodada(str(self.transcrito(registros)), None)[0], [self.EN])

    def test_notas_param_no_teto_da_medida(self):
        """O total lido das notas para em TETO_DA_MEDIDA: o tempo não cresce com a rodada."""
        caminho = self.transcrito([self.dono("oi")] + [self.nota("x" * 30) for _ in range(5)])
        with mock.patch.object(self.meta, "TETO_DA_MEDIDA", 70):
            notas = self.meta.notas_da_rodada(str(caminho), self.PT)[0]
        self.assertEqual([len(n) for n in notas], [30, 30, 10])

    # E109.1 (META-NOTAS-RECONTA, A1 e A2 de docs/reviews/v0479-meta-notas.md): num segundo Stop sem fala nova do dono, a
    # nota já medida e a final anterior não se recontam; e a nota cuja chamada traz o texto "tool_result" ainda é lida.
    PT2 = "Recebi o aviso do agente e não ficou pendência; você já pode ver a branch."

    def com_uuid(self, registro, uuid):
        return {**registro, "uuid": uuid}

    def final(self, texto, uuid):
        return {"type": "assistant", "uuid": uuid, "message": {"content": [{"type": "text", "text": texto}]}}

    def aviso(self, uuid):
        return {"type": "user", "uuid": uuid, "message": {"content": "<task-notification>pronto</task-notification>"}}

    def test_segundo_stop_sem_fala_do_dono_nao_reconta_a_nota(self):
        rodada = [self.com_uuid(self.dono("oi"), "u0"), self.com_uuid(self.nota(self.EN), "u1"), self.final(self.PT, "u2")]
        self.assertEqual(self.medir(rodada), (1, True))
        seguinte = rodada + [self.aviso("u3"), self.com_uuid(self.nota(self.PT), "u4"), self.final(self.PT2, "u5")]
        self.assertEqual(self.medir(seguinte, final=self.PT2), (0, False))

    def test_nota_nova_depois_da_marca_ainda_conta(self):
        rodada = [self.com_uuid(self.dono("oi"), "u0"), self.final(self.PT, "u1")]
        self.assertEqual(self.medir(rodada), (0, False))
        seguinte = rodada + [self.aviso("u2"), self.com_uuid(self.nota(self.EN), "u3"), self.final(self.PT2, "u4")]
        self.assertEqual(self.medir(seguinte, final=self.PT2), (1, True))

    def test_final_anterior_que_chegou_depois_ao_transcrito_nao_conta(self):
        """D13: no primeiro Stop a final (em inglês) ainda não estava no transcrito; no segundo ela aparece depois da marca."""
        rodada = [self.com_uuid(self.dono("oi"), "u0"), self.com_uuid(self.nota(self.PT), "u1")]
        self.assertEqual(self.medir(rodada, final=self.EN), (0, True))
        seguinte = rodada + [self.final(self.EN, "u2"), self.aviso("u3"), self.final(self.PT2, "u4")]
        self.assertEqual(self.medir(seguinte, final=self.PT2), (0, False))

    def test_marca_de_outro_transcrito_nao_vale(self):
        (self.tmp / "run").mkdir(exist_ok=True)
        (self.tmp / "run" / "notas.json").write_text(json.dumps(
            {str(self.tmp / "outro.jsonl"): {"marca": "u1", "final": self.meta.resumo(self.EN)}}), encoding="utf-8")
        self.assertEqual(self.medir([self.dono("oi"), self.com_uuid(self.nota(self.EN), "u1")]), (1, True))

    # E137.1 (A1 de docs/reviews/v0480-meta-notas.md): o .forge/run é um só para as sessões do projeto; a marca de uma
    # sessão não apaga a da outra.
    def test_stop_de_outra_sessao_no_meio_nao_faz_recontar(self):
        rodada = [self.com_uuid(self.dono("oi"), "u0"), self.com_uuid(self.nota(self.EN), "u1"), self.final(self.PT, "u2")]
        self.assertEqual(self.medir(rodada), (1, True))
        self.assertEqual(self.medir([self.com_uuid(self.dono("oi"), "b0"), self.final(self.PT, "b1")], nome="b.jsonl"), (0, False))
        seguinte = rodada + [self.aviso("u3"), self.com_uuid(self.nota(self.PT), "u4"), self.final(self.PT2, "u5")]
        self.assertEqual(self.medir(seguinte, final=self.PT2), (0, False))

    def test_marca_do_transcrito_fora_da_forma_e_ignorada(self):
        (self.tmp / "run").mkdir(exist_ok=True)
        (self.tmp / "run" / "notas.json").write_text(json.dumps({str(self.tmp / "t.jsonl"): "u1"}), encoding="utf-8")
        self.assertEqual(self.medir([self.dono("oi"), self.com_uuid(self.nota(self.EN), "u1")]), (1, True))

    def test_marcas_guardadas_param_no_teto_e_sai_a_mais_velha(self):
        for i in range(self.meta.MARCAS_GUARDADAS + 1):
            self.medir([self.dono("oi"), self.final(self.PT, f"u{i}")], nome=f"s{i}.jsonl")
        marcas = json.loads((self.tmp / "run" / "notas.json").read_text(encoding="utf-8"))
        self.assertEqual(len(marcas), self.meta.MARCAS_GUARDADAS)
        self.assertNotIn(str(self.tmp / "s0.jsonl"), marcas)

    # E137.21 (A1 de docs/qa/v0480-meta-notas-reconta.md): sai a marca usada há mais tempo, não a gravada primeiro.
    def test_sessao_que_volta_a_ser_usada_guarda_a_marca(self):
        teto = self.meta.MARCAS_GUARDADAS
        for i in range(teto):
            self.medir([self.dono("oi"), self.final(self.PT, f"u{i}")], nome=f"s{i}.jsonl")
        self.medir([self.dono("oi"), self.final(self.PT, "u0")], nome="s0.jsonl")
        for i in range(teto, 2 * teto - 1):
            self.medir([self.dono("oi"), self.final(self.PT, f"u{i}")], nome=f"s{i}.jsonl")
        marcas = json.loads((self.tmp / "run" / "notas.json").read_text(encoding="utf-8"))
        self.assertEqual(len(marcas), teto)
        self.assertIn(str(self.tmp / "s0.jsonl"), marcas)
        self.assertNotIn(str(self.tmp / "s1.jsonl"), marcas)

    def test_marca_ilegivel_ou_fora_da_forma_e_ignorada(self):
        (self.tmp / "run").mkdir(exist_ok=True)
        for conteudo in ("{quebrado", "[]"):
            with self.subTest(conteudo=conteudo):
                (self.tmp / "run" / "notas.json").write_text(conteudo, encoding="utf-8")
                self.assertEqual(self.medir([self.dono("oi"), self.nota(self.EN)]), (1, True))

    def test_marca_que_nao_grava_nao_perde_a_linha_da_medida(self):
        """E109.7 (A1 e S1 de docs/security/v0480-meta-notas.md): notas.json como pasta; a linha vai ao disco e o erro ao log."""
        (self.tmp / "run" / "notas.json").mkdir(parents=True)
        self.assertEqual(self.medir([self.dono("oi"), self.nota(self.EN)]), (1, True))
        self.assertEqual([type(e) for e in self.erros], [IsADirectoryError])

    def test_nota_cuja_chamada_traz_tool_result_ainda_conta(self):
        nota = {"type": "assistant", "message": {"content": [
            {"type": "text", "text": self.EN}, {"type": "tool_use", "name": "Grep", "input": {"pattern": "tool_result"}}]}}
        self.assertEqual(self.medir([self.dono("oi"), nota]), (1, True))

    def test_nota_cuja_entrada_traz_o_par_type_tool_result_ainda_conta(self):
        """E137.1 (A2 de docs/reviews/v0479-meta-notas.md): a entrada da ferramenta é objeto, sem aspas escapadas; o par
        "type":"tool_result" ali não faz da nota um resultado de ferramenta."""
        nota = {"type": "assistant", "message": {"content": [
            {"type": "text", "text": self.EN}, {"type": "tool_use", "name": "Busca", "input": {"type": "tool_result"}}]}}
        self.assertEqual(self.medir([self.dono("oi"), nota]), (1, True))


class VariosProjetos(unittest.TestCase):
    """MP1 (diretriz 35, v0474 E3.3): com dois projetos ativos, a medida acusa a mensagem sem `Projeto:` e a fala do dono que
    cita o outro projeto sem a pergunta; com um projeto só ou na sessão do Forge, nada muda."""

    def setUp(self):
        self.meta = importar_meta()
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-mp1-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.raiz = self.tmp / "loja"
        (self.raiz / ".forge").mkdir(parents=True)
        (self.raiz / ".forge" / "versao").write_text("0.47.5\n", encoding="utf-8")
        ativos = self.tmp / "ativos.json"
        original, self.meta.ATIVOS = self.meta.ATIVOS, str(ativos)
        self.addCleanup(setattr, self.meta, "ATIVOS", original)
        self.ativos(["loja", "estoque"])

    def ativos(self, valor):
        ativos = self.tmp / "ativos.json"
        ativos.rmdir() if ativos.is_dir() and not ativos.is_symlink() else ativos.unlink(missing_ok=True)  # link, FIFO ou pasta
        (self.tmp / "ativos.json").write_text(valor if isinstance(valor, str) else json.dumps({"projetos": valor}), encoding="utf-8")

    def medir(self, resposta, fala="faça o relatório", raiz=None, depois=()):
        transcrito = self.tmp / "t.jsonl"
        linhas = [{"type": "user", "message": {"content": fala}}, {"type": "assistant", "message": {"content": "ok"}}, *depois]
        transcrito.write_text("".join(json.dumps(l) + "\n" for l in linhas), encoding="utf-8")
        campos = {"last_assistant_message": resposta, "transcript_path": str(transcrito)}
        with tempfile.TemporaryDirectory() as pasta:
            hook = type("Hook", (), {"campo": lambda self, chave: campos.get(chave), "run": lambda self: Path(pasta),
                                     "iniciante": lambda self: False})()
            self.meta.medir_mensagem(hook, self.raiz if raiz is None else raiz)
            linha = json.loads((Path(pasta) / "mensagens.jsonl").read_text(encoding="utf-8"))
        return {k: linha[k] for k in ("projetos_ativos", "sem_projeto", "cita_outro_projeto", "sem_pergunta_do_projeto") if k in linha}

    def test_recibo_sem_projeto_acusa_e_com_projeto_passa(self):
        self.assertEqual(self.medir("Recebi: vou fazer o relatório."),
                         {"projetos_ativos": 2, "sem_projeto": True, "cita_outro_projeto": False, "sem_pergunta_do_projeto": False})
        self.assertFalse(self.medir("Projeto: loja\nRecebi: vou fazer o relatório.")["sem_projeto"])

    def test_fala_que_cita_o_outro_projeto_pede_a_pergunta(self):
        fala = "mude o login do Estoque"
        self.assertEqual(self.medir("Projeto: loja\nFeito.", fala)["sem_pergunta_do_projeto"], True)
        self.assertEqual(self.medir("Projeto: loja\nIsto é para o projeto estoque?", fala),
                         {"projetos_ativos": 2, "sem_projeto": False, "cita_outro_projeto": True, "sem_pergunta_do_projeto": False})
        self.assertFalse(self.medir("Projeto: loja\nFeito.", "mude o login da loja")["cita_outro_projeto"], "o próprio projeto")
        self.assertFalse(self.medir("Projeto: loja\nFeito.", "mude o estoque-novo")["cita_outro_projeto"], "nome dentro de outro")

    def test_um_projeto_so_registro_ilegivel_ou_sessao_do_forge_nao_mede(self):
        for valor in (["loja"], ["loja", ""], "{x", "[" * 50000, json.dumps(["loja", "estoque"]), json.dumps({"projetos": "loja estoque"})):
            with self.subTest(ativos=str(valor)[:20]):
                self.ativos(valor)
                self.assertEqual(self.medir("Recebi."), {})
        self.ativos(["loja", "estoque"])
        forge = self.tmp / "Forge"
        (forge / ".claude-plugin").mkdir(parents=True)
        (forge / ".claude-plugin" / "plugin.json").write_text('{"name": "forge"}', encoding="utf-8")
        self.assertEqual(self.medir("Recebi.", "mude o estoque", raiz=forge), {}, "exceção do dono: a sessão do Forge")
        self.assertEqual(self.meta.medida_do_projeto(None, None, "Recebi."), {}, "sem raiz")
        with mock.patch.object(self.meta, "projetos_ativos", side_effect=AssertionError("ATIVOS lido")):
            self.assertEqual(self.meta.medida_do_projeto(None, forge, "Recebi."), {}, "a sessão do Forge nem lê ATIVOS")
            self.assertEqual(self.meta.medida_do_projeto(None, None, "Recebi."), {}, "sem raiz, nem lê ATIVOS")

    def test_so_a_fala_digitada_pelo_dono_conta(self):
        """Review A1: aviso de subagente, linha meta e lembrete do sistema depois da fala não são a fala do dono."""
        avisos = ({"type": "user", "message": {"content": "<task-notification>o PR do estoque</task-notification>"}},
                  {"type": "user", "isMeta": True, "message": {"content": "o estoque caiu"}},
                  {"type": "user", "message": {"content": [{"type": "text", "text": "<system-reminder>estoque</system-reminder>"}]}})
        for aviso in avisos:
            with self.subTest(aviso=str(aviso)[:40]):
                self.assertFalse(self.medir("Projeto: loja\nFeito.", "mude o login da loja", depois=[aviso])["cita_outro_projeto"])
        self.assertTrue(self.medir("Projeto: loja\nFeito.", "veja o estoque", depois=[avisos[0]])["cita_outro_projeto"])
        so_espaco = {"type": "user", "message": {"content": "  "}}
        self.assertTrue(self.medir("Projeto: loja\nFeito.", "veja o estoque", depois=[so_espaco])["cita_outro_projeto"])
        self.assertEqual((self.meta.fala_do_dono(None), self.meta.ultima_mensagem(None)), (None, None), "sem transcrito")

    def test_leitor_distingue_sem_registro_de_registro_ilegivel(self):
        """MP5: sem o arquivo, [] (um projeto); link, FIFO, pasta, caminho sob arquivo ou fora da forma, None (o `agentes`
        recusa o escape, falha fechada)."""
        ler, ativos = self.meta.ler_projetos_ativos, self.tmp / "ativos.json"
        self.assertEqual(ler(str(self.tmp / "nada.json")), [], "sem o arquivo")
        self.assertIsNone(ler(str(ativos / "sob-arquivo.json")), "caminho sob um arquivo")
        for nome, montar in {"link": lambda: ativos.symlink_to(self.tmp / "nada.json"), "fifo": lambda: os.mkfifo(ativos),
                             "pasta": lambda: ativos.mkdir(), "lista": lambda: self.ativos("[]"),
                             "projetos texto": lambda: self.ativos('{"projetos": "loja"}')}.items():
            with self.subTest(caso=nome):
                ativos.unlink(missing_ok=True) if not ativos.is_dir() or ativos.is_symlink() else ativos.rmdir()
                montar()
                self.assertIsNone(ler(str(ativos)))

    def test_erro_de_leitura_e_registro_ilegivel(self):
        """MP5, volta (review A1, segurança A2): OSError no fstat ou no read devolve None, nunca exceção que o `executar`
        libera (falha aberta)."""
        self.ativos(["loja"])
        for funcao in ("fstat", "read"):
            with self.subTest(funcao=funcao), mock.patch.object(os, funcao, side_effect=OSError(5, "EIO")):
                self.assertIsNone(self.meta.ler_projetos_ativos(self.meta.ATIVOS))

    def test_nome_fora_da_forma_fecha_o_agentes_e_o_meta_tolera(self):
        """MP5, volta (segurança A1): nome fora da forma não baixa a contagem do `agentes` (None); o `meta` só o deixa de fora."""
        for ruim in ("x" * 129, 5, "  ", None):
            with self.subTest(nome=str(ruim)[:10]):
                self.ativos(["loja", ruim])
                self.assertIsNone(self.meta.ler_projetos_ativos(self.meta.ATIVOS))
                self.assertEqual(self.meta.ler_projetos_ativos(self.meta.ATIVOS, tolerante=True), ["loja"])
        self.ativos(["loja", "x" * 128])
        self.assertEqual(len(self.meta.ler_projetos_ativos(self.meta.ATIVOS)), 2, "128 caracteres ainda vale")
        self.ativos(["loja", "estoque", 7])
        self.assertEqual(self.medir("Recebi.")["projetos_ativos"], 2, "o `meta` segue tolerante")

    def test_nome_repetido_conta_uma_vez(self):
        """MP5, volta (review A2): repetido, sem diferença de maiúsculas, conta uma vez; vale o primeiro, na ordem."""
        self.ativos(["Loja", "estoque", "loja", "LOJA"])
        self.assertEqual(self.meta.ler_projetos_ativos(self.meta.ATIVOS), ["Loja", "estoque"])
        self.ativos(["loja", "Loja"])
        self.assertEqual(self.medir("Recebi."), {}, "um projeto só: o `meta` não mede")

    def test_proprio_projeto_sem_diferenca_de_maiusculas(self):
        self.ativos(["Loja", "estoque"])
        self.assertFalse(self.medir("Projeto: loja\nFeito.", "mude a loja")["cita_outro_projeto"])

    def test_ativos_em_link_fifo_grande_ou_com_nomes_demais_nao_mede(self):
        """Segurança A1: ATIVOS só vale como arquivo regular, sem link, de até TETO_DE_ATIVOS bytes e MAXIMO_DE_ATIVOS nomes."""
        ativos = self.tmp / "ativos.json"
        valido = json.dumps({"projetos": ["loja", "estoque"]})
        casos = {"link": lambda: (ativos.unlink(), (self.tmp / "real.json").write_text(valido, encoding="utf-8"),
                                  ativos.symlink_to(self.tmp / "real.json")),  # o alvo é válido: só o link recusa
                 "fifo": lambda: (ativos.unlink(), os.mkfifo(ativos)),
                 "pasta": lambda: (ativos.unlink(), ativos.mkdir()),
                 "grande": lambda: self.ativos(valido + " " * self.meta.TETO_DE_ATIVOS),
                 "nomes demais": lambda: self.ativos(["loja"] + [f"p{i}" for i in range(self.meta.MAXIMO_DE_ATIVOS)])}
        for nome, montar in casos.items():
            with self.subTest(caso=nome):
                self.ativos(valido)
                montar()
                self.assertEqual(self.medir("Recebi."), {})
        self.ativos(valido + " " * (self.meta.TETO_DE_ATIVOS - len(valido)))
        self.assertEqual(self.medir("Recebi.")["projetos_ativos"], 2, "no teto exato ainda vale")
        self.ativos(["loja"] + [f"p{i}" for i in range(self.meta.MAXIMO_DE_ATIVOS - 1)])
        self.assertEqual(self.medir("Recebi.")["projetos_ativos"], self.meta.MAXIMO_DE_ATIVOS, "no máximo exato ainda vale")
        self.ativos(["loja", "estoque", "x" * (self.meta.MAXIMO_DO_NOME + 1)])
        self.assertEqual(self.medir("Recebi.")["projetos_ativos"], 2, "nome longo demais fica de fora")
        self.ativos(["loja", "x" * self.meta.MAXIMO_DO_NOME])
        self.assertEqual(self.medir("Recebi.")["projetos_ativos"], 2, "nome no máximo exato vale")

    def test_ativos_em_fifo_com_escritor_e_json_valido_nao_vale(self):
        """Segurança A1 (MP5-01): o FIFO com escritor e JSON válido de dois nomes também dá None; só a guarda S_ISREG recusa."""
        ativos = self.tmp / "ativos.json"
        ativos.unlink()
        os.mkfifo(ativos)
        escritor = os.open(ativos, os.O_RDWR | os.O_NONBLOCK)  # o escritor fica aberto: a leitura acharia o JSON
        self.addCleanup(os.close, escritor)
        os.write(escritor, json.dumps({"projetos": ["loja", "estoque"]}).encode("utf-8"))
        self.assertIsNone(self.meta.ler_projetos_ativos(self.meta.ATIVOS))

    def test_ativos_em_fifo_nao_troca_a_recusa_do_stop(self):
        """Segurança A1 (S2): com ATIVOS em FIFO, o Stop com a checagem falhando sai com 2 (R-PROVA) no prazo, sem travar."""
        raiz = self.tmp / "proj"
        (raiz / ".forge" / "run").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(raiz)], check=True, env=sem_manutencao(), capture_output=True)
        (raiz / ".forge" / "versao").write_text("0.47.5\n", encoding="utf-8")
        (raiz / ".forge" / "run" / "meta.json").write_text(json.dumps({"pedido": "p1", "checagens": [["false"]], "armado": True,
                                                                       "repeticoes": 0}), encoding="utf-8")
        (raiz / "t.jsonl").write_text(json.dumps({"type": "user", "message": {"content": "mude o estoque"}}) + "\n", encoding="utf-8")
        (self.tmp / "home" / ".forge" / "maquina").mkdir(parents=True)
        os.mkfifo(self.tmp / "home" / ".forge" / "maquina" / "projetos-ativos.json")
        env = sem_manutencao({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.tmp / "home"),
                              "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
        lancador = "import runpy, sys; sys.path.insert(0, sys.argv[1]); runpy.run_path(sys.argv[2], run_name='__main__')"
        entrada = {"hook_event_name": "Stop", "session_id": "s1", "cwd": str(raiz), "transcript_path": str(raiz / "t.jsonl"),
                   "last_assistant_message": "Recebi."}
        r = subprocess.run([sys.executable, "-I", "-c", lancador, str(RAIZ / "hooks"), str(RAIZ / "hooks" / "meta.py")],
                           input=json.dumps(entrada), cwd=raiz, env=env, capture_output=True, text=True, timeout=20)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("`false` (rc=1)", r.stderr)


if __name__ == "__main__":
    unittest.main()
