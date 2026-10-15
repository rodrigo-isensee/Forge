### Corrigido
- **`scripts/ci-local` e `tests/test_ci_local.py`:** acompanham o CI consolidado do #138 (jobs `rapida` e `bateria`). O teste confere os jobs atuais e que a `bateria` ainda traz os passos dos jobs antigos; no script, o job `workflows` deixou de existir, então o que era opcional (actionlint e zizmor) passou a ser opcional por passo, e todo o resto da `bateria` continua obrigatório.
