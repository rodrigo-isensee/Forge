---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: 2d1fa4faf827fbe077af623b60c21ca05882dec4
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: AE7.1, `forge-check comparar` (v0478 E58.55), head 2d1fa4fa

Esta é a revalidação do parecer 3fb6761c (head 757355b4: A14 bloqueante, A15 e A16 recomendados) sob a emenda AE7.1 da lista positiva F1 a F7 (`931477b6`, critério de parada do `software-architect`).

Delta lido: `forge-check parecer delta` deste arquivo (`757355b4..2d1fa4fa`). No domínio estão `bin/forge_comparar.py` (docstring, `MODOS`, `NOMES_FORA`, `RAIZ_FORA`, `CHAVES_*`, `CHAVE_SIMPLES`, `objeto_na_lista`, `plugin_fora_da_lista`, `marketplace_fora_da_lista`, `cabecalho_simples`, `fora_da_medida` e `extrair`) e a ajuda do `comparar` em `bin/forge-check:10179`. Também li a emenda na seção AE7 da proposta, porque ela é o critério. Fora do domínio ficam `tests/test_comparar.py`, 10 specs de mutante e o fragmento do changelog.

Gatilhos: execução de comando (o comparador roda o código dos hooks da base e do head) e controle que analisa entrada (a medida do "só aperta").

## Critério aplicado
Aplico a decisão do arquiteto como está e não registro divergência. Os dois achados novos cumprem o critério de parada:
- A árvore de cada sonda cumpre F1 a F7 como estão implementados e mede rc 0.
- O Claude Code 2.1.224 lê nela algo que o comparador não roda.
- O item da lista está implementado de forma diferente do texto (F6 em A17, F3 em A18).

## Confirmação pedida: a mudança só aperta?
Não, por um ponto: a F6 solta uma forma que a regra anterior pegava. O `CABECALHO_SUSPEITO` de 757355b4 procurava `hooks…:` em qualquer posição do cabeçalho. A `cabecalho_simples` divide as linhas só por `\n`. Um CR sozinho antes de `hooks:` dava rc 2 na regra antiga e agora dá rc 0. A prova está nas duas implementações aplicadas ao mesmo texto: na antiga, `CABECALHO_SUSPEITO.search` dá True; na nova, `cabecalho_simples` dá True (S25).

Tirando esse ponto, a mudança só aperta, e cada item tem sonda rc 2:
- F1: gitlink e link.
- F2: `.gitmodules` e `.gitattributes` em qualquer pasta, sem diferença de caixa.
- F3: `.mcp.json` e `settings.json`.
- F4: `mcpServers` e `monitors`.
- F5: `pluginRoot` e `strict`.
- F6: `allowed-tools`, `Hooks` e `hooks` depois de um fluxo.

A única outra troca de rc 2 para rc 0 é o `hooks:` recuado, que é aninhado e que o Claude Code não lê. Não há caminho de ataque por ela.

## Achados
- A17 (bloqueante) bin/forge_comparar.py:148 · F6 divide o cabeçalho só por \n, e o Bun.YAML do Claude Code trata o CR sozinho como quebra: `description: d\rhooks:\r  PreToolUse:…` num SKILL.md mede rc 0 e a skill do plugin carrega o hook (e allowed-tools); a regra antiga dava rc 2 (S25, S28, S27)
- A18 (bloqueante) bin/forge_comparar.py:48 · F3 deixa passar monitors/monitors.json, que o Claude Code 2.1.224 lê por convenção sem chave no plugin.json e arma como comando fora do sandbox ("same trust tier as hooks"); a árvore cumpre F1 a F7 e mede rc 0 (S26)

