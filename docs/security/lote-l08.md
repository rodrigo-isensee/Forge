---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/lote-l08
commit: a46eab7891b4f0c233e547b303dfa9ff6feee35b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033 (lote L08)

Diff revisado: `4f53bde..874c89e` (E10, E12, E16, E7, E19) e, na revalidação, `874c89e..7925640`, em leitura estática; rodei só os testes dos arquivos tocados (D-5).

## Gatilhos
Controles do Forge (R-SEGURANCA): `bin/forge-check` (`pr`, `entrega`, `brief`), `docs/regras/R-PROVA.md` e a conferência de entrega (`agents/conferente.md`, `agents/jarvis.md`).

## Achados
- A3 (recomendado) bin/forge-check:858 · `gh pr view <n>` sem `--repo` usa o repositório padrão do gh; com mais de um remoto (fork e origem), o #n pode ser de outro repositório. Passe `--repo` do origin ou imprima a URL do PR.
- A4 (recomendado) bin/forge-check:686 · `promocao` compara o head com `refs/remotes/origin/<b>` local (ou a branch local sem remoto); um `git update-ref` local dessa ref faz uma branch de trabalho passar por promoção sem a conferência do head. Confirme a ponta por `git ls-remote origin`.

## Detalhe dos achados
**Respostas ao foco.**
- E10: o head não é forjável por quem não controla o `gh` do PATH (fora do modelo). A resposta só vale com `state == MERGED`, `headRefOid` em sha40 exato (`SHA40.fullmatch`, sem sha curto, então sem ambiguidade) e presente no clone (`rev-parse --verify <sha>^{commit}` igual a ele), e com `headRefName` sem caractere de controle; `--pr` e `--ref` juntos dão rc 2. PR de fork: o `headRefName` escolhido por quem abriu o fork só escolhe *qual* parecer, que ainda precisa casar com o head pelo `commit_vale`. Por isso o fork não ganha nada. O único vetor que sobra é o A3.
- E12: o resultado não confere menos. A base do dono igual ao head já era recusada pelo `desde_valido`. Agora a proposta cai no Base-sha, que é a branch inteira, mais escopo. A conferida de outra branch deixa de abrir o Base-sha quando há conferida da própria branch, e a conferida já contida na base passa a abrir o Base-sha. Nos dois casos o intervalo é o certo ou um intervalo maior. As duas expectativas antigas mudaram nessa direção (`tests/test_conferencia_base_dono.py`, `tests/test_mensagem_conferente.py`).
- E16: só acrescenta texto à recusa que o `commit_vale` já dava (`commit_junto_do_parecer` não decide nada). Não muda a superfície de ataque.
- E7: um agente fora do Jarvis não forja a linha. `docs/pedidos/` (no clone e em `~/.forge-contrib`) é só do jarvis em `hooks/conformidade.json:48-50`, e `caminho_do_pedido` lê a cópia principal antes da worktree. Também não troca o pedido pelos briefs, porque `docs/briefs/` é só do jarvis (`hooks/conformidade.json:51-53`) e o `pr` recusa dois pedidos para a mesma branch. A conferida precisa ser sha40 existente, ancestral do head e com só LIVRES e o fragmento do changelog depois dela. A falha que sobra é de redação do próprio Jarvis (A1) e de falha aberta (A2).
  - A1: caminho realista. O Jarvis registra uma rodada reprovada como "E1.2 conferida <sha> ... não cumpriu", forma que já aparece em pedidos antigos de `~/.forge-contrib/docs/pedidos/`. Com isso, o `pr` libera o QA e o merge sobre um head que o conferente reprovou. Severidade baixa (quem escreve é confiável e o erro é dele). Correção mínima: no `conferencia_do_head`, uma expressão própria `^\s*-\s.*\bentrega conferida ([0-9a-f]{40})\b`, e manter o `CONFERIDA` atual no `--desde`. Esforço P. Dono: tech-lead.
  - A2: o pedido sem Histórico só gera aviso no stderr. Quem pode tirar o Histórico é só o Jarvis, e o caso sem pedido é o CI, de propósito. Severidade baixa. Correção mínima: com o pedido achado e sem `## Histórico`, devolver a violação em vez do aviso. Esforço P. Dono: tech-lead.
