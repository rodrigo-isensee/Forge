---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae2-desenho
commit: 0cf8b8ae69d937f7655ff67f25bd0814f2e7c83e
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E121.3, desenho do AE2, o quadro anda com o PR)

Revisão completa única do `docs/propostas/ae2-quadro-anda-com-pr.md` no head 0cf8b8ae: corte P1 a P6, arquivos de cada parte, tabela "uma entra, uma sai" (DECISÃO DO DONO 21/11 20:54, regra 3), merge automático (DECISÃO DO DONO 21/11 20:15) e a troca do trailer pelo argumento. Desenho só de texto: sem suíte, sem mutante. As referências de linha do `bin/forge-fechar` e do `bin/forge-check` foram conferidas no head e batem.

## Achados
- A1 (bloqueante) docs/propostas/ae2-quadro-anda-com-pr.md:41 · `cmd_kanban` é o que o hook `hooks/quadro.py:24` roda em todo Write/Edit do KANBAN.md; com P3, todo projeto com cartão aberto sem histórico passa a ter toda edição do quadro barrada. P6 só migra o Forge. Falta a migração dos projetos ou um corte por data.
- A2 (bloqueante) docs/propostas/ae2-quadro-anda-com-pr.md:33 · O caminho do merge pelo dono (`--limpar`) grava `mesclado em <alvo> (forge-fechar --limpar)` sem `PR #N` (`bin/forge-fechar:1357`); o `ja_mesclado` grava só o head (`:1622`). A contagem da linha 9 perde esses PRs. P1 precisa gravar o PR nos dois motivos.
- A3 (bloqueante) docs/propostas/ae2-quadro-anda-com-pr.md:55 · DECISÃO DO DONO 21/11 20:54, regra 3: trava nova só entra se outra sair. A linha 55 diz "nada a tirar", e na 54 sai um padrão, não uma trava. Nomeie a trava viva que sai em cada linha ou leve as duas à lista do dono de segunda.
- A4 (bloqueante) docs/propostas/ae2-quadro-anda-com-pr.md:6 · Troca a D1 (trailer) e a D3 (`Cartão-parcial`) aceitas pelo dono (pedido v0478:1088) sem a linha "decidido pelo time na ausência do dono" com o "reabre quando" (ordem 20/11 21:34). A reversão da seção 8 cobre só o `--cartao`, não a volta ao trailer.
- A5 (recomendado) docs/propostas/ae2-quadro-anda-com-pr.md:53 · O aviso "quadro editado fora do movimento" compara todas as células (`bin/forge-check:5010`), e a violação nova só compara ID e seção. Ele não está coberto, e sem ele o `--gerar` troca a Obs. editada à mão sem avisar, ao contrário da linha 45.
- A6 (recomendado) docs/propostas/ae2-quadro-anda-com-pr.md:47 · A linha `quadro: ...` não pode sair na lista que o `cmd_kanban` devolve: o hook trata cada item como violação e barraria toda edição. Diga que ela sai só no comando de linha.
- A7 (recomendado) docs/propostas/ae2-quadro-anda-com-pr.md:73 · P4 "em paralelo com P3 em outra branch" toca `bin/forge-check` e `tests/test_kanban*.py`, os mesmos arquivos do P3, o que contraria o corte por arquivo (pedido v0478:1068) e a linha 77. Ponha o P4 depois do P3.
- A8 (recomendado) docs/propostas/ae2-quadro-anda-com-pr.md:71 · P2 (recusa do título) e P4 (condições de fim nas métricas) criam guardas sem `tests/mutantes/<pedido>.json` na lista de arquivos. Toda guarda pede mutante declarado e teste do ramo de falha.
- A9 (recomendado) docs/propostas/ae2-quadro-anda-com-pr.md:74 · O texto do `agents/tech-lead.md` sobre o `--cartao` obrigatório vai no P5, longe do P1 que muda o comportamento. A doc afetada vai na mesma entrega, e a recusa da ferramenta já ensina. Basta o texto do `--limpar`.
- A10 (recomendado) docs/propostas/ae2-quadro-anda-com-pr.md:31 · `--parte` usa `--de X --para X` com X tirado de `coluna_do_cartao`, que pode ser um estado do histórico sem seção. O `movimento` recusa `--para` fora das colunas (`bin/forge-check:5065`) e a nota vira pendência. Use a seção canônica.
- A11 (recomendado) docs/propostas/ae2-quadro-anda-com-pr.md:35 · Em projeto, o movimento do merge fica só como texto no `tech-lead.md`. É o esquecimento que a linha 19 aponta como causa, e o desenho aceito tinha a conferência no CI do modelo (C4). Registre a lacuna no risco.

## Sondas

## Parecer
Reprovado. Merge automático: nenhuma parte o reintroduz. O movimento só roda depois do MERGED provado (`bin/forge-fechar:1612-1623`) ou no `--limpar` com o PR MERGED lido. Nada usa `--armar` nem `gh pr merge --auto`, e P1 espera o E114.1. Os quatro bloqueantes pedem ajuste no texto do desenho, não no código:
- A1: falta a migração dos projetos para o P3, por causa do hook do quadro.
- A2: o motivo do `--limpar` sai sem `PR #N`, e a contagem perde o merge feito pelo dono.
- A3: a tabela da regra 3 de 21/11 não cumpre "uma entra, uma sai" em duas linhas.
- A4: a troca do trailer está bem fundamentada, mas mexe em D1 e D3 aceitas pelo dono. Precisa do registro como decisão do time com o "reabre quando" e da linha na lista de segunda.

O corte P1 a P6 está nos tetos de linhas, e as dependências estão certas, salvo o A7.
