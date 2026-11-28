# {{PROJETO}}

{{DESCRICAO}}

Este projeto é desenvolvido pela fábrica **Forge** (plugin `forge@forge`, https://github.com/rodrigo-isensee/Forge). O time de agentes, o fluxo, as skills e as práticas gerais vêm do Forge; este arquivo guarda só o que é **deste sistema**.

## Stack
- Pacote do Forge: `{{STACK}}` (`stacks/{{STACK}}/` no Forge: agentes de desenvolvimento, skills, `seguranca.md` e `pronto.md`). O Jarvis delega o desenvolvimento só aos agentes desse pacote; sem esta seção vale `node-react`.

## Sessão
- Abra e retome o Jarvis sempre no automático: `jarvis` ou `claude --agent forge:jarvis --permission-mode auto`. No primeiro comando o Jarvis confere o sandbox do Bash; se falhar, para e avisa o dono com o comando para reabrir a sessão (o dono nunca aprova comando a comando).
- **Vários projetos na máquina:** uma janela e um Jarvis por projeto, cada um na sua pasta, no modo auto. Com dois ou mais ativos, o teto de agentes da máquina é dividido em partes iguais; para dar mais a este projeto, `jq '.peso = 2' .forge/config.json > .forge/config.novo && mv .forge/config.novo .forge/config.json` (acima de 0 e até 10; padrão 1), por branch e PR. O escape `FORGE_CARGA_LIVRE=1` só vale com um projeto ativo; no Telegram, um bot só, com `[<projeto>]` em cada resposta. Ver a máquina: `forge-status --maquina`. Guia: README do Forge, seção "Vários projetos na mesma máquina".

## Ritmo do time
- **Ritmo diário:** o time desenvolve em paralelo, dia e noite, e junta cada item verde na branch de integração em lotes de até 3, nunca sem os testes verdes; a versão fecha quando a branch de integração soma 20 itens integrados, sem versão por dia, num PR para a `main`. À noite o Jarvis não escreve ao dono, salvo algo grave que mude prazo ou risco.
- **Corte por arquivo:** cartões que mexem nos mesmos arquivos vão para o mesmo agente, na mesma branch, um depois do outro; de 3 a 5 cartões pequenos por lote, com uma revisão só.
- **Teto do time:** até 20 agentes e 12 branches abertas; agente livre termina o que está aberto (revisão, conserto, teste vermelho) antes de abrir item novo.

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
- **Conferência de registros** (índices, mapas e contagens derivados que o CI reprova; só leitura, em segundos): o comando da chave `registros` do `.forge/config.json`, que o `.githooks/pre-push` roda em todo envio de branch; saída fora de 0 barra o envio, e sem a chave nada roda. <!-- o que o comando confere -->
- **Versões do intérprete** (as do CI do projeto; o padrão é o campo `Versões` do `pronto.md` da stack): <!-- ex.: as da matriz do CI --> O autor roda os testes rápidos em cada uma antes de entregar, um log por versão com `head=` na 1.ª linha e `rc=` na última; versão sem o intérprete na máquina não é verde.
- **Linha de status (opcional)**: `forge-status` mostra uma linha por pedido em curso; para ligar, ponha `"statusLine": {"type": "command", "command": "forge-status"}` em `.claude/settings.local.json`.

- **Ambiente:** durante o trabalho, desligue a atualização automática da extensão do Claude Code (ela reinicia a sessão e leva os agentes em curso); o nome da opção muda entre versões, procure por atualização automática nas configurações da extensão.

## Exceções locais às regras da fábrica
<!-- Só o que diverge do Forge, com o motivo. Ex.: teto de recursos diferente, outro banco, outra branch de integração. -->
- Nenhuma.

## Regras da fábrica
Valem aqui; o texto completo de cada uma está em `docs/regras/` do Forge (https://github.com/rodrigo-isensee/Forge/tree/main/docs/regras). Exceções só na seção acima, com o motivo.
- `R-DECISAO` decisões levadas ao usuário uma a uma, com opções e a recomendação do time; sem resposta, ficam pendentes; melhoria vista entra direto pelo critério da regra. Pedido de decisões do usuário: o Jarvis responde já, só com elas, por peso e uma a uma (skill `falar-com-o-dono`).
- `R-MAIN` a main é do usuário (hook `.githooks/pre-push`; ative com `git config core.hooksPath .githooks`).
- `R-VERIFY` nunca `--no-verify` nem `--force`.
- `R-FLUXO` branches e promoção · `R-WIP` 1 cartão por agente e limites de coluna · `R-TETO` teto de recursos da máquina.
- `R-DISCOVERY` todo pedido começa com discovery · `R-REVIEW` code review em toda entrega · `R-QA` portão de QA · `R-SEGURANCA` parecer de segurança quando há gatilho.
- `R-COPIA` não copiar agentes e skills para o projeto: mudanças em agentes, skills, fluxo e práticas gerais vão para o repositório **Forge** (seção "Fábrica × projeto" do Jarvis).
