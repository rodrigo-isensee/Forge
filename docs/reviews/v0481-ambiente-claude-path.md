---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v0481-ambiente-claude-path
commit: df4b2bf9acc9db23f376b385f50f59ccf42dc467
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 (E13.7, PR #965, ambiente: claude novo no PATH)

1.ª rodada completa no head df4b2bf9, contra a develop a1971853 (Base-sha do brief, igual à `origin/develop` lida).

## Achados
- A1 (bloqueante) scripts/preparar-estacao.sh:197 · a regex nova entre aspas simples dispara SC2016 (info) e o `shellcheck` sai 1: o job "bateria (verificações longas)" do run 46166032218 no df4b2bf9 está vermelho. Ponha `# shellcheck disable=SC2016` com o motivo na linha de cima, como a 198 já faz.
- A2 (recomendado) tests/test_ambiente_recriacao.py:219 · `bash_com_falsos` e o teste da sessão nova (linha 247) herdam `os.environ` inteiro no subprocesso; o `rodar` do mesmo arquivo já tira GIT_, GH_, XDG_ e FORGE_. Use o mesmo filtro.
- A3 (recomendado) tests/test_ambiente_recriacao.py:277 · `comando() + ""` não faz nada; tire o `+ ""`.

## Sondas
- S1 · `shellcheck scripts/preparar-estacao.sh` no df4b2bf9 · espera: rc=0 (na base a1971853 sai 0) · obtido: rc=1, SC2016 (info) na linha 197; o log do job 141043709196 mostra o mesmo

## Retomada e escopo
- `git diff a1971853 df4b2bf9` e `git diff a1971853...df4b2bf9` dão o mesmo resultado (7 arquivos, +195/-5): a merge-base é a própria develop, então a retomada não trouxe nada velho por cima dela.
- O comportamento é um só (o claude novo vem primeiro e o postStart do ambiente falha com ERRO, sem seguir em silêncio): a guarda do `.bashrc`, o `&&` do `mktemp`, o comando manual pela main e os avisos e o README pelo `/root/.local/bin/claude`. Isso dá 14 linhas de código, abaixo do teto H1.
- GH-CONFIG-DERRUBA-SANDBOX: o `~/.config/gh` já vem da develop (`persistir` na linha 441 e a verificação na 470), então essa parte não pede mudança neste diff, como diz a entrega do E13.5.
- Histórico: c711ac15 e 1ff74c20 têm a mesma mensagem, e o segundo só move os testes. Isso não bloqueia e some se o PR for integrado com squash.

## Verificação
- Testes do diff: `python3 -m unittest tests.test_ambiente_recriacao tests.test_guia_varios_projetos`: 22 testes, OK.
- Mutantes: `bin/forge-mutante --processos 1 tests/mutantes/v0481-ambiente-claude-path.json`: os 8 morreram (M1 a M8). As guardas mudadas têm um mutante cada: o `grep ... && return` (M5, M6), o `&&` do `mktemp` (M1) e o `exit 1` (M2). O `--cobertura --base a1971853` dá `não coberto` para o JSON e para o shell, que ele não analisa, e por isso conferi as guardas à mão.
- CI do df4b2bf9 (run 46166032218): "bateria (verificações longas)" falhou (SC2016, A1) e a suíte em 5 partes ficou `pending`. Sem CI verde, sem linha `ci:`.

## Parecer
Reprovado só pelo A1, que é um defeito provado: o CI do head está vermelho no shellcheck que o próprio diff causou. A correção é de uma linha, a diretiva com o motivo em scripts/preparar-estacao.sh:196, e o autor roda o `shellcheck` local antes do envio. O resto está correto. A regex só aceita o `.local/bin` seguido de `:`, logo na frente do PATH, os testes cobrem o fim do PATH, a linha que não se repete e a sessão nova que acha o claude certo, e o postStart para sem a pasta temporária. A2 e A3 são recomendados e viram cartão depois do merge.
