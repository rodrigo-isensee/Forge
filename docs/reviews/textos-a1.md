---
tipo: review
contrato: 1
pedido: textos-a1
branch: melhoria/textos-a1
commit: b9a8d7548e429dc7abebd4c61c5c16895484a001
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Review: textos-a1 (E1.2)

Escopo: `0f480c8..b9a8d75` (4 commits, 5 arquivos). Nenhum outro arquivo mudou: `docs/regras/R-FLUXO.md`, `tests/test_hooks.py`, `skills/qa-testing/SKILL.md`, `skills/ci-cd/SKILL.md`, `changelog.d/textos-a1.md`. Sem delta anterior (primeira rodada). Segurança e DevOps: sem parecer próprio neste diff (texto, teste e skills; nada de pipeline, container ou IaC); o teste do hook cobre a recomendação de `docs/security/fc-aq-hook.md`.

## Achados

## Detalhe dos achados
- Frase da `R-FLUXO`: só acrescenta (1 linha, só inserção dentro do parêntese da trava da release); nada afrouxado, nenhum item de `invariantes` tocado. Os testes de duplicação, neutralidade e changelog passam na worktree.
- Mutação do hook, feita aqui numa cópia em `$TMPDIR` (o autor não a fez), rodando `test_aq_grava_so_nas_duas_pastas_do_clone_de_contribuicao`. Base: OK. `casa` sem distinção de caixa: falham "maiúsculas no caminho" e "maiúsculas na raiz do clone". `em_qualquer_lugar` sempre falso: falha ".git aninhado em propostas". Lista `escrita_permitida` ignorada (hook deixa passar): falham 7 casos, entre eles "maiúsculas no caminho", "maiúsculas na raiz do clone" e "clone como link para fora do home". Os quatro casos novos falham quando o hook deixa passar.
- Roteiro das skills: neutro (`R-NEUTRO`; só git genérico, `<base>`), correto (fetch da base, merge `--no-ff` de `refs/remotes/origin/<base>` em cópia descartável, checagem contra essa base, confirmação por `git rev-parse`) e sem afrouxar nada.
- Recomendado, não bloqueia: "clone como link para fora do home" só falha sob a mutação ampla (lista ignorada), não sob uma mutação só da forma `home`; basta como regressão do comportamento. A seção idêntica nas duas skills duplica texto por escolha do pedido; se crescer, extrair para um ponto único e citar.
- Risco informado pelo autor (primeiro push falhou sob carga, segundo passou): cartão FLAKY-CARGA já aberto; fora do diff.
