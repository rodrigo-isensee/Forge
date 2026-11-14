"""L51 (AQ-8): o texto do Jarvis é o núcleo `agents/jarvis.md` mais as skills para onde o texto longo se mudou. Os testes que
conferem uma frase do Jarvis leem os dois: a frase segue exigida, só mudou de arquivo.

Folga do texto do Jarvis (v047, P4; diretriz 25 do dono): o conjunto do Jarvis é calculado, não uma lista fixa. Entram o
`agents/jarvis.md`, as skills que ele cita (pelo caminho `${CLAUDE_PLUGIN_ROOT}/skills/<x>/SKILL.md` ou pelo nome entre crases,
`` `x` `` ou `` `forge:x` ``, em que `x` é pasta de `skills/`) e as que essas citam (um nível a mais), os `docs/*.md` citados
pelo caminho e o texto de cada regra com ID citada entre crases."""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILLS_DO_JARVIS = ("briefs-e-conferencia", "trabalho-em-paralelo", "falar-com-o-dono", "fluxo-do-pedido")
JARVIS = "agents/jarvis.md"
SKILL_PELO_CAMINHO = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/skills/([a-z0-9-]+)/SKILL\.md")
SKILL_PELO_NOME = re.compile(r"`(?:forge:)?([a-z0-9-]+)`")
ID_ENTRE_CRASES = re.compile(r"`(R-[A-Z]+)`")
ID_DA_TABELA = re.compile(r"^\| \[?`(R-[A-Z]+)`", re.M)
DOC_CITADO = re.compile(r"\bdocs/[a-z0-9-]+\.md\b")
INDICE_DAS_REGRAS = "docs/regras/README.md"  # a tabela dos IDs e a linha da R-WIP (regra só de hook)
ORDEM_DE_LEITURA = re.compile(r"\bleia\b|\bantes de\b", re.I)
TRECHO_MINIMO = 20


def texto_do_jarvis(raiz=RAIZ):
    arquivos = [raiz / "agents" / "jarvis.md"] + [raiz / "skills" / nome / "SKILL.md" for nome in SKILLS_DO_JARVIS]
    return "\n".join(a.read_text(encoding="utf-8") for a in arquivos)


def skills_citadas(texto, raiz=RAIZ):
    """Nomes das pastas de `skills/` que o texto cita pelo caminho do plugin ou pelo nome entre crases."""
    nomes = set(SKILL_PELO_CAMINHO.findall(texto)) | set(SKILL_PELO_NOME.findall(texto))
    return {n for n in nomes if (raiz / "skills" / n / "SKILL.md").is_file()}


def arquivo_da_regra(raiz, rid):
    """Onde mora o texto da regra: `docs/regras/<rid>.md`, o trecho `## <rid>: ` de R-LIMITES.md ou a linha `**`<rid>``
    do índice das regras (R-WIP, regra só de hook); None se não há texto."""
    regras = raiz / "docs" / "regras"
    if (regras / f"{rid}.md").is_file():
        return f"docs/regras/{rid}.md"
    for rel, marca in (("docs/regras/R-LIMITES.md", f"\n## {rid}: "), (INDICE_DAS_REGRAS, f"\n**`{rid}`")):
        if (raiz / rel).is_file() and marca in (raiz / rel).read_text(encoding="utf-8"):
            return rel
    return None


def conjunto_do_jarvis(raiz=RAIZ):
    """{caminho relativo: texto} do que o Jarvis lê ou é mandado ler (docstring do módulo)."""
    def ler(rel):
        return (raiz / rel).read_text(encoding="utf-8")
    textos = {JARVIS: ler(JARVIS)}
    nivel1 = skills_citadas(textos[JARVIS], raiz)
    nivel2 = set().union(*(skills_citadas(ler(f"skills/{s}/SKILL.md"), raiz) for s in nivel1))
    for nome in sorted(nivel1 | nivel2):
        textos[f"skills/{nome}/SKILL.md"] = ler(f"skills/{nome}/SKILL.md")
    juntos = "\n".join(textos.values())
    for doc in sorted(set(DOC_CITADO.findall(juntos))):
        if (raiz / doc).is_file():
            textos[doc] = ler(doc)
    for rid in sorted(set(ID_ENTRE_CRASES.findall(juntos))):
        arq = arquivo_da_regra(raiz, rid)
        if arq:
            textos[arq] = ler(arq)
    return textos


