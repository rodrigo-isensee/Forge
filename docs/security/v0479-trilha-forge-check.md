---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-trilha-forge-check
commit: 06ab19882f2550d175dbd077d85d02f0d2d1d16c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 E91.16 (TRILHA-FORGE-CHECK, revalidação por delta)

Gatilhos: controle do Forge (bin/forge-check: falha fechada do `parecer conferido`, VOLTAS-REVISOR-WT M1/M8, K-156).

Delta lido (`forge-check parecer delta`): `d2f79996..06ab1988`, sem o que veio da base. Nenhum arquivo do domínio mudou. Entraram a develop 27169ed1 (merge ce5b60de, fora do escopo do item) e `tests/mutantes/v0479-trilha-forge-check-2.json`, que fica fora do domínio. O `bin/forge-check` não mudou no item. A rodada anterior (parecer em d2f79996, sondas S1 a S12) está no git.

O que já foi lido: o mutante M7 (FC-DOCS-CAMINHO) agora tem o `para` `f"origin/{'develop'}"` no lugar de `"origin/develop"`. O efeito é o mesmo: ignora o `--base`. O `de` continua único em `bin/forge-check:466`. Apliquei o mutante numa cópia em TMPDIR, e `tests.test_volta_por_delta.DocsEstritoNoDelta` o mata (FAILED, failures=1). Sem o mutante, os 5 testes passam (OK).

Achados anteriores: A1 (bloqueante, `bin/forge-check:2431` em 95994eec) segue corrigido. Não há achado novo.

Suíte: não rodou localmente (o brief diz "sem suíte local"). No `gh run list` da branch, o CI 44966242523 está em andamento, e o PR mostra a Catraca com falha (44966242496), que confere os pareceres no head. O CI verde continua obrigatório para o merge.

## Riscos aceitos e ferramentas
Sem risco aceito. Não estão no PATH: gitleaks, semgrep, zizmor, actionlint e osv-scanner. Isso é lacuna, sem efeito aqui, porque o delta não toca workflow, dependência nem credencial.
