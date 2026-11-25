---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 4ab16b74a90aa0d9214d1a6c32764dfac9e7fe89
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481

Review por delta (E7.45, 3.ª volta, E7.40) de 1d6692f5 a 4ab16b74. Li o delta pelo `forge-check parecer delta docs/reviews/v0481-prazo-forge.md` (`revalida: sim`, o parecer anterior barrou) e o `git diff 1d6692f5..4ab16b74`. Do autor: 5a630ac0 (`hooks/_comum.py`, `hooks/conformidade.py` só na docstring, changelog, specs e testes), d7ca46e4 (M22 e os mutantes do -3 sem troca vazia), o merge da develop 5f99d144 e 4ab16b74 (testes). O resto do diff é a develop trazida, fora deste review.

## Sondas

## Parecer
Aprovado: o A1 do parecer anterior (A5 da segurança: o merge com FIFO no `.git` morto pelo corte de 10 s, que libera) está fechado pela opção (2) que o parecer sugeria, sem teste enfraquecido.

- **A correção.** `idade_do_processo` lê o campo 22 de `/proc/self/stat` (índice 19 depois do `)`, certo) contra o `CLOCK_BOOTTIME`, e o `inicio` do `executar` recua essa idade: a partida do Python e os imports passam a contar no prazo. O hooks.json lança `python3` direto, sem shell, então o fork é a partida que o corte de 10 s vê. A sessão e o registro depois do prazo vencido cabem no teto `prazo + 2 x 0,5` (`prazo_da_etapa`); sem tempo, a sessão não roda e a linha crítica recusa (falha fechado), e o registro é pulado sem mudar a decisão. Fora do processo do hook (driver do lote, teste em processo) ou sem `/proc`, a idade é 0 e o comportamento é o de antes, nunca mais frouxo. A leitura da entrada agora também conta no prazo, o que só aperta.
- **Testes.** Os novos do relógio falso cobrem a idade (`test_prazo_conta_da_partida_do_processo`), o alarme atrasado que encurta a sessão e pula o registro, o alarme que passa do teto (recusa sem ler a sessão), o erro interno sem vigia e o prazo vencido sem prazo do hook. A prova de parede real (`test_partida_lenta_recusa_o_merge_antes_do_corte`) parte 3 s atrasada e exige a recusa antes dos 10 s. O 4ab16b74 troca o FIFO do `commondir` para o `HEAD` da worktree: depois do #886 o FIFO no `commondir` recusa sem esperar, e a prova deixaria de chegar ao prazo; no `HEAD` o `git` do hook espera, e o caminho do A5 segue provado. Não enfraquece: o FIFO no `commondir` tem a prova própria vinda do #886. O `LANCADOR_MEDIDO` (L31) conta o prazo do mesmo ponto da sua medida, como antes do E7.40; a idade real tem a prova acima. A guarda do `test_hooks_reais_e_driver_nao_passam_relogio_nem_armar` passa a cobrir também o `idade`, o que só aperta. As trocas das specs `lote-unico-032-l31`, `v0478-bp1-relogio` e M11 só seguem a linha nova (AR-12 conferido: `forge-mutante --conferir` diz o trecho no lugar).
- **A2 do parecer anterior** (docstrings do 8 s): corrigido nas duas, e a fixture de 9 s renomeada.

Verificadores que rodei no Revisar-sha:
- Módulos tocados: `tests.test_hooks.SondaS1ComRelogioFalso`, `tests.test_hooks.PrazoVencidoNaSessaoDoForge`, `tests.test_hooks_volta_corpus` e `tests.test_hooks_volta_propriedades`: 61 testes OK em 766 s, com loadavg de 20 a 34.
- `bin/forge-mutante --cobertura --base 1d6692f5`: as guardas novas de `hooks/_comum.py` (2883, 2895, 2902, 2927, 2969, 2972, 2978, 2992) cobertas. `bin/forge-mutante --processos 1` em `v0481-prazo-forge-3.json`: M14 a M21 morreram; `--ids M22` em `v0481-prazo-forge-2.json`: morreu.
- CI do head (run 45692259103, `headSha` 4ab16b74): as 10 partes da suíte, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, os tetos de pulados, a instalação e a `árvore já provada` verdes. `bateria (pareceres)` e `bateria` vermelhas por faltar o parecer. A `catraca` (run 45695828717, mesmo head) barra por dois motivos: a mudança em `hooks/_comum.py` e `hooks/conformidade.py`, que espera o rótulo do dono (controle, R-CONFORMIDADE), e uma guarda dada como apagada em `hooks/_comum.py:2875(base)` (`critico is None and evento != 'PreToolUse'`); essa guarda foi reescrita no E7.23 (a4d12870), fora deste delta, como `recusa = evento != "PostToolUse" and (critico is not None or evento == "PreToolUse")`, com mutantes em `v0481-prazo-forge.json`. O aviso de valor esperado trocado no `test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada` não é do delta e não barra.
- Tamanho H1: o delta tem cerca de 45 linhas de código em `hooks/`, dentro do teto.

- ci: 4ab16b74a90aa0d9214d1a6c32764dfac9e7fe89 verde
