---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-placar-fases
commit: 2343148728af2cf625c63ac236290daa2344d29b
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 E20.2 (melhoria/v0479-placar-fases, head 23431487)

Escopo: `forge-placar fases` (META85-PLACAR-RODADA-E-FASE) e `forge-placar --prs` (PLACAR-SEM-TESTE-POR-SEMANA), contra a ordem do dono de 18/11 17:00 e 17:05 (`docs/pedidos/v0478.md`, Histórico 2026-11-18 17:02 e 17:03).

## Achados
- A1 (bloqueante) bin/forge-placar:580 · requisito: fases só lê merge de dois pais, e o forge-fechar mescla na develop com --squash (bin/forge-fechar:167); em 18/11 vê 4 de 28 itens e diz "total do dia: 4 itens" sem avisar. A ordem pede tempo por fase e 1.ª rodada por item, todo dia, em todo projeto (R-NEUTRO).

## Sondas
- S1 · `bin/forge-placar fases --git . --ref origin/develop --dia 2026-11-18` no clone (origin/develop 2904a68a) · espera: os itens mesclados no dia (28 commits na linha principal) · obtido: "total do dia: 4 itens"; `git log --first-parent --format=%p` do dia dá 2 pais: 4, 1 pai: 24

## Parecer
Reprovado por A1. A definição das fases confere com a ordem do dono: desenvolvimento, pareceres, voltas e integração somam o tempo do 1.º commit ao merge (a medida de 169 min, com 33 de desenvolvimento e 130 em pareceres e voltas), e a 1.ª rodada lê a primeira versão de cada parecer (`parecer:` dos modelos de `templates/projeto/docs/*/_modelo.md`); nada de projeto específico, as pastas são as do modelo (R-NEUTRO).

O defeito é de alcance: o método de merge que o próprio fluxo usa (`forge-fechar`, passo 6, `--squash` na develop) apaga a linha de commits do item, e o comando conta só os merges manuais. A medida que o dono pediu fica com 14% dos itens e a média sai enviesada, sem aviso. Correção de lógica, do autor; caminhos possíveis: reconhecer o commit de squash pelo `(#N)` do assunto e ler os commits do item em `refs/pull/N/head` (trazidos fora, como o `--prs`), ou ao menos contar e mostrar os itens sem fases ("itens sem fases (squash): N") em vez de omiti-los, com teste de um merge por squash.

`--prs` (Sem teste por semana): correto; janela das duas semanas, `mergedAt` nulo e corpo nulo cobertos.

Ferramentas e provas: testes novos `Fases` e `SemTeste` rodados no head, 12 OK; `bin/forge-mutante tests/mutantes/v0479-placar-fases-5.json`: M32 e M33 morreram. Suíte inteira: fica no CI do PR (sem suíte local, pelo brief).
