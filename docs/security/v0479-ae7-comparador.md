---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: caae27c42db773f7984803f27b62ae3da7b4053e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: AE7.1, `forge-check comparar` (v0478 E58.59), head caae27c4

Esta é a revalidação do parecer reprovado `5c0d03d5` (head 2d1fa4fa: A17 e A18 bloqueantes). A rodada anterior está no git e não é recopiada aqui.

Delta lido: `forge-check parecer delta` deste arquivo (`2d1fa4fa..caae27c4`). No domínio estão `bin/forge_comparar.py` (docstring da F3 e da F6, `RAIZ_FORA`, `cabecalho`, `cabecalho_simples` e o teste da F3 em `fora_da_medida`) e a ajuda do `comparar` em `bin/forge-check:10179`. Fora do domínio ficam `tests/test_comparar.py`, 3 specs de mutante, a proposta e o fragmento do changelog.

Gatilhos: execução de comando (o comparador roda os hooks da base e do head) e controle que analisa entrada (a medida do "só aperta").

## Critério aplicado
Uso o critério de parada do arquiteto (emenda AE7). Um achado bloqueia só se:
- a árvore cumpre F1 a F7, mede rc 0 ou 1, e o Claude Code roda nela algo diferente; ou
- o item está implementado de forma diferente do texto.

Nenhuma sonda desta rodada cumpre o critério, então não há achado.

## Estado dos achados anteriores
- A17: resolvido. `cabecalho` (`:145`) parte o texto com `splitlines`, e `cabecalho_simples` (`:152`) junta e parte por `\n`. O CR sozinho passa a separar linhas.
  - S25 (`hooks` depois de CR) e S28 (`allowed-tools` depois de CR) dão rc 2 (F6).
  - O controle S34 (CRLF legítimo) segue rc 0.
  - O texto da F6 no docstring (`:23-26`) e na ajuda agora descreve a regra implementada.
- A18: resolvido. `RAIZ_FORA` (`:54`) inclui `monitors` e `workflows`, e `fora_da_medida` (`:178`) compara o primeiro nome do caminho, em minúsculas.
  - S26 (`monitors/monitors.json`), S30 (`workflows/w.js`) e S32 (`monitors` como arquivo) dão rc 2 (F3).
  - O controle S33 (`x/monitors/monitors.json`, fora da raiz) segue rc 0.
  - O docstring (`:13-19`) cita a lista de convenção do binário 2.1.224, que conferi no binário nesta rodada (evidência abaixo).
- Controles: C0 (o head contra si mesmo) dá rc 0 com 215 casos. C1 (hook allow em Bash) dá rc 1 com 34 aceites novos.

## Confirmação pedida: a mudança só aperta?
Sim, em tudo o que o Claude Code lê. Comparei a `cabecalho_simples` de 2d1fa4fa com a de caae27c4 sobre os mesmos textos (`cmpf6.py`).

Formas que passam de rc 0 para rc 2:
- CR sozinho (S25);
- `\x85` (S35);
- U+2028 depois de um comentário.

Há duas formas que passam de rc 2 para rc 0. Nas duas, o Claude Code não lê `hooks` nem `allowed-tools`:
- S29: `name:\x85  x`. O pedaço depois de `\x85` está recuado, e a chave da linha é `name`. O Bun.YAML não quebra linha no `\x85`.
- S38: `---\rhooks: 1` fecha o cabeçalho na linha `---`. A regex do Claude Code (`hne=/^---\s*\n([\s\S]*?)---\s*\n?/`) fecha no primeiro `---` do texto, e por isso o `hooks` também fica no corpo para ele. Emulei a regex e o grupo lido é `name: z\n`.

Como o Claude Code fecha o cabeçalho no primeiro `---` em qualquer posição, ele fecha no mesmo ponto que o comparador ou antes. As quebras do `splitlines` incluem as do Bun.YAML (`\n`, `\r`, `\r\n`).

