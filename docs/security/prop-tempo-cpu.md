---
tipo: revisao-seguranca
contrato: 1
pedido: prop-tempo-cpu
branch: melhoria/prop-tempo-cpu
commit: 650dbf9398a2a151368cd231d0e691a53857ccc0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: prop-tempo-cpu

Diff revisado: `9620160fc7ce0c0a3e411cb0bc52d1d9716e6fa4...650dbf9398a2a151368cd231d0e691a53857ccc0`. Esta é a revalidação por delta do parecer `2a55d584b73a211daaf0902284c0447463cc5d1e` (head `fe9dfb2`). O delta `fe9dfb2..650dbf9` sobe os três limites, por decisão do dono de 2026-10-27 19:13: corpus de 60 para 90 s de CPU por trabalhador, as duas propriedades do lançador de 60 para 120 s de CPU, teste T de 1,0 para 2,0 s de CPU. Ele também ajusta o mutante M4 e o teste do limite.

## Gatilhos
- Controles do Forge: os testes que provam o desempenho dos hooks `conformidade` e `parecer`.

## Achados
- A1 (recomendado) tests/apoio_volta_unica.py:44 · o teto somado (agora 90 s x trabalhadores) perde sensibilidade a um texto caro sozinho: com 4 trabalhadores, ele só reprova quando esse texto gasta mais de cerca de 267 s de CPU (360 s menos os 93 s do corpus medidos no parecer anterior); medir a CPU por texto no driver e limitar o pior
- A2 (recomendado) tests/test_hooks_volta_corpus.py:114 · o relógio fica só no texto da mensagem do corpus e das duas propriedades do lançador; uma regressão que espera sem gastar CPU passa até o timeout do lote (900 s); um teto largo de relógio (por exemplo 300 s) guardaria travamento
- A3 (recomendado) tests/test_hooks_volta_propriedades.py:142 · as docstrings ainda dizem os limites antigos: "menos de 1 s de CPU" (o limite agora é 2,0) e, em tests/test_hooks_volta_lancador.py:140 e :355, "60 s de CPU" (agora 120); atualizar o texto

## Detalhe dos achados
`forge-check delta --parecer` lista só as 9 linhas trocadas em 6 arquivos. Todas são operandos de limite, mensagens, a docstring do apoio, o nome do teste do limite e o M4. Os três pontos pedidos:

1. **Um custo que exploda continua reprovado.**
   - **T** (`tests/test_hooks_volta_propriedades.py:153`). Sonda local, os 6 casos de 50 mil palavras: de 0,01 a 0,17 s de CPU (pior caso: `env com NOME=valor`). A versão quadrática levava 8,3 s com 10 mil palavras, o que dá cerca de 200 s com 50 mil. O limite de 2,0 s fica cerca de 12x acima do pior caso linear e cerca de 100x abaixo do quadrático.
   - **Propriedades do lançador** (`tests/test_hooks_volta_lancador.py:153`, `:372`). No CI: 72,7 s de CPU contra 120 s (run 40585968086). Na máquina local: de 24 a 34 s. Uma regressão de 1,7x já reprova no CI, e de 3,5x reprova localmente. Um custo quadrático em mais de 10 mil formas passa disso por ordens de grandeza.
   - **Corpus** (`tests/apoio_volta_unica.py:44`). No CI: 121 s de CPU com 2 trabalhadores, contra 180 s (1,5x de folga). Na máquina local: 93 s com 4 trabalhadores, contra 360 s (cerca de 3,9x).
   - **Textos grandes.** O guarda do custo por tamanho do texto não mudou: `test_t_orcamento_por_numero_de_palavras` (`tests/test_hooks_volta_propriedades.py:136`) ainda exige menos de 3 s de relógio por decisão, até o teto de palavras e o teto de caracteres.

   A trava de desempenho fica mais frouxa, como o dono aceitou, mas continua pegando um custo que exploda. O que se perde é a sensibilidade a regressões moderadas (de 1,5x a 2x), e isso não abre caminho de desvio. O prazo de produção (o vigia que recusa com marcador) tem testes próprios no relógio, e o delta não os tocou.
2. **O teto de relógio do T ficou:** `self.limite_de_tempo(5)` (`tests/test_hooks_volta_propriedades.py:149`, alarme `ITIMER_REAL`, `tests/apoio_volta_unica.py:1096`) não mudou. Nas outras duas medidas, o relógio ainda fica só na mensagem (A2, sem mudança desde o parecer anterior).
3. **Nenhuma asserção de recusa saiu.** Contagem das asserções em `fe9dfb2` e em `650dbf9`:

   | Arquivo | Em `fe9dfb2` | Em `650dbf9` |
   |---|---|---|
   | corpus | 59 | 59 |
   | lançador | 113 | 113 |
   | propriedades | 38 | 38 |
   | apoio | 13 | 13 |
   | `test_medida_cpu` | 6 | 6 |

   As 8 linhas com `assert` no delta são as 4 de tempo, trocadas no lugar. Os testes do item passam: `tests.test_medida_cpu` e o T (6 testes, OK). O M4 agora troca `90 * trabalhadores_do_lote()` por `90` e continua morto pelo `test_limite_do_corpus_e_90_s_por_trabalhador` (o caso de 4 núcleos espera 180).

A1 e A2 seguem como recomendados. A1 só teve o número atualizado para o limite novo. A3 é novo: um texto desatualizado, sem efeito no controle. Severidade: baixa ou informativa. Esforço P. Dono: `tech-lead`.

## Riscos aceitos e ferramentas
Nenhum risco aceito por este parecer. Subir os limites é decisão do dono de 2026-10-27 19:13, registrada no pedido. Ferramentas usadas: leitura do diff, `forge-check delta`, os testes do item e uma sonda local de CPU do T (em `$TMPDIR`). `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH (lacuna). O delta não toca workflow, dependência nem segredo.
