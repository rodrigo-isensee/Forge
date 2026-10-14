# Práticas de engenharia — {{PROJETO}}

As práticas padrão vêm da skill `engineering-practices` do Forge. Este arquivo registra só o que é **específico deste projeto** e prevalece sobre a skill. Decisões estruturais ficam em ADR.

## Stack
<!-- linguagens, frameworks, banco, gerenciador de pacotes -->

## Comandos
<!-- pronto, testes, lint, migrações -->

## Commits e branches
Padrão da fábrica: Conventional Commits em português; `R-FLUXO` branches e promoção; `R-MAIN` a main é do usuário.
<!-- exceções deste projeto -->

## Regras e quem as decide
Cada regra diz quem a decide: uma **ferramenta** (comando que roda na suíte do projeto, como lint, tipos ou teste; o comando concreto vem do `pronto.md` da stack) ou a **leitura** (o revisor lê o diff). O review não refaz o que a ferramenta decide: cita a saída do comando. Regra "ferramenta" sem comando configurado é pendência a registrar, não revisão manual. Acrescente uma linha por regra do projeto.

| Regra | Decidida por |
|---|---|
| Lint e formatação sem erro | `<comando de lint do pronto.md>` |
| Tipagem no modo estrito | `<comando de tipos do pronto.md>` |
| Testes passam; teste novo para todo bug corrigido | `<comando de testes do pronto.md>` (a existência do teste novo: leitura) |
| Cobertura mínima exigida | `<comando de cobertura do pronto.md>` |
| Nomes, tamanho das funções, duplicação | leitura |
| Segue a arquitetura e os ADRs | leitura |
| Segurança: segredos, injeção, autorização, dados pessoais | leitura |
| Modelagem do banco (chaves, índices, histórico, migração com volta) | leitura |
