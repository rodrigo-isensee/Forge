---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0476-stack-deps
commit: ecfc40c355010520c48d15ded98990fe3b66464b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0474 (E3.258, branch melhoria/v0476-stack-deps)

Revalidação por delta da rodada aprovada no head 95605e66 (E3.248). Delta lido: `forge-check parecer delta docs/security/v0476-stack-deps.md`, intervalo 95605e66..ecfc40c3; no domínio só `bin/forge-copia` (`env_sem_credencial`); `tests/test_forge_copia.py` e os mutantes, fora do domínio, lidos só para conferir a prova.

## Gatilhos
Gatilhos: execução de comando externo por ferramenta do Forge, cadeia de suprimentos (dependências de terceiros instaladas na cópia), segredo no ambiente (token do bot)

## Achados
- A4 (recomendado) stacks/python/instalar.json:1 · a instalação do pacote local (e de pacote só de fonte do lockfile) usa o isolamento de build do gerenciador, que baixa o backend de build do índice sem hash; resíduo de A1, estreito (só o backend de build) e já sem o token.

## Sondas

## Detalhe dos achados
**A3 (recomendado na rodada anterior): corrigido.** `bin/forge-copia:48-54`: `GIT_CONFIG_PARAMETERS` entrou no conjunto fixo e todo nome que contenha `TOKEN`, `SECRET` ou `PASSWORD` sai, comparado em maiúsculas (`k.upper()`), o que cobre também nome em minúsculas. O resto da lista de A2 segue igual. Prova: `test_instalacao_tira_config_injetada_e_nomes_de_segredo` põe `GIT_CONFIG_PARAMETERS`, `FOO_TOKEN`, `bar_secret_x`, `MEU_PASSWORD` e `TOKEN` no ambiente e confere que nenhum chega ao comando, mantendo `MINHA_VAR`. Sonda refeita no ambiente real desta estação (só nomes, nunca valores): `env_sem_credencial()` filtrada por `token|secret|password|GIT_CONFIG|ASKPASS|SSH_AUTH|CREDENTIAL|API_KEY` devolveu lista vazia; na rodada anterior saíam `GIT_CONFIG_PARAMETERS` e três nomes com `TOKEN`.

A remoção de `test_instalacao_real_so_com_lockfile` não perde cobertura: `test_todo_instalar_json_usa_modo_congelado_ou_hash_e_detecta_o_lockfile` exige que todo item de `detecta` contenha `lock`, o que já exclui `package.json` e `pyproject.toml`.

**A4, backend de build sem hash** (`stacks/python/instalar.json:1`): inalterado pelo delta; texto, caminho de ataque, severidade (baixa) e correção mínima no parecer do head 95605e66 (no git). Dono: `forge:devops-engineer`. Segue recomendado (R-REVIEW: critério não mudou).

## Revalidação
Delta 95605e66..ecfc40c3 lido inteiro no domínio (uma função). O que estava correto antes (origem do `instalar.json` no plugin, argv sem shell, `cwd` na cópia confinada, detecção só pelo lockfile, instalação congelada ou com hash) não foi tocado. Estado: A1 e A2 corrigidos (rodada anterior), A3 corrigido nesta, A4 aberto e recomendado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Provas rodadas no head ecfc40c3: `python3 -I tests/catraca.py --base origin/develop` (rc 0); `python3 -m unittest tests.test_forge_copia` (30 testes, OK); `python3 -m unittest tests.test_ambiente_git` (20 testes, OK); a sonda do ambiente real. CI: a branch não tem PR, sem rodada no head ecfc40c3; a suíte inteira fica para o CI do PR, obrigatório para o merge. Ferramentas: `gitleaks`, `osv-scanner` e `semgrep` não usados (o delta não adiciona dependência nem segredo; revisão por leitura e sonda).
