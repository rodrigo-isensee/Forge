---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-placar-fases
commit: c08aee63c9d6161a53a2ead78cf2af20551a1221
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-19
---
# QA: v0478 (E20.4), forge-placar `fases` e `--prs`

Escopo: `bin/forge-placar` (subcomando `fases`, opção `--prs` e linha `sem_teste:`), `tests/evals/test_placar.py`, mutantes M1 a M33 em `tests/mutantes/v0479-placar-fases*.json`, texto em `docs/melhoria-continua.md` e fragmento de changelog. Sem suíte local (a suíte inteira é do CI do PR, `R-QA`).

## Achados

## Critério → teste → resultado
Obrigações lidas do cabeçalho de `bin/forge-placar` e do fragmento de changelog (o pedido `docs/pedidos/v0478.md` não está neste clone).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `--prs`: contagem por semana ISO nas duas janelas | `SemTeste.test_dados_de_exemplo_por_semana` | PR aberto (mergedAt nulo) e PR fora da janela | passou |
| `--prs` ausente: `-`, nunca 0 | `SemTeste.test_sem_dados_sai_tracinho_nunca_zero` | sem fonte | passou |
| `--prs` lista vazia: "nenhum PR mesclado" | `SemTeste.test_lista_vazia_diz_nenhum_pr` | vazio | passou |
| `--prs` ausente, não JSON ou não lista: saída 2 | `SemTeste.test_arquivo_ausente_ou_invalido_sai_com_2` | três entradas inválidas | passou |
| `fases`: quatro fases, primeira rodada e total do dia | `Fases.test_fases_e_primeira_rodada_por_item_e_total_do_dia` | merge de dois pais (squash fica fora) | passou |
| `fases`: item sem parecer e assunto sem nome de branch | `Fases.test_item_sem_parecer_e_assunto_sem_branch` | sem parecer: `-` | passou |
| `fases`: dia sem item | `Fases.test_dia_sem_item` | vazio | passou |
| `fases`: total zero sem divisão por zero | `Fases.test_item_de_total_zero_nao_divide_por_zero` | zero | passou |
| `fases`: ref inexistente sai 2; padrões de `--dia` e `--git` | `test_ref_que_nao_existe_sai_com_2`, `test_sem_dia_vale_hoje`, `test_sem_git_vale_a_pasta_atual` | ref inválida | passou |
| `fases`: texto com meta de 85 min e primeira rodada | `Fases.test_texto_traz_a_meta_e_a_primeira_rodada` | n/a | passou |

## Cenários e resultado real
- Módulo `tests/evals/test_placar.py` com `python3 -I -m unittest discover -s tests/evals -p test_placar.py`: `Ran 35 tests ... OK`.
- Sonda manual no próprio repositório (`fases --git . --ref origin/develop --dia <último merge>`): 4 itens, fases e média coerentes (110 min contra meta de 85, primeira rodada 3/4). `--dia 2020-01-01`: "nenhum item mesclado", rc 0. `--dia xx`: rc 2. `--prs` com `{}`: "não é uma lista de PRs".
- Observação, não é defeito: item cujo 1.º commit já é de parecer sai com desenvolvimento 0 min, como o cabeçalho define.

## Vermelho antes do verde
`forge-testes --vermelho` não aceita módulo fora de `tests/` (`módulo sem arquivo em tests/: test_placar`, rc 2; o teste mora em `tests/evals/`) e a forma sem módulo não devolveu saída no prazo da sessão. Prova equivalente, manual, numa cópia em `$TMPDIR` com o HEAD e só `bin/forge-placar` da base `0c47762a`:

```
python3 -I -m unittest discover -s tests/evals -p test_placar.py
ERROR: SemTeste.test_sem_dados_sai_tracinho_nunca_zero
FAIL: Fases (8 testes) e SemTeste (test_arquivo_ausente_ou_invalido_sai_com_2 x3, test_dados_de_exemplo_por_semana, test_lista_vazia_diz_nenhum_pr)
Ran 35 tests ... FAILED (failures=13, errors=1)
```
Os 14 testes novos caem sem a implementação; os 21 anteriores seguem verdes.

## Mutação
`bin/forge-mutante --processos 4 tests/mutantes/v0479-placar-fases*.json` (5 specs, rev 2343148728af): rc 0, M1 a M33 todos `morreu`, nenhum sobrevivente, nenhum equivalente. M20 morreu por erro do teste declarado sob o mutante (passa sem ele), aceito: o mutante não passa.

