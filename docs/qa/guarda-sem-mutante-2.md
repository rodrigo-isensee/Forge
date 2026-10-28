---
tipo: qa
contrato: 1
pedido: guarda-sem-mutante-2
branch: melhoria/guarda-sem-mutante-2
commit: a1571168d78646e8ccdd0ad3a225dfafc3775ffb
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-10-28
---
# QA: guarda-sem-mutante-2 (PR 2: shell, isentas, tetos de T7, A5 e o PQ no gerar_volta), volta 1

Base `ff3936ae4011a95f25c37280fe32e4fa5ced0d95`, head `a1571168d78646e8ccdd0ad3a225dfafc3775ffb` (delta `43a8cc8..a157116`). Controle do Forge (`bin/`): a conferência de mutantes vale. Em paralelo com o review e a segurança. Substitui o parecer da rodada 1 (commit 43a8cc8, aprovado).

## Achados
- A1 (bloqueante) tests/test_forge_mutante.py:553 · teste de tempo instável: o limite de 0,05 s de CPU (p95 isolado 0,021 s) falha sob carga; a spec -12 deu `M82 controle vermelho` e rc 2 numa de 3 rodadas das 13 specs, e 43 de 60 execuções com 4 em paralelo caíram; subir o limite (a regressão quadrática custava 9 s)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Review A1: `#` dentro de `${a##*/}` não é comentário | sonda `x=${a##*/}; if [ -n "$x" ]; ...` + `test_shell_por_regex...` | `#` precedido de `#`, `%`, `/` | passou (`sem mutante`, rc 1) |
| Review A2: `cmd \|\| true  # c` não conta | sonda + `test_shell_por_regex...` | lado direito só `true` com comentário | passou (rc 0, sem linha); `cmd \|\| true` idem |
| Review A3: `until` é condição | sonda `until grep -q pronto log; ...` | palavra-chave nova | passou (`sem mutante`, rc 1) |
| Segurança A1: apóstrofo em heredoc e `\'` fora de aspas não escondem condição | sondas S1 e S3 | máscara de aspas | passou (`sem mutante`, rc 1 nas duas) |
| Segurança A1: `bash -c '...'`, `eval '...'`, heredoc sem linha final e aspa solta saem `não coberto: arq:L` | sondas + `test_shell_que_nao_se_le_com_certeza...` | o que o analisador não lê com certeza | passou (linha `não coberto`, rc 0, conforme a decisão de 11:16) |
| Heredoc legítimo com apóstrofo seguido de condição com mutante; corpo de heredoc com `if you want` não conta | sonda + teste acima | falso positivo | passou (corpo mascarado, rc 0) |
| Segurança A2 / T7: regex linear | sondas ponta a ponta com `--cobertura`: 40 KB e 1 MB de `"\"`, `[[ `, `[ `, `'`, `<<A `, 100 mil heredocs | linha longa sem fecho | passou (0,2 a 1,1 s, sem catástrofe) |
| Teste de tempo em CPU (`time.process_time`, PROP-TEMPO-CPU) | `test_shell_de_40_kb_sem_fecho_gasta_pouca_cpu` | 40 KB sem fecho, três unidades | **falhou sob carga** (A1) |
| Shell coberto (if, elif, while, until, `[ ]`, `[[ ]]`, test, `&&`, `\|\|`) | `Cobertura` + sondas | condição mudada sem mutante rc 1, com mutante rc 0 | passou |
| Isentas válidas, inválidas, mais de 8, que não cruzam condição (rc 0 e rc 2) | `Cobertura` (M48 a M55) | motivo 19/20, trecho 7/8, 8/9 isentas | passou |
| Tetos de T7 (4 MiB, 5000 condições, 1 MiB) | spec -9, -11 (M73, M74) e sondas com 400 KB a 1,5 MB | limite e logo acima | passou (rc 2) |
| A5: editada pareada pela posição do nó | spec -9, -10, `test_condicao_apagada_e_outra_nova...` | par por posição | passou |
| PQ do `--cobertura` no brief de volta | `tests.test_volta_por_delta` (BriefDeVolta, 2 testes) | numeração `PQ-N` com e sem PQ de merge | passou |
| Documentação do shell e das isentas | `skills/qa-testing/SKILL.md:88` | n/a | passou |

