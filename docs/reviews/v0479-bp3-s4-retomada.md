---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s4-retomada
commit: 687112b1ed9755fd1935f2dee26c75b5c048db2c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E39.36 (BP3 S4, `forge-check retomada`)

## Escopo lido
Diff `cf097822..687112b1` (merge-base com a `develop`): `bin/forge_retomada.py` (novo), `bin/forge-check` (uso, subcomando, despacho), `bin/forge-testes` (mapa), `docs/indice-forge.md`, `changelog.d/v0479-bp3-s4-retomada.md`, `tests/test_forge_check_retomada.py` e três arquivos de mutantes. Referência: seção 4.2 e corte S4 do desenho `docs/propostas/v0479-bp3-sessao-duravel.md` (10113b09).

## Ferramentas citadas
- Tamanho (H1): `forge-check pr v0479-bp3-s4-retomada --previo` no head, só a linha de classe C, sem aviso de teto (150 linhas de código pelo brief).
- Teste do item: `python3 -m unittest test_forge_check_retomada` (em `tests/`), 41 testes OK em 22,9 s no head. Suíte inteira: no CI do PR (`R-REVIEW`), não rerrodada.
- Guardas: 33 mutantes declarados em `tests/mutantes/v0479-bp3-s4-retomada-{1,2,3}.json`, cada um apontando um teste do ramo de falha; a mutação é do autor (V2) e não foi refeita.

## Leitura
- Faz o que a S4 pede: só leitura, sem rede, `git` com prazo de 3 s e sem `GIT_*`, saídas 0/2/4, `--contar` para o atalho, uma linha por item com brief e sha256, e a remoção sempre com o dono. A ordem da matriz (entregue, continua, sem brief, vencido, suja, relançar) está testada caso a caso.
- Entradas do registro validadas antes de virar caminho ou glob (`NOME`, `briefs_validos`, `realpath` dentro de `docs/briefs`, `O_NOFOLLOW|O_NONBLOCK`, limites de bytes); saída passa por `sem_controle`; a `descricao` nunca é impressa.
- Módulo fora do `forge-check`, como o desenho pede; testes rodam o processo de verdade com ambiente limpo e `-I`.
- Commits limpos, Conventional Commits em português.

## Achados
- A1 (recomendado) bin/forge_retomada.py:101 · a matriz 4.2 do desenho diz "selo vencido (brief mudou ou base andou)"; só o hash do brief é comparado, a base que andou não leva a `vencido`. Implementar ou corrigir a tabela do desenho na S6.
- A2 (recomendado) bin/forge_retomada.py:99 · a worktree suja só é olhada com selo válido; item `vencido` ou `sem_brief` com mudança não commitada manda reselar e relançar sem o "nunca descartar" da linha `suja`. Juntar o aviso à ação quando `suja()` for verdadeiro.
- A3 (recomendado) bin/forge_retomada.py:3 · docstring, ajuda do `--contar` e changelog dizem "sem git", mas `agentes.arquivo_de_estado` consulta o git (hooks/agentes.py:747); o prazo de 3 s cobre, o texto não. Trocar por "sem rede, até 3 s".
- A4 (recomendado) bin/forge_retomada.py:76 · `git show` roda para cada `entrega conferida` antes do `--is-ancestor`; no v0478 são 131 shas, até 262 `git` por item. Testar o ancestral primeiro e só então ler a hora.

## Parecer
Aprovado no head 687112b1. Nenhum defeito provado nem requisito faltando com gatilho; os quatro achados são recomendados (`R-REVIEW`) e viram cartão depois do merge. Segurança (classe C) e QA são portões à parte.
