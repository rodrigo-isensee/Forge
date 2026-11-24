"""COMANDO-PRONTO-NO-TEXTO (v0478 E66.1): nas skills tocadas, o comando do Forge citado entre crases sai pronto para colar.

Regra: `forge-check` e `forge-changelog` levam um subcomando que existe; `forge-fechar`, `forge-mutante` e `forge-testes` levam
argumento ou opção; toda opção citada existe no --help da ferramenta e as opções obrigatórias do uso estão lá. A fonte da verdade
é o --help de cada ferramenta, rodado com o ambiente limpo."""
import os
import re
import subprocess
import sys
import unittest
from functools import lru_cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTAS = ("briefs-e-conferencia", "fluxo-do-pedido", "trabalho-em-paralelo", "qa-testing", "esperar-estado")  # E96.1: + as duas
COM_SUBCOMANDO = {"check", "changelog"}
FERRAMENTA = re.compile(r"(?<![\w-])(?:\S*/)?forge-(check|fechar|mutante|testes|changelog)(?![\w-])")
CRASE = re.compile(r"`([^`\n]+)`")
OPCAO = re.compile(r"--[a-z][a-z0-9-]*")
ESCOLHAS = re.compile(r"\{([a-z0-9_,-]+)\}")
# Falta de opção obrigatória aceita só aqui, com o motivo; o subcomando segue cobrado. Sai quando o comando couber completo.
SEM_OBRIGATORIAS = {
    # As 6 opções obrigatórias não cabem no teto de tests/fixtures/metricas-texto.json desta skill sem tirar regra (E66.1).
    ("skills/trabalho-em-paralelo/SKILL.md", "check", "escape registrar"),
}


@lru_cache(maxsize=None)
def ajuda(ferramenta, *caminho):
    """O --help da ferramenta (com os subcomandos do caminho), rodado sem o ambiente herdado."""
    arq = str(RAIZ / "bin" / f"forge-{ferramenta}")
    cmd = ["bash", arq] if ferramenta == "fechar" else [sys.executable, "-I", arq]
    env = {"PATH": os.defpath, "LANG": "C.UTF-8", "TMPDIR": os.environ.get("TMPDIR", "/tmp")}
    r = subprocess.run(cmd + list(caminho) + ["--help"], cwd=RAIZ, env=env, capture_output=True, text=True, timeout=60)
    return r.stdout if r.returncode == 0 else ""


def uso(texto):
    """A linha `usage:` (ou `Uso:`) e as continuações recuadas."""
    linhas = texto.splitlines()
    ini = next((i for i, l in enumerate(linhas) if l.startswith(("usage:", "Uso:"))), None)
    if ini is None:
        return ""
    fim = next((j for j in range(ini + 1, len(linhas)) if not linhas[j][:1].isspace() or not linhas[j].strip()), len(linhas))
    return " ".join(linhas[ini:fim])


def obrigatorias(texto_uso):
    """Grupos de opções obrigatórias do uso: cada grupo é satisfeito por qualquer uma das suas (alternativa `( a | b )`)."""
    while re.search(r"\[[^\[\]]*\]", texto_uso):
        texto_uso = re.sub(r"\[[^\[\]]*\]", "", texto_uso)
    grupos = [set(OPCAO.findall(g)) for g in re.findall(r"\(([^()]*)\)", texto_uso)]
    resto = re.sub(r"\([^()]*\)", "", texto_uso)
    return [g for g in grupos if g] + [{o} for o in OPCAO.findall(resto)]


def problemas_da_citacao(ferramenta, resto):
    """Problemas de uma citação: `resto` são as palavras depois do nome da ferramenta."""
    caminho, palavras = [], list(resto)
    if ferramenta in COM_SUBCOMANDO:
        escolhas = ESCOLHAS.search(uso(ajuda(ferramenta)))
        if not palavras or not escolhas or palavras[0] not in escolhas.group(1).split(","):
            return ["sem subcomando"]
        caminho.append(palavras.pop(0))
        sub = ESCOLHAS.search(uso(ajuda(ferramenta, *caminho)))
        if palavras and sub and palavras[0] in sub.group(1).split(","):
            caminho.append(palavras.pop(0))
    elif not palavras:
        return ["sem argumento nem opção"]
    texto = ajuda(ferramenta, *caminho)
    if not texto:
        return [f"--help falhou para {' '.join(caminho)}"]
    conhecidas, usadas = set(OPCAO.findall(texto)), set(OPCAO.findall(" ".join(palavras)))
    erros = [f"opção {o} não existe no --help" for o in sorted(usadas - conhecidas)]
    erros += [f"falta {' ou '.join(sorted(g))}" for g in obrigatorias(uso(texto)) if not g & usadas]
    return erros + formas_que_falham(ferramenta, palavras, usadas, uso(texto))


