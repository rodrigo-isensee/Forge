---
tipo: revisao-seguranca
contrato: 1
pedido: hook-raiz-contrib
branch: melhoria/hook-raiz-contrib
commit: 1fa594650a77002bc0f4e638719951147a01a3d4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: hook-raiz-contrib

Revisão estática do diff `139a3b4...1fa5946` (2 commits: `196906c` teste vermelho, `1fa5946` proteção) e sondas do hook `conformidade` com `HOME` isolado em `$TMPDIR/security-engineer-hookraiz/` (projeto com `.forge/versao`, tipos `forge:tech-lead`, `forge:qa-engineer`, `general-purpose`, `forge:jarvis` e sessão sem `agent_type`). `python3 -m unittest tests.test_hooks`: 43 testes, OK.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): o hook `conformidade` (`hooks/conformidade.json:50`, `:53`; `hooks/conformidade.py:265-271`, `:1095`).

## Achados

## Detalhe dos achados
Sem bloqueante. A proteção nova fecha o A1 do review da CONF-BASE-DONO: o Write do tech-lead em `~/.forge-contrib/forge/docs/pedidos/` agora sai com rc 2 e o do jarvis (e da sessão principal) com rc 0.

Sondas (todas com o caminho resolvido por `realpath` antes do casamento, `hooks/conformidade.py:637-639`):
- Recusadas para o não jarvis: Write/Edit em `<pasta>/docs/pedidos/` e `.../briefs/`; o próprio diretório como alvo; `..` (`wt/../forge/...`), `//` e `./`; maiúsculas no nome da pasta (`Forge/`, que o `[^/]+` cobre); Bash com `>`, `>>`, `~`, `$HOME`, `tee`, `cp` (arquivo e pasta de destino), `mv` para dentro e para fora, `rm`, `rm -rf` da pasta `pedidos`, `ln -s`/`ln -sf` com destino na pasta protegida, `sed -i`, `cd` + caminho relativo, `python3 -c` com o literal e `git -C <clone> checkout -- docs/pedidos/...`.
- O `*` não tira nada do que antes era protegido: as entradas antigas (`conformidade.json:49`, `:52`) continuam e o ramo sem `*` de `casa` é o mesmo; em `pode_ser_protegido` (`conformidade.py:1095`) o `rsplit("*")` só alarga o filtro (`/docs/pedidos`), nunca o estreita. O `[^/]+` não atravessa `/` e não casa `.`/`..`, que o `realpath` já tirou.
- Trabalho legítimo nas worktrees de `~/.forge-contrib/wt/` segue livre: Write e Bash em `wt/<nome>/src/` e o parecer do tech-lead em `wt/<nome>/docs/reviews/` saem com rc 0.

Recomendações (não bloqueiam; fora do delta ou sem caminho de ataque realista):
- R1 (média, pré-existente, vale também para as entradas antigas `~/.forge-contrib/docs/` e `docs/pedidos/` do projeto): mexer na pasta-mãe contorna a proteção de dono. `mv ~/.forge-contrib/forge/docs ~/.forge-contrib/forge/d2`, gravar em `d2/pedidos/`, `mv` de volta (rc 0 nos três passos), e também `cp -r`/`rsync -a`/`tar -x -C` com destino numa pasta que contém `pedidos/`. Causa: `checar_remocao` só olha entradas sem dono (`hooks/conformidade.py:675`) e o destino é conferido só pelo próprio caminho. Caminho de ataque: um papel não jarvis (por erro ou instrução injetada) reescreve a linha `conferida <sha40>` do Histórico e abre o `--desde` do `forge-check entrega` (VV-2). O sandbox não cobre (`~/.forge-contrib` é gravável). Correção mínima: em `checar_remocao` e no destino de `mv`/`cp -r`, barrar também, para quem não está em `quem`, a pasta que contém uma entrada com dono; ou registrar o limite na BP-5 de `docs/hooks.md`. Esforço M. Dono: tech-lead (cartão novo).
- R2 (baixa, latente): o `*` só é entendido por `casa` (`hooks/conformidade.py:265-271`); `em_qualquer_lugar` (`:274`), `checar_remocao` (`:678`), o literal de `checar_texto` (`:690`) e `hooks/vigia.py:64` o tratam como caractere. Hoje só há `*` em entradas com dono, que esses ramos não usam (o `python3 -c` com o caminho real foi recusado por outro ramo). Uma entrada futura sem dono com `*` ficaria sem efeito em silêncio. Correção mínima: `entrada_valida` (`:1589-1595`) recusar `*` em entrada com `quem` vazio, ou citar o limite na docstring de `casa`. Esforço P. Dono: tech-lead.
- R3 (informativa): o `*` vale por uma pasta só; `~/.forge-contrib/wt/<nome>/docs/pedidos/` e um link simbólico novo em `~/.forge-contrib/<nome>` -> fora ficam livres, mas nenhum leitor de pedido usa esses caminhos: o `forge-check` lê a cópia principal, a raiz e `~/.forge-contrib/docs/` com `realpath` (`bin/forge-check:698-709`, `:977`). `docs/Pedidos/` com outra caixa é outra pasta no ext4 do home e ninguém a lê. Sem ação.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, sondas locais do hook (`HOME` em `$TMPDIR`) e `python3 -m unittest tests.test_hooks`. Não se aplicam ao diff: `gitleaks`, `semgrep`, `zizmor`/`actionlint` (sem workflow nem segredo no delta).
