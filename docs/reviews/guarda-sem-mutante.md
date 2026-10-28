---
tipo: review
contrato: 1
pedido: guarda-sem-mutante
branch: melhoria/guarda-sem-mutante
commit: 7c86f530cb491355a40f2699215ebd45f3d2c5d4
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Code review: GUARDA-SEM-MUTANTE, PR 1 (`bin/forge-mutante --cobertura`, núcleo Python)

Diff revisado: `991cd092b42c88d86a16912ff8ddc1b72b8da026...7c86f530cb491355a40f2699215ebd45f3d2c5d4` (4 commits). Referências: as 5 linhas DECISÃO TÉCNICA da ata `docs/alinhamentos/2026-10-28-revisao-desenho-guarda-sem-mutante.md` (fora do repositório, em `~/.forge-contrib/docs/alinhamentos/`), com a linha do PR 1 da tabela como escopo. Shell sai como `não coberto` até o PR 2: é o plano e não gera achado. Primeira rodada, sem delta.

## Achados
- A1 (bloqueante) bin/forge-mutante:320 · classe: defeito provado contra a decisão 3. Um arquivo que não é UTF-8 em qualquer ponto do diff, inclusive em tests/fixtures/ (TESTE) ou num binário, faz o rc ser 2. O git() decodifica o git diff como texto (l. 320 e 324) e ler_no_commit (l. 315) decodifica todo arquivo lido
- A2 (bloqueante) bin/forge-mutante:426 · classe: requisito da decisão 3 (T5, nada passa calado). Um arquivo não Python removido (.sh, .yml, .json de hook) some da saída sem `não coberto`, e o teste tests/test_forge_mutante.py:453 trava o comportamento errado. Sugestão: listar o removido também
- A3 (recomendado) bin/forge-mutante:417 · o teto de 300 arquivos só é conferido depois de mudancas() rodar um git diff por arquivo. Conferir o tamanho do --name-status antes do laço da l. 323 evita trabalho com um diff grande (T7)
- A4 (recomendado) bin/forge-mutante:363 · se o texto mutado não faz parse, o SyntaxError sai como rc 2 sem o id do mutante nem o arquivo. Sugestão: capturar o erro e citar m['id'], como faz o ValueError do mutante equivalente
- A5 (recomendado) bin/forge-mutante:382 · `apagadas` é indexado pelo texto: se a contagem de um texto cai 2 ou mais, sai uma linha só, com a 1a ocorrência da base. O rc fica certo, mas a saída esconde a 2a guarda apagada

## Parecer
**Reprovado**, por A1 e A2. Os dois são pequenos e não mudam o desenho.

A1. Sonda em `$TMPDIR/tech-lead-guarda-sem-mutante/sonda1`: na base, `lib.py` com `if x > 100:`. Três casos:
- commit que só adiciona `tests/fixtures/latin1.txt` (`caf\xe9`): rc 2, `'utf-8' codec can't decode byte 0xe9 in position 175`;
- `logo.png` com NUL: rc 2, `... position 0`;
- `logo.png` sem NUL: rc 2, `... position 123`.

Pela decisão 3, o arquivo de TESTE fica fora e o resto sai como `não coberto` sem mudar o rc. Hoje o repositório não tem arquivo que não seja UTF-8 (conferido com `git ls-files`), mas o gatilho é real: um corpus de hook com bytes hostis ou uma imagem bastam. Também é a falha que mais pesa no critério de reversão do dono quando o PR 2 puser o PQ no brief. A mensagem nem cita o arquivo.

Sugestão:
- ler o `git diff` em bytes (só os cabeçalhos `@@` interessam) ou com `errors="surrogateescape"`;
- decidir TESTE e `FORA_DA_COBERTURA` antes de ler qualquer coisa;
- no candidato, ler só o shebang para decidir o tipo;
- tratar o não UTF-8 que não é Python como `não coberto` e, no Python, dar rc 2 citando o arquivo.

A2. A volta 1 tirou o pulo do arquivo removido só para o Python. A decisão 3 diz "todo outro arquivo mudado fora de `TESTE`, de `*.md` e de `changelog.d/` ... sai como `não coberto: <arquivo>` sem mudar o rc", e um arquivo removido é um arquivo mudado. Apagar `run.sh`, um workflow `.yml` ou o `.json` de um hook passa calado, e o PR 2 só resolve o shell. Sugestão: tirar o `if status != "D"` da l. 426 e inverter a asserção da l. 453 do teste.