- E19: o executor não marca o tipo. `Tipo: ato-github` vem do brief do Jarvis (hook em `docs/briefs/`), e a etapa exige `--branch —`, um único `--brief` com o mesmo pedido, Base e Base-sha, e nenhuma PQ `sha` ou `push`. Mesmo um brief de código marcado assim por engano não chega ao merge: o `pr` do E7 ainda cobra `entrega conferida <sha40>` do head, e o ato-github não produz essa linha (com a ressalva do A2).
- A3: severidade baixa. Exige um clone com dois remotos e um PR #n mesclado também no outro repositório, com head presente no clone e pareceres válidos para ele. A saída imprime o `headRefName`, o que ajuda a perceber a troca. Correção mínima: `--repo` derivado de `git remote get-url origin`, ou imprimir o `url` do PR. Esforço P. Dono: tech-lead.

Nada disso bloqueia: nenhum caminho dá a um agente sem escrita em `docs/pedidos/` ou `docs/briefs/` um jeito de pular a conferência.

## Revalidação (874c89e..7925640)
Delta lido inteiro (`forge-check delta --parecer`): `bin/forge-check:708-754` e `:1400`, a prosa de R-PROVA, conferente, jarvis, skill e fechamento-integrador, e os testes. A1 e A2 da rodada anterior estão **fechados**; A3 segue recomendado, sem mudança.
- A1 fechado: `ENTREGA_CONFERIDA` (`bin/forge-check:708`) exige `- <data> <hora>: entrega conferida <sha40>` no começo da linha, só dentro do `## Histórico`; `NÃO conferida`, `- não: entrega conferida`, sha abreviado, maiúscula e a linha fora do Histórico não casam. O texto depois do sha é livre, como nos pedidos reais (anotação da volta); não achei nenhum caso com veredito negativo depois de `entrega conferida <sha40>` em `~/.forge-contrib/docs/pedidos/`.
- A2 fechado: sem pedido, pedido ilegível, dois pedidos nos briefs da branch, pedido fora das raízes ou sem `## Histórico`, o `conferencia_do_head` devolve a violação (`bin/forge-check:741-754`); o CI e o hook `parecer` continuam fora, por desenho.
- Sha para branch (`branch_do_sha`, `bin/forge-check:718-729`): `for-each-ref --points-at` em `refs/heads` e `refs/remotes/origin`, sem `develop`, `homolog`, `main` nem `HEAD`; mais de uma branch no sha dá None e, sem pedido direto, a violação. Falha de git também dá None. O sha vem de `sha_do_commit`, não da entrada crua.
- Bypass procurado, sem caminho: (a) sha de outra branch: o nome só escolhe o pedido; a liberação continua presa a `commit_vale` (só pareceres, quadro e o fragmento do changelog entre a conferida e o head), então o código liberado é o que foi conferido; (b) linha forjada no Histórico: `docs/pedidos/` é escrita só do Jarvis (hook), e a forma estrita barra as variantes negativas; (c) pedido de outra branch (`--pedido` direto): a conferida dele só libera um head cujo conteúdo, fora dos livres, é o mesmo commit conferido; ramo empilhado com código novo reprova.
- Tipo da PQ em minúsculas (`bin/forge-check:1400`): fecha `(SHA)` e `(Push)` no ato-github; nos outros consumidores só faz a grafia maiúscula valer como a minúscula, sem tipo novo aceito.
Testes (um módulo por vez): `test_forge.py` só nas classes tocadas (`ConferenciaPresaAoHead` 8, `EntregaAtoGithub` 3, `PrMescladoPeloHead` 4, `LerDirigidoDoBrief` 2), `test_fechar.py`, `test_etapa_do_brief.py`, `test_isencoes.py`, `test_volta_por_delta.py`: todos OK. Os casos de abuso acima têm teste (`test_so_a_linha_de_entrega_conferida_libera`, `test_sem_historico_ou_sem_pedido_reprova`, `test_ref_por_sha_acha_a_branch_como_no_forge_fechar` com a branch gêmea).