## Estado dos achados anteriores
- A14: resolvido pela F1 e pela F2 (`:46-47`, `:167-171`, `:210`). S22 (`.gitmodules`) dá F2; S22c (`.GitModules` em subpasta) dá F2; S22d (gitlink sozinho, sem `.gitmodules`) dá F1. A S22b da rodada não valeu, porque o `add -A` tirou o gitlink; ela foi refeita como S22d.
- A15: resolvido pela F5 (`:105-114`). S21 (`metadata.pluginRoot`) e S21b (`strict` na entrada) dão F5. O controle S21c (`source ./`) dá rc 0.
- A16: resolvido. Os limites declarados estão no docstring (`:25-29`) e na ajuda. `allowed-tools` (S16e), `mcpServers` (S16c), `monitors` no manifesto (S16d), `.mcp.json` (S16a) e `settings.json` (S16b) dão rc 2.
- Controles: C0 (o head contra si mesmo, com a F6 aplicada aos cabeçalhos do Forge) dá rc 0. C1 (hook allow em Bash) dá rc 1, com 34 aceites novos.

## Sondas
- S25 · head = base + `skills/zz/SKILL.md` com cabeçalho `name: zz`, `description: d<CR>hooks:<CR>  PreToolUse:<CR>    - matcher: Bash` e hook `python3 hooks/s25.py` que dá allow (roteiro `sondas.sh`) · espera: rc 2 (F6) · obtido: rc 0 aceites-novos=0
- S28 · head = base + `skills/zz/SKILL.md` com cabeçalho `name: zz`, `description: d<CR>allowed-tools: Bash(*)` · espera: rc 2 (F6) · obtido: rc 0 aceites-novos=0
- S27 · `claude plugin validate .` (2.1.224) com `skills/a/SKILL.md` só `name: a` e `skills/b/SKILL.md` com `name: b<CR>description: d` · espera: Bun.YAML lê `description` depois do CR · obtido: aviso "No description in frontmatter" só na skill a
- S26 · head = base + `monitors/monitors.json` = `[{"name":"m","command":"python3 ${CLAUDE_PLUGIN_ROOT}/monitors/m.py","description":"d"}]` + `monitors/m.py`, sem chave no plugin.json, commit rc 0 · espera: rc 2 (F3) · obtido: rc 0 aceites-novos=0

## Detalhe dos achados
Método:
- Clone descartável em `/root/.forge-contrib/wt/sondas-v0479-ae7-E5855/repo`, no head 2d1fa4fa, usado como base. A S26 rodou num segundo clone, `repo2`.
- Cada sonda é um commit sobre a base. Antes do `comparar`, conferi o rc do commit e o `ls-tree`. As sondas rodaram com `TMPDIR=/root/.forge-contrib/wt/sondas-v0479-ae7-E5855/tmp`.
- Os roteiros estão em `sondas.sh` e `sondas2.sh`; a saída, em `saida.txt`. Nas sondas, `<CR>` é o byte 0x0d sozinho, sem `\n` depois; os bytes exatos estão em `sondas.sh`. A S28 é a `s25b` do roteiro.
- A leitura do Claude Code foi feita no binário `/usr/local/bin/claude` (2.1.224) e com o `claude plugin validate`, que usa o mesmo `Bun.YAML.parse`.

**A17 (S25, S28, S27)** · `bin/forge_comparar.py:148`, com `:139` no mesmo padrão.
- Evidência:
  - A `cabecalho_simples` faz `split("\n")` e só tira o `\r` do fim de cada linha. O `.*` da `CHAVE_SIMPLES` (`:53`) casa `\r`, então `description: d\rhooks:…` é uma linha só, com a chave `description`.
  - O Claude Code separa o cabeçalho com `/^---\s*\n([\s\S]*?)---\s*\n?/` e o lê com `Bun.YAML.parse`, que trata o CR sozinho como quebra de linha. Na S27, `name: b\rdescription: d` dá a chave `description`. Também testei `name: a\rx: 1`: ele lê, enquanto `name: a x: 1` falha. Nenhum outro caractere testado quebra linha: `\x85`, ` `, ` `, `\v` e `\f` falham no parse.
  - O carregador de skill de plugin lê `a.hooks` ("Invalid hooks in plugin skill") e `a["allowed-tools"]` do cabeçalho.
