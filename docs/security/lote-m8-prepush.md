---
tipo: revisao-seguranca
contrato: 1
pedido: lote-m8-prepush
branch: melhoria/lote-m8-prepush
commit: e025ed8a210a7c97796adc5075854066bc0e0b9a
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: lote-m8-prepush

Escopo: revalidação 2 por delta (`forge-check delta --parecer`, intervalo `a15a5697609a207eb56aca0b0c64e6f26c1a1e1d..e025ed8a210a7c97796adc5075854066bc0e0b9a`), sobre o diff `3c66b881af31817ce5d2dde996c7ca56d54cb511...e025ed8a210a7c97796adc5075854066bc0e0b9a`. O delta toca `.githooks/pre-push`, `bin/forge-testes`, `tests/test_pre_push_afetados.py`, `tests/test_testes_tocados.py`, `tests/mutantes/lote-m8-prepush.json` e o fragmento do changelog. Por ser controle do Forge, reli por inteiro o `dirigido()` do hook e o `planejar` do filtro, não só as linhas do delta.

## Gatilhos
`R-SEGURANCA`, controles do Forge: o pre-push (bloqueios de `R-MAIN`, `R-VERIFY`, `R-FLUXO` e a prova de árvore verde) depende do plano do `bin/forge-testes`, que é o filtro de um portão local.

## Achados
- A5 (bloqueante) bin/forge-testes:117 · classe mapa mais estreito que os testes que executam o arquivo (a mesma do A1, variante módulo de teste importado por outro): IMPORTADO_POR é escrito à mão e só cobre test_forge e test_portao_diff_proprio; no envio dirigido, mudar tests/test_fechar.py não roda os 13 test_fechar_* que o importam, e o mesmo vale para test_doutor (4 módulos), test_voltas (5), test_volta_por_delta (2), test_hooks (1), test_atualizar (1) e test_forge (faltam 3)

## Detalhe dos achados
**A1 (fechado).** `python3 bin/forge-testes --listar` dá, para `hooks/agentes.py`, `hooks/_comum.py` e `hooks/vigia.py`, um plano dirigido que inclui `test_agentes_clone`, `test_agentes_hash_brief` e `test_textos_dono_f10` (`bin/forge-testes:95`). Para `bin/forge-changelog`, o plano inclui `test_conferir_release` (`:81`). A conferência `MapaCobreOQueOsTestesLeem` passou a ler o código pela árvore sintática e reconhece `HOOKS / ...`, `ler(...)`, `joinpath` e o caminho montado com variável, com falha fechada (`tests/test_testes_tocados.py:129-201`). `test_a_familia_dos_testes_que_executam_hooks_e_bin_roda_no_envio_dirigido` prova os quatro casos. Refiz a varredura de `hooks/`, `bin/` e `scripts/` contra o texto de todos os `tests/test_*.py`. Tirando o ruído (nome citado como texto, cópia de semente, o próprio `test_testes_tocados`, que só cita), não sobra nada.

**A5 (bloqueante; mesma classe do A1, ainda aberta numa variante que a minha 1.ª varredura não cobriu: a importação entre módulos de teste).** Evidência: o `bin/forge-testes:117` declara `IMPORTADO_POR = {"test_forge": ("test_hooks", "test_guarda_git"), "test_portao_diff_proprio": ("test_ambiente_git",)}`, e o `planejar` (`:150-151`) só acrescenta quem importa a partir dessa lista. Só que 27 módulos importam outro módulo de teste (`grep -E '^\s*(import|from) test_' tests/*.py`):
- `test_fechar` é importado por 13 `test_fechar_*`, que herdam `base.Fechar.tearDown` e `base.SCRIPT` (por exemplo, `tests/test_fechar_config.py:10,22`);
- `test_doutor` é importado por `test_doutor_custo`, `test_doutor_relogio`, `test_doutor_protecao_gh` e `test_sessao_versao_carregada`;
- `test_voltas` é importado por `test_pedido_fora`, `test_erros_no_brief`, `test_medidas_m14b`, `test_conferencia_registrar` e `test_forge`;
- `test_volta_por_delta` é importado por `test_conferencia_base_dono` e `test_erros_no_brief`;
- `test_hooks` é importado por `test_guarda_conferente`, e `test_atualizar` por `test_sessao_versao_carregada`;
- de quem importa `test_forge`, faltam `test_conferencia_base_dono`, `test_volta_por_delta` e `test_guarda_conferente`.

