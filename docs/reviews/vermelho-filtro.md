---
tipo: review
contrato: 1
pedido: vermelho-filtro
branch: melhoria/vermelho-filtro
commit: 21a4caa312799f62bfd9e31cb8dd687218c16d59
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Code review: VERMELHO-FILTRO

Rodada 1 (E1.2), branch inteira `9e6fa28..21a4caa`, 3 commits, 4 arquivos, 97+/2-. Revisor diferente do autor (implementação feita no outro computador; D-ETAPAS-INST).

Ferramentas rodadas em 21a4caa: `python3 -m unittest tests.test_testes_tocados` → `Ran 85 tests ... OK`; `bin/forge-mutante tests/mutantes/vermelho-filtro.json` → M1, M2, M3 e M4 `morreu` (`bin/forge-testes:417`, `:417`, `:419`, `:418`); `bin/forge-mutante --cobertura --base 9e6fa28` → linhas 417 e 418 `coberta`, nenhuma descoberta; `git merge-tree --write-tree origin/develop HEAD` (develop em 8c07b44) → rc 0, merge limpo. Shell não tocado (sem shellcheck). Suíte inteira e `scripts/validar-plugin.sh` ficam no CI do PR (decisão M8); `bin/forge-testes --listar` pede a suíte completa porque o diff toca `bin/forge-testes`. Segurança (a prova do vermelho é controle do Forge): parecer próprio do `security-engineer` (E1.3), não refeito aqui.

## Teto (decisão M14)
`git diff --numstat --no-renames 9e6fa28...HEAD`: `bin/forge-testes` 7+/2- e `tests/test_testes_tocados.py` 42+/0- = 51 linhas que contam; `tests/mutantes/vermelho-filtro.json` e `changelog.d/vermelho-filtro.md` ficam fora. Dentro do teto de 150, sem `hooks/` nem caminho de `PROTEGIDOS`, um comportamento só (o filtro do plano do `--vermelho` sem `--modulos`, com a linha de motivo do plano completo). Cumpre a M14.

## O que foi lido
- `bin/forge-testes:417`: o filtro passa de `MODULO_DE_TESTE` para `TESTE_DO_DIFF`, devolvendo `tests/config.json` ao `planejar` por `ALTERA_O_MAPA`. Correto: os dados de teste (`tests/mutantes/`, `fixtures/`, `hooks/`, `transcricoes/`, `migracoes/`) já estavam em `mantidos` (linha 402), iguais nas duas cópias, então não discriminam e só empurravam à suíte completa por não terem mapa. Os módulos de teste do diff continuam entrando por `modificados`. Com `--modulos`, o ramo não muda.
- `bin/forge-testes:418-419`: a linha `vermelho: o mapa não sabe (...)` sai só no plano completo e diz o motivo do `planejar`; o docstring (linhas 21-22) foi atualizado junto.
- Borda conferida: diff só com dados de teste (sem produção) dá plano dirigido vazio e módulos só do diff; antes seria a suíte completa. É o resultado certo: sem produção revertida nada pode provar, e o código sai sem prova (contagem "nenhum teste").
- Testes: os quatro casos novos cobrem spec mais fixture (plano do mapa, sem aviso), caminho sem mapa (aviso e suíte completa), `tests/config.json` (suíte completa com o motivo) e `--modulos` (sem aviso). A spec tem um mutante por guarda e todos morrem; a checagem 11 do checklist (asserções de ausência) se sustenta, porque cada `assertNotIn` tem um par `assertIn` que o mutante M4 ou M3 derruba.
- Commits: três, Conventional Commits em português (fix, test, docs), cada um citando o pedido; o fragmento `changelog.d/vermelho-filtro.md` está presente (`### Corrigido`).

## Recomendações (não devolvem)
- `bin/forge-testes:419`: no caso de `tests/config.json`, a linha fica "o mapa não sabe (tests/config.json altera o mapa ou a configuração)", que é um pouco imprecisa (o mapa sabe, e manda a suíte inteira). Algo como "vermelho: plano completo (...)" ficaria mais exato. Cosmético.

## Achados

## Parecer
Aprovado. A mudança faz o que o pedido pede, nem mais nem menos, cabe na M14, tem teste para cada guarda e mutantes que morrem, e não tem conflito com a develop. Nenhum bloqueante.
