---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-mutantes-ci
commit: c965ed6c98d77ab9c70114f16cecaa73e55262ce
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.67, melhoria/v0475-mutantes-ci)

Escopo: condição do dono no #641 (linha de 2026-11-17 19:46 do pedido), mutantes das guardas do CI que faltaram. O diff contra a base 2fa505d7 só traz testes, specs e o fragmento: `tests/test_falhas_no_resumo.py` (+147), `tests/test_forge_tamanho.py` (+11), três specs em `tests/mutantes/` e `changelog.d/`. Nenhum código de produção muda.

## Achados
- A1 (recomendado) tests/mutantes/v0475-mutantes-ci-1.json:144 · as isentas de suite-partes (144 e 149) repetem as de v047-ci-rapido-4.json; a mesma condição só admite uma, então `--cobertura` sai rc 2 contra a develop e no intervalo do #615 (S1, S2). Basta apagar as duas.
- A2 (recomendado) changelog.d/v0475-mutantes-ci.md:2 · cita tests/test_ci_falhas.py, que c965ed6c removeu; os testes estão em tests/test_falhas_no_resumo.py e tests/test_forge_tamanho.py.
- A3 (recomendado) tests/test_falhas_no_resumo.py:389 · o subprocesso usa o ambiente herdado e `python3` do PATH; use `env=` limpo e `sys.executable`, como o teste da linha 181.
- A4 (recomendado) tests/test_falhas_no_resumo.py:1 · tests/*.py somam 158 linhas, acima da orientação de 150 (M14); o PR, quando abrir, traz `teto: excedido, 158 linhas, <motivo>`.

## Sondas
- S1 · `bin/forge-mutante --cobertura --base 2fa505d7` no head c965ed6c · espera: rc 0 (diff só de testes e specs) · obtido: rc 2, isenta que não cruza condição listada (falhas-no-resumo e as duas de suite-partes)
- S2 · `--cobertura --base 63691c5c^` numa cópia sintética (scripts do #615 e specs no estado do head) · espera: rc 0 ou só `apagada` · obtido: rc 2 com as duas isentas de suite-partes; sem elas, rc 1 com apenas `apagada · scripts/suite-partes.py:121(base) · partes`

## Pergunta do brief: a condição apagada `if partes:` (scripts/suite-partes.py:121 na base) bloqueia?
Não bloqueia. A condição ficava em `pesos_por_modulo`, função que o #615 (63691c5c) apagou inteira e que hoje não existe na develop. Não há código para mutar nem comportamento para provar. A remoção da função já tem isenta com motivo em `tests/mutantes/v047-ci-rapido-4.json` (trecho `k.startswith(nome + ".")`), e a mesma explicação vale para a segunda condição dela. A isenta própria não é aceita: o nó é `partes`, com 6 caracteres, e a ferramenta exige trecho de 8 ou mais dentro do nó. É limite da ferramenta, não falha da entrega. Nenhum portão do merge confere esse intervalo: o CI roda `--conferir --todas`, e não `--cobertura`. Correção da premissa: a cobertura do diff real contra a develop não sai vazia. Ela sai rc 2 pelas isentas repetidas (A1, S1).

## Ferramentas (citadas, não refeitas)
- Mutantes: `bin/forge-mutante` com as 3 specs no head c965ed6c, 2 processos: 38 de 38 morreram, rc 0.
- `bin/forge-mutante --conferir --base 2fa505d7`: rc 0. O `--conferir --todas` acusa z075-uma-delegacao-por-branch M6 e M7, e o mesmo acontece na origin/develop (3d8ad440). Não vem deste diff.
- Testes do diff: `python3 -m unittest tests.test_falhas_no_resumo tests.test_forge_tamanho` deu 67 OK. Suíte inteira: sem PR, logo sem CI ainda; fica para o CI do PR.

## Parecer
Aprovado. Os 38 mutantes têm teste de comportamento do ramo de falha e todos morrem. As guardas do `falhas-no-resumo.py` no intervalo do #615 ficam cobertas (S2: só sobra a apagada). O teste do corpo nulo do PR (MC38) prova a guarda de `pr_da_branch`. A1 a A4 são recomendados e não devolvem a entrega: A1 e A2 são correções de dado e texto que o autor faz antes do PR.
