---
tipo: qa
contrato: 1
pedido: guarda-sem-mutante-2
branch: melhoria/guarda-sem-mutante-2
commit: 865761ab41370dfbaafc84572996e7be642b3d8e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: guarda-sem-mutante-2 (PR 2: shell, isentas, tetos de T7, A5 e o PQ no gerar_volta), volta 4

Base `ff3936ae4011a95f25c37280fe32e4fa5ced0d95`, head `865761ab41370dfbaafc84572996e7be642b3d8e` (delta `0ba9da7..865761a`: decisão do dono de 2026-10-28 15:36, todo arquivo de shell sai `não coberto` por arquivo e o varredor de shell sai do código). Controle do Forge (`bin/`): a conferência de mutantes vale. Em paralelo com o review e a segurança. Substitui o parecer da volta 3 (commit 7291359, reprovado: A1 a A3, classe `mascara-do-shell-esconde-codigo`). A classe fecha pela raiz: o código que mascarava shell (`eh_shell`, `linhas_incertas_sh`, `mascarar_sh`, `sem_fecho`, `condicoes_sh`, regexes) foi apagado, então A1 a A3 e a recomendação A4 deixam de existir.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Decisão 15:36: todo arquivo de shell sai `não coberto: <arquivo>`, sem análise de linha (com extensão, só com shebang, heredoc com apóstrofo, `bash -c` com aspa solta, `$[`, `<<"$f"`) | `test_arquivo_de_shell_sai_nao_coberto_uma_vez_sem_olhar_a_linha`; mutantes M112 e M113 | uma linha só por arquivo (sem `arq:L`), formas hostis que derrubaram as voltas 1 a 3 | passou; M112 e M113 morreram |
| Shell removido sem extensão: o tipo vem da base; Python sem extensão removido segue `apagada` | `test_arquivo_python_removido_sai_como_apagada_e_o_que_nao_e_python_nao_coberto`; M22, M37, M74 | arquivo removido (`depois` vazio) | passou; mortos |
| Isenta (até 8, trecho exato, motivo) que mira arquivo de shell não cruza condição: rc 2 | `test_isenta_para_arquivo_de_shell_e_solta_e_sai_2`; M114 | isenta solta | passou; M114 morreu |
| Isentas de Python, tetos de diff e de condições, A5 (pareamento pela posição do nó), PQ no `gerar_volta` | testes de `Cobertura` e `BriefDeVolta` (inalterados no delta), specs -2 a -10 | tetos, 8 isentas, posição no hunk | passaram; todos os mutantes morreram |
| Mistura no mesmo diff: shell `não coberto` e Python analisado | teste de `.github/workflows/ci.yml`, `run.sh`, `tools/ferramenta` (`não coberto: run.sh` ao lado de `sem mutante · tools/ferramenta:2`) | arquivo sem extensão com shebang Python segue analisado | passou |
| Documentação afetada: `skills/qa-testing/SKILL.md:88`, docstring e changelog dizem "shell sai `não coberto` por arquivo" | leitura | texto = comportamento | conferido; sem resto de "shell por regex" fora dos pareceres anteriores |

## Execução (real)
- `python3 -m unittest tests.test_forge_mutante tests.test_volta_por_delta`: `Ran 124 tests in 44.745s ... OK`. A suíte completa fica com o pre-push (corte 1 da decisão de 2026-10-24).
- `bin/forge-mutante tests/mutantes/guarda-sem-mutante*.json` (as 11 specs numa rodada): rc 0, 71 mutantes `morreu`, nenhum sobrevivente nem sem veredito. Inclui M112, M113 e M114 de `-11`. Trecho final: `M6 · morreu · bin/forge-mutante:440`, `M7 · morreu · bin/forge-mutante:440`, `M8 · morreu · bin/forge-mutante:447`, `rc=0`.
- `bin/forge-mutante --cobertura --base ff3936ae4011a95f25c37280fe32e4fa5ced0d95`: rc 0 (`rev=865761ab4137`), só linhas `coberta` e `spec editada` (3 specs: -3, -6, -7); nenhuma `sem mutante`, `apagada` ou `não coberto`.
- Vermelho: `forge-testes --vermelho ff3936ae4011a95f25c37280fe32e4fa5ced0d95 --modulos test_forge_mutante,test_volta_por_delta` (rc 0): `vermelho: base=ff3936ae4011 head=865761ab4137`; `contagem: não prova (passa na base)=116; prova (API ausente)=1; prova (asserção)=7`; nenhum teste cai no HEAD. O teste do shell por arquivo passa na base (o PR 1 já listava shell como `não coberto`); ele é guarda de regressão, e a prova dele está em M112 e M113.
- Conferência da lista de mutantes contra o diff de `bin/`: as linhas de guarda mudadas no delta (`if not eh_python(arquivo, exemplo)`, o `continue` do ramo, `if ast.dump(...) == ...` sem `py and`, `casa(...)` sem o argumento `py`, `if soltas`) têm mutante: M22/M37 (+M112, M113), M33, M8, M114, M74 (tipo da base no removido). Nenhuma linha de guarda sem mutante. As linhas apagadas (varredor) não têm guarda a mutar.
- Conferência PA-7 (`docs/engineering/achados-recorrentes.md`): AR-1 `mascara-do-shell-esconde-codigo` (review, 5 ocorrências, última `bin/forge-mutante:404`) cita código que saiu do arquivo; a classe encerra por remoção e a linha é do review (decisão técnica 2026-10-28 12:52). Este parecer não grava AR.
- Acessibilidade e E2E: n/a (ferramenta de linha de comando).

## Recomendações (não devolvem)
- O bug `docs/qa/bugs/guarda-sem-mutante-2-mascara-do-shell.md` (média, da volta 3) fica fechado pela remoção do código; não o editei por o brief limitar o commit a este parecer. Quem o fecha: o próximo commit de documentação do autor.
- Risco aceito pelo dono (15:36): arquivo de shell nunca tem condição mudada listada (rc 0 com `não coberto: <arquivo>`); a checagem vale para Python.

## Casos de abuso e riscos aceitos
A3 e A4 da segurança do PR 1 ficam como risco aceito (decisão técnica 2026-10-28 10:25). Nada do diff é executado: a checagem lê `git show` e só faz `ast.parse`; sem varredor de shell, a superfície de regex sobre texto hostil deixa de existir. Parecer de segurança é do `security-engineer`.
