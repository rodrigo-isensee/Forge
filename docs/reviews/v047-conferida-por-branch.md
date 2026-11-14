---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conferida-por-branch
commit: 7c91b13d795b743b129ef41f55ab755b5eee4ad2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (conferida por branch, E1.185; review E1.194)

## Achados
- A1 (recomendado) bin/forge-check:2186 · o ramo `revisados` (MP1311) ainda testa só `e_ancestral(desde, base_sha)`, sem `ja_na_base`; um Revisar-sha desta branch que já entrou na develop seguiria aceito como Desde. Usar `ja_na_base(raiz, desde, base_sha, base_ref)` deixa a regra única (R-PROVA).

## Sondas

## Parecer
Aprovado. Intervalo `origin/develop..7c91b13d` (merge-base 6517ff14, igual ao Base-sha), 3 commits em Conventional Commits.

O que muda: `ja_na_base` junta o Base-sha e a `origin/<base>` (`ref_da_base`) e substitui o `e_ancestral(c, base_sha)` em `desde_valido` e `base_sha_como_desde`; `base_ref` desce a todos os chamadores (`recusa_do_desde`, `gerar_volta`, `mensagem_de_entrega`, `corrigir_derivados`, `cmd_entrega_conferir`, `veredito_do_desde`). Com isso, a conferida de outro item que o merge da develop trouxe ao head deixa de ser o Desde, e o intervalo volta ao Base-sha. A ref só tira candidatas, então o intervalo só cresce: uma `origin/develop` reescrita não esconde código (falha fechada). O filtro de commit já na base continua sendo o de antes, sem mudança neste diff.

Os dois testes de `MergeDaBaseDepoisDoBrief` com expectativa mudada (o brief pediu atenção a eles):
- `test_merge_base_sem_ancora_fica_o_base_sha` (tests/test_selo_e_entrega.py:1197): `rc` passa de 1 a 0. O rc=1 antigo fixava justamente o defeito (a conferida trazida virava Desde e `agents/outro.md`, da develop, aparecia fora do escopo). O nome do teste continua verdadeiro (sem âncora, sem `base: merge-base`, fica o Base-sha), e agora ele afirma o intervalo `<Base-sha>..` e a ausência do arquivo da develop. A mudança é coerente com `test_conferida_trazida_pela_develop_nao_e_desde` e não é afrouxamento.
- `test_head_ja_na_develop_mantem_o_base_sha` (:1245): o `assertNotIn("pendente: intervalo vazio")` virou `assertIn("intervalo: <Base-sha>..")`. A asserção nova é mais forte, porque um intervalo que parte do Base-sha não é vazio. A guarda do "head já na base" continua coberta pelo `assertNotIn("base: merge-base")`.

Testes: `tests/test_conferida_por_branch.py` (4 casos, entre eles o controle da conferida da própria branch, que segue sendo o Desde) e `MergeDaBaseDepoisDoBrief` rodados aqui: 12 testes OK. Mutantes declarados (2 specs, 10 guardas, uma por linha): `bin/forge-mutante` deu 10 de 10 mortos, rc=0. `bin/forge-mutante --cobertura --base 6517ff14` deu todas as condições mudadas cobertas, rc=0. Os subprocessos dos testes herdam o padrão de `se.Repositorio`. Suíte inteira: fica para o CI do PR, que ainda não existe (o brief pede "sem PR"); não rerrodada.

Tamanho (M14): 26+18 em `bin/forge-check`, 83 no teste novo e 6+2 no teste mudado dão 135 linhas, dentro de 150, com um comportamento só. O fragmento `changelog.d/v047-conferida-por-branch.md` está presente.
