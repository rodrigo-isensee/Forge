---
tipo: review
contrato: 1
pedido: pr-verde-lote-check
branch: melhoria/pr-verde-lote-check
commit: 26d2260eecbc01712927cfdaa67003df6b0ec107
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: pr-verde-lote-check (PR-VERDE-LOTE-CHECK-REV E1.1)

Intervalo revisado: `1f7bd7f...26d2260`. São cinco commits, um por item, todos em Conventional Commits: E1 `8b7579e`, E2 `6f0f709`, E3 `79f1e1c`, E4 `b01179b` e docs `26d2260`.

## Achados
- A1 (bloqueante) bin/forge-check:4377 · defeito provado (G1 b): CAMINHO_NO_PQ corta o caminho no glob, e o PQ `ls tests/test_*.py` reprova com `pq: PQ-1 cita "tests/test_", que não existe` (sonda); é reprovação sem mérito numa guarda nova; pular o token com `*?[{`, com teste do glob e mutante
- A2 (recomendado) tests/test_forge.py:4519 · depois da inversão, falta afirmar que, na etapa pr, o commit do autor feito depois do merge que mexe em src/y.txt volta ao escopo (hoje só a etapa merge-integracao afirma isso)
- A3 (recomendado) bin/forge-check:1044 · no escopo pelo primeiro pai, as contagens +/- continuam sendo as do intervalo inteiro: um arquivo do autor que a base também mudou aparece com os números somados; é só informativo, mas pode confundir o conferente

## Parecer
**Reprovado.** Há um bloqueante deste review (A1) e dois do parecer de segurança (`docs/security/pr-verde-lote-check.md`), que cito sem refazer:
- A1 da segurança: o merge `-s ours` some do escopo do G2.
- A2 da segurança: o D4 casa o fragmento por prefixo.

O A2 da segurança também fere o requisito da decisão D4, que pede "só o fragmento". A correção que ela sugere (igualdade para a entrada sem `/` no fim) resolve esse ponto também para o review. Todos os bloqueantes estão nesta passada.

**A1 (G1 b).** A sonda `$TMPDIR/tech-lead-pr-verde-lote-check/sonda_pq.py` chama `caminhos_ausentes_do_pq` sobre o head.
- Reprova: `ls tests/test_*.py`, que vira o caminho `tests/test_`.
- Não reprovam: `python3 -m unittest tests.test_forge`, `git show HEAD:bin/forge-check`, `docs/reviews/{a,b}.md`, `bin/forge-check:702` e `tests/mutantes/`.

Nenhum dos 682 briefs de `~/.forge-contrib/docs/briefs/` tem hoje um PQ com glob. Mesmo assim, a reprovação sem mérito está provada, e numa guarda nova cujo propósito é justamente cortar reprovações sem mérito. Sugestão: um lookahead negativo `(?![*?\[{])` no fim do segmento (ou descartar o token que tenha esses caracteres), com um teste do glob e o mutante dele.

**Por item.**
- **G1 (a), corte da etapa do `Cobre:`.** Está correto. Só dispara com `Cobre:` no cabeçalho, na mesma etapa e no papel do destino. Nos briefs antigos que o conferente reprovou por leitura (RET-LOTE-FORGE-CHECK-tech-lead-1 e ESTUDO-RELEASE-aq-4), a checagem que já existia continua pegando o caso. Teste e mutante M1 ok.
- **G1 (b).** Ver o A1. Fora o glob, varri os 200 briefs mais recentes a partir da raiz do Forge e não apareceu nenhuma linha `pq:` nova.
- **G1 (c), decisões do pedido de origem.** É o comportamento pedido: está no E1 do pedido e no G1 do estudo, e o conferente já reprovava esse caso por leitura (por exemplo, LOTE-FECHAR2-PR-tech-lead-1 em 2026-10-27 09:31, "decisões B só no pedido de origem procede").
  - O número real é maior que 4: com o binário novo, 47 briefs `-PR`/`-REV` que passavam no anterior passam a reprovar (10 `-PR` e 37 `-REV`). Todos reprovam só por `decisões: falta` de linhas de `docs/pedidos/<X>.md`.
  - Brief novo não é afetado: o `brief gerar` copia `fontes[1:]` do `decisoes_cobradas`, que agora inclui a origem (`bin/forge-check:1409-1415`).
  - Um pedido `-PR` sem origem (METADE-K6-PR) sai só com o aviso informativo.
- **G2.**
  - O escopo pelo primeiro pai está correto no merge limpo, com commits de parecer antes ou depois.
  - Falha fechada no merge de outra branch, no octopus e no commit raiz.
  - O `pedido_do_pr` só troca o argumento quando há um único slug, e o `uso_do_pr` roda de novo sobre o resultado.
  - O `Base-sha` do `brief gerar` já era o merge-base (E11, `bin/forge-check:4637`); nada a mudar ali.
  - O merge que descarta a base é o A1 da segurança.
- **G6.** O `reescrito_por_portao` só roda depois de `autoria_do_parecer`, casa pelo `commit:` e pelo papel do `Agente destino:`, e muda só uma linha informativa. A união com um brief do `-REV` continua exigindo a mesma Branch, Base e Base-sha. Os testes cobrem o caso de outro papel e o de outro commit.
- **D4.** O fragmento entra pelo `livres` do `commit_vale`, e só no `cmd_pr`. O problema do prefixo é o A2 da segurança.

**As 4 asserções invertidas** (`tests/test_conferencia_base_dono.py:125` e `:151`, `tests/test_forge.py:4519`, `tests/test_volta_por_delta.py:287`) seguem o G2 pedido: o que o merge limpo da base trouxe sai do escopo em toda etapa.
- A de `test_volta_por_delta` documentava justamente o falso positivo que o G2 corta.
- A de `:151` troca "sem a linha de integração" por "sem `e.txt`", que é o que importa, e mantém `s.txt` (o conteúdo do autor no primeiro merge).
- A lacuna que sobra é o A2.

**As 5 fixtures** (`tests/fixtures/brief/*.md`) só trocam, no PQ-2, o `docs/a.md` (que não existe) por `docs/pedidos/pedido-sintetico.md`, para não caírem no G1 (b). A mudança é mínima, e o que cada fixture testa (corte, etapa, PQ sem espera) continua igual.

**Ferramentas e checklist.**
- Testes do item: `python3 -m unittest tests.test_etapa_do_brief tests.test_conferencia_base_dono tests.test_portao_diff_proprio tests.test_volta_por_delta tests.test_forge.PrAposMergeDaBase tests.test_forge.EntregasParalelas` deu `Ran 176 tests ... OK`. A suíte completa fica com o pre-push e o CI.
- Mutantes M1 a M8 em `tests/mutantes/pr-verde-lote-check.json`: o autor registrou todos mortos, e não os refiz.
- Teto M14: 280 linhas (`bin/forge-check` 149 e `tests/*.py` 131), abaixo de 400. O PR não toca `hooks/` nem `tests/catraca.py`.
- `bin/forge-check` é controle do Forge, então o PR vai pedir o rótulo do dono.
- O fragmento `changelog.d/pr-verde-lote-check.md` está presente.
- `R-NEUTRO` e `R-CUSTO`: sem achado.
- PA-7 (`docs/engineering/achados-recorrentes.md`): a lista está vazia, então não há item a conferir.
- É a primeira revisão, sem delta.
