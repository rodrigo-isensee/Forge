---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-d2-no-brief
commit: 7cacc94c8fe74c3fba5cd9368d5c388d1007b910
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E14.69, #903, D2-NO-BRIEF E14.51; classe C), 1.ª rodada completa

Diff lido: `34ab6714..7cacc94c`, contra o merge-base com a develop. A develop entrou com o #885 sem conflito. O diff toca `bin/forge-check`, `bin/forge_pronto.py`, `changelog.d/v0481-d2-no-brief.md`, `tests/test_forge_pronto.py`, `tests/test_pre_envio_brief.py`, `tests/test_selo_e_entrega.py` e três specs de mutante. O pedido é o brief tech-lead-178, com os itens (1) a (4) da ordem do dono de 25/11 07:52 e o cartão PR-TITULO-DO-BRIEF.

## Conferência
- **(1) Brief:** `montar_brief` põe o `PQ_DO_D2` no brief de código só quando `e_o_forge(raiz)` (`bin/forge-check:9943`). A PQ cobra `rc=0` e pede a última linha do pronto no relatório. O teste `test_codigo_do_forge_manda_rodar_o_d2_e_fora_do_forge_nao` cobre os dois ramos.
- **(2) Conferência da entrega:** `prova_do_pronto` (`:10447`) roda na etapa `codigo` (`:10622`). Usa o `forge-check` de quem confere, com `--raiz` na worktree, de modo que a branch não certifica o próprio portão. Rc fora de 0, timeout ou `OSError` reprovam com a última linha. `--so-leitura`, a falta de worktree e uma cópia fora do Forge não rodam e não reprovam, e a linha manda conferir o relatório do autor, como pede o "(ou lê a prova dele)" do brief. Não roda em dobro: o `bin/forge-check pronto` da PQ está fora da lista do `reexecutar-provas.py` (`comando_permitido`). `test_d2_vermelho_na_copia_do_forge_nao_cumpre` prova de ponta a ponta que a entrega não é gravada.
- **(3) Título do PR:** `TITULO_DO_BRIEF` casa `E<n>.<m> (papel):` no início ou `[branch ` em qualquer posição. Um título em Conventional Commits que cita `E3 (qa)` no meio passa, e o teste cobre esse caso. Com `corpo`, o `pr_da_branch` pede `title` ao `gh`, e as specs M18/M19 do v0474 foram realinhadas a isso (AR-12).
- **(4) Base velha:** `base_velha` compara a `version` do `plugin.json` na base com a do merge-base. Antes de comparar, busca a `origin/<ramo>`, com o ramo validado (alfabeto, sem `-` inicial nem `..`) e com `--end-of-options`. Sem rede, ou fora do Forge, não compara. A saída é uma linha, antes das checagens, como o brief pede.
- **Guardas e mutantes (V2):** são 13 guardas mudadas, cada uma com um mutante. `bin/forge-mutante --processos 1` com as duas specs, no head `7cacc94c`: M1 a M13 morreram. `--ids M18,M19` do `v0474-h1-ferramenta-3.json`: os dois morreram (`:9589`, `:9600`). `--cobertura --base 34ab6714`: cada guarda do diff está coberta, sem linha descoberta.
- **Testes do item:** `python3 -m unittest tests.test_forge_pronto tests.test_pre_envio_brief tests.test_selo_e_entrega tests.test_forge_tamanho`: 259 testes, OK (393 s), no head.
- **Tamanho (H1):** cerca de 90 linhas de código em `bin/` (50 + 41 no diffstat, com as docstrings), abaixo do teto. É um comportamento só: o D2 cobrado antes da entrega.
- **CI do head** (runs 45751592922 e 45753156934, em `7cacc94c`): as 10 partes da suíte em 3.12 e 3.14, os passos, a bateria em 3.14, as verificações longas, a instalação, o teto de pulados e a árvore provada estão verdes. Ficam fora três jobs, que esperam o parecer ou o rótulo:
  - `bateria (pareceres)`, pelo log: "PR toca bin/forge-check (e outros 1) sem parecer aprovado de review". É este parecer.
  - `bateria`: agrega a de pareceres (`pareceres: failure`, as outras em `success`).
  - `catraca`, pelo log: "R-CONFORMIDADE: mudança em bin/forge-check". É a classe C, que pede o rótulo do dono.
- ci: 7cacc94c8fe74c3fba5cd9368d5c388d1007b910 verde

## Achados
- A1 (recomendado) bin/forge-check:10444 · a conferência espera o pronto até 3600 s, mas o Bash do Jarvis em primeiro plano para em 600 s. Com testes afetados longos, o `forge-check entrega` precisa ir ao segundo plano com log até `rc=` (esperar-estado). Dizer isso na receita da conferência.
- A2 (recomendado) bin/forge-check:9718 · a PQ manda o autor rodar o `bin/forge-check pronto` da própria branch. Uma branch que quebra o pronto se aprova sozinha. O brief tech-lead-178 pedia o forge-check do clone -d2 da develop com `--raiz`. A conferência cobre isso, mas a PQ deve dizer o mesmo.
- A3 (recomendado) bin/forge_pronto.py:50 · cada marca de versão na develop (até 2 por dia) obriga todas as branches abertas a trazer a base antes da entrega, o que muda o "só na hora do merge" do R-FLUXO. Está no escopo do brief. Medir as voltas causadas por isso e registrar a exceção no R-FLUXO.

## Parecer
**Aprovado** no head `7cacc94c`. Os quatro itens do brief estão entregues, cada guarda tem mutante e teste do ramo de falha, os 13 mutantes e os 2 realinhados morrem no head, e o CI está verde fora dos três jobs que esperam o parecer ou o rótulo. A1 a A3 são recomendados e viram cartão depois do merge. Para o merge faltam os pareceres de QA e de segurança da classe C e o rótulo do dono, que a catraca exige.
