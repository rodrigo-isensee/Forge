---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0476-stack-deps
commit: 8727471d9fdde8d6e9bf04edb75a3c8a91adf9ba
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0474 (E3.306, branch melhoria/v0476-stack-deps)

Revalidação por delta da rodada aprovada no head f1091255 (E3.269). Delta lido: `forge-check parecer delta docs/security/v0476-stack-deps.md`, intervalo f1091255..8727471d, sem o que veio da base; no domínio só `bin/forge-copia` (junção 8e21fb07 com o MP6, conferida também por `git show --remerge-diff 8e21fb07`); `tests/test_forge_copia.py` e `tests/test_forge.py`, fora do domínio, lidos só para conferir a cobertura da recusa por disco.

## Gatilhos
Gatilhos: execução de comando externo por ferramenta do Forge, cadeia de suprimentos (dependências de terceiros instaladas na cópia), segredo no ambiente (token do bot)

## Achados
- A4 (recomendado) stacks/python/instalar.json:1 · a instalação do pacote local (e de pacote só de fonte do lockfile) usa o isolamento de build do gerenciador, que baixa o backend de build do índice sem hash; resíduo de A1, estreito (só o backend de build) e já sem o token.

## Sondas

## Detalhe dos achados
**Junção 8e21fb07 (`bin/forge-copia`):** o conflito do `--remerge-diff` ficou só na docstring (linhas 8-11): a resolução mantém as duas frases (instalação com lockfile e ambiente sem credencial; disco do MP6 "antes de criar") e a linha de saída "1 git ou instalação falhou". O código entrou sem conflito.

**Recusa por disco antes de criar e falha fechada (`bin/forge-copia:111-120`):** a medida vem logo depois de `destino_dentro` e antes do desvio `worktree`/`clone`, então vale para os dois modos e nenhum `git` roda quando recusa. `OSError` de `uso_do_disco` vira `recusa` (rc 2), e `bin/forge_disco.py:24` conta disco sem espaço ocupável como 100%: falha fechada. A medida usa o primeiro pai existente do destino já resolvido (`real`), dentro da pasta liberada. O import de `forge_disco` vem da pasta do próprio script resolvido (`bin/forge-copia:19`), não do diretório corrente: sem sequestro de módulo por cópia de trabalho. Testes: `Disco` em `tests/test_forge_copia.py` (acima do limiar sem chamar o git, disco ilegível recusa, sem espaço ocupável recusa, mede o pai que existe); o pacote falso de `Instalar` leva o `forge_disco.py` (commit 8727471d), o que mantém os testes de instalação vivos.

**Instalação inalterada:** `instalar()` e `env_sem_credencial()` fora do delta; seguem só com o lockfile de `detecta` presente na cópia, argv sem shell e ambiente sem credencial (rodada de f1091255, no git).

**A4** (`stacks/python/instalar.json:1`): inalterado pelo delta; texto, caminho de ataque, severidade (baixa) e correção mínima no parecer do head 95605e66 (no git). Dono: `forge:devops-engineer`. Segue recomendado (R-REVIEW: critério não mudou).

## Revalidação
- Delta lido: f1091255..8727471d (acima). Achados anteriores: A1, A2, A3 corrigidos em rodadas anteriores; A4 aberto, recomendado.
- Testes rodados: `python3 -m unittest tests.test_forge_copia` (36 testes, OK); `python3 -I tests/catraca.py --base origin/develop`: rc=0. A suíte inteira roda no CI do PR: o merge depende dele.
- Ferramentas: sem varredura nova; o delta não traz dependência nem segredo.

## Riscos aceitos
Nenhum.
