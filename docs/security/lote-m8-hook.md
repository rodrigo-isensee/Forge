---
tipo: revisao-seguranca
contrato: 1
pedido: lote-m8-hook
branch: melhoria/lote-m8-hook
commit: 0ff73965e955912d52fc078fa03d219a6f43e0a6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-26
---
# Review de segurança: lote-m8-hook

Escopo: `git diff 35057a2c5436f7415a9473bf4bd656b85264125c...0ff73965e955912d52fc078fa03d219a6f43e0a6`. Esta é a revalidação por delta do parecer `02f5224`, que reprovou o head `0e64acb`. O delta é `0e64acb..0ff7396` (`forge-check delta --parecer`): `.githooks/pre-push:240-241`, `:252`, `:266`, `:276`, `tests/test_pre_push_afetados.py:182-223`, `tests/mutantes/lote-m8-hook.json` e `changelog.d/lote-m8-hook.md:3`. Como o delta toca o controle do Forge, reli o hook inteiro de `:180` a `:314`, não só as linhas mudadas.

Ameaças consideradas:
- um envio que não é simples cair no caminho dirigido;
- o filtro se auto-julgar, inclusive por código da branch carregado pelo Python do plano;
- os bloqueios de conteúdo perderem a precedência;
- a prova de árvore verde ser anotada sem a suíte inteira.

## Gatilhos
`R-SEGURANCA`, gatilho "controles do Forge": o `.githooks/pre-push` é portão local (`R-MAIN`, `R-VERIFY`, `R-FLUXO`). Valem as decisões do dono de 2026-10-23 "A", 2026-10-24 "A" e 2026-10-24 "C".

## Resumo
**Aprovado, sem achado.** O A1 do parecer anterior foi fechado. O plano (`:266`) e a execução dirigida (`:276`) agora rodam com `python3 -I`. Com isso, um módulo da biblioteca padrão falso no `bin/` da branch não decide mais o plano nem zera a execução.

O dirigido passou a valer só para `refs/heads/melhoria/*` (`:252`). Isso endurece o controle e segue a decisão do dono.

Julguei uma a uma as cinco chamadas `python3` que continuam sem `-I` (`:195`, `:197`, `:272`, `:279`, `:282`). Nenhuma decide o plano nem escolhe o que roda. Elas são a suíte da branch, executada por desenho. Detalhe na verificação 2.

Testes do item: `python3 -m unittest tests.test_pre_push_afetados tests.test_testes_tocados.NaoEPortao`, 25 testes, OK. `shellcheck .githooks/pre-push` sem aviso. `bin/forge-mutante tests/mutantes/lote-m8-hook.json`: M4, M5, M6, M7, M9, M10, M11 e M12, todos mortos.

## Verificações
1. **A1 fechado** (`:266`, `:276`).
   - Sonda num clone em `$TMPDIR/security-engineer-lote-m8-hook/sonda-v2`, com `refs/remotes/origin/develop` no head revisado. Um commit muda o `README.md` e planta em `bin/` os falsos `json`, `argparse`, `re`, `subprocess`, `shutil`, `tempfile`, `unittest`, `ast`, `signal`, `pathlib` e `datetime`. Cada falso imprime `forge-testes: dirigido (falso)` e sai 0.
   - `python3 -I bin/forge-testes --listar` deu `suíte completa (bin/argparse.py sem mapa)`. Sem `-I`, deu `dirigido (falso)`.
   - Com `PYTHONPATH=bin` no ambiente e `-I`, o plano continua sendo a suíte completa.
   - `test_modulo_falso_em_bin_nao_decide_o_plano_nem_a_execucao` cobre o plano pelo hook de ponta a ponta, e o mutante M9 morre.
   - `test_modulo_falso_ja_na_base_nao_zera_a_execucao_dirigida` cobre o `-I` da execução, com o falso fora do diff, e o mutante M10 morre.
   - O filho que a execução dirigida abre (`bin/forge-testes:537`, `sys.executable -m unittest`, sem `-I`) põe a raiz no `sys.path`, não o `bin/`. Um `.py` novo na raiz não tem regra no `MAPA` (`bin/forge-testes:81-112`) e leva à suíte inteira. Nenhuma regra mapeia um `.py` da raiz.
