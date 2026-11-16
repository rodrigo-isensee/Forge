---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-juncao-sem-vencer
commit: 7babe7b84c382dc4ecba5ca59bfac38e3e210995
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (E2.201, junção sem vencer parecer)

## Gatilhos
Controle do Forge (`R-SEGURANCA`): muda o portão `forge-check pr` (`bin/forge-check`, `pr_da_cli`), que decide se um parecer está desatualizado. Diff revisado: `4138445e..7babe7b8` (bin/forge-check, testes, mutantes, fragmento do changelog).

## Achados

## Sondas

## Detalhe dos achados
Sem achado bloqueante nem recomendação.

Análise do afrouxamento: sem `--base`, numa branch de trabalho (fora de `develop`, `homolog`, `main`), o `pr` passa a usar a `develop` como base. Esse é o mesmo caminho já aceito do `--base develop` explícito (validação de `BASES_DO_FLUXO`, base lida de `origin/develop` pelo `base_do_delta`, a local só sem remoto, e head já contido na base volta ao diff literal), igual ao `forge-fechar` e ao `parecer delta`. Não abre superfície nova: quem pudesse forjar `refs/remotes/origin/develop` local já conseguia o mesmo com `--base develop`, e a catraca do CI recebe a base do evento do PR, não deste padrão (`cmd_pr`).

Casos de borda conferidos: branch não resolvida (HEAD destacado sem branch) segue o diff literal, o caminho mais estrito; nas branches de integração o padrão não se aplica (teste `test_branch_de_integracao_segue_o_diff_literal`); arquivo que a branch mudou depois do parecer segue vencendo (`test_mudado_pela_branch_depois_do_parecer_vence`). O aviso T1 e a isenção de QA passam a ler o diff contra a develop, o que só os torna mais fiéis ao que a branch traz.

Suíte: os testes do item rodaram no clone (`python3 -m unittest tests.test_forge_check_base_igual`, 13 OK; `tests.test_forge.TesteEParecerSeparados`, 3 OK); a suíte inteira roda no CI do PR, aberto depois dos pareceres.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Varredura de segredos e SAST de workflow não se aplicam (sem workflow nem credencial no diff); as ferramentas de varredura não estão no PATH deste ambiente (lacuna registrada; rodam no CI).