Conferido contra a ata (sem achado além dos acima):
- Decisão 1, condição apagada: o multiconjunto pelo `ast.unparse` (`Counter`) funciona, e o arquivo Python removido sai como `apagada` (volta 1). Uma condição só modificada (`x > 100` vira `x >= 100`) sai como `sem mutante` e também como `apagada`, rc 1. Sem `isentas` no PR 1, editar uma condição existente sempre dá rc 1. É o que a decisão 1 diz, e o plano só põe o PQ no brief junto com as `isentas` (PR 2). Não é achado aqui, mas o PR 2 precisa medir esse caso no critério de reversão.
- Decisão 2, casamento: a troca é medida pelo prefixo e pelo sufixo comuns em bytes e tem de cair dentro de `[ini, fim]` do nó. Há a trava de 8+ não brancos, o `de` precisa ser único, o `ast.dump` igual dá rc 2, e a saída diz `declarado, não provado`. O deslocamento em bytes com UTF-8 tem teste.
- Decisão 3, escopo por tipo: `.py` ou shebang `python`, `hooks/`, `.githooks/` e `stacks/` sem exceção, e TESTE, `.md` e `changelog.d/` fora. Ressalvas: A1 e A2.
- Decisão 5 e T4, T6 e T7: `--base` e `--rev` passam por `resolver` (`--end-of-options`, `^{commit}`), merge-base igual a rev dá rc 2, a leitura é por `git show <sha>:` e a árvore suja só avisa. O diff usa `-U0 --no-renames` sem `-w`, com `-z`, `--literal-pathspecs` e `--`. Só há `ast.parse`, nada é executado. `validar_spec` e `MAXIMO_DA_SPEC` são reusados (volta 1). Os tetos de 300 arquivos e 1 MiB existem, as regexes não têm quantificador aninhado, a primeira linha é `base= mb= rev=`, e uma spec removida ou editada é listada.
- Fora do escopo do pedido: `hooks/` não foi tocado, e nenhum hook, pre-push ou CI chama `--cobertura`.

Qualidade de `cobertura()` e do código novo:
- O código é legível e cada função tem um propósito.
- A tabela `TESTES_DO_NO` deixa claro o que conta como condição.
- Os erros caem num único `except` que dá rc 2 com mensagem.
- `os.chdir` para a raiz só roda no caminho da CLI.

Os 11 testes novos cobrem cada tipo de nó, as travas do casamento, o multiconjunto, as specs do diff, a base, os limites e nomes hostis (`-x.py`, `a b.py`). Faltam os casos de A1 e A2.

Teto M14: `git diff --numstat --no-renames 991cd09...7c86f53` dá `bin/forge-mutante` 158+1 e `tests/test_forge_mutante.py` 188+0, ou seja, 347 linhas de código e teste, dentro do teto de 400. As specs em `tests/mutantes/`, o fragmento em `changelog.d/` e os `.md` ficam fora da conta.

Saídas citadas, sem refazer:
- `bin/forge-mutante --cobertura --base 991cd092b42c88d86a16912ff8ddc1b72b8da026 --rev 7c86f53...`: rc 0. São 24 linhas `coberta`, de `bin/forge-mutante:313` a `:513`, todas com mutante de `tests/mutantes/guarda-sem-mutante*.json`, e nenhuma `sem mutante` ou `apagada` (T6, a checagem cobre a si mesma).
- `python3 -m unittest tests.test_forge_mutante`: `Ran 51 tests ... OK`.
- A rodada de mutantes (M1 a M39) é evidência do QA (E3.1) e não foi refeita aqui.

Outros pareceres:
- Segurança (E2.1, `docs/security/`) é do `security-engineer` e roda em paralelo. Fica para ele, sem achado meu: o `git diff` não passa `--no-textconv` (o textconv depende de configuração local) e `ler_no_commit` lê o blob inteiro antes de conferir o teto de 1 MiB.
- QA (E3.1) roda em paralelo.

Achados recorrentes (PA-7): conferi `docs/engineering/achados-recorrentes.md`, que ainda não tem nenhuma linha. A1 e A2 são de classes novas neste pedido, então nenhuma linha `AR-<n>` foi gravada.
