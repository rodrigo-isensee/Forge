---
tipo: revisao-seguranca
contrato: 1
pedido: suite-fluida
branch: melhoria/suite-fluida
commit: 24499f721c2c7be8868fef7eb62aa826a9773056
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: suite-fluida

Revisão estática do diff `b45e40a...24499f7` (fe61323 e 24499f7, 6 arquivos: `scripts/suite-paralela.py`, `tests/test_suite_paralela.py`, `docs/regras/R-TETO.md`, `README.md`, `docs/hooks.md`, `changelog.d/suite-fluida.md`) contra os critérios C8 a C11 e a linha security de `## E5` do desenho (`docs/propostas/suite-fluida-desenho.md`) e a DECISÃO DO DONO de 2026-11-04 20:41 (medida pela CPU de `/proc/stat` e `MemAvailable`). Os ajustes da E1.2b que estão na árvore de trabalho, ainda sem commit, ficam fora: este parecer vale para `24499f7`. Os testes não foram rodados (fora do escopo do brief; a suíte é do QA).

Resultado: reprovado por um bloqueante (A1, falha fechada de `FORGE_SUITE_PROCS` mais larga que a regra). Trava, sinais, higiene dos workers tardios, guarda de completude e invariantes estão cumpridos.

## Gatilhos
Controle do Forge (R-SEGURANCA): `scripts/suite-paralela.py`, o portão da suíte chamado pelo `.githooks/pre-push` e pelo CI. Regra protegida afrouxada: o R-TETO deixa de ter o teto fixo de 4 processos na suíte (decisão do dono de 2026-11-04).

## Achados
- A1 (bloqueante) scripts/suite-paralela.py:192 · FORGE_SUITE_PROCS aceita até max(4, nproc), não 1..nproc (C8, R-TETO.md:14): com nproc=2, o valor 4 passa e a suíte roda 4 processos em 2 núcleos; o teste :114 fixa o defeito. Corrigir para maximo = nproc e trocar o teste para recusar nproc+1.
- A2 (recomendado) tests/test_suite_paralela.py:187 · O harness fixa FORGE_SUITE_PROCS=3, então os testes de sinal (:623, :682) só cobrem o modo fixo; falta um teste do modo fluido: sinal no meio da fila, nenhum worker novo depois e todos os grupos encerrados (C9).
- A3 (recomendado) docs/regras/R-TETO.md:14 · O item novo diz que a suíte segue a mesma conta do teto de agentes (load de 1 min), mas a medida é a CPU de /proc/stat de fora da suíte (decisão de 2026-11-04 20:41); texto da regra protegida diverge do controle (AR-9; o mesmo do A2 do review).

## Detalhe dos achados
**A1.** Evidência: `scripts/suite-paralela.py:192` (`maximo = max(TETO, nproc or 1)`) e `:193`; o teste `tests/test_suite_paralela.py:114` exige que `"4"` com nproc = 2 seja aceito, e `:652` deriva o inválido de `max(4, cpu_count) + 1`. O critério C8, o texto novo do R-TETO (`docs/regras/R-TETO.md:14`) e o changelog dizem de 1 a nproc. Caminho: não há atacante externo; quem fixa a variável (um agente ou o CI) sobe a suíte acima dos núcleos de uma máquina pequena sem recusa, e o controle que deveria falhar fechado aceita um valor que a regra proíbe. É requisito do brief com gatilho, então bloqueia (R-REVIEW). Severidade: baixa. Correção mínima: `maximo = max(1, nproc or 1)` (com nproc desconhecido só "1", como diz C8), mensagem com a faixa real; em `:114` trocar por `n({"FORGE_SUITE_PROCS": "3"}, 2, ...)` com `assertRaises(ValueError)` e em `:652` derivar de `nucleos() + 1` do próprio script (não de `os.cpu_count()`, AR-4). Esforço: P. Dono: tech-lead (E1.2b, mesma branch).

**A2.** Evidência: `tests/test_suite_paralela.py:187` e `:219` fixam o modo; os dois testes fluidos (`:633`, `:646`) não mandam sinal. A leitura do código mostra o comportamento correto (abaixo), mas nada o prende contra regressão. Severidade: baixa. Correção mínima: um teste com `FORGE_SUITE_PROCS=""`, um módulo lento, SIGTERM no orquestrador, e a conferência de que nenhuma marca de módulo da cauda da fila aparece e não sobra processo dos grupos. Esforço: P. Dono: qa-engineer.

**A3.** Evidência: `docs/regras/R-TETO.md:14`. Não afrouxa além do decidido, mas a regra protegida descreve uma medida que o controle não usa, e quem audita a regra não acha o controle. Correção mínima: trocar a expressão da mesma conta pela medida real (núcleos de fora da suíte por `/proc/stat` e `MemAvailable`, limite 0,8 × nproc), citando a decisão de 2026-11-04 20:41. Esforço: P. Dono: tech-lead (E1.2b).