2. **As chamadas sem `-I`, uma a uma.**
   - **`:195` e `:197`, modo `--suite`.** Usam `exec` e não chegam ao `so_parecer`, ao `dirigido` nem à anotação (`:307`). Rodam a suíte inteira da árvore local, como a pessoa pediu. Não decidem plano nem prova.
   - **`:272`, `so_parecer`.** O conjunto de classes é fixo no hook. O caminho só é tomado quando a árvore remota já está na prova (`:223`) e o delta só acrescenta arquivos em `docs/{reviews,security,qa,devops}/` (`:225-233`). Um `.py` na raiz ou em `scripts/` cai em `return 1` (`:231`), e um arquivo dentro de `docs/` não é importável como módulo de topo pelo `python3 -m unittest`. O código Python executado é o da árvore que já passou na suíte inteira. Não decide plano.
   - **`:279` e `:282`, suíte inteira.** Com `scripts/` (`:279`) ou a raiz (`:282`) no `sys.path`, um `scripts/json.py` falso poderia fazer a `suite-paralela.py` sair 0. Nesse caso a árvore seria anotada como verde (`completa=1`, `:307`).
     - Isso não é uma capacidade nova. A mesma branch pode editar o próprio `scripts/suite-paralela.py` ou um módulo de teste, que a suíte inteira executa por desenho. Nenhum dos dois está protegido: `hooks/conformidade.py:34` e `:130` protegem `.githooks`, `tests/config.json`, `.claude` e `.forge`, não `scripts/` nem `tests/test_*.py`.
     - Um `-I` nessas linhas não fecha nada: a suíte abre `unittest` sobre os testes da branch, e um teste pode sair 0 por conta própria.
     - Isso é diferente do A1. Lá existia uma guarda declarada contra o auto-julgamento do filtro (`:261-265`, decisão do dono) e ela podia ser contornada. Aqui não há guarda nem requisito.
     - Também não está no diff deste PR. Quem fecha esse risco é o CI do PR, que roda a bateria completa num ambiente que a branch não controla.
     - Um sombreamento por acidente (um auxiliar novo em `scripts/` com nome de módulo) quebraria a suíte, isto é, falharia fechado. Sem caminho realista, não há achado.
3. **Dirigido só para `melhoria/*`** (`:252`). Os destinos `feature/x`, `fix/x` e `chore/x` rodam a suíte inteira (`test_dirigido_so_vale_para_melhoria`, mutante M11). Main, homolog e develop continuam recusadas antes, dentro do laço das refs (`:106-132`, `exit 1`).
4. **Âncora do diff vigiado** (`:263-265`). Ela é o `merge-base` com a develop. `test_ancora_e_a_base_comum_com_a_develop_nao_a_ponta_da_develop` e o mutante M12 cobrem a troca pela ponta da develop. O resto do `dirigido` (`:251-260`) não mudou e continua falhando fechado, como no parecer anterior.
5. **Árvore verde.** `completa=0` só é atribuída no ramo dirigido (`:274`), e a anotação exige `completa = 1` (`:307`). Isso não mudou.
6. **Spec de mutantes.** Ela trocou M1, M2, M3 e M8 por M9 a M12, para caber no teto de 8 (E2 do pedido). Os testes das guardas que saíram da spec continuam no arquivo (`tests/test_pre_push_afetados.py:128`, `:138`, `:224`, `:229`), e as guardas continuam no hook (`:251`, `:255-257`). Não há regressão de controle.
7. **PA-7** (`docs/engineering/achados-recorrentes.md`): não há linha `AR-` registrada, então não havia item para conferir.

## Achados

## Detalhe dos achados
Não há achado.

Observação sem achado, que segue do parecer anterior e não muda com este PR: o portão local confia no código da branch e na cópia local. Isso inclui `refs/remotes/origin/develop`, que pode ser movida com `git update-ref`, a `scripts/suite-paralela.py` e os testes. Quem fecha esse risco é o CI do PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas usadas:
- `shellcheck`, sem aviso;
- `python3 -m unittest` nos testes do item;
- `bin/forge-mutante` na spec do pedido;
- `bin/forge-check delta`;
- sondas em `$TMPDIR/security-engineer-lote-m8-hook/`.

Ferramentas ausentes no PATH e não instaladas (`R-CUSTO`): `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner`. Este diff não toca workflow nem dependência, então a lacuna não afeta o veredito.
