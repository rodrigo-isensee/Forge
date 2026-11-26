---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 22a57afc418542f52f1e306f0ddc4e51ed213f57
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E7.57, #888, revalidação por delta, 5ª volta)

Gatilhos: hook de bloqueio (`hooks/_comum.py`: `prazo_vencido`), R-REVIEW, R-CONFORMIDADE, R-QA (mutantes).

## Resumo
- Delta lido: `git diff ecb13af6..22a57afc` e `forge-check parecer delta`, que dá "revalida: não" (sem o que veio da develop, o domínio não mudou). O delta tem dois merges da develop e os três pareceres da rodada anterior:
  - `ad212884` (develop `8f0a7313`): `git show --remerge-diff` vazio, ou seja, merge limpo e sem resolução manual;
  - `22a57afc` (develop `020e4af7`): `--remerge-diff` mostra só o conflito em `docs/hooks-fixtures.md`, resolvido pela linha gerada com 3594 fixtures. `scripts/indice-fixtures.py --conferir` responde "em dia". `tests/hooks/*/*.json` conta 3594 arquivos. `tests.test_indice_fixtures` passou (7 testes).
- A develop entrou igual. Os arquivos fora do item são idênticos aos de `020e4af7`, porque não aparecem em `git diff 020e4af7 22a57afc`. A lista de arquivos de `git diff 020e4af7 22a57afc` é a mesma de `git diff 34ab6714 14161c3c`, que é o item revisado sobre a base anterior. Comparei as linhas `+`/`-` arquivo a arquivo e todas são iguais, inclusive em `hooks/_comum.py`, `hooks/conformidade.py` e `tests/test_hooks.py`. A única diferença está em `docs/hooks-fixtures.md`, que é o índice gerado. Nenhuma linha de controle foi escrita na resolução.
- **O que aperta:** nada neste delta.
- **O que é neutro:** o delta inteiro. O índice é gerado, os merges não escrevem código e o conteúdo da develop já foi revisado nos PRs de origem. As duas falhas locais por prazo de 120 s (`pesado`/`mesma-sessao-libera`, sob carga, que passam isoladas) não vêm do delta, porque o código do item é idêntico ao já aprovado.
- **O que afrouxa:** nada novo. O afrouxamento na margem, já aceito pelo dono em 25/11 às 21:15, segue como estava em `ecb13af6`: as travas de recurso desistem mais cedo sob carga, e as travas de segurança continuam recusando.
- **Achados anteriores:** A3, A6 e A7 continuam resolvidos (`4ab16b74`). A isenção de `:2875(base)` continua atendida (`ecb13af6`), sem mudança.
- **CI** no head `22a57afc` (run 45809714839, `pull_request`):
  - verdes: `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)` e `árvore já provada na develop`;
  - vermelho `bateria (pareceres)`: o log diz R-REVIEW, porque o parecer de review ficou desatualizado pela regeneração de `docs/hooks-fixtures.md`. Os pareceres desta volta resolvem isso;
  - vermelho `catraca` (run 45809714849): o log diz R-CONFORMIDADE em `hooks/_comum.py` e `hooks/conformidade.py`, que pedem o rótulo `afrouxa-regra` do dono depois do último push. É um passo do dono, não um defeito;
  - suíte: as 10 partes não terminaram no head revisado. O push do parecer de QA (`bdc4fdce`) cancelou a parte 3.12 5/5, e as outras seguiam em andamento.

  Por isso este parecer não grava a linha `ci:`. A suíte vale pelo CI do head final da branch.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas: `forge-check parecer delta`, `git show --remerge-diff`, `git diff` arquivo a arquivo (md5 das linhas `+`/`-`), `scripts/indice-fixtures.py --conferir`, o unittest `tests.test_indice_fixtures` e `gh api` (check-runs e logs dos jobs). Não usei nada externo. O delta não traz dependência nem segredo.
