---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-fechar-defeitos
commit: 5d383ebfa624c7eabd7ea02fdd2909091c50d29e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478, E75.4 (melhoria/v0479-fechar-defeitos)

Escopo: diff `65de25ce..5d383ebf` (11 arquivos; código só em `bin/forge-fechar`): FECHAR-1C-ANTES-DO-2B, FECHAR-6A-DEVELOP-ANDOU e FECHAR-CHECKS-ANTES-DO-MERGE (com a volta E75.2).

## Gatilhos
Gatilhos: controle do Forge (ferramenta de merge `bin/forge-fechar`: portões de checks, pareceres, conflito e R-FLUXO no passo 1c).

## Resumo
Nenhum dos três caminhos abre merge sem checks verdes, sem pareceres ou com conflito:
- **Pareceres:** o passo 1 (`forge-check pr`) e a trava do head (`--match-head-commit` e `pre_head = remoto_sha`, `bin/forge-fechar:1583`) não mudaram.
- **1c** (`bin/forge-fechar:1032-1039`): o 1c confere um commit solto, sem ref, com a árvore do `merge-tree` limpo entre o head e a base. Esse commit contém todas as mudanças do head: parecer reprovado, versão e fragmento do head ficam no merge, e se a base mexeu no mesmo arquivo há conflito e o 1c volta para o head. Conflito, falha do `merge-tree` ou falha do `commit-tree` caem no comportamento antigo (`return 0` com `sha_1c` = head). A base local velha não chega a mesclar, porque o 2b para antes (`:960`).
- **6a** (`:988-997`): a busca escreve só `refs/remotes/origin/<alvo>`. Depois dela, três condições continuam exigidas: a base local tem de ser igual ao sha do servidor, `base_2b` tem de ser ancestral dele, e o `merge-tree` tem de sair limpo contra esse sha (`conflito_com 6a "$srv"`, `:915-926`; objeto ausente vira rc 128 e para). Se a busca falha, para. Se a busca traz outro sha, para (`:994`). Uma base reescrita para no teste de ancestralidade. O head conferido (`remoto_sha`) não muda.
- **Checks** (`:864-874`, `:1590`): a mudança só acrescenta recusas. O check obrigatório tem de existir e todas as execuções com esse nome têm de estar em completed/success. Leitura que falha para. Nome mais longo não vale pelo exigido.

Confirmação: **não só aperta**. Dois pontos aceitam o que antes era recusado, e pela DECISÃO DO DONO de 19/11 08:54 e de 20/11 21:34 o rótulo `afrouxa-regra` espera o OK do dono:
1. **1c:** a branch criada antes de uma release promovida, com o head numa versão menor que a da homolog e o merge-tree limpo, antes parava em "versão menor" e agora passa, porque o 1c confere o merge com a base.
2. **6a:** com a base andando durante os checks e a base local velha, o 6a antes parava e pedia `git fetch`. Na rodada seguinte o 2b trazia a base e o CI rodava sobre o merge. Agora o 6a busca a base e mescla na mesma rodada, sem CI sobre o merge. É a mesma política do E8, que já valia quando a base local estava em dia.

Os dois corrigem recusas falsas e nenhum deles dispensa checks, pareceres ou a conferência de conflito. O 1c chega a apertar num caso: com release não promovida na develop, o fragmento do head entra no merge e o 1c para.

Ponto de atenção para o dono (A1): a recusa nova não cobre o `--armar`, que é o caminho padrão do time desde 21/11 11:58 (`docs/pedidos/v0478.md`, DECISÃO DO TIME). A premissa do próprio código é que o `--auto` da conta do dono mescla na hora pelo bypass (`:860-861`). Se ela vale, o `--armar` continua mesclando com check obrigatório vermelho ou rodando, como antes da mudança: o caminho não é novo, mas continua aberto.

Suíte: a branch não tem PR, então não há CI (`gh run list --branch melhoria/v0479-fechar-defeitos` devolve `[]`). Rodei os testes novos de abuso: `python3 -m unittest tests.test_fechar_checks_do_head tests.test_fechar_base_andou` deu 49 testes OK no 5d383ebf.

