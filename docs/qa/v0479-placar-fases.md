---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-placar-fases
commit: 2343148728af2cf625c63ac236290daa2344d29b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
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
