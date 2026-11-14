# Práticas de engenharia — {{PROJETO}}

As práticas padrão vêm da skill `engineering-practices` do Forge. Este arquivo registra só o que é **específico deste projeto** e prevalece sobre a skill. Decisões estruturais ficam em ADR.

Pipeline, containers, IaC e releases seguem a skill `ci-cd` do Forge; segurança, a skill `cyber-security`.

## Stack
<!-- linguagens, frameworks, banco, gerenciador de pacotes -->

## Comandos
<!-- pronto, testes, lint, migrações -->

## Commits e branches
Padrão da fábrica: Conventional Commits em português; `R-FLUXO` branches e promoção; `R-MAIN` a main é do usuário.
Integração (skill `trabalho-em-paralelo` do Forge): um item por vez com o CI do push na integração verde antes do próximo, ou lote de até 3 PRs verdes sem arquivo em comum com um CI só, o do último merge, acompanhado até o fim; vermelho reverte o lote e volta ao um por vez. A promoção leva o commit da marca, não o topo da integração; marca, versão, changelog e pareceres num PR só.
<!-- exceções deste projeto -->

## Regras e quem as decide
Cada regra diz quem a decide: uma **ferramenta** (comando que roda na suíte do projeto, como lint, tipos ou teste; o comando concreto vem do `pronto.md` da stack) ou a **leitura** (o revisor lê o diff). O review não refaz o que a ferramenta decide: cita a saída do comando. Regra "ferramenta" sem comando configurado é pendência a registrar, não revisão manual. Acrescente uma linha por regra do projeto.

| Regra | Decidida por |
|---|---|
| Lint e formatação sem erro | `<comando de lint do pronto.md>` |
| Tipagem no modo estrito | `<comando de tipos do pronto.md>` |
| Testes passam; teste novo para todo bug corrigido | `<comando de testes do pronto.md>` (a existência do teste novo: leitura) |
| Cobertura mínima exigida | `<comando de cobertura do pronto.md>` |
| Pontuação de mutação no código alterado ≥ meta | `<comando de mutação do pronto.md>` |
| Nomes, tamanho das funções, duplicação | leitura |
| Segue a arquitetura e os ADRs | leitura |
| Segurança: segredos, injeção, autorização, dados pessoais | leitura |
| Modelagem do banco (chaves, índices, histórico, migração com volta) | leitura |

## Meta de mutação
Meta: `<pontuação da primeira rodada>` (a pontuação do comando de mutação do `pronto.md` na primeira entrega com código; o modo incremental reaproveita o resultado anterior e roda só no código alterado).
- A meta só sobe: a rodada que passa da meta vira a meta nova.
- Descer a meta pede decisão do dono (`R-DECISAO`), registrada aqui com a data.
- Entrega sem código (só texto, documentação ou configuração) não roda mutação.
