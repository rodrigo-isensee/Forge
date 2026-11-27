---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-devcontainer-sem-gh
commit: a5f6c0f1343dbad87df1f227b647e9c0e8460515
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E35.8, #926, DEVCONTAINER-SEM-GH), volta 2

Revalidação por delta (e1c3ba7c..a5f6c0f1, `forge-check parecer delta`): no domínio só `.devcontainer/devcontainer.json` e `scripts/preparar-estacao.sh` (comentário). A rodada anterior (reprovado, commit 046cd9a1) fica no git.

Gatilhos: comando executado como root fora do sandbox (postStartCommand), arquivo em vigor (.devcontainer/devcontainer.json), credencial do dono (login do gh no volume ~/.claude), defesa B2 da 0.43.1

## Achados anteriores
- A1 (bloqueante): fechado. `.devcontainer/devcontainer.json:30` clona a `main` de URL fixa no próprio arquivo para `mktemp -d` do root e roda o script de lá; nada de `/workspaces/Forge` é executado. O caso de abuso voltou para o Forge (`tests/test_forge.py`, `PrepararEstacao.test_poststart_roda_so_a_main_do_remoto_nunca_o_ref_local_forjado`: script forjado no work tree e no ref local não roda); rodei esse, `test_poststart_do_forge_exige_a_guarda_no_script_da_main` e `test_devcontainer_prepara_sozinho_sem_rodar_o_work_tree`: 3 OK.
- A2 (recomendado): fechado. `.devcontainer/devcontainer.json:14-15` troca "protegido pelo hook" pela garantia real e diz que o hook libera a escrita deste arquivo na sessão do Forge.
- A3 (recomendado): fechado. `scripts/preparar-estacao.sh:8` alinhado ao desenho (baixa a main pelo GitHub, nunca a cópia de trabalho).

## Caminhos restantes de código do agente para o root (conferidos)
- O `git clone` roda com cwd em `/workspaces/Forge`, mas não lê a configuração do repositório do cwd: sonda local com `core.fsmonitor` e `alias.clone` no repositório do cwd não executou nada (git 2.43.0). A configuração global do root (`/root/.gitconfig`, `/root/.config/git`) não é gravável no sandbox.
- `-c credential.helper=` vem por último e limpa a lista inteira, inclusive o helper por URL que o `gh auth setup-git` grava; com `GIT_TERMINAL_PROMPT=0` não há prompt. O root não usa o token do dono no postStart.
- O script da `main` (essencial) só faz `git -C /workspaces/Forge config` (lê `.git/config`, protegido no sandbox; `config` não executa hook nem fsmonitor) e roda `instalar-atalho.sh` e `forge-sempre-atual` do installPath do plugin, que `plugin_ativo` restringe a `~/.claude/plugins/cache` (negado à escrita no sandbox). `container_vigente`, que roda `scripts/jarvis-forge` do work tree, fica fora com `FORGE_PREPARO_ESSENCIAL=1`.
- `mktemp -d` do root fica em `/tmp`, fora da escrita do sandbox; sem corrida explorável.
- A `main` remota tem a marca da guarda (`FORGE_PREPARO_ESSENCIAL:-0`), então o postStart não falha por main antiga.

O que aperta: o root volta a rodar só o que passou por PR e pelo merge do dono (B2), agora sem credencial nenhuma na rede; falha de clone, guarda ou preparo aparece (ERRO e rc 1) em vez de ser engolida; o caso de abuso do B2 volta a cobrir o Forge.
O que fica neutro: `FORGE_PREPARO_ESSENCIAL=1`; a execução do cache do plugin; o vetor pelo próprio `devcontainer.json` (já existia, cartão da rodada anterior ao `tech-lead`, ainda aberto); a dependência de rede no início, que é disponibilidade, não segurança.
O que afrouxa: nada no delta.

Cartão (fora do delta, `devops-engineer`, recomendação): a mensagem de ERRO manda o dono rodar `bash /workspaces/Forge/scripts/preparar-estacao.sh --container`, o script do work tree, completo (com `jarvis-forge` do work tree), como root. É ação deliberada do dono e já existia; vale o comando manual também partir do clone da `main` ou avisar que roda a branch que estiver na raiz.

## Riscos aceitos e ferramentas
Nenhum risco aceito. CI do head a5f6c0f1: as 10 partes da suíte (3.12 e 3.14), instalação, catraca, passos, verificações longas e teto de pulados verdes; vermelhos só `bateria (pareceres)` e o agregado `bateria`, que esperam os pareceres desta volta. Ferramentas: leitura do diff, a sonda local do clone e os 3 testes de abuso acima; o resto da suíte só no CI.
