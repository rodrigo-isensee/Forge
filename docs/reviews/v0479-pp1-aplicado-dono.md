---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pp1-aplicado-dono
commit: 4d60adf4f5d43fc8f55c8a7f27727e0823b18674
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E52.2 (PP1-APLICADO-PELO-DONO), revalidação no head 4d60adf4

Delta lido (`forge-check parecer delta`, 58da41ec..4d60adf4; base origin/develop 5ccac0b): `bin/forge-check` (`isencao_do_dono`, `patch_revisado_do_dono`, `parecer_cita_o_patch`, chamada em `linhas_de_entrega`), `changelog.d/v0479-pp1-aplicado-dono.md`, `tests/mutantes/v0479-pp1-aplicado-dono{,-3,-4}.json` e `tests/test_conf_escopo.py` (`PatchDoDono.isencao`, classe `PatchRevisadoDoDono`). Só o delta; o resto vale dos pareceres anteriores (A1 e A2 anteriores resolvidos, (c) A3 em vigor).

A4 da segurança (E52.6): `parecer_cita_o_patch` passa a receber `(pedido, branch)` da entrega conferida e só aceita parecer `tipo: revisao-seguranca`, `parecer: aprovado` (o `riscos-aceitos` sai), `pedido:` e `branch:` iguais aos conferidos, fora de `PASTAS_RECUSADAS_DE_PARECER` (aceites/ e ameacas/, a mesma constante já usada na linha 7346). Só aperta a aceitação; nenhum caminho novo isenta. Teste próprio cobre S3 (outra branch), outro pedido, riscos-aceitos, S4 (aceites/) e ameacas/, com o controle positivo em `docs/security/outro.md`. Os trechos `de` de M24, M25 e M28 aparecem uma vez só no arquivo.

## Achados
- A1 (recomendado) tests/mutantes/v0479-pp1-aplicado-dono.json:30 · O `para` do M3 ainda chama `patch_revisado_do_dono` com 4 argumentos: o mutante morre por TypeError, não por pular a guarda. Atualize o `para` para a assinatura nova com `and False` (aberto desde 58da41ec).

## Parecer
Aprovado. Classes `PatchRevisadoDoDono` e `PatchDoDono` rodadas: 19 testes, OK. `forge-mutante --conferir --base 58da41ec`: trecho de cada spec no lugar. `--cobertura --base 58da41ec`: linhas 2304, 2306 e 2307 cobertas (M31, M28, M24/M25/M29/M30). Mutantes do delta (`--ids M3,M23,M24,M25,M28,M29,M30,M31`, 1 processo): todos morreram, rc 0. Suíte inteira fica no CI do PR (R-REVIEW).
