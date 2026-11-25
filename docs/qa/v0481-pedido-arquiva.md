---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-pedido-arquiva
commit: 8b3124465d4c1a3c0b31e100731a5b9935d8a223
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0481 E9.11 (delta do #874, de ec38cbc4 a 8b312446)

## Achados
- A1 (bloqueante) tests/mutantes/v0481-pedido-arquiva-3.json:56 · Com `ENTREGUE_DA_ETAPA.match`, 4 mutantes sobrevivem: M21 (guarda `.md=`), M23 (`split(";")`), M24 e M38 (corte na 2ª etapa). O teste declarado deixou de matá-los. Falta teste para `E1.1 entregue .md=x`, `E1.1 (x;y) entregue`, `E1.1 (E1.2) entregue`, ou equivalente justificado.
- A2 (recomendado) bin/forge-check:8061 · `E1.1 entregue-se` ainda fecha a etapa (o hífen não entra no `(?![\w?])`). Texto livre residual; incluir `-` na exclusão, ou aceitar como forma estrita.

## Critério → teste → resultado (delta)
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 do QA anterior: só a forma estrita `<id> entregue` fecha | `test_forma_estrita_de_entregue_fecha` (5 linhas), `test_negacao_futuro_e_texto_livre_de_entregue_nao_fecham` (9), `test_entregue_com_interrogacao_nao_fecha` (2) | negação, futuro, texto livre, interrogação | passou (M22 e M40 a M48 morreram) |
| Corte na linha: `;`, 2ª etapa, linha de parecer | `test_linha_que_cita_outra_etapa_so_fecha_a_atribuida` | `.md=`, `;`, id entre parênteses | reprovou: M21, M23, M24, M38 sobrevivem (A1) |
| Demais critérios do parecer anterior (E9.7) | testes inalterados | n/a | passou (suítes verdes) |

## Cenários e resultado real
- Local no head 8b312446: `test_brief_tamanho` (23) e `test_forge_tamanho` (24) OK.
- Sondas na cópia limpa: `E1.1 (E1.2) entregue`, `E1.1 entregue .md=x` e `E1.1 (x;y) entregue` dão None no código real; sob o mutante M24/M38, a primeira dá `E1.1`. `E1.1 entregue-se` dá `E1.1` (A2).
- `forge-mutante --processos 4` nas 7 specs (`rev=8b3124465d4c`): M22 e M40 a M48 morreram; M5 e M37 mortos por erro com controle verde (aceitos, do parecer anterior); sobreviveram M21, M23, M24 e M38 (todos em `etapa_entregue_na_linha`).
- Vermelho: `forge-testes --vermelho 8d7914bc... --modulos test_brief_tamanho`: não prova (passa na base)=5; prova (API ausente)=13; prova (asserção)=5. Os 3 testes novos provam.
- `forge-check parecer delta`: `bin/forge-check` e o teste no domínio do QA.
- CI: no sha 8b312446 a Catraca está `failure` e o `CI` (bateria) na fila no momento da leitura; a suíte inteira vale pelo check-run `bateria` do mesmo sha, e não leio o log no sandbox.
