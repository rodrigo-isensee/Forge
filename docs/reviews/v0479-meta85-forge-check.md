---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-forge-check
commit: dd6e111021f53ee783e47dc4649767d8f35289f8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E34.3 e E34.7, META85 na trilha do bin/forge-check)

## Achados
- A2 (recomendado) agents/jarvis.md:29 · o passo 5 do Jarvis ainda diz que a revalidação retoma quem deu o parecer, sem o filtro `revalida: sim` que a skill autor-ate-o-merge.md:10 passou a citar como "passo 5 do Jarvis".
- A3 (recomendado) tests/test_meta85_item_arquivos.py:22 · o subprocesso herda `os.environ` e roda o Python sem `-I`; use `ambiente_limpo()` como em test_meta85_entrega. A sonda com GIT_DIR e GIT_INDEX_FILE ruins ficou verde, então não há defeito provado.

## Parecer
Aprovado. Revisei o diff `eca1d21b..6853e0ee`: 18 arquivos, 7 contam no teto do item, e 96 linhas de código em `bin/` (H1, dentro do teto). Os três cartões seguem o desenho em `docs/propostas/meta85-forge-check.md`, e o corte em três cartões na mesma branch veio do dono (E34 no `## Escopo`).

- **Entrega com provas:** só a forma antiga cobra as provas. A conferência (`entrega --pedido`) recusa `--mutantes` e `--pronto`, e o teste cobre isso. A leitura do log é limitada por `TETO_DA_PROVA`, e a ferramenta só lê o log, nunca o roda. O PQ do `brief gerar` e o da volta trazem os dois logs.
- **Revalida:** chama o `commit_vale` com os mesmos livres, estritos, domínio e dispensados do `cmd_pr`, e a linha sai nos dois ramos de rc 0. Havia uma divergência de borda (A1, fechado na revalidação abaixo).
- **Classe:** `arquivos_do_item` reusa `e_teste`, `FRAGMENTOS` e `LIVRES`, sem regra nova. Com a base ilegível, a ferramenta não conta os arquivos e a classe já sai C (decisão testada). O `--json` traz a contagem.
- **ESCOPO+ (`bin/forge-testes`):** só põe os três módulos novos no mapa. O `test_testes_tocados` foi ajustado para 105.

Provas que rodei no head 6853e0ee:
- `python3 -m unittest tests.test_meta85_entrega tests.test_meta85_revalida tests.test_meta85_item_arquivos`: 22 OK.
- `bin/forge-mutante --processos 1` com as quatro specs: M1 a M21 morreram, rc 0.
- `bin/forge-mutante --cobertura --base eca1d21b`: rc 0, sem condição sem mutante.
- `tests.test_forge.AntiDuplicacao`, `test_metricas_texto`, `test_indice_forge` e `test_testes_tocados`: 185 OK, 1 pulado pelo sandbox (proc de outro namespace).
- `test_etapa_do_brief.PqDoExecutor` e `test_volta_por_delta.BriefDeVolta`: 31 OK.
- `forge-check classe --base eca1d21b --json`: classe C, `arquivos_do_item` 7, rc 0.

A suíte inteira fica para o CI do PR. Pela regra META85 do recomendado, A2 e A3 viram cartão depois do merge.

## Revalidação (E34.7, head 99f474bb)
Delta lido: `forge-check parecer delta docs/reviews/v0479-meta85-forge-check.md`, intervalo `6853e0ee..99f474bb`, `revalida: sim` (bin/forge-check mudou). No domínio: `bin/forge-check`, `tests/mutantes/v0479-meta85-forge-check-3.json`, `-5.json`, `-6.json`, `tests/test_meta85_item_arquivos.py` e `tests/test_meta85_revalida.py`; nada fora dele foi relido.

