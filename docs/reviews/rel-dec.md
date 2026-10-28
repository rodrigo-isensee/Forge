---
tipo: review
contrato: 1
pedido: rel-dec
branch: melhoria/rel-dec
commit: fcc5980ee53f58cb021b7c96e19ca81d712d07e8
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: rel-dec (REL-R4 e REL-D1A)

Diff lido: `git diff ed7fbd80ba9b57562442a20c9cfa479a1a5c94c7...fcc5980ee53f58cb021b7c96e19ca81d712d07e8` (3 commits, 7 arquivos, 15 adições e 13 remoções). Primeira rodada: sem parecer anterior, sem delta.

## Achados
- A1 (bloqueante) scripts/promover-homolog.py:259 · requisito (E2 do REL-DEC, decisão REL-D1A): com checks pendentes ou nenhum check ainda (linhas 242 e 259), o script sai com 3 sem imprimir o comando --auto; ele só aparece com tudo verde (263), e o tech-lead segue esperando os checks
- A2 (bloqueante) docs/regras/R-FLUXO.md:13 · requisito e defeito provado: o ruleset merge-commit-homolog-main exige só os checks bateria e catraca; o PR #343 rodou também bateria (python 3.14), fora dos obrigatórios; o merge automático mescla com esse check vermelho, contra "todos os checks passam" (idem agents/tech-lead.md:32)
- A3 (recomendado) agents/tech-lead.md:32 · o comando citado (gh pr merge <branch> --auto --merge) não leva --match-head-commit, que o script imprime (scripts/promover-homolog.py:213); alinhar R-FLUXO.md:13, tech-lead.md:32 e docs/promocao-integrador.md:18 num comando só, com o sha conferido
- A4 (recomendado) docs/regras/R-FLUXO.md:27 · "só na hora do merge (git fetch + merge da develop)" soa como merge sempre; o forge-fechar (passo 2b) só para quando há arquivo em comum, e o squash não pede o merge; dizer "quando há conflito ou o forge-fechar pede"
- A5 (recomendado) tests/config.json:407 · a frase nova da R-FLUXO.md:13 que limita o merge automático à homolog (a main fica com o usuário) não tem invariante; uma invariante guardaria esse limite

## Parecer
Reprovado, por dois bloqueantes de requisito; o resto está correto.

O que confere:
- REL-R4: a `R-FLUXO.md:27` e o `agents/tech-lead.md:29` passam a dizer "só na hora do merge", e a frase "o `forge-check pr` confere o merge simulado" é verdadeira: `bin/forge-check` `arquivos_divergentes` (linha 393) e `commit_vale` (linha 443) simulam o merge com `git merge-tree` sobre a base. Nenhum outro texto de `agents/`, `skills/`, `templates/` ou `docs/regras/` repete a regra antiga (grep por "uma vez, antes" e "antes do review" fora dos pareceres antigos).
- Invariantes de `tests/config.json`: 3 trechos trocados, nenhum removido; cada um casa com o texto novo (`RegrasInviolaveis.test_trechos_obrigatorios` OK). A troca é coerente com a `R-FLUXO` e com o `tech-lead`, e o PR precisa de destaque no título e do rótulo `afrouxa-regra` (decisão do dono 09:10).
- Teto M14: 4+4 (`scripts/`), 3+3 (`tests/config.json`) e 1+1 (`tests/*.py`) = 16 linhas, bem abaixo de 400.
- Hooks: `gh pr merge develop --auto --merge ...` passa pelo `parecer.py` (a `develop` está em `INTEGRACAO`) e pelo `conformidade.py` (`pr_merge_integracao` do tech-lead); a `main` continua barrada (`R-MAIN`). A catraca escuta `labeled`, então o rótulo do dono a refaz e o merge automático espera por ela.
- Testes do item: `python3 -m unittest tests.test_promover_homolog` (25 OK). `bin/forge-testes --listar` aponta a suíte completa, porque `scripts/promover-homolog.py` não tem mapa; ela fica no pre-push e no CI.
- Commits em Conventional Commits, um por item, mais a volta 1 (`fix(promocao)`).

A1, `scripts/promover-homolog.py:242/259/263` e `docs/promocao-integrador.md:18`: a decisão REL-D1A e o E2 dizem que o PR nasce com o merge automático ligado e que o tech-lead não espera os checks. O script abre o PR (passo 4), mas com checks pendentes, que é o estado normal logo depois da abertura, sai com 3 e "rode de novo". O comando `--auto` só sai no passo 7, com tudo verde, quando o merge manual já bastaria. Sugestão: com o PR aberto e sem vermelho (pendente, nenhum check ainda ou catraca pedindo o rótulo), imprimir o comando `--auto --match-head-commit <sha>` e sair com um código que diga "armar o merge automático". Teste novo: o caso pendente imprime o comando. Severidade: bloqueia.

A2, `docs/regras/R-FLUXO.md:13` e `agents/tech-lead.md:32`: o merge automático do GitHub espera só os checks obrigatórios. Pela leitura de `gh api repos/rodrigo-isensee/Forge/rules/branches/homolog`, eles são `bateria` e `catraca`, e o job `bateria (python 3.14)` de `.github/workflows/ci.yml:37`, que rodou no PR #343, não está entre eles. Hoje o script lê todos os checks e só passa `pass` e `skipping`; com o `--auto` armado antes disso, a promoção mescla com o 3.14 vermelho ou pendente, e isso afrouxa um portão sem a decisão do dono. A correção tem duas saídas: o dono põe `bateria (python 3.14)` nos checks obrigatórios do ruleset (configuração do repositório, ação do dono, como a E3.1), ou o texto passa a dizer que o automático espera só os obrigatórios, e aí volta ao dono como decisão. Severidade: bloqueia. Cartão para o `security-engineer`: o merge automático e o conjunto de checks obrigatórios da `homolog`.

A3 a A5 são recomendações e não devolvem.

Segurança e QA: pareceres próprios (E2.1 e E3.1, em paralelo), não refeitos aqui.
