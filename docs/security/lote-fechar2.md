---
tipo: revisao-seguranca
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: 03155612d2d56a54686248d5131557075289e4b8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-26
---
# Review de segurança: lote-fechar2

Escopo: diff `b6eb84f...0315561` (LSREMOTE-EXATO e SHELLCHECK-FECHAR): `bin/forge-fechar` (ajudante `remoto_exato` e os três pontos que liam o `git ls-remote`, mais o passo 2b reescrito com `mapfile` e `if`), `.github/workflows/ci.yml:238`, `tests/test_fechar.py`, `tests/mutantes/lote-fechar2.json`, `changelog.d/lote-fechar2.md`.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): o `forge-fechar` decide abrir e mesclar o PR (passo 2, head no servidor; passo 2b, base no servidor) e apagar a branch remota (limpeza); o lote também toca o workflow de CI.

## Achados

## Detalhe dos achados
Sem bloqueante. Verificações pedidas no brief, com evidência:

1. **Ref de nome parecido, ref de tag e linha malformada** (`bin/forge-fechar:137-141`). O ajudante só aceita a linha cuja coluna 2 é igual a `refs/heads/<branch>` inteiro e para na primeira. Sonda local num repositório nu (`$TMPDIR/security-engineer-lote-fechar2/`): com `refs/heads/a/refs/heads/melhoria/x`, `refs/tags/z/refs/heads/melhoria/x`, `refs/heads/melhoria/x-2` e `refs/heads/Melhoria/x` no servidor, o `ls-remote` devolveu três linhas e o ajudante devolveu só o sha da ref exata; ref ausente sai vazia com rc 0; remoto inacessível sai com rc 1. O `--ref` passa por `git check-ref-format --branch` (`bin/forge-fechar:70`) e o `$alvo` é fixo (`develop`, `bin/forge-fechar:72`), então nem glob nem barra invertida chegam ao padrão do `ls-remote` ou ao `awk -v`. Os quatro pontos usam o ajudante: passo 2 (`:599`), passo 2b (`:513`), limpeza (`:461`) e a conferência depois do delete que falhou (`:474`); não sobra outra chamada de `ls-remote` no código (`:482`, `:544` e `:545` são texto de mensagem). Linha malformada: linha vazia, sem coluna 2 ou com `\r` no fim não casa (sai como ausente); a única forma de enganar é uma linha com a coluna 2 exata e coluna 1 que não é sha, que só o próprio servidor `origin` produziria. Mesmo nesse caso o efeito é falha fechada: o passo 2 e o 2b comparam com sha conhecido e param, e a limpeza passa o valor ao `sha_confere` (`:278-284`), cujo `merge-base --is-ancestor` falha, e a branch fica `pendente`, sem apagar nada. Recomendação de baixa severidade, sem caminho de ataque realista (exige servidor hostil, que já controla o conteúdo da branch): validar a coluna 1 como sha hexadecimal (40 ou 64) no `awk` do ajudante. Esforço P; dono `tech-lead`. Não entra no bloco porque o parecer é aprovado.

2. **A troca para `if`/`mapfile` muda algum caminho de falha para sucesso?** Não. `if ! { sort && sort && comm; }; then die` (`:529-531`) é equivalente ao `A && B && C || die` anterior, sob `set -euo pipefail` (`:35`). O `mapfile -t lista_mb <<< "$mbs"` (`:522`) só roda depois de `[ -n "$mbs" ] || die` (`:521`), e o `$(...)` tira a quebra final, então não nasce elemento vazio; o laço (`:525`) e o `rev-list --not "${lista_mb[@]}"` (`:537`) recebem os mesmos shas que a expansão sem aspas recebia. No passo 2, a leitura que antes não tinha checagem de falha (falhava pelo `set -e` ou caía em vazio e parava em "não está no origin") agora para com mensagem própria (`:599`). O único caminho que passou a ter sucesso é o que antes falhava por causa da isca (passo 2 e 2b paravam com sha concatenado ou o da isca; a limpeza deixava a branch pendente), e esse é o comportamento correto. Os testes do lote (`tests/test_fechar.py`, `lsremote_exato` e `shellcheck_fechar`, 6 testes) passaram neste commit, e o `shellcheck bin/forge-fechar` local saiu limpo (rc 0).

3. **A linha nova do shellcheck no `ci.yml` roda antes de algum código da branch?** A mudança só acrescenta `bin/forge-fechar` à lista do passo existente (`.github/workflows/ci.yml:238`); o `shellcheck` é análise estática, não executa o arquivo. O passo fica depois da suíte (`:233-235`) e de outros passos que já executam código da branch (`bin/forge-changelog`, `:161`), então não cria execução nova nem antecipa nenhuma. O gatilho continua `pull_request` (não `pull_request_target`), com `permissions: contents: read` (`:14-15`) e sem segredo no passo; o `shellcheck` é o do runner, sem download novo.

Nota de teste (`tests/test_fechar.py:99-100`): o `delete_apaga_e_falha` do git falso só existe na suíte; não alcança o script de produção.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `shellcheck` (no PATH), sonda local com `git` em repositório nu no `$TMPDIR`. Faltaram no ambiente, e ficam como lacuna: `gitleaks`, `zizmor` e `actionlint` (o diff não traz credencial nem passo novo de workflow; o CI cobre o diff de segredo em `ci.yml:184`).
