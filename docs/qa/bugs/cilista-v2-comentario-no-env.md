# cilista-v2-comentario-no-env - comentário dentro do env zera a leitura e deixa PATH passar
- Severidade: alta
- Estado: fechado em 0ad1ad7 (revalidado pelo QA: a sonda reprova)
- Responsável sugerido: agente de desenvolvimento da stack (test_ci_local.py)
- Ambiente: melhoria/lote-cilista-v2 @ 6f7a9d1, python3 -I

## Passos para reproduzir
1. Em `.github/workflows/ci.yml`, no passo "Baixa actionlint e zizmor...", antes de `run: |` insira `        env:` / `        # c` (recuo 8) / `          PATH: ./scripts`.
2. Chame `passos_antes_do_lint_fora_da_lista(texto)`.
3. Sem a linha de comentário a função reprova; com ela devolve `[]`.
4. No env do job: após `ZIZMOR_SHA256: ...` insira `    # c` (recuo 4) e `      PATH: scripts`; também devolve `[]`.

## Resultado esperado
Reprovar: PATH está fora da lista positiva.
## Resultado obtido
Escapou. `passos_da_bateria` trata o comentário no recuo do `env:` como chave nova e zera `em_env`; `env_do_job` idem no recuo 4. As chaves seguintes não são lidas.
## Evidência
Script de reprodução: "step c8: ESCAPOU" e "job: ESCAPOU"; as mesmas linhas sem comentário reprovam. Comentário em coluna 0 quebra `ler_jobs` (falha fechada). Tab no recuo também passa, mas o YAML o rejeita (sem efeito).
