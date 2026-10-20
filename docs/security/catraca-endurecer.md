---
tipo: revisao-seguranca
contrato: 1
pedido: catraca-endurecer
branch: melhoria/catraca-endurecer
commit: fb5028ea246f6f884260c96ad6ed9e24019093cc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: catraca-endurecer

Revalidação por delta (volta 1): HEAD fb5028e. `bin/forge-check delta --parecer` sobre o parecer anterior (60328da) lista só `tests/test_catraca.py` (+40 -3, linhas 14, 440, 445, 454-468 e 1182-1204). `git diff --quiet 60328da fb5028e -- tests/catraca.py bin/ scripts/ .github/ .githooks/` dá rc 0: nenhum controle mudou. O resto deste parecer, abaixo de "Revisão inicial", fica como já lido em 60328da e vale igual em fb5028e.

## Delta lido (volta 1)
- `import mock` (linha 14) e preparação tirada de `test_git_diff_com_erro_vira_violacao` (linhas 440-441): o teste continua usando base inexistente. O teste de base inexistente com rótulo só foi renomeado (linha 445).
- `test_git_diff_falho_com_base_valida_e_rotulo_do_dono_nao_libera` (linhas 454-468): base válida, dono definido, rótulo depois do push e `alterados` trocado por um que levanta `ErroDeDiff`. Exige rc 1 e a ausência de "liberada". Prova que o rótulo não libera a violação de diff.
- `test_git_diff_falho_no_head_rotulado_nao_libera_pelo_conteudo` (linhas 1182-1204): primeiro roda o controle (com o git funcionando, o rótulo por conteúdo da S-16 vale, rc 0). Depois o `git diff` falha só no head rotulado, e o teste exige rc 1. Prova que o caminho por conteúdo falha fechado.
- Mutação numa cópia própria de fb5028e em `$TMPDIR`: a suíte `tests.test_catraca` passa (161 OK). Tirar a guarda `SEM_LISTA in x` (tests/catraca.py:911) derruba só o primeiro teste novo. Fazer `rotulo_vale_pelo_conteudo` devolver True diante de `ErroDeDiff` (tests/catraca.py:518-525) derruba o segundo teste novo (e `test_sem_execucoes_ou_commit_desconhecido_falha_fechado`). Os testes provam o que dizem provar.
- Sem rede nem custo novo (`R-CUSTO`): o `mock` é da biblioteca padrão.

## Revisão inicial (60328da, já lida)
Escopo: o commit 60328da sobre ef71b3c (`tests/catraca.py`, `tests/test_catraca.py`, `changelog.d/catraca-endurecer.md`). Os workflows não mudam. O CI roda a cópia da base do script (catraca.yml:41-45), então este PR ainda é julgado pela catraca antiga. Ela barra a mudança em `tests/catraca.py` e exige o rótulo do dono. O comportamento novo vale depois do merge.

## Gatilhos
Controles do Forge: `tests/catraca.py` é a própria catraca (`R-SEGURANCA`, `R-CONFORMIDADE`). Cadeia de CI: só a lógica do job `catraca`. Não há credencial nova nem chamada de rede nova.

## Achados

## Detalhe dos achados
Não há achado bloqueante. Conferi os pontos que o brief pediu:

