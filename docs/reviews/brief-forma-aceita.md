---
tipo: review
contrato: 1
pedido: versao-035
branch: melhoria/brief-forma-aceita
commit: 7374443691d336ce869d2d1d0db1003f12dc82b2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-06
---
# Review: versao-035, E7 BRIEF-FORMA-ACEITA

Etapa E2.4 (outra instância; não implementei o E7). Esta é a revalidação de 4f2ef7e. O parecer anterior, sobre 93225df, reprovou por A1. Lidos: a seção `## E7.` do desenho (`docs/arquitetura/versao-035-desenho.md`) e a linha do Histórico de 15:32 do pedido.

## Revalidação por delta (93225df..4f2ef7e)
`forge-check delta --parecer docs/reviews/brief-forma-aceita.md` (rc 0) listou `bin/forge-check` 4553-4554, 5968-5969; `bin/forge-testes` 71, 104; `changelog.d/brief-forma-aceita.md` 2; `tests/test_brief_forma_aceita.py` 10, 33, 37, 40-61; `tests/test_testes_tocados.py` 61. Li só esses trechos e os pontos de uso de `CABECALHO_BRIEF` que o A1 alcança (`cabecalho_do_brief`, `blocos_literais`, `delta_de_brief`, `conferir_brief`, `destino_da_mensagem`). O resto do diff da base ficou como "já lido" no parecer de 93225df: a constante `FORMAS_DE_COMMIT`, os testes (c) do hook e o primeiro fragmento.

Commits novos: 524c154 (A1), a266d90 (A2), b59fa02 (A4), 7d618dc (move o parecer para `docs/reviews/`, ADR 0004), 17148b5 (fragmento) e 4f2ef7e (mapa do `forge-testes`). Os seis seguem Conventional Commits, em português, um assunto cada.

## Achados anteriores
- A1, fechado em 524c154. O ajuste está em `bin/forge-check:4553-4554`: `SECAO_DAS_FORMAS` entra no `CABECALHO_BRIEF`, então a seção abre um bloco próprio que nenhuma checagem lê. O `com_commit` de `conferir_brief` lê só `Entregar` e `Pronto quando`. O teste está em `tests/test_brief_forma_aceita.py:48-61`: gera o brief, preenche e confere `forma: ok`. Para provar que o teste pega o defeito, tirei a seção do regex numa cópia: esse teste reprova. Os outros usos do regex não mudam para briefs gerados, porque a seção vem depois de todas as de `SECOES_BRIEF`. `delta_de_brief` percorre só `SECOES_BRIEF`.
- A2, fechado em a266d90. A linha do merge saiu de `bin/forge-check:5968-5969`, e o merge vem só do `pq_de_merge`. O teste está em `tests/test_brief_forma_aceita.py:40-46` e conta 1 ocorrência na etapa `merge-integracao`. Recoloquei a linha numa cópia: esse teste e o `:27` reprovam. O fragmento (17148b5, `changelog.d/brief-forma-aceita.md:2`) acompanha a mudança.
- A3, aberto (recomendado; não devolve). `FORMAS_DE_COMMIT` (`bin/forge-check:4568`) segue sem o merge. Com o A2, o merge deixou de fazer parte da oferta e fica de vez com o `pq_de_merge`. Hoje a fonte única das formas de commit é essa constante, e a do merge é o `pq_de_merge`. A recomendação perdeu quase todo o peso.
- A4, fechado em b59fa02 (`tests/test_brief_forma_aceita.py:37`, `assertEqual(rc, 0, saida)` no teste do review).

## Commits novos fora dos achados
- 4f2ef7e: `test_brief_forma_aceita` entra em `FORGE_CHECK` (`bin/forge-testes:71`) e na regra de `hooks/.*` (`:104`). Está correto, porque o teste (c) carrega o hook `conformidade`, e uma mudança no hook tem de rodar a oferta. A contagem de `tests/test_testes_tocados.py:61` passa de 39 para 40. O comentário da linha ainda fala só do L08 (A6).
- 7d618dc: é só um rename. O parecer passa a ficar onde o `forge-check docs` e o `forge-check pr` o leem.

## Teto (M14) e forma
Contado com `git diff --numstat --no-renames d9b26bb...HEAD` (código e teste): `bin/forge-check` 9+1, `bin/forge-testes` 2+2, `tests/test_brief_forma_aceita.py` 91, `tests/test_testes_tocados.py` 1+1. O total é 107, abaixo de 150. A branch tem um comportamento só, não toca `hooks/` nem caminho de `PROTEGIDOS`, e o teto do desenho (30 no script) foi respeitado. Não há gatilho de segurança (desenho, E7), então não há parecer do `security-engineer` a citar. `R-NEUTRO` e `R-CUSTO` não são afetados.

