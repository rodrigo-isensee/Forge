# mp1311-01 - migração 0.47.1 escreve fora do projeto por link simbólico
- Severidade: alta
- Responsável sugerido: tech-lead (autor da migração)
- Ambiente: melhoria/mp1311-modelo-seguranca, 4b78a54b, python3

## Passos para reproduzir
1. `mkdir -p proj/docs fora; ln -s "$PWD/fora" proj/docs/security`
2. `python3 migrations/0.47.1/migrar proj`

## Resultado esperado
Recusar ou ignorar o link; nada escrito fora de `proj`.

## Resultado obtido
Imprime `criado docs/security/_modelo.md` e `fora/_modelo.md` passa a existir (`exists()` e `copy` seguem o link; o link pendurado no arquivo se comporta igual).

## Evidência
`ls fora` mostra `_modelo.md` após a migração (rodada em cópia do head 4b78a54b).
