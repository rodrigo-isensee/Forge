---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-promocao-pr
commit: 1e0c50a715ebd00251278c278722b7be3819bb3c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478-promocao-pr

Revalidação (E31.7) no head 1e0c50a7, por delta. A rodada anterior (E31.4, head d836c435) fica no git.

## Gatilhos
Gatilhos: controle do Forge (portão do `forge-check pr`: quando a conferência E7 e o teto H1 deixam de valer).

## Resumo
- Delta lido (`forge-check parecer delta`, `d836c435..1e0c50a7`): no domínio, só `bin/forge-check` (`promocao` e a nova `ponta_da_integracao`, `:1575-1593`, e a docstring de `foi_ponta_da_integracao`). Fora do domínio: o fragmento do changelog, os mapas de mutantes e `tests/test_promocao_por_marca.py` (lido só o teste novo de ff, que prova o A1).
- A1 (recomendado, avanço rápido vira promoção): **resolvido**. Sem a remota, só a ponta atual da develop local vale (`bin/forge-check:1591-1593`); a cadeia de primeiros pais fica só para `origin/<base>` (`:1589-1590`). Segue a correção mínima proposta. A docstring agora diz em quais métodos de merge a garantia vale (`:1597-1600`). O teste `test_avanco_rapido_na_develop_local_sem_remoto_nao_vira_promocao` cobre os dois destinos e a ponta atual. A falha fechada continua igual: `sha_do_commit` devolve None sem a ref, e o git com erro dá False.
- Resíduo do mesmo raciocínio na remota: o "merge pelo PR" da docstring (`:1587`) não cobre o "Rebase and merge" do GitHub, que deixa os commits do item em linha na cadeia. Vira o A2, recomendado.

## Achados
- A2 (recomendado) bin/forge-check:1587 · Na remota, o código presume merge por squash ou merge commit. Com "Rebase and merge" ligado num projeto, os commits intermediários rebaseados entram na cadeia de primeiros pais de origin/develop e viram promoção (sonda S2: True). Deixe a premissa documentada no guia de promoção ou confira-a.

## Sondas

## Detalhe dos achados
**A2** · evidência: `bin/forge-check:1585-1590` usa `foi_ponta_da_integracao` com toda ref `origin/<base>` presente. A premissa fica só na docstring (`:1587`, `:1597-1600`). Sonda S2 (`scratchpad/sonda_s2.sh` da sessão, não versionada): remoto bare; item `c1`→`c2` rebaseado sobre a develop, que avança em linha e é enviada (o mesmo resultado do "Rebase and merge"). `promocao(c1', "main")` dá `True` no head 1e0c50a7.
Caminho de ataque: o mesmo do A1 da E31.4. Quem abre o PR de promoção escolhe como head um intermediário do item e escapa de E7 e H1. Isso só acontece num projeto que liga o rebase-merge na integração. O Forge mescla por squash (`bin/forge-fechar`), e `cmd_pr` continua cobrando os pareceres. Por isso não bloqueia.
Severidade: baixa. Correção mínima (esforço P): escrever, onde se descreve a promoção para os projetos, que a integração não usa "Rebase and merge" (só squash ou merge commit), ou recusar a cadeia quando o commit da ponta não é um merge nem um squash de PR. Dono: o autor da E31.1 (código) ou o `devops-engineer` (configuração do repositório).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Rodado no head 1e0c50a7: `tests/test_promocao_por_marca.py`, 5 testes OK em 2,9 s. Suíte inteira: não rodada (brief). O CI do PR continua como portão. Ferramentas: o varredor de segredos e os linters de workflow não estão no PATH (lacuna). O delta não toca em workflow nem em segredo.
