# O envio longo e o CI longo: detalhe

Parte da skill `esperar-estado`, num arquivo próprio porque o texto inteiro não cabe no teto de caracteres da
`SKILL.md` (diretriz 25 do dono: regra existente não se apaga nem se resume; o que não cabe muda de arquivo, com ponteiro).

## Caminho literal nas três vezes
O laço do log cita o mesmo caminho literal nas três vezes, sem variável: com `$log`, o caminho que cita `.forge/` ou
outra marca de ação crítica é recusado pela `conformidade`.

## O `bin/forge-fechar <pedido> --ref <branch> --espera <s>` acima de 170 s
Vale a mesma forma do envio longo: lance-o no lugar de `<envio>` e, com `fim=rc=1`, leia no log a linha
`fim: código <n>` (3 é integrado com limpeza pendente).

## Pasta temporária no mesmo comando
O comando longo que escreve em pasta temporária cria a sua no mesmo comando, fora de `~/.forge-contrib` (o `mktemp -d`
usa o `TMPDIR` da sessão), e grava o log com caminho literal:

`TMPDIR=$(mktemp -d) <envio> > <log> 2>&1 && echo rc=0 >> <log> || echo rc=1 >> <log>`

## O laço do PR sem teto (regra 6)
Para a sessão principal, com o `run_in_background`; a mesma saída do laço com teto, sem `fim=teto`. Troque `123` pelo
número do PR:

```bash
n=123; while :; do e=$(gh pr view "$n" --json state --jq .state 2>/dev/null) || { echo "fim=erro"; break; }; [ "$e" = OPEN ] || { echo "fim=$e"; break; }; s=$(gh pr checks "$n" 2>&1); c=$?; case $s in *"no checks reported"*) c=8;; esac; [ "$c" -eq 8 ] || { echo "fim=checks:$c"; break; }; sleep 30; done
```