Reprodução: `python3 bin/forge-testes --listar tests/test_fechar.py` dá `dirigido (test_fechar)`. Hoje é isso que o pre-push roda (`.githooks/pre-push:271-274`). A volta acrescentou à mão uma única entrada (`test_portao_diff_proprio`), e não a família. A conferência do mapa não olha importação entre testes.
Caminho do problema: não é ataque. Uma mudança num módulo de teste base (por exemplo, `test_fechar.Fechar` ou `test_voltas.Raiz`) quebra os módulos que o herdam, passa no pre-push verde e chega à branch remota. Entre os módulos afetados estão os testes do `forge fechar` e do conferente, que são controles do Forge. O CI do PR ainda barra a mudança antes da `develop`. Severidade: média, a mesma do A1, pelo mesmo motivo.
Correção mínima: calcular `IMPORTADO_POR` pela árvore sintática dos `tests/test_*.py` (`import test_x`, `from test_x import ...`), de forma transitiva, em vez de mantê-lo à mão. Uma alternativa: manter a lista à mão e acrescentar uma conferência em `tests/test_testes_tocados.py` que derive as importações reais e exija que cada uma esteja no plano (no mesmo molde do que já existe para o `bin/forge-check` na `:438-449`). Os módulos de apoio que não são `test_*` (`apoio_versao_defasada.py`, `ambiente_git.py`, `gh_falso.py` etc.) já caem na suíte completa por "sem mapa", e isso está certo. Esforço: P. Dono: `tech-lead`.

**A2 (fechado).** Antes de chamar o filtro, o hook calcula sozinho `merge-base` com a base remota e confere `git diff --name-only -- bin/forge-testes tests/config.json .githooks/` (`.githooks/pre-push:261-263`). Se a saída não for vazia, roda a suíte inteira. `test_diff_que_toca_o_filtro_o_mapa_ou_o_hook_roda_a_suite_inteira` prova os três caminhos com um filtro permissivo já na base, e o caso de controle mostra que, sem a conferência, o filtro permissivo venceria. O caminho dirigido só depende do `bin/forge-testes`, que importa só a biblioteca padrão (`bin/forge-testes:28-37`). Nota sem achado: um erro do `git diff` na `:263` dá saída vazia e segue para o filtro. Isso é falha aberta só em tese, porque `ancora` já foi validado como commit.

**A3 (fechado).** A base é `refs/remotes/origin/develop^{commit}`, resolvida uma vez para um sha (`.githooks/pre-push:257`), e esse mesmo sha vai para o `--listar` e para a execução (`:264`, `:274`). `test_base_e_a_ref_remota_mesmo_com_branch_local_de_mesmo_nome` cria `refs/heads/origin/develop` e prova que ela não vence. A mensagem da `:273` ainda diz "base origin/develop". É só texto, sem efeito.

**A4 (fechado).** Os comentários das `:241-242` e `:301-303` agora dizem que o `so_parecer` também anota a árvore, por herança da árvore remota já verde.

**Conferido sem achado no delta.**
- Continuam antes do filtro, sem mudança, os bloqueios de `main`, `homolog`, `develop` e de envio não fast-forward.
- A guarda de árvore limpa tem agora o teste do mutante (`tests/test_pre_push_afetados.py:112`), e o `! -L` da ferramenta tem o seu (`:122`).
- A anotação de árvore verde continua só com `completa=1`.
- `R-CUSTO`: nada pago.
- Achados recorrentes (PA-7, `docs/engineering/achados-recorrentes.md`): a lista está vazia, nada a conferir. A classe deste A1/A5 aparece pela 1.ª vez num parecer de segurança e ainda não entra na lista.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `shellcheck` sobre `.githooks/pre-push` (limpo). Rodei `python3 -m unittest tests.test_pre_push_afetados tests.test_testes_tocados` (92 testes, OK). Refiz a varredura própria do mapa contra o texto dos testes e contra as importações entre testes (só leitura, `$TMPDIR`). Faltaram no PATH, e ficam como lacuna (não instalo nada): `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner`. O diff não traz dependência, segredo nem workflow.
