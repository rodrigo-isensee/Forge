---
tipo: review
contrato: 1
pedido: versao-035
branch: melhoria/brief-forma-aceita
commit: 4f2ef7ed87f238ba07b694c8d6ef1ce8f8b92219
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-05
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

## Achados
- A3 (recomendado) bin/forge-check:4568 · FORMAS_DE_COMMIT segue sem o merge; com o A2 o merge é só do pq_de_merge, então a fonte única virou duas, por desenho
- A5 (recomendado) bin/forge-check:4554 · brief à mão com o cabeçalho das formas logo após Entregar tira o trecho da cobrança de PQ do conferente (provado com conferir_brief); só abrir essa seção depois do Pronto quando
- A6 (recomendado) tests/test_testes_tocados.py:61 · o comentário da contagem 40 ainda cita só o L08; citar o E7

## Parecer
Aprovado. A1, o único bloqueante, fechou com teste que reprova sem a correção (mutante conferido). A2 e A4 também fecharam. A3, A5 e A6 são recomendações e não devolvem. A5 não passa de recomendado: é um desvio estreito do "nenhuma recusa muda" do desenho, só para brief escrito à mão, e a mesma cobrança já se contorna sem a seção, trocando a palavra.
