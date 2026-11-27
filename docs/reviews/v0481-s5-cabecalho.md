---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-s5-cabecalho
commit: c8c2e1384d3811c4380f295b0a72f72d191c3951
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 E25.6 (S5, #917), volta 1 por delta

Delta lido (`forge-check parecer delta`): `e216aa71..c8c2e138`, no domínio `bin/forge_autorizacao.py`, `tests/mutantes/v0479-pv-a2-concessao-3.json`, `tests/mutantes/v0479-pv-a2-concessao-4.json`, `tests/mutantes/v0481-s5-cabecalho.json` e `tests/test_autorizacao.py` (o código novo vem do `c8c2e138`; o resto do intervalo são pareceres). Código: 2 linhas, dentro do H1.

## Verificação
- ci: c8c2e1384d3811c4380f295b0a72f72d191c3951 verde
- CI do `c8c2e138` (run 45885735709; catraca run 45885857531): suíte 3.12 e 3.14 partes 1 a 5, instalação, bateria (passos), bateria (verificações longas), árvore já provada e catraca verdes; `bateria` e `bateria (pareceres)` esperam o parecer.
- Local: `python3 -m unittest tests.test_autorizacao tests.test_forge_mutante.ConferirTodas`: 30 testes, OK (ConferirTodas era o vermelho do A2).
- `bin/forge-mutante tests/mutantes/v0481-s5-cabecalho.json --processos 1`: M1 a M5 mortos (M4 por erro). M18 (concessao-3) e M27 (concessao-4) mortos (M27 por erro).
- `bin/forge-mutante --cobertura --base 3c833f3f`: L219 (M5), L234 (M1, M18), L237 (M2), L238 (M4, M27) cobertas; `isenta · bin/forge_autorizacao.py:230(base)` com motivo. Sem shell tocado.

## Leitura do delta
- A1 resolvido: a guarda apagada `texto.startswith("---\n")` ganhou isenta; a regra segue em `linhas[0] != "---"` (L234), morta por M1 e M18. Aceito: mesma condição, com mutante nas duas specs.
- A2 resolvido: M18 e M27 miram o texto da `frente` nova e morrem; ConferirTodas verde local e no CI parte 4/5.
- A5 resolvido: `FIXA = {` restaurado.
- A3 da segurança (L219): achado do grep com `frente` vazia barra com "Parecer sem cabeçalho legível", falha fechada; o teste novo passa pelo git real e prova o ramo de falha. Vem antes do teste de tipo e pasta, ordem certa.
- O comentário de sondas antes de `class Frente` é documentação do teste; não muda comportamento.

## Achados
- A3 (recomendado) bin/forge_autorizacao.py:234 · Mantido da 1.ª rodada: abertura exata (`linhas[0] != "---"`) contra o `strip()` do `ler_frontmatter`; `--- ` no topo dá `{}` aqui e campos lá. Falha fechada; vira cartão.
- A4 (recomendado) bin/forge-fechar:1347 · Mantido da 1.ª rodada: o `awk` de `pedido_da_branch` fecha só em `$0 == "---"`; fora do corte deste item; vira cartão.
- A6 (recomendado) bin/forge_autorizacao.py:219 · A guarda nova vale para todo arquivo do grep em docs/reviews, qa, security e devops; há 50 sem frontmatter (docs/qa/bugs/). Relato que cite `branch: <ramo>` trava a concessão do ramo. Falha fechada, sem gatilho hoje; restringir aos pareceres num cartão.

## Parecer
Aprovado. O delta fecha os bloqueantes A1 e A2 do review e o A3 da segurança, com mutante declarado e morto em cada guarda nova ou mudada e o CI do head verde fora dos checks que esperam o parecer. A3, A4 e A6 viram cartões depois do merge.
