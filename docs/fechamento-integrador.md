# Fechamento da entrega por script (`bin/forge-fechar`, TA-5)

Propósito: tirar da conversa os passos mecânicos do integrador, sem tirar nenhum portão. Público: `tech-lead` e Jarvis. Regras: `R-FLUXO` (métodos de merge, "Depois do merge"), `R-CONTRIB` (checklist de merge), `R-MAIN`, `R-VERIFY`.

## Uso
```bash
bin/forge-fechar <pedido> --ref <branch> [--base origin/develop|origin/homolog] \
  [--titulo T] [--origem T] [--muda T] [--medir T] [--espera SEGUNDOS] [--dry-run]
```
Rode na raiz do repositório do Forge, com a branch já enviada ao `origin` e os pareceres gravados. `--dry-run` imprime os sete passos e não executa nenhum (nem `forge-check`, nem `git` remoto, nem `gh`). `--origem`, `--muda` e `--medir` preenchem as seções que a catraca exige no corpo do PR (`Projeto de origem` e `Como medir`, mínimo de 20 caracteres); sem elas, o corpo cita o pedido.

## Passos (em ordem; para no primeiro erro)
1. `forge-check pr <pedido> --ref <branch> --base <base>`: pareceres de review e QA válidos.
2. `git ls-remote origin refs/heads/<branch>`: o head remoto é igual ao local.
3. Abre o PR para a base (ou reusa o aberto), já pronto para revisão: só chega aqui com os pareceres do passo 1.
4. Lê `gh pr checks` até nenhum pendente (limite `--espera`, padrão 1800 s); qualquer check que não seja `pass` ou `skipping` para.
5. Recusa o PR cujo título ou corpo pede o rótulo `afrouxa-regra` sem que ele esteja aplicado.
6. `gh pr merge`: `--squash` na `develop`, `--merge` na `homolog` (`R-FLUXO`); confere o estado `MERGED`.
7. Limpeza: apaga a branch remota, remove a worktree e apaga a branch local. Se o script roda dentro da worktree da branch, só avisa os comandos. Falha de limpeza é aviso (o merge já ocorreu).

## O que nunca faz
Mescla na `main` (base `main` ou fora do fluxo é recusada), aplica rótulo, usa `--force` ou `--no-verify`, apaga `develop`, `homolog` ou `main`, dispensa parecer ou check. O rótulo continua sendo do dono (`R-CONTRIB`).

## Teste
`tests/test_fechar.py` usa repositório temporário e `gh` e `forge-check` falsos (`FORGE_GH`, `FORGE_CHECK`, `FORGE_FECHAR_INTERVALO`).

## Reversão
Se o script mascarar um portão ou mesclar o que não devia, apague `bin/forge-fechar` e a menção em `agents/tech-lead.md`: o fechamento volta a ser manual, como antes.
