# CL-01 - Ctrl-C no ci-local imprime traceback do Python
- Severidade: baixa
- Status: corrigido em f1fdb80 (revalidado por QA: INT rc 130 e TERM rc 143, sem traceback, sem worktree nem pasta temporária novas)
- Responsável sugerido: forge:python-dev (ou o agente de desenvolvimento da stack do script)
- Ambiente: melhoria/ci-local @ e808d6c, `scripts/ci-local`

## Passos para reproduzir
1. `timeout --preserve-status -s INT 25 scripts/ci-local 126 > saida.txt 2>&1; echo $?`
2. `grep -c Traceback saida.txt; tail -1 saida.txt`
3. `git worktree list` e `ls -d $TMPDIR/ci-local.*`

## Resultado esperado
Interrupção limpa: uma linha curta ("interrompido"), rc 130, sem traceback.

## Resultado obtido
rc 130 e a worktree temporária e a pasta `ci-local.*` somem (a limpeza funciona), mas a saída termina com traceback de `KeyboardInterrupt` (2 linhas "Traceback"). Só cosmético; sem perda de dados.

## Evidência
`grep -c Traceback` = 2; última linha da saída: `KeyboardInterrupt`; `git worktree list` sem entrada `ci-local.*` depois.
