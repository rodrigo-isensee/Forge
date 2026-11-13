---
tipo: review
contrato: 1
pedido: mp1311-modelo-seguranca
branch: melhoria/mp1311-modelo-seguranca
commit: c734a22a012c8564c2c65e354e3401aa5394ae39
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: mp1311-modelo-seguranca

Head revisado c734a22a (classe C, item 9 do pedido melhorias-de-projeto-1311, E1.26, review por delta da volta única E1.18), instância que não fez a entrega.

## Achados

## Sondas

## Parecer
Aprovado. A migração 0.47.1 (a versão seguinte à 0.46.0 em curso, pasta na ordem de `forge-upgrade`) copia `templates/projeto/docs/security/_modelo.md` só quando o destino falta: não sobrescreve modelo do projeto e rodar de novo não altera nada (saída vazia, bytes iguais). Os cinco testes novos de `ModeloDeSegurancaNoProjeto` passam (init recebe o modelo; upgrade de projeto em 0.46.0 cria o arquivo, commita "chore(forge): migração 0.47.1" e deixa a árvore limpa; modelo existente intacto; repetição idempotente; LEIA resume o conteúdo). Tamanho: 71 linhas de código e teste, um comportamento só. Fragmento de changelog presente e marcado "requer migração". Os três pareceres (review, QA, segurança) ainda faltam por `forge-check pr`; este é o de review. CI do PR: não há PR; rodei só o teste afetado.

## Revalidação (delta c734a22a)
Delta lido por `forge-check parecer delta`: `4b78a54b..d9ca3866` no domínio, em `migrations/0.47.1/migrar`, `tests/mutantes/mp1311-modelo-seguranca.json` e `tests/test_forge.py` (os demais commits são pareceres). A migração agora recusa (saída 1) `docs`, `docs/security` ou o modelo como link simbólico, inclusive pendurado, e cria o arquivo com `O_EXCL|O_NOFOLLOW`. Dois testes de comportamento cobrem o ramo de falha (link pendurado no modelo; `docs/security` como link para fora) e checam que nada nasce fora do projeto. A1 anterior resolvido: a spec traz um mutante por guarda (M1, M2, M3, M5), todos mortos (`bin/forge-mutante`); os 7 testes de `ModeloDeSegurancaNoProjeto` passam. Tamanho: 109 linhas de código e teste (migração 31, teste 78), um comportamento só. Sem PR, sem CI para citar; rodei só o teste afetado e a mutação.
