---
tipo: review
contrato: 1
pedido: v047-fila-suite-espera
branch: melhoria/v047-fila-suite-espera
commit: 1e04c56fe51c0165e112a1fcd5aab23ea52cc666
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047-fila-suite-espera (E1.171, code review da E1.131, classe C)

Diff revisado: `origin/develop...1e04c56f` (base e60183d0), 3 commits: `.githooks/pre-push` +62/-6, `tests/test_pre_push_fila.py` +158, specs `tests/mutantes/v047-fila-suite-espera.json` e `-2.json` (14 mutantes), `docs/hooks.md`, fragmento em `changelog.d/`. Instância que não fez a entrega.

## Achados
- A1 (recomendado) .githooks/pre-push:553 · o texto da trava só é regravado depois do `ja_no_remoto` (ls-remote, até 20 s, linhas 550 a 558): quem entra nessa janela vê a trava presa com o pid da dona anterior, já morta, e recebe "dona pid N morta" falso (linha 521). Gravar `pid/ns/desde` logo depois da `vez`, antes do ls-remote.
- A2 (recomendado) .githooks/pre-push:523 · o `else return 0` do aviso de trava velha é saída antecipada sem mutante declarado; o teste da dona viva o mata hoje, mas declarar o mutante (F15 na spec -2) deixa a trava da catraca explícita.

## Sondas

## Parecer
Aprovado. A entrega faz o que o cartão pede (E1.131: posição na fila, aviso de trava velha e a medida de envios barrados por dia em `<trava>.barrados`), sem liberar a trava nem pular a fila: o teste da dona morta confere que a trava segue presa e a suíte não roda. A troca do `flock -w` por laço de `flock -n` mantém o mesmo limite (F12) e a exclusão continua sendo a trava (`R-TETO`). O julgamento de dona morta pelo `kill -0`, só com pid numérico e no mesmo namespace, e só com "No such process", está correto e coberto (F6, F7, F13, F14). O registro não segue link nem toca arquivo de outro dono (F10); a segurança é portão próprio (E1.172, `R-SEGURANCA`). Texto da trava e nome das senhas passam por filtro antes do terminal. `docs/hooks.md` atualizado na mesma entrega. Commits limpos, Conventional Commits em português.

A1 é defeito real, mas de efeito só informativo (o aviso diz "parece velha" e manda conferir com `ps`; nada é liberado), por isso recomendado (`R-REVIEW`); a correção é mover duas linhas. A2 é cobertura de catraca, não defeito.

Tamanho (M14): 226 linhas de código e teste (68 do hook, 158 do teste), acima da orientação de 150; o corpo do PR traz `teto: excedido, 226 linhas, ...` com o motivo, um comportamento só (a espera na fila). Aceito.

Pendências fora deste portão: a catraca do PR 553 falha esperando o rótulo do dono, e o `forge-check pr` ainda não vê a linha `entrega conferida` do head 1e04c56f no histórico do pedido (Jarvis, E1.174, `R-PROVA`).

Provas (comando e saída):
- CI do PR 553 no head 1e04c56f (`gh pr checks 553`): bateria, bateria (pareceres, passos, python 3.14, verificações longas), instalação, suíte 3.12 e 3.14 (partes 1 a 3), teto de pulados e árvore já provada: `pass`; `catraca`: `fail` (rótulo do dono). Suíte não rerrodada.
- Teste novo: `python3 -m unittest tests.test_pre_push_fila`: `Ran 8 tests in 30.329s`, `OK`.
- Mutantes: `bin/forge-mutante --processos 1 tests/mutantes/v047-fila-suite-espera.json tests/mutantes/v047-fila-suite-espera-2.json` em rev 1e04c56fe51c: F1 a F14 `morreu` (linhas 409 a 546), `rc=0`.
- `bin/forge-mutante --cobertura --base e60183d0`: `não coberto: .githooks/pre-push` (shell não é analisado pela ferramenta); as guardas foram conferidas por leitura, linha a linha, contra F1 a F14 (A2 é a única saída sem mutante).
- `shellcheck .githooks/pre-push`: saída 0, sem achados.
