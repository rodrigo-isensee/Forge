---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 1d6692f507ac6bf65faf1b5be6cff0de3403c9dc
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481

Review por delta (E7.37) de 21a96c1a a 1d6692f5. Li o delta pelo `forge-check parecer delta docs/reviews/v0481-prazo-forge.md`: `revalida: sim` (o `changelog.d/v0481-prazo-forge.md`, do domínio do parecer, mudou). O diff de código é `hooks/_comum.py` (`PRAZO_DO_MERGE_S` de 8.0 para 7.5 e o comentário), as 4 fixtures de merge, a spec P1, o M13, `tests/prova_de_carga.py` e `tests/test_hooks.py`.

## Achados
- A1 (bloqueante) hooks/_comum.py:2827 · O A5 não fecha: com 7,5 s, o hook parecer com `gh pr merge` e FIFO no commondir, na sessão do Forge e com 48 laços de CPU, ainda é morto pelo corte de 10 s (libera) em 3 de 7 rodadas (S1). A parede fora do relógio do hook passa de 1,5 s sob carga (S2).
- A2 (recomendado) tests/test_hooks.py:1230 · A docstring de `test_prazo_do_merge` ainda diz "o merge com 4 s de git libera", e a da linha 1373 diz "a fronteira dos 8 s". A fixture `v0455-merge-com-git-muito-lento-recusa-em-8s.json` também guarda o 8 s no nome.

## Sondas
- S1 · FIFO no commondir de worktree, Forge, parecer.py real, `gh pr merge melhoria/x --squash`, `timeout 10`, 48 laços de CPU, 7 rodadas · espera: 2 antes de 10 s nas 7 · obtido: 3 de 7 com 124 (10,09 a 10,11 s; em 2 a mensagem já tinha saído); 4 com 2, em 9,0 a 9,2 s
- S2 · a mesma sonda, 7,5 s contra 8 s (21a96c1a) em seguida, 6 rodadas cada, loadavg de 32 a 140 · espera: 7,5 s sem corte · obtido: 21a96c1a com 5 de 6 cortadas; 1d6692f5 com 4 de 6 cortadas; as que decidiram levaram de 9,5 a 9,8 s, contra 8,5 s nominais
- S3 · a mesma sonda com FIFO em `.git/HEAD` de um clone, 1d6692f5, 8 rodadas, loadavg até 109 · espera: código 2 antes de 10 s · obtido: 2 nas 8, pelo erro interno (`falhar_fechado`), em 6,9 a 9,5 s; é o caminho do A2 do parecer anterior, fora do diff, a 0,5 s do corte

## Parecer
Reprovado: o diff faz o que a opção (a) do A5 da segurança pedia, mas a medida não fecha o A5 (A1).

- **O que está certo.** O 7,5 s entrou em todos os lugares onde o 8 s aparecia: as specs, as fixtures (3,5 s de git deixam os mesmos 4 s de resto), a tabela de `prova_de_carga.py` e o changelog. O teste `test_s1_...` agora deriva os passos de `PRAZO_DO_MERGE_S`, sem número fixo. Nada que barra hoje deixa de barrar: o prazo menor só adianta a recusa. O preço é recusar antes um merge legítimo em máquina carregada, o que falha fechado.
- **Por que o A5 não fecha.** O `test_recusa_do_prazo_longo_presa_deixa_folga` confere, no relógio falso, que 7,5 + 0,5 + 0,5 fica 1,5 s abaixo do `timeout`. Mas os 1,5 s são uma constante (`FOLGA_DE_PAREDE_S`) baseada em uma medida (1,1 s), e a parede que o relógio do hook não vê cresce com a carga: partida do Python antes de `inicio`, saída depois do `bloquear` (S1 mostra rodadas cortadas com a mensagem já escrita). Sob a mesma carga da S3 da segurança (48 laços), o corte ainda libera (S1). Tirar 0,5 s só desloca o limiar, como mostra a S2.
- **Correção sugerida (decisão do autor com a segurança).** Tirar a corrida com o relógio em vez de afinar o número: (1) não esperar o FIFO, conferindo com `os.stat` e `S_ISFIFO` (ou abrindo com `O_NONBLOCK`) o `.git`, o `gitdir` e o `commondir` antes da leitura da sessão e antes do `git` do registro, e recusando direto, sem precisar do vigia; ou (2) a opção (b) da segurança com a origem na partida do processo (`/proc/self/stat`, campo 22, ou `time.monotonic()` lido antes do `import` pesado): um teto total de cerca de 8 s, com o vigia da sessão e o do registro armados com o tempo que sobra. Nos dois casos, o teste de parede deve ser real (subprocesso sob carga, como a S1) ou sair do relógio falso com a partida contada.

Verificadores que rodei no Revisar-sha:
- `SondaS1ComRelogioFalso`: 3 testes OK, com o novo.
- `bin/forge-mutante --processos 1 --ids M13` em `v0481-prazo-forge-2.json`: o M13 morreu.
- `bin/forge-mutante --ids P1` em `v0455-prazo.json`: `controle vermelho`. O `test_prazo_do_merge` sem mutante, com loadavg de 30 a 45, recusou o merge com git de 3,5 s ("não decidiu em 7.5 s"), e a prova de carga não o aceitou. É a mesma classe das 2 falhas sob carga que o autor relata. O CI decide.
- CI: o 1d6692f5 não tem run no #888 (`gh run list`: o último CI é do f17ee6f4, com as 10 partes da suíte verdes e a `bateria (pareceres)` vermelha por faltar parecer). Não gravo `- ci:`. As partes de `test_hooks` sob carga ficam para o CI deste head.
- Tamanho H1: o delta tem 2 linhas de código em `hooks/`, e o item segue dentro do teto.
