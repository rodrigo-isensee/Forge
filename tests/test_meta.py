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
