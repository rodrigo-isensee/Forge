---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-pesos-gerados
commit: cb924113ca811f1c5172f7aad569e2b22b7a4595
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 E19.4, PESOS-GERADOS (#909), 1.ª rodada completa

Diff lido: `git diff 8ae4d6c6..cb924113` (merge-base com a develop), 8 arquivos. Pedido de controle (`bin/forge-testes`) e sem gatilho de segurança.

- ci: cb924113ca811f1c5172f7aad569e2b22b7a4595 verde

`gh pr checks 909` no `commit:`: suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), bateria (verificações longas), instalação, teto de pulados e árvore já provada verdes. Vermelhos esperados: `bateria (pareceres)` e `bateria` (esperam os pareceres) e `catraca` (log do run 45825156644: asserções 17845 para 17843, cinco testes de controle apagados ou afrouxados, que pedem o rótulo `afrouxa-regra` do dono, e R-QA com duas guardas apagadas sem mutante).

## Achados
- A1 (bloqueante) tests/mutantes/v0481-pesos-gerados.json:1 · R-QA: `--cobertura --base 8ae4d6c6` lista `apagada` em bin/forge-testes:967 e :965 da base e a catraca barra. Declare as duas em `isentas` com motivo (código removido); sem isso o rótulo do dono cobriria também esta falha.
- A2 (recomendado) tests/test_testes_tocados.py:1907 · `test_modulo_antigo_sem_peso_nao_e_do_pr` passa a falhar pelo mesmo motivo que `test_modulo_de_teste_novo_sem_peso_sai_0` (sem peso, rc 0): fundir ou apagar um deles.
- A3 (recomendado) scripts/suite-paralela.py:143 · `ler_pesos` devolve `{}` em silêncio se o JSON está corrompido; a única guarda é o `PesosDaSuite` (erro de JSON), sem teste que o prove. Um teste com pesos `{` e `[]` o fixaria.

## Critério → teste → resultado
Pedido sem `docs/ux`; as obrigações vêm do brief e do PR (E19.1).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E19.1-a: `--registros` não reprova módulo novo sem peso | `Registros.test_modulo_de_teste_novo_sem_peso_sai_0` | módulo novo não versionado e commitado | passou; vermelho na base |
| E19.1-b: base que não resolve segue sem veredito (2) | `Registros.test_base_que_nao_resolve_sai_2`; PG1 | base inexistente | passou; PG1 morreu |
| E19.1-c: registro vermelho segue saindo 1 | `Registros.test_changelog_reprovado_sai_1`; PG2 | falha de registro sem a conta de pesos | passou; PG2 morreu |
| E19.1-d: `--regerar` não mede peso | `Regerar.test_modulo_novo_sem_peso_nao_e_medido` | módulo novo, medidor falso como sentinela | passou; vermelho na base |
| E19.1-e: escrever os pesos no `--regerar` sai 2 | `Regerar.test_escrita_fora_da_lista_fechada_sai_2` (subteste pesos); `test_lista_fechada_sem_arquivo_de_controle_e_geradores_que_existem`; PG3 | lista fechada de derivados | passou; vermelho na base; PG3 morreu |
| E19.1-f: git ilegível no `--regerar` sai 2 | `Regerar.test_sem_veredito_sai_2_e_a_busca_que_falha_avisa`; PG4 | base sem merge-base | passou; PG4 morreu |
| E19.1-g: dois PRs com módulo novo se juntam sem conflito (a trava do item) | `Regerar.test_dois_prs_paralelos_com_modulo_novo_se_juntam_sem_conflito` | duas branches da mesma base | passou; vermelho na base |
| E19.1-h: `PesosDaSuite` barra só o módulo da base que perde o peso | `PesosDaSuite.test_regra_por_pr` e `test_pr_nao_aumenta_os_modulos_sem_peso` | módulo da base sem peso, apagado, novo | passou |
| E19.1-i: resumo do CI não manda medir | `test_suite_paralela` (resumo, linha "vale a mediana") | texto do resumo | passou |

## Cenários e resultado real
- Módulos tocados, no `commit:`: `bin/forge-testes --completa -k test_testes_tocados -k test_suite_paralela -k PesosDaSuite`: `Ran 320 tests in 180.293s`, `OK (skipped=1)` (o pulado é a prova de `/proc` do sandbox, não deste diff).
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-pesos-gerados.json`:
```
forge-mutante: pedido=v0481-pesos-gerados rev=cb924113ca81 spec=e2081661985c...
PG1 · morreu · bin/forge-testes:966
PG2 · morreu · bin/forge-testes:979
PG3 · morreu · bin/forge-testes:989
PG4 · morreu · bin/forge-testes:1018
```
- Cobertura: `bin/forge-mutante --cobertura --base 8ae4d6c63c27aed480d822c66f361f53d8d4594d` (`base=8ae4d6c6… mb=8ae4d6c6…`): `coberta · bin/forge-testes:979 · PG2`; `apagada · bin/forge-testes:967(base)` e `apagada · bin/forge-testes:965(base)`, sem mutante nem `isenta` (A1).
- Vermelho antes do verde: `bin/forge-testes --vermelho` não rodou, porque a trava da suíte (R-TETO) estava com outra sessão por mais de 10 min e o hook recusou a vez. Feito à mão, numa cópia em `$TMPDIR` do head com o `bin/forge-testes` da base: dos 7 testes novos de comportamento, 5 falharam (`test_modulo_de_teste_novo_sem_peso_sai_0`, `test_modulo_novo_sem_peso_nao_e_medido`, `test_dois_prs_paralelos_com_modulo_novo_se_juntam_sem_conflito`, o subteste `tests/pesos-d4.json` de `test_escrita_fora_da_lista_fechada_sai_2` e `test_lista_fechada_sem_arquivo_de_controle_e_geradores_que_existem`); `test_base_que_nao_resolve_sai_2` e `test_gerador_vermelho_sai_1` passam na base de propósito (comportamento mantido, guardado pelos mutantes PG1 e PG4).
- Saída R4, R5, R7 (e R6) da spec `v0478-pv-b1-registros`: justa. Os trechos `de` não existem mais no head (`--cobertura` os lista como `apagada`); o R6 virou PG1 e PG4; R1, R2, R3 e R8 seguem. A conferência dos registros nunca fica sem guarda de falha: o ramo de git ilegível tem PG1 e PG4.
- Arquivo de pesos corrompido: nenhum lugar dá mais saída 2. `--registros` e `--regerar` não leem o arquivo; o `PesosDaSuite` falha (rc 1, `registro desatualizado: pesos da suíte`), então nunca dá verde. A divisão da suíte (`ler_pesos`) degrada em silêncio para a mediana, como antes do PR (A3).
- Afrouxamento de PR-VERDE C1 (módulo novo precisa do peso): o PR o declara no título; o rótulo `afrouxa-regra` é decisão do dono, não deste parecer.
- Acessibilidade e E2E: n/a (sem interface).
