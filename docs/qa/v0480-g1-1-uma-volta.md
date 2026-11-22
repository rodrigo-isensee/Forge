---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-1-uma-volta
commit: 45d1fc2728a489d04950a6a304369f6f4f6e8fa5
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: G1.1, no máximo 1 volta por item (E100.4)

Passada única no head 57c0cbff. Sem suíte local: o CI do PR dá a suíte inteira. Rodados aqui só os testes do arquivo tocado e as duas specs de mutantes. A falha de `test_oraculo_sempre_atual` na develop, dita pelo autor, não foi contada.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| G1.1: a 2.ª volta é recusada pelo `brief gerar --volta` e nada é gerado | test_volta_dois_so_com_decisao_do_dono_que_cita_a_branch | volta 2 sem decisão | passou |
| A decisão só vale se citar a branch exata e a volta | mesmo teste, subTests (nome parecido `melhoria/xy`, frase no meio da linha, branch sem volta) | prefixo, formato | passou |
| Uma decisão autoriza uma volta a mais, não duas | mesmo teste (volta 3 recusada) | teto + 1 | passou |
| A conferência recusa numeração recomeçada ou pulada e volta acima do teto | test_conferencia_recusa_a_numeracao_contornada | volta 1 segue sem recusa | passou |
| Sem `Branch:` lida, teto 1 e recusa nomeia `<branch>` | test_sem_branch_nenhuma_decisao_autoriza (unitário) + probe do QA na conferência | `None`, vazio | passou (ver A1) |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_volta_por_delta.py` com TMPDIR próprio: `Ran 104 tests ... OK`.
- Sem `skip`, `skipIf` ou `expectedFailure` em `tests/test_volta_por_delta.py` (grep vazio).
- Vermelho antes do verde, `bin/forge-testes --vermelho 2d73a35e... --modulos test_volta_por_delta` (rc 0):
  `vermelho: base=2d73a35e75b9 head=57c0cbffa460 módulos=test_volta_por_delta (restrito por --modulos)`;
  `test_conferencia_recusa_a_numeracao_contornada · H=ok · B=falha · prova (asserção)`;
  `test_sem_branch_nenhuma_decisao_autoriza · H=ok · B=erro · prova (API ausente)`;
  `test_volta_dois_so_com_decisao_do_dono_que_cita_a_branch · H=ok · B=falha · prova (asserção)`;
  `contagem: não prova (passa na base)=101; prova (API ausente)=1; prova (asserção)=2`.
- Mutantes, `bin/forge-mutante` nas duas specs, rc 0, 9 de 9 mortos:
  `M1 · morreu · bin/forge-check:4257 · (erro) o teste declarado deu erro sob o mutante e passa sem ele`; M2 4260; M3 4259; M4 4265; M5 4292; M6 4418; M7 4421; M8 4251; M9 4267, todos `morreu`.
- `forge-mutante --cobertura --base 2d73a35e...`: todas as condições mudadas `coberta`; `isenta · bin/forge-check:4312(base)` com motivo, sem `isenta velha`.
- Caso sem `Branch:` (probe em `$TMPDIR` do QA, brief de volta 2 com a decisão presente e a linha `Branch:` removida): a conferência emite `volta: volta 2 recusada para "<branch>"`; com a linha, sem recusa. Falha fechada, como declarado.
- Revisão do diff contra a lista de guardas: cada linha de guarda mudada tem mutante (1 isenta declarada).

## Revalidação no head 8522e8fe (delta sobre 57c0cbff)
- Delta lido por `forge-check parecer delta`: forge-check (voltas_autorizadas, voltas_da_branch, conferir_volta), as 3 specs de mutantes e `tests/test_volta_por_delta.py`.
- Vermelho antes do verde, `forge-testes --vermelho 57c0cbff --modulos test_volta_por_delta` (rc 0): `base=57c0cbffa460 head=8522e8fe58bc`; provam (asserção) em BriefDeVolta: test_so_a_forma_canonica_autoriza_e_uma_linha_vale_uma_volta, test_volta_conta_o_item_e_nao_a_cadeia, test_volta_sem_volta_de_e_recusada, test_conferencia_sem_branch_no_anterior_e_teto_um (A1). `test_volta_de_outro_item_nao_conta` e `test_conferencia_sem_cobradas_le_as_decisoes_do_pedido` (A2) passam na base: guardam comportamento que o código antigo já tinha; a prova delas é o mutante, não o vermelho. Contagem: prova=4, não prova=106.
- Mutantes M1 a M22 nas três specs, `forge-mutante --processos 3`, rc 0, 22 de 22 `morreu` (M21 cobre o fallback `cobradas or` do A2); `--cobertura --base 2d73a35e`: tudo `coberta`, uma `isenta` declarada, sem `isenta velha`.
- Sem `skip`, `skipIf` ou `expectedFailure` em tests/test_volta_por_delta.py (grep 0).
- `test_volta_tira_o_fora_do_escopo_do_pedido`: o ajuste só apaga o brief -2 criado antes (o anterior com volta não gera outra); as asserções do corte do dono ficam; sem enfraquecimento.
- A1 e A2 do parecer anterior resolvidos (teste e mutante). Sem achados abertos.

## Revalidação no head 4d2c5333 (delta sobre 8522e8fe, volta 2)
- Delta lido por `forge-check parecer delta`: forge-check (`branch_do_anterior_diferente`, `VOLTA_NA_DECISAO` até o fim da linha), fixture `volta-anterior.md`, specs `-3` (M23) e `-4` (M24 a M28) e os testes de volta.
- Testes afetados, `python3 -I -m unittest discover -s tests -p <arquivo>` com TMPDIR próprio: test_volta_por_delta `Ran 113 ... OK`; test_conferencia_base_dono `Ran 34 ... OK`; test_etapa_do_brief `Ran 89 ... OK`. Sem `skip`/`expectedFailure` novo no diff.
- Teste mudado: `→ "pode"` agora recusado (a forma canônica vai até o fim da linha) e `→ "não"` somado ao grupo de recusa; endurece, não afrouxa.
- Mutantes, `forge-mutante spec-3 spec-4 --base 8522e8fe` (`mb=8522e8fe`): M16, M18 a M28 `morreu`; **M17 `sobreviveu · bin/forge-check:4273`**.
  Causa: `branch_do_anterior_diferente` agora recusa o anterior sem `Branch:` antes de `voltas_da_branch`, então `bool(branch) and` ficou sem efeito observável pelo teste declarado (guarda morta ou redundante).

## Revalidação no head e103b9a6 (delta sobre 4d2c5333, volta 3)
- Delta lido por `forge-check parecer delta`: `bin/forge-check` (apagado o `bool(branch) and` morto em `voltas_da_branch`) e specs `-2` (M9 único, M11 fora) e `-3` (M16 ajustado, M17 fora).
- Mutantes, `forge-mutante` nas 4 specs com `--base 4d2c5333` (`base=4d2c5333 mb=4d2c5333 rev=e103b9a6`), rc 0: M1 a M10, M12 a M16, M18 a M28 todos `morreu`, nenhum sobrevivente (M16 em bin/forge-check:4273 e M9 em :4293 morreram).
- `forge-mutante --cobertura --base 2d73a35e` rc 0, sem condição descoberta nem `isenta velha`.
- Testes afetados, `python3 -I -m unittest discover -s tests -p <arquivo>` com TMPDIR próprio: test_volta_por_delta `Ran 113 ... OK`; test_conferencia_base_dono `Ran 34 ... OK`; test_etapa_do_brief `Ran 89 ... OK`. Nenhum teste mudado no delta, sem `skip`.
- A1 resolvido: guarda morta removida e M17 retirado junto. M11 saiu porque o trecho que ele mutava deixou de existir desde a volta anterior (`VOLTA_NA_DECISAO` até o fim da linha); a recusa de `melhoria/xy` segue no teste de forma canônica. Sem achados abertos.

## Revalidação no head 45d1fc27 (delta sobre e103b9a6, volta 4)
- Delta lido por `forge-check parecer delta`; o que muda de teste é o commit 45d1fc27 (`tests/test_forge.py`, `tests/test_revisor_wt.py`), fora o merge da develop.
- Diff dos testes: o anterior de `VoltaComRecomendacao` ganha a linha `Branch: melhoria/x   Base: develop` (fixture do item), e dois testes apagam o `-2.md` que eles mesmos gravaram antes de gerar de novo. Só 4 linhas somadas e 1 trocada: nenhuma asserção removida nem afrouxada.
- Os testes ainda falham sem a guarda: numa cópia sem as duas linhas `unlink`, `VoltaComRecomendacao` cai (`test_recomendacao_incluida_sem_decisao_tecnica...`) e `VoltaLeParecerConferido` cai com `já tem volta; gere a partir do último brief da branch`. A recusa do G1.1 está viva e o `unlink` só tira o brief que a própria guarda barraria.
- Testes afetados, `python3 -I -m unittest` com TMPDIR próprio: `test_forge -k VoltaComRecomendacao` `Ran 16 ... OK`; `test_revisor_wt.py` `Ran 40 ... OK`. Sem `skip`/`expectedFailure` somado. Código de produção igual ao e103b9a6 (delta só de teste): mutantes não rerrodados.
- Sem achados abertos.
