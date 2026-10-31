---
tipo: qa
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c2
commit: 40472ddba9cf8d420f42b8518f2d6f81c147ec14
parecer: aprovado
escopo: completo
revisor: forge:qa-engineer
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-n-ci (c2)

## Achados
- A1 (recomendado) tests/test_suite_paralela.py:338 · mutantes R5 (soma zerada) e R10 (soma ÷ N errado) sobreviveram: o teste só confere o formato `\d+\.\d`, não o valor. Informa e nunca reprova; vale um teste com sleep conhecido na próxima vez que o arquivo for tocado.
- A2 (recomendado) scripts/suite-paralela.py:428 · mutante R8 (sem o filtro `k in nomes` das durações) sobreviveu: nenhum teste põe nome fora de `partes` no relatório. O filtro é defesa em profundidade do C-9; um teste com relatório forjado o prova.
- A3 (recomendado) scripts/suite-paralela.py:452 · mutante R9 (`raise` no `except OSError` da escrita do resumo) sobreviveu: nenhum teste com `GITHUB_STEP_SUMMARY` não gravável mostra que o veredito segue. É o C-12, que o pedido põe na c3 (veredito protegido); conferir lá.
- A4 (recomendado) tests/test_suite_paralela.py:343 · três testes novos caem na base por `IndexError`/`ValueError`, não por asserção; `forge-testes --vermelho` sai 2 por isso. Vermelho real (ver abaixo), mas asserir a presença do trecho antes de indexar dá uma falha legível.

## O que a branch entrega e a M14
- Item do pedido: E2 (item 55 d), a parte de medida: unidades mais lentas (10), soma, soma ÷ N, maior unidade, desequilíbrio, módulos sem peso (até 20, "e mais N") no resumo do passo, e os módulos no título do `::group::`. Só informação; a divisão e o veredito não mudam. O veredito protegido (C-6 a C-8) é da c3.
- M14 (agents/tech-lead.md:19): cumpre. Contam 117 linhas (`scripts/suite-paralela.py` 44, `tests/test_suite_paralela.py` 73), abaixo de 150; fragmento fora da conta. Sem `hooks/` nem `PROTEGIDOS`. Um comportamento (a medida no resumo).
- O escopo do pedido não mudou: E2 inteiro menos a parte da c3, que o próprio pedido separa.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2 unidades mais lentas | `test_resumo_do_ci_traz_as_unidades_mais_lentas` | a mais lenta vem primeiro | passou |
| E2 soma, maior unidade, desequilíbrio | `test_resumo_do_ci_traz_soma_maior_unidade_e_desequilibrio` | formato (valor: A1) | passou |
| E2 sem peso | `test_resumo_do_ci_lista_os_modulos_sem_peso` | arquivo de pesos com 1 módulo | passou |
| C-11 resumo curto | `test_resumo_limita_as_unidades_sem_peso` | 27 módulos: 10 lentas, 20 sem peso, "e mais 10" | passou |
| E2 grupo do CI | `test_grupo_do_ci_traz_as_unidades_do_processo` | 3 grupos com módulos | passou |
| C-9 só nomes e números | `test_resumo_so_leva_nomes_e_numeros` | `::`, caminho, token na saída do filho | passou |
| sem `GITHUB_STEP_SUMMARY` | `test_sem_github_step_summary_nada_e_escrito` | variável ausente | passou |
| C-12 divisão não depende da execução anterior | `test_divisao_nao_depende_da_execucao_anterior` | tempos diferentes, mesma divisão | passou |

## Vermelho antes do verde
`forge-testes --vermelho 234dbe0… --modulos test_suite_paralela` (rc 2, abre com `vermelho: base=234dbe0fb90b head=c78f54fe2ba7`):
```
test_resumo_do_ci_lista_os_modulos_sem_peso · H=ok · B=falha · prova (asserção)
test_resumo_do_ci_traz_soma_maior_unidade_e_desequilibrio · H=ok · B=falha · prova (asserção)
test_grupo_do_ci_traz_as_unidades_do_processo · H=ok · B=erro · sem veredito
test_resumo_do_ci_traz_as_unidades_mais_lentas · H=ok · B=erro · sem veredito
test_resumo_limita_as_unidades_sem_peso · H=ok · B=erro · sem veredito
contagem: não prova (passa na base)=26; prova (asserção)=2; sem veredito=3
```
Os 3 "sem veredito": rodei à mão na base (`git archive 234dbe0` mais o teste do head): `IndexError: list index out of range` (2) e `ValueError: not enough values to unpack` (1), isto é, o trecho ausente da base; vermelho real (A4). Os dois "passa na base" que são deste PR (`test_resumo_so_leva_nomes_e_numeros`, `test_sem_github_step_summary_nada_e_escrito`, `test_divisao_nao_depende_da_execucao_anterior`) são contraprovas declaradas pelo autor e pelo desenho §3.2.

## Mutação (`scripts/` não é pedido de controle; spec minha, fora da árvore)
`forge-mutante`: R1 `LIMITE_LENTAS` 5: morreu; R2 `LIMITE_SEM_PESO` 30: morreu; R3 sem lista de sem peso: morreu; R4 desequilíbrio com `min`: morreu; R7 ordem invertida: morreu; R5, R8, R10: sobreviveram (A1, A2). R6 (grupo sem módulos): `inválido` no forge-mutante, e à mão `ERROR: test_grupo_do_ci_traz_as_unidades_do_processo`, morreu. R9: o trecho repetido no arquivo; à mão, `OK`, sobreviveu (A3). Os mutantes do §5.1 do desenho (resumo sem a lista ou sem as unidades sem peso) morreram.

## Cenários e resultado real
- `python3 -m unittest tests.test_suite_paralela tests.test_pesos_teto tests.test_changelog`: `Ran 79 tests`, `OK`.
- Sem interface nem API: acessibilidade e contrato não se aplicam. Sem bugs abertos.
