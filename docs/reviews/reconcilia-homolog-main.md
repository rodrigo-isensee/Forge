---
tipo: review
contrato: 1
pedido: reconcilia-homolog-main
branch: melhoria/reconcilia-homolog-main
commit: 295da22a3d03999b822e879f94a927a4fba65ce8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-19
---
# Code review: RECONCILIA-HOMOLOG-MAIN (reconciliar a develop com a homolog e a main)

Diff revisado: `0c77d23...295da22` (2 commits: `6bf8021` merge octopus `-s ours` de `origin/homolog` 2b22729 e `origin/main` 6bd7188; `295da22` fragmento). Escopo revisado: E1 e E3 do pedido. E2 (ruleset) tem parecer próprio do `devops-engineer` (`docs/devops/reconcilia-homolog-main.md`) e do `security-engineer` (E2.2), não refeitos aqui. Suíte e `scripts/validar-plugin.sh` não refeitos (R-TETO; prova do autor em E1.1, 813 OK, e QA em E1.3).

## Conferências (saída das ferramentas, nesta revisão)
- Árvore sem mudança de conteúdo: `git rev-parse 0c77d23^{tree}` = `6bf8021^{tree}` = `95b58497fa44...`; `git diff --name-status 6bf8021 HEAD` = só `A changelog.d/reconcilia-homolog-main.md`. A árvore do HEAD é a da develop mais o fragmento.
- Premissa do pedido: árvores de 2b22729, 6bd7188 e 7033e45 idênticas (`016f9d1b3c36...`); a estratégia `ours` não descarta nada que não esteja na develop.
- Ancestralidade: `git merge-base --is-ancestor` verdadeiro para `origin/homolog` (2b22729) e `origin/main` (6bd7188) sobre o HEAD.
- `git merge-tree --write-tree origin/homolog HEAD` e `... origin/main HEAD`: saída 0, árvore `ca7559619ace...` = `HEAD^{tree}`, sem conflito. O PR develop → homolog fica rápido e limpo.

## Checklist (leitura)
1. Escopo: faz E1 e E3, nada mais; nenhum arquivo fora do fragmento muda.
2. Regras: exceção pontual a R-FLUXO:15 (develop por squash) decidida pelo dono (DECISÃO DO DONO 2026-10-19); a regra não é alterada; sem custo (R-CUSTO); neutro (R-NEUTRO).
3. Fragmento `changelog.d/reconcilia-homolog-main.md`: tipo `Corrigido` (válido em `bin/forge-changelog`), descreve a exceção (merge commit `ours`, exceção única ao squash da develop) e o motivo (divergência por #201/#202, destravar develop → homolog).
9. Commits: Conventional Commits em português, mensagens claras, com atribuição.
10. Critério de reversão: não se aplica a mecanismo novo; o merge não muda conteúdo e o impedimento de reincidência é o ruleset (E2).

## Condição para o merge (bloqueia se descumprida)
- **O PR precisa entrar na develop por merge commit, não squash nem rebase** (E1.4). Squash recriaria um commit sem 2b22729 e 6bd7188 como pais e desfaria a reconciliação. Quem mescla confere depois: `git merge-base --is-ancestor origin/homolog origin/develop` e o mesmo para `origin/main`, ambos verdadeiros.

Parecer: **aprovado**.
