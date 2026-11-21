---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-d3-modelo
commit: 60be3dffce7a93a6d1ee0434efb632ecbcc54eba
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-pv-d3-modelo, revalidação (v0478 E57.86)

Volta por delta (R-REVIEW): a rodada anterior (E57.78, head `146b4050`, reprovado por A1) fica no git. Gatilhos: hook de envio (guarda do fluxo), execução de comando vindo de configuração do repositório.

## Delta lido
`forge-check parecer delta` no intervalo `146b4050..60be3dff`. No domínio: `templates/projeto/.githooks/pre-push` (linhas 347 e 349 ganham `9>&-`) e `tests/test_prepush_so_docs.py` (`TravaDaChecagem.path_sem` e `test_trava_nao_passa_para_os_registros`, com e sem `timeout` no PATH). Fora do domínio: `changelog.d/v0479-pv-d3-modelo.md`, `tests/mutantes/v0479-pv-d3-modelo-2.json` (lido só para conferir M10 e M11). Reli o bloco de registros inteiro (`:318-354`) e a abertura da trava (`:284-305`), que o delta toca pelo descritor.

## Achados anteriores
- A1 (bloqueante): corrigido em `templates/projeto/.githooks/pre-push:347` e `:349`, exatamente a correção mínima pedida. O descritor 9 sai só do comando de registros; o subshell que o envolve termina junto com ele, então nada que o comando deixe em segundo plano segura a trava. O descritor 8 da fila já fecha antes (`fila_sair`, `:304`).

## Sondas
- S1 · registros `setsid sleep 300 >/dev/null 2>&1 & echo $! >> pids`, 2º envio com FORGE_PREPUSH_ESPERA=1, com e sem `timeout` (test_trava_nao_passa_para_os_registros) · espera: rc 0 · obtido: rc 0 nos dois subtestes (antes: rc 1)
- S2 · mutante M10 (tira `9>&-` da linha 347), mesmo teste · espera: falha · obtido: FAIL `[com timeout]`, rc 1 "outra checagem do projeto está rodando nesta máquina"
- S3 · mutante M11 (tira `9>&-` da linha 349), mesmo teste · espera: falha · obtido: FAIL `[sem timeout]`, rc 1, mesma mensagem

## Só aperta?
Sim. O delta só fecha um descritor herdado no comando de registros: não acrescenta caminho de saída 0, não remove nenhum `exit 1`, não mexe na leitura da chave, no prazo nem no `refs_branches`; sem `flock` (descritor 9 nunca aberto), `9>&-` é inócuo no bash. O efeito é devolver a garantia que a etapa local já tinha (`:154`). O teste novo só acrescenta asserções e limpa os processos que cria (`matar_se_vivo` no `finally`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: sem CI neste head (`gh run list` vazio); rodei `TravaDaChecagem` e `ConferenciaDeRegistros` (20 testes, OK; 2 pulos pré-existentes de `chown` no sandbox) e os mutantes M10 e M11 numa cópia em `$TMPDIR`; o merge segue exigindo CI verde. Ferramentas ausentes no ambiente (lacuna): `gitleaks`, `shellcheck`, `semgrep`.
