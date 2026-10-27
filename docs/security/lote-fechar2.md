---
tipo: revisao-seguranca
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: a35a18171fd920286e73c511dfe5c5d0cfb897f6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: lote-fechar2 (revalidação, voltas 4 e 5)

Escopo: revalidação por delta do parecer anterior (commit revisado `5c6684d`, parecer `768b2ec`) até `a35a181`. O `forge-check delta` sobre este parecer lista `bin/forge-fechar:80`, `:177`, `:337` e `:750` (+4 -4), `changelog.d/lote-fechar2.md:5`, `tests/mutantes/lote-fechar2-4.json:1-46` e `tests/test_fechar.py:613-630` (+18 -0). O intervalo não toca `.github/` nem `hooks/` (`git diff --quiet` rc 0).

## Gatilhos
Controle do Forge (`R-SEGURANCA`): o `forge-fechar` decide abrir e mesclar o PR (passo 2 e passo 2b) e apagar a branch remota (limpeza).

## Achados

## Detalhe dos achados
Sem bloqueante e sem recomendação nova. Verificações, com evidência:

1. **As quatro reescritas mantêm o caminho de falha.** Em `bin/forge-fechar:80` (faixa numérica), `:177` (pasta do log é diretório e não é link), `:337` (laço dos checks: só segue com `catraca` e run conhecido) e `:750` (PR MERGED com commit de merge), `A && B || C` virou `if ! { A && B; }; then C; fi`. As duas formas rodam C quando A ou B falham e não rodam C quando os dois passam. A diferença clássica do `A && B || C` (C rodar quando B falha depois de A passar) não muda nada aqui, porque C já rodava nesse caso e continua rodando. Cada `die` e o `continue` ficam no mesmo ramo, com a mesma mensagem. Conferi a tabela verdade das duas formas sob `set -euo pipefail` (`:35`), com os quatro casos de A/B e com a regex de `:80` para `12`, `abc` e um número longo demais. Saídas iguais nos sete casos (sonda local em `$TMPDIR`, fora do repositório).
2. **Nenhuma asserção afrouxou.** `tests/test_fechar.py` só ganha linhas (+18 -0): o teste de fonte `test_fechar_sem_a_e_b_ou_c_solto` (`:613-630`). A spec nova `tests/mutantes/lote-fechar2-4.json` (S1 a S4) volta cada linha à forma antiga e espera que o teste de fonte a recuse. As formas `&& ... ||` que restam no script (`:82`, `:180`, `:187`) estão agrupadas em `{ }`, `$( )` ou `( )`, não são SC2015, e o teste as aceita de propósito.
3. **Execução.** No commit `a35a181`, `shellcheck bin/forge-fechar` dá rc 0 (versão local) e `python3 -m unittest tests.test_fechar` passa os 87 testes.
4. **PA-7.** `docs/engineering/achados-recorrentes.md` está sem achados registrados, então não há item a conferir.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas, todas locais: `forge-check delta`, `git diff`, `shellcheck`, `unittest` e uma sonda de equivalência em bash. Faltaram no ambiente, e ficam como lacuna: `gitleaks`, `zizmor` e `actionlint` (o delta não traz credencial nem mudança de workflow).
