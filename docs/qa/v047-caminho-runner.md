---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-caminho-runner
commit: 72d2eaa01398a1f9d9713347fe2a9620fa035863
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 (E5.24, CAMINHO-PESSOAL-BARRA-RUNNER)

Branch `melhoria/v047-caminho-runner`, código testado no head 72d2eaa0 (os commits seguintes só trazem pareceres de review e segurança).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Home do runner do CI não é acusado | `VerificarContribuicao.test_home_do_runner_passa_mas_nome_que_o_contem_ou_o_segue_falha` | `/home/runner/` exato | passou; CP-M1 morreu |
| Caminho pessoal colado ao home do runner é acusado (`/home/runner/home/<nome>`, `/home/runner/Users/<nome>`) | mesmo teste, 2 linhas novas | barra do caminho colado não é comida pelo marcador | passou; CR-M1 morreu |
| Só o segmento `runner/` exato é tirado | mesmo teste (`runner2`, `/Users/runner`) | nome que contém ou segue `runner` | passou; CP-M2 morreu |
| Achado reprova (não inverte) | mesmo teste | polaridade da guarda | passou; CP-M3 morreu |

## Cenários e resultado real
- Diff contra a base: 1 linha de guarda mudada (`scripts/verificar-contribuicao.sh:55`, marcador `@` vira `@/`), com 1 mutante novo (CR-M1) e os 3 CP reescritos para o trecho novo. Escopo bate com o pedido.
- Verde: `python3 -m unittest tests.test_forge.VerificarContribuicao` no head, ver Provas. A suíte inteira fica para o check-run `bateria` do CI do PR (não há PR aberto).
- Vermelho na base: `forge-testes --vermelho b27f6985` saiu 0: o script voltou à base e o teste de `tests/test_forge.py` mantido no HEAD prova a falha.
- Mutantes: CR-M1, CP-M1, CP-M2 e CP-M3 morreram (saída 0). A linha 55 é a única guarda do diff e tem mutante; `--cobertura` diz "não coberto" por ser shell, coberto à mão pela lista acima.

## Provas
```
vermelho: base=b27f69857887 head=03dc345fe4ac ...
revertidos à base: changelog.d/v047-caminho-runner.md, docs/reviews/..., docs/security/..., scripts/verificar-contribuicao.sh
mantidos no HEAD: tests/mutantes/v047-caminho-pessoal.json, tests/mutantes/v047-caminho-runner.json, tests/test_forge.py
rc=0
forge-mutante: pedido=v047 rev=03dc345fe4ac
CR-M1 · morreu · scripts/verificar-contribuicao.sh:55
CP-M1 · morreu · scripts/verificar-contribuicao.sh:55
CP-M2 · morreu · scripts/verificar-contribuicao.sh:55
CP-M3 · morreu · scripts/verificar-contribuicao.sh:55
rc=0
```
