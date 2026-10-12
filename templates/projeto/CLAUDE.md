# {{PROJETO}}

{{DESCRICAO}}

Este projeto é desenvolvido pela fábrica **Forge** (plugin `forge@forge`, https://github.com/rodrigo-isensee/Forge). O time de agentes, o fluxo, as skills e as práticas gerais vêm do Forge; este arquivo guarda só o que é **deste sistema**.

## Fonte da verdade
<!-- Documentos de referência do sistema (briefing, especificações, contratos). Aponte caminho e o que cada um decide. -->
- `docs/pedidos/`: pedidos do usuário, um arquivo por pedido.

## Regras invioláveis do sistema
<!-- Regras de negócio, de segurança e de dados que nenhum agente pode quebrar. Uma por linha, objetivas. -->
- 

## Comandos do projeto
- **Pronto** (critério de entrega dos agentes): `{{COMANDO_PRONTO}}`
- **Testes rápidos**: <!-- ex.: npm test -->

## Exceções locais às regras da fábrica
<!-- Só o que diverge do Forge, com o motivo. Ex.: teto de recursos diferente, outro banco, outra branch de integração. -->
- Nenhuma.

## A main é do usuário
Nenhum agente faz commit, merge ou push na `main`. Toda mudança chega por pull request validado e mesclado pelo usuário. O hook `.githooks/pre-push` bloqueia envios para a `main` (ative com `git config core.hooksPath .githooks`).

## Fábrica × projeto
Mudanças em agentes, skills, fluxo e práticas gerais vão para o repositório **Forge**, nunca para este projeto. Ver a seção "Fábrica × projeto" do Jarvis.
