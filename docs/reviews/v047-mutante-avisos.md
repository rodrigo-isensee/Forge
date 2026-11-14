---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-mutante-avisos
commit: 4553163442c9ff33e3993de0bee982f924a16a5f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (E1.161, lote do bin/forge-mutante)

Intervalo `origin/develop..45531634` (base e60183d0 = merge-base), 4 commits de código e teste e 1 de changelog, feitos por outra instância (E1.140). Classe C (código de controle do Forge).

## Achados
- A1 (recomendado) bin/forge-mutante:772 · teste herdado de classe-base noutro módulo (já commitado) sai "teste fora do commit" no controle vermelho: o `def` não está no módulo do nome. Sonda: tests/base.py com Base.test_herdado, tests/test_a.py com T(Base) → teste_no_commit False. Sugestão: só avisar quando o módulo falta.
- A2 (recomendado) bin/forge-mutante:675 · nenhum teste do --conferir tem isenta sem `linha_base` (o ramo que pula); sem `"linha_base" in i and` o --conferir cai com KeyError, e nenhum teste exercita o ramo. Sugestão: uma isenta sem linha_base em test_linha_base_que_bate_sai_0_e_a_deslocada_sai_1.

## Sondas

## Parecer
**Aprovado.** Os três comportamentos pedidos pela E1.140 (retro 0.45.6, candidatas 8 e 9, e o aviso de teste fora do commit) estão no diff, nem mais nem menos; o `--conferir` reaproveita `ler_no_commit`, `fonte`, `condicoes` e `validar_spec` e repete a regra de `cruza` (linha da base e trecho uma vez na fatia de bytes do nó), sem duplicar mecanismo; a extração de `base_do_diff` tira a repetição da `--cobertura` sem mudar o comportamento dela.

Checklist (leitura; o Forge não tem `docs/engineering/praticas.md`, vale o da skill):
1. Escopo: confere com o item da E1.140. Changelog em fragmento, sem tocar o `CHANGELOG.md`.
2. Regras: `R-VERIFY` e `R-CUSTO` sem alcance; nada de projeto (`R-NEUTRO`).
3/4. Legível; erros explícitos (`except` com tipo e motivo; o aviso do log vai ao stderr e não muda o código de saída). A1 é limite da heurística documentada no docstring, não muda o veredito (a linha já sai rc 2): recomendado.
7. Testes de comportamento dos ramos de falha (saídas 0, 1 e 2 do `--conferir`, arquivo sumido, sem parse, log que não se grava, teste e módulo fora do commit); subprocesso com `-I` e ambiente limpo (`AMBIENTE`). A2 é lacuna de borda: recomendado.
9. Commits por comportamento, Conventional Commits em português.
10. Mecanismo novo pedido em DECISÃO DO DONO (14/11 08:42, candidata 9); reversão é tirar a opção.

Guardas e mutantes (`R-REVIEW`, 'Mutantes declarados'): 19 mutantes em 3 specs (8 + 8 + 3), um por linha de guarda. `forge-mutante --cobertura --base e60183d0` rodado aqui: rc=0, 13 linhas `coberta` e nenhuma sem mutante. Rodei a spec `-3` no head: CF17, CF18 e CF19 morreram, rc=0. Testes novos (`Conferir` e os três de `Execucao`): 9 OK em 18,4 s. `forge-mutante --conferir --base origin/develop` na própria branch: rc=0. A suíte inteira fica para o CI do PR.

Tamanho (M14): 206 linhas de código e teste (`bin/forge-mutante` 105, `tests/test_forge_mutante.py` 101), acima da orientação por três comportamentos pedidos juntos no mesmo item; o corpo do PR leva `teto: excedido, 206 linhas, três comportamentos do forge-mutante pedidos juntos na E1.140`.

Segurança e QA têm parecer próprio (E1.162, E1.163); não os refaço.
