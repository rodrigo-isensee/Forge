---
tipo: review
contrato: 1
pedido: prepush-leve
branch: melhoria/prepush-tags
commit: 24e055ce0157013cee88f2873b3147eb37ab2b4e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-05
---
# Review: prepush-tags (pedido prepush-leve, parte 1)

## Achados

## Parecer
Aprovado. Diff lido: `b45e40a...24e055c` (f835f66 código, 24e055c parecer de devops).

Escopo: cobre só o subitem de tags do E2 (`tags_ja_no_remoto`). O E1 (push só de parecer sem prova) e o subitem de texto do E2 (`sem_codigo`, checagem leve) estão ausentes desta branch, como a divisão manda; ficam na `melhoria/prepush-sem-codigo`.

Teto M14: `git diff --numstat --no-renames` dá `.githooks/pre-push` 30, `tests/apoio_pre_push.py` 67 e `tests/test_pre_push_tags.py` 50, total 147, dentro de 150 sem exceção. Um comportamento só (a saída sem teste do push só de tags). Fechados os A1 e A2 da rodada 1 (review e773a16). O A3 dela (`*.md` de controle) não se aplica aqui: o caminho de texto não está nesta branch.

Segurança da rodada 1 (16f5660): o A1 (`*.md` de controle na checagem leve) é do caminho `sem_codigo`, ausente aqui, e volta a ser conferido na outra branch. O A2 (refs de acompanhamento forjáveis) era recomendado e a correção mínima sugerida entrou: o comentário do hook e `docs/hooks.md` registram que essas refs são confiança local, não prova, e que o CI do PR repete tudo. O A3 (modo do arquivo) é do caminho de texto, ausente aqui.

Lógica, lida no hook:
- A decisão vem depois do laço das refs, então a recusa de `main`, `homolog`, `develop` e de tag movida (R-VERIFY) já valeu; vem também depois de PREPUSH-JA-NO-REMOTO e PREPUSH-DELETE e antes da trava. Coberto em `test_tag_nao_abre_develop_homolog_main_nem_tag_movida`.
- Falha fechada: qualquer ref fora de `refs/tags/*` zera `so_tags`; só remoções de tag deixam `tags_enviadas` vazio e caem no caminho de antes; remoto vazio, começado por `-` ou fora de `[A-Za-z0-9._-]` (URL, caminho) recusa; o `--remotes=<nome>` sem caractere de glob vira `refs/remotes/<nome>/*`, sem casar prefixo de outro remoto; objeto que não chega a commit (`^{commit}`) recusa; o modo `--suite` não entra. Cobertos: commit novo, commit só em outro remoto, tag com branch e remoto por URL.
- Tag anotada é descascada até o commit (coberto, `v2`). `local` declarado à parte, então o `|| return 1` vê o código do `git` (classe AR-6 não se aplica); o `cd` ao topo e o `unset GIT_DIR` vêm antes (classe AR-7 não se aplica).
- Testes de texto: `só leva tags`, `esperando a vez` e `a vez não chegou` existem no hook (item 11 do checklist). O ambiente do teste tira `GIT_*` e `FORGE_SUITE_*` e fixa `FORGE_TRAVA_ESPERA` (classe AR-4 conferida).

Observação sem achado: `tests/apoio_pre_push.py` já traz `ARQUIVOS` e a menção ao PREPUSH-SEM-CODIGO, que só a parte 2 usa; é o apoio partilhado dos dois PRs empilhados e não muda o comportamento aqui.

Ferramentas: `shellcheck .githooks/pre-push` sem achados; `python3 -I -m unittest discover -s tests -p test_pre_push_tags.py` deu 3 OK; `-p test_pre_push_parecer.py` deu 20 OK (vizinho do mesmo hook). `bin/forge-testes --listar` dá suíte completa (`.githooks/pre-push` sem mapa), que é do QA e do CI do PR; não rodei. Parecer de devops em `docs/devops/prepush-tags.md` (aprovado, sobre f835f66), citado e não refeito. A mutação no diff é verificador do autor; não há spec em `tests/mutantes/` neste diff, pendência para o QA conferir.
