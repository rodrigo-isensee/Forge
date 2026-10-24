---
tipo: qa
contrato: 1
pedido: lote-forge-check-0.28.0
branch: melhoria/lote-forge-check-0.28.0
commit: eee8e7316ea7bffd9c489e36b4f9f7898377d7f4
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: lote-forge-check-0.28.0

Pedido RET-LOTE-FORGE-CHECK, E1.2. HEAD testado `a18209c` (base `af79bef`; review e segurança aprovados antes). Sem especificação de UX nem API: as obrigações são as regras e itens do lote (M4, M5, M13, M16, P2 a P6) como nos commits, no review e na segurança desta branch.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| M16 marca única das etapas | `test_etapa_do_brief` | etapa sem menção, junção de delegações, etapa de outro papel | passou |
| P2 `brief gerar --cobre` e tabela de pareceres | `test_etapa_do_brief` | etapa inexistente, papel errado, `pr` sem pareceres | passou |
| M13 isenção única de QA só para `.md` fora de controle | `test_isencoes` e fixtures `parecer/pr-md-de-*-sem-qa-bloqueia` | diff vazio, base ausente (falha fechada), agente/regra/skill de stack | passou |
| M4 `merge` e `cmd` do conferente como prova | `test_forge` | `cmd` do autor não vale | passou |
| P6 `--gravar` com número livre, lote, 0444 | `test_brief_gravar` | nome inseguro, pasta com link simbólico | passou |
| P4 `anotar` só em `docs/pedidos/<id>.md` | `test_anotar` | link simbólico, campo com controle, caminho fora (segurança A1) | passou |
| P3 citação só de `.md`, nunca `.env` | `test_citacao` | id inexistente, fonte fora das raízes (segurança A2) | passou |
| P5 estado antes do ato e Base-sha | `test_estado_da_branch` | sem gh (não verificável), PR MERGED, Base-sha fora da branch | passou |

## Cenários e resultado real
- Suíte completa (`python3 -m unittest discover -s tests`, 410 s): 1661 testes, 4 falhas, 1 skip. As 4 são as conhecidas do ambiente que o PR #288 corrige: `test_shellcheck_no_hook` (SC2329 em `.githooks/pre-push`), `test_erro_interno_com_lista_de_permissao_falha_fechado` e as fixtures `conformidade/contrib-falha-fechada-pela-raiz-cwd-home-bloqueia` e `-cwd-wt-bloqueia`. Nenhuma falha nova. O skip não vem do diff (nenhum `skip` adicionado pela branch).
- Testes novos (6 módulos, 67 testes) sobre o HEAD: OK.
- Vermelho antes do verde: código de produção da base `af79bef` com os testes do HEAD (cópia em `$TMPDIR`, `git archive`): 67 testes, 55 falhas e 23 erros; sem a implementação os testes novos caem.
- `scripts/validar-plugin.sh`: "Validation passed".
- Mutação: o Forge não tem ferramenta de mutação gratuita em `stacks/`; não executada.
- Acessibilidade e E2E de navegador: não se aplicam (CLI e hooks).

## Bugs abertos
Nenhum.

