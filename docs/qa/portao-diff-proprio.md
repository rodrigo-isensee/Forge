---
tipo: qa
contrato: 1
pedido: portao-diff-proprio
branch: melhoria/portao-diff-proprio
commit: b771f68254872435ff39e67fb156f6e4a279bf51
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-15
---
# QA: o portão compara o parecer por merge simulado (cartão 15a, D-15A = A)

Links: `docs/reviews/portao-diff-proprio.md`, `docs/security/portao-diff-proprio.md`, emenda do item 3 em `docs/adr/0004-contrato-verificavel-entre-agentes.md`. Sem UX nem API. Obrigações: ADR 0004 item 3 (mudança de conteúdo ou de posição em arquivo executável pede novo parecer; a base que só desloca linhas não) e a decisão D-15A = A. Offline, sem custo (`R-CUSTO`).

O código testado é o de b771f68 (diff `b5411e9..b771f68`: `bin/forge-check`, `tests/test_portao_diff_proprio.py`, ADR, changelog, pareceres). Os commits depois só mexem em pareceres.

## Critério -> teste -> resultado
Método: `$TMPDIR/qa-portao.sh` monta 5 repositórios git reais (base `develop` e ramo com pareceres de review e QA para o commit de trabalho) e chama `python3 ~/.forge-contrib/wt/portao/bin/forge-check pr p --base develop`, o binário da worktree.

| ID | Obrigação | Cenário | Fronteira protegida | Esperado | Obtido | Resultado |
|---|---|---|---|---|---|---|
| CASO 1 | Base que só desloca linhas não desatualiza | base ganha linhas no topo e entrada no changelog; merge resolve o changelog | deslocamento de linhas, conflito só no changelog | vale (saída vazia) | vale | passou |
| CASO 2 | Mudança de conteúdo pede novo parecer | depois do merge, a branch altera `src.py` | uma linha a mais | desatualizado, cita `src.py` | `desatualizado: src.py mudou depois do parecer` | passou |
| CASO 3 | Mudança de posição pede novo parecer | a linha da branch muda de lugar | mesma linha, outra posição | desatualizado | `desatualizado: src.py mudou...` | passou |
| CASO 4 | `\r` não esconde conteúdo | changelog em conflito; o HEAD junta duas linhas do parecer com `\r` | `\r` como separador | desatualizado | `desatualizado: CHANGELOG.md mudou...` | passou |
| CASO 5 | Conflito em código falha fechado | base e branch mudam a mesma linha de `src.py`; merge resolvido à mão | conflito em arquivo de código | desatualizado, cita `src.py` | `desatualizado: src.py mudou...` | passou |

Casos reais (binário da worktree, base `origin/develop`): `pr teste-abertura-feita --ref melhoria/teste-abertura-feita` e `pr ci-ubuntu-26 --ref melhoria/ci-ubuntu-26`: rc 0 e saída vazia nas duas.

## Vermelho antes do verde
Os mesmos 5 casos com o `forge-check` de b5411e9 (`git show b5411e9:bin/forge-check`): CASO 1 dá desatualizado (esperado: vale) e os casos 2 e 5 desatualizam citando `CHANGELOG.md` e não `src.py`. Falham sem a implementação e passam com ela. Os casos 3 e 4 já barravam antes (a regra anterior era estrita); aqui guardam que o afrouxamento não os deixou passar. Mutação: sem ferramenta gratuita na stack do Forge; não executada.

## Suíte
`env -u FORGE_ABERTURA_FEITA python3 -m unittest discover -s tests` (load 0,32 antes): `Ran 578 tests in 152.973s`, `OK`. Inclui os 16 testes de `tests/test_portao_diff_proprio.py`.

## Observações
Nenhum bug. A emenda da ADR traz o rótulo `afrouxa-regra`; o envio e o PR são do dono (D-ETAPAS = A). O portão continua barrando parecer reprovado ou desatualizado de verdade (casos 2 a 5).
