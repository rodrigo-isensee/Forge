---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-k170-movimento
commit: 0000c1bfedc51ec787fc29791f385e85b33bf3e4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (K170, E77.2)

Escopo lido: `bin/forge-check` (`movimentos_do_cartao`, `sem_entrada_em_bloqueado`, `cmd_movimento`, `executar`), `tests/test_sobreposicao_quadro.py` (`MovimentoDeBloqueado`), `tests/mutantes/v0478-k170-movimento.json`, `changelog.d/v0479-k170-movimento.md`. Base 5e3ca873.

## Achados
- A1 (recomendado) bin/forge-check:4810 · Cartão já em Bloqueado sem a linha de entrada (legado): a dica `--de <coluna atual> --para Bloqueado` com a coluna atual (Bloqueado) também recusa (rc 2, reproduzido); dizer `--de <coluna anterior>` ou aceitar `--de Bloqueado --para Bloqueado` como registro da entrada.

## Parecer
Aprovado. Faz o que o K170 pede: `--de Bloqueado` sem a última linha do cartão em Bloqueado recusa com rc 2, antes de qualquer escrita (o arquivo nem é criado), e as outras origens seguem sem a conferência. A extração de `movimentos_do_cartao` mantém o comportamento de `custo_do_movimento` (mesma expressão). A recusa tem prefixo próprio (`MOVIMENTO_RECUSADO`) e o `executar` a separa do erro de uso (rc 1). Guardas com um mutante por linha (M1 a M6) e teste do ramo de falha por comportamento, em subprocesso com ambiente limpo e `-I`; o caso de outro cartão em Bloqueado e o de entrada já fechada (caixa e acento) estão cobertos. Teto H1: cerca de 30 linhas de código. Suíte inteira: fica no CI do PR (`R-REVIEW`).

Rodado no head 0000c1bf: `tests.test_sobreposicao_quadro` e `tests.test_fechar_move_cartao` (77 testes, OK); `tests.test_forge -k SaidaSanitizada` (10 testes, OK). Sonda do A1: `movimento K-9 --de Bloqueado --para Bloqueado` num quadro sem histórico deu rc 2 e não criou `docs/`.
