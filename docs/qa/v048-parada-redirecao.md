---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-parada-redirecao
commit: 101050172f9ce1e6717263a826cde736e4117917
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 (HOOK-PARADA-CONTA-REDIRECAO, E12.3, classe C)

- ci: 101050172f9ce1e6717263a826cde736e4117917 verde

Check-runs do commit: suíte 3.12 partes 1 a 5, bateria passos, verificações longas, python 3.14, catraca e conferência, todos success.

Mudança: `_DESCARTE` em `hooks/vigia.py` tira a redireção para /dev/null (N>, >, >>, &>) entre separadores antes de calcular alvo e verbos do contorno. Os commits posteriores ao head só tocam docs/reviews e docs/security.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Ler o alvo barrado com `2>/dev/null` (e `>`, `&>`, `2>>; true`, subshell) não é contorno | `DescarteNaoConta.test_ler_o_alvo_barrado_com_2_dev_null_nao_e_contorno`; fixture `descarte-dev-null-nao-conta.json` (Stop sem violacoes.jsonl) | grafias com e sem espaço, `;`, `(` | passou; vermelho na base |
| `/dev/null` não é alvo comum entre duas chamadas | `test_dev_null_nao_e_alvo_comum_entre_duas_chamadas` | alvo `/r/tools/y.py` sem `/dev/null` | passou; vermelho na base |
| Escrita no alvo barrado com `2>/dev/null` no fim segue contorno | `test_escrita_no_alvo_barrado_com_2_dev_null_no_fim_e_contorno` | `cp`, `>`, `tee </dev/null >/dev/null` | passou; guarda de regressão (verde na base, esperado) |
| `/dev/null` colado a outra grafia segue contando | `test_dev_null_colado_a_outra_grafia_segue_contando_como_escrita` | lookahead de fim | passou; mutante M2 morto |
| Redireção colada à palavra anterior fica | `test_redirecao_colada_a_palavra_anterior_fica` | lookbehind | passou; mutante M3 morto |

## Provas locais
vermelho (`bin/forge-testes --vermelho d056c2ca --modulos test_vigia_descarte`):
```
vermelho: base=d056c2ca0b2e head=101050172f9c módulos=test_vigia_descarte (restrito por --modulos)
revertidos à base: changelog.d/v048-parada-redirecao.md, docs/hooks-fixtures.md, hooks/vigia.py
... test_dev_null_nao_e_alvo_comum_entre_duas_chamadas · H=ok · B=falha · prova (asserção)
... test_ler_o_alvo_barrado_com_2_dev_null_nao_e_contorno · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=3; prova (asserção)=2
```
Os 3 que passam na base são guardas de que a escrita segue contando; a prova de que não afrouxaram vem dos mutantes.

mutantes (`bin/forge-mutante tests/mutantes/v048-parada-redirecao.json`, rev=101050172f9c): M1, M2, M3, M4 morreram; um mutante por linha de guarda do diff (a chamada de substituição e as 3 condições da regex).

Fixtures do vigia: 62 arquivos em `tests/hooks/vigia/` (o novo incluído); `descarte-*` registrado em `docs/hooks-fixtures.md`. A suíte completa no CI os roda e passou. A rodada local de test_hooks e afins foi interrompida por prazo; vale o CI do head.

Sondagem extra de abuso (à mão): `echo x >/dev/null >.git/config`, `2>/dev/null >.git/config`, `>/dev/null;>.git/config` e `>/dev/null/../../r/.git/config` mantêm o verbo `>`, ou seja, seguem contando como escrita.
