---
tipo: revisao-seguranca
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c6
commit: 5de4830c47d7f460aea4ec7eaafbe184017527cb
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-pre-push, branch c6 (texto da trava limitado e imprimível)

Diff lido: `234dbe0..5de4830` (`ee86b7f` C-14; `113635c` fragmento; `5de4830` parecer do code review, só `docs/reviews/`).

## O que entrega
Parte do E3 do pedido (TRAVA-SANDBOX): o controle C-14 do modelo `docs/security/ameacas/pre-push.md` e o teste T-C4h (caso de abuso 12). `texto_da_trava` (`.githooks/pre-push:42`) lê no máximo 200 bytes da trava e mantém só os bytes imprimíveis em `LC_ALL=C` (0x20 a 0x7E: some ESC, BEL, DEL, quebra de linha e bytes não ASCII). As duas saídas que exibiam a trava por `cat` passam a usá-la: `--status` (`:102`) e o aviso de espera (`:222`). Não sobra outra leitura do conteúdo da trava no hook (busca por `cat`/`head` sobre `$trava`).

## M14 (agents/tech-lead.md:19)
`git diff --numstat --no-renames 234dbe0 5de4830`: `.githooks/pre-push` 6+2, `tests/test_pre_push_trava.py` 17; total 25, abaixo de 150 (fragmento e parecer fora da conta). Um comportamento só (o que o hook exibe do texto da trava). Mexe em `.githooks/`, protegido, sem precisar da exceção. Cumpre.

## Gatilhos
R-SEGURANCA: controles do Forge (o pre-push e a trava da suíte).

## Achados
- A1 (recomendado) .githooks/pre-push:42 · Ordem de integração: a c6 entra na develop antes ou junto da c4 (trava comum); sem ela, o texto gravado na trava de dentro do sandbox chega ao terminal de fora sem filtro (A5 do modelo).
- A2 (recomendado) .githooks/pre-push:43 · texto_da_trava relê a trava pelo caminho, não pelo descritor 9 conferido; trocar o arquivo por um FIFO depois da conferência trava o --status e o aviso de espera (negação local, baixa, já existia com o cat).

## Detalhe dos achados
- **A1.** Evidência: `.githooks/pre-push:42`, `:102`, `:222`; A2 do parecer de review da c5 e A1 do review desta branch. Caminho: com a c4 sem a c6, um processo no sandbox grava sequência de escape na trava comum e o dono a vê no terminal de fora. Severidade: baixa (só se a ordem falhar). Correção mínima: mesclar a c6 antes ou junto da c4. Esforço P. Dono: `tech-lead` (integração, E1.5).
- **A2.** Evidência: `.githooks/pre-push:43` lê `"$trava"`; a conferência (`trava_confere`) é sobre o descritor 9 aberto em `:96` (leitura) e `:215` (anexação). Caminho: processo do mesmo usuário (o sandbox, com a pasta comum da c4) troca o arquivo por um FIFO entre a conferência e a leitura; o `head` bloqueia e o push do dono fica parado. O 1 MiB e o `/dev/zero` já ficam limitados pelo `head -c 200`. Severidade: baixa, sem ganho além de negação local; comportamento anterior idêntico. Correção mínima: ler por `/proc/self/fd/9` (reabre o mesmo inode, também no descritor de anexação) com `head -c 200`. Esforço P. Dono: `tech-lead`, em pedido futuro.

## Verificação
- `python3 -m unittest tests.test_pre_push_trava -k test_texto_da_trava` na worktree: 1 teste, OK (18 s). O teste grava ESC, BEL e 1 MiB e confere as duas saídas sem `\x1b`/`\x07` e com tamanho limitado.
- `|| true` no fim do pipe mantém o hook vivo se a trava sumir entre o `flock` e a leitura; o texto vazio não abre caminho.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff e o teste acima. Faltaram no PATH: `shellcheck`, `gitleaks`, `zizmor`, `actionlint` (lacuna; o CI roda o shellcheck do hook). Sem segredo no diff (leitura manual).

## Parecer
Aprovado.
