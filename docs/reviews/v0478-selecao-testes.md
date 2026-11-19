---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-selecao-testes
commit: 95c7fc2ff9f42c6c071f7943b5424dd571f21562
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 (E18.3, seleção de testes)

Diff `0c47762a..53f89698`, 5 commits, um por comportamento: `forge-testes --vermelho` com progresso e os módulos do diff primeiro (VERMELHO-COM-PROGRESSO), conjunto mínimo no lugar da contagem fixa do `forge-check` (DEFEITO-CONTAGEM-FIXA-FORGE-CHECK), o `CITA` aceita `BIN / "forge-check"` (CITA-BIN-BARRA), `suite-paralela.py --medir` e o fragmento do changelog.

## Parecer
Aprovado, sem achados.

- Tamanho (H1): 52 linhas de produção somadas (`bin/forge-testes` +16, `scripts/suite-paralela.py` +36), dentro do teto.
- `--medir` contra o `R-TETO`, como o autor pediu: ele não pega a trava da suíte (`FORGE_SUITE_TRAVA`) e não grava o carimbo da prova da suíte, o que está certo, porque roda um módulo só e não é a suíte que o `R-TETO` manda rodar uma por vez. A trava de máquina continua valendo: sondei `hooks/pesado.py` no head e `pesado("python3 scripts/suite-paralela.py --medir test_forge", PESADOS_DO_FORGE)` e `pesado("scripts/suite-paralela.py --medir test_a", ...)` devolvem `True` (o padrão casa por prefixo, com qualquer argumento). Chamado por um agente, o `--medir` entra na fila do `pesado` como a suíte e não roda junto com ela. Na prática é mais conservador que o teste dirigido (`bin/forge-testes`, classificado pelos argumentos), sem defeito. A frase "não pega a trava da suíte" na docstring é exata.
- `medir()`: o módulo desconhecido sai 2 antes de rodar, o vermelho e a guarda de completude e da árvore (`conferir_completude` e `conferir_arvore` dentro de `rodar_partes`) saem 1 sem regravar, o sinal sai com 128+n, e o `gravar_pesos` mescla o novo peso sem apagar os pesos dos outros módulos (o teste confere `test_b` e `test_c` intactos).
- `--vermelho`: `modificados`, `inicio` e `time` já existem no escopo. A ordem nova muda só a execução; a linha da saída segue em ordem alfabética, e o teste confere isso.
- Conjunto mínimo: prova o mesmo que a contagem fixa (todo módulo do `FORGE_CHECK` e dos evals de forma está no plano, e nada sobra além dos oráculos e do `test_indice_forge`), com um piso de 90 contra a lista vazia (checklist 11). Ele também acaba com o conflito que a contagem fixa causava a cada junção.
- `CITA`: `\bBIN` recusa `SBIN`, e o teste novo traz as formas aceitas e as recusadas. O `MapaDoForgeCheck` segue verde com a regex ampliada, então nenhum módulo novo ficou fora do mapa.
- Guardas do diff: as 5 de `medir()` e de `main()` e a ordem do `--vermelho` têm um mutante cada em `tests/mutantes/v0478-selecao-testes.json`, e os testes de subprocesso usam `-I` com o ambiente limpo do brinquedo.

Provas rodadas (máquina carregada: só os testes do diff, sem a suíte, que fica no CI do PR):
- `python3 -m unittest -k medir tests.test_suite_paralela`: `Ran 7 tests ... OK`.
- `python3 -m unittest tests.test_testes_tocados.MapaDoForgeCheck tests.test_testes_tocados.Mapa.test_forge_check_roda_os_modulos_dele tests.test_testes_tocados.Vermelho.test_vermelho_escreve_progresso_com_o_teto_e_os_modulos_do_diff_primeiro tests.test_forge.PesosDaSuite`: `Ran 6 tests ... OK`.
- `bin/forge-mutante tests/mutantes/v0478-selecao-testes.json` (rev 53f8969816a5): M1 a M6 morreram.

## Revalidação no head 95c7fc2f (E18.11)
Aprovado. Delta lido só por `forge-check parecer delta` (intervalo `53f89698..95c7fc2f`, sem o que veio da develop): no domínio só `bin/forge-testes`, cuja mudança é a da develop (`test_promocao_por_marca`, `test_fc_pr_parecer_forjado` e `test_filtros_l08_g2_ancora` no `FORGE_CHECK`); `git diff c720891e 95c7fc2f -- bin/forge-testes` não a traz. `tests/test_suite_paralela.py` fica com o QA.
- Conflito de `tests/test_testes_tocados.py` pelo lado da branch: a develop só subia a contagem fixa de 99 para 102; o conjunto mínimo da branch cobre os 3 módulos novos sem número. O arquivo no head é igual ao de `8a456181`.
- Prova: `python3 -m unittest tests.test_testes_tocados.MapaDoForgeCheck tests.test_testes_tocados.Mapa.test_forge_check_roda_os_modulos_dele` no head 95c7fc2f: `Ran 4 tests ... OK`. Suíte inteira: CI do PR.
