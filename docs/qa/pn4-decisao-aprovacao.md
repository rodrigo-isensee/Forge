---
tipo: qa
contrato: 1
pedido: pn4-decisao-aprovacao
branch: melhoria/pn4-decisao-aprovacao
commit: e2f3390adad9be87cca02a42d37bde2411812ff4
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: pn4-decisao-aprovacao

Parecer de QA (`R-QA`) da volta 1 da P-N4 sobre e2f3390, por delta ddcf322..e2f3390 (revalida o parecer anterior, 0321b6b, sobre 8ebaa95). Base add00ab. Delta conferido: `hora_da_aprovacao` agora só aceita a linha `aprovado` com hora >= mtime do brief (minuto, fuso local), fechando o A1 da segurança; mutantes M14 e M15, dois testes de borda e a contagem de `test_testes_tocados`. Escopo do pedido preservado; `conferencias.md` sem mudança de formato.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 aprovado, decisão posterior faltando: aviso, rc 0 | test_aprovado_com_decisao_posterior_avisa_e_passa | aprovação 10:00 com brief escrito 10:00:30 (mesmo minuto vale) | passou |
| E1 aprovado, decisão anterior faltando: reprova | test_aprovado_com_decisao_anterior_faltando_reprova | anterior à aprovação | passou |
| E1 sem aprovação: cobra tudo | test_sem_aprovacao_cobra_tudo | sem linha no registro | passou |
| E1 vale a última aprovação | test_vale_a_ultima_aprovacao | duas aprovações | passou |
| E1 hora igual à da aprovação segue cobrada | test_hora_igual_a_da_aprovacao_segue_cobrada | igualdade | passou |
| E1 decisão sem hora segue cobrada | test_decisao_sem_hora_segue_cobrada | data sem hora | passou |
| E1 reprovação, outro brief, outro modo, hora torta e aprovação retrodatada (09:59, antes do mtime) não valem | test_reprovacao_outro_brief_outro_modo_hora_torta_ou_retrodatada_nao_valem_como_aprovacao | 5 linhas falsas, limite do mtime | passou |
| E2 mapa FORGE_CHECK roda o módulo novo | tests.test_testes_tocados | contagem 32 | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_decisao_aprovacao tests.test_testes_tocados` sobre e2f3390: 88 testes, OK.
- Mutantes (`bin/forge-mutante tests/mutantes/pn4-decisao-aprovacao.json`, rc=0): M1 a M15 morreram. A lista confere com o diff: uma linha de guarda mudada com mutante cada (4342 a 4344, 4350, 4419, 4432, 4434, 4626, regex 4333); M14 (tira o `>= escrita`) e M15 (`>=` vira `>`) cobrem a guarda nova.
- `bin/forge-mutante --cobertura --base add00ab...` (chamada separada), rc=0: linhas 4342, 4344, 4350, 4419, 4432 e 4434 cobertas ("declarado, não provado", provado pela rodada acima). Nenhuma guarda mudada sem mutante.
- Mutante extra manual (cópia em `$TMPDIR`, fora da lista): o mtime comparado com segundos (`%H:%M:%S` no lugar de `%H:%M`) derruba o teste do mesmo minuto; a truncagem ao minuto está protegida.
- Vermelho (`bin/forge-testes --vermelho ddcf322... --modulos test_decisao_aprovacao`), rc=0, saída: `vermelho: base=ddcf3221c46b head=e2f3390adad9 módulos=test_decisao_aprovacao`; `revertidos à base: bin/forge-check`; `test_reprovacao_outro_brief_outro_modo_hora_torta_ou_retrodatada_nao_valem_como_aprovacao · H=ok · B=falha · prova (asserção)`; os outros 6 passam na base (regressão do que ddcf322 já fazia, guardados por M1 a M13); contagem: prova=1, não prova=6.
- `scripts/verificar-contribuicao.sh origin/develop`: rc=0, sem segredo nem caminho pessoal.
- A1 da segurança (aprovação retrodatada ou anterior ao texto do brief): fechado no comportamento e coberto por teste (linha 09:59 cobra tudo). A2 (conferencias.md sem dono em `hooks/`) é recomendação da segurança fora do escopo, sem efeito neste parecer.
- PA-7: AR-1 (lista de mutantes completa) e AR-2 (ramo de falha com teste de comportamento: `hora_da_aprovacao` devolve None por linha torta, retrodatada ou sem linha, todas testadas) conferidos, sem ocorrência nova.
- Acessibilidade e E2E de navegador: n/a (ferramenta de linha de comando).
