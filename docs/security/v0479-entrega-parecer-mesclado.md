---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: 9f4c3ca37024789b7994296fc3f9716021b098af
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: merge da develop e teste antigo do parecer trazido (v0478 E50.22, revalidação)

Delta lido (`forge-check parecer delta`, `5376b86d..9f4c3ca3`): no domínio, `bin/forge-check`, `docs/hooks.md` e `tests/test_hooks.py`; fora, `tests/test_revisor_wt.py`. O que o delta traz nesses arquivos veio do merge da `develop` (`6f41c645`, base `20bbbd8d`): `checks_ruins`, `ci_verde_no_head` e `adiar_suite` são do #718 e seguintes, revisados nos PRs deles. O patch próprio da branch não mudou: as linhas `+/-` de `bin/forge-check`, `hooks/conformidade.py`, `tests/test_hooks.py`, `docs/hooks.md` e `tests/test_selo_e_entrega.py` contra a base são iguais byte a byte em `8a503799..5376b86d` e em `20bbbd8d..9f4c3ca3`. O único commit novo da branch é o `9f4c3ca3`, que só toca `tests/test_revisor_wt.py`. A rodada anterior está no git (`0f296462`, parecer no `5376b86d`).

Gatilhos: controle do Forge (`bin/forge-check entrega`, hook `conformidade`), afrouxa-regra com condições do dono (DECISÃO DO DONO 2026-11-20 10:59, 13:21, 17:29 e 17:31).

## Sondas
- S20 · `ParecerTrazido` (lançador de `tests/test_revisor_wt.py`), p2 mesclado, sem `autoria.jsonl`, Histórico com `parecer conferido` p2 e depois p1 (p2 superado) · espera: não sai `ok` · obtido: `escopo: fora (parecer não conferido ou superado) "docs/reviews/x.md"`
- S21 · contexto da S20, Histórico só com `parecer conferido` p1 (p2 nunca registrado) · espera: não sai `ok` · obtido: `escopo: fora (parecer não conferido ou superado)`, mais o merge não conferido

## Detalhe

**A pergunta do brief: o `tests/test_revisor_wt.py:315` cabe no afrouxamento declarado?** Sim, e não aceita nada a mais.
- O teste não muda o código. Ele só alinha a asserção ao `bin/forge-check` revisado no `5376b86d`, cujo patch é idêntico no head. A linha antiga (`confira`) descrevia a regra de antes do E50.1, e o teste quebraria com o código do E50.
- O caso do teste é o que o rótulo declara: o parecer do `tech-lead` num commit que muda só `docs/reviews/`, mesclado sem resolução à mão, com `commit:` igual ao `de` (`c1`; condição 1, `revisado != de`) e na própria pasta.
- O teste passa com mais do que o rótulo exige. Sem brief de codigo, `autores` fica vazio, e o E50.6 (A4) fecha a falha: o anexo só vale com o blob do último `parecer conferido` do Histórico (`parecer_trazido`), o registro do Jarvis. Tirar a autoria não abre caminho, porque a âncora passa a ser esse registro. S20 e S21 provam o lado negativo: sem o p2 como último conferido, a linha sai `fora`, mais dura que o `confira` antigo.
- `python3 -m unittest tests.test_revisor_wt.ParecerTrazido`: 4 testes, OK.

**Achados anteriores (A1 a A6).** Seguem corrigidos, porque o patch da branch não mudou: `revisado != de` e `commit_so_de_parecer` (fora de `docs/security/aceites/`) estão no head, e o merge da develop não toca essas linhas.

**Condições do dono.**
- (1) Os dois apertos seguem no head.
- (2) Confirmo de novo, por escrito, que o autor não grava nas pastas de parecer na sessão do Forge. O `hooks/conformidade.py` tem o mesmo patch do `5376b86d`, e a matriz da rodada anterior vale para ele (720 casos e mais 102 da dimensão do A6). O merge da develop não toca esse arquivo.
- (3) O delta só aperta ou é neutro. O que entrou da develop (`ci_verde_no_head`: parecer só conta com CI verde) soma exigência, e o teste novo não libera nada que o código revisado já não liberasse.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Suíte inteira: fica com o CI do PR. Não conferi o CI em `9f4c3ca3`, porque o `gh` não lê credenciais no sandbox; o merge depende do CI verde.

Lacuna: gitleaks, semgrep, zizmor e actionlint estão fora do PATH. O delta da branch não toca workflow nem dependência.
