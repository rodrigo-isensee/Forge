---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0480-d3-teste-enfraquecido
commit: 8daa161194a94fffbeba29e5a1a087aa0a9343fb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 E2.2 (D3, catraca recusa teste afrouxado; PR #867), revalidação por delta

Delta revisado: `e7a71a8e..8daa1611` (`forge-check parecer delta`: "revalida: sim (este parecer barrou: o último parecer não é aprovado)"). Código: `tests/catraca.py` +21/-4 (`_so_constantes`, `_vacua`, cruzamento `da_branch` em `regra_testes_afrouxados`), `tests/test_catraca.py` +32, mutantes `-5` (de/para ajustados), `-8` e `-9` (novos), fragmento em `changelog.d/`. Pareceres de QA e segurança da rodada anterior entram no delta sem código. H1: dentro do teto.

## Ferramenta (citada, sem refazer)
- CI do PR (#867): `catraca` vermelha só por `R-CONFORMIDADE: mudança em tests/catraca.py` (rótulo do dono, decisão de 24/11); `bateria (pareceres)` vermelha pela falta dos pareceres; suíte em andamento na leitura, o merge espera o verde.
- Mutação do delta rodada aqui: `bin/forge-mutante --processos 1` em `-5`, `-8` e `-9`: 15 mutantes, todos mortos (D3H1 a D3H7, D3E1 a D3E8).
- Testes do item: `python3 -m unittest tests.test_catraca.TestesAfrouxados tests.test_catraca.TestesNoCi`: 41 testes, OK.

## Leitura
- A1 corrigido: na volta, só barra o teste que também tem valor trocado contra a base (`da_branch`). O teste novo reproduz a S1 do parecer anterior (develop troca `== 4` por `== 5` depois da aprovação, merge na branch) e não acha violação; D3H1 prova que o cruzamento é o que o faz passar. Valor trocado de novo pela branch na volta segue barrando (`test_valor_trocado_na_volta_contra_a_versao_aprovada_barra`); valor restaurado ao da base não barra, coberto por `test_volta_que_restaura_o_valor_da_base_barra_so_pela_perda_dura` (D3H2).
- A2 (recomendado anterior) adiantado pelo autor: asserção só de constantes não conta nem tem valor esperado; `assert True` no lugar da asserção barra como asserção a menos.
- `TestesNoCi` ganha a guarda de raiz ausente (8daa1611): falha por asserção, não por erro.
- Changelog atualizado com o comportamento novo.

## Achados
- A1 (recomendado) tests/catraca.py:681 · `_vacua` lê o `msg=` como argumento: `self.assertTrue(True, msg=m)` conta como asserção (S1), embora o `msg=` não seja valor esperado (docstring de `_perfil_do_teste`). Cartão: excluir o keyword `msg` de `_so_constantes`.

## Sondas
- S1 · `_perfil_do_teste` de `def test_a(self): m='x'; self.assertTrue(True, msg=m)` · espera: 0 asserções · obtido: 1
- S2 · `_perfil_do_teste` de `def test_a(self): self.assertTrue(True)` · espera: 0 asserções · obtido: 0

## Parecer
Aprovado no head 8daa1611: o bloqueante A1 anterior está corrigido, com teste espelho da sonda e mutante morto; o delta não quebra os testes do item. O A1 desta rodada é recomendado (o caso exige `msg=` com variável numa asserção vácua) e vira cartão depois do merge.
