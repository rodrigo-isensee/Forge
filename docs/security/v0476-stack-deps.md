---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0476-stack-deps
commit: f10912559b0561216f157059b9828099c5ee463e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0474 (E3.269, branch melhoria/v0476-stack-deps)

Revalidação por delta da rodada aprovada no head ecfc40c3 (E3.258). Delta lido: `forge-check parecer delta docs/security/v0476-stack-deps.md`, intervalo ecfc40c3..f1091255; no domínio `bin/forge-copia` (`env_sem_credencial`, lista fixa) e `stacks/node-react/pronto.md` (uma frase); `tests/mutantes/v0476-stack-deps-2.json`, fora do domínio, lido só para conferir que a guarda não perdeu mutante.

## Gatilhos
Gatilhos: execução de comando externo por ferramenta do Forge, cadeia de suprimentos (dependências de terceiros instaladas na cópia), segredo no ambiente (token do bot)

## Achados
- A4 (recomendado) stacks/python/instalar.json:1 · a instalação do pacote local (e de pacote só de fonte do lockfile) usa o isolamento de build do gerenciador, que baixa o backend de build do índice sem hash; resíduo de A1, estreito (só o backend de build) e já sem o token.

## Sondas

## Detalhe dos achados
**Delta de `bin/forge-copia:50`:** saem da lista fixa `GH_TOKEN`, `GITHUB_TOKEN`, `GH_ENTERPRISE_TOKEN` e `GITHUB_ENTERPRISE_TOKEN`; os quatro contêm `TOKEN` e continuam fora pelo padrão de nome (`bin/forge-copia:51-53`, comparação em `k.upper()`). Ficam na lista fixa os que o padrão não cobre: `GIT_ASKPASS`, `SSH_AUTH_SOCK`, `GIT_CONFIG_COUNT`, `GIT_CONFIG_PARAMETERS`, além do prefixo `GIT_CONFIG_KEY_`/`GIT_CONFIG_VALUE_`. Sem perda de proteção. Sonda local (valores falsos, só nomes impressos): com `GH_TOKEN`, `GITHUB_TOKEN`, `GH_ENTERPRISE_TOKEN`, `GITHUB_ENTERPRISE_TOKEN`, `gh_token`, `NPM_TOKEN` e `MINHA_VAR` no ambiente, `env_sem_credencial()` manteve só `MINHA_VAR`. Teste: `test_instalacao_roda_sem_credencial_no_ambiente` segue pondo os quatro nomes e exigindo a ausência.

**Mutantes:** M2 e M3 da spec 2 (que mutavam a lista fixa) saem porque o texto mutado deixou de existir; a guarda do padrão `TOKEN` segue morta por mutante em `tests/mutantes/v0476-stack-deps-3.json` ("nome com TOKEN sai do ambiente"). `python3 -I tests/catraca.py --base origin/develop`: rc=0.

**`stacks/node-react/pronto.md:13`:** a frase nova documenta o efeito colateral (registro privado com `NPM_TOKEN` não autentica na cópia). Correta e sem dado sensível; falha fechada, que é o lado certo.

**A4** (`stacks/python/instalar.json:1`): inalterado pelo delta; texto, caminho de ataque, severidade (baixa) e correção mínima no parecer do head 95605e66 (no git). Dono: `forge:devops-engineer`. Segue recomendado (R-REVIEW: critério não mudou).

## Revalidação
- Delta lido: ecfc40c3..f1091255 (acima). Achados anteriores: A1, A2, A3 corrigidos em rodadas anteriores; A4 aberto, recomendado.
- Testes rodados: `python3 -m unittest tests.test_forge_copia` (30 testes, OK); catraca rc=0. A suíte inteira roda no CI do PR (a branch ainda sem PR nem execução de CI): o merge depende dele.
- Ferramentas: sem varredura nova; o delta não traz dependência nem segredo.

## Riscos aceitos
Nenhum.
