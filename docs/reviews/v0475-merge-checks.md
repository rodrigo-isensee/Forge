---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-merge-checks
commit: 9f497b0f140a450c578dae79e5ec00d88d3ff31c
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.70, branch melhoria/v0475-merge-checks)

## Achados
- A1 (bloqueante) bin/forge-check:1549 · checks_do_head roda no passo 1 do forge-fechar (bin/forge-fechar:1221, sem --previo): com o PR pronto e CI pendente o fechar morre no passo 1; o --armar (linha 14) e a espera do passo 4 viram letra morta, e o "rode de novo com --armar" (linha 761) falha (S1)
- A2 (recomendado) bin/forge-check:1472 · falta teste de integração do forge-fechar com o forge-check real e PR pronto com checks pendentes; foi o que deixou A1 passar (os fakes do test_fechar_forge_check_real não respondem ao gh pr view)
- A3 (recomendado) tests/test_forge_check_pr.py:1 · M14: 324 linhas de código e teste (99 em bin/); a H1 da ferramenta conta só código (99, abaixo de 150) e não exige, mas o corpo do PR deve trazer `teto: excedido, 324 linhas, <motivo>`

## Sondas
- S1 · checks_do_head com os argumentos do passo 1 do fechar (--ref refs/heads/<branch>, previo=False), gh falso: PR OPEN, isDraft false, head igual, bateria pending · espera: [] (o fechar espera no passo 4) · obtido: "checks do head no PR #9 não concluídos e verdes: CI/bateria (pending)..."

## Parecer
Reprovado por A1. O comportamento pedido está certo no `gh pr merge` direto, que passa pelo hook e pelo `forge-check pr`. O defeito está no outro chamador: o `forge-fechar` roda o mesmo `forge-check pr` no passo 1 para conferir os pareceres, antes de esperar os checks (passo 4) ou de armar o auto-merge (`--armar`). Com o PR fora do rascunho, que é o fluxo normal (o tech-lead roda `gh pr ready` antes do fechar, e o próprio passo 6 tira o PR do rascunho antes da segunda volta do `--armar`), o CI ainda rodando faz o fechar parar com "parou no passo 1", em vez de esperar ou armar. A sonda S1 roda a função com os argumentos que o fechar passa (`--ref refs/heads/<branch> --base origin/develop`, sem `--previo`).

Sugestão para A1, a decidir entre o autor e o arquiteto: o `forge-fechar` passa ao `forge-check pr` uma opção que dispensa só a conferência dos checks, porque os passos 4 e 6 dele já exigem os checks verdes (o auto-merge preso ao head). Essa opção não pode valer para o hook do `gh pr merge`. Também pode servir que, chamado pelo fechar, o pendente não reprove e só o vermelho reprove. Em qualquer caso, inclua o teste do A2.

O restante está correto:
- `checks_exigidos` ignora a forma inesperada da resposta (o corpo do 404).
- A regex do destino barra a interpolação antes da `gh api`.
- O par `workflow/nome` do Forge (C-6) continua no Python e no bash. O curinga `*/` vale só para os contextos lidos do ruleset ou da proteção.
- `test_os_pares_do_forge_sao_os_do_forge_fechar` amarra as duas listas.
- `ler_exigidos_do_destino` só soma, nunca tira um par.
- O mutante M1 do I4 foi atualizado para a nova linha.

Testes novos rodados com o ambiente limpo e `python3 -I`: `test_forge_check_pr`, 23 OK; `test_forge_fechar`, 5 OK. Não há PR nem CI da branch para citar (`gh pr list --head` vazio). A suíte e os mutantes declarados ficam para o CI e a catraca.
