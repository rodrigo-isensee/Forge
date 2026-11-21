---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-trilha
commit: a247ae11fac6c9ce96b3d56abe8b4f18763173a6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E63.21, revalidação da trilha CONFORMIDADE-SEGURANCA no head a247ae11)

Revalidação (H3, `R-REVIEW`) do parecer aprovado no head 7a739fca. Li só o delta de
`forge-check parecer delta docs/reviews/v0479-conformidade-trilha.md`: intervalo `7a739fca..a247ae11`, domínio "código e
testes", escopo sem o que veio da base (`develop` em c8e8a08d). Fora desse domínio nada foi relido.

## Delta lido
- `docs/hooks-fixtures.md`: índice regerado (3368 fixtures, `pesado` 27, prefixo `forgetestes-*`). `scripts/indice-fixtures.py --conferir` no a247ae11: `docs/hooks-fixtures.md: em dia`, rc 0.
- `docs/hooks.md` (linha de `pesados`) e `tests/test_hooks.py:3236` (`--dirigida` vira `--afetados`): idênticos à base c8e8a08d (vêm do #747, PESADO-VERSOES-FORA-DA-FILA); `git diff c8e8a08d a247ae11` não toca esses trechos. `--afetados` está em `LEVES_DO_FORGE_TESTES` (`hooks/pesado.py:294`); o teste roda verde.
- `tests/mutantes/v0435-review.json` R6: o `de` agora casa a guarda real `hooks/conformidade.py:2801` (tupla com `help.autocorrect`, A13 da segurança E63.7); o `para` troca só `alias.` por `aliasx.` e mantém o ramo `help.autocorrect`. Rodado: `R6 · morreu · hooks/conformidade.py:2801`.

## Ferramentas (citadas, não refeitas)
- Suíte inteira: fica com o CI do PR (sem PR nesta etapa; o brief pede revisão sem suíte local).
- `bin/forge-mutante tests/mutantes/v0435-review.json --ids R6 --processos 1`: R6 morreu.
- `python3 -m unittest tests.test_hooks.PesadoClassePelosArgumentos.test_formas_leves_e_citacoes_nao_sao_pesadas`: OK.

## Parecer
Aprovado no head a247ae11. O delta é a entrada da base, o índice regerado e o mutante R6 realinhado à guarda já aprovada no
7a739fca; nenhum comportamento novo além do que a base trouxe.
