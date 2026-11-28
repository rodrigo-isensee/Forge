"""S1 (0.44.1): métricas do texto de instrução com teto que só desce, em agents/jarvis.md, docs/regras/R-*.md e skills/*/SKILL.md.

Por arquivo: caracteres, palavras da frase mais longa e média de palavras por frase (x10), linhas de prosa com mais de 100 colunas,
tamanho da `description:` do cabeçalho e ocorrências de sinônimo proibido (um conceito, um nome: dono, cartão, revisor). Prosa é o
arquivo sem o cabeçalho, os blocos cercados, as tabelas e os títulos; item de lista abre frase. A linha de base fica em
tests/fixtures/metricas-texto.json: medida acima do teto reprova. `python3 tests/test_metricas_texto.py --gravar` baixa os tetos
para a medida atual e acrescenta os arquivos novos; nunca sobe um teto (subir é afrouxar: edite o arquivo e diga no PR).
Folga do texto do Jarvis (v047, P3; diretriz 25): no que o Jarvis lê ou é mandado ler, a mensagem manda mover, não reduzir."""
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_jarvis import conjunto_do_jarvis  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
LINHA_DE_BASE = RAIZ / "tests" / "fixtures" / "metricas-texto.json"
SINONIMOS = {"dono": ("owner", "proprietário", "chefe"), "cartão": ("card", "ticket", "task"), "revisor": ("reviewer",),
             "pull request": ("pull-request",)}
PROIBIDO = re.compile(r"(?<!\w)(" + "|".join(s for lista in SINONIMOS.values() for s in lista) + r")(?!\w)", re.I)
CERCA = re.compile(r"^```.*?^```", re.S | re.M)
CABECALHO = re.compile(r"\A---\n(.*?)\n---\n", re.S)
FIM_DE_FRASE = re.compile(r"(?<=[.;!?])\s+(?=[A-ZÀ-Ú`*\"(\[])")
ITEM = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")
COLUNAS = 100
METRICAS = ("caracteres", "frase_max", "frase_media_x10", "linhas_longas", "descricao", "sinonimos")
REDUZA = "reduza o texto; subir o teto é afrouxar"
MOVA = ("não apague nem resuma regra (diretriz 25): mova o detalhe para uma skill que o Jarvis manda ler e deixe o resumo; "
        "não suba o teto")


def arquivos(raiz=RAIZ):
    return sorted(["agents/jarvis.md"] + [p.relative_to(raiz).as_posix() for p in (raiz / "docs" / "regras").glob("R-*.md")]
                  + [p.relative_to(raiz).as_posix() for p in (raiz / "skills").glob("*/SKILL.md")])


def prosa(texto):
    """As linhas de prosa: sem cabeçalho, blocos cercados, tabelas e títulos; a linha vazia fica ("") e separa parágrafos."""
    texto = CERCA.sub("", CABECALHO.sub("", texto))
    return ["" if l.lstrip().startswith(("|", "#")) else l.rstrip() for l in texto.splitlines()]


def frases(linhas):
    """Palavras de cada frase; o item de lista e o parágrafo abrem frase nova."""
    blocos, atual = [], []
    for linha in linhas:
        if (ITEM.match(linha) or not linha.strip()) and atual:
            blocos.append(" ".join(atual))
            atual = []
        atual += [ITEM.sub("", linha).strip()] if linha.strip() else []
    blocos += [" ".join(atual)] if atual else []
    return [len(f.split()) for b in blocos for f in FIM_DE_FRASE.split(b) if f.strip()]


def medir(texto):
    linhas, cabecalho = prosa(texto), CABECALHO.match(texto)
    palavras = frases(linhas)
    descricao = re.search(r"^description:\s*(.*)$", cabecalho.group(1), re.M) if cabecalho else None
    return {"caracteres": len(texto), "frase_max": max(palavras, default=0),
            "frase_media_x10": round(10 * sum(palavras) / len(palavras)) if palavras else 0,
            "linhas_longas": sum(1 for l in linhas if len(l) > COLUNAS), "descricao": len(descricao.group(1)) if descricao else 0,
            "sinonimos": len(PROIBIDO.findall("\n".join(linhas)))}


