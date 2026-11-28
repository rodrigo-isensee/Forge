---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-s5-cabecalho
commit: 6a3d08296b7c002f7cf52675efdfc07a0a67efc3
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 S5 (cabeçalho do parecer em `frente`), PR #917, volta 1 (delta ebc6690e..6a3d0829)

- ci: 6a3d08296b7c002f7cf52675efdfc07a0a67efc3 verde

Delta lido com `forge-check parecer delta`: `bin/forge_autorizacao.py`, `tests/test_autorizacao.py`, specs `v0481-s5-cabecalho` e `v0479-pv-a2-concessao-3/4`. A develop (f1e4f478, #918/#922) entrou sem conflito e fica fora do domínio.

## Conferência dos achados da 1.ª rodada
- A1 resolvido: a guarda apagada (`startswith('---\n')`) é isenta na spec, com motivo, coberta por M1 e por M18 de `v0479-pv-a2-concessao-3`. `forge-mutante --cobertura --base f1e4f478`: L221 M5, L256 M1/M18, L259 M2, L260 M4/M27 `coberta`; L252(base) `isenta`; nenhuma `apagada`.
- A2 resolvido: `tests/test_autorizacao.py:388` tem `FIXA = {`.
- A3 resolvido: M5 declara e cobre o novo bloqueio "Parecer sem cabeçalho legível" (L221), testado em `ItemPresoAoCommit.test_parecer_sem_fecho_anterior_ao_commit_barra_em_vez_de_sumir`.

## Resultado real
- `python3 -m unittest tests.test_autorizacao` · 33 testes, OK.
- `bin/forge-mutante tests/mutantes/v0481-s5-cabecalho.json` · rev=6a3d08296b7c; M1 a M5 morreram (M4 `(erro)`: o teste dá erro sob o mutante e passa sem ele). Nenhum sobrevivente.
- `bin/forge-mutante tests/mutantes/v0479-pv-a2-concessao-3.json tests/mutantes/v0479-pv-a2-concessao-4.json --base e216aa71cd0e` · `base=e216aa71cd0e` conferida; todos morreram (M18 e M27 inclusos; M27/M28 `(erro)`), nenhum sobrevivente, rc 0.
- CI no head (`gh pr checks 917`): verdes todas as partes da suíte (python 3.12 e 3.14, 5/5), `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `catraca`, instalação, teto de pulados e árvore provada. Não verdes: `bateria` e `bateria (pareceres)`, que esperam os pareceres (excluídos pela regra).