## Execução (real)
- 13 specs (`bin/forge-mutante tests/mutantes/guarda-sem-mutante*.json`, M1 a M87, 87 mutantes): 1ª rodada rc 2, 86 `morreu` e `M82 · controle vermelho · bin/forge-mutante` (o teste do A1 caiu no commit sem mutação); 2ª e 3ª rodadas rc 0, 87 `morreu`, 0 sobrevivente. Só a spec -12 sozinha: rc 0 duas vezes. Prazo por rodada: 65 s.
- `bin/forge-mutante --cobertura --base ff3936ae4011a95f25c37280fe32e4fa5ced0d95` sobre o próprio diff: rc 0, 38 linhas (5 `spec editada`, o resto `coberta ... declarado, não provado`), nenhuma `sem mutante`, `apagada` ou `não coberto`. Lista conferida contra o diff: cada condição mudada em `bin/forge-mutante` tem mutante; o diff de `bin/forge-check` é uma linha que não é condição.
- `python3 -m unittest tests.test_forge_mutante tests.test_volta_por_delta`: `Ran 126 tests ... OK` (42 s, sozinho na máquina). A suíte completa fica com o pre-push.
- Vermelho, `forge-testes --vermelho ff3936ae4011a95f25c37280fe32e4fa5ced0d95 --modulos test_forge_mutante,test_volta_por_delta` (rc 0): abre com `vermelho: base=ff3936ae4011 head=a1571168d786`; `contagem: não prova (passa na base)=113; prova (API ausente)=3; prova (asserção)=10`. Provam, entre outros, `test_shell_por_regex_com_aspas_comentario_e_o_ou_que_nao_guarda` (A1 a A3 do review), `test_shell_que_nao_se_le_com_certeza_sai_nao_coberto_e_o_heredoc_com_apostrofo_nao_esconde` (A1 da segurança), `test_shell_de_40_kb_sem_fecho_gasta_pouca_cpu` (A2 da segurança), `BriefDeVolta.test_etapa_de_merge_acrescenta_o_pq_por_ancestralidade` e o `test_gera_blocos_copiados_decisoes_achados_e_prova`.
- Teste de tempo em CPU, medido: sozinho, mínimo 0,020 s e máximo 0,028 s para `"\"` (as outras unidades, 0,007 a 0,012 s). Com 4 processos em paralelo (máquina de 12 núcleos), `"\"` chega a 0,053 a 0,059 s, acima do limite de 0,05 s. O teste, em 4 laços paralelos de 15 execuções: 43 falhas em 60 (8, 11, 11 e 13 de 15); sozinho, 3 de 3 passam. O pre-push e o CI rodam módulos em paralelo, então a carga é a de uso real. A guarda é boa (a versão quadrática gastava 9 s); o limite é que está apertado, com margem de 2x sobre o mínimo.
- Mutação: M82 (`m.start() < len(linha)`) morre no teste de tempo, quando ele passa; o A1 vale para o controle, não para a guarda.
- Acessibilidade e E2E: n/a (ferramenta de linha de comando).

## Recomendações (não devolvem)
- `case` e `(( ))` isolado seguem fora e declarados no docstring; `until cmd` entra pelo A3 do review. Sem ação.
- Condição de shell em `bash -c`/`eval` sai `não coberto` com rc 0, como pede a decisão de 11:16; se o dono quiser rc 1, é decisão nova.
- Achados recorrentes (PA-7): `docs/engineering/achados-recorrentes.md` está vazio e a classe (limite de tempo apertado) não se repete na lista; sem linha `AR`.

## Casos de abuso e riscos aceitos
A3 e A4 da segurança do PR 1 ficam como risco aceito (decisão técnica 2026-10-28 10:25). O A4 do PR 2 (motivo da isenta cru na saída) e o A3 do PR 2 (`parecidas`) seguem recomendados. Nada do diff é executado: a checagem lê `git show` e só faz `ast.parse` e regex.