- **Todo erro de `git diff` vira violação, sem nenhum caminho que falhe aberto.** `alterados` levanta `ErroDeDiff` quando o código de saída não é zero (tests/catraca.py:97-99). Esse é o único lugar da catraca que roda `git diff`. Os chamadores tratam o erro assim:
  - `violacoes_das_regras` e `violacoes_de_pareceres` o devolvem como violação `R-CONFORMIDADE` (tests/catraca.py:433-437 e 831-835).
  - `main` captura o que escapa do resto, com rc 1 (tests/catraca.py:870-876). Isso cobre `pareceres_do_pedido` (tests/catraca.py:499-500), `regra_protegidos` no caminho do PR mesclado (tests/catraca.py:773) e `so_troca_sha_de_acoes` do dependabot (tests/catraca.py:816).
  - No caminho do rótulo por conteúdo da S-16, `violacoes_das_regras(..., sha)` sobre o head rotulado devolve só a violação de diff, e as violações atuais continuam novas, então não há liberação (tests/catraca.py:525). `mesmo_diff` do `bin/forge-check` dá False quando o git falha (bin/forge-check:399-401).
  - `candidatos_mesclados` devolve a lista vazia quando o `git log` falha, então nada é liberado.
  - Um timeout do `subprocess` derruba o script com rc 1.

  Sonda numa cópia própria em `$TMPDIR` (repositório descartável). Todos os casos com base ou SHA rotulado inexistente deram rc 1: modo regras com rótulo válido, modo pareceres, autor dependabot, e rótulo por conteúdo com o SHA rotulado ausente do clone (mensagem `não consegui listar os arquivos alterados`). `tests.test_catraca` na cópia de 60328da passou (159 testes OK).
- **O rótulo não libera a violação de diff.** Uma violação que contém o texto da violação de diff entra no conjunto `custo` (tests/catraca.py:911). Com esse conjunto não vazio, nenhum dos três caminhos de liberação roda: rótulo depois do push, rótulo por conteúdo e PR mesclado. O teste `test_git_diff_com_erro_deixa_a_catraca_vermelha_e_o_rotulo_nao_libera` cobre o caso. No modo pareceres não existe caminho de rótulo.
- **`scripts/conferir-release.py` passa a pedir o rótulo.** O arquivo está em `PROTEGIDOS` (tests/catraca.py:39-41) e já existe no repositório. A sonda mostrou que mudar só esse arquivo gera a violação `mudança em scripts/conferir-release.py`, que só passa com o rótulo do dono. Os testes `test_regra_de_release_e_protegida` e `test_mudanca_em_arquivo_protegido_barra` cobrem o caso.
- **Sem rede (`R-CUSTO`).** O diff não importa módulo de rede nem chama URL. As únicas chamadas continuam sendo as GET já existentes a `api.github.com` com o `GITHUB_TOKEN` do run.

Recomendações (não bloqueiam; severidade informativa, sem caminho de ataque):

1. **Disponibilidade na promoção.** No caminho do rótulo por conteúdo, um SHA rotulado ausente do clone agora interrompe toda a avaliação com rc 1, antes de chegar ao caminho do PR mesclado (tests/catraca.py:522 e 773). Isso é mais rígido e fica dentro da decisão CATRACA-FALHA-FECHADA → "A". Com `fetch-depth: 0` e a checagem de reescrita, não espero falso vermelho. Se aparecer, a correção mínima é tratar o erro dentro de `rotulo_vale_pelo_conteudo` como "não liberado" e seguir. Esforço P. Dono: tech-lead.
2. **Robustez da ordem.** Quando a base não tem `tests/catraca.py`, `regra_protegidos` não chama `alterados` (tests/catraca.py:418-419). A falha fechada com base inexistente depende de `regra_arquivos_de_regras` chamar `alterados` antes (tests/catraca.py:426). Hoje isso está correto e o teste `test_git_diff_com_erro_vira_violacao` cobre o caso. Uma refatoração futura deve manter esse teste. Esforço P. Dono: tech-lead.
3. **Correspondência por substring.** O teste da linha 911 procura o texto da violação de diff dentro da mensagem. Um caminho de arquivo com esse texto deixaria a sua violação fora do rótulo. Isso só aperta e só afeta o próprio PR, por isso não muda nada.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Ferramentas: leitura do diff e do código, a sonda em Python e `git` numa cópia descartável em `$TMPDIR`, e `python3 -m unittest tests.test_catraca`. Ausentes no PATH, registradas como lacuna sem efeito neste diff, que não toca dependência, workflow nem segredo: `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint`. O CI do projeto roda a varredura de segredos.
