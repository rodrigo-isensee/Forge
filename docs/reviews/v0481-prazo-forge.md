---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 07a1bf5c6420ea060b517927cf06cb8090e7bb6f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481

Review por delta (E7.59, conflito do E7.58) de 22a57afc a 07a1bf5c. Li o delta pelo `forge-check parecer delta docs/reviews/v0481-prazo-forge.md` (intervalo 22a57afc..07a1bf5c, escopo sem o que veio da develop; no domínio, `docs/hooks-fixtures.md`, `hooks/conformidade.py` e `tests/test_hooks.py`). Do autor: o merge 39d6f4f4 da develop 22ceb2c8 (traz o #878, revisado no PR de origem; ordem do dono de 26/11 07:54) e o merge 07a1bf5c, que só junta o parecer ec272bb6 (`git diff --stat 39d6f4f4 07a1bf5c`: só `docs/reviews/v0481-prazo-forge.md`).

## Parecer
Aprovado: a resolução do conflito não muda o patch do item e o que veio da develop entrou igual.

- **Conflito.** `git show --remerge-diff 39d6f4f4` mostra a mão do autor só em `docs/hooks-fixtures.md`: 3603 fixtures (3594 do item mais 9 do #878) e `conformidade` 2725. `python3 -I scripts/indice-fixtures.py --conferir`: "em dia"; `ls tests/hooks/*/*.json | wc -l`: 3603; `ls tests/hooks/conformidade/*.json | wc -l`: 2725.
- **O que veio da develop entrou igual.** `hooks/conformidade.py` e `tests/test_hooks.py` mesclaram sem conflito: as linhas `+`/`-` de `git diff 020e4af7 22ceb2c8` (o #878 sobre a base anterior) e de `git diff 22a57afc 07a1bf5c` nesses dois arquivos são idênticas (`diff` vazio): `ultima_raiz`, `forge_check_publica` e a chamada em `Guarda`, e `test_fixtures_do_publicar`. Os mutantes `tests/mutantes/v0481-g2-1-publicar*.json` vêm do #878, sem mudança.
- **Teste apontado pela catraca** (`test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada`, valor esperado 4.0 → 3.5 em `sono_do_git_lento`): é mudança do item, não da junção. Vem do 1d6692f5 (E7.32, prazo do merge em 7,5 s), que baixou o `sleep` da fixture `parecer/v0455-merge-com-git-lento-decide-no-prazo-longo.json` de 4 para 3,5 s; o corpo do teste é o mesmo no 22a57afc e no 07a1bf5c (md5 igual) e já foi revisado nas voltas anteriores. O aviso não barra.
- Rodei os testes tocados: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_publicar tests.test_hooks.Hooks.test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada`: "Ran 2 tests ... OK". Nenhuma spec de mutante do item mudou no delta.

CI (runs 45815173541 e 45815173436, headSha 07a1bf5c):
- Verdes: as 10 partes da suíte (3.12 e 3.14), os 2 tetos de pulados, `bateria (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)` e `árvore já provada na develop`.
- Vermelhos que não contam para o G3: `bateria (pareceres)` ("commit: desatualizado: docs/hooks-fixtures.md mudou depois do parecer", espera este parecer), `catraca` (R-CONFORMIDADE em `hooks/_comum.py` e `hooks/conformidade.py`, espera o rótulo `afrouxa-regra` do dono; mais o aviso de valor esperado trocado acima) e `bateria`, que os agrega.

- ci: 07a1bf5c6420ea060b517927cf06cb8090e7bb6f verde
