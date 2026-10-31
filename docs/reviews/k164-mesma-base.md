---
tipo: review
contrato: 1
pedido: k164-mesma-base
branch: melhoria/k164-mesma-base
commit: 84f20d3430e30bb79602a0809194c026e0561e87
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: k164-mesma-base

## Revalidação (volta 1, head 84f20d3)
- `forge-check delta --parecer docs/reviews/k164-mesma-base.md` (rc=0): intervalo `18721bc..84f20d3`; delta lido: `tests/hooks/parecer/pr-base-fora-do-fluxo-continua-estrita-bloqueia.json:1-98` (novo) e `tests/mutantes/k164-mesma-base.json:34-43` (M4). Já lido na rodada anterior: todo o resto da branch, sem mudança de código (`bin/`, `hooks/` iguais ao `18721bc`).
- A fixture abre o PR com `--base feature/y`, uma cópia da develop feita depois do merge puro dela na `feature/x` com pareceres no commit anterior; espera código 2 e `R-REVIEW`. Com a guarda trocada por `if False`, a base `feature/y` contém o merge e o parecer passaria a valer: a fixture é o que prende o requisito.
- `bin/forge-mutante tests/mutantes/k164-mesma-base.json` (rodado neste review, rev 84f20d3), rc=0: `M1 · morreu · hooks/parecer.py:383`, `M2 · morreu · hooks/parecer.py:374`, `M3 · morreu · bin/forge-check:622`, `M4 · morreu · bin/forge-check:613`.
- `bin/forge-mutante --cobertura --base 8c07b44...`: `coberta · bin/forge-check:613 · tests/mutantes/k164-mesma-base.json:M4`; seguem sem mutante as linhas 612 e 639 e as apagadas de `hooks/parecer.py` (já avaliadas: A2 recomendado; as demais sem efeito de afrouxar).
- M14 no head: 35 linhas de código contadas (`bin/forge-check` 21+7, `hooks/parecer.py` 3+4); a fixture nova e a spec ficam fora. Cumpre; um comportamento, uma classe em `hooks/` com corpus próprio (agora 3 fixtures).
- Veredito da revalidação: A1 resolvido, sem mudança de lógica; A2 e A3 seguem recomendados e não devolvem. Aprovado.

## Rodada 1 (head 18721bc)

Escopo revisado: `git diff 8c07b44..18721bc` (4 commits: fixtures antes do código, correção, spec de mutação, fragmento), item E1 do pedido. O E2 (intervalo de linhas a-b) está na branch `melhoria/k164-intervalo`, fora daqui.

## Achados
- A1 (bloqueante) bin/forge-check:613 · resolvido no 84f20d3 (fixture pr-base-fora-do-fluxo-continua-estrita-bloqueia e mutante M4, que morre). Era: a guarda da base fora do fluxo (modo estrito, requisito E1) sem teste; trocá-la por False sobrevivia à tests.test_hooks.
- A2 (recomendado) hooks/parecer.py:447 · o caminho git merge na integração passou a usar a base do fluxo, mas nenhuma fixture o cobre: voltar ao "HEAD" anterior sobrevive à tests.test_hooks. Sugestão: fixture de merge puro da develop seguido de git merge feature/x na develop, liberando.
- A3 (recomendado) tests/mutantes/k164-mesma-base.json:27 · a guarda do M3 descreve a fixture que bloqueia, mas o mutante (retorno None) é morto pela que libera; ajuste o texto para "a base resolvida chega ao cmd_pr".

## Verificação
- M14: cumpre. 35 linhas contadas (`bin/forge-check` 21+7, `hooks/parecer.py` 3+4); fixtures, spec, fragmento e `.md` ficam fora. Um comportamento só (a base do delta compartilhada); o intervalo a-b saiu para a `melhoria/k164-intervalo`. Mexe em `hooks/` com corpus próprio (2 fixtures em `tests/hooks/parecer/`), uma classe de comportamento.
- `bin/forge-mutante tests/mutantes/k164-mesma-base.json` (rodado neste review): `M1 · morreu · hooks/parecer.py:383`, `M2 · morreu · hooks/parecer.py:374`, `M3 · morreu · bin/forge-check:622`, rc=0.
- `bin/forge-mutante --cobertura --base 8c07b44...` (rodado neste review), rc=1: `sem mutante · bin/forge-check:612 · base or ''`, `sem mutante · bin/forge-check:613 · nome not in BASES_DO_FLUXO`, `sem mutante · bin/forge-check:639 · aviso`, `apagada · hooks/parecer.py:440(base) · chave in branches`, `apagada · hooks/parecer.py:375(base) · sha_base or None`. Os dois que pesam viraram A1 e A2, provados com mutação manual numa cópia da árvore (`git archive`): os dois sobrevivem à `tests.test_hooks` (55 testes, OK).
- Vermelho e verde do autor: fixtures no `970ffd0` antes do código; `tests.test_hooks` verde no `18721bc` (log do autor, rc=0).
- Shellcheck: sem shell tocado.

## Parecer
Reprovado só pelo A1. A correção está certa e simples: `base_do_delta` tira de `pr_da_cli` a regra da base (fluxo, remota antes da local, head contido na base volta ao diff literal) e o hook passa a usá-la, de modo que o merge puro da base depois do parecer deixa de invalidar no hook, como já não invalidava no `forge-check pr`; a mudança do autor depois do merge segue bloqueando (fixture `pr-mudanca-do-autor-depois-do-merge-da-base-bloqueia`). O `pr_da_cli` mantém a recusa explícita de `--base` fora do fluxo antes de chamar a função, então a CLI não muda.

O ponto que bloqueia: antes, o hook chamava `cmd_pr` sem base (estrito sempre), e o review e a segurança do `forge-check-lote` se apoiaram nisso para aceitar `--base` restrito só na CLI. Agora o hook passa a base do evento (`gh pr create --base <x>`, `gh pr ready`, `git merge`), e a única coisa que impede o autor de escolher uma base que já contém a própria mudança é o `if nome not in BASES_DO_FLUXO` da linha 613. O texto do pedido (E1) pede isso, e o código o faz, mas nenhum teste o prende: a mutação o apaga sem quebrar nada. Num caminho de `PROTEGIDOS`, que é portão, o requisito precisa de prova (fixture que bloqueia com base fora do fluxo e mutante declarado na spec). Sem mudança de lógica: só teste e spec.

A2 e A3 não devolvem. O A2 é o mesmo tipo de lacuna, mas o efeito de voltar ao comportamento antigo é ficar mais estrito, não mais frouxo. Para o review de segurança (E1.3), fica a observação de que `docs/security/forge-check-lote.md` e `docs/reviews/forge-check-lote.md` citam o hook "sem base" como premissa; com esta branch a premissa muda, e a nova guarda é a linha 613.
