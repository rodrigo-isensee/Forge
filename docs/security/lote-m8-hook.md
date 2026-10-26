---
tipo: revisao-seguranca
contrato: 1
pedido: lote-m8-hook
branch: melhoria/lote-m8-hook
commit: 0e64acb2341f43de138ebfdfe405edb264617d11
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-26
---
# Review de segurança: lote-m8-hook

Escopo: `git diff 35057a2c5436f7415a9473bf4bd656b85264125c...0e64acb2341f43de138ebfdfe405edb264617d11`, 5 arquivos (`.githooks/pre-push`, `tests/test_pre_push_afetados.py`, `tests/test_testes_tocados.py`, `tests/mutantes/lote-m8-hook.json`, `changelog.d/lote-m8-hook.md`). É o PR 2 do M8: o pre-push de branch roda só os testes afetados pelo `bin/forge-testes` quando o envio é simples e o plano é dirigido; fora disso, roda a suíte inteira.

Ameaças consideradas:
- um envio que não é simples cair no caminho dirigido;
- o filtro julgar a própria mudança;
- os bloqueios de conteúdo perderem a precedência;
- a prova de árvore verde ser anotada sem a suíte inteira.

## Gatilhos
`R-SEGURANCA`, gatilho "controles do Forge": o `.githooks/pre-push` é portão local (`R-MAIN`, `R-VERIFY`, `R-FLUXO`). As decisões que valem aqui são as do dono de 2026-10-23 "A", 2026-10-24 "A" e 2026-10-24 "C".

## Resumo
**Reprovado por um bloqueante (A1).** Os bloqueios de conteúdo continuam antes de qualquer caminho. Cada envio que não é simples cai na suíte inteira. A árvore verde não é anotada no caminho dirigido.

A falha está na guarda contra o filtro se auto-julgar. O hook roda `python3 bin/forge-testes`, e assim o diretório `bin/` da própria branch entra no início do `sys.path`. Um arquivo novo `bin/<módulo da biblioteca padrão>.py` não tem regra no mapa e por isso devia levar à suíte inteira. Em vez disso, ele toma o lugar do módulo que o filtro importa e decide o plano. Provei com um repositório-sonda: o push passou com zero testes. Testes do item: `python3 -m unittest tests.test_pre_push_afetados tests.test_testes_tocados.NaoEPortao`, 21 testes, OK. `shellcheck .githooks/pre-push` sem aviso.

## Verificações
1. **Bloqueios de conteúdo antes de qualquer caminho.**
   - Main, homolog e develop são recusadas em `.githooks/pre-push:127-131`. O envio não fast-forward e o objeto remoto ausente são recusados em `:111-126`.
   - Tudo isso roda dentro do laço de leitura das refs (`:106-132`), com `exit 1`. Fica antes da trava, do `so_parecer` (`:268`) e do `dirigido` (`:271`).
   - `test_bloqueios_de_conteudo_valem_antes_do_filtro` confere as três branches e o histórico reescrito, sem nenhuma marca de teste rodado.
   - O `--no-verify` não passa pelo hook. Quem o recusa é o `hooks/conformidade.py`, sem mudança neste diff.
2. **Envio que não é simples cai na suíte inteira** (`dirigido`, `:247-267`).
   - Várias refs: `n_refs` conta também as linhas de remoção (`:107`), e `:249` pede exatamente uma.
   - Ref que não é branch: `:250`. Sha local malformado ou zerado: `:251-252`.
   - Ferramenta ausente ou que é link: `:253`.
   - HEAD diferente do sha enviado: `:254`.
   - Árvore suja: `:255` usa `--untracked-files=all`. O `.forge/` (log do filtro) é ignorado pelo `.gitignore:20` e não suja a árvore.
   - Base: só `refs/remotes/origin/develop`, resolvida para um sha (`:257`) e passada igual ao plano e à execução (`:264`, `:274`). Uma branch local chamada `origin/develop` não a substitui (`test_base_e_a_ref_remota_mesmo_com_branch_local_de_mesmo_nome`).
   - Base desatualizada: o merge-base fica mais velho e o diff, maior. Isso roda mais testes, nunca menos.
   - Diff vazio: o filtro diz "nada alterado", a saída não começa por `forge-testes: dirigido (` e o hook roda a suíte inteira (`:265-266`).
   - Diff que toca `bin/forge-testes`, `tests/config.json` ou `.githooks/`: a conferência fica no próprio hook (`:263`), sobre o mesmo intervalo âncora..HEAD que o filtro usa. Os mutantes M4 e M5 cobrem essa conferência.
   - Falha nessa conferência: as dependências executáveis do filtro ficam de fora dela (A1).
