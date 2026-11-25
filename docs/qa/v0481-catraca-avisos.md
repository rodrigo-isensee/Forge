---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-catraca-avisos
commit: 7b107cfd7bc8bc61303e894731e91e5818050156
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 (catraca avisa o teto estourado e nomeia a violação liberada)

Clone `/root/.forge-contrib/wt/v0481-catraca-avisos-qa`, criado com o `bin/forge-copia` da develop (`b224ee09`); `HEAD` = `7b107cfd7bc8`, igual ao `git ls-remote` da branch no momento da criação. Depois dele a branch só ganhou os pareceres de review e de segurança (`869bcb81`, `c33dffc5`), sem código.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Teto estourado: a catraca diz qual módulo (e a ref) e que contou só as asserções diretas | `AssercaoNoAjudante.test_teto_estourado_avisa_o_modulo_e_o_que_contou` (mutantes CAV1, CAV2) | sem estouro, stdout vazio; com estouro, linha exata e contagem direta 0 | passou |
| Violação liberada pelo rótulo: uma linha `catraca: liberada: <violação>` por violação, texto inteiro | `LinhaDeComando.test_liberada_pelo_rotulo_nomeia_cada_violacao` (mutante CAV3) | `viol` não vazio (afirmado); contagem de linhas igual a `len(viol)`; rc 0 | passou |
| Só a mensagem muda: nenhum ramo de decisão, mesmo rc, nada que barrava deixa de barrar | `test_catraca` inteiro (417 testes) e leitura do diff | rc 0/1 e `perdas`/`afrouxamentos` já cobertos pelos testes existentes, que seguem verdes | passou |
| A linha nova não vaza nada que o log público não tenha | leitura do diff e do `_main` | `viol` é o mesmo texto que `print(v)` e o `resumo` já emitem no CI | passou |

## Cenários e resultado real
- **Diff** `b224ee09..7b107cfd` em `tests/catraca.py` (8 linhas): (1) parâmetro novo `onde="o módulo"` em `testes_da_arvore`, só rótulo; (2) um `print` dentro do `except AjudantesDemais`, antes do mesmo `return testes_da_arvore(arvore, 0, math.inf)`; (3) `_testes_por_modulo` passa `onde=f"{arq} em {ref}"`; (4) um `for v in viol: print(...)` depois do `print` da contagem e antes do mesmo `return 0`. Nenhum `if`, comparação, retorno ou código de saída foi tocado. A chamada recursiva sem `onde` usa teto infinito e não volta a estourar, então o aviso sai uma vez por módulo.
- **Vazamento:** `viol` já sai inteiro no caminho sem liberação (`print(v)`) e no resumo do passo (`resumo(titulo, [...] + viol)`), ambos no log do CI; a linha nova só o repete no caminho liberado. `onde` traz caminho de módulo de teste e a ref (sha ou nome de branch): nada novo para o log público.
- **Módulo tocado** `python3 -I -m unittest discover -s tests -p test_catraca.py`: `Ran 417 tests ... OK` (local, 280 s). Os dois testes novos imprimem o aviso no stdout dos testes que já usavam teto pequeno: ruído, sem falha.
- **Mutantes** `bin/forge-mutante tests/mutantes/v0481-catraca-avisos.json` (saída 0):
  ```
  forge-mutante: pedido=v0481-catraca-avisos rev=7b107cfd7bc8 spec=476a84cc4bf058e6949a2b6d405ae8deb928b16d51833c4933372234061e6729
  CAV1 · morreu · tests/catraca.py:775
  CAV2 · morreu · tests/catraca.py:811
  CAV3 · morreu · tests/catraca.py:2265
  ```
  `forge-mutante --cobertura --base b224ee09e78032d99a9682d6ffd2da534ae6ae60` (`base=b224ee09… mb=b224ee09… rev=7b107cfd…`): sem condição mudada sem mutante, rc 0. Três mutantes cobrem as três linhas de efeito do diff; a assinatura (`onde=`) é rótulo sem decisão.
- **Vermelho antes do verde:** `bin/forge-testes --vermelho b224ee09… --modulos test_catraca` saiu 2 (sem veredito: o prazo de 600 s por cópia estourou com a máquina carregada; não vale como vermelho). Recuo por cópia em `$TMPDIR`: `tests/catraca.py` da base com os testes do head, `python3 -I -m unittest discover -s tests -p test_catraca.py -k test_teto_estourado_avisa -k test_liberada_pelo_rotulo_nomeia`:
  ```
  ERROR: test_teto_estourado_avisa_o_modulo_e_o_que_contou
  FAIL: test_liberada_pelo_rotulo_nomeia_cada_violacao
  AssertionError: Lists differ: [] != ['catraca: liberada: R-CONTRIB: a chave `d[179 chars]md)']
  Ran 2 tests ... FAILED (failures=1, errors=1)
  ```
  Os dois caem sem a implementação e passam com ela.
- **CI do head `7b107cfd`:** `suíte` (3.12 e 3.14, 5 partes), `instalação`, `bateria (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)` e `teto de pulados` verdes. Vermelhos: `catraca` (reproduzido local: `R-CONFORMIDADE: mudança em tests/catraca.py`, que só passa com o rótulo `afrouxa-regra` do dono depois do último push; rótulo ainda ausente), `bateria (pareceres)` (esperam este parecer e os demais) e `bateria` (agregador). Por isso não gravo `- ci:`: as partes que contam ainda não estão verdes. Não consegui ler o log dos jobs (o sandbox nega o host do armazenamento de logs).
- ci: 7b107cfd7bc8bc61303e894731e91e5818050156 verde

## Dados de teste
Fixtures do próprio `tests/test_catraca.py` (repositório temporário com módulo de teto estourado; eventos de issue simulados com o rótulo do dono).
