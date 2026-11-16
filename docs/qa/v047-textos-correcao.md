---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-textos-correcao
commit: 061f0091bbe46b3936106595434fcc5d993233fc
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
---
# QA: v047 (lote DOC1, E2.159)

Escopo `bf475209...061f0091` (E8-TEXTO-ANTIGO na ADR 0012; CORRECAO-ANTES-DOS-PORTOES na skill `trabalho-em-paralelo` e ponteiro no `tech-lead`). Só texto e `tests/test_textos_034.py`; sem código de controle, logo sem mutante de `forge-mutante` (n/a). Não havia parecer anterior: completo. Obrigações: o pedido não traz `CA-n`; viram obrigação a regra `R-REVIEW` e o texto decidido em E2.74.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E8-TEXTO-ANTIGO: ADR 0012 pede a regra "branch atualizada" desmarcada, cita `docs/protecao-de-branch.md`, sem a frase antiga | `E8TextoAntigo.test_conferencia_da_0012_pede_a_regra_desmarcada` | frase antiga ausente | passou |
| CORRECAO-ANTES-DOS-PORTOES: skill traz a regra com `R-REVIEW` e `recomendado` | `CorrecaoAntesDosPortoes.test_skill_tem_a_regra_com_o_id` | ID da regra, `recomendado` | passou |
| Ponteiro no `tech-lead` para a skill, com `R-REVIEW` | `CorrecaoAntesDosPortoes.test_tech_lead_aponta_para_a_skill` | ponteiro e ID | passou |
| Compactação não tira regra (invariantes e tetos de `tests/config.json`) | `test_forge`, `test_clareza`, `test_jarvis_nucleo`, `test_modelos_projeto` + invariantes lidos por regex | tetos de caracteres | passou |
| Regra `R-CONFORMIDADE` da skill ainda ancorada (linha compactada) | `PermissaoAgentesMd` | ID na âncora | passou |

## Cenários e resultado real
- `test_textos_034` no head: 9 testes, OK.
- Invariantes de `agents/tech-lead.md` (21) e da skill (7): todos casam por regex no head. `tech-lead.md` 8615 caracteres, skill 3005.
- Suíte afetada (test_forge, test_clareza, test_jarvis_nucleo, test_modelos_projeto): `Ran 656 tests in 907.501s`, OK.
- `forge-check docs`: rc=0.
- Suíte inteira: no CI do PR (check-run `bateria`); sem PR ainda, não citada.

## Vermelho antes do verde
`bin/forge-testes --vermelho bf475209` não deu veredito aqui: o processo morreu no sandbox (`fatal library error, lookup self`) após 180 s, nas duas tentativas; é "sem veredito", não vale como vermelho. Substituí por cópia em `$TMPDIR` com o head e os 3 arquivos de texto trazidos da base `bf475209`: `Ran 9 tests ... FAILED (failures=3)`, caem os 3 testes novos (`test_skill_tem_a_regra_com_o_id`, `test_tech_lead_aponta_para_a_skill`, `test_conferencia_da_0012_pede_a_regra_desmarcada`); no head, 9 OK. O autor rode o `--vermelho` oficial no CI/PQ dele.

## Achados recorrentes (PA-7)
Conferidos AR-1 a AR-13: nenhum se aplica a este diff (sem código, hook, mutante nem comando). AR-9 (limite antigo no texto): o texto compactado não traz limite numérico alterado; o teste novo prova a frase antiga ausente na ADR 0012. Nenhuma linha nova.

## Mesclagem
O remoto avançou com os pareceres de review e segurança (`c47baa9e`, `b8af82d8`), só `docs/`; trazido por merge, sem rebase.
