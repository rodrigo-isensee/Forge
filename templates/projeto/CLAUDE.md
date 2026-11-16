# {{PROJETO}}

{{DESCRICAO}}

Este projeto é desenvolvido pela fábrica **Forge** (plugin `forge@forge`, https://github.com/rodrigo-isensee/Forge). O time de agentes, o fluxo, as skills e as práticas gerais vêm do Forge; este arquivo guarda só o que é **deste sistema**.

## Stack
- Pacote do Forge: `{{STACK}}` (`stacks/{{STACK}}/` no Forge: agentes de desenvolvimento, skills, `seguranca.md` e `pronto.md`). O Jarvis delega o desenvolvimento só aos agentes desse pacote; sem esta seção vale `node-react`.

## Sessão
- Abra e retome o Jarvis sempre no automático: `jarvis` ou `claude --agent forge:jarvis --permission-mode auto`. No primeiro comando o Jarvis confere o sandbox do Bash; se falhar, para e avisa o dono com o comando para reabrir a sessão (o dono nunca aprova comando a comando).

## Fonte da verdade
<!-- Documentos de referência do sistema (briefing, especificações, contratos). Aponte caminho e o que cada um decide. -->
- `docs/pedidos/`: pedidos do usuário, um arquivo por pedido.
- `docs/constituicao.md`: princípios e portões do projeto; o plano técnico é conferido contra ela.

## Regras invioláveis do sistema
<!-- Regras de negócio, de segurança e de dados que nenhum agente pode quebrar. Uma por linha, objetivas. -->
- 

## Comandos do projeto
- **Pronto** (critério de entrega dos agentes): `{{COMANDO_PRONTO}}`
- **Testes rápidos**: <!-- comando de testes da stack -->
- **Linha de status (opcional)**: `forge-status` mostra uma linha por pedido em curso; para ligar, ponha `"statusLine": {"type": "command", "command": "forge-status"}` em `.claude/settings.local.json`.

- **Ambiente:** durante o trabalho, desligue a atualização automática da extensão do Claude Code (ela reinicia a sessão e leva os agentes em curso); o nome da opção muda entre versões, procure por atualização automática nas configurações da extensão.

## Exceções locais às regras da fábrica
<!-- Só o que diverge do Forge, com o motivo. Ex.: teto de recursos diferente, outro banco, outra branch de integração. -->
- Nenhuma.

## Regras da fábrica
Valem aqui; o texto completo de cada uma está em `docs/regras/` do Forge (https://github.com/rodrigo-isensee/Forge/tree/main/docs/regras). Exceções só na seção acima, com o motivo.
- `R-DECISAO` decisões levadas ao usuário uma a uma, com opções e a recomendação do time; sem resposta, ficam pendentes; melhoria vista entra direto pelo critério da regra.
- `R-MAIN` a main é do usuário (hook `.githooks/pre-push`; ative com `git config core.hooksPath .githooks`).
- `R-VERIFY` nunca `--no-verify` nem `--force`.
- `R-FLUXO` branches e promoção · `R-WIP` 1 cartão por agente e limites de coluna · `R-TETO` teto de recursos da máquina.
- `R-DISCOVERY` todo pedido começa com discovery · `R-REVIEW` code review em toda entrega · `R-QA` portão de QA · `R-SEGURANCA` parecer de segurança quando há gatilho.
- `R-COPIA` não copiar agentes e skills para o projeto: mudanças em agentes, skills, fluxo e práticas gerais vão para o repositório **Forge** (seção "Fábrica × projeto" do Jarvis).
