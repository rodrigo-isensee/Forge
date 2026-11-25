---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-fechar-dryrun-branch
commit: 1bf95225578a79532bae4ee99f3875af3a8bc007
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E14.42, #898, forge-fechar --dry-run sem a branch local)

Gatilhos: controle do Forge (bin/forge-fechar, fechamento e merge), guarda com mutante.

Escopo: `git diff b224ee09e78..1bf95225` (bin/forge-fechar, tests/test_fechar.py, tests/mutantes/v0481-fechar-dryrun-branch.json, docs/fechamento-integrador.md, changelog.d). Clone de revisão criado com o `bin/forge-copia` da develop (`--revisao`), no head remoto 1bf95225.

## Achados
- A1 (bloqueante) tests/mutantes/mp1311-fechar-cartao.json:26 · M3 e M5 (e FL-M11, FL-M12 em tests/mutantes/v0478-fechar-lote-2.json:26 e :37) têm o `de` em linhas que o diff apagou e apontam para testes removidos; o CI do #898 está vermelho (suíte parte 4/5, nos dois Pythons) em ConferirTodas.
- A2 (recomendado) bin/forge-fechar:1674 · a branch que o --dry-run cria fica; com a origin/<b> velha, o passo real depois confere o sha velho e para no passo 2 (bin/forge-fechar:1840) com "envie a branch", em vez de ler o servidor como antes; diga no --dry-run que a ref fica e como refazê-la.

## Sondas
- S1 · python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes · espera: OK · obtido: FAIL, specs fora da fonte: mp1311-fechar-cartao.json M3, M5; v0478-fechar-lote-2.json FL-M11, FL-M12

## O que foi conferido (só aperta ou neutro)
- **Remoto e outras branches intactos:** sonda S-lado (subclasse de `tests.test_fechar.Fechar`, arquivo `~/.forge-contrib/wt/_sec-v0481-dryrun-sonda.py`): sem a branch local, o `--dry-run` sai 0, a única ref nova é `refs/heads/melhoria/x` no sha da `origin/melhoria/x`; `for-each-ref` do remoto, `.git/config` (sem chave de rastreio) e o `HEAD` iguais antes e depois; nenhuma chamada a `gh` nem ao servidor. Neutro.
- **O que barrava continua barrando:** o 1c sem branch local antes saía 0 com "não rodou"; agora roda (rc do `--conferir-ref` diferente de 0 para com 1, `test_1c_no_dry_run_sem_a_branch_local_que_recusa_para_com_1`) ou para com 1 sem a `origin/<b>` (M3) ou se a ref não se cria (M4). Aperta.
- **Teste removido** `test_dry_run_sem_branch_local_marca_o_sha_como_nao_lido`: a guarda era "o dry-run não finge um nome que não existe"; com a mudança não há mais caminho que imprima o passo 1 sem a ref existir (cria e mostra `refs/heads/<b>` ou para antes do passo 1, `test_1c_no_dry_run_sem_a_branch_local_nem_a_origin_para_com_1_e_diz_como_destravar`). Guarda substituída por uma mais estrita; o que falta é alinhar os mutantes dela (A1).
- **`--limpar --dry-run`:** deixa de rodar o 1c, que o `--limpar` real não roda (bin/forge-fechar:1719, só o passo 7 com prova de MERGED); o dry-run que antes podia sair 1 pelo 1c era falso alarme do preview, não controle. Neutro.
- **Nome da branch:** `$ref` passa por `git check-ref-format --branch` (bin/forge-fechar:217) antes do `git branch --no-track`; nomes com cara de opção (`-D`, `--force`, `-x`) recusados (sonda `_sec-v0481-dryrun-sonda.sh`). Sem `-f` no `git branch`: não sobrescreve ref existente.
- Módulo tocado: `python3 -m unittest tests.test_fechar` 114 OK (1 pulado: shellcheck fora do PATH, o CI roda). Mutantes `bin/forge-mutante tests/mutantes/v0481-fechar-dryrun-branch.json`: M1 a M4 morreram.
- CI do head 1bf95225 (`gh pr checks 898`): vermelho (A1); sem linha `- ci:`.

## Detalhe dos achados
**A1.** Evidência: `tests/mutantes/mp1311-fechar-cartao.json:26` (M3, `de: ref_dry="$sha_dry"; }`, teste removido), `:46` (M5, `de:   ref_dry="refs/heads/$ref"`), `tests/mutantes/v0478-fechar-lote-2.json:26` (FL-M11) e `:37` (FL-M12, teste `test_1c_no_dry_run_sem_a_branch_local_nao_roda`, renomeado), todos com `de` no bloco `if [ "$ref_dry" = ...` apagado. Caminho: não há ataque externo; a guarda FECHAR-REF-POR-NOME e FECHAR-DRY-RUN-1C perde a prova por mutante e o CI fica vermelho, o que impede o merge (defeito provado). Severidade: baixa (controle de qualidade do controle). Correção mínima, no mesmo commit que muda a fonte: M5 passa a mutar `passo 1 "$check pr $pedido --ref refs/heads/$ref --base $base"` (teste `test_dry_run_descreve_o_nome`); FL-M11 passa a mutar a chamada `conferir_1c "$sha_dry"` do dry-run; M3 e FL-M12 saem ou apontam para os testes novos (`..._nem_a_origin_para_com_1_e_diz_como_destravar`, `..._cria_da_origin_sem_rastreio_e_roda`), sem duplicar M2 a M4. Esforço P. Dono: autor da branch (dev do pedido).

**A2.** Evidência: bin/forge-fechar:1674 cria `refs/heads/<b>` e nada a desfaz; bin/forge-fechar:1743 (passo 1 real) passa a usar a local, e :1840 para. Sonda S2 (mesmo arquivo de sonda): servidor à frente da `origin/<b>` deste clone → dry-run sai 0 no sha velho; o passo real sai 1 com "o head local (velho) difere do remoto; envie a branch", remoto intacto. Antes, sem a local, o passo real lia o servidor (FECHAR-CRIA-BRANCH) e seguia. Caminho de ataque: nenhum (falha fechada; o push do sha velho seria recusado sem `--force`, R-VERIFY); é regressão de uso. Severidade: baixa. Correção mínima: a linha `registro: criei a branch local` diz que a ref fica e que o passo real a usa (`git branch -D <b>` ou `git fetch origin <b>` para refazê-la), ou a mensagem do passo 2 cita a ref criada pelo dry-run. Esforço P. Dono: autor da branch.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, unittest, `bin/forge-mutante`, `gh pr checks` (só leitura). Faltou shellcheck no PATH (o CI roda).
