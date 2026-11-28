---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-autoria
commit: f0c380e28827a0c6168b142dd65d3499faef0dd7
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 (G2-M9-2-AUTORIA, #914)

## Critério → teste → resultado
Sem especificação de UX; as obrigações são M9.2 do G2 (`docs/security/ameacas/g2-parecer-status.md`, T9) e a regra de papel por caminho do #878.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `.forge/pareceres/<pedido>/<tipo>.md` gravado entra em `autoria.jsonl` | `test_autoria_registra_forge_pareceres`, fixture `autoria-forge-pareceres-registra.json` | caminho exato aceito | passa; vermelho na base |
| O registro leva o papel de quem gravou | `test_caminho_por_papel_em_forge_pareceres`, `test_ponta_a_ponta_recusa_autoria_de_outro_papel` | permissão (QA gravando `review.md` vira `qa`, não `tech-lead`) | passa; o 1º vermelho na base, o 2º é guarda de não afrouxar |
| Fora de pedido/tipo/extensão/pasta não registra | `test_fora_de_pedido_e_tipo_nao_registra`, fixture `...fora-do-caminho-nao-registra.json` | sem pedido, subpasta, `.txt`, `.forge/outros` | passa; guarda (passa na base; M2 e M3 a matam) |
| `parecer publicar` aceita com a autoria do hook | `test_ponta_a_ponta_publica_com_autoria_do_hook` | hook real em subprocesso + `gh` falso | passa; vermelho na base |
| Sem registro, publicar recusa (M9.1) | `test_ponta_a_ponta_recusa_sem_autoria` | ausência do registro, nada chama o `gh` | passa; guarda |

## Cenários e resultado real
- Risco apontado pelo autor (`recusa_do_publicar` confere só sha256 e papel, não o caminho): analisado em `bin/forge-check:3883-3905`. Para publicar `review`, exige registro do papel `tech-lead` com o mesmo texto; um texto de outro papel nunca vira registro `tech-lead` (o papel vem do hook, M4 e `recusa_autoria_de_outro_papel` provam). O que o registro de outro caminho do mesmo papel permite (texto do tech-lead gravado em `docs/reviews/` e copiado para `.forge/pareceres/`) continua texto do tech-lead; não é escalada. Não afrouxa nada: só soma um caminho registrado. Sem achado.
- Vermelho antes do verde (`bin/forge-testes --vermelho b4ae17556998 --modulos test_conformidade_pareceres`): `vermelho: base=b4ae17556998 head=f0c380e28827`; revertidos à base: `bin/forge-testes, changelog.d/v0481-g2-autoria.md, hooks/conformidade.py, tests/pesos-d4.json`; 3 provam (asserção), 3 "não prova (passa na base)" (as guardas negativas, cobertas por M2, M3, M4).
- Local: `python3 -m unittest tests.test_conformidade_pareceres tests.test_forge_pareceres`: 41 testes OK.
- Mutantes (`bin/forge-mutante tests/mutantes/v0481-g2-autoria.json`, spec=b959439c7fb5): M1 a M5 `morreu`; nenhum sobrevivente. `--cobertura --base b4ae1755`: `coberta` para as linhas 4079 e 4084 (M5, M2); `não coberto: tests/pesos-d4.json` (dado, não guarda). Mutantes cobrem as linhas de guarda mudadas (4068, 4069, 4079, 4084, 4086).
- Diff conferido contra o escopo: só `hooks/conformidade.py` (16 linhas), `bin/forge-testes` (registra o módulo novo nas listas que executam o `forge-check` e os hooks), pesos, fixtures, spec de mutantes e changelog.
- CI do PR #914 no head exato: 5+5 partes da suíte (3.12 e 3.14), `bateria (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)`, `instalação`, `teto de pulados` e `árvore já provada` verdes. Vermelhos esperados: `catraca` (log: `R-CONFORMIDADE: mudança em hooks/conformidade.py ... só passa com o rótulo afrouxa-regra do dono`; decisão do dono, fora do QA), `bateria (pareceres)` e `bateria` (esperam os pareceres).
- ci: f0c380e28827a0c6168b142dd65d3499faef0dd7 verde
- suíte: local só os módulos tocados rc=0 módulos=test_conformidade_pareceres,test_forge_pareceres
