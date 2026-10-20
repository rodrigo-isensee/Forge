---
tipo: review
contrato: 1
pedido: rotulo-so-dono
branch: melhoria/rotulo-so-dono
commit: d6b9b352af4b1ee40f4d3d2e06b20909a3321546
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Review: o rótulo afrouxa-regra só do dono do Forge (E1.2, revalidação da volta 3)

Revisor independente (outra instância do `tech-lead`, D-ETAPAS-INST = A). Este parecer substitui o anterior (aprovado sobre `6ec5095`). Revalidação por delta: `forge-check delta` não foi necessário, li direto `3b266e4...d6b9b35` (1 commit, `d6b9b35`, 2 arquivos: uma fixture e `tests/test_hooks.py`). Já lido e mantido do parecer anterior: hook, `tests/config.json`, as demais fixtures `rotulo-so-dono-*` e as voltas 1 e 2.

## O que foi conferido
- **Causa da volta:** a fixture antiga (anterior a este pedido) dependia do `gh` real da máquina; no CI, sem credencial, o hook barrava a remoção do rótulo (a volta 2 exige a conta dona também para remover). A volta 3 deixa a fixture hermética.
- **Fixture `contrib-sessao-forge-raiz-pr-edit-rotulo-libera`:** continua com `esperado.codigo: 0`; o comando é o mesmo (`gh pr edit 70 --remove-label afrouxa-regra`). Ganhou `bin/gh` falso que imprime o login do dono, marcado em `executaveis`, e o `PATH` com `{tmp}/proj/bin` à frente. O dono remove o rótulo e libera, sem rede nem credencial.
- **Teste estrutural novo:** `test_fixtures_da_sessao_do_forge_que_citam_o_rotulo_usam_o_gh_falso` percorre as fixtures com `forge: false` e `plugin.json` do Forge na raiz que citam o rótulo e exige `bin/gh` nos arquivos, em `executaveis` e o `PATH` começando por `{tmp}/proj/bin:`. Fixture sem `gh` falso falha a asserção; há mínimo de 10 itens (item 11 do checklist), sem teste de ausência.
- **R-QA, asserções:** nenhuma asserção saiu nem ficou mais frouxa; o esperado da fixture segue 0, o diff só acrescenta linhas de teste e dados.
- **Escopo:** `git diff --stat` sobre `hooks/` e `tests/config.json` no delta é vazio; o hook e os invariantes não mudaram. Só `tests/` mudou.
- **Ferramenta (saída citada):** `python3 -m unittest tests.test_hooks` sobre `d6b9b35`, sem credencial de `gh` no ambiente: `Ran 32 tests in 64.066s OK`. A suíte completa (884 OK) e `scripts/validar-plugin.sh` (OK) são do autor, na E1.1v3.
- **Regras da fábrica:** `R-CUSTO` sem custo (gh falso, sem rede); `R-NEUTRO` mantido (o login do dono só aparece em `gh` falso de teste). Commit Conventional Commits em português, coerente. Segurança: parecer próprio do `security-engineer`, citado; o hook não mudou.

## Achados

## Detalhe dos achados
1. Recomendação 4 anterior, ainda de pé: o dono vem do `plugin.json`, não da URL do remoto como dizia o E2; registrar no corpo do PR · severidade: recomendado.
2. `hooks/conformidade.py`, `rotulo_no_argumento` (já lido): falso positivo em aspas simples, para o lado fechado · nada a fazer agora · severidade: recomendado.

## Pendências para o merge (não são do review)
- Rótulo `afrouxa-regra` pela conta do dono, depois do último push (catraca por mudança em `hooks/conformidade.py`).
- QA (E1.4) sobre o novo head e `forge-check pr` antes do merge.

## Parecer
Aprovado: a volta 3 torna a fixture antiga hermética sem mudar o esperado nem afrouxar asserção, e o teste estrutural impede a regressão. Não impede o QA.
