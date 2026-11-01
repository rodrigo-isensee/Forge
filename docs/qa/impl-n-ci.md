---
tipo: qa
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c3
commit: 44617ead4fee4eab8193b8e07cda121e45f5cf2b
parecer: aprovado
escopo: completo
revisor: forge:qa-engineer
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-n-ci (c3)

## Achados
- A1 (recomendado) tests/test_suite_paralela.py:279 · o contraste do C-7 (medida só no verde) fica em dois testes; o caso verde de test_resumo_comeca_pelo_veredito confere só a primeira linha. Basta, pois os mutantes Q2 e Q3 morreram; é o mesmo A1 do review.

## O que a branch entrega e a M14
- Item do pedido: E2 (item 55 d), a segunda metade: o veredito protegido (C-6 a C-8, e o C-12 que o A3 do QA da c2 deixou para cá). O veredito sai impresso antes do resumo; erro ao montar ou gravar o resumo vira "resumo indisponível" no stderr sem mudar o código; o resumo abre com o veredito; execução FAILED não leva as linhas da medida e vale "não vale para o orçamento"; módulo sem duração é listado.
- M14 (agents/tech-lead.md:19): cumpre. `scripts/suite-paralela.py` 28+13 e `tests/test_suite_paralela.py` 80+15 = 136 linhas, abaixo de 150; fragmento e pareceres fora da conta. Sem `hooks/` nem `PROTEGIDOS`; um comportamento só. Sem exceção.
- Escopo do pedido inalterado; a c3 aplica a proteção às linhas de medida da c2, já na develop (#408).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C-6 resumo não muda veredito nem código | `test_resumo_nao_muda_o_veredito` | destino não gravável e `montar_resumo` que levanta, em verde e em vermelho | passou |
| C-7 veredito primeiro, FAILED sem medida | `test_resumo_comeca_pelo_veredito` | OK e FAILED; 4 linhas da medida ausentes no FAILED | passou |
| C-8 processo morto, módulo sem duração | `test_resumo_com_processo_morto_nao_quebra_o_veredito` | SIGKILL no filho; "sem duração: test_b" | passou |
| C-10 teste do orquestrador não escreve no resumo real | `test_orquestrar_no_processo_nao_escreve_no_resumo_real` | `GITHUB_STEP_SUMMARY` e `GITHUB_ACTIONS` setados | passou |
| guarda de completude segue reprovando | `test_guarda_reprova_quando_um_modulo_some` | módulo ausente | passou |

## Vermelho antes do verde
`forge-testes --vermelho c162bcb… --modulos test_suite_paralela` (rc 0; abre com `vermelho: base=c162bcb42af8 head=b8d76a84a569`; head é o HEAD da worktree, com os pareceres à frente de 44617ea, sem mudança de código):
```
test_resumo_com_processo_morto_nao_quebra_o_veredito · H=ok · B=falha · prova (asserção)
test_resumo_comeca_pelo_veredito · H=ok · B=falha · prova (asserção)
test_resumo_nao_muda_o_veredito · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=32; prova (asserção)=3
```
Os 32 "passa na base" são testes herdados ou contraprovas (o teste de ausência do `orquestrar_no_processo` e o de guarda só trocaram de mecanismo).

## Mutação (`scripts/` não é pedido de controle; spec minha, fora da árvore, 11 mutantes sobre C-6 a C-8; o §5.1 do desenho só declara mutantes do resumo da c2, que o QA da c2 já rodou)
`forge-mutante --rev 44617ead4fee --prazo 900` (rc 2 por Q1, abaixo):
```
Q2 · morreu · scripts/suite-paralela.py:432   (FAILED sem o retorno antecipado)
Q3 · morreu · :430   (sem a linha "sem duração")
Q4 · morreu · :425   (veredito fora do título)
Q5 · morreu · :462   (sem a mensagem "resumo indisponível")
Q6 · morreu · :429   (sem_duracao vazio)
Q7 · morreu · :532   (FAILED devolve código 0)
Q8 · morreu · :536   (orquestrar devolve 0)
Q9 · morreu · :458   (montar_resumo fora do try)
Q10 · morreu · :533  (fechar_verde também no vermelho)
Q11 · morreu · :59   (limite de sem duração 0)
Q1 · inválido · :461 (except OSError em vez de Exception)
```
Q1 saiu "inválido" (erro de execução do teste, não falha de asserção); rodei à mão: `ZeroDivisionError: division by zero` em `tests/test_suite_paralela.py:311`, `FAILED (errors=1)`: o teste cai, o mutante morre. Worktree restaurada (`git status` limpo). Nenhum sobrevivente.

## Cenários e resultado real
- `python3 -m unittest tests.test_suite_paralela` em 44617ea: `Ran 35 tests in 30.974s`, `OK`.
- Sem interface nem API: acessibilidade e contrato não se aplicam. Sem bugs abertos.
