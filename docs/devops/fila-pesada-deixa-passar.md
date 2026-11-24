---
tipo: revisao-devops
contrato: 1
pedido: fila-pesada-deixa-passar
branch: melhoria/v0480-fila-pesada-diag
commit: 0e59c44642a8f388649cb794072fd347ebebd8aa
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-23
---
# Fila pesada deixa passar mais de 2 baterias (E138.5)

Diagnóstico só, sem código. Leitura de `hooks/pesado.py` e `bin/forge-pesado` (develop 0e59c446) e sonda local
barata (funções puras do hook, `FORGE_MAQUINA` em pasta temporária, nenhuma bateria rodada). Máquina de teste: 12
núcleos, então `vagas()` = 12 // 6 = 2.

## O que a leitura e a sonda provam
O limite de 2 vagas só vale para o que o hook enxerga. Quatro furos deixam baterias reais acima disso:

1. **Mesma sessão e mesmo agente furam a trava (causa principal).** `ocupada()` exclui `mesma_sessao()`
   (`pesado.py:188`, `:368`). Sonda: trava viva de `u1` da própria sessão, pedido `u2` => `ocupada = False`. Duas
   baterias em chamadas paralelas do mesmo agente passam as duas; a segunda só regrava a trava (`gravar_a_vez`), e a
   máquina conta 1 vaga para 2 processos.
2. **Segundo plano libera na hora.** O Post (`solta()`, `:182`, `:397-402`) dispara quando a chamada do Bash volta.
   Com `run_in_background` ela volta já; a trava some e a vaga fica livre com a bateria ainda rodando. Inferido da
   leitura (o hook não lê `run_in_background`); a sonda não o reproduz.
3. **Trava vence antes da bateria.** `vez_viva()` exige `agora - desde < TRAVA_S` (1200 s, `:38`, `:192`). Sonda:
   trava com 1300 s => `vez_viva = False`, vaga devolvida a uma suíte lenta que segue rodando (`maquina_cheia`
   deixa de contá-la).
4. **Comando fora do padrão nunca entra na fila.** `PESADOS_DO_FORGE` (`:47`) só casa `unittest discover`,
   `suite-paralela`, `pre-push --suite`, `forge-testes` e `forge-mutante` fora das formas leves. Sonda: `python3 -m
   unittest tests.test_x`, `python3 -m unittest -v` e `python3 -m pytest` => não pesado; laço de carga em shell
   também não. Esses rodam sem vaga e sem senha. Cobre as hipóteses "unittest direto" e "laços de carga" do cartão.

Descartado: PID na fila. A senha é `flock` preso pelo processo vivo (`entrar_na_fila`, `:99`), e `fila_viva` poda a
de processo morto; não vi vazamento aí. `maquina_cheia` não tem erro de contagem: com 2 outros projetos tomando as
2 vagas, o terceiro é recusado (sonda: `True`); o próprio projeto é barrado pelo `ocupada()` (uma trava por projeto).
`bin/forge-pesado` só lê o estado e não decide nada; não é causa. Limite da sonda: o pid de outro namespace
(sandbox) cai em "morto" pelo `inicio` gravado, então não testei vez de outra sessão por pid.

## Correção sugerida (arquivo: `hooks/pesado.py`)
- Contar tarefas, não projetos: guardar na vez uma lista de `tool_use_id` ativos (ou contador) e fazer
  `ocupada()` recusar também a mesma sessão quando já há bateria viva dela (fura 1).
- Soltar o Post só do `tool_use_id` dono e, em comando de segundo plano, manter a vez enquanto o PID da bateria
  viver (fura 2); `TRAVA_S` só vale com o PID morto ou sem PID da bateria (fura 3).
- Ampliar `PESADOS_DO_FORGE` com `unittest` por módulo e `pytest` (fura 4); laço de carga fora do hook segue sem
  cobertura e pede regra de `pesados` no projeto ou orientação aos agentes.
- Teste de regressão em `tests/` (dev da stack/QA), com um caso por furo.

Ordem de valor: 1, depois 4, depois 2 e 3.
