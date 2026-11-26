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
