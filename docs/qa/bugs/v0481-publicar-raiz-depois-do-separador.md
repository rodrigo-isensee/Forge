# v0481-publicar-raiz-depois-do-separador - trava R-CONTRIB do publicar lê `--raiz=` depois do `--`
- Severidade: alta
- Responsável sugerido: tech-lead (autor do hook `conformidade`)
- Ambiente: melhoria/v0481-g2-1-publicar, 841c14dc

## Passos para reproduzir
1. Sessão de projeto (agente `forge:tech-lead`).
2. Comando: `forge-check --raiz <clone do Forge> parecer publicar -- --raiz=x/.forge/pareceres/v1/review.md`.
3. Rodar o hook `conformidade` (ou `ultima_raiz("--raiz /f parecer publicar -- --raiz=./x.md".split())`).

## Resultado esperado
Código 2, R-CONTRIB (barrava em c78bfe22; o argparse trata o que vem depois do `--` como o arquivo e usa a raiz do Forge).

## Resultado obtido
`ultima_raiz` devolve `./x.md`; o hook libera (código 0) em 841c14dc.

## Evidência
Chamada direta a `ultima_raiz` na cópia do QA; mesma sonda nos pareceres de review E6.22 (S4) e segurança E6.24 (S1). Correção: parar o laço em `--`, com fixture lado 2 e mutante.
