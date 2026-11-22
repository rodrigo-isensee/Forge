---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-1-uma-volta
commit: 57c0cbffa460dfdd6ea459f31e32f398f7262a4c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: G1.1, no máximo 1 volta por item (E100.4)

Passada única no head 57c0cbff. Sem suíte local: o CI do PR dá a suíte inteira. Rodados aqui só os testes do arquivo tocado e as duas specs de mutantes. A falha de `test_oraculo_sempre_atual` na develop, dita pelo autor, não foi contada.

## Achados
- A1 (recomendado) tests/test_volta_por_delta.py:1027 · o caso sem `Branch:` só tem teste unitário (voltas_autorizadas e recusa_da_volta). Falta teste de `conferir_volta` com brief sem a linha: a probe do QA recusou, mas nenhum teste guarda isso. Vira cartão.
- A2 (recomendado) tests/mutantes/v0480-g1-1-uma-volta.json:54 · o fallback `cobradas or {"fontes": ...}` da conferência não tem mutante próprio (o M7 só neutraliza a condição inteira). Vira cartão.

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
