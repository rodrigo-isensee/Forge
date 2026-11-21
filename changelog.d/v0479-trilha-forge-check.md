### Corrigido
- O `brief gerar` de portão (review, segurança, QA) com branch traz a linha de envio do parecer: commit só dele, `pedido:` com o id do pedido (nunca o nome da branch) e, com o remoto adiante, `git pull --rebase` sobre o commit do parecer, nunca merge nem `--force` (BRIEF-PORTAO-REBASE, v0478 E91.1).

### Adicionado
- O `brief gerar` recusa a etapa que já tem entrega conferida (uma etapa por delegação, K-166), põe no Entregar da etapa que cita `.githooks/` que o arquivo é do usuário e vai como proposta de diff (K-252) e propõe ao portão o PQ `forge-check pr <pedido> --previo --base <base>` rodado depois do commit do parecer (K-156) (MODELO-PEDIDO-E-BRIEF, v0478 E91.1).
