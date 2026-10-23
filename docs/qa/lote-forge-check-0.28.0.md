---
tipo: qa
contrato: 1
pedido: lote-forge-check-0.28.0
branch: melhoria/lote-forge-check-0.28.0
commit: a18209c69da8a207adb4b576a6d4fa39ad63b109
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
