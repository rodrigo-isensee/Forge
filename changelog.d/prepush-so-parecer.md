### Alterado
- O pre-push de um push que só acrescenta pareceres (docs/reviews, security, qa, devops) sobre código cuja árvore já passou na suíte roda só as classes de teste que leem pareceres; qualquer outro arquivo, prova ausente ou dúvida roda a suíte inteira, e o CI repete tudo (PREPUSH-SO-PARECER).
