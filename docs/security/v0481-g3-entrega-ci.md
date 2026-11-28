---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g3-entrega-ci
commit: 18e27eebe017f5c9f6e0e3281c32b952fc7f3ef9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E28.3, G3 parte 1, #923)

1ª rodada completa sobre `f1e4f478..18e27eeb` (`bin/forge-check`, testes, mutantes, fragmento do changelog). A conferência da entrega (etapa codigo) no head do Forge troca o D2 local (`prova_do_pronto`) pela `prova_do_ci`: PR da branch lido pelo nome exato, head do PR igual ao head entregue, checks lidos, head relido, falha fechada sem rede. Ordem do dono de 26/11 18:54 (no `## Decisões` do pedido) cobre o afrouxamento do D2 local.

Gatilhos: controle do Forge (portão da conferência da entrega), leitura do GitHub pelo gh.

## Achados
- A1 (recomendado) bin/forge-check:1587 · Com o agregador `bateria` fora (`CHECKS_FORA_DA_LINHA_DO_CI`), nada exige os jobs só dele (5 partes da suíte no 3.12, teto de pulados 3.12, passos, verificações longas): ausente ou `skipping` passa e a linha diz "concluído". Exigir esses nomes em pass na prova_do_ci.

## Sondas
- S1 · prova_do_ci, gh falso: exigidos do Forge; checks passos, bateria (python 3.14) e instalação em pass, parte 1/5 do 3.12 em skipping, o resto ausente · espera: pendente · obtido: prova: CI do PR #9 concluído e verde (4 checks), reprova False

## O que aperta, o neutro e o que afrouxa
**Aperta**
- Head do Forge sem `--worktree` ou com `--so-leitura`: antes a linha do D2 só informava ou pedia a worktree; agora a entrega só cumpre com o CI do PR lido e verde no head exato (`bin/forge-check:10727`, `:10731`). Leitura do gh, sem rodar código da branch.
- Falha fechada: gh ausente, sem rede, saída ilegível, PR inexistente, nenhum check, pendente, cancelado ou vermelho reprovam (`tests/test_forge_pronto.py` `ProvaDoCi`, 6 testes verdes aqui).

**Neutro**
- Forja por PR de outra branch: `gh pr view <branch>` casa só o PR do mesmo repositório com aquele `headRefName` (PR de fork leva o rótulo `dono:branch`); e o `headRefOid` tem de ser o sha40 entregue, logo qualquer PR aceito testou o mesmo código. A branch vem do brief selado. Residual: a base do PR não é comparada com a `Base:` do brief (PR aberto contra outra base daria CI do merge com ela); o merge na develop segue exigindo todos os checks (`checks_do_head`), sem ganho para quem tenta.
- Head trocado entre leituras: lido antes e depois dos checks (`:10727`, `:10731`); o ABA (H, H', H) pede envio não fast-forward, barrado pelo `R-VERIFY` e pelo pre-push. Check de um sha que também está noutro PR só soma checks ao rollup: um vermelho reprova (todo check lido fora de pass/skipping é ruim).
- Check homônimo de outro app: os exigidos do Forge casam `CI/<nome>` pelo workflow; um status de commit postado à mão chega sem workflow e não satisfaz o exigido; um check vermelho homônimo só reprova. Criar workflow chamado `CI` na branch pede o escopo `workflow`, que o token do bot não tem. Alterar o código que o CI roda (testes, scripts) é diff revisado, igual ao D2 local.
- `CHECKS_FORA_DA_LINHA_DO_CI` (`bateria (pareceres)`, `bateria`, `catraca`): a mesma lista do parecer (PARECER-LE-O-CI); casada só pelo nome, sem workflow. Esconde só checks com esses três nomes exatos, que são os do CI e da Catraca. Ver A1 para o que o agregador escondido deixa de garantir.
- Decisão Forge/projeto pelo conteúdo do head (`:10901`): um projeto que apagasse `.forge/versao` e pusesse o manifesto cairia na `prova_do_ci`; fora do Forge o D2 já só informava, então não afrouxa; e a mudança fica visível no diff.

**Afrouxa (por ordem do dono)**
- A conferência deixa de rodar o `forge-check pronto` no Forge. Além dos testes afetados (cobertos pela suíte inteira do CI), ele conferia: título do PR (PR-TITULO-DO-BRIEF, só em `bin/forge_pronto.py:73`, sem outro portão), teto H1 sem motivo no corpo (o `forge-check pr` confere no merge) e o pr-texto da catraca (a `catraca` está fora da prova; o merge a exige). O título deixa de ter portão na entrega e em lugar nenhum, a menos que o autor rode o D2 como o brief manda. Leve ao dono, pelo Jarvis, se esse pedaço também sai (`R-DECISAO`); não é furo de segurança.
- Base velha (PRONTO-BASE-VELHA) sai da entrega; o CI do PR testa o merge com a base, o que cobre o risco técnico.

## Detalhe dos achados
**A1** · evidência: `bin/forge-check:1587-1588` (filtro `fora` e `skipping` aceito), `:10730`; `.github/workflows/ci.yml:856` (o agregador `bateria` é o único que exige `bateria (passos)`, `bateria (verificações longas)`, as 5 partes da suíte no 3.12 e o teto de pulados 3.12, e trata pulado como falha). Sonda S1 (em arquivo, só a função com o gh falso). Caminho: não é forja por terceiro; é janela de tempo. No `gh pr checks 923` os jobs dependentes ganham check run só quando ficam prontos (ids maiores: teto de pulados 3.12 e `bateria (python 3.14)` criados minutos depois das partes), então entre o fim das partes 3.12 e a criação do teto 3.12 a conferência grava "concluído e verde" sem o teto. O merge segue exigindo o agregador, por isso não é bloqueante. Severidade: baixa. Correção mínima: na `prova_do_ci`, além dos exigidos, exigir presentes e em pass (não `skipping`) os jobs que o agregador `bateria` junta, fora `bateria (pareceres)`: `bateria (passos)`, `bateria (verificações longas)`, `suíte (python 3.12, parte 1/5)` a `parte 5/5` e `teto de pulados (python 3.12)`; ou ler o run do workflow `CI` no head e exigir `status` completed. Teste: o caso da sonda reprova. Esforço: P. Dono: tech-lead (autor do E28.1).

Ao tech-lead (estilo, não segurança): `prova_do_pronto(..., forge_no_head=...)` (`bin/forge-check:10692`) perdeu o único chamador que passava o parâmetro; o ramo E14.81 ficou morto em produção.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes novos rodados aqui: `tests.test_forge_pronto.ProvaDoCi` e `tests.test_selo_e_entrega.Entrega.test_sem_worktree_com_o_head_no_forge_nao_cumpre`, 7 OK. CI do #923 no head c79e7a98 (18e27eeb mais o parecer do review, só doc; run 45906241354): todos em pass ou skipping, instalação (e2e) inclusa, fora os 3 da lista de fora (vermelhos por construção: esperam parecer e rótulo). Ferramentas: o varredor de segredos não está no PATH (lacuna; diff sem credencial lido à mão); sem SAST de workflow, que esta entrega não toca.
