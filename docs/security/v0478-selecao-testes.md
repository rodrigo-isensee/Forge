---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-selecao-testes
commit: 53f8969816a5d1d2c0f4d2db3a1172ae0322010d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E18.4, melhoria/v0478-selecao-testes)

Primeira rodada. Lido: `git diff 0c47762a..53f89698` inteiro (bin/forge-testes, scripts/suite-paralela.py, tests/test_testes_tocados.py, tests/test_suite_paralela.py, tests/test_forge.py, docs/devops/suite-paralela-d4.md; a spec de mutantes e o changelog só por forma).

Gatilhos: controle do Forge (seleção de testes do envio e do autor em `bin/forge-testes`; pesos e trava da suíte em `scripts/suite-paralela.py`, R-TETO).

## Conclusão
**Contagem fixa virou conjunto mínimo (`tests/test_testes_tocados.py:79-89`) e não afrouxa.** O teste antigo fixava 99 módulos. O novo exige cada módulo de `FORGE_CHECK ∪ EVALS_DE_FORMA` no plano (`assertIn` um a um) e nenhum extra além dos oráculos e de `test_indice_forge`. Com isso, o plano fica igual ao mapa, e o piso de 90 barra o mapa vazio. A contagem é que pinava o tamanho do mapa. Esse papel agora é de duas âncoras externas ao mapa. A primeira é `MapaDoForgeCheck.test_mapa_lista_todo_modulo_que_usa_o_forge_check` (`:994-999`), que exige `FORGE_CHECK` igual ao conjunto que cita ou importa o script. A segunda é a lista literal de `:90-92` e a lista exata do `bin/forge-changelog` (`:59`), que pina `EVALS_DE_FORMA`. A sonda S1 tira um módulo do mapa e as duas âncoras reprovam.

**O CITA ampliado (`:953-955`) só aumenta o conjunto `usam`.** Assim, a igualdade com o mapa fica mais exigente, não menos. O teste novo (`:986-993`) prova as formas aceitas e recusa `SBIN /`, outro script e o `.py`.

**`--medir MÓDULO` (`scripts/suite-paralela.py:922-947`).**
- O nome só é aceito se estiver na lista de `modulos()`. `../test_a` e `test_a.T` saem 2 sem rodar (teste `test_medir_modulo_que_nao_existe_sai_2_sem_rodar_nem_gravar`).
- Regrava pesos só com verde e com a guarda de completude e da árvore (`rodar_partes`, `:850-851`).
- Não grava o carimbo K6 (`gravar_carimbo` só é chamado em `fechar_verde`, `:897-898`). Por isso um módulo verde não vira "suíte verde" no `reuso` (`:425`).
- Os pesos só mudam a divisão, e `conferir_particao` e a completude já a conferem. Peso adulterado ou JSON truncado não muda o veredito.
- Ficar sem a trava é coerente com R-TETO ("a suíte inteira roda uma por vez"): o módulo roda num processo, como o teste dirigido do autor.
- Gravar ao mesmo tempo que um `FORGE_SUITE_MEDIR=1` pode perder uma atualização de peso, mas sem efeito de segurança.

**Progresso do `--vermelho` (`bin/forge-testes:752-754,813-824`).** Só ordena e escreve no stderr. O conjunto de módulos e a saída (stdout) não mudam, e o teste novo confere a linha da saída em ordem alfabética.

## Achados
- A1 (recomendado) scripts/suite-paralela.py:922 · Sem teste que prove que `--medir` verde não grava o carimbo K6 (forge-suite-verde): um ajuste futuro que reuse fechar_verde faria um módulo verde valer como suíte verde no reuso local. Correção: no teste do medir verde, assertar ausência do carimbo.

## Sondas
- S1 · cópia de `bin tests scripts` do head com `"test_anotar"` tirado de `FORGE_CHECK` em `bin/forge-testes`; `python3 -I -m unittest discover -s tests -p test_testes_tocados.py -k test_forge_check_roda_os_modulos_dele -k test_mapa_lista_todo_modulo_que_usa_o_forge_check` · espera: as duas reprovam · obtido: `FAILED (failures=2)` (`'test_anotar' not found` e `faltam no mapa FORGE_CHECK: ['test_anotar']`)

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas: leitura do diff, a sonda S1 e os testes novos. `discover -s tests -p test_suite_paralela.py -k medir` deu 7 OK. `-p test_testes_tocados.py -k test_forge_check_roda_os_modulos_dele -k MapaDoForgeCheck -k progresso` deu 5 OK. A suíte inteira roda só no CI do PR e não foi rodada aqui. Não há segredo, dependência nem workflow no diff.