**Conferência pedida no brief (sem achado):**
- Falha fechada de `FORGE_SUITE_PROCS` antes de lançar: cumprida, salvo a faixa (A1). A recusa (`:193`) vem antes do `discover` e de qualquer `Popen` (`orquestrar`, `:650` a `:654`, rc 1 e `FAILED (configuração)`). `isdigit` recusa espaço, sinal, ponto e vazio com espaços; dígito Unicode que o `int` não lê gera `ValueError`, que cai no mesmo `except`: recusa. Vazio liga o modo fluido, de forma coerente em `:193` e `:660`.
- Trava de uma suíte por vez: intacta. `main` e `conferir_trava` (`:736` a `:784`) não mudam no diff, nem `.githooks/pre-push`, nem `.github/`; `orquestrar` só roda depois de `conferir_trava`, e à mão o script se reexecuta pelo hook (`:778`). A fluidez vale dentro da vez da trava (C11).
- Nenhum worker depois de sinal: cumprido. `ao_sinal` (`:410`) levanta `Interrompido`, que sai do laço de `rodar_fluido` (`:480` a `:484`) antes do próximo `lancar_um`; o `except` (`:694`) ignora novos sinais e chama `encerrar`, que manda TERM e KILL a cada grupo de `filhos`. Janela residual, a mesma de antes em `lancar`: sinal entre o fork dentro do `Popen` e o `append` (`:450`) deixa um filho fora de `filhos`; o `vigiar_pai` dele (`:283`) mata o próprio grupo em até 1 s depois de o orquestrador sair. Informativa, sem achado.
- Grupo, nice e TMPDIR 700 nos workers tardios: cumpridos. Todo worker, do primeiro ao último, nasce por `lancar_um` (`:442`): `mkdir(mode=0o700)` dentro de `mkdtemp` (`:445`, `:675`), `TMPDIR` próprio (`:448`), `start_new_session=True` (`:453`); `processo` aplica `os.nice(10)` e `vigiar_pai` (`:292`, `:293`). Tudo é apagado no `finally` (`:702`).
- Guarda de completude: intacta. Em modo fluido, `partes` recebe um módulo por worker na ordem em que nasce e passa por `conferir_particao` depois do laço (`:682`), além do multiconjunto contra o `discover` (`:691`, `:692`) e do `resumir` (rc, sinal, relatório, zero testes). Nenhum módulo é repetido.
- Limite superior (E2): no modo fluido, `quantos_em_paralelo` (`:252` a `:266`) devolve `max(base, cabe)` com `base = min(4, nproc)`, `cabe <= nproc` e `minimo = min(2, nproc)`, todos até nproc; a fila (`pendentes`) limita aos módulos. Nenhum caminho fluido passa de min(nproc, módulos) nem toca a trava. O único caminho acima de nproc é o fixo (A1). Medida: `/proc/stat` e `/proc/<pid>/stat` são só leitura; outro usuário não entra num grupo da suíte (exige a mesma sessão), e em cpuset as CPUs do host inflam os alheios, o que só reduz o paralelismo (lado seguro).
- Invariantes: `tests/config.json` sem mudança no diff; os cinco do R-TETO continuam no texto (`docs/regras/R-TETO.md:10`, `:11`, `:12`, `:15`).

**E3, o que muda na regra protegida:** só um item novo (`docs/regras/R-TETO.md:14`); nenhuma linha antiga sai nem muda. O que se afrouxa: a suíte passa a poder rodar até nproc processos (antes até 4), com piso de min(4, nproc) com folga e min(2, nproc) com carga alta, e `FORGE_SUITE_PROCS` vai de 1 a nproc (antes 1 a 4). Ficam as tarefas pesadas uma por vez e a trava.

**E4:** a frase de `## E4` do desenho troca o item do hook de teto (`docs/regras/R-TETO.md:13`) só por texto: acrescenta que a medida é refeita a cada disparo, sem cache nem janela. O comportamento descrito é o de hoje, nenhum limite muda e nenhum invariante cita a frase. Não afrouxa. Em `24499f7` ela ainda não foi aplicada (é da E1.2b).

**E5, título do PR:** o título destaca que a regra afrouxa e qual é, por exemplo `feat(suite): suíte fluida, sem o teto fixo de 4 processos [afrouxa R-TETO] (SUITE-FLUIDA)`. O corpo traz o motivo (a DECISÃO DO DONO de 2026-11-04, citada pelo ID e pela data), o item novo do R-TETO e a nova faixa de `FORGE_SUITE_PROCS`. O rótulo `afrouxa-regra` é aplicado pelo dono (E1.7). Nenhum invariante é removido, então a catraca não deve acusar violação de conteúdo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e do script em `24499f7` (`git show`), `grep`. Faltaram no PATH: `gitleaks` e `semgrep` (lacuna registrada; o diff não traz credencial nem URL, conferido na leitura). PA-7 conferido: AR-3, AR-5, AR-7, AR-8, AR-10 e AR-11 não se aplicam ao diff; AR-4 e AR-9 aparecem em A1 e A3.
