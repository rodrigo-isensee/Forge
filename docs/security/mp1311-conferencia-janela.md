---
tipo: revisao-seguranca
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-conferencia-janela
commit: 773e7e7aa9f87a8dfa14e308a0c1b167ecd0c06d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: mp1311-conferencia-janela

Head revisado `773e7e7a` (base `efe7c9e8`). Gatilho (`R-SEGURANCA`): a conferência de entrega (`forge-check entrega`) é controle do Forge.

## Gatilhos
Controle do Forge: a janela e o escopo da conferência de entrega.

## Achados
- A1 (recomendado) bin/forge-check:2654 · o `--desde` no `Revisar-sha:` só vale na forma antiga e só de leitura (sem gravar); registre num teste que `entrega --pedido` ignora o commit revisado e calcula o Desde sozinho.

## Sondas

## Detalhe dos achados
**Pergunta 1: esconder arquivo de produção como parecer de outro papel.** Não. A isenção estendida a toda etapa de código (`bin/forge-check:2757`) só vale para arquivo sob a pasta de portão, sem caractere de controle, cujo frontmatter no head tem o `tipo` da pasta, `branch` igual, `pedido` da entrega, `parecer` válido e `commit:` igual a um `Revisar-sha:` de brief selado do papel certo, desta branch e pedido (`parecer_de_portao_da_branch`, `bin/forge-check:2545-2563`). O selo é registro do Jarvis, não texto do autor. A busca por veredito trocado segue do Base-sha. O código de produção fora das pastas de parecer continua em `confira`. A extensão é só de etapa (`ETAPAS_DE_CODIGO`); nenhuma condição foi afrouxada. Uma observação sobre o que já existia: o `tipo` vem do prefixo da pasta e não da extensão, então um arquivo qualquer de `docs/<pasta>/` com esse frontmatter passa; isso já valia na etapa `codigo` e é documentação, não código executado, então não muda o risco.

**Pergunta 2: encurtar a janela com `--desde`.** Não por um caminho que grave ou que um portão consuma. O commit revisado só vira Desde se for `Revisar-sha:` de brief selado de portão da mesma branch e pedido, ancestral do head, fora do Base-sha e sem pedido gravado na entrega (`bin/forge-check:2170-2185`). Os três ramos de recusa estão cobertos pelos testes e pelos mutantes M2, M3, M4 e M6. A forma que grava a linha `entrega conferida` (`--pedido`, `bin/forge-check:8973-8980`) calcula o Desde sozinha com `desde_valido` e não recebe os revisados; `brief gerar --volta` (`bin/forge-check:3474`) também não. Então quem executa não escolhe uma janela menor numa conferência que vale como portão. Um Desde mais curto na forma antiga só mostra menos arquivos a quem pediu a leitura. Daí o A1, que é só endurecimento por teste.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem PR aberto no momento: sem CI para citar. Rodados localmente os testes afetados (`JanelaDaEntrega`, `ParecerDoPortao`, `MatrizDaBuscaDoVeredito`); a suíte inteira fica para o CI do PR. Ferramentas de varredura de segredo e de workflow não se aplicam (sem workflow nem segredo no diff).