def formas_que_falham(ferramenta, palavras, usadas, texto_uso):
    """E96.1: formas aceitas pelo --help que os agentes relataram erradas. `--vermelho` sem `--modulos` pode rodar a suíte
    toda; a spec do `forge-mutante` vai pelo caminho em tests/mutantes/, não pelo nome do pedido."""
    if ferramenta == "testes" and "--vermelho" in usadas and "--modulos" not in usadas:
        return ["--vermelho sem --modulos"]
    if ferramenta != "mutante":
        return []
    com_valor = set(re.findall(r"(--[a-z][a-z0-9-]*) [A-Z]", texto_uso))
    soltas = [p for i, p in enumerate(palavras) if not p.startswith("-") and (i == 0 or palavras[i - 1] not in com_valor)]
    return [f"spec fora de tests/mutantes/: {p}" for p in soltas if not p.startswith("tests/mutantes/")]


def citacoes(texto):
    """(linha, ferramenta, palavras depois dela) de cada comando do Forge entre crases."""
    for n, linha in enumerate(texto.splitlines(), 1):
        for trecho in CRASE.findall(linha):
            achou = FERRAMENTA.search(trecho)
            if achou:
                yield n, achou.group(1), trecho[achou.end():].split()


def arquivos_tocados():
    return sorted(p for pasta in PASTAS for p in (RAIZ / "skills" / pasta).glob("*.md"))


class TestComandoPronto(unittest.TestCase):
    def test_skills_tocadas_citam_comando_pronto(self):
        achados, total, excecoes_usadas = [], 0, set()
        for arq in arquivos_tocados():
            rel = arq.relative_to(RAIZ).as_posix()
            for n, ferramenta, resto in citacoes(arq.read_text(encoding="utf-8")):
                total += 1
                problemas = problemas_da_citacao(ferramenta, resto)
                chave = (rel, ferramenta, " ".join(resto[:2]))
                if chave in SEM_OBRIGATORIAS and all(p.startswith("falta ") for p in problemas):
                    excecoes_usadas.add(chave)
                    continue
                achados += [f"{rel}:{n} forge-{ferramenta}: {p}" for p in problemas]
        self.assertGreaterEqual(len(arquivos_tocados()), 5)
        self.assertGreaterEqual(total, 20, "a busca deixou de achar as citações")
        self.assertEqual(achados, [])
        self.assertEqual(excecoes_usadas, SEM_OBRIGATORIAS, "exceção sem uso: tire-a de SEM_OBRIGATORIAS")

    def test_ramos_de_falha(self):
        self.assertEqual(problemas_da_citacao("check", []), ["sem subcomando"])
        self.assertEqual(problemas_da_citacao("check", ["inexistente"]), ["sem subcomando"])
        self.assertEqual(problemas_da_citacao("changelog", ["--base", "x"]), ["sem subcomando"])
        self.assertEqual(problemas_da_citacao("fechar", []), ["sem argumento nem opção"])
        self.assertEqual(problemas_da_citacao("fechar", ["<pedido>"]), ["falta --ref"])
        self.assertEqual(problemas_da_citacao("mutante", ["--inventada"]), ["opção --inventada não existe no --help"])
        self.assertIn("falta --tipo", problemas_da_citacao("check", ["anotar", "--pedido", "<p>", "--literal", "<t>"]))
        self.assertIn("falta --nota", problemas_da_citacao("check", ["escape", "registrar", "--pedido", "<p>"]))
        self.assertEqual(problemas_da_citacao("check", ["pausa"]), ["falta --gravar ou --retomar"])
        self.assertEqual(problemas_da_citacao("check", ["pausa", "--retomar", "--esperar"]), [])
        self.assertEqual(problemas_da_citacao("fechar", ["<pedido>", "--ref", "<branch>", "--sem-limpar"]), [])
        self.assertEqual(problemas_da_citacao("testes", ["--vermelho", "<base>"]), ["--vermelho sem --modulos"])
        self.assertEqual(problemas_da_citacao("testes", ["--vermelho", "<base>", "--modulos", "test_x"]), [])
        self.assertEqual(problemas_da_citacao("mutante", ["<pedido>"]), ["spec fora de tests/mutantes/: <pedido>"])
        self.assertEqual(problemas_da_citacao("mutante", ["--base", "<sha>", "tests/mutantes/<p>.json"]), [])
        self.assertEqual(problemas_da_citacao("mutante", ["--cobertura", "--base", "<Base-sha>"]), [])

    def test_citacoes_acha_so_entre_crases(self):
        texto = "rode forge-check solto e `bin/forge-fechar` e `${CLAUDE_PLUGIN_ROOT}/bin/forge-check classe` e `forge-checks x`"
        self.assertEqual(list(citacoes(texto)), [(1, "fechar", []), (1, "check", ["classe"])])


if __name__ == "__main__":
    unittest.main()