def medidas(raiz=RAIZ):
    return {rel: medir((raiz / rel).read_text(encoding="utf-8")) for rel in arquivos(raiz)}


def estouros(medido, tetos, do_jarvis=frozenset()):
    """Uma linha por arquivo sem linha de base e por métrica acima do teto; no arquivo de `do_jarvis`, a mensagem manda mover."""
    erros = [f"{rel}: sem linha de base (rode python3 tests/test_metricas_texto.py --gravar)" for rel in medido if rel not in tetos]
    return erros + [f"{rel}: {m} = {valores[m]} passa do teto {tetos[rel][m]} em {valores[m] - tetos[rel][m]} "
                    f"({MOVA if rel in do_jarvis else REDUZA})"
                    for rel, valores in medido.items() if rel in tetos for m in METRICAS if valores[m] > tetos[rel][m]]


def baixar(tetos, medido):
    """Os tetos novos: o menor entre o teto e a medida; arquivo novo entra com a medida; o que saiu da árvore sai."""
    return {rel: {m: min(tetos.get(rel, valores)[m], valores[m]) for m in METRICAS} for rel, valores in sorted(medido.items())}


class MetricasDoTexto(unittest.TestCase):
    def test_nenhuma_metrica_passa_do_teto(self):
        medido = medidas()
        self.assertGreaterEqual(len(medido), 30)
        self.assertEqual(estouros(medido, json.loads(LINHA_DE_BASE.read_text(encoding="utf-8")), set(conjunto_do_jarvis())), [])

    def test_o_teto_so_desce_e_a_medida_acusa_cada_metrica(self):
        texto = ("---\nname: x\ndescription: " + "d" * 30 + "\n---\n# Título\n\n- Um item curto. Outra frase aqui;\n"
                 "- " + "palavra " * 20 + "\n\n```\nnão conta owner\n```\n| tabela | owner |\n" + "y" * 101 + " o chefe e o Card.\n")
        m = medir(texto)
        self.assertEqual((m["descricao"], m["linhas_longas"], m["sinonimos"], m["frase_max"]), (30, 2, 2, 20))
        self.assertEqual(m["frase_media_x10"], round(10 * (3 + 3 + 20 + 6) / 4))
        tetos = {"a.md": dict(m, caracteres=10), "c.md": dict(m)}
        self.assertEqual(estouros({"a.md": m}, tetos), [f"a.md: caracteres = {len(texto)} passa do teto 10 em {len(texto) - 10} "
                                                        "(reduza o texto; subir o teto é afrouxar)"])
        self.assertEqual(estouros({"a.md": m}, tetos, {"a.md"}), [f"a.md: caracteres = {len(texto)} passa do teto 10 em {len(texto) - 10}"
                                                                  f" ({MOVA})"])
        self.assertIn("b.md: sem linha de base", estouros({"b.md": m}, tetos)[0])
        novos = baixar(tetos, {"a.md": dict(m, sinonimos=0), "b.md": m})
        self.assertEqual(novos["a.md"]["caracteres"], 10, "o teto nunca sobe")
        self.assertEqual(novos["a.md"]["sinonimos"], 0, "a medida menor baixa o teto")
        self.assertEqual(novos["b.md"], m)
        self.assertNotIn("c.md", novos)


if __name__ == "__main__":
    if sys.argv[1:] == ["--gravar"]:
        atuais = json.loads(LINHA_DE_BASE.read_text(encoding="utf-8")) if LINHA_DE_BASE.is_file() else {}
        LINHA_DE_BASE.write_text(json.dumps(baixar(atuais, medidas()), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"linha de base gravada em {LINHA_DE_BASE.relative_to(RAIZ)}")
    else:
        unittest.main()
