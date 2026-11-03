"""AQ-7 (L36): regressão de comportamento. Cada erro real do orquestrador vira um caso anonimizado em `tests/comportamento/`
e o detector da ADR 0007 (`forge-check transcricao verificar`, só lê, sem IA e sem rede) o acusa. A métrica é a reincidência
detectada: casos detectados sobre casos."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from neutralidade import termos_achados  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "tests" / "comportamento"
MANIFESTO = json.loads((PASTA / "casos.json").read_text(encoding="utf-8"))
CONFIG = json.loads((RAIZ / "tests" / "config.json").read_text(encoding="utf-8"))
REGRA_DA_LINHA = re.compile(r"^transcricao: (?:aviso: )?(R-[A-Z]+(?:\.[a-z]+)?):")
DADO_PESSOAL = [re.compile(p) for p in (
    r"[\w.+-]+@[\w-]+\.[\w.-]+",              # e-mail
    r"/home/|/Users/|[A-Za-z]:\\\\|~/",         # caminho pessoal
    r"gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN",  # token e chave
    r"https?://")]                              # endereço


def verificar(arquivo):
    """(código de saída, linhas) do `transcricao verificar` sobre o arquivo."""
    r = subprocess.run([sys.executable, str(RAIZ / "bin" / "forge-check"), "transcricao", "verificar", str(arquivo)],
                       capture_output=True, text=True, errors="replace")
    return r.returncode, r.stdout.splitlines()


def regras_acusadas(linhas):
    return {m.group(1) for linha in linhas if (m := REGRA_DA_LINHA.match(linha))}


def detectado(caso, pasta=PASTA):
    """O caso é detectado quando o verificador acusa exatamente as regras dele, no código de saída esperado."""
    codigo, linhas = verificar(pasta / caso["arquivo"])
    return (not any(": formato:" in linha for linha in linhas) and regras_acusadas(linhas) == set(caso["regras"])
            and codigo == (1 if caso["bloqueia"] else 0))


def reincidencia_detectada(casos, pasta=PASTA):
    """(detectados, total) dos casos."""
    return sum(1 for caso in casos if detectado(caso, pasta)), len(casos)


class Comportamento(unittest.TestCase):
    def test_cada_caso_de_erro_conhecido_e_detectado_com_as_regras_dele(self):  # L36
        casos = MANIFESTO["casos"]
        self.assertGreaterEqual(len(casos), 3, "de três a cinco casos de erro real")
        self.assertEqual(len({c["id"] for c in casos}), len(casos))
        for caso in casos:
            with self.subTest(caso=caso["id"], erro=caso["erro"]):
                self.assertTrue(detectado(caso), verificar(PASTA / caso["arquivo"]))

    def test_a_reincidencia_detectada_e_todos_os_casos(self):  # L36, AQ-7
        detectados, total = reincidencia_detectada(MANIFESTO["casos"])
        self.assertEqual((detectados, total), (len(MANIFESTO["casos"]),) * 2, f"reincidência detectada: {detectados}/{total}")

    def test_a_sessao_limpa_nao_dispara_nenhuma_regra(self):  # L36
        self.assertEqual(verificar(PASTA / MANIFESTO["sessao_limpa"]), (0, []))

    def test_caso_que_o_detector_nao_acusa_nao_conta_como_detectado(self):  # L36
        sem_erro = {"id": "CP-X", "arquivo": MANIFESTO["sessao_limpa"], "regras": ["R-MAIN"], "bloqueia": True}
        reais = MANIFESTO["casos"]
        self.assertEqual(reincidencia_detectada([*reais, sem_erro]), (len(reais), len(reais) + 1))
        outra_regra = {**reais[0], "regras": ["R-MAIN"]}
        self.assertFalse(detectado(outra_regra))

    def test_os_arquivos_da_pasta_sao_os_do_manifesto_sem_link(self):  # L36, C-36
        declarados = {c["arquivo"] for c in MANIFESTO["casos"]} | {MANIFESTO["sessao_limpa"], "casos.json"}
        presentes = {p.name for p in PASTA.iterdir()}
        self.assertEqual(presentes, declarados)
        self.assertFalse([p for p in PASTA.iterdir() if p.is_symlink()])

    def test_os_casos_so_levam_marcadores_sem_dado_pessoal_nem_segredo(self):  # L36, T-36
        entradas = CONFIG["termos_proibidos_hash"]
        for caminho in sorted(PASTA.iterdir()):
            texto = caminho.read_text(encoding="utf-8")
            with self.subTest(arquivo=caminho.name):
                self.assertEqual(termos_achados(texto, entradas), set(), "termo de projeto")
                for padrao in DADO_PESSOAL:
                    self.assertIsNone(padrao.search(texto), f"{padrao.pattern}: dado pessoal, caminho, endereço ou segredo")
                if caminho.suffix == ".jsonl":
                    for linha in texto.splitlines():
                        json.loads(linha)


if __name__ == "__main__":
    unittest.main()
