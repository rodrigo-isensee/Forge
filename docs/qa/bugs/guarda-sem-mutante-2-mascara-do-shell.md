# guarda-sem-mutante-2-mascara-do-shell - o corte grosso do shell ainda esconde condição nova (A1 a A3)
- Severidade: média
- Responsável sugerido: agente de desenvolvimento da stack (tech-lead do Forge)
- Ambiente: melhoria/guarda-sem-mutante-2 @ 729135968bf6, python3

## Passos para reproduzir
1. Carregar `bin/forge-mutante` e chamar `condicoes_sh(texto, incertas)` com o texto de cada sonda (A1: heredoc com `  EOF` e `it's`; A2: `eval "echo a` + `b"`; A3: `f=X; (( 1 )) && cat <<"$f"` + `it's`), todas seguidas de `if [ -d / ]; then exit 1; fi`.

## Resultado esperado
A condição seguinte é lida (`sem mutante`) ou a região sai `não coberto`.

## Resultado obtido
Nenhuma condição lida e nenhuma região incerta cobrindo o `if`; `--cobertura` sai rc 0.

## Evidência
Detalhe em `docs/qa/guarda-sem-mutante-2.md` (sondas A1, A2, A3); o review 930e596 reproduz as mesmas.