## Testes rodados (só os tocados, D-5)
`python3 -m unittest test_brief_forma_aceita test_testes_tocados` (de `tests/`): 92 testes, OK, em 31 s. Também rodei, em cópias da árvore (`git archive`), um mutante para A1 e outro para A2. Cada um reprova o teste correspondente.

## Revalidação 2026-11-06
Revalida o parecer de 4f2ef7e em 7374443, depois das junções da develop 4b44286 (30b4453, L09) e 7374443 (3011d84, L10, BRIEF-HEAD-LOCAL e estoques A, B e C da 0.34). Decisão 27 de `decisoes-estudos`: revalidação por outra instância, com brief e conferente iguais.

Delta conferido:
- `forge-check delta --parecer docs/reviews/brief-forma-aceita.md` (rc 0) listou o intervalo 4f2ef7e..7374443 com 239 arquivos. Quase tudo é a develop que entrou, já revisada nos PRs #450 a #456. Não reli esse conteúdo e o deixei como "já lido".
- O patch do E7 foi comparado antes e depois das junções: `git diff d9b26bb 4f2ef7e` contra `git diff 3011d84 7374443`, em `bin hooks tests agents skills changelog.d`. A diferença está só em duas linhas. Uma é o contexto da tupla `FORGE_CHECK` (`bin/forge-testes:72`), que ganhou o `test_qa_doutor_034` da develop, e o E7 continua acrescentando só `test_brief_forma_aceita`. A outra é a contagem de `tests/test_testes_tocados.py:61`, que passou de 40 para 43: E7 + L09 + L10 + doutor-034. `bin/forge-check` (9+1), `tests/test_brief_forma_aceita.py` (91) e `changelog.d/brief-forma-aceita.md` (2) estão iguais byte a byte.
- `git show --cc --name-only` das duas junções lista `bin/forge-check`, `bin/forge-testes` e `tests/test_testes_tocados.py`. Em `bin/forge-check` a junção foi automática, porque os dois lados mexeram no arquivo, e o `--cc` não mostra nenhum trecho combinado. A comparação dos patches acima confirma que o E7 não mudou ali. O `--cc` mostra as resoluções das contagens em `tests/test_testes_tocados.py:61`, nas duas junções, e da tupla em `bin/forge-testes:72`, só em 7374443. As duas estão corretas.
- Interação de comportamento: li os trechos da develop em `bin/forge-check` que usam os mesmos símbolos do E7: `etapas_novas_da_volta`, `fora_do_escopo_da_volta`, `conferir_volta` (E14, :1844-1881 e :2042-2046) e `so_pareceres_a_frente` (:4964-4991). O E14 lê `blocos_literais` só no `Fora do escopo`, `Entregar` e `Decisões e restrições`. A seção das formas (`SECAO_DAS_FORMAS`, :4596-4597) vem depois do `Pronto quando` e não entra nesses blocos. Nenhum `SECOES_BRIEF` nem `FORMAS_DE_COMMIT` mudou na develop.
- Os achados em aberto mudaram de linha: A3 vai para :4611 e A5 para :4597. O A6 fechou na junção 4b44286, porque o comentário da contagem agora cita o E7.
- Teto (M14): o patch do E7 continua com 107 linhas e um comportamento só.
- Testes tocados (D-5), na worktree: `python3 -m unittest test_brief_forma_aceita test_testes_tocados` deu 100 testes OK em 29,8 s. A suíte inteira não foi rodada de novo: o push de 7374443 passou com 2730 testes OK (2026-11-06 12:03, `/tmp/push-e7-3.log`), log do QA (R-QA).

Veredito: as junções só mudaram as contagens de módulos, que estão corretas. O parecer continua **aprovado** em 7374443.

## Achados
- A3 (recomendado) bin/forge-check:4611 · FORMAS_DE_COMMIT segue sem o merge; com o A2 o merge é só do pq_de_merge, então a fonte única virou duas, por desenho
- A5 (recomendado) bin/forge-check:4597 · brief à mão com o cabeçalho das formas logo após Entregar tira o trecho da cobrança de PQ do conferente (provado com conferir_brief); só abrir essa seção depois do Pronto quando
- A6 (recomendado) tests/test_testes_tocados.py:61 · o comentário da contagem 40 ainda cita só o L08; citar o E7 (fechado na junção 4b44286: o comentário cita o E7)

## Parecer
Aprovado. A1, o único bloqueante, fechou com teste que reprova sem a correção (mutante conferido). A2 e A4 também fecharam. A3, A5 e A6 são recomendações e não devolvem. A5 não passa de recomendado: é um desvio estreito do "nenhuma recusa muda" do desenho, só para brief escrito à mão, e a mesma cobrança já se contorna sem a seção, trocando a palavra.