A F3 só ganhou nomes, e o teste por primeiro nome em minúsculas cobre arquivo, pasta e caixa (S31). Ela não libera nada que antes dava rc 2.

## Sondas
- S25 · head = base + `skills/zz/SKILL.md` com `description: d<CR>hooks:<CR>  PreToolUse:…` e hook allow (`sondas.sh`) · espera: rc 2 (F6) · obtido: rc 2 `nao-verificavel (F6 cabeçalho de .md fora da forma simples)`
- S28 · head = base + `skills/zz/SKILL.md` com `description: d<CR>allowed-tools: Bash(*)` · espera: rc 2 (F6) · obtido: rc 2 (F6)
- S27 · `claude plugin validate vp` (2.1.224) com `skills/a/SKILL.md` só `name: a` e `skills/b/SKILL.md` com `name: b<CR>description: d` · espera: Bun.YAML lê `description` depois do CR · obtido: aviso "No description in frontmatter" só na skill a, rc 0
- S26 · head = base + `monitors/monitors.json` e `monitors/m.py` · espera: rc 2 (F3) · obtido: rc 2 `nao-verificavel (F3 monitors/m.py na raiz)`
- S30 · head = base + `workflows/w.js` · espera: rc 2 (F3) · obtido: rc 2 (F3)
- S31 · head = base + `Monitors/monitors.json` · espera: rc 2 (F3) · obtido: rc 2 (F3)
- S32 · head = base + arquivo `monitors` na raiz · espera: rc 2 (F3) · obtido: rc 2 (F3)
- S33 · head = base + `x/monitors/monitors.json` · espera: rc 0 · obtido: rc 0 aceites-novos=0
- S34 · head = base + `skills/zz/SKILL.md` em CRLF legítimo · espera: rc 0 · obtido: rc 0 aceites-novos=0
- S35 · head = base + `description: d<U+0085>hooks: 1` · espera: rc 2 (F6) · obtido: rc 2 (F6)
- S36 · head = base + cabeçalho só com CR · espera: rc 2 (F6) · obtido: rc 2 (F6)
- S37 · head = base + `description: d<CR>  hooks: 1` (recuado, aninhado) · espera: rc 0 · obtido: rc 0 aceites-novos=0

## Método e evidência
Pasta de sonda: `/root/.forge-contrib/wt/sondas-v0479-ae7-E5859`.
- Clone `repo` no head caae27c4, usado como base. Cada sonda é um commit sobre a base. Antes do `comparar`, conferi o rc do commit e o `ls-tree`.
- As sondas rodaram com `TMPDIR=.../sondas-v0479-ae7-E5859/tmp`. O roteiro é `sondas.sh` e a saída está em `saida.txt`.
- A comparação velho × novo da F6 está em `cmpf6.py` (versões em `old/`).
- `claude.strings` tem 40331518 bytes. O arquivo de 0 byte da rodada anterior saiu assim porque `strings` não está no PATH; agora a extração é feita por Python.
- O que li no binário 2.1.224:
  - `kad=[".claude-plugin","commands","skills","agents","hooks","themes","output-styles","monitors","workflows","SKILL.md",".mcp.json",".lsp.json"]`;
  - em `gn_`, `monitors/monitors.json` é carregado quando não há chave;
  - o carregador de skill lê `a.hooks` e `a["allowed-tools"]`;
  - `hne` e `Np` leem o cabeçalho com `Bun.YAML.parse`, e o fallback `g_y` só põe valores entre aspas, sem criar chave.

## Riscos aceitos e ferramentas
- Riscos aceitos: nenhum.
- CI: não há CI no head, porque não há PR aberto. A suíte inteira fica para o CI do PR. Aqui rodei só as sondas e o `claude plugin validate` (S27).
- Lacunas de ferramenta: gitleaks, osv-scanner, semgrep, zizmor, actionlint e `strings` não estão no PATH. O delta não toca workflow nem dependência.
- Segredo: nenhum padrão de token ou chave nas linhas acrescidas.
- Escrita: nenhuma fora da pasta de sonda e deste parecer.
