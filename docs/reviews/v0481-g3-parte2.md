---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g3-parte2
commit: 91e3d5fe4cbfae0a7e99bdb6e1e6bd6a1aebd23f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E28.7, #927, F2 partes 2 e 3)

## Achados
- A1 (recomendado) bin/forge-check:8543 · o `passo_do_item` (forge-check proximo) ainda manda "conferir a entrega do head" antes dos portões, embora review e QA agora leiam o CI sem esperar a conferência (G3-ENTREGA-PELO-CI); o passo poderia apontar os portões e deixar a conferência para o merge.
- A2 (recomendado) skills/briefs-e-conferencia/SKILL.md:19 · "Opções e D2: `conferencia-da-entrega.md`" ficou velho: no Forge o D2 saiu; trocar por "Opções e prova do pronto".

## Parecer
Aprovado. Diff contra o Base-sha 346a7860: 2 commits, 45 linhas de código em `bin/forge-check` (H1 dentro do teto), mais testes, specs de mutante, skill e fragmento de changelog.

- Faz o que o E28.6 pede, sem mais: o brief de código do Forge troca o `PQ_DO_D2` pelo `PQ_DO_CI`; a linha dos testes afetados diz que é só para se guiar; a `LINHA_LE_O_CI` diz que o CI do head basta; a `prova_do_ci` lê o `title` e reprova a linha da etapa do brief (reusa `forge_pronto.TITULO_DO_BRIEF`, sem regra nova, conforme a decisão técnica de 26/11 20:33) e exige em pass os `JOBS_DO_AGREGADOR` via `checks_ruins(..., mais=)`.
- `JOBS_DO_AGREGADOR` conferido contra `.github/workflows/ci.yml:856` (`needs: [bateria, pareceres, verificacoes, partes-doze, pulados-doze]`): passos, verificações longas, teto de pulados 3.12 e as 5 partes 3.12; `pareceres` fica fora (CHECKS_FORA_DA_LINHA_DO_CI). O teste `test_os_jobs_do_agregador_sao_os_needs_do_job_bateria_do_ci` amarra os dois e afirma mínimo de 8 (checklist 11).
- O afrouxamento fica só no `--previo`: `conferencia_do_head` devolve [] com aviso no stderr; `pr` sem `--previo`, o hook `parecer` (lê o resultado gravado só fora do `--previo`) e o `forge-fechar` seguem exigindo. Nenhum hook nem o `.githooks/pre-push` chama `pr --previo`. PR com rótulo `afrouxa-regra` e a seção do que afrouxa.
- Falso do gh (`ProvaDoCi.prova`) responde só a `pr view melhoria/x` e `pr checks 9`, nome exato (checklist 12); título não-str (None, 7) coberto.
- Commits em Conventional Commits, português, escopo e etapa.

## Provas
- `python3 -m unittest tests.test_forge_pronto tests.test_pre_envio_brief` no 91e3d5fe: Ran 73 tests, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0481-g3-parte2.json`: M1 a M8 morreu (M4 por erro: título 7 quebra o `.search`, o que é o comportamento que a guarda evita).
- `bin/forge-mutante --cobertura --base 346a7860515c8b74506aa160e198e2b73d4020b1`: guardas 1803, 10751 e 10752 cobertas; specs editadas lote-l08-e7 (M29, M30 com o `previo` e um teste a mais) e v0481-d2-no-brief (M8 no novo comentário) sem perda de guarda.
- CI no 91e3d5fe (run 45920800632): todos os checks em pass ou skipping fora `bateria (pareceres)` (falta o parecer) e `bateria` (log do agregador: "passos: success; pareceres: failure; verificações: success; partes: success; pulados: success"); `catraca` em pass. Nenhum vermelho vem do código.
- ci: 91e3d5fe4cbfae0a7e99bdb6e1e6bd6a1aebd23f verde
