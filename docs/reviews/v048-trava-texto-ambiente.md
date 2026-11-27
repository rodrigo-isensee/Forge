---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-trava-texto-ambiente
commit: 2ba3d2d0a724d5e0a1903968a1982ed0177f24bb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v048-trava-texto-ambiente (#949, TRAVA-TEXTO-LIMITE-AMBIENTE)

1ª rodada completa (E1.3), classe C (teste de controle). Delta lido desde a base `b3dfe154`: `tests/test_pre_push_trava.py` (+8/-2), `tests/mutantes/v048-trava-texto-ambiente.json` (novo, 3 mutantes), `changelog.d/v048-trava-texto-ambiente.md` (novo). Nenhuma linha de código do hook mudou; teto H1 não se aplica (0 linhas de código).

- ci: 2ba3d2d0a724d5e0a1903968a1982ed0177f24bb verde

## Conferência
- Faz o que o cartão pede: o teste tira do stderr só a linha do aviso de locale do bash antes de medir; o limite de 600 e a ausência de ESC ficam; a trava passa a ter um segundo campo (o pid lido pela fila) com controle e sem fim, o que exercita o corte `${pid:0:12}` de `.githooks/pre-push:506`.
- Reprodução: o teste da base, nesta máquina (LANG en_US.UTF-8 sem o locale instalado), falha com `666 not less than or equal to 600`; o da branch passa (1 teste, OK).
- Mutantes declarados (`bin/forge-mutante`, 1 processo): M1 e M2 (`.githooks/pre-push:60`) e M3 (`.githooks/pre-push:506`) morreram. O M3 prova que o novo conteúdo da trava pega o pid sem corte.
- Alcance do regex: a sonda com o aviso real do bash (`bash: line 1: warning: setlocale: LC_ALL: cannot change locale (...)`) o remove por inteiro; a linha da fila com o texto da trava fica intacta, também quando vem junto do aviso. O texto da trava passa por `tr -cd '[:print:]'` e não traz quebra de linha, então não forma linha própria. Só uma linha do hook cujo conteúdo imite `: line N: warning: setlocale: ` some inteira (A1); com o conteúdo fixo do teste, sem gatilho.
- Commits: um commit de teste, Conventional Commits em português, com fragmento em `changelog.d/`.

## Achados
- A1 (recomendado) tests/test_pre_push_trava.py:26 · regex sem âncora no formato do bash: uma linha do hook com texto da trava que imite ': line N: warning: setlocale: ' some inteira. Sugestão: exigir 'warning: setlocale: LC_[A-Z]+: cannot change locale \(' na linha. Sem gatilho com o conteúdo fixo do teste.

## Sondas

## Parecer
Aprovado. O teste volta a medir o texto do hook, não o caminho da cópia, e ficou mais forte: com o conteúdo antigo, sem espaço, o campo do pid vinha vazio e o corte não era exercitado (lido no `read` de `.githooks/pre-push:501`). A1 é recomendado e vira cartão depois do merge.
