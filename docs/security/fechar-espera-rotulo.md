---
tipo: revisao-seguranca
contrato: 1
pedido: fechar-espera-rotulo
branch: melhoria/fechar-espera-rotulo
commit: 9930be95b0ee3ab10c6bb1c4c7d971f1d6d41471
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: fechar-espera-rotulo

Escopo: o diff `10c838f..9930be9` (bin/forge-fechar, tests/test_fechar.py, docs/fechamento-integrador.md, changelog.d/fechar-espera-rotulo.md), com o script lido inteiro e o workflow da Catraca (`.github/workflows/catraca.yml`) como referência do controle que o script consome.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): o `forge-fechar` é o passo mecânico que mescla na `develop`, e a nova opção muda como ele interpreta o check `catraca`, que é o portão do rótulo `afrouxa-regra` do dono (`R-CONFORMIDADE`, `R-FLUXO`).

## Achados

## Detalhe dos achados
Nenhum achado bloqueante. Pontos avaliados:

- **O script nunca aplica rótulo nem mescla sem Catraca verde.** Não há `--add-label`, `pr edit`, `gh api` nem `--admin` no script (busca no arquivo inteiro); o teste `test_esperar_rotulo_mescla_quando_o_rotulo_aparece_na_leitura_n` confere a ausência nas chamadas. A troca de `catraca fail` por `pending` (bin/forge-fechar:194) só alimenta a condição de continuar esperando: o laço de checks só sai por `break` quando nenhum estado é pendente (bin/forge-fechar:216), então uma Catraca vermelha mascarada nunca leva ao merge; só uma leitura `pass`/`skipping` dela leva. `cancel` (o workflow usa `cancel-in-progress`) continua caindo em "check desconhecido" e para. Falha fechada.
- **Tolerância de 10 leituras depois do rótulo** (suposição do autor): é limite de espera, não de liberação. Esgotada, a Catraca vermelha volta a parar no passo 4 (teste `..._para_apos_a_tolerancia`). O contador soma leituras com o rótulo presente, não seguidas; tirar e repor o rótulo não estende a espera além de `--espera`. Sem caminho de ataque.
- **Prazo.** Além dos passos 4 e 5 (bin/forge-fechar:217 e :235), o ramo "nenhum check ainda" também confere o prazo; as leituras de head e rótulo usam `ler` (até 3 tentativas). Não há laço sem limite. Prazo esgotado sem rótulo para com a mensagem do passo 5, com rótulo, com a do passo 4; nos dois casos, sem merge.
- **Head preso.** A releitura do head a cada volta (bin/forge-fechar:182) para se o head mudou; o merge continua com `--match-head-commit` do head conferido no passo 2 (bin/forge-fechar:258), que é o controle de fato. Um commit empurrado durante a espera não é mesclado.
- **Sem a opção**, o comportamento é o anterior (teste `test_sem_a_opcao_o_rotulo_pedido_e_ausente_continua_parando`); `FORGE_GH`/`FORGE_CHECK` continuam só com `FORGE_FECHAR_TESTE=1`.

Recomendações (não bloqueantes, dono: tech-lead):
- R1 (informativa) bin/forge-fechar:182: a leitura do head com `|| true` aceita vazio e pula a conferência quando o `gh` falha 3 vezes. Não abre caminho (o `--match-head-commit` segura o merge), mas a falha fechada seria mais coerente com o resto: tratar vazio como erro de leitura e parar. Esforço P.
- R2 (baixa, usabilidade do controle) bin/forge-fechar:194: com a opção, a Catraca vermelha é mascarada mesmo quando o PR não pede o rótulo (título e item marcado sem `afrouxa-regra`) e ela falhou por outro motivo (seção do corpo faltando, teste removido). O script espera até `--espera` e para com a mensagem do rótulo, que engana o integrador. Falha fechada, sem risco de merge; sugestão: só mascarar quando o passo 5 detecta o pedido do rótulo. Esforço P.
- R3 (informativa): o mascaramento depende do nome exato do job `catraca` (`.github/workflows/catraca.yml:19`). Se o nome mudar, a espera deixa de valer e o script para no primeiro vermelho (falha fechada). Vale um comentário no workflow apontando o acoplamento.

## Riscos aceitos e ferramentas
Nenhum risco aceito. `python3 -m unittest tests.test_fechar`: 54 testes OK nesta revisão (sobre o commit revisado). `shellcheck` e `gitleaks` não estão no PATH deste ambiente (lacuna registrada; o CI roda o shellcheck). Nenhuma varredura externa; nenhum segredo no diff (leitura manual).