3. **A árvore verde não sai do dirigido.**
   - `completa=0` só é atribuída no ramo dirigido (`:272`), e a anotação exige `completa = 1` (`:305`).
   - O `so_parecer` segue anotando como antes, porque só passa sobre uma árvore remota que já estava na prova.
   - Um push dirigido não anota nada. O próximo push só de parecer sobre essa árvore não acha prova e roda a suíte (dirigida ou inteira).
   - `test_so_os_modulos_do_mapa_rodam_e_nao_anotam_a_arvore_verde` confere isso.
4. **Fora dos portões de CI.** `NaoEPortao` segue vigiando `.github`, `hooks`, `scripts/ci-local` e `bin/forge-check`. Em `.githooks/`, só o `pre-push` pode citar o filtro (`test_so_o_pre_push_cita_o_script_em_githooks`). A bateria completa do CI do PR não muda.

## Achados
- A1 (bloqueante) .githooks/pre-push:264 · classe guarda de auto-julgamento incompleta (código da branch executado pelo filtro fora da conferência do diff): `python3 bin/forge-testes` põe bin/ no sys.path; um bin/json.py novo, sem regra, decide o plano e o push passa com zero testes

## Detalhe dos achados
**A1.** Evidência: `.githooks/pre-push:264` e `:274`. Ambas chamam `python3 bin/forge-testes` sem `-I`. O filtro importa `json`, `argparse`, `ast`, `re`, `shutil`, `tempfile`, `unittest` e outros módulos da biblioteca padrão (`bin/forge-testes:30-43`). O Python procura cada um primeiro no diretório do script, que é o `bin/` da branch.

Requisito violado: a decisão do dono de 2026-10-24 "A" diz que um caminho sem regra cai na suíte completa. O comentário do próprio hook (`:259-260`) diz que quem muda o filtro não se auto-julga. Um `bin/json.py` não casa nenhuma regra do `MAPA` (`bin/forge-testes:81-112`), mas muda o comportamento do filtro.

Prova, num clone em `$TMPDIR`, com `refs/remotes/origin/develop` no head revisado e uma trava isolada:
1. Um commit acrescenta uma linha ao `README.md` e cria um `bin/json.py` que imprime `forge-testes: dirigido (nada). ...` e sai 0.
2. O hook, chamado com uma ref `refs/heads/melhoria/sonda`, imprimiu "rodando só os testes afetados", depois a linha falsa, e saiu `rc=0`. Nenhum teste rodou.
3. O mesmo plano com `python3 -I` dá suíte completa.

Caminho de ataque: um agente implementador quer passar o push com testes vermelhos. O `--no-verify` está barrado, e editar o `.githooks/` também (`hooks/conformidade.py:34`, `:130`). O `bin/` não é protegido, então criar um arquivo nele vence o portão local. O histórico do LOTE-M8-HOOK registra uma tentativa de `--no-verify` nesta mesma entrega. Também pode acontecer por acidente, com um script auxiliar novo em `bin/` cujo nome coincida com o de um módulo.

Severidade: baixa como risco, porque o CI do PR roda a bateria completa e o review e o QA continuam. Mesmo assim é bloqueante, porque o defeito foi provado e viola o requisito da decisão do dono sobre o controle que este PR introduz.

Correção mínima: `python3 -I bin/forge-testes` nas duas chamadas (`:264` e `:274`). O `-I` tira o diretório do script do `sys.path` e ignora `PYTHON*` do ambiente. O filtro só importa a biblioteca padrão, e com `-I` a sonda funcionou. O `unittest` filho do filtro roda com `sys.executable` sem `-I` e continua achando `tests.*` pela raiz. Junto, um teste no `test_pre_push_afetados`: uma branch com `bin/json.py` (ou outro nome da biblioteca padrão) roda a suíte inteira. Também um mutante que tire o `-I`. Esforço P. Dono: tech-lead (autor do hook).

**Observações sem achado:**
- O caminho dirigido vale para qualquer `refs/heads/*` fora das três protegidas, não só para `melhoria/*`. Isso não é defeito: pelo `R-FLUXO`, toda outra branch vai à develop, e o CI dela roda a bateria completa.
- Resta um risco que não muda com este PR. Quem controla a cópia local pode mover `refs/remotes/origin/develop` (`git update-ref`) para estreitar o diff, ou mudar o `scripts/suite-paralela.py` da própria branch. O portão local confia no código da branch, e quem fecha isso é o CI do PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas usadas: `shellcheck` (sem aviso no hook), `python3 -m unittest` nos testes do item e as sondas em `$TMPDIR/security-engineer-lote-m8-hook/`.

Ferramentas ausentes no PATH e não instaladas (`R-CUSTO`): `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner`. Este diff não toca workflow nem dependência, então a lacuna não afeta o veredito.
