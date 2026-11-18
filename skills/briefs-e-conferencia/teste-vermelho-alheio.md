# Teste vermelho de outro item (ADOTAR-TESTE-VERMELHO-ALHEIO)

Detalhe da skill `briefs-e-conferencia`, lido pelo autor, pelo `tech-lead` e pelo QA. Vale no Forge e em todo projeto. Decisão do dono de 18/11, com duas condições.

## Quando vale
O PR de um item para por um teste vermelho que não é do item: o teste cai também na base, ou cai em código que o diff não toca (no Forge, `forge-testes --vermelho` o mostra como herdado da base). Em vez de o PR parar à espera do dono original do teste, o time adota o conserto.

## Condição 1: PR próprio e pequeno
- **A correção vai num PR próprio e pequeno**, com prioridade máxima na fila de integração e **parecer próprio do QA**.
- **Nunca se mistura ao PR parado:** nenhum commit do conserto entra na branch que travou. O PR parado espera só a correção chegar à base (e então traz a base, `R-FLUXO`), não o dono original do teste.
- O `tech-lead` abre a branch e o brief do conserto; quem conserta pode ser o autor do PR parado, em branch nova.

## Condição 2: o teste fica inteiro
- **É proibido apagar o teste, pulá-lo ou afrouxar o que ele confere para ficar verde:** sem `skip`, sem tirar asserção, sem trocar o valor esperado pelo obtido, sem tirá-lo da lista que roda.
- **Teste errado de verdade:** o QA explica no parecer do PR do conserto por que ele está errado: o que confere, o que deveria conferir e a evidência.
- **Os mutantes daquele trecho continuam morrendo:** o QA roda a mutação no código que o teste guarda (no Forge, `bin/forge-mutante` com a spec do trecho) e cola a saída no parecer; mutante sobrevivente bloqueia.

## Quem faz o quê
- **Autor:** ao ver o PR vermelho por teste de outro item, avisa o `tech-lead` e não mexe no teste na sua branch.
- **`tech-lead`:** no review, é achado bloqueante o PR parado que traz o conserto e o conserto que apaga, pula ou afrouxa o teste.
- **QA:** parecer próprio no PR do conserto, com as duas provas da condição 2 quando o teste muda.

## Medida e revisão
- Substitui, para o teste que para um PR, o "vira cartão" da dívida pré-existente (skill `qa-testing`).
- Medida: horas entre o vermelho do PR parado e o merge do conserto, levada ao dono a cada versão.
- Revisão: se em duas versões o conserto adotado demorar mais que esperar o dono original do teste, o `tech-lead` traz ao dono a revisão desta regra.
