---
tipo: revisao-seguranca
contrato: 1
pedido: flaky-teto-lancador
branch: melhoria/flaky-teto-lancador
commit: b4bd24c39821e74ec66c4064a09c1f2499140aeb
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: flaky-teto-lancador

Diff revisado: `b3791ed...b4bd24c` (3 commits: `62e071a` medida temporária, `d2970bd` revert, `b4bd24c` limites; 2 arquivos no saldo: `tests/test_hooks_volta_lancador.py`, `changelog.d/flaky-teto-lancador.md`).

## Gatilhos
Controles do Forge (`R-SEGURANCA`): o teste de tempo do teto das leituras do lançador, que guarda o custo em CPU da decisão do `conformidade` atrás de lançadores encadeados. O código dos hooks não muda; só os dois limites do teste e a docstring.

## Achados

## Detalhe dos achados
Sem achado bloqueante nem recomendado. O que conferi:

1. **O controle funcional do teto não mudou.** `tests/test_hooks_volta_lancador.py:316-319` segue exigindo `K = 3`, a linha com `K` palavras fora da tabela liberada (0) e a com `K + 1` recusada (2) pelo motivo do lançador que o hook não modela; o mutante "teto" (`tests/test_hooks_volta_lancador.py:365`) continua obrigando o teste de mutações a ficar vermelho sem a checagem `gasto >= TETO_FORA_DA_TABELA`. Rodei os três testes do item (tempo do teto, `test_guarda_mede_cpu_e_nao_relogio`, mutações): `Ran 3 tests ... OK`.
2. **O limite maior não abre caminho para regressão de desempenho sem ser vista.** O tempo segue em CPU (`process_time` na `Guarda`, provado por `test_guarda_mede_cpu_e_nao_relogio`), e os novos limites (`tests/test_hooks_volta_lancador.py:322-323`: 24,5 ms máximo, 20,8 ms média) são 2x o maior p95 medido no runner (12,21 e 10,38 ms no Python 3.12), arredondado para cima na primeira casa, como manda a regra do dono de 2026-10-27 20:13. No job do 3.12, uma regressão de 2x no hook reprova o CI; o código do hook é o mesmo nas duas versões, então uma regressão real aparece nesse job. O limite antigo (10 ms de média) estava abaixo do próprio p95 do runner (10,38 ms), o que explica os vermelhos do #353 e do #354 sem relação com o diff.
3. **A medida é a do teste.** A sonda temporária (`62e071a`) mede a mesma entrada do teste (`env -Z` x3 + `env` x47 + `ls`, 20 decisões, 10 execuções) e o p95 de 10 amostras é o máximo delas (conservador). O run 40756009076 (API pública do GitHub) é `workflow_dispatch` do `.github/workflows/ci.yml` existente, `head_sha` `62e071a`, na branch `melhoria/flaky-teto-lancador`, jobs `bateria` e `bateria (python 3.14)` em `failure` (o `self.fail` da sonda, só com `CI`): nenhum workflow novo, sem custo (`R-CUSTO`, repositório público). As linhas do log não li (a API de logs pede autenticação); valho-me do registro do Jarvis de 2026-10-28 16:55 no pedido.
4. **O commit temporário não deixou resto.** `git diff b3791ed d2970bd` é vazio (o revert desfaz as 19 linhas exatas da sonda), e o saldo do diff só traz os limites, a docstring e o fragmento. `hooks/`, `bin/`, `.githooks/`, `.github/` e `tests/config.json` intactos.

Observação informativa (sem caminho de ataque, não é achado): o limite é único para as duas versões de Python; no 3.14 (p95 5,35/4,04 ms no runner, e 3,5-5,8/2,6-4,6 ms no sandbox local) a folga é de 4x a 5x, mas o job do 3.12 cobre a mesma regressão a 2x.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão manual do diff e dos três commits, testes do item, sonda local de CPU em `$TMPDIR` e metadados do run pela API pública. Lacunas: `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH (não toca workflow, dependência nem configuração com segredo). PA-7 (`docs/engineering/achados-recorrentes.md`): lista vazia, nada a conferir.
