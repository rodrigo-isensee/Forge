---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp2-i2-regra
commit: 0ce5173bf504d028f1a49eeb94491c9d22cdedae
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E38.9 (BP2 I2 e I5, fila e conserto na R-FLUXO)

Diff 004ce869..0ce5173b: 7 arquivos, só texto e `tests/config.json` (0 linha de código, H1 ok). Escopo confere com o desenho (I2, I5 e a ampliação da E38.8 para o `ritmo-e-corte.md`); C1 a C7 (D2) estão nos 7 itens do conserto; D3, D4, D1 e D6 aparecem no texto; o fragmento do changelog declara o afrouxamento (D5, `afrouxa-regra`). Invariantes novos casam com o texto: módulos tocados rodados (`tests.test_modelos_projeto` 20 OK; `test_forge` Neutralidade, NeutralidadeDoNucleo, RegrasInviolaveis, RegrasComId, TextosDoAgenteEDaRegra: 15 OK). Suíte inteira: no CI do PR (sem run na branch).

## Achados
- A1 (bloqueante) docs/protecao-de-branch.md:45 · Diz que o `bin/forge-fechar` já barra o PR testado sobre `develop` velha; hoje o 6a segue sem retestar (bin/forge-fechar:937, E8) e a I4 não entrou. Escreva que, até a I4, a fila é à mão (como o `ritmo-e-corte.md`), senão quem lê pula a conferência (`R-FLUXO`, D3).
- A2 (recomendado) templates/projeto/docs/engineering/protecao-de-branch.md:30 · O passo 8 ainda diz que a branch traz a base uma vez; a seção nova (linha 51) e a D3 pedem novo teste sempre que a base anda. Alinhe o passo 8 aqui e em docs/protecao-de-branch.md:21.

## Sondas
- S1 · grep -n "sigo para o merge" bin/forge-fechar · espera: o 6a recusa ou retesta quando a base andou · obtido: 937 echo "... sem conflito com $ref; não trago a base (E8); sigo para o merge."

## Parecer
Reprovado por A1: documento de proteção afirma um controle que a ferramenta ainda não tem (prova em S1); a correção é de uma frase. A2 não devolve e vira cartão. Os A1 do QA (linha da `develop` sem invariante) e da segurança (C3 e C4 mais completos) são deles; não repito.
