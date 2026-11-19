---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: bdbdc257dd492ee2ec6f79af7614b3a5d82e57e2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 E1.14 (revalidação da volta 3, catálogo DESTINOS)

Escopo lido: só o delta de `forge-check parecer delta` (848dd5ec..bdbdc257, mais o parecer de segurança 6a3e3983, fora do domínio): changelog.d, docs/hooks.md, hooks/conformidade.py, specs -6 a -10 dos mutantes, tests/test_conformidade_verde.py. Fora do domínio, nada relido.

## Achados
- A1 (recomendado) tests/test_conformidade_verde.py:463 · o pulo sem GNU tar também pula no CI; siga o `tests/apoio_sandbox.py` (com `CI`/`GITHUB_ACTIONS` definido, reprova) para o pulo nunca contar no `teto_pulados`. O +1 estático da catraca (36→37) vai no texto do PR, coberto pelo `afrouxa-regra` que o hook já pede.
- A2 (recomendado) hooks/conformidade.py:1096 · H1: o item soma 298 linhas a mais em hooks/ desde a base 4182a6b9 (agentes.py 29, conformidade.py 269), acima do teto de 150; o PR leva `teto: excedido, <n> linhas, <motivo>`.

## Sondas
- S3 · `tar -xf docs/a.tar --one-top-level=.git/forge/run` (jarvis e tech-lead, clone temporário) · espera: rc 2 · obtido: rc 2
- S4 · `tar -xf docs/a.tar -C docs --one-top-level=../.git/forge` (jarvis e tech-lead) · espera: rc 2 · obtido: rc 2
- S5 · GNU tar 1.35 real: `tar -cf a.tar src && tar -xf a.tar --one-top-level=dst/alvo` · espera: extrai em `dst/alvo` · obtido: `dst/alvo/src/f` (a opção é pasta de extração; o hook a lê como tal)
- S8 · vizinhas: `--one-top=`, `gtar`, `--transform` com `flags=r;` e com `\/`, `7z x -O.git/forge` (dois papéis) · espera: rc 2 · obtido: rc 2; `--one-top-level .git/forge/run` sem `=` dá rc 0, correto: no GNU a palavra é operando
- S9 · 33 usos legítimos fora do estado (tar `--transform`/`--xform`, `-N`, `-T`, `--one-top-level` em `docs`; bsdtar `-s`; 7z `-o`, `-xr!`, `-ir!`, `-scs`; unzip, cpio, busybox, toybox), dois papéis · espera: rc 0 · obtido: rc 0 em todos

## Revalidação dos achados anteriores
- A1 (`--one-top-level`): fechado; S3 e S4 recusam, a opção entra em `subpasta` relativa a cada `-C`, e o teste do catálogo confere a ajuda do `tar --help` nos dois sentidos.
- A2 (H1): segue recomendado, agora com 298 linhas.

## Verificação
- Testes do delta: `python3 -m unittest tests.test_conformidade_verde.CatalogoDosDestinos` e os dois testes novos de `EstadoDoAgentesNoClone`: 5 testes, OK (GNU tar 1.35, sem pulo).
- Mutantes: `bin/forge-mutante --cobertura --base 848dd5ec`: toda condição mudada coberta por mutante declarado (specs -6 a -10), rc 0; execução não rodada (brief: sem suíte local).
- Catraca local (`tests/catraca.py --modo regras`, eventos vazios): rc 1 com duas linhas, o pulo 36→37 e a mudança em hooks/conformidade.py; as duas pedem o rótulo `afrouxa-regra` do dono depois do último push, que este PR já precisaria pela segunda. O pulo é aceitável com A1 (no CI não pula) e declarado no PR.
- Suíte inteira: não rodada (brief); sem PR, CI do head não citável.

## Parecer
Aprovado. O catálogo `DESTINOS` fecha o A1 (S3 a S5) sem recusa a mais em 33 usos legítimos (S9); os dois recomendados não bloqueiam.
