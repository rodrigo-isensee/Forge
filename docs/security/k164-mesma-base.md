---
tipo: revisao-seguranca
contrato: 1
pedido: k164-mesma-base
branch: melhoria/k164-intervalo
commit: 8e8fe8daea2fb09a9926d7fcd48958772cbdb1a9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-30
---
# Review de segurança: k164-mesma-base (item E2, branch k164-intervalo)

## Gatilhos
Toca `bin/forge-check`, controle do Forge protegido (`R-SEGURANCA`). Diff de código: 2 linhas em `bin/forge-check` (a gramática `ACHADO` e um ramo `elif` em `achados_do_parecer`) e 15 de teste; um comportamento só, abaixo do teto da M14 (agents/tech-lead.md:19): cumpre a M14. Fora do diff: `hooks/parecer.py` não chama `achados_do_parecer`, sem mudança de superfície no hook.

## Achados
- A1 (recomendado) bin/forge-check:1283 · int() de intervalo com mais de 4300 dígitos levanta ValueError (traceback, saída 1); não passa achado, mas vira falha opaca em vez de erro de formato.

## Detalhe dos achados
Varredura da entrada `a-b` (executada com o analisador carregado do commit revisado): `3-5`, `5-5` e `0-0` aceitos; `9-3` (invertido), `3-`, `-3`, `3--5`, `3-5-7` e `a-b` recusados com erro, sem achado válido; o conferente `--incluir` copia o intervalo inteiro. Nenhum caminho deixa um achado passar sem ser lido: a regex é ancorada, a ordem recusa antes do teto de texto, e o id repetido segue pegando.

A1: evidência `bin/forge-check:1283`. Caminho de ataque: quem escreve um parecer põe `a.py:1-<5000 dígitos>`; `forge-check docs` e `brief gerar` morrem com ValueError (confirmado em fixture local). Falha fechada (a saída é diferente de zero e nada é aprovado), por isso só recomendação; a regressão é que a forma sem hífen e com dígitos longos antes era tratada como texto. Severidade baixa. Correção mínima: limitar os dígitos na regex (por exemplo até 9 por lado) ou comparar por tamanho e depois por texto, sem converter. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Sem risco aceito. Análise estática e execução local do analisador sobre fixtures; sem ferramenta externa necessária. Lacuna: o review da outra branch (k164-mesma-base) e o hook `hooks/parecer.py` não fazem parte deste commit.
