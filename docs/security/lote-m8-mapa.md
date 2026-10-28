---
tipo: revisao-seguranca
contrato: 1
pedido: lote-m8-mapa
branch: melhoria/lote-m8-mapa
commit: 80d90ee950eca2b23983286520bff5107e415195
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-26
---
# Review de segurança: lote-m8-mapa

Escopo: `git diff f142001c7e870c7b80c87d5e67438b70f538f2a6...80d90ee950eca2b23983286520bff5107e415195`, 4 arquivos (`bin/forge-testes`, `tests/test_testes_tocados.py`, `tests/mutantes/lote-m8-mapa.json`, `changelog.d/lote-m8-mapa.md`). Este é o PR 1 do M8, com a opção C do dono: todo módulo de teste no diff roda a suíte inteira. O hook fica para o PR 2.

Ameaças consideradas:
- um módulo de teste no diff gerar plano dirigido e deixar de rodar quem depende dele;
- uma varredura de pasta escapar do mapa;
- o `--vermelho` deixar de rodar um teste mudado;
- caminho da linha de comando sair do repositório ou virar opção;
- o filtro entrar num portão de CI.

## Gatilhos
`R-SEGURANCA`, gatilho "controles do Forge": o mapa decide o que o pre-push roda (decisões do dono de 2026-10-23 "A", 2026-10-24 "A" e 2026-10-24 "C").

## Resumo
**Aprovado.** Todo módulo de teste no diff cai na suíte completa: novo, apagado, renomeado ou importado por outro, e também o caminho fora do padrão. Nenhuma varredura de pasta do Forge escapa do mapa. O `--vermelho` segue a especificação C. Ele pode deixar de rodar um teste herdado de um módulo de teste mudado e sair 0 com falha no HEAD, o que foi provado num repositório de brinquedo (R1). Ele é evidência, e não portão: o CI do PR, o review e o QA rodam a suíte inteira. Por isso R1 é recomendação. Há uma segunda recomendação baixa (R2). Nenhum bloqueante. Testes do lote: `python3 -m unittest tests.test_testes_tocados`, 77 testes, OK.

## Verificações
1. **Módulo de teste no diff → completa.**
   - Nenhuma regra do `MAPA` (`bin/forge-testes:81-112`) começa por `tests/`, e todas usam `re.fullmatch`. Uma sonda sobre `planejar` deu `completo` para `tests/test_x.py` (novo), `tests/test_forge.py` (importado por `test_hooks` e `test_guarda_git`), `tests/sub/test_x.py`, `tests/Test_X.py`, `tests/__init__.py`, `tests/catraca.py`, nome com quebra de linha e nome entre aspas (`core.quotePath`).
   - O apagado aparece no `git diff --name-only` (`:134`). O renomeado lista os dois caminhos por causa do `--no-renames` (`:133-134`).
   - Na linha de comando, `caminhos_pedidos` (`:139-148`) normaliza `..` e recusa o que cai fora do repositório. `hooks/../tests/x.py` só chega ao `planejar` sem normalizar se for chamado direto, e nem o git nem a linha de comando o produzem.
   - `test_todo_teste_importado_por_outro_leva_quem_importa_a_suite_inteira` confere as arestas reais de importação.
2. **Varredura de pasta.**
   - Toda regra do mapa inclui `test_forge`. Por isso as varreduras com base em variável de `tests/test_forge.py:70-76`, `:349-351`, `:419-421` e `:457-459`, que a conferência AST do lote pula, ficam cobertas.
   - Fiz uma sonda própria, mais larga: todo literal de um `tests/test_*.py` que nomeia uma pasta do Forge, cruzado com o plano de cada arquivo dela. Ela só encontrou falsos positivos: o literal monta um repositório de brinquedo em `$TMPDIR`, ou o script citado (`scripts/suite-paralela.py`, `scripts/conferir-release.py`, `scripts/promover-homolog.py`, `scripts/reexecutar-provas.py`) não tem regra e cai na completa.
   - `hooks/doutor.py` casa a regra própria antes de `hooks/.*`. Conferi que nenhum hook executado por `test_agentes_*` ou `test_textos_dono_f10` o importa (`hooks/agentes.py:23-24` importa `_comum` e `pesado`).
