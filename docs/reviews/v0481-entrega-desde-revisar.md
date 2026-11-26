---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-entrega-desde-revisar
commit: c056f38d285c454744e3a343b705621d2cacda49
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E16.3, code review do #904, 1ª rodada completa, de 34ab6714 a c056f38d, classe C)

Escopo: o diff inteiro da branch contra o merge-base com a develop (34ab6714), 1 commit (c056f38d, E16.1): `desde_do_parecer_aprovado` em `bin/forge-check` (32 linhas de código, dentro do teto H1, um comportamento), a chamada em `cmd_entrega_conferir`, o texto de ajuda, o fragmento `changelog.d/v0481-entrega-desde-revisar.md`, a classe `CicloDo878` (12 testes), as specs ED1 a ED12 e o peso em `tests/pesos-d4.json`.

## O que foi conferido
- **O desenho segue a opção A do dono (25/11 21:15):** o Desde passa ao `commit:` X comum dos pareceres aprovados no head só com conferida anterior, o review entre eles, todos `aprovado`, X `Revisar-sha:` de brief selado de cada portão, X adiante da conferida, ancestral do head e fora da base, e depois de X só pareceres, quadro, anexo do portão, o fragmento e merge limpo da base. Faltando uma condição, None e o `or valido` mantém o Desde de sempre. O trecho que sai da conferência é conferida..X; de X ao head tudo segue conferido.
- **Falha o requisito "todos os pareceres aprovados" (A1):** a conta lê só os pareceres presentes no head. O parecer reprovado de um portão sobre X, apagado depois (S2), some da conta e o Desde anda para X: a conferência passa e o arquivo fora do declarado em conferida..X não é relido. O parecer de segurança do #904 (cdef93fb, A1, S1 a S4) prova o mesmo e as variantes `_*.md` e `contrato: 0`.
- **Veredito trocado no mesmo arquivo segue barrado:** reprovado em X trocado para aprovado num commit só da pasta, a função devolve X, mas a conferência sai `fora do declarado` no parecer trocado e `não cumpriu` (o `parecer_de_portao_da_branch` com `veredito_trocado` desde o Base-sha o recusa em X..head). O furo é só o parecer que sai do head.
- **Pareceres de outro item vindos da develop** não entram na conta (filtro por `branch:` e `pedido:`; `test_parecer_de_outra_branch_ou_pedido_vindo_da_develop_nao_conta`); duas rodadas com `commit:` diferentes dão None (neutro).
- **Testes:** `python3 -m unittest tests.test_selo_e_entrega.CicloDo878` no c056f38d: 12 ok em 17,5 s, ramo de falha de cada guarda por comportamento.
- **Mutantes:** `bin/forge-mutante --processos 1` nas duas specs: ED1 a ED12 morreram (ED1 por erro, A2). `bin/forge-mutante --cobertura --base 34ab6714`: as 11 linhas de guarda do diff cobertas (`não coberto: tests/pesos-d4.json`, dado de teste).
- **Documentação e commit:** texto de ajuda do `entrega` e fragmento atualizados no mesmo commit; Conventional Commits em português.
- **CI do #904 no c056f38d** (run 45735551783, `headRefOid` conferido): as 10 partes da suíte, os dois tetos de pulados, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)` e `árvore já provada na develop` verdes. Vermelhos só os que esperam parecer ou rótulo: `bateria (pareceres)` (R-REVIEW: `bin/forge-check` sem parecer aprovado de review), `bateria` (agregado: `pareceres: failure`, o resto `success`) e `catraca` (run 45736460224, R-CONFORMIDADE: `bin/forge-check` pede o rótulo `afrouxa-regra` do dono).

- ci: c056f38d285c454744e3a343b705621d2cacda49 verde

## Achados
- A1 (bloqueante) bin/forge-check:2732 · a conta dos pareceres lê só o head: o reprovado de um portão sobre X, apagado depois, some e o Desde anda para X (S2). Parta dos portões com X selado (`revisados_selados` por tipo), exija o aprovado de cada um no head e rode `veredito_trocado` desde o Base-sha.
- A2 (recomendado) tests/test_selo_e_entrega.py:2245 · o ED1 morre por exceção (`e_ancestral` com None), não por asserção: o teste prova que a guarda evita o erro, não que sem conferida o Desde fica o de sempre. Cartão: um caso pela `entrega --pedido` sem conferida que afirme o intervalo a partir do Base-sha.

## Sondas
- S1 · `CicloDo878`, segurança `reprovado` em X, develop trazida, parecer de segurança apagado; `entrega --pedido` · espera: Desde na conferida e `não cumpriu` (`docs/indice.md` fora) · obtido: `intervalo: X..head`, `resultado: cumpriu`

## Parecer
Reprovado no c056f38d. O conserto do ciclo do #878 está bem desenhado e testado, mas a condição "todos os pareceres aprovados" se cumpre pela ausência: o parecer reprovado que sai do head deixa o Desde andar e esconde da conferência o trecho conferida..X (A1). Volta ao autor; na revalidação leio o delta. A2 vira cartão depois do merge.
