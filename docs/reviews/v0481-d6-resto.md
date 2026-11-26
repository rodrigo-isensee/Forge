---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 1f127ddd1ac05ae80a9306dda56802dec43ee50d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Code review: resolução do conflito com a develop, volta E11.26 (D6 parte a; v0481 E11.27, PR #877)

Revisado por delta: `e66e30a2..1f127ddd`, lido pelo `forge-check parecer delta` (o apontamento foi `docs/hooks-fixtures.md`, do domínio do review). O delta é o merge `1f127ddd`, que traz a develop até o `8f0a7313` (#885 e #895), já revisada nos PRs de origem. Parecer anterior: aprovado no `200d8b37`.

- ci: 1f127ddd1ac05ae80a9306dda56802dec43ee50d verde

## Parecer
**Aprovado.** A resolução só junta os dois lados e não muda a lógica do item. Também não perde teste.

**Resolução (`git show --remerge-diff 1f127ddd`).** Só dois arquivos diferem do merge automático:
- Em `tests/test_hooks.py`, a resolução tira os marcadores e põe as duas linhas em branco entre `SalvarAoParar` (do item) e `ModoPorGrupo` (da develop). `RecusaComFifoNoRegistro` vem logo depois, sem nenhuma linha mudada.
- Em `docs/hooks-fixtures.md`, só muda a contagem: 3584 do item e 3583 da develop dão 3587 no head. `scripts/indice-fixtures.py --conferir` responde "em dia", e o corpus tem 3587 casos.

Nenhum arquivo de produção do item (`hooks/salvar.py` e afins) aparece no delta.

**Nenhum teste perdido.** Contei os métodos `test_` de `tests/test_hooks.py`: 213 na base comum, 242 no item (29 a mais) e 224 na develop (11 a mais). O head tem 253, que é 213 + 29 + 11.

**Verificadores.** Rodei, no head, `python3 -m unittest` com as classes `SalvarAoParar`, `ModoPorGrupo`, `RecusaComFifoNoRegistro` e `OrdensEmVigor` (a vizinha do conflito): 63 testes OK. Os mutantes que vieram da develop foram provados no PR de origem, e o delta não tem mutante novo do item.

**CI.** Nos runs 45737895249 e 45737895074, com o `headSha` conferido como `1f127ddd`, deram 17 verdes e 7 pulados (só os de push na develop). Estão verdes as 10 partes da suíte, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação`, `teto de pulados`, `árvore já provada` e `catraca`. Ficam vermelhos só `bateria (pareceres)`, que espera este parecer, e `bateria`, que a agrega. Não rerrodei o SHA.
