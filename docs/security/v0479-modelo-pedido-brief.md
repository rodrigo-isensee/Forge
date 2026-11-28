---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-modelo-pedido-brief
commit: 83246fbf4c5ec96f5e9caeb114084f6089289423
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-modelo-pedido-brief

Etapa E86.4 do pedido v0478 (MODELO-PEDIDO-E-BRIEF). Diff lido inteiro: `ad3b3b6f..83246fbf` (8 arquivos, texto de skill, modelo de projeto, teste e mutantes).

## Gatilhos
Gatilhos: controle do Forge (skills `checagem-do-brief` e `fluxo-do-pedido`, modelo de pedido do projeto)

## Veredito
Só aperta; nenhum corte afrouxa regra.

Cortes feitos para caber no teto, conferidos um a um:
- `skills/checagem-do-brief/SKILL.md:3` (description) perde o caminho `docs/engineering/brief-checklist.md`; o corpo (`:21`) continua citando o caminho e mantém inteiro "nunca dispensa portão ... nem afrouxa uma regra" (`R-DECISAO`).
- `skills/checagem-do-brief/SKILL.md:21` troca o caminho do modelo vazio por "vem no `forge-init`": só localização, sem regra.
- `skills/fluxo-do-pedido/SKILL.md:30` perde "selado pelo passo 3 dela" e "selo no genérico, uma escrita por branch". O passo segue mandando o brief selado (`R-BRIEF`) e aponta a skill `briefs-e-conferencia`, cujo passo 4 (`skills/briefs-e-conferencia/SKILL.md:14`) guarda o selo em todo tipo que escreve (hook `agentes`) e a escrita única por branch (Z10). A trava é do hook, não do texto cortado. Nenhum trecho de `invariantes` sumiu (`tests/config.json` idêntico à base).

Texto novo:
- `.githooks/` (`skills/checagem-do-brief/por-tema.md:6`): reafirma que o arquivo é do usuário e que o hook `conformidade` barra a escrita do agente; o Entregar não manda editar, só pede o diff como proposta que o dono aplica. Não abre contorno (não sugere script, cópia nem outro caminho de escrita); o mutante M5 prova que trocar por "manda editar o arquivo" quebra o teste.
- Criar a cópia (`por-tema.md:5`, `fluxo-do-pedido/SKILL.md:30`): os comandos citados são os da ADR 0009 (`forge-copia`, `git worktree add --no-track`), sem `-u`, sem `--force`, sem tocar `.git/config`; a conferência `git status -sb` logo depois só acrescenta verificação.
- Parecer (`por-tema.md:7`): `forge-check pr` com `rc=0` antes do QA antecipa a cobrança de autoria e validade; aperta.
- Número de testes (`por-tema.md:8`): só de comando rodado na entrega, com data e commit; aperta `R-PROVA`.
- Modelo de pedido (`templates/projeto/docs/pedidos/_modelo.md:36-41`): etapa numerada por delegação, marca `(outro repositório)` e etapa da retrospectiva; nada remove a etapa de segurança (E1.3 intacta).

## Detalhe dos achados
Sem achados.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Sem suíte local (brief); a suíte inteira roda no CI do PR para a `develop`. Rodado para tirar dúvida: `python3 -m unittest tests.test_modelos_projeto.ModeloPedidoEBrief tests.test_modelos_projeto.ChecagemDoBrief` no head 83246fbf: 12 testes, OK. Varredura de segredo não se aplica (só texto, sem credencial no diff).
