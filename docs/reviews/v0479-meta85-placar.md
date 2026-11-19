---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-placar
commit: 87aff761c47ae4aa8bcf2b81c7565c71888cbcbc
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 E36.2 (melhoria/v0479-meta85-placar, head 87aff761)

Escopo: só o que a branch acrescenta à `melhoria/v0479-placar-fases` (42c2a906, aprovada nos três portões), `git diff origin/melhoria/v0479-placar-fases...HEAD`: `bin/forge-placar`, `tests/evals/test_placar.py`, `tests/mutantes/v0479-meta85-placar{,-2,-3,-4}.json`, os três `v0479-placar-fases-{2,3,4}.json` reescritos, `changelog.d/v0479-meta85-placar.md` e `docs/melhoria-continua.md`.

## Achados
- A1 (bloqueante) bin/forge-placar:664 · Sem nenhuma linha PARADA do tipo nos pedidos, a parada sai 0 em vez de "-": na área real de 19/11, com duas quedas de sessão no histórico, diz "0 h 00 min" (S1). Fere "fonte ausente sai -, nunca 0" (melhoria-continua) e o pedido do dono. Sem linha do tipo, devolva None.
- A2 (recomendado) bin/forge-placar:658 · Nada no time escreve as linhas `PARADA sessão|promoção ... até ...` (grep em agents/, skills/, templates/: zero); sem o Jarvis registrá-las ao retomar, a medida nunca sai. Cartão para o texto de registro do histórico.
- A3 (recomendado) bin/forge-placar:676 · `gh run list --branch develop` mistura workflows e o PR develop→homolog (headBranch develop): um verde de outro workflow fecha a vermelha; timed_out e startup_failure não contam. Cartão: documentar `--workflow ci.yml --event push` e tratar essas conclusões como falha.
- A4 (recomendado) tests/evals/test_placar.py:580 · O teste compara com o relógio real (tolerância 60/61 min); passa de 90 s de carga e cai. É da classe da varredura de testes de prazo pedida pelo dono (19/11 08:54): injete o "agora" (variável de ambiente ou parâmetro) em vez de ler a hora.

## Sondas
- S1 · `bin/forge-placar fases --git . --ref origin/develop --dia 2026-11-19 --raiz-pedidos /root/.forge-contrib` (histórico com "Sessão caiu de novo (~15:06 a 15:30)", sem linha PARADA) · espera: `horas paradas, sessão: -` · obtido: `horas paradas, sessão: 0 h 00 min`

## Parecer
Reprovado por um bloqueante (A1), de correção pequena e local: em `paradas_do_historico`, sem nenhuma linha `PARADA <tipo>` em todos os pedidos, devolver `None`; com ao menos uma linha do tipo (em qualquer dia), a janela sem parada segue 0. Teste do ramo: raiz com `docs/pedidos` e histórico sem `PARADA` dá `min` None e o texto `-`; mutante declarado na guarda nova. Sem a raiz (`docs/pedidos` ausente) já sai `-` (S1 sem `--raiz-pedidos`).

O resto está correto e coberto: média, mediana e p75 inclusivo (`statistics.quantiles`, um item só vale o próprio total), corte `[desde, ate)` pela hora do merge com fuso opcional e erro com rc 2, PR do merge de dois pais pelo assunto e do squash pelo `(#N)`, `merge` no `--json`, união de intervalos recortada na janela, develop vermelha do fim do reprovado ao fim do verde seguinte, cada parada com a fonte por escrito, meta 42 min (ordem do dono 19/11 14:52). Ajuda, `docs/melhoria-continua.md` e fragmento de changelog acompanham. A2 a A4 não devolvem (META85: recomendado vira cartão depois do merge).

Tamanho (H1): `bin/forge-placar` +124 −21 sobre a placar-fases, dentro de 150; a placar-fases entra antes na develop (mesmo arquivo, `forge-check sobreposicao`), e esta branch traz a develop só no merge.

Ferramentas e provas: `python3 -m unittest tests.evals.test_placar` no head 87aff761: 47 testes OK. `bin/forge-mutante --processos 1 tests/mutantes/v0479-meta85-placar*.json`: M1 a M28 morreram; `v0479-placar-fases-{2,3,4}.json` (M13, M19 e M24 reescritos): todos morreram. `bin/forge-mutante --cobertura --base origin/melhoria/v0479-placar-fases`: toda guarda de `bin/` coberta (o "sem mutante" só aparece em linhas auxiliares do teste). Suíte inteira: fica no CI do PR (sem suíte local, pelo brief).
