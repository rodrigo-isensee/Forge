---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-corpus-custo
commit: b953cd459e87c06d6d0a049130505de8b9c8502d
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0479-corpus-custo

Code review do conserto do teste de custo do corpus da volta única (v0478 E41.1) no head b953cd45, base develop ef186de8 (v0478 E41.2). O diff troca a medida de CPU do `test_corpus_nos_dois_hooks` por um contador de trabalho (`sitecustomize` com auditoria: execuções do hook, subprocessos abertos e `time.sleep` do código do hook) e declara 12 mutantes.

## Achados
- A1 (bloqueante) tests/test_hooks_volta_corpus.py:124 · O contador não vê CPU do Python do hook: a sonda S1 (cerca de 200 ms de CPU a mais por decisão, uns 110 s a mais no lote) sobrevive. Regex ou parser lento, a regressão de custo mais provável num hook, sai do portão que a media (PROP-TEMPO-CPU).
- A2 (bloqueante) tests/apoio_volta_unica.py:146 · O teto de 10 por execução deixa 20% de folga sobre a medida (8,31, 4631 em 557; ruído visto de 1). A sonda S2 mostra que um git a mais em cada decisão (4631+557) passa. Isso contraria o "nenhum limite folgado" do dono (E41). Aperte o teto para a medida mais o ruído.
- A3 (recomendado) tests/apoio_volta_unica.py:77 · `trabalhadores_do_limite_de_cpu`, `limite_de_cpu_do_corpus` e `limite_de_cpu_do_corpus_sob_carga` ficaram sem uso fora do `test_medida_cpu.py`: é código morto. Apague os três com os testes deles.
- A4 (recomendado) tests/apoio_volta_unica.py:117 · A reprodução e as 10 rodadas estão só em `~/.forge-contrib/tmp/e411` (dez.log, repro-*.log), fora do commit e do PR. Os repro deram 137 a 142 s, abaixo de 180, então mostram a variação e não a falha. A docstring diz "o mesmo em qualquer máquina", mas a rodada 9 contou 4632. Leve as provas para o PR.

## Sondas
- S1 · forge-mutante com spec ad hoc, hooks/_comum.py:2872 `hook = Hook(nome)` seguido de `sum(range(20000000))`, teste test_corpus_nos_dois_hooks · espera: morreu (regressão de CPU do hook reprova) · obtido: S1 · sobreviveu · hooks/_comum.py:2872
- S2 · python3 -I: excessos_de_trabalho({'execucoes':557,'subprocessos':4631+557,'sono':0.0},557) · espera: excesso (um git a mais por decisão, +12%) · obtido: []

## Provas conferidas
- Mutantes: 12 declarados (`tests/mutantes/v0478-corpus-custo.json` M1 a M8 e `-2.json` M9 a M12), um por guarda mudada. O log do autor (`tmp/e411/mutantes.log`, `forge-mutante` em rev b953cd45, base ef186de8) dá os 12 como mortos, com rc=0. O M1 (o driver roda o caso duas vezes) e o M2 (o hook dorme) são regressões reais e morrem. O M2 é válido: `time` é importado em `hooks/_comum.py:23`, então não morre por NameError.
- 10 rodadas sob carga: `tmp/e411/dez.log` registra 10 verdes, com carga de 1 min entre 4,4 e 39 em 12 núcleos. Cada rodada deu 557 execuções, 4631 subprocessos (4632 na 9.ª) e sono 0. A CPU informativa ficou entre 139,8 e 145,1 s.
- Causa: o comentário do commit registra 125,5 s livre contra 142,1 s sob carga (o mesmo lote) e os 127 a 185 s do CI. Os logs repro-carga, repro-cache e repro-2cpu confirmam a subida sob carga, mas nenhum passou de 180 s.
- Teste novo: rodei `ContadorDeTrabalhoDoCorpus` (6 testes, OK em 0,13 s). A suíte inteira não foi rodada (fica para o CI). O módulo verde do autor está em `tmp/e411/modulo.log` (22 testes OK).

## Parecer
Reprovado. A medida deixa de depender da máquina, como o dono pediu, e os mutantes cobrem as guardas. Mas o novo portão não pega a classe de regressão que o antigo pegava: CPU gasta dentro do processo do hook (A1, sonda S1). E o teto que sobrou é folgado o bastante para deixar passar um git a mais por decisão (A2, sonda S2).

Para corrigir o A1, uma medida de trabalho do interpretador que não dependa da máquina. Por exemplo: chamadas de função contadas com `sys.setprofile` ou `sys.monitoring` (Python 3.12+) no mesmo `sitecustomize`, com teto da medida mais o ruído. Ou uma contagem de passos do parser do hook. Regex catastrófico dentro do motor `re` em C escapa à contagem de chamadas; nesse caso, explique no PR qual teste o cobre (o P3 de `test_hooks_volta_propriedades`, de 3 s por chamada, não pega 200 ms).

Para corrigir o A2, troque o teto por execução por um teto do lote próximo da medida, ou por um teto por execução de 8,4. O teste de borda continua no teto.

Os achados A3 e A4 não bloqueiam.
