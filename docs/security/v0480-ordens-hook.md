---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: 8e84ef3b57fa6fe7cee56e7b640dfecaba1a8271
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E123.12, 2ª volta do hook ordens)

Revalidação por delta (`forge-check parecer delta`, intervalo cf679683..8e84ef3b, sem o que veio da develop). Lidos, no domínio: `hooks/conformidade.py` (`PELA_COPIA_PRINCIPAL`, `relativos_a_copia_principal`, listas do controle), `hooks/conformidade.json:66-67`, `hooks/ordens.py:20-21`, `bin/forge-init:221`, a emenda da ADR 0003 (itens 1 e 6), as fixtures `tests/hooks/conformidade/ordens-*.json`, as 2 de `tests/hooks/ordens/` e `tests/test_hooks.py` (`OrdensEmVigor`). A rodada anterior (ec50f8f2, no head cf679683) fica no git.

Gatilhos: hook de controle (texto injetado na sessão principal a cada mensagem), política de conformidade (mapa de donos), afrouxa-regra (ADR 0003 item 1).

Estado dos achados anteriores:
- A1 resolvido: as ordens do Forge foram para `docs/ordens/`, guardada como pasta (`hooks/conformidade.json:67`, `hooks/conformidade.py:3819`); sondado, sessão do Forge, dev: `cp` para a pasta, `rm -rf`, `git -C ... checkout HEAD -- docs/ordens/`, `ln -sfn`: código 2; `cat` do dev e escrita do jarvis: 0. Fixtures `ordens-s1`, `ordens-s2`, `ordens-s3-*`.
- A2 resolvido para o caminho literal (`hooks/conformidade.py:1612`): dev com cwd na worktree, na cópia principal, Write, Edit, `>>`, `../`, `cd ... &&`, link já existente na worktree, `mv`, `cp`, `sed -i`, `python3 -c open`, `rm`: código 2; jarvis e `cat` do dev: 0. Fixtures `ordens-s4-*` e `tests/hooks/ordens/s5-*`.
- A3 resolvido: `.forge/ordens-em-vigor.md` nos ignorados (`bin/forge-init:221`).

`CONTROLE_NO_TEXTO` com `ordens` não recusa o legítimo sondado: o dev editando `hooks/ordens.py` e copiando para `tests/hooks/ordens/` na sua cópia de `wt/` (código 0).

## Achados
- A4 (bloqueante) hooks/conformidade.json:66 · o S2 da rodada anterior no projeto: o arquivo é entrada de arquivo numa pasta sem dono (.forge/), e o nome com curinga escapa; o dev na worktree faz `cp x ../proj/.forge/ordens-em-vigo?.md` (ou *, [r], tee, >>) e o texto vira ordem do dono (S1-S3)

## Sondas
- S1 · projeto, dev com cwd na worktree {tmp}/wt, Bash `cp x ../proj/.forge/ordens-em-vigo?.md` (arquivo existente na cópia principal) · espera: código 2 · obtido: código 0
- S2 · idem, `cp x {tmp}/proj/.forge/ordens-em-vigo?.md`, `cp x ../proj/.forge/ordens-em-*`, `cp x ../proj/.forge/ordens-em-vigo[r].md`, `echo f | tee -a ../proj/.forge/ordens-em-vigo?.md`, `echo f >> ../proj/.forge/ordens-em-vigo?.md` · espera: código 2 · obtido: código 0 nos cinco
- S3 · dev com cwd na cópia principal {tmp}/proj, `cp x .forge/ordens-em-vigo?.md` · espera: código 2 · obtido: código 0 (com o nome literal: 2)

## Detalhe dos achados
**A4** (alta). Evidência: `hooks/conformidade.json:66` registra `.forge/ordens-em-vigor.md` como arquivo; a pasta `.forge/` não tem dono, e o nome com curinga não casa a entrada (S1 a S3). É o mesmo defeito do S2 da rodada anterior, que no Forge a volta fechou com a pasta própria (`docs/ordens/`); no projeto ficou o arquivo solto. O bash expande o curinga para o arquivo existente (no `cp`, no `tee` e no redirecionamento com um só casamento), e o hook `ordens` lê a cópia principal na sessão do Jarvis: o texto entra como ordem do dono na próxima mensagem. Caminho de ataque: um subagente dev (instrução injetada por conteúdo que ele leu) na worktree dele, um comando. Correção mínima, só nas listas e nas constantes, como a do A1: a fonte do projeto vai para uma pasta própria, `.forge/ordens/ordens-em-vigor.md`, e a entrada passa a ser a pasta. Lista completa do que muda: `hooks/ordens.py:20` `NO_PROJETO = ".forge/ordens/ordens-em-vigor.md"`; `hooks/conformidade.json:66` `"caminho": ".forge/ordens/"`; `hooks/conformidade.py:3818` `PELA_COPIA_PRINCIPAL = (".forge/ordens/",)`; `bin/forge-init:221` `'.forge/ordens/'` nos ignorados no lugar do arquivo; emenda da ADR 0003, itens 1 e 6; a docstring de `hooks/ordens.py`. Conferido numa cópia fora do repositório com só a entrada e a constante trocadas: S1, S2 e S3 na pasta nova dão código 2, e também `cp ../proj/k/* ../proj/.forge/ordens/` e `rm -rf ../proj/.forge/ordens` (2); link na worktree e `cd ... &&` seguem 2; o jarvis gravando e o `cat` do dev seguem 0. Fixtures novas: S1, S2 (os cinco) e S3 na pasta nova (código 2), o `cp` para a pasta e o `rm -rf` (2), o jarvis e o `cat` (0); as fixtures `ordens-s4-*` e `ordens-dev-*` do projeto mudam de caminho. Esforço P. Dono: tech-lead.

## Cartão à parte (lacuna da base): curinga na pasta e no nome
Não bloqueia este item; soma-se ao cartão da pasta mãe da rodada anterior. Evidência, na base f4836717 e no head: o curinga num componente de pasta passa em entrada com dono, `cp x ~/.forge-contrib/docs/brief?/b1.md` (sessão do Forge, dev: código 0), `cp x .forg?/pausa.json` e `cp x .forg?/recados/a.md` (projeto, dev: 0); e o curinga no nome de entrada de arquivo também, `cp x .forge/pausa.jso?` (0). Neste item, o mesmo vale para `cp x ../proj/.forg?/ordens-em-vigor.md` e `cp x ~/.forge-contrib/docs/orden?/ordens-em-vigor.md` (0), e a pasta própria do A4 não fecha o curinga na pasta (também 0 com a pasta nova). Cartão: o casamento de caminho com dono expande o curinga de cada componente (pasta e nome) contra o disco, ou recusa curinga que possa alcançar entrada com dono, com fixtures para briefs, pedidos, ordens, pausa e recados; dono tech-lead, severidade média.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do delta e sondas locais pela máquina de fixtures (`Fixture.montar` e `rodar` de `tests/test_hooks.py`), fora do repositório, no head, na base e numa cópia com a correção do A4; `python3 -m unittest tests.test_hooks.OrdensEmVigor` no head: 23 testes, OK. A suíte inteira não foi rodada (brief: sem suíte local) e não há CI desta branch citado no brief.