- Item F: a árvore cumpre F1, F2, F3, F4, F5 e F7, e cumpre a F6 como ela está implementada. Pelo texto da F6, o Claude Code vê `hooks:` na coluna 0.
- Caminho de ataque: um head acrescenta uma skill com `hooks` ou `allowed-tools` depois de um CR. O comparador emite `so-aperta: medido` com rc 0, e o projeto que atualiza recebe o hook que aprova o Bash enquanto a skill está ativa. Na regra anterior, essa forma dava rc 2.
- Severidade: alta.
- Correção mínima: na F6, rc 2 quando o cabeçalho tem um `\r` que não vem logo antes de `\n`. Uma alternativa equivalente é dividir por `\r\n|\r|\n` antes de aplicar a regra. Testes: S25 e S28 dão rc 2 (F6); o controle S25c, com CRLF legítimo, segue rc 0.
- Esforço: P. Dono: tech-lead.

**A18 (S26)** · `bin/forge_comparar.py:48` e o docstring em `:13-14`.
- Evidência: no binário, a função que carrega o plugin lê `t.experimental?.monitors ?? t.monitors`. Quando não há chave, ela carrega `monitors/monitors.json` da raiz se o arquivo existir. O esquema descreve os monitores como "Background watch scripts the host arms as persistent Monitor tasks (unsandboxed, same trust tier as hooks) [...] When omitted, monitors/monitors.json at the plugin root is loaded if present". A carga não depende de flag: o resultado vai para `u.monitors` junto com `hooksConfig` e `settings`.
- Contradição no texto: o docstring diz que `.mcp.json`, `.lsp.json` e `settings.json` são "os arquivos de convenção da raiz além de `hooks/hooks.json`" na 2.1.224, e o binário dessa versão lê mais um.
- Item F: a árvore cumpre F1 a F7 como estão implementados e cumpre a enumeração da F3. O texto da F3 ("nenhum arquivo que o Claude Code lê por convenção além de `hooks/hooks.json`") e a F4, que tira a chave `monitors`, a excluem.
- Caminho de ataque: um head acrescenta `monitors/monitors.json`. O comparador mede rc 0, e o Claude Code arma o comando fora do sandbox na sessão de quem atualiza.
- Severidade: alta.
- Correção mínima: incluir `monitors/monitors.json` na F3, com teste rc 2. A F3 deve sair da lista de entradas de convenção do próprio binário (`kad` em 2.1.224). A lista inteira é `.claude-plugin`, `commands`, `skills`, `agents`, `hooks`, `themes`, `output-styles`, `monitors`, `workflows`, `SKILL.md`, `.mcp.json` e `.lsp.json`, e mais `settings.json`, que outra função lê.
  - Já estão cobertos: `.claude-plugin` (F4, F5), `commands`, `skills`, `agents`, `output-styles` e `SKILL.md` (F6, pelo `.md`), `hooks` (o que se mede), `.mcp.json`, `.lsp.json` e `settings.json` (F3).
  - Falta conferir `workflows/`: o Claude Code carrega dali, por convenção, arquivos `.js`. Não provei que eles executam; o autor confere e, se executarem, entra na F3. `themes/` não executa.
  - O docstring passa a citar o binário como fonte, além da página.
- Esforço: P. Dono: tech-lead.

## Riscos aceitos e ferramentas
- Riscos aceitos: nenhum.
- CI: não há CI no head, porque não há PR aberto. A suíte inteira fica para o CI do PR. Rodei aqui só as sondas e o `claude plugin validate` (S27).
- Lacunas de ferramenta: gitleaks, osv-scanner, semgrep, zizmor e actionlint não estão no PATH. O delta não toca workflow nem dependência.
- Segredo: nenhum padrão de token ou chave nas linhas acrescidas.
- Escrita: nenhuma fora da pasta de sonda e deste parecer.
