---
tipo: review
contrato: 1
pedido: lote-0307-a
branch: melhoria/lote-0307-a
commit: 38f3f7194f36fd0e9b0dd1e0e01bf4c7280e4c19
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: lote-0307-a

Pedido LOTE-0307-A-REV, etapa E1.1 (`R-REVIEW`). Diff lido: `3b94791...38f3f71` (9 arquivos, +63 -4). Teto M14: 42 linhas de código e teste (`bin/forge-fechar` +14, `tests/test_fechar_base_andou.py` +28; `tests/mutantes/` e `.md` ficam fora), abaixo de 400; nada em `hooks/` nem em `PROTEGIDOS`.

## Achados
- A1 (bloqueante) bin/forge-fechar:596 · regressão: worktree da branch com o diretório já apagado (registro órfão, caso que o passo 7 trata com prune) agora para antes do passo 1 com "não consegui ler a pasta git"; na base o fechamento segue até o fim. Pular o diretório ausente e cobrir com teste.
- A2 (recomendado) bin/forge-fechar:544 · o --dry-run não imprime o passo 0 da guarda do index.lock, que o docs/fechamento-integrador.md já lista; acrescente a linha para o dry-run descrever o caminho real inteiro.

## Parecer
Reprovado por A1, defeito de comportamento provado.

**A1, a prova.** Usei uma sonda em `$TMPDIR/tech-lead-lote-0307-a/sonda_prunable.py`, montada sobre o ambiente de `tests/test_fechar_base_andou.py`: a branch `melhoria/x` tem uma worktree e o diretório dela é apagado com `rmtree`, sem prune. Com o `bin/forge-fechar` do head 38f3f71, o script sai com rc=1 e escreve `parou antes do passo 1: não consegui ler a pasta git da worktree .../wt-x`. Com o `bin/forge-fechar` da base 3b94791, o mesmo cenário sai com rc=0: o fechamento vai até o fim e o passo 7 limpa a branch remota. O `git worktree list --porcelain` continua listando a worktree (marcada `prunable`), então o `git -C "$arvore_lock" rev-parse --git-dir` falha e cai no `die`. O passo 7 já trata esse caso ("prune se o diretório já sumiu", linhas 404 a 411), então ele acontece de verdade. Sugestão: na linha 595, `[ -n "$arvore_lock" ] && [ -d "$arvore_lock" ]`. Um diretório ausente não tem `index.lock` que trave o avanço. Também falta um teste do diretório ausente, que deve seguir com rc=0.

**O que está certo:**
- A guarda nova é o passo 0. Ela roda antes do passo 1 e só no caminho real: fica depois do `exit 0` do `--dry-run` e do `exit` do `--limpar`.
- Ela só lê e avisa. Nunca apaga o lock. Imprime o caminho, a idade em minutos e o comando `rm` com `printf %q`.
- O caminho relativo de `--git-dir` (worktree principal) é resolvido contra a worktree.
- O `stat` tem fallback entre GNU e BSD, e a idade vira `desconhecida` quando ele falha.
- `set -euo pipefail` está ligado, então a falha do `git worktree list` não fica escondida pelo `awk` (AR-1, `mascara-do-shell-esconde-codigo`, conferido: não se repete aqui).
- O `awk` compara o nome exato da branch (`$2==b`), não um prefixo.
- O texto dos três modelos (reviews, qa e security em `templates/projeto/docs/`) e do `docs/security/_modelo.md` da raiz ficou igual e coerente com o `forge-check docs`: ele só recusa parecer `reprovado` sem `bloqueante` (bin/forge-check:1211) e aceita aprovado com `recomendado`. A raiz igual ao template é exigida pelo teste de igualdade, conforme a DECISÃO TÉCNICA de 21:34.
- `docs/fechamento-integrador.md` documenta o passo 0, e o fragmento `changelog.d/lote-0307-a.md` está presente.

**Testes do item.** `python3 -m unittest tests.test_fechar_base_andou` passou: 22 testes, OK. O teste do lock presente confere rc=1, o caminho, `idade: 7 min`, o `rm <caminho>`, o lock ainda existindo e nenhuma criação nem merge de PR. O teste do lock ausente confere rc=0 e um PR criado. O mutante L1 (`if false`) é morto pelo teste do lock presente, conforme o histórico do pedido. Os falsos de `git` só interceptam `ls-remote`, `rev-list` e `diff`; o `worktree list` vai ao git real (checklist item 12, sem afrouxamento).

**Ferramenta.** Não refiz o shellcheck nem a suíte completa: ficam com o pre-push e o CI do PR (decisão de 2026-10-24).

**Fora do review.** Segurança é do `security-engineer` (E2.1, em paralelo) e QA é do `qa-engineer` (E3.1). Não gravei linha AR: a classe do A1 não se repetiu neste pedido nem está em `docs/engineering/achados-recorrentes.md`.
