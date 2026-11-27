---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-pesos-gerados
commit: f9fa7be39c883bc3da77a43669223e8e50813f32
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 E19.8, PESOS-GERADOS (#909), volta por delta

Delta lido: `git diff cb924113..f9fa7be3` (só `tests/mutantes/v0481-pesos-gerados.json`, +12 linhas, e os pareceres). Fecha o A1 da 1.ª rodada: as duas guardas apagadas (bin/forge-testes 965 e 967 da base) entraram em `isentas` com motivo "código removido". Os recomendados A2 e A3 da 1.ª rodada seguem como cartão (Melhoria vista), fora desta volta.

- ci: f9fa7be39c883bc3da77a43669223e8e50813f32 verde

`gh pr checks 909` no `Revisar-sha`: suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), bateria (verificações longas) e instalação verdes. Vermelhos fora da conta: `bateria (pareceres)` e `bateria` (esperam os pareceres) e `catraca`, lida no log do run 45832767176: só R-CONFORMIDADE (asserções 17860 para 17858 e cinco testes de controle apagados ou afrouxados), o afrouxamento de PR-VERDE C1 que o dono aceitou em 26/11 10:4x e que pede o rótulo `afrouxa-regra`. Nenhuma linha R-QA: a falha de guardas sem mutante sumiu.

Provas desta volta:
```
bin/forge-mutante --cobertura --base 8ae4d6c63c27aed480d822c66f361f53d8d4594d   (rc 0)
coberta · bin/forge-testes:979 · tests/mutantes/v0481-pesos-gerados.json:PG2 · declarado, não provado
isenta · bin/forge-testes:967(base) · código removido: o filtro de módulo novo sem peso saiu com a função; ...
isenta · bin/forge-testes:965(base) · código removido: a leitura do tests/pesos-d4.json ...
```
Mutantes PG1 a PG4: sem mudança no delta (a spec só ganhou `isentas`) e código de produção intocado; o resultado da 1.ª rodada vale.

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
