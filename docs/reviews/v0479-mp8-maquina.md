---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp8-maquina
commit: 6ebd057c42e72eafe3b1033c3685799e9fef951e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 E23.2 (MP8, `forge-status --maquina`)

Diff de `0c47762a` (Base-sha) a `6ebd057c`: `bin/forge-status` (81 linhas a mais, 15 a menos; dentro do teto H1), `tests/test_maquina.py`, duas specs novas de mutante e a S1 do `v0476-mp2-mp4-3.json` reapontada para o laço novo, `docs/hooks.md` e o fragmento `changelog.d/v0479-mp8-maquina.md`.

## Achados
- A1 (recomendado) bin/forge-status:109 · `uso` entra cru na linha; o hook (`agentes.uso_de`, hooks/agentes.py:231) recusa uso não inteiro, negativo ou bool. Com `"uso": "x"` a visão mostra `agentes x de N`; usar a mesma forma (fora dela, `?`) deixa a visão igual ao que o hook decide.
- A2 (recomendado) bin/forge-status:103 · o filtro de pasta absoluta não é o do MP3: `projetos_ativos` (hooks/agentes.py:219) conta toda pasta texto. Com sessão de pasta relativa, o número de projetos e a parte mostrados divergem dos do hook; alinhar os dois num só critério.

## Conferência
- Pedido (MP8, `docs/propostas/multi-projeto-1711.md`): projetos ativos, agentes de cada um, carga, memória, disco, versão do Forge e decisões pendentes, com "saída conferida em teste". Tudo presente; nada além disso.
- Reuso, sem duplicar mecanismo: a parte usa `peso_valido` e a mesma fórmula do `Maquina.recusa` com `teto_adaptativo` (o mesmo `total` do hook, hooks/agentes.py:1049); o escape lê `ler_projetos_ativos` como o hook (hooks/agentes.py:1080); decisões por `forge_dono.cmd_abertas`; disco por `forge_disco`; tarefas pesadas por `vez_viva`/`vagas`.
- Leitura de outro projeto: só `ler_regular` (sem seguir link, teto de bytes, regular) e `cmd_abertas` (recusa `docs` por link); saída passa por `sem_controle` e corte de 300; sem rede. O parecer de segurança no mesmo head está na branch (`docs/security/v0479-mp8-maquina.md`).
- Guardas do diff: 13 mutantes declarados (MP8-1 a MP8-13), um por linha de guarda, em duas specs de até 8; cada um com teste do ramo de falha por subprocesso com `-I` e ambiente controlado.
- Suíte inteira: fica no CI do PR (`R-REVIEW`); aqui só os testes do diff.

## Sondas

## Parecer
Aprovado. O MP8 faz o que o pedido manda, reaproveitando os leitores e as fórmulas do MP2 a MP5, sem caminho novo de escrita nem rede. A1 e A2 são de consistência com o hook em entrada fora da forma e não devolvem a entrega (`R-REVIEW`).

Provas rodadas no head 6ebd057c, na worktree do review:
- `cd tests && python3 -m unittest test_maquina`: `Ran 33 tests ... OK`.
- `bin/forge-mutante --processos 1` nas duas specs do MP8: MP8-1 a MP8-13 `morreu`.
- `bin/forge-mutante --processos 1 tests/mutantes/v0476-mp2-mp4-3.json`: `S1 · morreu · bin/forge-status:132` (a spec editada segue matando).
- `bin/forge-mutante --cobertura --base 0c47762a`: toda condição nova `coberta`; único aviso `spec editada · tests/mutantes/v0476-mp2-mp4-3.json`, conferida acima.
