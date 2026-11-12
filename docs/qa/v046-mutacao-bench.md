---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/v046-mutacao-bench
commit: 203e3554785746c600bd590fddb807d930eaa7a2
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v046 E7.4 (mutação dirigida e medidas por versão)

Diff 8b5a44d5..60bba369: `bin/forge-mutante` (`--base SHA` com SPEC, M-1), `bin/forge-changelog release` (aviso M-5 e BENCH-POR-RELEASE), 2 specs de mutantes, testes, doc e fragmento.

## Critério -> teste -> resultado
| Obrigação (decisão do dono 12/11 11:06) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| M-1 roda só os mutantes do arquivo mudado; o resto sai `fora do diff` | `MutacaoDirigida.test_so_o_mutante_do_arquivo_mudado_roda` | mb..rev vs arquivo fora do diff | passa; cai na base |
| M-1: nenhum mutante no diff, saída 2, sem rodar | `test_nenhum_mutante_no_diff_sai_2_sem_rodar` | diff vazio para a spec | passa; cai na base |
| M-1: base inválida ou sem ancestral, saída 2 sem Traceback | `test_base_que_nao_e_commit_ou_sem_ancestral_sai_2` | base ilegível, histórico órfão | passa; cai na base |
| M-5/BENCH: aviso com a tag anterior, só no clone do Forge, sem mudar o código de saída | `ReleaseAvisaMedidasDaVersao` (4 testes) | com tag, sem tag, fora do Forge | passa; 2 caem na base |
| Nada no CI nem em `.githooks/` roda o placar | `test_nem_o_ci_nem_o_envio_rodam_o_placar` (mínimo de 3 fontes) | pasta vazia | passa; diff sem arquivo em `.github`/`.githooks` |

## Provas
- `python3 -m unittest tests.test_changelog`: Ran 73 tests, OK (9,5 s).
- `python3 -m unittest tests.test_forge_mutante`: Ran 105 tests, OK (98 s).
- Vermelho: base 8b5a44d5 (`git archive`) com os testes do head, classes novas: `Ran 7 tests, FAILED (failures=6)` (os 3 de MutacaoDirigida com 4 subcasos, e 2 de medidas). Os 2 restantes (fora do Forge, sem CI) afirmam ausência e passam na base por desenho. `forge-testes --vermelho 8b5a44d5` estourou o prazo de 590 s (rc 124, sem veredito); vale o vermelho manual acima mais a mutação.
- Mutantes: `forge-mutante` das 2 specs (M1..M10, 10 mutantes), `--processos 4`, rc 0, todos `morreu` (M1 :827, M2 :865, M3 :792, M4 :805, M5 :807, M6 :808, M7 :798, M8 :867, M9 changelog:217, M10 changelog:221).
- Cobertura: `forge-mutante --cobertura --base 8b5a44d5`: 9 condições `coberta` (M7 em :798 não aparece na lista, é linha de retorno, não condição); nenhuma linha de guarda sem mutante achada.
- Medida pedida pelo dono: o diff não toca `.github/` nem `.githooks/`; o CI do PR não ganha passo. Custo no teste: as 2 classes novas somam 2,1 s (7 testes), dentro dos 73 e 105 de cada módulo. O M-1 só roda a pedido (`--base`), o placar e o bench só imprimem aviso na release.
- O que só o CI do PR prova: a bateria completa no sha (check-run `bateria`) e o tempo de relógio do job antes e depois; localmente não há como comparar o job.

## Revalidação por delta 60bba369..e452582f (E7.8)
O delta amplia o `--base` (spec mudada e módulo de teste mudado entram no diff), cita a tag do aviso com `shlex.quote` e troca A1 por parênteses. Novas obrigações: S1/S2 (teste enfraquecido entre base e rev roda o mutante), spec mudada roda os seus mutantes, tag com metacaractere sai citada.
- `python3 -m unittest tests.test_changelog`: Ran 74 tests, OK (27,9 s).
- `python3 -m unittest tests.test_forge_mutante`: Ran 108 tests, OK (254,8 s).
- `forge-mutante` das 2 specs, `--processos 4`, rc 0: M1..M15 todos `morreu`; M11 :800 e M12 :800 (dois pedaços da mesma condição, cada um por um teste), M13 :802, M14 e M15 :821. Cada um morre só pelos `testes` declarados (o runner só conta esses), e cada teste exercita a ramificação do mutante: M11 e M14 pela spec mudada, M13 pelo teste enfraquecido (sobrevive M1), M12 pelo arquivo mudado, M15 pela spec fora do repositório.
- Cobertura `--base 8b5a44d5`: 11 condições `coberta`, nenhuma sem mutante. A linha nova `shlex.quote` (:222, não é condição) não aparece; sonda minha (Q1, `shlex.quote` removido, teste de metacaractere): `morreu`.
- A1 do parecer anterior: atendido (`or (args.base and not args.spec)`, spec M1 atualizada).
- Vermelho dos 3 testes novos de MutacaoDirigida e do de metacaractere: a base do delta (60bba369) não tem `modulos_do_teste` nem `shlex.quote`; a morte dos mutantes M11, M13, M14 e Q1 prova que o teste falha sem a lógica. `forge-testes --vermelho` não rodado (estourou prazo na rodada anterior).
- CI do PR: o delta não toca `.github/` nem `.githooks/`; o `bateria` do sha fica com o portão.

