---
tipo: review
contrato: 1
pedido: lote-m8-mapa
branch: melhoria/lote-m8-mapa
commit: 80d90ee950eca2b23983286520bff5107e415195
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-26
---
# Review: lote-m8-mapa

PR 1 do M8 com a opção C do dono (2026-10-24): todo módulo de teste no diff roda a suíte inteira. O diff vai de `f142001` a `80d90ee` (8 commits) e mexe em `bin/forge-testes`, `tests/test_testes_tocados.py`, na spec `tests/mutantes/lote-m8-mapa.json` e no fragmento `changelog.d/lote-m8-mapa.md`. Revisor independente: não fui o autor do lote.

## Achados
- A1 (recomendado) bin/forge-testes:25 · a docstring (e :71, :473, :536) já diz que o pre-push filtra pelo plano, mas o hook só muda no PR 2 e `NaoEPortao` (tests/test_testes_tocados.py:393, :408) ainda afirma o contrário; alinhar o texto no PR 2 ou dizer "a partir do PR 2"

## Parecer
**Aprovado.** Não há defeito de comportamento provado, requisito da opção C descumprido nem segurança com gatilho.

Pontos que o brief pede para conferir:
- **O mapa sem a regra de módulo de teste.** Saem a regra `tests/(test_…)\.py` do `MAPA`, o `IMPORTADO_POR` e o caso especial em `planejar` (`bin/forge-testes:151-168`). Fiz uma sonda com `planejar`. `tests/test_fechar.py`, `tests/helpers.py` e `tests/__init__.py` dão `completo` com o motivo "sem mapa". `hooks/doutor.py` e `dev/.claude-plugin/x` seguem dirigidos. `planejar([])` dá `("dirigido", [])`. `bin/forge-testes --listar tests/test_hooks.py docs/regras/R-MAIN.md` dá "suíte completa (tests/test_hooks.py sem mapa)". Também entram regras novas (`LEITORES_DE_TEXTO`, a família de `hooks/`, `scripts/conferir-reversao.py`, `dev/.claude-plugin`). Elas só alargam o mapa, e `MapaCobreOQueOsTestesLeem` as confere.
- **O `--vermelho` sem `--modulos`** (`bin/forge-testes:403-410`). Ele usa os módulos de teste do diff que ainda existem mais o plano dos caminhos que não são teste, e todos quando esse plano é completo. Com diff só de teste, `planejar([])` devolve um plano vazio e o resultado é só o módulo do diff, que é o que se espera. O módulo apagado fica de fora (`m in todos`). Isso está correto.
- **Critério de C, itens 1 a 5.**
  - C.1: `test_todo_teste_importado_por_outro_leva_quem_importa_a_suite_inteira` (:468) exige no mínimo 31 arestas.
  - C.2: `test_toda_varredura_de_pasta_conhecida_leva_o_modulo_a_suite_inteira_ou_ao_plano` (:478) exige no mínimo 1000 arquivos e que os três módulos que varrem `tests/` estejam no conjunto.
  - C.3: `test_modulo_de_teste_no_diff_cai_na_completa_com_o_motivo_sem_mapa` (:93). `bin/forge-sugerir` segue dirigido em `test_caminhos_conhecidos_rodam_so_os_modulos_do_mapa`.
  - C.4: `test_vermelho_usa_o_modulo_de_teste_do_diff_mais_o_plano_dos_outros_caminhos` (:664). O autor trocou o brinquedo da proposta (`lib.py` com `test_lib.py`) por `bin/forge-sugerir`. A troca está correta: `lib.py` não tem regra, então o plano da proposta daria completo e o item não provaria nada.
  - C.5: M1 (a regra devolvida ao `MAPA`) e M2 (o `planejar` puro no `--vermelho`) estão na spec.
- **O enxugamento para 397 linhas** (`b761042`, `80d90ee`). Saíram a fonte sintética de importação e varredura, o rastreio de `import_module` dinâmico e o teste do `--vermelho` com caminho sem mapa.
  - A fonte sintética é o item 3 da opção A e não está no critério de C.
  - Com C, todo módulo de teste dá completo, seja qual for a forma de importação. Por isso o rastreio dinâmico não muda o plano. Os mínimos de 31 e de 1000 impedem que as conferências passem sem verificar nada.
  - O M5 que o teste retirado guardava morre pelo `test_teste_que_chama_funcao_que_a_base_nao_tem_e_prova_de_api_ausente` (execução abaixo).
  - Nada do que saiu era requisito.
- **`NaoEPortao` não exige o hook.** A classe (`tests/test_testes_tocados.py:392-418`) está igual à da `develop`: nenhum portão cita o script e o pre-push roda a suíte inteira. O `.githooks/pre-push` não está no diff e não cita `forge-testes`. A exigência do hook fica para o PR 2, como a proposta pede. O A1 é a única consequência disso: um texto que se adianta ao PR 2.

Regras de ferramenta (cito a saída, não refiz):
- `python3 -m unittest -q tests.test_testes_tocados` na worktree em `80d90ee` deu `OK` (19 s).
- `bin/forge-mutante tests/mutantes/lote-m8-mapa.json` deu M1 a M7 `morreu` (spec `034a3b05…`, rev `80d90ee950ec`).
- A suíte completa não rodou aqui, por instrução do brief. O pedido registra o pre-push da entrega com `1955 OK`.
- O repositório não tem `docs/engineering/praticas.md`, então não há regra "leitura" de projeto a aplicar. Usei o checklist da skill.

Teto M14: `git diff --numstat --no-renames origin/develop...HEAD` dá 59+21 (`bin/forge-testes`) e 279+38 (`tests/test_testes_tocados.py`), 397 linhas contáveis. A spec de mutantes (fixture) e o fragmento ficam fora da conta. Fica dentro do teto, sem exceção. O diff não mexe em `hooks/` nem em `PROTEGIDOS`.

Outros pontos:
- PA-7 (`docs/engineering/achados-recorrentes.md`) está sem linhas, então não há item a conferir.
- `R-NEUTRO` e `R-CUSTO`: nada específico de projeto e nada pago.
- Os commits estão em Conventional Commits em português, um por passo.
- O fragmento `changelog.d/lote-m8-mapa.md` está presente.

Riscos, sem bloquear:
- A `develop` andou 3 commits depois de `f142001`. Entraram módulos de teste novos, entre eles `tests/test_fechar_orfao.py`. Com C eles não mudam o plano, mas a conferência `MapaCobreOQueOsTestesLeem` só roda sobre o conjunto mesclado no CI do PR.
- O A1 fica para o PR 2.
