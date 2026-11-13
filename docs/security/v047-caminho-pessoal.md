---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-caminho-pessoal
commit: 700913201442a8d57dd0e021ca72d3944b7fa63f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047 caminho pessoal (E5.4, head 70091320)

## Gatilhos
Controle do Forge que analisa entrada (varredura de contribuição que barra caminho pessoal e segredo); gatilho da `R-SEGURANCA` por controle. Sem segredo, sem workflow tocado.

## Achados
- A1 (recomendado) scripts/verificar-contribuicao.sh:55 · a troca de /home/runner/ por @ consome a barra inicial: /home/runner/home/<nome>/x e /home/runner/Users/<nome>/x passam; trocar por / em vez de @ fecha.

## Sondas

## Detalhe dos achados
A1: evidência `scripts/verificar-contribuicao.sh:55`. Sonda local (só o padrão, sem exploração): `/home/runner/home/<nome>/x` e `/home/runner/Users/<nome>/x` dão 0 achados; `/home/runner//home/<nome>/x`, `/home/runner/x /home/<nome>/y` e o aninhado `/home/runner/home/runner/home/<nome>/` dão 1. Caminho de ataque: só um autor que escreva um caminho pessoal logo depois do home do runner, o que é raro e de baixo ganho (a varredura é barreira contra descuido, não contra autor hostil). Severidade baixa; correção mínima: `${texto//\/home\/runner\//\/}` (uma linha, mais um caso no teste); esforço P; dono tech-lead.

Cobertura do requisito da E5.4 (lida no código e no teste, não só no texto): o home do runner sai da linha antes do padrão (linha 55); `/home/runner2/projeto` falha (o segmento exato `runner/` é o que sai; CP-M2 prova); `/Users/runner/projeto` falha (só `/home/runner/` é trocado); `/home/runner/work /home/<nome>/x` falha (a troca é global na linha e o segundo caminho sobra). Os 4 caminhos recusados desde 1c06dc18 seguem recusados (15 testes de `VerificarContribuicao` verdes). A troca não toca a lista de segredos nem o desvio `forge:exemplo`.

Por que `forge-mutante --cobertura` diz "não coberto" no script: a checagem só analisa condição com `ast` em arquivo Python; shell, binário e fora do UTF-8 viram "não coberto: <arquivo>" por arquivo, sem erro e com saída 0 (`bin/forge-mutante`, ramo `eh_python` da função `cobertura`). Não é falha da entrega: o mutante é declarado à mão em `tests/mutantes/v047-caminho-pessoal.json` e a rodada real mata os três (CP-M1, CP-M2 e CP-M3, "morreu"). Lacuna da ferramenta, não do código.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Usados: `forge-mutante` (rodada e `--cobertura`), unittest da classe `VerificarContribuicao`, bash. Suíte inteira: roda no CI; não há PR aberto para o head, então valem os testes afetados e a rodada de mutantes. Sem lacuna de instalação.
