---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-limpeza-fim-item
commit: 011d6e1b9db4f44d236988740619d1776b8922aa
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-limpeza-fim-item (revalidação)

Etapa E68.19 do pedido v0478. Revalidação por delta (R-REVIEW); a rodada anterior (E68.13, aprovada no head 70115210) está no git.

## Gatilhos
Gatilhos: apagamento de arquivo no disco (cópias de trabalho), controle do fluxo de fechamento (`forge-fechar --limpar`), leitura de dado vindo do GitHub (`gh pr list`).

## Delta lido
`forge-check parecer delta` sobre `70115210..cd24113e`, sem o que veio da base (develop).
- `05bf2146` (merge de `origin/develop`): o diff combinado (`git show --cc`) é vazio, sem resolução de conflito; a branch não muda nada do que trouxe da base.
- `011d6e1b`: `skills/trabalho-em-paralelo/ritmo-e-corte.md:22,31,44` passa a citar `bin/forge-fechar <pedido> --ref <branch>` (e `--limpar` na linha 44). Confere com o uso em `bin/forge-fechar:3` e a recusa sem pedido em `bin/forge-fechar:150`. Só texto; não muda trava nem amplia o que se apaga.
- `cd24113e`: só `docs/reviews/`, fora do domínio.
- `git diff 70115210 011d6e1b -- bin/forge-fechar bin/forge-copia`: vazio; o `fim_sem_merge` e as duas travas em série lidas na E68.13 seguem iguais.

## Estado dos achados anteriores
- A1 e A2 (recomendado, corrigidos em 9aa1e723): continuam corrigidos; o delta não toca o `bin/forge-copia`.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. O delta é uma linha de skill: nenhum teste de abuso novo a rodar. A suíte inteira fica com o CI do PR, portão do merge (R-FLUXO). Faltam no PATH `gitleaks`, `semgrep` e `shellcheck`; o delta não toca credencial nem dependência.
