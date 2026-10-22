---
tipo: review
contrato: 1
pedido: impl-n-qa
branch: melhoria/impl-n-qa4
commit: 738cfff89e751d0543ff977bde075c0ea45ffe13
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Review: impl-n-qa

Escopo lido: `git diff a3dbe226..738cfff8`, 11 arquivos em 76670d1 (item 34 com a R3 e a correção do A1 da qa3), 66fdc39 (item 65), bd1b485 (item 36) e 738cfff (fragmento), contra o desenho `docs/propostas/discovery-0.29.0/n-qa.md` e o adendo `docs/security/ameacas/n-qa.md`. A EXT-1 fica fora até a P-1 do dono. A branch foi refeita, então não há parecer anterior nela e o `forge-check delta` não se aplica. A leitura foi por delta contra a qa3, revisada no 7df9915.

## Achados

## Parecer
**Aprovado.** O A1 da qa3 (review 7df9915 e segurança 9e74609) está resolvido no próprio commit do item 34. O resto do lote é idêntico ao da qa3, e cada commit se reverte sozinho com a suíte inteira verde.

**Delta lido.** Comparei o patch de cada commit com o da qa3 (`git show` de um contra o outro, ignorando `index`):
- 66fdc39 contra 9e2c9fa: idêntico, exceto o deslocamento de uma linha num cabeçalho `@@` de `tests/config.json`;
- bd1b485 contra 51456c6: idêntico;
- 738cfff contra 1230d12: só o nome do fragmento (`impl-n-qa4.md`);
- `git diff 1d0c14e 76670d1`: só a correção do A1, em `bin/forge-testes` (`HERDADA`, `TodosExistiam`, `testes_da_base`, o parâmetro `existiam` de `da_base` e a chamada em `vermelho`), uma frase em `skills/qa-testing/SKILL.md` e seis testes em `tests/test_testes_tocados.py`.

Ficou como já lido, sem releitura, o que o 7df9915 e o 44a6406 conferiram: a R3 com o executor real, o A1 da qa2, os A2 a A4 da rodada antiga, a mutação nas guardas e o `tests/config.json` só com acréscimos.

**A correção do A1.** A entrada herdada (falha de carga, `setUpClass` ou `setUpModule`) só prova teste que a versão da base do módulo não tinha. A lista de testes da base vem de `git show` mais `ast`, sem executar nada. O teste que já existia sai como `não prova (herdada da base)`, que não conta como prova. Se a base do módulo estiver ilegível, todos os testes contam como existentes, ou seja, a falha é fechada. Rodei os seis testes novos numa cópia em `$TMPDIR/rv-nqa4`, com o `bin/forge-testes` de 1d0c14e (sem a correção):
- os dois de classificação dão ERROR;
- os três negativos dão FAIL. São eles o import novo no topo, o `setUpClass` novo e o `setUpModule` novo em módulo existente sem teste novo. O primeiro dá `AssertionError: 0 != 1`;
- o caso misto dá FAIL, com `tests.test_lib.T.test_um · ... · prova (API ausente)`.

Com a correção, o módulo passa: 65 testes OK. O teste da R3 (módulo novo com import no topo) continua dando 0.

**P3 = B, conferida à mão.** Usei um clone em `$TMPDIR/rv-nqa4` no HEAD 738cfff. Para cada commit, sozinho, rodei `git revert --no-commit` e depois a suíte inteira (`python3 -m unittest discover -s tests`), uma por vez, sob a trava da suíte:
- 76670d1: revert limpo, 1402 testes OK (skipped=1);
- 66fdc39: limpo, 1407 OK (o `tests/test_forge_mutante.py` sai junto, pela DECISÃO TÉCNICA de 10:38);
- bd1b485: limpo, 1437 OK;
- 738cfff: limpo, 1437 OK.

Commits em Conventional Commits em português, um por item mais o do fragmento.

Recomendações (não bloqueiam):
- `bin/forge-testes:320`: `testes_da_base` só segue a herança dentro do próprio módulo. Um teste que já existia na base e foi herdado de uma classe importada de outro módulo ainda pode ganhar prova herdada. Isso não acontece hoje: as classes importadas entre módulos de teste (`Raiz` em `test_voltas`, `Cenario` em `test_forge`) não têm métodos `test_`. A sugestão é tratar uma classe com base não resolvida no módulo, que não seja `unittest.TestCase`, como `TodosExistiam` quando o texto for tocado de novo.
- O mesmo trecho trata como novo um teste existente que só foi renomeado. Um teste existente que foi alterado para usar a API nova cai em "herdada" (falha fechada: sai 1 sem teste novo). O comportamento é coerente com o CA-5, mas vale uma frase na skill quando ela for tocada.
- Seguem da qa3: a chave `""` em `bin/forge-testes:336` para id de uma parte só, os detalhes do desenho §2.3 no item 36 e a duplicação entre os dois scripts, que vira cartão depois do merge.

Regras "ferramenta": o Forge não tem `docs/engineering/praticas.md` com "decidida por". A suíte, o shellcheck e a validação do plugin rodam no pre-push e no CI, e não as refiz fora da sonda da P3. A pendência continua: falta o `praticas.md`.
Segurança: o parecer é da E1.3 (`docs/security/impl-n-qa.md`, 343202e, aprovado sobre 738cfff) e não o refiz aqui.
