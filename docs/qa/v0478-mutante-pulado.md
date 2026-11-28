---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-mutante-pulado
commit: c3cbb941c7bbd8967203ab3d7d2b071ba6f29261
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (mutante pulado, E13.4)

Escopo: `bin/forge-mutante` (teste declarado pulado sai `sem veredito`, saída 2, nunca `sobreviveu`), `tests/test_forge_mutante.py` e `tests/mutantes/v0478-mutante-pulado.json`. Sem suíte local: só o módulo tocado, com TMPDIR; a suíte inteira é do check-run `bateria` do CI.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| DEFEITO-MUTANTE-PULADO-SOBREVIVE: pulo sem morte é sem veredito | `Veredito.test_teste_declarado_pulado_e_sem_veredito_e_nunca_sobreviveu` | pulo em classe, em teste único e em subTest, com e sem `erro_mata` | passou; vermelho na base (asserção) |
| Pulo não esconde morte, erro de outro teste nem teste que não rodou | `Veredito.test_pulo_nao_esconde_a_morte_nem_o_teste_que_nao_rodou` | falha ou erro junto do pulo | passou (guarda de regressão; passa na base, esperado) |
| Saída 2 de ponta a ponta, equivalente com pulo não confirma, sobrevivente sem pulo segue 1, morte segue 0 | `Execucao.test_teste_pulado_sai_2_sem_veredito_e_o_sobrevivente_segue_1` | classe e teste único declarados; equivalente; controle com pulo | passou; vermelho na base (asserção) |

## Provas
- Módulo `tests/test_forge_mutante.py` (TMPDIR, `python3 -I -m unittest discover -s tests -p test_forge_mutante.py`): `Ran 137 tests`, `OK`.
- `bin/forge-testes --vermelho 4182a6b9 --modulos tests.test_forge_mutante`: `contagem: não prova (passa na base)=135; prova (asserção)=2`; `...test_teste_declarado_pulado_e_sem_veredito_e_nunca_sobreviveu · H=ok · B=falha · prova (asserção)`.
- `bin/forge-mutante tests/mutantes/v0478-mutante-pulado.json`: P1, P2, P3, P7, P4, P5, P6 todos `morreu` (saída 0); linhas 290, 312, 316, 316, 869, 883, 884.
- `bin/forge-mutante --cobertura --base 4182a6b9`: `coberta` para 289, 312, 316, 869 e 883, sem condição sem mutante.

## Cenários e resultado real
Diff lido contra a lista de guardas: a troca do controle (`ok` para `sem veredito`), o ramo do pulo no mutante, o `pulado_de` e o ramo final do `veredito` têm mutante declarado. A remoção da asserção antiga (`pulado` igual a `inválido`) é coerente com o novo contrato. Nenhum bug aberto.

## Revalidação (E13.8, delta 8186cef3..c3cbb941)
Delta lido por `forge-check parecer delta`: `bin/forge-mutante` (morte provada vale com outro declarado só pulado), `scripts/placar-mutacao.py` (coluna `sem-veredito-pulado`), `tests/test_forge_mutante.py`, as duas specs e o fragmento do changelog. O mutante P2 teve o trecho reescrito para o novo ramo e segue morrendo; Q1, Q2, Q4, Q5 e Q6 cobrem as guardas novas (A1 e A2 do review), uma por linha mudada.

### Provas
- `bin/forge-mutante tests/mutantes/v0478-mutante-pulado.json tests/mutantes/v0478-mutante-pulado-2.json` (rev=c3cbb941c7bb), saída 0: P1, P2, P3, P7, P4, P5, P6, Q1, Q2, Q4, Q5, Q6, todos `morreu`.
- Módulo `tests/test_forge_mutante.py` (TMPDIR): `Ran 138 tests`, `OK`.
- `bin/forge-testes --vermelho 8186cef3 --modulos tests.test_forge_mutante`: `contagem: não prova (passa na base)=136; prova (asserção)=2`; `...Veredito.test_morte_provada_vale_com_outro_declarado_so_pulado · H=ok · B=falha · prova (asserção)`.
- Não rodei `--cobertura --base` (trava R-TETO tomada por outra sessão); a conferência do diff contra os mutantes foi manual e não achou guarda mudada sem mutante.

Resultado: aprovado, nenhum bug aberto.
