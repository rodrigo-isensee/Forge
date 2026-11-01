---
tipo: review
contrato: 1
pedido: release-0.31
branch: melhoria/release-031
commit: 0e67326671c6c1e9b42785920d44e5a7b6300dde
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-01
---
# Review: release-0.31

Escopo: o commit de release `0e67326` sobre a develop `91d6cc1` (`git diff 91d6cc1 0e67326`, um commit, 27 arquivos, +30 −50). Os itens da leva (E1, corte P-CORTE-031 = A) entraram na develop por PRs próprios, cada um com review, QA e, quando havia gatilho, segurança; este parecer julga só o commit de release (etapa E2.2).

## Achados
- A1 (recomendado) CHANGELOG.md:13 · capitalização desigual na seção 0.31.0: entradas que começam em minúscula (linhas 13 a 21 e 28 a 33) vêm assim dos fragmentos; vale uma checagem no `forge-changelog novo` para as próximas levas, sem mexer no texto já publicado.

## Parecer
Aprovado. Nenhum defeito provado, requisito descumprido nem achado de segurança com gatilho; o A1 é cosmético e não devolve (`R-REVIEW`).

- **Fragmentos:** `git ls-tree 91d6cc1 changelog.d/` lista 24 fragmentos; o commit apaga os 24 e `changelog.d/` fica vazio no HEAD. A seção `[0.31.0] - 2026-11-01` tem 24 entradas (3 em Alterado, 21 em Corrigido) e `[Não publicado]` segue vazio.
- **Reprodução:** extraí `91d6cc1` numa pasta temporária e rodei `bin/forge-changelog release 0.31.0 2026-11-01` (`[0.31.0]: 24 fragmento(s) juntado(s) e apagado(s)`); `cmp` deu `CHANGELOG.md`, `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` idênticos aos do `0e67326`. O commit é exatamente a saída da ferramenta.
- **Manifestos:** os dois dizem 0.31.0 (0.30.8 → 0.31.0, minor, como pede o pedido). O `dev/.claude-plugin/plugin.json` entra pela DECISÃO TÉCNICA do Jarvis de 2026-11-01 14:48, como no `57baeb6`.
- **Nada além:** `git diff --name-only origin/develop...HEAD` sem nenhum caminho fora de `CHANGELOG.md`, `changelog.d/` e dos dois manifestos.
- **Ferramentas citadas, não refeitas:** `scripts/conferir-release.py --base origin/develop` rc 0 (`ok: changelog.d/ sem fragmentos pendentes`, `versão base: 0.30.8 | versão da release: 0.31.0`); `python3 -m unittest tests.test_changelog` OK (46 testes). Mutação e shellcheck não se aplicam: nenhum código nem shell no diff.
- **Teto M14:** `git diff --numstat --no-renames origin/develop...HEAD` soma 80 linhas, todas em `CHANGELOG.md`, `changelog.d/` e nos manifestos de `.claude-plugin/`, fora das pastas que contam; 0 linhas contáveis e um comportamento só (fechar a release 0.31.0). A branch cumpre a M14.
- **Commit:** mensagem Conventional Commits em português, com o pedido e a lista do que muda.
- **Neutralidade e custo:** nenhum texto novo além das entradas já revisadas nos PRs; nada consome serviço pago (`R-NEUTRO`, `R-CUSTO`).
- **Devops e segurança:** o diff não toca `.github/`, contêiner, IaC, hooks nem código; sem parecer de devops nem de segurança para este commit. O QA é a etapa E2.2q, depois deste review (`R-QA`).
