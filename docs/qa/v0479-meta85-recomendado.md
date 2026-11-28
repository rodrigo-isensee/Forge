---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-recomendado
commit: eba8b7d01c0dd892615d9846c97c8eeb17dd6f34
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-19
---
# QA: v0478 (META85, recomendado vira cartão)

Mudança só de texto (regras, agentes, skills, modelos) mais `tests/config.json` e `tests/test_achado_teto_doc.py`; sem código de produção nem controle.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| R-REVIEW: recomendado de review e QA vira cartão, o de segurança volta | `RecomendadoViraCartao.test_cada_texto_que_decide_a_volta_traz_a_regra` (12 arquivos, mínimo 12) | lista de textos não esvazia | passou; cai na base |
| Passo 6 do Jarvis separa os dois | `test_o_passo_6_do_jarvis_separa_review_e_qa_da_seguranca` | n/a | passou; cai na base |
| Brief de volta só inclui o recomendado da segurança | `test_o_brief_de_volta_inclui_so_o_recomendado_da_seguranca` | n/a | passou; cai na base |
| Regra antiga some dos textos | `test_nenhum_texto_manda_corrigir_antes_o_recomendado_de_review_ou_qa` (mínimo 13) | frases antigas ausentes | passou; cai na base |
| Invariantes protegem a frase nova | `tests/config.json` (R-REVIEW, autor-ate-o-merge) | n/a | módulos de texto verdes |

## Cenários e resultado real
Vermelho (`bin/forge-testes --vermelho eca1d21b --modulos test_achado_teto_doc`, rc=0):
```
vermelho: base=eca1d21b18ee head=cdea2f3807f4 módulos=test_achado_teto_doc (restrito por --modulos)
RecomendadoViraCartao.test_cada_texto_que_decide_a_volta_traz_a_regra · H=ok · B=falha · prova (asserção)
RecomendadoViraCartao.test_nenhum_texto_manda_corrigir_antes_o_recomendado_de_review_ou_qa · H=ok · B=falha · prova (asserção)
RecomendadoViraCartao.test_o_brief_de_volta_inclui_so_o_recomendado_da_seguranca · H=ok · B=falha · prova (asserção)
RecomendadoViraCartao.test_o_passo_6_do_jarvis_separa_review_e_qa_da_seguranca · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=4; prova (asserção)=4
rc=0
```
Os 4 que passam na base são testes antigos (AchadoTetoDoc, ParecerCurto), não novos.

Módulos de orçamento e textos, no head, em segundo plano, `python3 -I -m unittest`, rc=0: test_orcamento_instrucao (8), test_textos_034 (9), test_brief_tamanho (3), test_forge_tamanho (24), test_aq1_texto (6), test_achado_teto_doc (8), test_textos_ci_custo (5), todos OK. Suíte completa: fica no CI do PR (check-run `bateria`), não rodada aqui. Mutação: sem código de produção no diff, não se aplica.

## Revalidação
- Head aprovado: `eba8b7d0` (descendente de `cdea2f38`). Retestado nesse head: `test_metricas_texto` (2) OK, `test_achado_teto_doc` (8) OK.
- `test_forge.AntiDuplicacao` falhou na rodada anterior por texto copiado no parecer de segurança (fora do domínio do QA); corrigido em `fc05832a`. Depois do merge de `origin/melhoria/v0479-meta85-recomendado` (head `bd890048`), rodado de novo: Ran 2 tests, OK, rc=0.
- Diferença `eba8b7d0..bd890048`: só `docs/reviews/` e `docs/security/` (pareceres, fora do domínio do QA); nenhum código, teste ou regra mudou.
- `forge-check parecer delta` avisou que o merge de `fc05832` não está na `origin/develop` local, então o intervalo conta inteiro; não muda o veredito.
