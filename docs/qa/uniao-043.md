---
tipo: qa
contrato: 1
pedido: versao-043
branch: melhoria/uniao-043
commit: c14db03f9b41c1b4b9952a0a289bbf6de333e4cf
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-08
---
# QA do delta da junção da 0.43 (E2.4)

Ambiente: `git archive c14db03f` em `.../scratchpad/j/` (com `git init` só na cópia, para o `forge-mutante`), python 3.12.3, sem tocar o repositório, sem worktree. Antes da rodada: `.githooks/pre-push --status` = "nenhuma suíte do Forge rodando" (rc 1) e load1 1,39. A suíte inteira não rodou (fora do escopo; o CI da PR roda).

## uniao-043

veredito: aprovado

- Sha revisado: c14db03f9b41c1b4b9952a0a289bbf6de333e4cf (= `origin/melhoria/uniao-043`; base origin/develop f84153b3).

### (1) Módulos tocados pelas resoluções de conflito (árvore integrada)
| Módulo | Resultado |
|---|---|
| tests.test_voltas | 36 testes, OK (1 skip: "o usuário ignora permissões de arquivo", `root`) |
| tests.test_forge_mutante | 83 testes, OK |
| tests.test_pre_push_trava | 49 testes, OK (3 skips: root escreve/lê onde o teste exige falta de permissão) |
| tests.test_sobreposicao_quadro (conflito do 1.º lote) | 60 testes, OK |
| tests.test_testes_tocados (conflito do 1.º lote) | 104 testes, OK |

Os skips são condicionais ao usuário `root` do ambiente e já existem nas branches de origem; nenhum teste foi marcado `skip` pela junção.

### (2) Módulos deixados para o QA do delta (Histórico de 09:11)
- tests.test_pre_push_parecer: 21 testes, OK.
- `tests.test_pre_push_curto` não existe como arquivo; o módulo é `tests/test_pre_push_parecer_curto.py` (nome do Histórico abreviado): 12 testes, OK.

### (3) Mutantes das specs dos arquivos com conflito (árvore integrada)
Specs rodadas, uma por vez (a `forge-mutante` recusa specs de pedidos diferentes numa só chamada), `--processos 3`: est-m11-retro (-1, -2, -3), d12-medida-e3a (-1, -2), d12-medida-e3b (-1, -2), est-m12-atributos (-1, -2), est-m12-estados (-1, -2), est-m12-gerar (-1 a -4), est-m12-montar (-1, -2), est-m12-secao-1, maq-a7-medida (-1, -2), z075-prepush-prova-arvore e z075-prepush-relogio (-1, -2): 23 specs, 158 mutantes declarados, 157 mortos, 0 sobreviventes nas specs, 1 spec inválida (A1). Todas com rc 0, menos d12-medida-e3a-2 (rc 2, "inválido", não "sobreviveu").
O mutante M16 da d12-medida-e3a-2 mira um trecho que o E3b reescreveu (A1). A mesma guarda (`c[5] != "sim"`, `bin/forge-check:4047`) é provada pelo M3 da d12-medida-e3b, morto na árvore integrada. Conferi à mão: o mutante `if cod or c[5] != "sim":` → `if cod:` morre com `MedidaDaRelease.test_c_menos_de_3_pequenos_na_atual_ou_sem_release_anterior_so_tabela` e sobrevive ao teste que o M16 antigo citava, então a guarda tem cobertura, só a spec do E3a ficou velha.

Saída resumida (log completo em `.../scratchpad/mut.log`): `rc=0` em 22 specs; `rc=2 tests/mutantes/d12-medida-e3a-2.json` (`M16 · inválido · bin/forge-check · o trecho aparece 0 vezes no arquivo`).

### Critério → teste → resultado
A junção não traz critério novo (os `CA-n` são dos pareceres por branch). Obrigações do delta:
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Resolução de conflito mantém os dois lados (voltas, mutante, trava, quadro, tocados) | os 5 módulos acima | n/a | passa |
| `test_pre_push_parecer` e `_curto` na árvore integrada | os 2 módulos | envio só de parecer | passa |
| Guardas das branches seguem provadas pelas specs | 23 specs rodadas, 157 mutantes mortos (inclui o M3 do E3b, que cobre o M16 do E3a) | guardas de `bin/forge-check`, `.githooks/pre-push` | morreram |

Vermelho antes do verde: não se aplica (a junção não acrescenta teste novo; os testes vêm das branches, com o vermelho nos pareceres delas). Teste de mutação no código alterado: ver (3).

## Achados
- A1 (recomendado) tests/mutantes/d12-medida-e3a-2.json:62 · M16 ('de': `len(c) >= 7 and c[5] == 'sim'`) não casa mais depois do E3b (`bin/forge-check:4047`); `forge-mutante` sai rc 2 nessa spec. Guarda coberta pelo M3 do d12-medida-e3b; apagar ou atualizar o M16 na 0.44.

## Parecer
Aprovado. Os cinco módulos de conflito e os dois do Histórico passam na árvore integrada, e os mutantes das specs morrem, com uma spec velha do E3a que não bloqueia (guarda provada pela spec do E3b).
