---
tipo: revisao-devops
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sobrevive
commit: e3dfc4cbeb4b502c1ba31665f37e913863dc0df0
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-16
---
# Review de devops: v047-ambiente-sobrevive

## Achados
- A3 (recomendado) .devcontainer/devcontainer.json:23 · em repositório privado, sem gh nem login, o clone falha e o gh nunca é instalado; o 1º preparo é manual (`bash scripts/preparar-estacao.sh --container`). Documente no cartão.

## Detalhes
A1 e A2 do parecer anterior estão resolvidos. A1 (R-SEGURANCA): o comando faz clone raso novo da main (URL do .git/config) e só roda se o script traz `FORGE_PREPARO_ESSENCIAL:-0`; a main atual não traz (0), então pula e não executa o work tree como root. A2 (R-CONFORMIDADE): o `remoteEnv` com GH_TOKEN saiu e o comentário documenta o login do dono (repo e workflow) e que o token do bot não leva workflow.

Revalidado por delta 680725756d94..584b2239f8de (domínio: os dois devcontainer.json, scripts/preparar-estacao.sh, o modelo preparar-ambiente.sh). Novo no delta: chave apt do gh conferida por impressão digital, com falha fechada e mensagem `falta:`, nos dois scripts. `GH_CONFIG_DIR` e credential helper só no clone, sem segredo gravado. Falha ou falta de rede termina em `; true`, e o container sobe. PA-7: AR-5 e AR-12 tocam hook e mutante, fora do domínio; o `hooks.json` usa `-s -E` como os demais hooks.

Revalidado por delta 584b2239f8de..e3dfc4cbeb4b (E2.207): nenhum arquivo do domínio mudou; parecer segue aprovado.

Ferramentas: shellcheck nos dois scripts rc=0; JSON dos dois devcontainer válido sem comentários; testes test_ambiente_hook (6) e do item em test_forge (6) OK. actionlint e docker build não se aplicam. Suíte completa fica para o CI. O remoto da branch está no mesmo sha, e o merge deu "Already up to date".

## Custo e rollback
Sem minutos de CI nem recurso novo (R-CUSTO). Volta: reverter o commit; o preparo manual segue valendo.
