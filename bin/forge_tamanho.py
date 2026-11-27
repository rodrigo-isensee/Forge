"""Forge: os avisos de tamanho do `forge-check pr` e do `brief gerar` (H1-TETO-DE-TAMANHO-POR-ITEM e PEDIDO-TETO-BRIEF, v0474 E2.13).

Decisão do dono (17/11 11:15): até 150 linhas de código por item; testes e documentação não contam; passa do teto só quando cortar
mais quebra a suíte, com o motivo no corpo do PR, na linha `teto: excedido, <n> linhas, <motivo>` (a forma do M14). O pedido com mais
de cerca de 50 etapas e o brief perto do teto de caracteres só avisam. Só biblioteca padrão; não usa nada do forge-check (quem chama
passa a classificação de código, `e_codigo`).
"""
import re

TETO_DE_LINHAS_DE_CODIGO = 150
TETO_DE_ETAPAS = 50
MARGEM_DO_BRIEF = 0.8  # avisa (e o `brief gerar` arquiva as etapas fechadas) a partir de 80% do teto, antes de o selar recusar
LINHA_DE_MOTIVO = re.compile(r"^[ \t]*(?:[-*][ \t]+)?teto: excedido, (\d+) linhas, [ \t]*\S", re.M)
ORIGEM = "H1, decisão do dono 17/11 11:15"
CORTE_A_MAO = "cortar à mão (uma classe de comportamento por PR em hooks/, H1)"
PRS_NO_TEXTO = 6
CABECALHO_DO_TRECHO = re.compile(r"^@@ -\d+(?:,(\d+))? \+\d+(?:,(\d+))? @@ ?(.*)$", re.M)


def linhas_de_codigo(contagens, e_codigo):
    """Acrescentadas mais removidas dos arquivos de código de `contagens` ({arquivo: (mais, menos)} do `--numstat`); o binário (`-`)
    não tem linha e não conta."""
    total = 0
    for nome, (mais, menos) in contagens.items():
        if e_codigo(nome) and mais.isdigit() and menos.isdigit():
            total += int(mais) + int(menos)
    return total


def aviso_de_linhas(total):
    """A linha `tamanho:` do item acima do teto, ou None."""
    if total <= TETO_DE_LINHAS_DE_CODIGO:
        return None
    return (f"tamanho: {total} linhas de código, acima do teto de {TETO_DE_LINHAS_DE_CODIGO} por item (testes e documentação não "
            f"contam; {ORIGEM}): corte o item; passe só se cortar mais quebrar a suíte, com `teto: excedido, {total} linhas, "
            "<motivo>` no corpo do PR")


def tem_motivo(corpo, total=0):
    """True se o corpo do PR tem a linha `teto: excedido, <n> linhas, <motivo>` com motivo não vazio e `<n>` de pelo menos `total`
    (o número declarado cobre o tamanho medido: a linha de um item menor não libera o item que cresceu)."""
    return any(int(m.group(1)) >= total for m in LINHA_DE_MOTIVO.finditer(corpo or ""))


def falta_de_motivo(total, corpo, numero):
    """A violação do `pr` quando o item passa do teto e o corpo do PR `numero` não traz o motivo, ou None."""
    if total <= TETO_DE_LINHAS_DE_CODIGO or tem_motivo(corpo, total):
        return None
    return (f"pr: tamanho: {total} linhas de código acima do teto de {TETO_DE_LINHAS_DE_CODIGO} sem a linha "
            f"`teto: excedido, {total} linhas, <motivo>` no corpo do PR #{numero} ({ORIGEM})")


def linhas_por_funcao(diff):
    """{contexto: linhas} do `git diff -U0` de um arquivo (F5, v0481 E38.2): o contexto é o do cabeçalho `@@ -a,b +c,d @@ <contexto>`
    (a linha `def`/`class` de cima mais próxima, sem os argumentos); as linhas, `b + d` dos trechos dele; sem contexto, `topo`."""
    funcoes = {}
    for menos, mais, contexto in CABECALHO_DO_TRECHO.findall(diff):
        nome = contexto.split("(")[0].strip() or "topo"
        funcoes[nome] = funcoes.get(nome, 0) + int(menos or 1) + int(mais or 1)
    return funcoes


def corte_sugerido(unidades, teto=TETO_DE_LINHAS_DE_CODIGO):
    """O corte do item em PRs de até `teto` linhas (F5): `unidades` [(nome, linhas)], da maior para a menor (empate pelo nome), cada uma
    no primeiro PR em que cabe; a que sozinha passa do teto vira PR próprio marcado `CORTE_A_MAO`. Devolve [(total, [(nome, linhas)])]."""
    prs = []
    for nome, linhas in sorted(unidades, key=lambda u: (-u[1], u[0])):
        pr = next((p for p in prs if p[0] + linhas <= teto), None)
        if pr is None:
            pr = [0, []]
            prs.append(pr)
            nome = f"{nome}: {CORTE_A_MAO}" if linhas > teto else nome
        pr[0] += linhas
        pr[1].append((nome, linhas))
    return [(total, partes) for total, partes in prs]


def texto_do_corte(corte, maximo=PRS_NO_TEXTO):
    """A linha `corte sugerido: PR 1 (148): bin/a 90, ...` com até `maximo` PRs e `e mais N` no resto."""
    prs = "; ".join(f"PR {i} ({total}): " + ", ".join(f"{nome} {linhas}" for nome, linhas in partes)
                    for i, (total, partes) in enumerate(corte[:maximo], 1))
    resto = f"; e mais {len(corte) - maximo}" if len(corte) > maximo else ""
    return f"corte sugerido: {prs}{resto} (os testes de cada parte vão junto dela)"


def recusa_de_abertura(total, corte, corpo):
    """A recusa da abertura do PR com `total` linhas de código acima do teto sem a exceção do H1 no `corpo`, com os dois primeiros PRs
    do `corte` (None: o cálculo falhou, a recusa sai sem ele), ou None (F5)."""
    if tem_motivo(corpo, total) or total <= TETO_DE_LINHAS_DE_CODIGO:
        return None
    sugestao = f"; {texto_do_corte(corte, 2)}; o corte inteiro: forge-check pr <pedido> --previo" if corte else ""
    return (f"R-REVIEW: {total} linhas de código acima do teto de {TETO_DE_LINHAS_DE_CODIGO} por item ({ORIGEM}){sugestao}; ou "
            f"`teto: excedido, {total} linhas, <motivo>` no corpo do PR")


def aviso_de_etapas(quantas):
    """O aviso do `brief gerar` para o pedido com mais de `TETO_DE_ETAPAS` etapas, ou None."""
    if quantas <= TETO_DE_ETAPAS:
        return None
    return (f"o pedido tem {quantas} etapas, acima de cerca de {TETO_DE_ETAPAS} (H1): feche-o e abra o pedido de "
            "continuação, um por versão ou tema, com as etapas abertas")


def aviso_de_caracteres(quantos, teto):
    """O aviso do `brief gerar` para o brief com 80% ou mais do `teto` de caracteres, ou None (PEDIDO-TETO-BRIEF; o
    `brief gerar` arquiva as etapas fechadas nessa margem e só avisa se o brief segue nela, PEDIDO-ARQUIVA-SOZINHO)."""
    if quantos < int(teto * MARGEM_DO_BRIEF):
        return None
    return (f"o brief tem {quantos} caracteres, perto do teto de {teto} (o selar recusa acima dele) mesmo sem as etapas fechadas: "
            "abra o pedido de continuação com as etapas abertas, que encurta o Fora do escopo (PEDIDO-TETO-BRIEF)")