## Revalidação por delta (REVAL-288, E4.3)
Depois do review e da segurança por delta aprovados, pela decisão "C" do dono (2026-10-23). Delta desde `a18209c` (commit do parecer anterior) até `d4bc926`: a entrada da `develop` (`7423c44`, PR #288, FIX-SUITE-LOCAL: `.githooks/pre-push`, `tests/test_hooks.py`, `tests/apoio_pathlib_312/`, duas fixtures `contrib-falha-fechada-pela-raiz-cwd-*`, documentos `suite-local-verde`) e pareceres em `docs/`. Nenhum código da entrega mudou. `bin/forge-testes` escolheu a suíte completa (o hook sem mapa), que o dono vetou nesta rodada; rodei, no lugar, os 6 módulos da entrega mais `test_hooks` (`python3 -m unittest tests.test_etapa_do_brief tests.test_isencoes tests.test_forge tests.test_brief_gravar tests.test_anotar tests.test_citacao tests.test_estado_da_branch tests.test_hooks`): 529 testes, 448 s, `OK`. As 4 falhas conhecidas do ambiente agora passam (o #288 as corrigiu). Comportamento já aprovado (M16, P2 a P6, M4, M13): igual, sem regressão. Não refiz o vermelho antes do verde (fora do delta). Veredito: aprovado, sem achado novo.

## Revalidação por delta (INTEG-LOTE-FC-REV, E3.1)
Depois do review (`0be3566`) e da segurança (`f8b2a16`) do delta aprovados. Delta: o commit de merge `8649439` (integra a `develop` com a M14b, #291) e a resolução dos conflitos em `bin/forge-check` (despacho: ficam `anotar` do lote e `escape`, `afrouxamentos`, `esperas`, `corrigidos` da M14b), `bin/forge-testes` (`FORGE_CHECK` = união, 20 módulos) e `tests/test_testes_tocados.py` (contagem 20, `test_medidas_m14b` entre os conferidos); `docs/hooks.md` sem código. Worktree em `f8b2a16` (só pareceres sobre `8649439`; `git diff --name-only 8649439 HEAD` lista apenas `docs/reviews` e `docs/security`).
- Módulos: os 20 de `FORGE_CHECK` (`python3 -m unittest tests.test_anotar ... tests.test_voltas`, `HOME` numa pasta própria): 1041 testes, 228 s, `OK`, rc 0. Cobrem os três arquivos em conflito, o lote e `test_medidas_m14b`. Sem suíte completa (teto de memória, decisão do pedido).
- Ponta a ponta no `forge-check` mesclado, repositório de sonda em `$TMPDIR`: `anotar --tipo decisao` grava `DECISÃO DO DONO (hora): ctx → "vai"` em `## Decisões do usuário` (rc 0) e `--pedido ../x` é recusado (rc 2, nada gravado); `movimento` + `esperas` lista `EX-card dono ... minutos=aberta` e o total (rc 0); `escape registrar` grava a linha fixa (rc 0), recusa `--achado-por zzz` (rc 1), `escape resumo` conta `alto=1 qa=1` (rc 0); `corrigidos --ref HEAD` acha o `fix` que cita `#1` (`evidencia=cita`, rc 0); `afrouxamentos --prs 2 --ref HEAD` diz `sem-violacao` (rc 0). Os dois conjuntos de subcomandos coexistem no despacho, sem um engolir o outro.
- `scripts/validar-plugin.sh`: "Validation passed".
- Vermelho antes do verde e mutação: não refeitos (nenhum teste novo no delta; a resolução só une listas e contagens; sem ferramenta de mutação no Forge).
- Comportamento do lote (M16, P2 a P6, M4, M13) e da M14b: sem regressão. Veredito: aprovado, sem achado, nenhum bloqueante.

## Revalidação por delta (INTEG-LOTE-FC-2-REV, E3.1)
Depois do review e da segurança do delta. Delta: o commit `31e78cd` (integra a `develop` `139a3b4`, com o #294: `hooks/agentes.py` com o hash do brief, `bin/forge-check`, `ci.yml`, testes `test_agentes_clone`, `test_agentes_hash_brief`, `test_guarda_conferente`) e a resolução do conflito em `docs/hooks.md` (`git show --cc`: as duas linhas mantidas, a do hook `agentes` com R-BRIEF e a do `parecer` com `isencoes_da_entrega`, M13). Worktree em `eee8e73` (só pareceres sobre `31e78cd`).
- Módulos (`HOME` próprio): os 20 de `FORGE_CHECK` mais `test_agentes_clone` e `test_agentes_hash_brief`, que leem `hooks/agentes.py`, `hooks/parecer.py`, `bin/forge-check` e `docs/hooks.md`: 1071 testes, 278 s, `OK`, rc 0. Sem suíte completa (decisão do pedido).
- Ponta a ponta do hook `agentes` (sonda em `$TMPDIR`): brief com hash certo ao `forge:conferente` passa (rc 0); hash errado é bloqueado (rc 2, `R-BRIEF: o hash do brief não bate com o arquivo`). Isenção da entrega (`isencoes_da_entrega` do `forge-check`, que o hook `parecer` usa): diff só de `docs/x.md` isenta `{'qa'}`; com `agents/y.md` a isenção some (`set()`). As duas regras coexistem na resolução.
- Vermelho antes do verde e mutação: não refeitos (nenhum teste novo na resolução; os do #294 e do M13 já foram aprovados nas suas entregas). Sem regressão do lote. Veredito: aprovado, sem achado, nenhum bloqueante.
