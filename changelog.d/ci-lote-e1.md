### Alterado
- CI (A18): as partes da suíte, o job de verificações longas (Provas, shellcheck e e2e de instalação) e os agregadores esperam o job de passos baratos (lint, degrau, validação do plugin, changelog): passo barato vermelho pula a suíte e reprova `bateria` e `bateria (python 3.14)` sem esperar as seis partes; nenhum check exigido muda de nome. A Neutralidade roda uma vez só, nas partes.

### Adicionado
- CI (QA-1): o resumo do job (GITHUB_STEP_SUMMARY) da suíte vermelha lista os testes que caíram, só os IDs (sem a mensagem), até 30 e a contagem do resto; vale para as partes do PR e para a checagem rápida da develop.
