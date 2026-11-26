---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-catraca-avisos
commit: 7b107cfd7bc8bc61303e894731e91e5818050156
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 E14.37 (#897, catraca avisa o teto estourado e nomeia a violação liberada; classe C)

Base `b224ee09e78032d99a9682d6ffd2da534ae6ae60`, revisado `7b107cfd7bc8bc61303e894731e91e5818050156` (1 commit, E14.31). Diff: 6 linhas em `tests/catraca.py`, 2 testes em `tests/test_catraca.py`, spec `tests/mutantes/v0481-catraca-avisos.json` (CAV1 a CAV3) e fragmento `changelog.d/v0481-catraca-avisos.md`. Primeiro parecer da branch (não havia anterior).

## Só a mensagem muda (lido no diff)
- `tests/catraca.py:757`: `testes_da_arvore` ganha `onde="o módulo"` como último parâmetro com padrão; nenhum chamador posicional quebra (os únicos chamadores são a recursão da linha 776 e `_testes_por_modulo`, linha 811, que passa `onde=` por nome).
- `tests/catraca.py:775`: o `print` entra antes do `return` que já existia no `except AjudantesDemais`; a recursão segue `testes_da_arvore(arvore, 0, math.inf)` igual, sem `onde` (com teto infinito não estoura de novo, logo não imprime duas vezes). O perfil devolvido é o mesmo: a contagem "só as diretas" e a falha fechada do lado que perde asserção não mudam.
- `tests/catraca.py:2264-2265`: o laço `catraca: liberada: <v>` fica entre o `print` da contagem e o `return 0` do ramo `liberado`, que não muda; o ramo sem rótulo segue imprimindo cada violação e devolvendo 1. Nenhum `if`, condição ou código de saída mudou; nada que barra deixa de barrar.

## Vazamento no log público
- A linha `catraca: liberada: <v>` imprime o mesmo texto `v` que o ramo sem rótulo já imprime no stdout (`for v in viol: print(v)`) e que o próprio ramo liberado já grava no `GITHUB_STEP_SUMMARY` pelo `resumo(...)` (linha 2262). Não há classe nova de dado no log: violação é caminho, regra e trecho do diff do próprio PR público.
- O aviso do teto imprime `arq` (caminho de `tests/`) e `ref` (o argumento `b`/`h` já usado na catraca: sha ou nome de ref), mais o teto numérico. Nada de token, ambiente ou resposta da API.
- Consumidores do stdout conferidos: `bin/forge_pronto.py:45` só repassa a saída quando o rc é diferente de 0; `bin/forge_corrigidos.py` (afrouxamentos) chama `violacoes_das_regras` em processo, e a linha do teto, se estourar, sai entre as linhas `afrouxamentos:` sem que alguém as leia por máquina; `bin/forge-fechar:1383` e `:1690` não alcançam `perdas_dos_testes`.

## Testes e mutantes
- `test_teto_estourado_avisa_o_modulo_e_o_que_contou`: confere o silêncio sem estouro, a linha exata com módulo e ref e o perfil com 0 asserções (só as diretas); o `mock.patch.object(..., "__defaults__", ...)` troca os 3 padrões (fundo, teto, onde) e o `onde` explícito de `_testes_por_modulo` vence o padrão, o que prova o CAV2.
- `test_liberada_pelo_rotulo_nomeia_cada_violacao`: afirma um mínimo (`assertTrue(viol)`), o rc 0, a linha da contagem e a lista exata e ordenada das linhas `liberada:` (checklist 11).
- `bin/forge-mutante --processos 1 tests/mutantes/v0481-catraca-avisos.json` (rev `7b107cfd7bc8`): CAV1 morreu (`tests/catraca.py:775`), CAV2 morreu (`:811`), CAV3 morreu (`:2265`).
- `bin/forge-mutante --cobertura --base b224ee09e78032d99a9682d6ffd2da534ae6ae60`: rc 0, sem condição mudada sem mutante.
- Módulo tocado: `python3 -I -m unittest discover -s tests -p test_catraca.py` no `7b107cfd`: `Ran 417 tests`, `OK`.
- Tamanho (H1): 6 linhas de código, um comportamento (a mensagem); dentro do teto.

## CI
Lido em `gh pr checks 897` no head `869bcb81`, descendente de `7b107cfd` só pelo parecer de segurança (`docs/security/v0481-catraca-avisos.md`): os checks concluídos e verdes fora `bateria (pareceres)`, `bateria` e `catraca`, que esperam o parecer ou o rótulo (o merge exige todos): suíte 3.12 e 3.14 (10 partes), `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)` e `árvore já provada na develop` verdes. A `catraca` vermelha é a esperada (`R-CONFORMIDADE: mudança em tests/catraca.py`, que pede o rótulo do dono).

- ci: 7b107cfd7bc8bc61303e894731e91e5818050156 verde

## Parecer
Aprovado. A mudança é só de mensagem, como o pedido diz: nenhum ramo de decisão nem código de saída muda, a linha nova não publica nada que o log e o resumo do CI já não publiquem, os três mutantes morrem e o módulo tocado está verde.
