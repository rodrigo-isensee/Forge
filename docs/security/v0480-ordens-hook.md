---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: fe14fb1ea179e325195005e2cab46a2bc95d4eaa
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E123.16, 3ª volta do hook ordens)

Revalidação por delta (`forge-check parecer delta`, intervalo 8e84ef3b..fe14fb1e). Lidos, no domínio: `hooks/ordens.py:5,20` (`NO_PROJETO`), `hooks/conformidade.json:66`, `hooks/conformidade.py:3818` (`PELA_COPIA_PRINCIPAL`), `bin/forge-init:222`, a emenda da ADR 0003 (itens 1 e 6), as 11 fixtures `tests/hooks/conformidade/ordens-a4-*.json`, as fixtures de caminho trocado (`ordens-s4-*`, `tests/hooks/ordens/*`) e `tests/test_hooks.py` (`OrdensEmVigor`). A rodada anterior (e29c3dbd, no head 8e84ef3b) fica no git.

Gatilhos: hook de controle (texto injetado na sessão principal a cada mensagem), política de conformidade (mapa de donos), afrouxa-regra (ADR 0003 item 1).

Estado dos achados anteriores:
- A1, A2, A3: seguem resolvidos (A3 agora com a pasta `.forge/ordens/` nos ignorados, `bin/forge-init:222`).
- A4 resolvido, com a correção mínima pedida, item por item: a fonte do projeto foi para a pasta própria `.forge/ordens/ordens-em-vigor.md` (`hooks/ordens.py:20`) e a entrada do mapa de donos passou a ser a pasta (`hooks/conformidade.json:66`, `hooks/conformidade.py:3818`). Sondado no head pela máquina de fixtures (`Hooks.rodar_dados`), fora do repositório, dev com cwd na worktree: `cp x ../proj/.forge/ordens/ordens-em-vigo?.md`, o mesmo absoluto, `ordens-em-*`, `ordens/*`, `ordens-em-vigo[r].md`, `tee -a` e `>>` com `?`, o nome literal, `cp k/* ../proj/.forge/ordens/`, `rm -rf`, `mv` e `ln -sfn` da pasta, `cd ../proj && cp ... vigo?.md`: código 2 em todos; dev com cwd na cópia principal, `cp x .forge/ordens/ordens-em-vigo?.md`, `cp x .forge/ordens/*`, `rm -r .forge/ordens`, `mv .forge .f2`: 2. Legítimos: `cat` do dev com `?` e com `*` e o jarvis gravando (com curinga, da worktree, e `>>` na cópia principal): 0. Fixtures `ordens-a4-*` (9 recusas, 2 liberações) e o teste `test_conformidade_recusa_curinga_no_nome_das_ordens_do_projeto`.

O curinga num componente de pasta (`../proj/.forg?/ordens/...`, `../proj/.forge/orden?/...`) ainda dá 0: é o cartão CONFORMIDADE-CURINGA-PASTA, já aberto, da base e de todas as entradas com dono; não bloqueia este item. O hook novo não está publicado, então não há fonte antiga a migrar; `.forge/ordens-em-vigor.md` solto deixa de ser lido.

## Achados

## Sondas

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do delta e 24 sondas locais pela máquina de fixtures de `tests/test_hooks.py`, fora do repositório, no head; `python3 -m unittest tests.test_hooks.OrdensEmVigor` no head: 24 testes, OK. A suíte inteira não foi rodada (brief: sem suíte local); vale o CI do PR.
