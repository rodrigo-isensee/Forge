### Adicionado
- Modelo de CI de projeto enxuto (R-CUSTO): um workflow só, suíte só em PR e nas branches do fluxo, detecção de mudança só de documento que pula a suíte, um único check `ci` que só passa com a suíte quando há código, concurrency por número do PR ou ref; skill ci-cd explica os minutos.
- Detecção de só documento do modelo de CI usa `git diff --no-renames`: renomear código para `docs/` ou `.md` não pula mais a suíte.
