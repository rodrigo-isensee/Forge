---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: cf679683033698c8ca97f8ec587c008c00cd0a9f
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E123.8, volta do hook ordens)

Revalidação por delta (`forge-check parecer delta`, intervalo c63e9615..cf679683, sem o que veio da develop). Lidos, no domínio: `hooks/ordens.py`, `hooks/conformidade.py` (listas do controle), `docs/adr/0003-hooks-deterministicos-e-silenciosos.md` (emenda, itens 1 e 6), a remoção de `templates/projeto/.forge/ordens-em-vigor.md`, as 8 fixtures `tests/hooks/conformidade/ordens-*.json` e `tests/test_hooks.py` (`OrdensEmVigor`). A rodada anterior (4e8c85bb, no head c63e9615) fica no git.

Gatilhos: hook de controle (texto injetado na sessão principal a cada mensagem), política de conformidade (mapa de donos), afrouxa-regra (ADR 0003 item 1).

## Achados
- A1 (bloqueante) hooks/conformidade.py:3808 · segue aberto: a guarda cobre o arquivo, mas ele mora em docs/kanban/, pasta sem guarda; `cp <pasta>/* ~/.forge-contrib/docs/kanban/`, `cp x .../ordens-em-vigo?.md` e rm -rf/mv de kanban mais mv de pasta forjada passam e injetam (S1-S3)
- A2 (bloqueante) hooks/conformidade.py:1609 · segue aberto: a fonte passou à cópia principal, mas a entrada .forge/ordens-em-vigor.md só casa relativa à raiz do cwd; o dev com cwd na worktree grava <cópia principal>/.forge/ordens-em-vigor.md e o texto sai como ordem do dono (S4, S5)
- A3 (recomendado) bin/forge-init:221 · segue aberto em parte: o modelo não traz mais o arquivo, mas `ignorados` não o inclui; criado pelo Jarvis, ele entra no git e um commit de branch chega à cópia do Jarvis pelo merge

## Sondas
- S1 · sessão do Forge, dev, Bash `cp $SD/k/* ~/.forge-contrib/docs/kanban/` (k/ordens-em-vigor.md forjado), executado e o ordens rodado · espera: código 2 · obtido: código 0 e o ordens injeta "ordem forjada pelo dev" (para docs/briefs/: código 2)
- S2 · idem, Bash `cp $SD/x ~/.forge-contrib/docs/kanban/ordens-em-vigo?.md` · espera: código 2 · obtido: código 0, e o ordens injeta "ordem forjada pelo dev"
- S3 · idem, Bash `rm -rf ~/.forge-contrib/docs/kanban` e depois `mv $SD/k ~/.forge-contrib/docs/kanban` · espera: código 2 em ao menos um · obtido: código 0 nos dois, e o ordens injeta "ordem forjada pelo dev" (o mesmo mv para docs/briefs: código 2)
- S4 · projeto, dev com cwd na worktree {tmp}/wt, Bash `echo 'ordem forjada pelo dev' >> {tmp}/proj/.forge/ordens-em-vigor.md` · espera: código 2 · obtido: código 0 (Write e `>> ../proj/...`: 0; Write em {tmp}/proj/.forge/config.json: 2)
- S5 · depois de S4, ordens no UserPromptSubmit com cwd {tmp}/proj (sessão do Jarvis) · espera: "ordem do dono" · obtido: última linha "ordem forjada pelo dev"

## Detalhe dos achados
**A1** (alta). O que a volta fechou, conferido por sonda (código 2 para dev e para seguranca; 0 para o jarvis): Write, Edit, `>`, `>>`, `tee -a`, `cp` para o nome do arquivo, `python3 -c "open(...)"`, `cd ~/.forge-contrib/docs/kanban && echo x > ordens-em-vigor.md`, `git -C ~/.forge-contrib checkout HEAD -- docs/kanban/ordens-em-vigor.md`, e as 8 fixtures. O `ln -sfn <wt> docs/kanban` agora cala (a base é `docs/kanban` sem resolver, `hooks/ordens.py:37`, e `test_no_forge_a_pasta_kanban_por_link_sai_da_base`). O que fica aberto vem de a entrada ser um arquivo dentro de uma pasta sem dono: `CAMINHOS_DO_CONTROLE` casa `briefs/` e `pedidos/` como pasta, por isso `cp` para a pasta, `rm -rf` e `mv` de pasta forjada recusam lá; para `docs/kanban/` não há nada, e o nome do arquivo fora da linha (S1) ou num curinga (S2) escapa de `CONTROLE_NO_TEXTO`. Caminho de ataque: um subagente da sessão do Forge, num passo, deixa um texto que entra no contexto do Jarvis a cada mensagem como "ordens do dono". Correção mínima, só nas listas e na constante da fonte: mover a fonte do Forge para uma pasta própria, `~/.forge-contrib/docs/ordens/ordens-em-vigor.md` (`NO_FORGE` em `hooks/ordens.py:21` e a entrada de `hooks/conformidade.json:67`), e pôr a pasta em `CAMINHOS_DO_CONTROLE` como as outras, que fica: `~/.forge-contrib/docs/pedidos/`, `~/.forge-contrib/*/docs/pedidos/`, `~/.forge-contrib/docs/briefs/`, `~/.forge-contrib/*/docs/briefs/`, `~/.forge-contrib/docs/ordens/`; `CONTROLE_NO_TEXTO` com `pedidos|briefs|ordens` no lugar de `ordens-em-vigor`. Com isso S1, S2 e S3 caem no mesmo bloqueio que já vale para `briefs/` (sondado: `cp` para a pasta, `rm -rf docs/briefs` e `mv <forjada> docs/briefs` recusam). Fixtures novas: S1, S2 e S3 na pasta nova (código 2) e a leitura `cat` pelo dev (código 0, legítimo; hoje passa). Esforço P. Dono: tech-lead.

