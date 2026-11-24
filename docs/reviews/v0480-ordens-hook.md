---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: a9187ffe255cf7ba75af7490340d882cc651079b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E140.13, revalidação do #805 depois do merge da develop, e o sentido do item depois do #811)

Revalidação por delta (H3, `R-REVIEW`). Rodei `forge-check parecer delta docs/reviews/v0480-ordens-hook.md` no intervalo `a6e0d101..a9187ffe`, sem o que veio da base. O parecer anterior foi aprovado em `a6e0d101` (`3cec56ec`). O único commit de código do intervalo é o merge `a9187ffe` da develop `6161978d`. O conflito foi só em `docs/hooks-fixtures.md`, que é gerado.

## Delta lido
- **`docs/hooks-fixtures.md`**: o total passa de 3500 (develop) para 3515, porque entram as 11 fixtures do `ordens` e as 4 do `vigia/time-parado-*`. As linhas `conformidade` e `trava-*` são as da develop (E141, `CONFORMIDADE-REPO-CREATE-PUBLICO`). Rodei `python3 -I scripts/indice-fixtures.py --conferir` e a saída foi `docs/hooks-fixtures.md: em dia`. A regeneração bate com o corpus.
- **`tests/test_hooks.py`**: o trecho que o delta lista (`test_fixtures_do_repo_publico`) veio da develop (E141.2, E141.7). Não tem mudança do item.
- **Escopo contra a develop**: em `git diff 6161978d a9187ffe -- hooks/`, só aparecem `hooks/ordens.py` (107+) e `hooks/hooks.json` (32+/1-). São 140 linhas, dentro do teto H1, e o recorte é o mesmo já aprovado. A mensagem do merge diz o mesmo ("hooks/ordens.py e hooks/hooks.json sem mudança").

## O hook das ordens depois do #811 (ordem do dono)
Os dois não são redundantes. São as duas metades de um mesmo mecanismo:
- **O #811 (`0e59c446`, na develop) só guarda a escrita.** O `conformidade` deixa só o `jarvis` gravar `.forge/ordens/`, inclusive pela cópia principal a partir da worktree, e `~/.forge-contrib/docs/ordens/`. Ele não lê o arquivo nem o põe no contexto. Na develop, nenhum hook lê essas pastas: o `SessionStart` tem `_maquina`, `vigia`, `doutor` e `ambiente`, e não existe `UserPromptSubmit`.
- **O #805 entrega o conteúdo.** O `hooks/ordens.py` lê o arquivo, que só o Jarvis grava (essa garantia vem do #811), e o reinjeta no `SessionStart` (`startup|resume|compact`) e a cada mensagem do dono, com teto de 15 linhas e 2000 caracteres e sem nunca bloquear. É isso que resolve o problema da emenda da ADR 0003: as ordens se perdem depois da compactação.
- **Se o #805 for fechado**, o problema de origem continua sem solução (ordem do dono de 22/11 05:30). A guarda do #811 passa a proteger uma pasta que ninguém lê. O `motivo` em `hooks/conformidade.json:66-67` cita o "hook ordens", que não existiria. A emenda da ADR 0003 na develop ficaria parada em "vigente a partir do PR que traz o hook" e com os caminhos antigos (`.forge/ordens-em-vigor.md`, `docs/kanban/`), que não batem com a guarda. Essa emenda só é corrigida nesta branch. Para fechar de forma limpa, seria preciso também reverter o #811 e a emenda.
- **O que se ganharia fechando:** nenhum hook em `UserPromptSubmit` e nenhum afrouxamento do item 1 da ADR 0003. Também sairiam até 2000 caracteres de contexto por mensagem e um processo `python3` por mensagem. Pela emenda, o custo de tempo é medido pelo `devops-engineer`, com reversão acima de 100 ms no p95.
- **Recomendação:** manter e mesclar o #805, que já tem o rótulo autorizado pelo dono (decisão 2a de 23/11 15:25), com os três portões no head. A reversão já está escrita na emenda: texto que não veio do dono chega ao arquivo, o hook passa de 100 ms no p95, ou o dono registra em 2 versões seguidas que as ordens não evitaram a perda.

## Provas
- `python3 -I scripts/indice-fixtures.py --conferir`: `docs/hooks-fixtures.md: em dia`.
- Rodei com `env -i` os módulos `tests.test_indice_fixtures`, `tests.test_hooks.OrdensEmVigor`, `tests.test_hooks.GuardaDasOrdens` e `tests.test_hooks.Hooks.test_hooks_json`, e todos passaram. `test_fixtures_do_repo_publico` falha local em 3 fixtures `*-libera` com `R-CONTRIB`: esse teste vem da develop e não do item, e a falha é do ambiente desta cópia (a sessão vista como de projeto sobre o Forge). Não é defeito.
- CI do PR #805 no head `a9187ffe`: suíte 3.12 e 3.14 (10/10), `catraca`, `instalação`, `passos`, `verificações longas` e `teto de pulados` verdes. `bateria (pareceres)` e o agregado `bateria` estão vermelhos porque os pareceres ainda não estão no head. O merge espera tudo verde.

## Achados
- A1 (recomendado) hooks/ordens.py:21 · No Forge o hook lê `~/.forge-contrib/docs/ordens/ordens-em-vigor.md`, que não existe. O arquivo de hoje está em `docs/kanban/ordens-em-vigor.md`. Depois do merge, o Jarvis precisa movê-lo para `docs/ordens/`, senão o hook fica em silêncio.

## Parecer
Aprovado. O merge da develop só regenerou o índice das fixtures e trouxe testes da base, e o código do item é o mesmo já aprovado. Pela ordem do dono, recomendo manter o item: sem ele, o #811 guarda um arquivo que ninguém lê.
