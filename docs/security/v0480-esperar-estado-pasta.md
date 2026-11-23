---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-esperar-estado-pasta
commit: be805bc832dbce125ef69637d62fc35229bf08ee
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E120.4, frase devolvida à skill esperar-estado)

Base 38c37de9, head be805bc8. Passada única e curta: o parecer é exigido pela classe do item, não por gatilho de código.

## Gatilhos
Gatilhos: nenhum (só texto de skill; sem código, hook, workflow, segredo nem controle do Forge).

## Resumo
- Diff de segurança: `skills/esperar-estado/SKILL.md:19` acrescenta "e rode na pasta do repositório" à instrução do laço do PR. O bloco de comando em `:21-23` não muda. O fragmento `changelog.d/v0480-esperar-estado-pasta.md` só descreve a correção.
- Efeito: o `gh pr view` e o `gh pr checks` resolvem o repositório pela pasta atual. A frase reduz o risco de consultar o PR de mesmo número em outro repositório e decidir pelo estado errado. Ela não amplia permissão nem abre caminho de entrada.
- `R-NEUTRO`: nada de projeto. Nenhum segredo no diff (3 arquivos lidos por inteiro).
- Suíte: a branch não tem CI rodado neste head; o item não tem teste de abuso devido (texto puro). A suíte inteira fica com o CI do PR.

## Achados

## Sondas

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática do diff `38c37de9...be805bc8`. A varredura de segredos não foi rodada porque o diff é texto lido por inteiro, sem credencial.
