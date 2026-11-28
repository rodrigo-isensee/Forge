---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-c1-pesos
commit: a94644bcdf3a3407f4ea92ed98389050e5c644f6
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E57.36 (PR-VERDE C1, pesos da suíte por PR)

Diff `5ccac0bf..a94644bc`: `tests/test_forge.py` (classe `PesosDaSuite`: regra por PR no lugar do limite global de 20%), `tests/test_suite_paralela.py` (+1 asserção do comando de medir), `scripts/suite-paralela.py` (+1 linha no resumo do CI), `skills/trabalho-em-paralelo/ritmo-e-corte.md`, fragmento do changelog. Sem suíte local (o CI do PR roda a bateria).

## Critério → teste → resultado
| Obrigação (E57.3/E57.4) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Módulo novo do PR sem peso reprova | `PesosDaSuite.test_regra_por_pr` + `test_pr_nao_aumenta_os_modulos_sem_peso` | novo sem medida | passou; reprova ao criar `tests/test_zz_novo.py` sem peso (cópia) |
| Módulo da base com peso não o perde | `test_regra_por_pr` | peso removido | passou; reprova ao apagar um peso (cópia) |
| Sem peso vindo da base passa; módulo apagado passa | `test_regra_por_pr` | base sem peso; apagado | passou |
| Módulo de pacote só vale com `__init__.py` em todo nível | `test_modulos_de_pacote_e_da_raiz` | sem `__init__`, nome com `-`, fora de `tests/` | passou |
| Sem merge-base com a develop não passa calado | `test_pr_nao_aumenta_os_modulos_sem_peso` (mensagem) | base vazia | passou |
| Resumo do CI diz o comando de medir | `test_suite_paralela.Brinquedo.test_resumo_do_ci_lista_os_modulos_sem_peso` | n/a | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_forge.py -k PesosDaSuite`: 3 testes, OK.
- `python3 -I -m unittest discover -s tests -p test_suite_paralela.py` (TMPDIR da sessão): 75 testes, OK, rc=0.
- Mutação em cópia de `violacoes_de_peso` (3 mutantes: inverter o teste de peso do novo; tirar a condição "tinha peso na base"; contar todo módulo como novo): os 3 mortos por `test_regra_por_pr` (falhas 2, 5 e 5).

## Vermelho antes do verde
```
vermelho: base=5ccac0bf616c head=a94644bcdf3a módulos=test_suite_paralela (restrito por --modulos)
tests.test_suite_paralela.Brinquedo.test_resumo_do_ci_lista_os_modulos_sem_peso · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=74; prova (asserção)=1
```
`--modulos test_forge`: `test_forge H 600.0 s, B 600.1 s` e `contagem: sem veredito=1`, rc=2 (o módulo estoura o prazo de 600 s; não vale como vermelho). Para a classe `PesosDaSuite` o vermelho vale pelas cópias descritas acima (a regra nova falha com o módulo sem peso e com o peso removido; verde no head limpo). Parte da regra antiga (limite de 20%) deixou de existir, então o teste novo não roda contra a base.

## Fusão com a develop
`origin/develop` avançou (c219c86b; merge-base 5ccac0bf). Não simulei o merge: a regra por PR depende do merge-base, e o CI do PR o confere no merge real.
