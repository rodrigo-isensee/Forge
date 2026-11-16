---
tipo: revisao-devops
contrato: 1
pedido: v047-ambiente-sobrevive
branch: melhoria/v047-ambiente-sobrevive
commit: 680725756d94129c230f52c6401d697463f6e88d
parecer: reprovado
revisor: forge:devops-engineer
data: 2026-11-15
---
# Review de devops: v047-ambiente-sobrevive

## Achados
- A1 (bloqueante) .devcontainer/devcontainer.json:23 · R-SEGURANCA: o postStartCommand lê scripts/preparar-estacao.sh da origin/main, que ainda não tem FORGE_PREPARO_ESSENCIAL (grep=0); até a release roda o --container inteiro como root, com jarvis-forge do work tree (B2 reaberto). Exija a marca no arquivo lido.
- A2 (recomendado) .devcontainer/devcontainer.json:18 · remoteEnv repassa o GH_TOKEN da máquina do dono; se tiver o escopo workflow, o agente o ganha no container. Documente o escopo mínimo (repo) e que o token do bot não leva workflow (R-CONFORMIDADE).

## Detalhes
Reprovado por A1. Defeito provado: `git show origin/main:scripts/preparar-estacao.sh | grep -c ESSENCIAL` dá 0, então o script antigo ignora a variável e executa `container_vigente` (`bash $origem/scripts/jarvis-forge --atualizar-vigente`) e o dev-marketplace, código do work tree que o agente edita, com o comando em root fora do sandbox. É o risco que o próprio comentário do arquivo diz evitar. Correção mínima: antes de rodar, `grep -q FORGE_PREPARO_ESSENCIAL "$f" &&` (sem a marca, pula e deixa o comando manual). O modelo de projeto não tem a janela: `git show` falha enquanto o script não está na main e o `&&` encerra; o `; true` mantém o container subindo.

Conferido sem achado: sem segredo gravado (só localEnv); falha do preparo não derruba o container; scripts idempotentes e sem apagar dado; hooksPath de outra ferramenta preservado; --verificar não altera nada e traz o comando exato; gh via apt oficial com chave em keyrings; sem Dockerfile, compose nem workflow tocados; sem custo (R-CUSTO). PA-7: nenhum AR aplicável (sem python, sem hook, sem mutante).

Ferramentas: shellcheck nos dois scripts, rc=0; 9 testes do item (devcontainer, essencial, hookspath, verificar, modelo_de_projeto) OK. actionlint e docker build não aplicáveis. Suíte completa fica para o CI. Remoto da branch não avançou (mesmo sha).

## Custo e rollback
Sem minutos de CI nem recurso novo. Volta: reverter o commit; o container volta ao preparo manual (`bash /workspaces/Forge/scripts/preparar-estacao.sh --container`).
