---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-trava-corrida
commit: ef5bb776e3a958119834407b76ab0185932bc88e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-trava-corrida (E64.15)

Escopo: a fixture `SUITE_COM_PID` de `tests/test_pre_push_trava.py` passa a gravar o pid da suíte num temporário (`suite-pid.<pid>`) e a renomear com `os.replace` para `suite-pid`. Corrige a corrida do run 44856922521 (PR #746): o teste lia `suite-pid` entre a criação e a escrita e via o arquivo vazio (`int("")`).

## Diff conferido
`git show ef5bb776`: 2 arquivos, `tests/test_pre_push_trava.py` (+4/-1, só dentro da string `SUITE_COM_PID`) e o fragmento `changelog.d/v0479-trava-corrida.md`. O corpo de `test_parar_o_hook_para_so_a_propria_suite` não mudou.

## O teste continua provando a mesma coisa
O pid gravado segue sendo `os.getpid()` da suíte filha; o arquivo final tem o mesmo nome e conteúdo. As asserções (a primeira suíte morre antes da trava soltar; a segunda pega a vez e roda a própria suíte; parar a primeira não derruba a segunda; o `.verde` não é gravado; as mensagens `kill <pid>`, `nunca pkill`, `suíte interrompida`) estão intactas. A renomeação só elimina a janela em que `pid_arquivo.exists()` vale e o conteúdo está vazio.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E64.11: leitura de `suite-pid` nunca vê arquivo vazio | `test_parar_o_hook_para_so_a_propria_suite` isolado, 20 rodadas sob carga (14 laços de CPU em 12 núcleos) | arquivo existe e vazio (janela criação/escrita) | passou 20/20 |
| E64.11: o resto do módulo não regride | `tests.test_pre_push_trava` inteiro (50 testes), 20 rodadas | n/a | passou 20/20 |
| Mesmo comportamento provado | leitura do diff acima | n/a | confere |

## Execução
Comandos (foreground, `timeout`, `TMPDIR` e saída em `/root/.forge-contrib/wt/`):
- `python3 -I -m unittest discover -s tests -p test_pre_push_trava.py -k test_parar_o_hook_para_so_a_propria_suite -v`: `Ran 1 test in 0.632s`, OK.
- Módulo inteiro 20 vezes: `modulo ok=20 ko=0 682s`; cada rodada `Ran 50 tests` (50,6s a 55,7s nas que a carga cobriu), nenhum `FAILED` (saída em `qa-modulo20.txt`).
- Isolado 20 vezes sob 14 laços de CPU: `isolado-sob-carga ok=20 ko=0`, 20 linhas `Ran 1 test` (saída em `qa-isolado20-carga.txt`).

Limite honesto: a carga das rodadas do módulo durou 400s (as 7 a 8 primeiras rodadas); as seguintes rodaram sem carga. O isolado teve carga em todas as 20 rodadas.

## Vermelho antes do verde
Não aplicado: não há teste novo, é correção da fixture de um teste existente, e a corrida da base é de temporização (não se reproduz de forma determinística). 20/20 verdes sob carga é evidência estatística, não prova de ausência. A causa é eliminada por construção: `os.replace` é atômico no mesmo diretório.

## Mutação
Não se aplica: o diff não toca código de produção nem guarda (`bin/`, `hooks/`, `.githooks/`), só a fixture de um teste.

## Prova no CI
O CI roda a suíte inteira no PR; o check-run `bateria` do mesmo sha é a prova da suíte inteira, não rerodada aqui.