- **A1 fechado:** `veredito_do_parecer` (bin/forge-check:2043) é a fonte única do `cmd_pr` e do `revalida_do_parecer`; o `riscos-aceitos` sem o aceite agora sai `revalida: sim (este parecer barrou: ...)`, com teste nos dois sentidos (sem e com o aceite).
- **`cmd_pr` dá o mesmo veredito de antes, caso a caso:** (1) `riscos-aceitos` sem aceite: mesma linha `parecer:`, texto idêntico; (2) parecer que não aprova: mesma linha; (3) `commit:` ausente ou fora de `COMMIT` (`COMMIT.match("")` é falso): nada, como antes; (4) commit só de parecer (AQ-5): o motivo começa pelo sha, nunca por `desatualizado`, então cai direto em `commit: {paralelo}`, a mesma linha que o `continue` antigo emitia (o `continue` era o fim do laço); (5) domínio mudado: `commit_vale` com os mesmos argumentos e o mesmo pós-processamento E16; (6) válido: nada. Os `dispensados` só se calculam no review que aprova com `commit:` legível, o mesmo ramo de antes. A remoção do ramo `paralelo` do `cmd_pr` é equivalente: a checagem foi para o veredito (M26).
- **Teste da linha 50:** o `.get` faz a base falhar sem erro (KeyError virava erro, não falha); correto.
- **Mutantes M22 a M32:** um por guarda mudada; o M12 foi reescrito para a nova linha.

Provas que rodei no head 99f474bb:
- `bin/forge-mutante --processos 1` com as specs `-5` e `-6`: M22 a M32 morreram, rc 0; `--ids M12` na spec `-3`: morreu.
- `bin/forge-mutante --conferir --base eca1d21b`: trechos no lugar, rc 0.
- `bin/forge-mutante --cobertura --base 6853e0ee`: toda condição nova coberta; rc 1 só pelas duas linhas `apagada` da base (`tipo == 'review'` e `paralelo`), guardas que mudaram de lugar e têm o M28 e o M26.
- `python3 -m unittest tests.test_forge.AntiDuplicacao tests.test_metricas_texto tests.test_indice_forge tests.test_indice_fixtures tests.test_testes_tocados tests.test_meta85_revalida tests.test_meta85_item_arquivos`: 205 OK, 1 pulado pelo sandbox (proc de outro namespace).

## Revalidação (E34.11, head 06abb4fa)
Delta lido: `forge-check parecer delta docs/reviews/v0479-meta85-forge-check.md`, intervalo `99f474bb..06abb4fa`, `revalida: sim` (bin/forge-check mudou). No domínio: `bin/forge-check`, `tests/mutantes/v0479-meta85-forge-check-7.json` e `tests/test_meta85_revalida.py`; nada fora dele foi relido.

- **`base_sem_flag_do_pr` (bin/forge-check:1537):** extrai a condição que o `pr_da_cli` tinha em linha (branch de trabalho, fora de `BASES_DO_FLUXO`, e `base_do_delta(...)[0]` verdadeiro) e a entrega ao `pr_da_cli` (1570) e ao `revalida:` do `parecer delta` (3585). Mesma condição, mesmos argumentos: o `pr` sem `--base` dá a mesma resposta.
- **Equivalência provada:** `forge-check pr v0478` na versão `99f474bb` e na `06abb4fa`, no mesmo clone: stdout e stderr idênticos, rc 1 nos dois.
- **Testes novos (3):** base que já contém o head, fora da branch de trabalho pelo diff literal, e branch de trabalho achada pelo sha; os dois sentidos da guarda estão cobertos.
- **Mutantes M33 a M36:** morreram; um por guarda mudada.

Provas que rodei no head 06abb4fa:
- `python3 -m unittest tests.test_meta85_revalida tests.test_forge.AntiDuplicacao`: 12 OK.
- `bin/forge-mutante --processos 1` na spec `-7`: M33 a M36 morreram, rc 0.
- `bin/forge-mutante --cobertura --base 99f474bb`: as três condições novas (1541, 1542, 1570) cobertas por M35, M34 e M36.
- Tamanho: o `pr` acusa 169 linhas de código no item todo (H1); o teto excedido vai com justificativa no PR, fora desta revalidação.

## Revalidação (E34.15, head a281e4a5)
Delta lido: `forge-check parecer delta docs/reviews/v0479-meta85-forge-check.md`, intervalo `06abb4fa..a281e4a5`, `revalida: sim` (bin/forge-testes mudou). O delta é a junção com a develop (`5ae868eb`), com três conflitos resolvidos; nada fora do domínio foi relido.