## Achados
- A1 (recomendado) bin/forge-fechar:1590 · a recusa por check não verde pula o --armar, caminho padrão do time (DECISÃO DO TIME 21/11 11:58); pela premissa de :860-861 o --auto do dono mescla na hora pelo bypass, então check vermelho ainda passa; :863 e :1480 dizem o contrário
- A2 (recomendado) bin/forge-fechar:994 · a guarda "base local igual ao servidor" depois da busca do 6a ficou sem teste: o mutante que tira `"$local_base" != "$srv" ||` sobrevive aos 43 testes de tests/test_fechar_base_andou.py (o teste que a cobria foi trocado)

## Sondas

## Detalhe dos achados
**A1.** Evidência: `bin/forge-fechar:1590` (`[ "$armar" = 1 ] || checks_do_head_verdes`). O comentário de `:860-861` afirma que o `--auto` da conta do dono mescla na hora com check vermelho ou rodando, e o de `:863` e `:1480` afirma que o auto-merge armado espera os checks obrigatórios. Para a mesma conta e a mesma chamada `gh pr merge --auto` (`mesclar_auto`), as duas afirmações não valem juntas. O passo 4 já exigia `pass` nos obrigatórios no merge direto (`:1511-1523`), então os 26 de 199 PRs mesclados com check vermelho ou rodando (cartão FECHAR-CHECKS-ANTES-DO-MERGE) passaram por outro caminho, e o `--armar` é o candidato.
- Caminho: um agente que fecha com `--armar` pela conta admin, num PR com a catraca vermelha (caso do #752), arma o merge e o GitHub mescla na hora pelo bypass. Isso fere "nunca use a exceção do ruleset" (DECISÃO DO DONO de 20/11 21:34).
- Severidade: média. É pré-existente, não aberto por este diff.
- Correção mínima, que não esvazia o `--armar`: com `--armar`, antes de `mesclar_auto`, ler os mesmos check-runs e parar se algum obrigatório estiver em completed com conclusão diferente de success. Rodando ou ausente continua armando. Corrigir o texto de `:863` e de `:1480` para a premissa real. O caso "rodando" só fecha com a retirada do bypass (AV1-BYPASS-RULESET, E5.1, decisão do dono).
- Esforço: P. Dono: tech-lead.

**A2.** Evidência: `bin/forge-fechar:994`. Sonda local, numa cópia em `$TMPDIR`: troquei `if [ "$local_base" != "$srv" ] || ! git merge-base --is-ancestor` por `if ! git merge-base --is-ancestor` e rodei `python3 -m unittest tests.test_fechar_base_andou`, que deu 43 OK.
- O teste antigo `test_6a_base_local_velha_para_e_pede_o_fetch` cobria essa guarda e virou o teste da busca. Nenhum mutante de `tests/mutantes/v0478-fechar-6a.json` cobre o caso da busca que traz um sha diferente do lido no `ls-remote`.
- Caminho: não há caminho de merge com conflito, porque `conflito_com` usa o sha do servidor e para sem o objeto. A guarda é o que prende a base buscada à base lida.
- Severidade: baixa.
- Correção mínima: no git falso de `tests/test_fechar_base_andou.py`, um caso em que a busca da develop traz um commit além do lido no `ls-remote`, com a espera de "parou no passo 6a ... $base não a tem" e nenhum merge, mais o mutante correspondente em `tests/mutantes/v0478-fechar-6a.json`.
- Esforço: P. Dono: qa-engineer, com o tech-lead.

Observação sem achado: `checks_do_head_verdes` casa os check-runs só pelo nome (`${par#*/}`) e perde o workflow do par de `CHECKS_EXIGIDOS`. No merge direto, o passo 4 já confere pelo par workflow/nome antes, então isso não abre caminho.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, a sonda de mutante local e os testes novos. Não rodei `gitleaks` porque o diff não toca segredo nem configuração. Os check-runs reais do GitHub não puderam ser lidos (a branch não tem PR), por isso o A1 fica como recomendado, sem prova de execução.