## Revalidação (a46eab7, review A9 e A10)
Delta `a46eab7~1..a46eab7`: `promocao` (`bin/forge-check:680-686`), o desvio em `pr_da_cli` (`:674-676`), a ajuda e o teste `ConferenciaPresaAoHead.test_promocao_nao_cobra_a_conferencia_e_branch_de_trabalho_segue_cobrada`. Só a conferência do head (E7) deixa de ser cobrada; `cmd_pr` (review, segurança, QA e o resto dos portões) roda igual, e o caminho sem `--base` não muda.
- Limite conferido: base `homolog` aceita só a ponta de `develop`; base `main`, a de `develop` ou `homolog`; `develop` como base nunca é promoção. A comparação é por sha40 (`sha_do_commit`, com `--end-of-options`), não por nome.
- `--ref origin/develop` sendo outra coisa: o nome não decide. Uma branch local `refs/heads/origin/develop` ganha do remoto no `rev-parse`, mas o sha dela é comparado com `refs/remotes/origin/develop` por caminho completo; se forem diferentes, não é promoção. Ref inexistente dá None e não é promoção.
- develop local à frente da origin: `ref_da_base` (`:1128-1130`) lê `refs/remotes/origin/develop` antes da local; a local só vale sem o remoto. Sem bypass.
- Ref local sem remoto: só vale quando `refs/remotes/origin/<b>` não existe (projeto sem origem). No Forge e nos projetos com origem, o remoto existe e a local é ignorada. Coberto no A4.
- Head igual à develop num repositório manipulado (A4): `refs/remotes/origin/develop` é ref local e pode ser movida por `git update-ref` ou por um `fetch` de outro remoto; o hook não barra (`hooks/conformidade.py:1321` só barra apagar). Caminho: quem tem Bash no clone aponta a ref para o head de trabalho e roda `forge-check pr --base main`. O `forge-fechar` confere por `ls-remote` o head e a base, mas não a integração anterior. O ganho fica limitado: só cai a conferência do head, os pareceres continuam exigidos e o PR no GitHub mostra a branch real contra a `main`. Severidade baixa. Correção mínima: em `promocao`, exigir também que o head seja igual ao `git ls-remote origin refs/heads/<b>` (coluna 2 exata, como o `forge-fechar:138-143`), com falha de rede = não é promoção. Esforço P. Dono: tech-lead.
- Branch de trabalho que já está na develop (head = ponta de `origin/develop`): é a leva já mesclada, que passou pela conferência no PR dela; correto por desenho.
Testes: `python3 -I -m unittest discover -s tests -p test_promover_homolog.py` (36, OK), só esse módulo, como pedido. O teste novo fica em `test_forge.py` e não rodou nesta rodada; li o teste: ele cobre a promoção para `main` e `homolog` e três casos que seguem cobrados (trabalho com `--base main`, com `--base homolog` e `develop` com `--base develop`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados (só os arquivos tocados, D-5): `python3 -m unittest tests.test_forge.PrMescladoPeloHead tests.test_forge.TesteEParecerSeparados tests.test_forge.ConferenciaPresaAoHead tests.test_forge.EntregaAtoGithub tests.test_conferencia_base_dono tests.test_mensagem_conferente tests.test_volta_por_delta tests.test_erros_no_brief`, com `Ran 173 tests ... OK`. Ferramentas ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, osv-scanner, zizmor, actionlint. O diff não toca workflow nem dependência.
