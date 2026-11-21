---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp9-guia
commit: e266490b885f01366dfd6abb80ef65950ffa90e5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E24.23, MP9 guia "vários projetos", revalidação após o merge da develop)

Revalidação (H3, R-REVIEW) do parecer aprovado no head 862d9ecb. Delta lido: `forge-check parecer delta docs/reviews/v0479-mp9-guia.md`, intervalo `862d9ecb..e266490b` (merge da develop 65a3f0a9); no domínio `README.md`, `bin/forge-testes`, `tests/pesos-d4.json` e `tests/test_reval_delta.py`.

- Os dois conflitos de lista (`bin/forge-testes`, `LEITORES_DE_TEXTO`; `tests/test_reval_delta.py`, `CITACOES_CONHECIDAS`) ficaram com os dois itens: `test_guia_varios_projetos` e `test_retro_pendentes` em `LEITORES_DE_TEXTO`; a citação do guia ao lado das da develop (`test_retro_pendentes`, `bin/forge_comparar.py`, `test_forge` em 16). Conferido: `git diff 65a3f0a9 e266490b` nesses quatro arquivos mostra só as linhas da branch (guia no README, módulo no mapa do `README.md`, peso 0.1, uma citação); o resto do delta é a develop.
- Sem guarda mudada; teto H1 não se aplica.

`docs/engineering/praticas.md` sem regra "decidida por: leitura" que alcance o delta. Suíte: só no CI do PR (R-REVIEW). Rodados: `python3 -m unittest test_testes_tocados test_reval_delta` (em `tests/`), 206 testes, OK (1 pulado); `bin/forge-testes --registros --base origin/develop`, rc=0 (9 conferências).

## Parecer
Aprovado no head e266490b.
