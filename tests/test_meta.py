"""S4 (0.44.2): `forge-check meta --armar|--desarmar|--estado` grava o objetivo onde o hook de Stop (hooks/meta.py) o lê
(fixtures em tests/hooks/meta)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
        meta.medir_mensagem = lambda hook: (_ for _ in ()).throw(RuntimeError("medida"))
        meta.avaliar_meta = lambda hook, raiz: chamado.append("meta")
        try:
            try:
                meta.principal(type("H", (Falso,), {"campo": lambda self, *c: "Stop"})())
            except RuntimeError:
                chamado.append("escapou")
        finally:
            meta.medir_mensagem, meta.avaliar_meta = original_medir, original_meta
        self.assertIsInstance(chamado[0], RuntimeError)
        self.assertEqual(chamado[1], "meta", "a falha da medida não pula a conferência do objetivo")


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


if __name__ == "__main__":
    unittest.main()
