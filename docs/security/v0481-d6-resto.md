---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 1f127ddd1ac05ae80a9306dda56802dec43ee50d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 E11.29 (#877, D6 parte a: hook `salvar`, volta E11.26 por delta)

## Gatilhos
Gatilhos: hook novo fora do sandbox, controle do git (R-VERIFY core.hooksPath, R-MAIN); sem rede no hook (opção b do dono, 25/11 07:37).

Delta lido (`forge-check parecer delta`, `e66e30a2..1f127ddd`): um único commit, o merge `1f127ddd` (pais `e66e30a2` e `8f0a7313`, a develop com o #895 e o #885). `git show --remerge-diff 1f127ddd` mostra que a resolução só toca dois arquivos:
- `tests/test_hooks.py`: tira os três marcadores de conflito e põe as duas linhas em branco entre `SalvarAoParar` (do item) e `ModoPorGrupo` (da develop). Nenhuma linha de teste muda. Os conjuntos de classes e `def test_` batem com a união exata da base `6cc4cd5a` mais os acréscimos dos dois lados (30 do item, 14 da develop), e nenhum lado perde teste.
- `docs/hooks-fixtures.md`: só a contagem passa a 3587, que é o número de `tests/hooks/*/*.json` no head. `scripts/indice-fixtures.py --conferir` diz "em dia".

`hooks/salvar.py`, `hooks/salvar.json` e `hooks/hooks.json` estão iguais aos de `e66e30a2` (o lado aprovado em `200d8b37`). `hooks/conformidade.py`, `hooks/conformidade.json`, `bin/forge-check` e as skills estão iguais aos de `8f0a7313` (a develop, já revisada no PR de origem).

Testes no clone em `1f127ddd`:
- `python3 -m unittest tests.test_hooks.SalvarAoParar tests.test_hooks.ModoPorGrupo tests.test_hooks.RecusaComFifoNoRegistro`: 40 testes OK. `Travou` é a exceção auxiliar e não é classe de teste.
- `bin/forge-mutante tests/mutantes/v0481-d6-resto-7.json`: M40 (`hooks/salvar.py:127`) e M41 (`:156`) morreram.

CI do PR no head exato (run 45737895249): verdes as suítes 3.12 e 3.14 (partes 1 a 5), `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação`, os tetos de pulados, `árvore já provada na develop` e `Catraca`. Vermelhos só `bateria (pareceres)` (R-REVIEW e R-SEGURANCA: pareceres em `200d8b37`, desatualizados pelo merge), que este parecer resolve, e `bateria`, que herda dele. Nenhum dos dois é do código.

- ci: 1f127ddd1ac05ae80a9306dda56802dec43ee50d verde

Estado dos achados anteriores (parecer em `200d8b37`): nenhum achado aberto. O merge não toca o hook.

## O que aperta, o que é neutro e o que afrouxa
- **Aperta:** nada neste delta. A resolução não acrescenta controle.
- **Neutro:** toda a resolução. Os marcadores saem, as classes dos dois lados ficam inteiras e a contagem do índice gerado foi atualizada. A lógica do item (`hooks/salvar.py`, `hooks.json`) não muda. O que veio da develop (#885 com o modo por grupo, #895 com a forma `via` da linha do CI) chega idêntico ao do PR de origem, que já tem parecer e afrouxamento declarado.
- **Afrouxa:** nada novo neste delta. O afrouxamento do item continua o já aprovado pelo dono em 25/11 17:37: o commit WIP é só local, com `core.hooksPath=/dev/null`, e não confere cada gravação. O rótulo `afrouxa-regra` está no PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `gitleaks`, Semgrep, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH (lacuna). A revisão foi manual: remerge-diff do merge, a comparação dos conjuntos de testes, as classes tocadas rodadas localmente e a spec de mutantes do item.
