---
tipo: qa
contrato: 1
pedido: v047-contrib-heredoc-fp
branch: melhoria/v047-contrib-heredoc-fp
commit: f7e12a87a474a2e61ea2a0e621e9847c988d9ca0
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
---
# QA: v047-contrib-heredoc-fp

Item E2.106 (cartões HOOK-CONTRIB-HEREDOC-FP e HOOK-REVIEW-HEREDOC-TIMEOUT): o corpo de heredoc que só `python3 -`, `timeout N python3`, `sh`, `bash -e` lê deixa de contar como comando de PR (afrouxa a rede D da ADR 0011, `R-REVIEW`). Sem especificação de UX nem contrato de API: as obrigações são as da emenda da ADR 0011 e as fixtures `heredoc-interpretador-*`.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Libera: docstring ou texto que cita `gh pr merge` em corpo de Python/sh só lido | `test_corpus_heredoc_interpretador_libera_e_bloqueia` (fixtures `*-cita-pr-libera`, `*-grava-saida-libera`, `*-dois-sh-sem-pr-no-segundo-libera`, `timeout-python-...-libera`) | constante solta (docstring) fora; `timeout` na frente | passou |
| Bloqueia: Python que lança processo com PR ou pull (`subprocess`, `os.system`, `asyncio`, `posix_spawnp`, `getattr`, concatenação, lista em várias linhas) | mesmo teste, fixtures `python-*-bloqueia` | nome montado; texto em várias linhas; corpo ilegível ao `ast` | passou |
| Bloqueia: chamada com caminho, atribuição (`PATH=`, `env -S`), `git` na chamada, pipe para sh, dono misto, lançador demais, ruby, zsh | fixtures `*-com-caminho`, `*-com-atribuicao`, `env-*`, `path-solto`, `em-pipe`, `dono-misto`, `lancador-demais`, `ruby`, `zsh` (`-bloqueia`) | programa que lê o corpo trocado | passou |
| Bloqueia: sh que executa PR (`eval`, número de PR, heredoc interno, `bash` com merge) | fixtures `sh-*-bloqueia`, `bash-merge-executado-bloqueia` | corpo que o shell roda | passou |
| Índice de fixtures coerente | `tests.test_indice_fixtures` | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_hooks_parecer_pasta tests.test_indice_fixtures`: 11 testes, OK (56 s).
- Vermelho antes do verde: `forge-testes --vermelho f4b0c2ae` (base=f4b0c2aeb42b head=f7e12a87a474): reverte `hooks/parecer.py`, ADR, docs e changelog à base e mantém testes e fixtures no HEAD; restrito a `--modulos test_hooks_parecer_pasta,test_indice_fixtures` (a suíte inteira estoura o prazo local): rc=0, 4 provam (`test_corpus_heredoc_interpretador_libera_e_bloqueia` e 3 de `test_indice_fixtures` caem na base por asserção), 7 passam na base (já existiam, não provam).
- Mutação: `forge-mutante` das 4 specs (`v047-contrib-heredoc-fp{,-2,-3,-4}.json`, `--processos 3`, rev=f7e12a87a474): M1 a M26 (M5 não existe, só salto de numeração) todos `morreu`, rc=0, nenhum sobrevivente.
- Cobertura: `forge-mutante --cobertura --base f4b0c2ae`: toda condição mudada de `hooks/parecer.py` (linhas 176 a 1038) tem mutante declarado; nenhuma sem mutante.
- Diff conferido: só `hooks/parecer.py`, fixtures, teste do corpus, mutantes, ADR, docs e changelog. Achados recorrentes (AR-1 lista de mutantes incompleta, AR-2 ramo de falha sem teste) conferidos: lista completa contra o diff e o ramo de falha do `ast` tem a fixture `ilegivel-bloqueia`.
- Suíte inteira: roda no CI do PR (check-run `bateria` do mesmo sha); não rerrodada aqui.