def skills_sem_ordem_de_leitura(raiz=RAIZ):
    """As skills que o Jarvis cita sem uma linha dele que a cite com "leia" ou "antes de" (a forma da diretriz 25). O nível a
    mais (skill citada por skill) conta para a presença, não para a ordem de leitura."""
    jarvis = (raiz / JARVIS).read_text(encoding="utf-8")
    linhas = jarvis.splitlines()
    return sorted(nome for nome in skills_citadas(jarvis, raiz)
                  if not any(nome in skills_citadas(linha, raiz) and ORDEM_DE_LEITURA.search(linha) for linha in linhas))


def ids_da_tabela(raiz=RAIZ):
    return ID_DA_TABELA.findall((raiz / INDICE_DAS_REGRAS).read_text(encoding="utf-8"))


def problemas_das_regras(raiz, conjunto):
    """Cada ID da tabela do índice das regras aparece entre crases no conjunto e tem texto em docs/regras/."""
    juntos = "\n".join(conjunto.values())
    problemas = []
    for rid in ids_da_tabela(raiz):
        if f"`{rid}`" not in juntos:
            problemas.append(f"{rid}: não aparece no Jarvis nem nas skills citadas")
        if arquivo_da_regra(raiz, rid) is None:
            problemas.append(f"{rid}: sem texto em docs/regras/")
    return problemas


def _achados(trechos, conjunto):
    return [t for t in trechos if len(t) >= TRECHO_MINIMO and any(re.search(t, texto, re.S) for texto in conjunto.values())]


def problemas_das_diretrizes(tabela, conjunto, max_pendentes, numeros_do_dono=()):
    """A tabela neutra das diretrizes (tests/fixtures/diretrizes-do-dono.json) contra o conjunto do Jarvis: numeração de 1 a N
    sem buraco; `fabrica` com trechos de 20+ caracteres achados no conjunto; `sessao` com motivo; `pendente` com cartão e sem
    trecho já presente; no máximo `max_pendentes` pendentes; cada número do arquivo do dono com entrada."""
    numeros = sorted(int(n) for n in tabela)
    problemas = [f"diretriz {n}: buraco na numeração" for n in range(1, max(numeros, default=0) + 1) if n not in numeros]
    lista = ", ".join(sorted(conjunto))
    for n in numeros:
        entrada, onde = tabela[str(n)], tabela[str(n)].get("onde")
        trechos = entrada.get("trechos", [])
        problemas += [f"diretriz {n}: trecho com menos de {TRECHO_MINIMO} caracteres: '{t}'" for t in trechos if len(t) < TRECHO_MINIMO]
        achados = _achados(trechos, conjunto)
        if onde == "fabrica":
            problemas += [f"diretriz {n}: de fábrica sem trecho"] if not trechos else []
            problemas += [f"diretriz {n}: '{t}' não está em agents/jarvis.md nem nas skills que ele manda ler ({lista}); não apague "
                          "(diretriz 25): leve o trecho a uma skill citada com 'leia ... antes de', ou cite a skill no Jarvis"
                          for t in trechos if len(t) >= TRECHO_MINIMO and t not in achados]
        elif onde == "sessao":
            problemas += [f"diretriz {n}: de sessão sem motivo"] if len(entrada.get("motivo", "")) < TRECHO_MINIMO else []
        elif onde == "pendente":
            problemas += [f"diretriz {n}: pendente sem cartão"] if not re.fullmatch(r"[A-Z0-9][A-Z0-9-]+", entrada.get("cartao", "")) else []
            problemas += [f"diretriz {n}: pendente com o trecho '{t}' já presente; passe a fabrica" for t in achados]
        else:
            problemas.append(f"diretriz {n}: onde = {onde!r}, esperava fabrica, sessao ou pendente")
    pendentes = sum(1 for e in tabela.values() if e.get("onde") == "pendente")
    if pendentes > max_pendentes:
        problemas.append(f"{pendentes} diretrizes pendentes, máximo {max_pendentes}: pendente só desce")
    problemas += [f"diretriz {n} do arquivo do dono sem entrada" for n in sorted(set(numeros_do_dono) - set(numeros))]
    return problemas
