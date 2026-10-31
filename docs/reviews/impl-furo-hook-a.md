---
tipo: review
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a2
commit: 7b5f5aa36d90f6368325dfd53d514ebafa545040
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-furo-hook-a, branch a2 (A2 PARECER-LANCADOR)

Escopo: `234dbe0..6ef09ba` (base 234dbe0fb90b005450d7c2eb59e6241ea9779155), commits `57f9a27` (teste das fixtures do lote), `ed4e092` (correção), `026c03f` (spec de mutantes) e `6ef09ba` (fragmento). Revisor em instância diferente do autor (D-ETAPAS-INST = A).

## Item entregue
E2, item A2 PARECER-LANCADOR do pedido, pelo desenho §2.6. Em `conferir_linha`, o `hooks/parecer.py` passa a ler cada comando por `analise_do_comando`, que usa `separar_lancadores`, a mesma fonte do conformidade. Dentro da função:
- o `cd` de lançador não muda a pasta;
- atrás do `xargs`, merge e pull recusam;
- `find` com `-exec`, `-execdir`, `-ok` ou `-okdir` recusa, e os lançadores fora da tabela (`OUTROS_LANCADORES`) também;
- `LancadorDemais` e `TextoDivididoAberto` recusam com R-REVIEW.

As 9 fixtures do lote cobrem `timeout`, `env`, `xargs`, `find -exec`, `flock`, o encadeado `nice timeout env`, o `nice` sem parecer e o `cd` de lançador. A contraprova `timeout` com parecer aprovado libera. Na `heredoc-volta-unica.json`, o CO5 (`time`) agora recusa no parecer, e isso é endurecimento coerente com o item. O `docs/hooks.md` foi atualizado.

## M14
Linhas que contam: `hooks/parecer.py` 32+3 e `tests/test_hooks.py` 5, num total de 40. Ficam fora as fixtures de `tests/hooks/` e `tests/fixtures/`, a spec de `tests/mutantes/`, o `.md` e o `changelog.d/`. São 40 linhas, abaixo de 150. Há uma classe só em `hooks/` (o parecer lê atrás do lançador), com corpus próprio, e nenhum caminho de `PROTEGIDOS`. Cumpre.

## Conferido
- Sondas pelo hook real no HEAD revisado, com o fixture `parecer/forge-clone-pr-merge-timeout-reprovado-bloqueia.json` como modelo e o merge reprovado. Todas saíram 2:
  - `timeout --foo 60`, `env -u X`, `sudo -u x`, `command`, `nohup`, `stdbuf -oL`, `exec`, `builtin` e `setsid`;
  - `find . -execdir … \;`, `env -S '…'`, `xargs -a f` e `env A=1 nice -n 5`.
- `$(echo gh pr merge …)` sai 0, com ou sem `timeout` na frente. É o nome calculado da classe N-HOOK1, que já existia na base e fica fora do A2.
- O `time` antes do merge sai 2, pelo CO5 atualizado.
- R-NEUTRO e R-CUSTO: nada a apontar. Não há shell tocado. O Forge não tem `docs/engineering/praticas.md`.
- Não refiz a mutação: o histórico do pedido registra os mutantes mortos na E1.1.

## Revalidação (head 7b5f5aa)
Desde o parecer em `6ef09ba`, a branch trouxe a develop duas vezes (`412abf7`, `7b5f5aa`); nenhum commit de código do autor. O `forge-check delta` listou o intervalo inteiro, quase todo da develop (0.30.8); li só o que é da branch, pela diferença contra a base `6b77146` (`git diff 6b77146...HEAD`).
- Delta lido: `hooks/parecer.py` (35 linhas), `tests/test_hooks.py` (5) e `docs/hooks.md` (a resolução do merge). Código e teste são idênticos aos do parecer anterior.
- `docs/hooks.md`: a linha "Palavra crítica só no texto" ficou com o texto da branch (lançadores lidos pela `separar_lancadores`, `xargs` e `find -exec` recusam) e a linha nova da develop (código de saída) segue intacta, sem perda de nenhuma das duas. A linha [B] também reflete a branch.
- Já lido, não relido: o restante do delta (CHANGELOG, `bin/`, `tests/` e corpus da develop), que não é da branch.
- M14 na base nova: 32+3 em `hooks/parecer.py` e 5 em `tests/test_hooks.py`, 40 linhas; uma classe em `hooks/`. Cumpre.

## Achados
- A1 (recomendado) hooks/parecer.py:264 · OUTROS_LANCADORES repete os 6 nomes de LANCADORES_RECUSADOS do conformidade.py:59 e acrescenta outros 6; uma lista só em _comum.py evita que os dois hooks divirjam quando um nome novo entrar.
- A2 (recomendado) hooks/parecer.py:274 · lê só a 1.ª leitura de separar_lancadores, e o desenho §2.6 pede a união de todas; a docstring explica (opção fora da tabela já recusa no nível 0) e a sonda `timeout --foo 60 gh pr merge` saiu 2; fixe isso numa fixture do lote.

## Parecer
Aprovado, também em 7b5f5aa. A branch entrega o A2 e cumpre a M14. As recomendações não devolvem.
