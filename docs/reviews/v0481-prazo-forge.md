---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 22a57afc418542f52f1e306f0ddc4e51ed213f57
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481

Review por delta (E7.55, volta E7.54) de ecb13af6 a 22a57afc. Li o delta pelo `forge-check parecer delta docs/reviews/v0481-prazo-forge.md` (intervalo ecb13af6..22a57afc; base 8f0a731 → 020e4af, escopo sem o que veio da develop; no domínio, `docs/hooks-fixtures.md` e `tests/test_hooks.py`). Do autor: só o merge 22a57afc da develop 020e4af7, que traz o #875, o #877, o #895, o #901, o #903, o #904 e a marca da 0.47.19, já revisados nos PRs de origem (ordem do dono de 26/11 07:54).

## Parecer
Aprovado: a resolução do conflito não muda o patch do item.

- **Patch do item igual.** As linhas `+`/`-` de `git diff 34ab6714 ecb13af6` (base antiga → head aprovado) e de `git diff 020e4af7 22a57afc` (base nova → head), fora pareceres e o índice gerado, são idênticas (960 linhas, `diff` vazio). O `tests/test_hooks.py` mesclou sem conflito e entra igual dos dois lados.
- **Conflito.** `git diff-tree --cc 22a57afc` mostra a mão do autor só em `docs/hooks-fixtures.md`: a contagem passa a 3594 e entra a seção `salvar` (do #877). `python3 -I scripts/indice-fixtures.py --conferir`: "em dia"; `ls tests/hooks/*/*.json | wc -l`: 3594.
- **Nenhuma linha de código nem de spec de mutante** do item mudou no delta: não há mutante novo a rodar nem módulo de teste tocado pelo autor. As duas falhas locais por prazo de 120 s em `pesado/mesma-sessao-libera` sob carga ficam com o autor e o QA; não reproduzi.

CI:
- No 22a57afc, as 10 partes da suíte e os tetos de pulados foram cancelados pelo push dos pareceres do QA e da segurança (concorrência do workflow); por isso `bateria (python 3.14)` e `bateria` caem ("partes: cancelled; pulados: cancelled"). `bateria (passos)`, `bateria (verificações longas)`, a instalação e a `árvore já provada` estão verdes. `bateria (pareceres)` espera este parecer e a `catraca` o rótulo do dono (R-CONFORMIDADE em `hooks/_comum.py` e `hooks/conformidade.py`, mais o aviso de valor esperado trocado, que não barra).
- O e922db75 descende do 22a57afc só por pareceres (`git diff --stat 22a57afc e922db75`: `docs/qa/` e `docs/security/`); a suíte dele vale pelo head revisado (forma via, G3.7, aceita pelo dono em 25/11 07:27). Check-runs do e922db75: as 10 partes da suíte, os 2 tetos de pulados, `bateria (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)`, a instalação e a `árvore já provada` verdes; vermelhos só `bateria (pareceres)`, `bateria` e `catraca`, que não contam para o G3.

- ci: 22a57afc418542f52f1e306f0ddc4e51ed213f57 verde via e922db75e67bc04890d966a5fa6c2473787140ed
