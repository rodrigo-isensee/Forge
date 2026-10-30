---
tipo: qa
contrato: 1
pedido: pn4-decisao-aprovacao
branch: melhoria/pn4-decisao-aprovacao
commit: 8ebaa9540c4019591558de816c0bda8775250cee
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: pn4-decisao-aprovacao

Parecer de QA (`R-QA`) da P-N4 sobre 8ebaa95, em paralelo com review e segurança (decisão ACELERA-RODADA). Base add00ab. Diff conferido: `bin/forge-check`, `bin/forge-testes` (mapa FORGE_CHECK), teste novo, spec de mutantes, fragmento de changelog e a conta 31 para 32 em `tests/test_testes_tocados.py`. Escopo do pedido (E1 e E2) preservado, sem mudança no formato de `conferencias.md`.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 brief aprovado, decisão com data e hora posteriores faltando: aviso, rc 0 | test_aprovado_com_decisao_posterior_avisa_e_passa | decisão logo após a aprovação | passou |
| E1 brief aprovado, decisão anterior faltando: reprova | test_aprovado_com_decisao_anterior_faltando_reprova | anterior à aprovação | passou |
| E1 brief sem aprovação: cobra tudo | test_sem_aprovacao_cobra_tudo | sem linha no registro | passou |
| E1 vale a última linha `aprovado` | test_vale_a_ultima_aprovacao | duas aprovações | passou |
| E1 hora igual à da aprovação segue cobrada | test_hora_igual_a_da_aprovacao_segue_cobrada | igualdade | passou |
| E1 decisão sem hora segue cobrada | test_decisao_sem_hora_segue_cobrada | data sem hora | passou |
| E1 reprovação, outro brief, outro modo e hora torta não valem | test_reprovacao_outro_brief_outro_modo_ou_hora_torta_nao_valem_como_aprovacao | 4 linhas falsas | passou |
| E2 mapa FORGE_CHECK roda o módulo novo | tests.test_testes_tocados (88 testes com o anterior) | contagem 32 | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_decisao_aprovacao tests.test_testes_tocados`: 88 testes, OK.
- Mutantes (`bin/forge-mutante tests/mutantes/pn4-decisao-aprovacao.json`): M1 a M13 morreram, rc=0.
- `bin/forge-mutante --cobertura --base add00ab...` (chamada separada): linhas 4341, 4343, 4349, 4418, 4431 e 4433 cobertas por M1 a M13; 4333 (M7) e 4625 (M10) também. Nenhuma linha de guarda mudada sem mutante.
- Vermelho (`bin/forge-testes --vermelho add00ab... --modulos test_decisao_aprovacao`), rc=0: `test_aprovado_com_decisao_posterior_avisa_e_passa` H=ok B=falha, prova (asserção). Os outros 6 passam na base porque guardam o comportamento antigo (regressão); a prova deles é a mutação acima.
- `scripts/verificar-contribuicao.sh origin/develop`: rc=0, sem segredo nem caminho pessoal.
- Leitura do diff: sem aprovação, `decisao_posterior` devolve False antes de comparar com None; comparação de texto `AAAA-MM-DD HH:MM` é ordenável; `brief gerar` e `hooks/` não foram tocados.
- Acessibilidade e E2E de navegador: n/a (ferramenta de linha de comando).
