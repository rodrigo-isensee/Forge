---
tipo: review
contrato: 1
pedido: guarda-sem-mutante-2
branch: melhoria/guarda-sem-mutante-2
commit: 865761ab41370dfbaafc84572996e7be642b3d8e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Code review: GUARDA-SEM-MUTANTE, PR 2 (shell não coberto por arquivo, isentas, tetos de T7, A5 e o PQ no `gerar_volta`)

Revalidação por delta (volta 4, decisão do dono de 15:36: todo arquivo de shell sai `não coberto` por arquivo, como no PR 1; a análise de shell linha a linha sai do escopo). Parecer anterior: `930e596`, sobre `7291359`. Delta `729135968bf674a758e5fd8b88798c7ab0673c02..865761ab41370dfbaafc84572996e7be642b3d8e`. O `forge-check delta --parecer docs/reviews/guarda-sem-mutante-2.md` listou `bin/forge-mutante` (o docstring, as constantes e as funções do shell removidas, `casa`, `analisar` e `cobertura`), `tests/test_forge_mutante.py` (9, 450-458, 507-525 e 667), as specs `-3`, `-5`, `-6`, `-8`, `-9`, `-11` e `guarda-sem-mutante.json` (retocadas) e `-12`, `-13`, `-16` e `-17` (removidas), `skills/qa-testing/SKILL.md:88` e `changelog.d/guarda-sem-mutante-2.md`. Li só esse delta. O resto da branch (isentas, tetos de T7, pareamento do A5, PQ no `gerar_volta`, `bin/forge-check`, `tests/test_volta_por_delta.py`) fica como "já lido" nos pareceres `1f394b7`, `fc721f1`, `a6f5184` e `930e596`. Os pareceres de segurança e de QA do delta não são revistos aqui.

## Achados

## Revalidação dos achados do parecer `930e596`
- **A1, A2 e A3 (máscara do shell): deixam de existir**, como manda a decisão de 15:36. `linhas_incertas_sh`, `mascarar_sh`, `sem_fecho`, `condicoes_sh`, `eh_shell` e as regex `SHEBANG_SH`, `FICHA_SH`, `LINHA_INCERTA_SH`, `HEREDOC_SH`, `SEM_PALAVRA_SH` e `CONDICAO_SH` saíram do código, junto com o `import bisect` e o parâmetro `py` de `casa` e `analisar`. Nenhuma referência sobra em `bin/`, `tests/*.py`, `tests/mutantes/`, `skills/` ou `agents/` (grep). Em `cobertura`, `if not eh_python(arquivo, exemplo)` manda shell, binário e o que não é Python para `não coberto: <arquivo>` e `continue`. O corpo do shell nunca é lido, então a classe `mascara-do-shell-esconde-codigo` não tem mais onde ocorrer.
- **A4 (`"$(if ...)"` mascarado): some junto**, pelo mesmo motivo.
- **Teste novo.** `test_arquivo_de_shell_sai_nao_coberto_uma_vez_sem_olhar_a_linha` usa as quatro formas, `.sh`, hook sem extensão, `bin/` com shebang `bash` e o corpo das sondas s1 a s7 da volta 3 (heredoc com `  EOF`, `bash -c '` multilinha, `$[` com `<<"$f"`). Ele exige rc 0 e exatamente uma linha `não coberto: <nome>`. `test_isenta_para_arquivo_de_shell_e_solta_e_sai_2` cobre a isenta que aponta para shell: sem análise, ela não cruza condição e sai rc 2. `test_arquivo_python_removido_...` ganhou `bin/py`, que é removido e não tem extensão, e o tipo dele vem da base (M74).
- **Mutantes.** M112 (rótulo), M113 (`continue` para `pass`, o que levaria o shell ao `ast.parse` e daria rc 2) e M114 (`if soltas:`) miram as guardas novas. Cada `de` aparece uma vez no arquivo (conferido). Os retoques em M8, M22, M33 e M37 acompanham o código que perdeu o `py`. M72 e as specs -12, -13, -16 e -17 saem porque o código que elas miravam saiu. Isso é consequência da mudança, como na decisão de 11:46.
- **Documentação.** O docstring do `forge-mutante`, `skills/qa-testing/SKILL.md:88` e o fragmento do changelog passam a dizer "shell sai `não coberto: <arquivo>`, uma vez por arquivo". Os três batem com o código.

## Pergunta do brief: shell sem condição mudada também sai `não coberto`?
É aceitável. A decisão de 15:36 diz "todo arquivo de shell", e esse é o comportamento do PR 1 para todo tipo que não é Python. A linha é aviso, não falha: o teste novo exige rc 0 com ela. Assim ela não trava o push e não conta como falso positivo para o critério de reversão da decisão de 05:06 (falso positivo em 3 entregas). O custo é uma linha por arquivo de shell tocado. O review e o QA a leem como "shell fora da checagem; mutantes do shell à mão" (`skills/qa-testing/SKILL.md`, "um por linha de guarda mudada"). Distinguir o shell sem condição mudada exigiria ler o shell, que é justo o que a decisão tirou.

## Saídas citadas, sem refazer
- `python3 -m unittest tests.test_forge_mutante tests.test_volta_por_delta`: `Ran 124 tests ... OK`.
- `bin/forge-mutante --cobertura --base ff3936a` no head: rc 0, com 19 linhas `coberta` e 3 `spec editada`, sem `sem mutante`, `apagada` nem `não coberto`.
- Teto M14 (`git diff --numstat --no-renames ff3936a...HEAD`): `bin/forge-check` 1 + `bin/forge-mutante` 118 + `tests/test_forge_mutante.py` 110 + `tests/test_volta_por_delta.py` 2 = 231 linhas, dentro de 400. Nenhum arquivo de `hooks/` nem de `PROTEGIDOS` foi tocado.
- Segurança e QA têm parecer próprio, em `docs/security/guarda-sem-mutante-2.md` e `docs/qa/guarda-sem-mutante-2.md`.

Achados recorrentes (PA-7): a classe `mascara-do-shell-esconde-codigo` não voltou nesta volta, porque não há achado. A linha `AR-1` de `docs/engineering/achados-recorrentes.md` fica como está (`vezes: 5`).

Veredito: **aprovado**.