3. **`--vermelho`.** Com `--modulos`, o filtro é explícito e a saída marca "restrito por --modulos" (`:399-400`, já na base). Sem `--modulos`, ele roda os módulos de teste do diff mais o plano dos outros caminhos (`:408-409`). As lacunas estão em R1 e R2.
4. **Sem injeção e fora dos portões.**
   - Não há `shell=True` no script. `--` antes de um caminho começado por `-` é tratado como caminho (`test_caminho_comecado_por_hifen_so_depois_de_dois_hifens`).
   - `.githooks`, `.github`, `hooks/` e `bin/forge-check` não citam `forge-testes`. As citações em `scripts/conferir-reversao.py:6,19` e `tests/config.json:460,468` já estavam na base e estão fora do diff.

## Achados

## Detalhe dos achados
**R1 (recomendado, baixa): o `--vermelho` não roda quem importa um módulo de teste mudado e pode sair 0 com falha no HEAD.**
- Evidência: `bin/forge-testes:409` (`modificados | plano`). O docstring diz "Saída 0 = há prova e nada cai no HEAD" (`:15`).
- Reprodução:
  1. Num repositório de brinquedo, `tests/test_a.py` define um mixin `Base.test_herdado` e `tests/test_b.py` herda dele.
  2. O diff muda `bin/forge-sugerir` e o mixin.
  3. `forge-testes --vermelho HEAD~1` roda `test_a,test_forge,test_sugerir`, imprime `prova (asserção)=1` e sai com `rc=0`.
  4. Já `unittest discover` dá `FAILED (failures=1)` em `test_b.U.test_herdado`.
- No Forge, 13 módulos `test_fechar_*` importam `test_fechar`, e `test_hooks` e `test_guarda_git` importam `test_forge`. Na base, o `IMPORTADO_POR` cobria os dois importadores de `test_forge`, e este diff o retirou.
- Caminho de ataque: nenhum. O `--vermelho` é evidência que o autor e o QA colam no parecer, e não um portão (`NaoEPortao`). O CI do PR, o review e o QA rodam a suíte inteira e pegam a falha. O comportamento segue o texto da decisão C.
- Correção mínima: no `--vermelho` sem `--modulos`, somar os módulos que importam um módulo de teste do diff. A varredura `ast` de `MapaCobreImportacaoEVarredura.importados` serve para isso. Outra opção é cair em `todos` quando houver importador. Mais um caso em `Vermelho` com mixin herdado. Esforço P. Dono: `tech-lead`. Se a mudança alterar a decisão C, ela vai ao usuário pelo Jarvis (`R-DECISAO`).

**R2 (recomendado, baixa): módulo de teste com nome fora de `test_[a-z0-9_]+` é revertido como produção e não roda no `--vermelho`.**
- Evidência: `bin/forge-testes:53` e `:394-398`. `TESTE_DO_DIFF` e `NOME_DE_MODULO` exigem minúsculas e `_`. O `unittest discover` (padrão `test*.py`) carrega também `tests/testfoo.py` ou `tests/test_Foo.py`. Um arquivo assim no diff volta à base na cópia B e fica fora de `todos`.
- Hoje não há arquivo assim em `tests/`, e o comportamento já existia na base. No modo normal, ele cai na completa, então o pre-push não perde nada.
- Correção mínima: recusar com saída 2 (sem veredito) quando um `tests/test*.py` do diff não casar com `NOME_DE_MODULO`. Esforço P. Dono: `tech-lead`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática e sondas locais em `$TMPDIR/security-engineer-lote-m8-mapa/`, com `python3 -I` e repositórios de brinquedo. Não havia `gitleaks`, `semgrep`, `zizmor`, `actionlint` nem `osv-scanner` no PATH, e o diff não toca workflow nem dependência. Isso fica registrado como lacuna.
