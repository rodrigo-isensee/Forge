---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-mutante-lote
commit: b11631b2e9e536b11b918c470f7e80c9147b83ec
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E17.2, melhoria/v0478-mutante-lote)

Diff `0c47762a..b11631b2`: `bin/forge-mutante` (`--ids`, isenta velha à parte com rc 1, isenta fora do diff na volta, isenta da condição nova por ocorrência no nó), `skills/qa-testing/SKILL.md`, fragmento em `changelog.d/`, specs antigas realinhadas (AR-12) e duas specs novas (M1 a M17, sem M12).

## Achados
- A1 (recomendado) bin/forge-mutante:596 · afrouxa de fato: uma isenta passa a liberar toda condição nova com o trecho, até guardas distintas (S1). Propor: isenta consumida, uma condição por isenta (`id(i) not in usadas` e uma vez no nó); trecho repetido pede uma isenta por condição, no teto de 8. Merge só com OK do dono e afrouxa-regra.
- A2 (recomendado) tests/test_forge_mutante.py:1053 · o teste fixa o comportamento que afrouxa (duas condições, uma isenta, rc 0); se A1 for aceito, ele vira o caso "duas condições pedem duas isentas" e a segunda condição com uma isenta só sai `sem mutante`, rc 1.

## Sondas
- S1 · clone em b11631b2, spec v0478-mutante-lote sem M1 e M2 e com uma isenta de trecho `args.ids is not None`; `--cobertura --base 0c47762a` · espera: rc 1 (uma isenta, duas guardas) · obtido: rc 0, `isenta · bin/forge-mutante:1138` e `:1179`; o forge-mutante da base no mesmo commit sai rc 2

## Parecer
Aprovado. O cartão 1 (`--ids`) e o 2 (erro sob mutante, só texto da skill) fazem o pedido e têm teste do ramo de falha: id ausente, vazio e `M1,` saem 2 sem rodar nada; `--ids` sem SPEC é recusado. A isenta velha à parte (rc 1, a cobertura inteira listada) e a isenta fora do diff na volta (pela spec do merge-base) corrigem o defeito do pedido sem afrouxar: a velha segue contando no rc.

Pergunta do autor, cartão 3: afrouxa de fato. Antes, o trecho da isenta de condição nova tinha de ser único no arquivo, então uma isenta liberava uma condição. Agora vale para cada condição nova cujo nó contém o trecho, sem consumo: um trecho genérico de 8 não brancos libera guardas com semântica diferente sob um motivo só. A S1 prova isso neste próprio diff: `args.ids is not None` libera a guarda de uso (`--ids` sem SPEC) e a de filtro, e o rc fica 0. A linha impressa por condição deixa o efeito visível ao review, mas o portão mecânico deixa de exigir uma decisão por condição. Proposta que conserta o defeito "repetida" sem afrouxar: tratar a condição nova como a apagada uma vez (ISENTA-POR-TEXTO): trecho uma vez dentro do nó e isenta consumida (`usadas`), uma por condição; trecho repetido no arquivo deixa de ser recusa, e N condições pedem N isentas, dentro do teto de 8. Alternativa equivalente: campo `condicoes: N` na isenta, com rc 1 se o número casado diferir. Fica como A1 recomendado porque o comportamento atual é o que o cartão pede e a decisão é do dono (já registrada como pendente no histórico do pedido); sem o OK, o PR leva afrouxa-regra no título e o motivo (`R-REVIEW`, CLAUDE.md, regras protegidas).

Ferramentas: `bin/forge-mutante --cobertura --base 0c47762a` no head sai rc 0, toda condição mudada coberta por mutante declarado, sem isenta. Rodei só os 6 testes novos ou mudados do lote (`OK`); a suíte inteira fica no CI do PR. Tamanho (H1): cerca de 60 linhas de código em `bin/forge-mutante`, fora a docstring de uso, dentro do teto. Commits em Conventional Commits, um por mudança.
