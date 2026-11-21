### Corrigido
- O `brief gerar` de portão (review, segurança, QA) com branch traz a linha de envio do parecer: commit só dele, `pedido:` com o id do pedido (nunca o nome da branch) e, com o remoto adiante, `git pull --rebase` sobre o commit do parecer, nunca merge nem `--force` (BRIEF-PORTAO-REBASE, v0478 E91.1).
- `forge-check docs --base <develop|homolog|main>` confere só os documentos do diff da branch contra a `origin/<base>`, todos no modo estrito, e reprova com o diff ilegível; o PQ do brief de portão passa a usá-lo, e o documento antigo fora do diff não reprova mais a entrega; a cópia do parecer de segurança fora da pasta segue acusando o `- Nenhum.` (FC-DOCS-CAMINHO, v0478 E91.1).

### Adicionado
- O `brief gerar` recusa a etapa que já tem entrega conferida (uma etapa por delegação, K-166), põe no Entregar da etapa que cita `.githooks/` que o arquivo é do usuário e vai como proposta de diff (K-252) e propõe ao portão o PQ `forge-check pr <pedido> --previo --base <base>` rodado depois do commit do parecer (K-156) (MODELO-PEDIDO-E-BRIEF, v0478 E91.1).