## Revalidação por delta e452582f..135b20d2 (E7.12)
`forge-check parecer delta` lista no domínio: `bin/forge-mutante`, `tests/test_forge_mutante.py`, `tests/mutantes/v046-mutacao-bench.json` e `-3.json`, `skills/qa-testing/SKILL.md`, `agents/qa-engineer.md`, `agents/tech-lead.md`, fragmento. Obrigações novas: arquivo de `tests/` fora de `test_*.py` e de `tests/mutantes/` põe todos os mutantes no `--base` (A4 da E7.7), e `test_*.py` ou spec mudados não põem.
- `python3 -m unittest tests.test_forge_mutante`: Ran 110 tests, OK (63,5 s; a medida do autor foi 70 s, antes 75 s). Fora do CI do PR: o delta não toca `.github/` nem `.githooks/` (diff vazio).
- `forge-mutante` das 3 specs (`-bench`, `-2`, `-3`; não existe `-1`), `--processos 4`, rc 0, M1..M20 todos `morreu` (32 s). M16 :830 (`if apoio:`), M17 :835 (`spec_mudou or bool(apoio)`), M18 :810, M19 :811, M20 :812 (os três termos de `apoio_de_teste`); M5 com o `de` atualizado morreu em :835.
- `forge-mutante tests/mutantes/v046-mutacao-bench-3.json --base e452582f`: linha `base=e452582f... rev=135b20d2...` confere com o head aprovado; M16..M20 `morreu`.
- Cobertura `--cobertura --base 8b5a44d5`: 13 condições/linhas `coberta` (:801, :810, :819, :830, :834, :835, :837, :840, :859, :897, :899, changelog :218 e :222), nenhuma sem mutante; as 3 linhas novas de `apoio_de_teste` e o `if apoio` têm M16..M20.
- Caso positivo (S2): `test_helper_de_tests_enfraquecido_poe_todos_os_mutantes_no_diff` em cópia da base e452582f com o teste do head: FAILED (falta a linha `apoio de teste no diff`), logo prova a correção; o helper enfraquecido faz M1 sobreviver (rc 1) no head.
- Caso negativo: `test_teste_e_spec_de_outro_mutante_nao_poem_todos_no_diff` passa na base por desenho (afirma ausência); a prova dele é a morte de M18, M19 e M20, que o tornam vermelho. `test_*.py` e `tests/mutantes/*.json` mudados deixam M2 `fora do diff`.
- `forge-testes --vermelho` não rodado (estourou o prazo antes); vale o vermelho manual e a mutação.
- Citação da `--base` e do bench por versão em `skills/qa-testing/SKILL.md`, `agents/qa-engineer.md` e `agents/tech-lead.md` lida no diff: coerente com o `forge-mutante` (linha `base=`, head já aprovado, placar e bench nunca no PR). O `bateria` do sha fica com o portão.

## Revalidação por delta 135b20d2..203e3554 (E7.16)
`forge-check parecer delta` lista no domínio: `agents/qa-engineer.md`, `agents/tech-lead.md`, `skills/qa-testing/SKILL.md`, `bin/forge-mutante`, specs `v046-mutacao-bench.json` e `-3.json`. Mudança de código: só `apoio` virou `apoio_mudado` em `dirigir` (:829-835, renomeação sem efeito de lógica, mesmos termos); `de` de M5, M16 e M17 acompanharam. O texto dos 3 arquivos de instrução foi enxugado sem tirar obrigação (mutante por linha de guarda, `--base`, `base=`, placar e bench por versão, `AR-<n>`).
- `python3 -m unittest tests.test_forge_mutante`: Ran 110 tests, OK (95,3 s).
- `python3 -m unittest tests.test_orcamento_instrucao`: Ran 8 tests, OK. `python3 -m unittest tests.test_metricas_texto`: Ran 2 tests, OK.
- `forge-mutante` das 3 specs, `--processos 4`: M1..M20 todos `morreu` (M5 :835, M16 :830, M17 :835 com os `de` novos).
- `forge-mutante <3 specs> --base 135b20d2`: `base=135b20d23a95... rev=203e3554785746c600bd590fddb807d930eaa7a2` confere com o head aprovado; M9 e M10 `fora do diff`; M1..M8 e M11..M20 `morreu`.
- Cobertura `--cobertura --base 8b5a44d5`: 13 linhas `coberta` (:801, :810, :819, :830, :834, :835, :837, :840, :859, :897, :899, changelog :218 e :222), nenhuma sem mutante.
- Vermelho: o delta não traz teste nem regra nova (renomeação e texto); a prova de que o teste cai sem a lógica segue a da E7.12 (mutantes M16 e M17 mortos pelo mesmo teste).
- Instrução: citações lidas no diff, coerentes com o `forge-mutante`; o orçamento é conferido por `tests.test_orcamento_instrucao` (OK). O `bateria` do sha fica com o portão; o delta não toca `.github/` nem `.githooks/`.
- Formato: o `## Achados` anterior tinha prosa e saía fora do formato do `forge-check docs`; agora é bloco vazio (parecer aprovado), e a prosa dos achados fechados vai aqui: A1 da E7.4 atendido (bin/forge-mutante:859), sonda S2 da E7.7 virou teste (tests/test_forge_mutante.py:1294).

## Achados
