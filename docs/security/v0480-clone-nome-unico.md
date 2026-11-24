---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-clone-nome-unico
commit: 56f3d992094b15b88b6210019abc1104ee4bcf1a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0480-clone-nome-unico (PR #860, E172.33, volta por delta)

Gatilhos: forge-check (controle que monta o comando copiado pelo agente), R-CONFORMIDADE.

Delta lido: `forge-check parecer delta` de d33eb54d..56f3d992; no domínio `bin/forge-check` (linhas 9567 e 9629) e `bin/forge-testes:160`; fora do domínio, lidos também `tests/test_forge_copia.py` (teste novo do `-` inicial e o texto da linha da cópia), o fragmento do changelog e o mutante. Já lido na rodada anterior (no git, parecer de d33eb54d): o restante do diff 5f1c6e97..d33eb54d.

Mérito do delta: **só aperta** (A2) e **neutro** (A1, A3).
- A2: o `id:` passa por `valor_de_shell_seguro("pedido", ...)`, isto é `NOME_SEGURO_DE_BRIEF` `[A-Za-z0-9][A-Za-z0-9._-]*` (bin/forge-check:9687), subconjunto estrito de `ID_DE_PEDIDO` `[A-Za-z0-9._-]+` (bin/forge-check:416): só recusa mais (o `-` inicial), não aceita nada novo.
- A3: só muda texto; a crase traz um subcomando (`forge-copia clone ...`) e a alternativa `worktree` sai da crase. Os valores interpolados seguem os mesmos (`copia` checada por `valor_de_shell_seguro("raiz")`, branch e papel como antes).
- A1: `test_forge_copia` entra na tupla `FORGE_CHECK`; só amplia o que o plano dirigido roda.

Provas: `python3 -m unittest tests.test_forge_copia` 77 OK (inclui `test_id_do_pedido_com_hifen_no_inicio_nao_vira_opcao`, `--lote` e `-h` saem `PREENCHER`); `tests.test_testes_tocados.MapaDoForgeCheck` 3 OK. CI do head 56f3d992 (run 45436339103): as dez partes da suíte (3.12 e 3.14), passos, verificações longas, instalação e teto de pulados verdes; vermelhos só `bateria (pareceres)`, o agregador `bateria` (log: `pareceres: failure`, demais `success`) e `catraca` (rótulo do dono para `bin/forge-check`), esperados nesta fase e não achado.

Achados anteriores: A1 (bloqueante) corrigido em bin/forge-testes:160; A2 (recomendado) corrigido em bin/forge-check:9567 com teste; A3 (recomendado) corrigido em bin/forge-check:9629.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta, os testes dos arquivos tocados e o CI do head (`gh pr checks`, `gh run view --job`). Varredores de segredo e SAST não estão no PATH (lacuna registrada; o delta não toca segredo nem dependência).
