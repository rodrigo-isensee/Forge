---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-s5-cabecalho
commit: e216aa71cd0e5e720ce00da880a6e4adfd8464fd
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 E25.2 (S5, #917), 1ª rodada completa

Diff lido: `3c833f3f..e216aa71` (merge-base com a `develop`), 4 arquivos: `bin/forge_autorizacao.py` (9 linhas de código, dentro do H1, um comportamento), `tests/test_autorizacao.py`, `tests/mutantes/v0481-s5-cabecalho.json` e `changelog.d/v0481-s5-cabecalho.md`.

## Verificação
- CI no `e216aa71` (run 45856837729, tentativa 2, depois da queda de infraestrutura do actionlint na 1.ª): sem linha `ci: verde`. `suíte (python 3.12, parte 4/5)` e `suíte (python 3.14, parte 4/5)` vermelhas pelo diff: anotação `tests/test_forge_mutante.py:1564 ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes`, specs `v0479-pv-a2-concessao-3.json: M18` e `v0479-pv-a2-concessao-4.json: M27` com o `de` fora da fonte (A2); `bateria` e `bateria (python 3.14)` vermelhas por consequência; `bateria (pareceres)` espera o parecer. Catraca (run 45856837897) vermelha pela guarda apagada (A1). O run do `ebc6690e` (parecer do QA) foi cancelado no checkout.
- Local, `python3 -m unittest tests.test_forge_mutante.ConferirTodas`: falha no head com as mesmas duas specs; OK na base `3c833f3f`.
- `python3 -m unittest tests.test_autorizacao`: OK.
- `bin/forge-mutante tests/mutantes/v0481-s5-cabecalho.json --processos 1`: M1 a M4 mortos (M4 por erro).
- `bin/forge-mutante --cobertura --base 3c833f3f`: L232, L235, L236 cobertas; `apagada · bin/forge_autorizacao.py:230(base) · texto.startswith('---\n')` sem mutante (A1). Sem shell tocado.

## Leitura
- Comportamento: `frente` abre só com a 1.ª linha `---`, fecha na 1.ª linha com `strip() == "---"` e, sem fecho, devolve `{}`. Os chamadores (`fora_do_revisado`, linhas 214 e 218, e a 387) só ficam mais fechados.
- O `strip` no fecho em vez da comparação exata do brief: aceito. É o fecho do `ler_frontmatter` (`bin/forge-check:265`, validador da ADR 0004); com a comparação exata, um fecho `--- ` que o `forge-check docs` aceita deixaria o `parecer:` do corpo valer, o defeito que o item tira.
- Testes: os 4 novos leem comportamento, nenhum lê a fonte; o de `ItemPresoAoCommit` passa pelo git real nos dois sentidos.
- Commit: um só, Conventional Commits em português, fragmento em `changelog.d/`.

## Achados
- A1 (bloqueante) bin/forge_autorizacao.py:232 · R-QA: a guarda apagada `texto.startswith('---\n')` (base:230) não tem mutante nem isenção na spec; a catraca reprova e o `--cobertura` confirma. Mesmo achado do A1 do QA.
- A2 (bloqueante) tests/mutantes/v0479-pv-a2-concessao-3.json:16 · M18 (`if texto.startswith(...) else ""`) e M27 de v0479-pv-a2-concessao-4.json:26 (`if ": " in linha)`) têm o `de` fora da fonte nova: ConferirTodas vermelho no CI parte 4/5 e local, verde na base. Alinhe as duas specs no mesmo commit.
- A3 (recomendado) bin/forge_autorizacao.py:232 · A abertura segue exata (`linhas[0] != "---"`) e o `ler_frontmatter` usa `strip()` no topo: `--- ` no topo dá `{}` aqui e campos lá; falha fechada, já existia na base.
- A4 (recomendado) bin/forge-fechar:1347 · O `awk` de `pedido_da_branch` fecha o cabeçalho só em `$0 == "---"`; com o fecho `--- ` que o `ler_frontmatter` aceita, lê o corpo; mesmo par de leitores do S5, fora do corte deste item.
- A5 (recomendado) tests/test_autorizacao.py:374 · `FIXA ={` perdeu o espaço antes do `{`; restaurar `FIXA = {`.

## Parecer
Reprovado. A lógica faz o que o E25.1 pede e o `strip` no fecho confere com o validador da ADR 0004, mas o diff deixa a suíte vermelha (A2: duas specs antigas apontam para o texto removido) e a catraca reprova a guarda apagada sem mutante (A1). Correção volta ao autor; o A1 e o A2 se resolvem juntos alinhando M18 e M27 (ou declarando a isenção) no mesmo commit.