`bin/forge-mutante --cobertura --base 0c47762a6a9d4453adfe0b8e244604a265c6bde3`: `base=0c47762a... mb=0c47762a... rev=23431487...`; todas as linhas listadas `coberta ... declarado, não provado` (bin/forge-placar:86, 191-208, 399, 536-643), nenhuma `sem mutante`, rc 0. Conferido contra o diff: as condições novas (SEM_TESTE, janela, mergedAt, parsing do git, fases, primeira rodada, divisão) têm mutante.

## Revalidação no head 42c2a906 (delta desde 2343148728af)
Delta lido (`forge-check parecer delta`): `bin/forge-placar` (squash do `forge-fechar` medido por `refs/pull/N/head`, linha `itens sem fases (squash)`, `--prs` com JSON aninhado fundo e `mergedAt` de dia inexistente saindo 2), `tests/evals/test_placar.py`, specs de mutantes 2, 4 e 6, changelog e `docs/melhoria-continua.md`.

| Critério novo | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Squash `(#N)` mede pelos commits do PR | `test_squash_mede_pelos_commits_do_pr_e_conta_a_parte_sem_eles` | com ref / sem ref no mesmo dia | passou |
| Dia só com squash sem ref não diz "nenhum mesclado" | `test_dia_so_com_squash_sem_ref_nao_diz_nenhum_mesclado` | vazio medido | passou |
| Dia sem squash não traz a linha | `test_dia_sem_squash_nao_traz_a_linha` | zero | passou |
| `--prs` mergedAt inválido e aninhamento fundo: rc 2, sem Traceback | `SemTeste.test_arquivo_ausente_ou_invalido_sai_com_2` (casos c e d) | data 2026-13-45; 100000 colchetes | passou |

- `python3 -I -m unittest discover -s tests/evals -p test_placar.py`: `Ran 38 tests ... OK`.
- `bin/forge-mutante --processos 4 tests/mutantes/v0479-placar-fases*.json` (rev 42c2a906363b): rc 0, 41 mutantes, todos `morreu`, nenhum sobrevivente.
- `bin/forge-mutante --cobertura --base 0c47762a...`: rc 0, 36 linhas `coberta`, nenhuma `sem mutante`.
- `bin/forge-mutante --base 2343148728af2cf625c63ac236290daa2344d29b tests/mutantes/v0479-placar-fases*.json`: `base=2343148728af... rev=42c2a906363b...`, rc 0, 41 `morreu`.
- Vermelho antes do verde: os novos testes de squash exercem comportamento ausente em 2343148728af (a linha `sem_fases` e a medição por `refs/pull/N/head` não existiam); os mutantes novos (M35 a M41) morrem apenas porque os testes caem sem a guarda. Sem suíte local.

## Revalidação no head c08aee63 (delta desde b8fb44f6)
Delta lido (`forge-check parecer delta`): `bin/forge-placar` (`fundo_demais`, teto próprio de 64 níveis de `[` e `{` fora das strings, saída 2 em qualquer versão do Python, sem o `RecursionError`), `SemTeste.test_aninhamento_no_teto_e_colchete_em_string_passam`, specs de mutantes 6 (M34 reescrito) e 7 (M42 a M44) e changelog.

| Critério novo | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Aninhamento 64 passa, 65 sai 2 com a mensagem do teto | `test_aninhamento_no_teto_e_colchete_em_string_passam` | máximo e logo acima | passou |
| Colchete e chave dentro de string não contam | mesmo teste | 1000 `[` e `{` em string com `\"` | passou |

- `python3 -I -m unittest discover -s tests/evals -p test_placar.py`: `Ran 39 tests ... OK`.
- `bin/forge-mutante --base b8fb44f6 tests/mutantes/v0479-placar-fases-6.json tests/mutantes/v0479-placar-fases-7.json`: `base=b8fb44f6f086... rev=c08aee63c9d6...`, rc 0, M34 a M44 todos `morreu` (11), nenhum sobrevivente.
- Vermelho: `bin/forge-testes --vermelho` estourou o prazo da chamada; vermelho feito à mão em cópia de HEAD com `bin/forge-placar` de b8fb44f6: o teste novo falha (`AssertionError: 0 != 2`, 65 níveis não é recusado), e passa no HEAD.
