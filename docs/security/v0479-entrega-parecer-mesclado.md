---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: 39351c755290a37abf829fedb17fe65744183491
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: índice das fixtures e teto do corpus +1084 (v0478 E50.29, revalidação)

Delta lido (`forge-check parecer delta`, `9f4c3ca3..39351c75`): nenhum arquivo do domínio mudou. Fora do domínio: `docs/hooks-fixtures.md`, `tests/apoio_volta_unica.py` e `tests/provas/v0479-corpus-custo.md`, lidos inteiros no diff. O resto do delta são os pareceres de review, QA e segurança da rodada anterior. A rodada anterior está no git (`21c9594c`, parecer no `9f4c3ca3`).

Gatilhos: controle do Forge (`bin/forge-check entrega`, hook `conformidade`), afrouxa-regra com condições do dono (DECISÃO DO DONO 2026-11-20 10:59, 13:21, 17:29, 17:31 e 19:09).

## Detalhe

**O delta não toca hook nem a barreira aprovada.** `git diff --quiet 9f4c3ca3 39351c75 -- hooks tests/hooks bin .githooks scripts .github` dá rc 0. O blob de `hooks/conformidade.py` no head (`927f99f7`) é o mesmo do `5376b86d`, onde a barreira de papel nas pastas de parecer foi aprovada. O blob de `bin/forge-check` (`accb8cb1`) é o mesmo do `9f4c3ca3`.

**Índice das fixtures.** `docs/hooks-fixtures.md` passa de 3097 para 3135 fixtures e ganha a linha `pp-*` (38 casos, `PARECER-PELO-PAPEL`). Nenhuma fixture mudou no delta: o índice só alcança o corpus que já estava na branch. `scripts/indice-fixtures.py --conferir`: "em dia", rc 0. Os 38 `pp-*` estão em `tests/hooks/conformidade/`.

**Teto do corpus (+1084 passos).** `tests/apoio_volta_unica.py:197` sobe `interpretador` de 5893967 para 5895051. O comentário cita a autorização do dono (19:09: só para este item e sem abrir precedente), e a prova está em `tests/provas/v0479-corpus-custo.md`. Execuções e subprocessos ficam iguais (557 e 4631), e o ruído continua 0. O teto é orçamento de custo, não controle de acesso. Os 1084 passos (0,02%) vêm do `hooks/conformidade.py` e do `forge-check` já revisados. Não há caminho de ataque: o aumento não libera entrada nenhuma e não muda o que o hook recusa. A medida segue exata, então um passo a mais reprova. `python3 -m unittest tests.test_hooks_volta_corpus` no head, nesta máquina: 33 testes, OK.

**Condições do dono.**
- (1) Os dois apertos (o parecer cita exatamente a versão revisada e cada tipo só vale na própria pasta) seguem no head, sem mudança.
- (2) Confirmo de novo, por escrito: na sessão do Forge, o autor do item não grava nas pastas de parecer, porque o hook barra pelo papel. O `hooks/conformidade.py` é o mesmo blob aprovado, e a matriz da rodada do `5376b86d` vale para ele: 720 casos, mais 102 da dimensão do A6.
- (3) O delta é neutro: índice gerado e orçamento de custo com autorização própria.

Achados anteriores (A1 a A6): seguem corrigidos, porque o patch de `bin/forge-check` e de `hooks/conformidade.py` não mudou.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

A suíte inteira fica com o CI do PR. Não conferi o CI em `39351c75`, porque o `gh` não lê credenciais no sandbox. O merge depende do CI verde.

Lacuna: gitleaks, semgrep, zizmor e actionlint estão fora do PATH. O delta não toca workflow nem dependência.
