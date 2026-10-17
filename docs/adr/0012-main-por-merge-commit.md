# 0012 - A main é mesclada por merge commit

Estado: vigente. Data: 2026-10-16.
Propósito: acabar com a divergência entre a `main` e as branches de integração e com o PR de sincronização `main` → `develop`. Público: quem mantém o Forge. Revisão: 2026-10-16.

## Contexto
A ADR 0008 (decisão 2) mandou squash na `main` para ela ter só commits do usuário. O commit de squash não existe na `homolog` nem na `develop`, então toda release deixa as duas divergentes da `main` e pede um PR de sincronização. Evidência (sugestão S-15, 2026-10-16): o PR de sincronização da 0.16.0 (#160), o #169 barrado pelo gate de review, o conflito entre #173 e #169, a solução com `merge -s ours` (#174) e o #175, com 3 briefs reprovados e 2 decisões do dono; sincronização observada de 0,3 h a 4,1 h por release. O objetivo da ADR 0008 (a `main` só com commits do usuário, sem os das branches de trabalho) se mantém, porque a `develop` continua por squash: as branches de trabalho já viram um commit por PR antes de chegar à `homolog`. Leitura da autoria dos últimos 50 commits da `develop`: todos de Rodrigo Isensee, em dois e-mails (24 pelo noreply do GitHub e 26 pelo e-mail corporativo), nenhuma identidade de teste.

## Decisão
Decisão do dono (2026-10-16): S-15 -> "A": a `main` passa a ser mesclada por **merge commit**, não por squash; muda o ADR 0008 e o `R-FLUXO` "Métodos de merge"; acaba o PR de sincronização `main` → `develop`. A `develop` continua por squash e a `homolog` por merge commit. A `main` continua só do usuário (`R-MAIN`). Esta ADR substitui a parte da ADR 0008 sobre o método de merge da `main`; o resto da 0008 vale.

## Alternativas
- Manter squash e automatizar a sincronização (`forge-check sync`, exceção no gate do CI): a divergência continua, só deixa de custar decisões; fora do pedido.
- Manter como está: o custo de cada release continua.

## Consequências
- Melhora: o commit de merge da `main` tem a `homolog` como pai; some o PR de sincronização e o conflito que ele causou.
- Piora: a `main` passa a ter os commits de promoção (um por PR da `develop`, já em squash) além do commit de merge.
- Fica a manter: o texto de `R-FLUXO` e seu invariante em `tests/config.json`; nenhum portão muda (review, QA, CI, `R-MAIN` e o merge do dono ficam).
- Os PRs de sincronização anteriores à mudança continuam no histórico.

## Por que o existente não basta
Não se aplica (nenhum mecanismo novo).

## Critério de reversão
Se a `main` ou a `develop` voltar a divergir uma da outra depois de uma release feita por merge commit, ou aparecer na `main` um commit de identidade de teste vindo das branches de trabalho.

## Leituras
| Data | Medida | Veredito (manter, ajustar, reverter) |
|---|---|---|
| 2026-10-16 | PRs de sincronização por release (antes: 1 a 2) | pendente |
