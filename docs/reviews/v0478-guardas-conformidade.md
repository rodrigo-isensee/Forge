---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: 848dd5ecd7bc18a87f957a26aec0e4bd1e88f51c
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 E1.10 (revalidação da volta 2, catálogo de extratores e cache do config)

Escopo lido: só o delta de `forge-check parecer delta` (b3312958..848dd5ec): changelog.d, docs/hooks.md, hooks/agentes.py, hooks/conformidade.py, specs -3 a -9 dos mutantes, tests/test_conformidade_verde.py. Fora do domínio, nada relido.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1102 · `alvos_do_tar` lê a pasta de extração só de `-C`/`--directory`; `--one-top-level=<pasta>`, que o GNU tar usa como pasta de extração (S5), passa com rc 0 (S3, S4). Some o valor dele (relativo a cada `-C`) às pastas e ponha os dois casos no teste.
- A2 (recomendado) hooks/conformidade.py:1051 · H1: o item soma 236 linhas a mais em hooks/ desde a base 4182a6b9 (agentes.py 29, conformidade.py 207), acima do teto de 150; o PR leva `teto: excedido, <n> linhas, <motivo>`.

## Sondas
- S1 · `tar -xf docs/a.tar -C.git/forge/run` (jarvis e tech-lead, clone temporário) · espera: rc 2 · obtido: rc 2
- S2 · `tar -cf.git/forge/run/agentes.json docs` (jarvis e tech-lead) · espera: rc 2 · obtido: rc 2
- S3 · `tar -xf docs/a.tar --one-top-level=.git/forge/run` (jarvis e tech-lead) · espera: rc 2 · obtido: rc 0
- S4 · `tar -xf docs/a.tar -C docs --one-top-level=../.git/forge` (jarvis e tech-lead) · espera: rc 2 · obtido: rc 0
- S5 · GNU tar 1.35 real: `tar -cf a.tar src && tar -xf a.tar --one-top-level=dst/alvo` · espera: extrai fora de `dst/alvo` · obtido: cria `dst/alvo/src/f`
- S6 · controle, recusa: `-xvf … -C.git`, `-x -fdocs/a.tar -C.git/forge`, `-C docs -C.git/forge`, `-rf.git/…`, `--to-c '<rm>'`, `--remove-f`, `gtar … -C.git`, `unzip -qo … -d.git/forge`, `unzip -d .git/forge …`, `cpio -idD.git/forge`, `7z x -o.git/forge …` · espera: rc 2 · obtido: rc 2 (os dois papéis)
- S7 · recusa a mais, uso legítimo fora do estado (48 linhas, jarvis e tech-lead): tar `-xzf`, `xzf`, `-czf -C docs .`, `-tvf`, `--strip-components`, `--exclude=.git`, `-I zstd`, `-Izstd`, `--use-compress-program='zstd -T0'`, `-T`, `-X`, `--wildcards`, `tar -cf - … | tar -xf - -C docs/b`, `--checkpoint=100 --checkpoint-action=dot`, `-xOf`, `--to-stdout`, `-tf .git/forge/a.tar`, `-cf … -C .git/forge run`, `--format=gnu`, `bsdtar`, `busybox tar`; unzip `-l`, `-t`, `-p`, `-x '*.git*' -d docs`, `-P senha`, `unzip a.zip` na raiz, `-l .git/forge/a.zip`; cpio `-it`, `-o`, `-o -H newc -F`, `-pdm docs/b`, `-idv -D docs`; 7z `x`, `x -odocs -y`, `l`, `t`, `a -mx=9`, `x -aoa -odocs`, `7za a -tzip`, `e -odocs`, `rn`; `busybox unzip -d docs` · espera: rc 0 · obtido: rc 0 em todas; nenhuma recusa a mais.

## Revalidação dos achados anteriores
- A1 (meu, valor colado no tar): fechado; S1 e S2 recusam, `ler_opcoes` toma o resto do grupo e o teste novo cobre as duas formas e vizinhas.
- A1 da volta 2 (cache do config): fechado no código; `ler_config` zera `hook._config` antes da troca, e `test_versao_na_worktree_nao_deixa_o_config_dela_no_cache` prova teto e piso pelo `h.config()`.

## Verificação
- Testes do delta: `python3 -m unittest tests.test_conformidade_verde.EstadoDoAgentesNoClone tests.test_conformidade_verde.ConfigDaWorktreeNoClone`: 14 testes, OK.
- Mutantes: `bin/forge-mutante --cobertura --base b3312958`: toda condição mudada coberta por mutante declarado (specs -3 a -9); execução dos mutantes não rodada (máquina carregada, brief: só os testes do delta).
- Suíte inteira: não rodada (brief: sem suíte local); sem PR, CI do head não citável.

## Parecer
Reprovado: um bloqueante, A1, com defeito provado (S3 a S5). O catálogo `EXTRATORES` e o leitor à maneira do getopt fecham o valor colado e não recusam a mais em 48 usos legítimos (S7); falta a outra opção do tar que escolhe a pasta de extração. A correção é local em `alvos_do_tar`; a revalidação lê só o delta.
