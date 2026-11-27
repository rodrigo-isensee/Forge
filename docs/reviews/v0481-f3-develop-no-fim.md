---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f3-develop-no-fim
commit: fe299c72efb4b606ccda44423ac9a241d157c38e
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E30.2, F3 develop só no fim, #924)

1ª rodada completa sobre `fe299c72` (Base-sha `ee05ee84`): 1 commit, 8 arquivos, 7 linhas de código (`bin/forge-check` +4/-3, `bin/forge-fechar` +1 de comentário), dentro do teto H1.

## Achados
- A1 (bloqueante) skills/trabalho-em-paralelo/ritmo-e-corte.md:20 · cita `bin/forge-fechar` entre crases sem argumento; o `test_comando_pronto` reprova ("forge-fechar: sem argumento nem opção") e a suíte parte 3/5 fica vermelha no CI do head (3.12 e 3.14). Cite com os argumentos (`bin/forge-fechar <pedido> --ref <branch>`).
- A2 (recomendado) skills/trabalho-em-paralelo/ritmo-e-corte.md:21 · "byte à mão no merge o desatualiza" vale só para arquivo `codigo` do domínio; `.md` de classe texto/forma e arquivo fora do domínio mudados à mão no merge não desatualizam (bin/forge-check:939, EST-M4). Diga "byte à mão em código do domínio", também em docs/fechamento-integrador.md:22.
- A3 (recomendado) docs/regras/R-FLUXO.md:26 · ainda lista "base velha" como exceção para trazer a integração antes do merge; com o F3 o pronto só avisa e a base entra no 2b. Alinhe o texto da regra (ADR/R-DECISAO se for o caso).
- A4 (recomendado) tests/mutantes/v0481-d2-no-brief.json:32 · M3 e M5 apontam para `test_marca_depois_do_nascimento_manda_trazer_a_base_sem_rodar_as_checagens`, renomeado neste diff; M5 também descreve a guarda que deixou de reprovar. Aponte para o teste novo ou registre a troca.

## Sondas
- S1 · `python3 -m unittest tests.test_comando_pronto` no fe299c72 · espera: OK · obtido: FAILED, `ritmo-e-corte.md:20 forge-fechar: sem argumento nem opção`

## Conferência
- ci: fe299c72efb4b606ccda44423ac9a241d157c38e vermelho: `suíte (python 3.12, parte 3/5)` e `suíte (python 3.14, parte 3/5)` em fail (run 45911883182, `test_comando_pronto`), `bateria (python 3.14)` fail por elas; as outras partes, instalação, verificações longas, passos e catraca verdes.
- Testes do item, rodados localmente: `tests.test_forge_pronto.BaseVelha` e `tests.test_fechar_forge_check_real.DevelopSoNoFim`, 6 testes OK.
- Mutantes declarados (`bin/forge-mutante tests/mutantes/v0481-f3-develop-no-fim.json`): F3-1 morreu (bin/forge-check:1241), F3-2 morreu (bin/forge-check:1244). A guarda mudada (o `if velha :=`) tem mutante e teste do ramo.
- Merge limpo estrito: para arquivo `codigo` do domínio, o `forge-check pr --base` compara a árvore do head com o `git merge-tree` do patch revisado sobre a base (`arquivos_divergentes`); conflito diverge, salvo o `CHANGELOG.md` (trechos, regra anterior). O 2b grava a árvore do `merge-tree`, e o teste `test_o_2b_traz_a_base_uma_vez...` confere pais e árvore; `test_merge_da_base_com_mudanca_a_mao...` prova o byte à mão em código. Ressalva da classe texto: A2.
- `base = ancora` no pronto: `forge-testes --registros`/`--afetados` e `forge-changelog conferir` aceitam sha (o `buscar_base` não busca sem `origin/`, o `merge-base` resolve); o teste prova as duas bases.

## Parecer
Reprovado só por A1: defeito provado que deixa o CI do head vermelho. A mudança de comportamento é pequena, correta e coberta (aviso no lugar da reprovação, checagens contra o ponto de partida, 2b como único ponto de entrada da base, parecer que vale no head com a base pelo merge simulado). A2 a A4 são recomendados e viram cartão depois do merge. Na volta, corrija a citação, rode `tests.test_comando_pronto` e envie; revalido pelo delta.
