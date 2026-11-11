### Alterado
- CI (A18): as partes da suíte esperam o job de passos (lint, degrau, validação do plugin, changelog e o teste de neutralidade, que entra nele): passo barato vermelho pula a suíte e os agregadores `bateria` e `bateria (python 3.14)` reprovam em cerca de 30 s, sem gastar os minutos das seis partes; nenhum check muda de nome.

### Adicionado
- CI (QA-1): o resumo do job (GITHUB_STEP_SUMMARY) da suíte vermelha lista os testes que caíram, só os IDs (sem a mensagem), até 30 e a contagem do resto; vale para as partes do PR e para a checagem rápida da develop.
