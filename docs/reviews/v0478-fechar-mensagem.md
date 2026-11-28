---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-fechar-mensagem
commit: 8989baa06876e4ad25235c846aaf4926f686a1d1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E4.2, FECHAR-PROMOVER-MENSAGEM-PT)

## Escopo lido
Diff `4182a6b9..3b1e324b`: `bin/forge-fechar` (o `mesclar_auto` repassa `"${@:3}"`; o P6 passa `--subject 'chore(promoção): <versão> para a homolog (#<n>)'` e `--body` em português; texto do `--seco` atualizado), `tests/test_fechar_lote.py`, `tests/mutantes/v0478-fechar-mensagem.json`, `changelog.d/v0478-fechar-mensagem.md`. Cerca de 6 linhas de código (H1 dentro do teto), um comportamento só.

## Conferência
- Faz o que o item pede, nem mais: o passo 6 (`--squash`) segue sem título extra, porque `"${@:3}"` vazio não expande nada sob `set -u`.
- As variáveis do título e do corpo estão definidas no P6: `versao` tem guarda no P1 (`die` se vazia), `pr_n` sai do PR reusado ou do criado (com `die` se o número não for lido), e o ramo MERGED não chega ao P6; `pedido` já entra no corpo do PR no P5.
- Título e corpo são um argumento cada; sem comando montado em texto (`R-SEGURANCA` fica com o parecer da segurança).
- O comentário "o único `gh pr merge` do script" segue verdadeiro.
- O teste novo cobre os dois caminhos do P6 (PR criado com o número 42 e PR aberto reusado com o 9), com o número no título; o teste antigo do P6 foi atualizado para a nova linha.
- Mutantes declarados, um por linha mudada (M1 no P6, M2 no repasse do `mesclar_auto`).
- Commit em Conventional Commits, em português; fragmento do changelog no lugar certo.

## Ferramentas (citadas, sem refazer)
- `bin/forge-mutante tests/mutantes/v0478-fechar-mensagem.json` no 3b1e324b: `M1 · morreu · bin/forge-fechar:1118`, `M2 · morreu · bin/forge-fechar:783`.
- Teste do item, `python3 -m unittest tests.test_fechar_lote.Promover`: `Ran 24 tests`, `OK`.
- Suíte completa e shellcheck ficam no CI do PR (o shellcheck não está instalado neste ambiente).

## Revalidação (8989baa0)
- Delta lido: `forge-check parecer delta docs/reviews/v0478-fechar-mensagem.md`, intervalo `3b1e324b..8989baa0`, sem o que veio da develop; no domínio só `tests/mutantes/v047-integracao-em-lote-8.json` (IL-M63: `de`/`para` com o `--subject` novo).
- A linha `de` bate com `bin/forge-fechar:1118`; `bin/forge-mutante --processos 1 tests/mutantes/v047-integracao-em-lote-8.json`: `IL-M63 · morreu · bin/forge-fechar:1118` (IL-M57 a IL-M64 morrem).

## Parecer
Aprovado. A mudança é pequena, presa ao P6 do `--promover`, com teste de comportamento dos dois caminhos e mutantes que morrem.
