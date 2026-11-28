# Conferência da entrega

Detalhe da skill `briefs-e-conferencia` (diretriz 25: o Jarvis traz o resumo e manda ler este arquivo). Vale no Forge e em todo projeto, salvo a prova pelo CI, que é do Forge.

## Opções da conferência
- `--worktree <cópia>`: a pasta da cópia do autor, onde os PQ `cmd` rodam. Sem ela, a ferramenta procura a branch no `git worktree list`; a cópia do autor que é clone não aparece ali.
- `--sem-gravar`: só confere, sem gravar a linha `entrega conferida` (o PQ do autor).
- `--so-leitura`: como `--sem-gravar`, sem rodar os PQ `cmd` (o conferente).

## Prova do pronto na etapa `codigo`
- **Forge (G3-ENTREGA-PELO-CI):** a conferência lê o CI do PR no head entregue: concluído e verde, com os jobs que o agregador `bateria` junta em pass, e o título do PR fora da linha da etapa do brief (PR-TITULO-DO-BRIEF). O D2 e a bateria local não rodam; o autor roda só os testes afetados, para se guiar. O pré-voo do review e do QA (`forge-check pr --previo`) lê o CI do head e não espera a conferência; o merge a exige.
- **Projeto (D2-NO-BRIEF):** a conferência não roda o `forge-check pronto`: a linha só informa, e vale a última linha do pronto no relatório do autor.

## Descrição do PR e renovação do rótulo (JARVIS-DESCRICAO-E-ROTULO)
Decisão do dono de 28/11, B: muda a regra "o Jarvis não implementa". O código continua só com o time.
- **Descrição do PR:** o Jarvis a escreve direto, sem brief e sem agente, preenchendo o modelo `.github/pull_request_template.md` (nunca do zero), e a aplica com `gh pr edit <n> --body-file <arquivo>`. Abrir e mesclar o PR seguem com o `tech-lead` (FILA-22, `R-CONTRIB`).
- **Renovação do rótulo:** quando um envio derruba o rótulo que a catraca pede, o Jarvis o aplica de novo, direto, nas condições do `R-CONTRIB` (o `afrouxa-regra` só com a conta dona do repositório e a decisão do dono registrada); o hook `conformidade` confere a conta.
