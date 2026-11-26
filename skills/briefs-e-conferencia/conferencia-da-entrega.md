# Conferência da entrega

Detalhe da skill `briefs-e-conferencia` (diretriz 25: o Jarvis traz o resumo e manda ler este arquivo). Vale no Forge e em todo projeto, salvo o D2, que é do Forge.

## Opções da conferência
- `--worktree <cópia>`: a pasta da cópia do autor, onde os PQ `cmd` e o D2 rodam. Sem ela, a ferramenta procura a branch no `git worktree list`; a cópia do autor que é clone não aparece ali.
- `--sem-gravar`: só confere, sem gravar a linha `entrega conferida` (o PQ do autor).
- `--so-leitura`: como `--sem-gravar`, sem rodar os PQ `cmd` nem o D2 (o conferente).

## D2 na etapa `codigo` (Forge; D2-NO-BRIEF)
- A conferência roda o `forge-check pronto` de quem confere, com `--raiz` na cópia do autor. Fora do rc 0, não cumpre e mostra a última linha do pronto.
- Sem a cópia (nem `--worktree`, nem worktree da branch) e com o head no Forge, não cumpre e pede `--worktree`. No `--so-leitura` e no projeto, a linha só informa: vale a última linha do pronto no relatório do autor.
- O pronto roda os testes afetados e passa de 10 min, além do limite do Bash em primeiro plano: lance a conferência com o `run_in_background`, com log até `rc=`, e espere o log no mesmo turno (skill `esperar-estado`, "O envio longo").