- **`bin/forge-testes`:** a lista `FORGE_CHECK` do head tem 102 módulos: os 99 da develop mais `test_meta85_entrega`, `test_meta85_revalida` e `test_meta85_item_arquivos`; nenhum da develop sumiu, nenhum duplicado. `REAPROVEITAM_O_LOTE`, o `progresso` e o `vermelho` ficaram como na develop.
- **`tests/test_testes_tocados.py`:** idêntico à versão da develop (diff vazio); o conjunto mínimo substituiu a contagem fixa, e os três módulos meta85 entram no mapa sem contagem a ajustar.
- **`skills/briefs-e-conferencia/autor-ate-o-merge.md`:** um item de cada lado: "Uma volta por rodada" é o da develop (com a exceção de segurança, META85) e "Na revalidação, só é retomado..." é o desta branch; nenhum se perdeu.
- **Código do item:** `git diff 06abb4fa..a281e4a5` em `bin/forge-check`, nos três `tests/test_meta85_*.py` e nas specs `v0479-meta85-forge-check*.json` está vazio.

Provas que rodei no head a281e4a5:
- `python3 -m unittest tests.test_testes_tocados tests.test_meta85_entrega tests.test_meta85_revalida tests.test_meta85_item_arquivos`: 192 OK, 1 pulado pelo sandbox.

O parecer segue aprovado. A suíte inteira fica para o CI do PR.

## Revalidação (E34.19, head 19e81adc)
Delta lido: `forge-check parecer delta docs/reviews/v0479-meta85-forge-check.md`, intervalo `a281e4a5..19e81adc`, `revalida: sim` (bin/forge-check mudou). No domínio: `bin/forge-check`, `docs/propostas/meta85-forge-check.md`, `tests/pesos-d4.json`, três testes que citam o PQ e oito specs de mutante; nada fora dele foi relido.

- **`PROVAS_DO_PQ` (bin/forge-check:3217):** só troca o destino dos logs de `.forge/run/` para `${TMPDIR:-/tmp}/forge-mutantes.log` e `forge-pronto.log`; a lógica de `provas_da_entrega` não mudou, e a proposta foi alinhada ao texto novo.
- **Pesos:** `tests/pesos-d4.json` ganhou os três módulos `test_meta85_*`; `PesosDaSuite` confere.
- **Specs antigas:** só os trechos `de`/`para` mudaram, para o texto atual do `bin/forge-check`; nenhum mutante saiu (`ConferirTodas` verde).

Provas que rodei no head 19e81adc (`python3 -m unittest`):
- `tests.test_selo_e_entrega`: 119 OK.
- `tests.test_forge_dono`: 79 OK.
- `tests.test_forge.PesosDaSuite`: 1 OK.
- `tests.test_forge_mutante.ConferirTodas`: 4 OK.

O parecer segue aprovado. A suíte inteira fica para o CI do PR.

## Revalidação (E34.23, head dd6e1110)
Delta lido: `forge-check parecer delta docs/reviews/v0479-meta85-forge-check.md`, intervalo `19e81adc..dd6e1110`. No domínio: `tests/test_revisor_wt.py`, `tests/mutantes/z075-pr-previo.json` e `tests/mutantes/v0433-integracao-2.json`; `bin/` não mudou, então não há `revalida: sim` e nada fora dele foi relido.

- **Teste novo:** `PrPrevio.test_ausente_sem_base_e_sem_develop_o_diff_literal_leva_o_previo` apaga a `develop` (base None) e confere os dois sentidos: com `--previo` sai o aviso e rc 0; sem ele, a violação e rc 1. Cobre o ramo de falha do M7.
- **Specs:** o M7 de z075-pr-previo aponta para o teste novo; o I26 de v0433-integracao-2 lista só o `test_aq5_parecer_novo`.

Provas que rodei no head dd6e1110:
- `unittest tests.test_revisor_wt.PrPrevio tests.test_aq5_parecer_novo`: 16 OK.
- `bin/forge-mutante --processos 1 --ids M7 tests/mutantes/z075-pr-previo.json`: M7 morreu, rc 0.
- `bin/forge-mutante --processos 1 --ids I26 tests/mutantes/v0433-integracao-2.json`: I26 morreu.

O parecer segue aprovado. A suíte inteira fica para o CI do PR.
