# {{PROJETO}}

{{DESCRICAO}}

Este projeto é desenvolvido pela fábrica **Forge** (plugin `forge@forge`, https://github.com/rodrigo-isensee/Forge). O time de agentes, o fluxo, as skills e as práticas gerais vêm do Forge; este arquivo guarda só o que é **deste sistema**.

## Stack
- Pacote do Forge: `{{STACK}}` (`stacks/{{STACK}}/` no Forge: agentes de desenvolvimento, skills, `seguranca.md` e `pronto.md`). O Jarvis delega o desenvolvimento só aos agentes desse pacote; sem esta seção vale `node-react`.

## Fonte da verdade
<!-- Documentos de referência do sistema (briefing, especificações, contratos). Aponte caminho e o que cada um decide. -->
- `docs/pedidos/`: pedidos do usuário, um arquivo por pedido.

## Regras invioláveis do sistema
<!-- Regras de negócio, de segurança e de dados que nenhum agente pode quebrar. Uma por linha, objetivas. -->
- 

## Comandos do projeto
- **Pronto** (critério de entrega dos agentes): `{{COMANDO_PRONTO}}`
- **Testes rápidos**: <!-- comando de testes da stack -->

## Exceções locais às regras da fábrica
<!-- Só o que diverge do Forge, com o motivo. Ex.: teto de recursos diferente, outro banco, outra branch de integração. -->
- Nenhuma.

## Regras da fábrica
Valem aqui; o texto completo de cada uma está em `docs/regras/` do Forge (https://github.com/rodrigo-isensee/Forge/tree/main/docs/regras). Exceções só na seção acima, com o motivo.
- `R-MAIN` a main é do usuário (hook `.githooks/pre-push`; ative com `git config core.hooksPath .githooks`).
- `R-VERIFY` nunca `--no-verify` nem `--force`.
- `R-FLUXO` branches e promoção · `R-WIP` 1 cartão por agente e limites de coluna · `R-TETO` teto de recursos da máquina.
- `R-DISCOVERY` todo pedido começa com discovery · `R-REVIEW` code review antes do QA · `R-QA` portão de QA.
- `R-COPIA` não copiar agentes e skills para o projeto: mudanças em agentes, skills, fluxo e práticas gerais vão para o repositório **Forge** (seção "Fábrica × projeto" do Jarvis).
