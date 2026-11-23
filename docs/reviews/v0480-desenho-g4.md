---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-desenho-g4
commit: 5f350950c697dffcad4de300ca5749b3905114ca
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E99.3, desenho do G4)

Escopo: `docs/propostas/g4-trava-real-bp8.md` e `changelog.d/v0480-desenho-g4.md` (base 2d73a35e, 128 linhas, só documentação). Sem código, sem guarda nova, sem mutante.

## Achados
- A1 (recomendado) docs/propostas/g4-trava-real-bp8.md:38 · referências de passo deslocadas em um na tabela (a): T4 cita 8b (é 9b), T6 "depois do passo 9" (CODEOWNERS é o 10), T10 "passo 10" (strictAllowlist é o 11); corrigir antes do dono seguir a tabela.
- A2 (recomendado) docs/propostas/g4-trava-real-bp8.md:22 · "102 pontos barrar(" não fecha com a soma da própria quebra (63+19+11+9+6+3 = 111, que bate com a contagem por ID na base 2d73a35e); trocar por 111 ou explicar o critério.

## Sondas

## Parecer
Aprovado. Conferido contra o brief:
- Fontes citadas e conferidas na base 2d73a35e: `hooks/conformidade.py` (contagem por ID 63/19/11/9/6/3 confere; 2452 leitura de `.env`; 3305 rótulo `afrouxa-regra` pela conta do `gh`; 3531 `gh api`), `bin/forge_sempre_atual.py:550` (`tag_na_main`, ADR 0017), `tests/catraca.py` (rótulo do `dono`), `docs/protecao-de-branch.md` (F8, `portoes`, `main-do-dono`), README ("Identidade do git", "Rede restrita de verdade"). O estado do GitHub (seção 0) é leitura do autor de segurança; não refiz `gh api`.
- `R-NEUTRO`: dono e contas como `<dono>` e "conta dos agentes", sem nome de projeto; `tests/neutralidade.py` rc=0 na worktree no head.
- `R-DECISAO`: nenhuma regra muda neste diff; as trocas de bloqueio para aviso (seção b) e o critério de bloqueio da revisão (seção d) ficam condicionados aos passos do dono conferidos (passo 12) e a PR com `afrouxa-regra`, coerente com a DECISÃO DO DONO de 22/11 05:21 (G4 segue 2a, passos 1 a 5 do dono primeiro). Critério de reversão presente (seção e), evidência do "por que o existente não basta" na seção 0, data de revisão 2026-12-21.
- `R-CUSTO`: a seção (f) mostra custo zero no repositório público e diz o que faria custar (privado), com alternativa sem custo.
- Commits: dois, Conventional Commits em português, um por mudança; fragmento em `changelog.d/` presente.

Os dois achados são de precisão do texto e viram cartão; não bloqueiam (`R-REVIEW`).
