---
tipo: qa
contrato: 1
pedido: lote-forge-check-0.28.0
branch: melhoria/lote-forge-check-0.28.0
commit: d4bc9267cba743dd1397fe9c5f179a3bab2ce64a
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
