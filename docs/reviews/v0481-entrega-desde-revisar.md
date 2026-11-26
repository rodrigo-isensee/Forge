---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-entrega-desde-revisar
commit: 3b5fde5f4ebfeb4a70792575d7ea6506d530134f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E16.8, code review por delta do #904, de c056f38d a 3b5fde5f, classe C)

Revalidação (H3, R-REVIEW): li só o delta de `forge-check parecer delta` (domínio código e testes): `bin/forge-check`, `changelog.d/v0481-entrega-desde-revisar.md`, `tests/mutantes/v0481-entrega-desde-revisar.json` e `tests/test_selo_e_entrega.py`, de c056f38d a 3b5fde5f (commit E16.6; os outros três commits do intervalo são só pareceres, fora do domínio). A 1.ª rodada (c056f38d) segue valendo para o resto do diff.

## O que foi conferido
- **A1 (review) e A1 (segurança) resolvidos:** `desde_do_parecer_aprovado` exige que os portões com o revisado X selado como `Revisar-sha:` sejam exatamente os portões com parecer no head (o selado sem parecer, apagado ou renomeado, cai) e roda `veredito_trocado` desde o Base-sha em todas as pastas de `PASTA_E_REGRA` com veredito esperado `aprovado`: o reprovado apagado, renomeado para `_*.md`, com `contrato: 0` ou sem brief selado segue no histórico e devolve None (Desde de sempre). A busca desde o Base-sha é mais estrita que a sugerida pela segurança (desde X), e o `veredito_trocado` falha fechado no erro do git. Segue a opção A do dono: afrouxa só o que a segurança já escreveu.
- **A guarda antiga saiu sem perder cobertura:** o "todos aprovados no head" agora é coberto pelo `veredito_trocado`, que lê também a versão do head (commit que toca a pasta em Base..head); `test_parecer_nao_aprovado_mantem_o_desde_da_conferida` segue verde e mata o ED6.
- **A2 (recomendado) resolvido:** `test_sem_conferida_pela_entrega_o_intervalo_parte_do_base_sha` afirma `intervalo: <Base-sha>..` pela `entrega --pedido`; com o ED1 aplicado à mão numa cópia, o teste falha pela asserção (a saída traz o `TypeError` de `e_ancestral` com None em vez do intervalo).
- **Sondas da rodada anterior viraram testes:** S1 do review e S2 a S4 da segurança em `CicloDo878` (`reprovado_tirado`: apagado, `_x.md`, `contrato: 0`, e o reprovado sem selo apagado), mais o portão selado sem parecer.
- **Testes:** `python3 -m unittest tests.test_selo_e_entrega.CicloDo878` no 3b5fde5f: 18 ok em 89,4 s.
- **Mutantes tocados:** `bin/forge-mutante --processos 1 --ids ED1,ED6,ED7`: ED1 (2732), ED6 (2746) e ED7 (2744) morreram; um mutante por linha de guarda mudada.
- **Documentação e commit:** texto de ajuda do `entrega`, docstring e fragmento do changelog atualizados no mesmo commit; Conventional Commits em português; delta de código pequeno (3 linhas de guarda), dentro do teto H1.
- **Corpo do PR:** `## Projeto de origem` e `## Como medir` presentes.
- **CI do #904 no 3b5fde5f** (run 45759626052, `headRefOid` conferido): as 10 partes da suíte (3.12 e 3.14), os dois tetos de pulados, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)` e `árvore já provada na develop` verdes. Vermelhos só os que esperam parecer ou rótulo: `bateria (pareceres)`, `bateria` (agregado) e `catraca` (run 45759680528, R-CONFORMIDADE: `bin/forge-check` pede o rótulo `afrouxa-regra` do dono).

- ci: 3b5fde5f4ebfeb4a70792575d7ea6506d530134f verde

## Parecer
Aprovado no 3b5fde5f. O conserto fecha o furo do parecer reprovado que saía do head (A1 do review e da segurança) pelo histórico da branch e pelo conjunto de portões selados, com teste de comportamento de cada variante e mutante por guarda; o A2 da rodada anterior também foi atendido. O merge segue dependendo do parecer de segurança no head e do rótulo `afrouxa-regra` do dono na catraca.