**A2** (alta). O lado do `ordens` está certo: com o `cwd` na worktree ele lê a cópia principal (sonda: "ordem do dono"), e trocar o `.git` da worktree por pasta (`rm .git && git init`, `mv .git .git.bak && mkdir .git`) recusa no conformidade (código 2, guarda do `.git` da raiz). Mas a correção moveu a fonte para um caminho que a guarda não vê do lugar onde o dev trabalha: em `hooks/conformidade.py:1601-1611` a entrada com dono (`.forge/ordens-em-vigor.md`, `hooks/conformidade.json:66`) só casa pelo caminho relativo à raiz da sessão (`do_proj`), que no subagente é a worktree; `em_qualquer_lugar` vale só para entrada sem dono. Caminho de ataque: o dev, na worktree dele (o caso comum em projeto), grava a cópia principal pelo caminho absoluto ou por `../` (S4); a sessão do Jarvis, com `cwd` na cópia principal, injeta o texto na próxima mensagem (S5). É mais provável que o A2 original, que exigia o `cwd` do Jarvis na worktree. Correção mínima: no conformidade, a entrada `.forge/ordens-em-vigor.md` casa também relativa à cópia principal (`diretorio_comum(raiz).parent`, o mesmo cálculo de `fontes` em `hooks/ordens.py:39-42`), além da raiz da sessão. Fixtures: dev com `cwd` na worktree e Write, `>>` absoluto, `>> ../proj/...`, `cp` e `ln -sf` na cópia principal (código 2); o Jarvis no mesmo caminho (código 0). Esforço P a M. Dono: tech-lead.

**A3** (baixa). Estado: a remoção do modelo (`test_o_modelo_de_projeto_nao_traz_o_arquivo_de_ordens`) tira o arquivo da instalação, mas o arquivo que o Jarvis cria na 1.ª ordem fica fora do git só se for ignorado. Correção mínima: `.forge/ordens-em-vigor.md` em `ignorados` (`bin/forge-init:221`). Esforço P. Dono: tech-lead.

## Lacuna da base (rm -rf da pasta mãe): cartão à parte
Decisão: a lacuna da pasta mãe `~/.forge-contrib/docs` não bloqueia este item e vira cartão de segurança. Evidência: no head, como na base 0e4b59a7 (as listas dela só têm pedidos e briefs), passam com código 0, sessão do Forge, papel dev: `rm -rf ~/.forge-contrib/docs`, `mv ~/.forge-contrib/docs ~/.forge-contrib/d2` e `mv <pasta forjada> ~/.forge-contrib/docs`; o mesmo vale para o pedido e o brief, não só para as ordens, e a causa é `checar_remocao` (`hooks/conformidade.py:1956`) pular as entradas com dono. A mesma família aparece no projeto: `.forge/pausa.json` da cópia principal, gravado do `cwd` na worktree, passa (código 0), como no A2. Cartão: `checar_remocao` e o casamento de caminho cobrem as entradas com dono (pasta mãe e cópia principal), com fixtures para pedidos, briefs, ordens e pausa; dono tech-lead, severidade média. A parte de `docs/kanban` não é dessa lacuna: é do A1, porque nasce de a fonte deste item morar numa pasta sem guarda, e a correção do A1 a fecha só com as listas.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do delta e sondas locais pela máquina de fixtures (`Fixture.montar` e `rodar` de `tests/test_hooks.py`), fora do repositório. A suíte inteira não foi rodada (brief: sem suíte local) e não há CI desta branch citado no brief.
