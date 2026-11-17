---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conferida-por-branch
commit: 8b9fa8df4b12a8822d5cb58ddc256cb003fc35cf
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (conferida por branch, E1.185; review E1.194; revalidação E2.56)

## Achados
- A1 (recomendado) bin/forge-check:2186 · o ramo `revisados` (MP1311) ainda testa só `e_ancestral(desde, base_sha)`, sem `ja_na_base`; um Revisar-sha desta branch que já entrou na develop seguiria aceito como Desde. Usar `ja_na_base(raiz, desde, base_sha, base_ref)` deixa a regra única (R-PROVA).

## Sondas

## Parecer
Revalidação (E2.56), por delta: `forge-check parecer delta docs/reviews/v047-conferida-por-branch.md` leu o intervalo `7c91b13d..8b9fa8df`, sem o que veio da base, no domínio `bin/forge-check`, `bin/forge-testes` e `tests/test_testes_tocados.py`. Os trechos de `pqs_de_pre_envio`, `linha_do_ci_do_parecer`, `--texto` e `test_hook_erro_libera` vieram da develop pelo merge `ef371633` (pais c496f36e e cb45a962, o Base-sha), limpo: `git show --cc ef371633` sem hunk de resolução. O commit próprio do delta é `8b9fa8df` (2+2 linhas): põe `test_conferida_por_branch` em `FORGE_CHECK` de `bin/forge-testes` e sobe a contagem de 82 a 83 em `tests/test_testes_tocados.py:67`, com o comentário da origem. Correto: o teste novo exercita o `bin/forge-check` e, sem o mapa, o pre-push dirigido não o rodaria quando o `forge-check` muda. `bin/forge-testes --listar bin/forge-check` agora o lista; `Mapa.test_forge_check_roda_os_modulos_dele` e `tests.test_conferida_por_branch` rodados aqui: 5 testes OK. Sem guarda nova no delta, sem mutante a declarar. A1 segue recomendado e aberto (`bin/forge-check:2186`, mesma linha). Suíte inteira: fica para o CI do PR, ainda sem PR; não rerrodada. Aprovado no head 8b9fa8df.

Review anterior (7c91b13d):
Aprovado. Intervalo `origin/develop..7c91b13d` (merge-base 6517ff14, igual ao Base-sha), 3 commits em Conventional Commits.

O que muda: `ja_na_base` junta o Base-sha e a `origin/<base>` (`ref_da_base`) e substitui o `e_ancestral(c, base_sha)` em `desde_valido` e `base_sha_como_desde`; `base_ref` desce a todos os chamadores (`recusa_do_desde`, `gerar_volta`, `mensagem_de_entrega`, `corrigir_derivados`, `cmd_entrega_conferir`, `veredito_do_desde`). Com isso, a conferida de outro item que o merge da develop trouxe ao head deixa de ser o Desde, e o intervalo volta ao Base-sha. A ref só tira candidatas, então o intervalo só cresce: uma `origin/develop` reescrita não esconde código (falha fechada). O filtro de commit já na base continua sendo o de antes, sem mudança neste diff.

Os dois testes de `MergeDaBaseDepoisDoBrief` com expectativa mudada (o brief pediu atenção a eles):
- `test_merge_base_sem_ancora_fica_o_base_sha` (tests/test_selo_e_entrega.py:1197): `rc` passa de 1 a 0. O rc=1 antigo fixava justamente o defeito (a conferida trazida virava Desde e `agents/outro.md`, da develop, aparecia fora do escopo). O nome do teste continua verdadeiro (sem âncora, sem `base: merge-base`, fica o Base-sha), e agora ele afirma o intervalo `<Base-sha>..` e a ausência do arquivo da develop. A mudança é coerente com `test_conferida_trazida_pela_develop_nao_e_desde` e não é afrouxamento.
- `test_head_ja_na_develop_mantem_o_base_sha` (:1245): o `assertNotIn("pendente: intervalo vazio")` virou `assertIn("intervalo: <Base-sha>..")`. A asserção nova é mais forte, porque um intervalo que parte do Base-sha não é vazio. A guarda do "head já na base" continua coberta pelo `assertNotIn("base: merge-base")`.

Testes: `tests/test_conferida_por_branch.py` (4 casos, entre eles o controle da conferida da própria branch, que segue sendo o Desde) e `MergeDaBaseDepoisDoBrief` rodados aqui: 12 testes OK. Mutantes declarados (2 specs, 10 guardas, uma por linha): `bin/forge-mutante` deu 10 de 10 mortos, rc=0. `bin/forge-mutante --cobertura --base 6517ff14` deu todas as condições mudadas cobertas, rc=0. Os subprocessos dos testes herdam o padrão de `se.Repositorio`. Suíte inteira: fica para o CI do PR, que ainda não existe (o brief pede "sem PR"); não rerrodada.

Tamanho (M14): 26+18 em `bin/forge-check`, 83 no teste novo e 6+2 no teste mudado dão 135 linhas, dentro de 150, com um comportamento só. O fragmento `changelog.d/v047-conferida-por-branch.md` está presente.
