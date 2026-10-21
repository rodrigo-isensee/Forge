# Fechamento da entrega por script (`bin/forge-fechar`, TA-5)

Propósito: tirar da conversa os passos mecânicos do integrador, sem tirar nenhum portão. Público: `tech-lead` e Jarvis. Regras: `R-FLUXO` (métodos de merge, "Depois do merge"), `R-CONTRIB` (checklist de merge), `R-MAIN`, `R-VERIFY`.

## Uso
```bash
bin/forge-fechar <pedido> --ref <branch> [--base origin/develop] \
  [--titulo T] [--origem T] [--muda T] [--medir T] [--espera SEGUNDOS] [--dry-run]
```
Rode na raiz do repositório do Forge (o script recusa rodar em outro lugar: sem `.claude-plugin/plugin.json` com `"name": "forge"`, ele para; em sessão de projeto o fechamento não é do script nem do projeto, `R-CONTRIB`). Só serve para a `develop`; a promoção `develop` → `homolog` segue manual (`R-FLUXO`), com a branch já enviada ao `origin` e os pareceres gravados. `--dry-run` imprime os sete passos e não executa nenhum (nem `forge-check`, nem `git` remoto, nem `gh`); se o diff da branch contra a base toca um caminho de controle que a catraca protege (a lista `PROTEGIDOS` de `tests/catraca.py`, lida de lá, sem cópia no script), acrescenta uma linha de aviso de que o rótulo `afrouxa-regra` do dono vai ser pedido. Se não consegue ler o diff (por exemplo, `--ref` sem branch local), avisa "não consegui conferir"; a falta do aviso não dispensa a catraca, que é o controle (passo 4). `--origem`, `--muda` e `--medir` preenchem as seções que a catraca exige no corpo do PR (`Projeto de origem` e `Como medir`, mínimo de 20 caracteres); sem elas, o corpo cita o pedido.

## Passos (em ordem; para no primeiro erro)
1. `forge-check pr <pedido> --ref <branch> --base <base>`: pareceres de review e QA válidos. `--base` só aceita `develop`, `homolog`, `main` ou `origin/<essas>` e é lida de `origin/<base>`; o merge da base depois do parecer não o invalida (por conteúdo: qualquer byte a mais no commit de merge dá `desatualizado`).
2. `git ls-remote origin refs/heads/<branch>`: o head remoto é igual ao local.
3. Abre o PR para a `develop` (ou reusa o aberto, exigindo que a base dele seja a `develop`; base `main` ou outra para): só chega aqui com os pareceres do passo 1. Não abre PR se o head já está na base (`git merge-base --is-ancestor`) nem se a branch já tem PR `MERGED` com este head (caso do squash vazio de um PR duplicado): avisa e vai à limpeza (passo 7), sem passos 4 a 6.
4. Lê `gh pr checks` até nenhum pendente (limite `--espera`, padrão 1800 s); "nenhum check ainda" (PR recém-aberto) conta como pendente; qualquer check que não seja `pass` ou `skipping` para.
5. Recusa o PR que pede o rótulo `afrouxa-regra` sem que ele esteja aplicado: o título é o lugar oficial do sinal (regra do título nos invariantes do `CLAUDE.md` do Forge, não da `R-CONFORMIDADE`), então citar o rótulo no título já para; no corpo, só a linha de item marcado que cita o rótulo (marcadores `-`, `*`, `+` e lista numerada `1.`/`1)`, com `[x]` ou `[X]`). O corpo que só cita o nome, ou o item desmarcado, não para. O corpo gerado no passo 3 traz o item do rótulo desmarcado (o mesmo texto do item de `.github/pull_request_template.md`), para o autor marcar quando a mudança afrouxa regra protegida. Erro de leitura do `gh` aqui também para (falha fechada). Atenção: um PR que afrouxa regra sem sinalizar passa por esta checagem; o controle do rótulo continua sendo o CI (a Catraca), cujo resultado o passo 4 exige.
6. Relê a base do PR (recusa `main` e qualquer outra que não a `develop`), marca como pronto o PR em rascunho (já com os pareceres do passo 1) e roda `gh pr merge --squash --match-head-commit <head conferido no passo 2>` (`R-FLUXO`): um commit novo na branch durante a espera faz o merge falhar. Confere o estado `MERGED`. PR que já consta `MERGED` (lido antes, ou depois de um merge que devolveu erro) é sucesso e o merge não se repete; o merge nunca é repetido sozinho.
7. Limpeza: apaga a branch remota (`refs/heads/<branch>`, com até 3 tentativas), remove a worktree e apaga a branch local. Se o script roda dentro da worktree da branch, só avisa os comandos. Falha de limpeza é aviso (o merge já ocorreu).

## Erro passageiro do GitHub (502)
Só as operações que não mudam o PR repetem, até 3 vezes e com espera curta (`FORGE_FECHAR_PAUSA`, padrão 3 s): a leitura do estado e dos dados do PR (passos 3, 5 e 6), a leitura dos checks (passo 4) e o `git push origin --delete` da limpeza. Push de código, criação de PR, `gh pr ready` e merge nunca se repetem sozinhos; se falham, o script para (no merge, só lê o estado para reconhecer um `MERGED` já feito).

## O que nunca faz
Mescla na `main` (base `main` ou fora do fluxo é recusada), aplica rótulo, usa `--force` ou `--no-verify`, apaga `develop`, `homolog` ou `main`, dispensa parecer ou check. O rótulo continua sendo do dono (`R-CONTRIB`).

## Teste
`tests/test_fechar.py` usa repositório temporário e `gh` e `forge-check` falsos (`FORGE_GH`, `FORGE_CHECK`, `FORGE_FECHAR_INTERVALO`, `FORGE_FECHAR_PAUSA`), que só valem com `FORGE_FECHAR_TESTE=1`; sem ela o script avisa em stderr e usa os comandos reais, para que uma variável esquecida no ambiente não troque o portão. O `--ref` passa por `git check-ref-format --branch`.

## Reversão
Se o script mascarar um portão ou mesclar o que não devia, apague `bin/forge-fechar` e a menção em `agents/tech-lead.md`: o fechamento volta a ser manual, como antes.
