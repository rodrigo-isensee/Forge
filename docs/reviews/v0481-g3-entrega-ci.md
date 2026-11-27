---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g3-entrega-ci
commit: 18e27eebe017f5c9f6e0e3281c32b952fc7f3ef9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E28.2, #923, G3 parte 1: a entrega no Forge prova o pronto pelo CI do PR), 1ª rodada completa

Diff lido: `f1e4f478..18e27eeb` (2 commits: `2476b05b` feat, `18e27eeb` mutantes). Arquivos: `bin/forge-check` (36 linhas de código, dentro do H1), `tests/test_forge_pronto.py`, `tests/test_selo_e_entrega.py`, `tests/mutantes/v0481-g3-entrega-ci.json` (M1 a M8), `tests/mutantes/v0481-g3-entrega-ci-2.json` (M9 a M13), `tests/mutantes/v0481-d2-no-brief-2.json` (M16 reapontado) e `changelog.d/v0481-g3-entrega-ci.md`. Os arquivos ficaram dentro da lista do brief do autor (tl-316).

## Achados
- A1 (recomendado) skills/briefs-e-conferencia/conferencia-da-entrega.md:10 · A seção do D2 ainda diz que a conferência roda o `forge-check pronto` no Forge e pede `--worktree` sem a cópia; com o item, no Forge a prova é o CI do PR. O brief do autor não liberou skills/: cartão para a parte 3 do G3.
- A2 (recomendado) bin/forge-check:10697 · O ramo `forge_no_head` da `prova_do_pronto` ficou inalcançável: o único chamador (10902) não passa mais o parâmetro. Ele segue vivo só pelos testes de ProvaDoPronto (test_forge_pronto.py:314 e 318) e pelos M14 e M15 da v0481-d2-no-brief-2.json. Remover os três juntos.

## Leitura
- **Faz o pedido (E28.1, decisão do dono de 26/11 18:54):** na etapa `codigo`, com o head do Forge (manifesto e sem `.forge/versao`), a conferência chama `prova_do_ci` no lugar da `prova_do_pronto`. O D2 local não roda nem com `--worktree`. Fora do Forge, nada muda.
- **Falha fechada:** sem PR lido (sem rede ou erro do `gh`), PR em outro head, checks ilegíveis, head mudado entre as duas leituras do `gh pr view` (antes e depois do `gh pr checks`, que lê o head do momento), check vermelho, pendente ou cancelado, exigido ausente e lista vazia: todos reprovam com a linha que nomeia o motivo. A prova só sai com ao menos um check lido e nenhum ruim.
- **Checks fora da linha:** a lista é a mesma `CHECKS_FORA_DA_LINHA_DO_CI` do parecer (fonte única). Ela vale nos lidos e nos exigidos, pelo parâmetro `fora=()` de `checks_ruins`. O default vazio deixa `checks_do_head` e `ci_verde_no_head` como estavam. Os exigidos do Forge seguem cobrando `CI/bateria (python 3.14)` em pass, então um CI todo em `skipping` não prova.
- **Teste reescrito (pergunta do brief):** em `Entrega.test_sem_worktree_com_o_head_no_forge_nao_cumpre`, a troca do valor esperado é a do comportamento novo. Antes, o esperado era `pendente: D2 sem worktree…`. Agora o mesmo cenário (head do Forge, sem worktree) não roda o D2: o teste exige `assertNotIn("D2 sem worktree")`, a linha do PR em outro head, a do CI vermelho no head e o `cumpriu` com o CI verde e a `catraca` vermelha. A parte final do teste (com `.forge/versao`, um projeto) segue igual. Não houve afrouxamento: o caso continua reprovando, por outro motivo e com mais ramos cobertos.
- **Falsos do gh (checklist 12):** o falso de shell casa `pr view melhoria/x` e `pr checks 7` pela string exata, e o falso de Python casa as tuplas exatas. Outra chamada responde com erro.
- **Legibilidade e commits:** função curta, com nome que diz o que faz. As mensagens seguem Conventional Commits em português, com uma mudança por commit.
- **Fora deste review:** o afrouxamento do D2 local na conferência (a catraca pede o rótulo) segue a decisão do dono de 26/11 18:54 ("não roda mais a bateria inteira no computador"); o rótulo e o que afrouxa por escrito são da segurança (E28.3).

## Verificações
- ci: 18e27eebe017f5c9f6e0e3281c32b952fc7f3ef9 verde
- `gh pr checks 923` no 18e27eeb (head do PR, rascunho): suíte 3.12 e 3.14 (partes 1 a 5), teto de pulados 3.12 e 3.14, bateria (passos), bateria (verificações longas), bateria (python 3.14), instalação (python 3.14, ponta a ponta) e árvore já provada na develop estão em pass. Os de push na develop e a cobertura informativa estão em skipping. Falham só `bateria (pareceres)`, `bateria` e `catraca`, que esperam o parecer ou o rótulo.
- Rodados aqui no 18e27eeb: `python3 -m unittest tests.test_forge_pronto.ProvaDoCi tests.test_forge_pronto.ProvaDoPronto tests.test_selo_e_entrega.Entrega.test_sem_worktree_com_o_head_no_forge_nao_cumpre` (12 testes, OK).
- `bin/forge-mutante --processos 1` com as duas specs do item: M1 a M13 morreram. M4, M5 e M6 morreram por erro: o mutante segue para `pr.get` em None, para o `pop` do falso sem o 2.º head e para o `join` de None. Nenhum desses caminhos vira prova. `--ids M16` da v0481-d2-no-brief-2.json: morreu. `--cobertura --base f1e4f478`: toda guarda mudada tem mutante declarado.

## Parecer
Aprovado. O item faz o que a decisão do dono pede, em uma fonte só, com falha fechada em todos os ramos e teste de comportamento para cada guarda. A1 e A2 são recomendados e viram cartão depois do merge.
