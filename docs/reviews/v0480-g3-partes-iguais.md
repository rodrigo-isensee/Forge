---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-g3-partes-iguais
commit: 8979faa4be379bdfb0febe55123745d5e875683c
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E102.3, reequilíbrio das partes da suíte do CI)

Base 2d73a35e, head 8979faa4. Diff: `tests/pesos-d4.json` (204 para 251 chaves) e `changelog.d/v0480-g3-partes-iguais.md`. Classe T; este review é o único portão.

## Achados
- A1 (bloqueante) tests/pesos-d4.json:133 · Escala 0,5377 aplicada para passar no test_pesos_teto: test_hooks.Hooks.test_fixtures vale 224 na escala e cerca de 416 s reais, acima do limite de 225 s que a guarda protege. Contorna a guarda (R-CONFORMIDADE); divida o teste ou leve o limite ao dono.
- A2 (recomendado) scripts/pesos-do-ci.py:107 · Pesos escalados misturam unidades na próxima regravação: gerar() mantém o peso atual (escalado) da unidade sem amostra e gravar_pesos/--medir gravam segundos; a LPT passa a comparar escalas diferentes. Sai com A1 (pesos em segundos).

## Sondas
- S1 · acima_do_limite({"test_hooks.Hooks.test_fixtures": round(224/0.5377, 1)}) de tests/test_pesos_teto.py · espera: [] (unidade cabe no limite) · obtido: [("test_hooks.Hooks.test_fixtures", 416.6)]

## O que foi conferido
- Nenhum teste sai da suíte: nenhuma chave removida (as 204 da base estão entre as 251); os pesos só equilibram e nunca decidem o que roda (`scripts/suite-paralela.py:11`); sem peso, a unidade usa a mediana.
- O número de partes não muda: o diff não toca `.github/` nem `scripts/` (0 linhas); `parte: [1, 2, 3, 4, 5]` segue no `ci.yml`.
- O divisor: a LPT (`repartir`, `scripts/suite-paralela.py:153`) é invariante a escala uniforme, e a mediana do peso ausente escala junto; a divisão desta árvore não quebra. A quebra vem depois, na mistura de escalas (A2). Todos os valores são números >= 0, aceitos por `ler_pesos`.
- Testes de pesos rodados (só eles, `tests/`, ambiente limpo): `test_pesos_teto` e `test_pesos_do_ci`, 18 testes, OK. Passar no teto é justamente o sintoma de A1: o número cabe, a unidade real não.
- Suíte inteira: só no CI do PR (`R-REVIEW`); não rerrodada aqui.

## Parecer
Reprovado. O reequilíbrio em si está correto (sem teste perdido, 5 partes, LPT intacta), mas a escala 0,5377 existe, pela mensagem do commit, "para caber no teto de 225 s por unidade do test_pesos_teto": é ajustar o dado para a guarda passar, e a guarda diz que o remédio é dividir a unidade, não subir o teto. Severidade: bloqueia.

Sugestão: gravar os pesos em segundos reais e dividir `test_hooks.Hooks.test_fixtures` (cerca de 416 s) e `test_hooks.Hooks.test_t1_variantes_que_o_bash_ignora_nao_tiram_comando_da_leitura` (cerca de 337 s) em testes menores, cada um com chave própria; se dividir não couber no item, o limite de 225 s volta ao dono por ADR (`R-DECISAO`), com a medida. A2 se resolve junto.
