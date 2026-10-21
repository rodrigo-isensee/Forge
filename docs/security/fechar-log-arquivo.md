---
tipo: revisao-seguranca
contrato: 1
pedido: fechar-log-arquivo
branch: melhoria/fechar-log-arquivo
commit: 12fb5147b5a96c2413b1afc0f924a5a2a3517af1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: fechar-log-arquivo

Escopo: `git diff 26f71895c37f16628d8ff914aec564fa336546f6 12fb5147b5a96c2413b1afc0f924a5a2a3517af1` (bin/forge-fechar, tests/test_fechar.py, docs/fechamento-integrador.md, changelog.d/fechar-log-arquivo.md).

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `bin/forge-fechar` é o script do fluxo de merge na `develop`. A entrega só acrescenta o log em arquivo (bin/forge-fechar:113-128); os passos, as checagens e o merge não mudam (conferido no diff: nenhuma linha removida no script).

## Achados

## Detalhe dos achados
Nenhum bloqueante. Conferências feitas:

- **O gate não muda.** O `exec > >(registrar 1) 2> >(registrar 2)` (bin/forge-fechar:127) só duplica a saída; o script não testa terminal em lugar nenhum, o código de saída e o `die` continuam iguais, e a primeira linha `log:` sai depois das checagens de argumento e de repositório, antes do passo 1. Falha ao gravar o log faz o leitor morrer e o script cair por pipe quebrado: falha fechada, não abre caminho para mesclar sem os portões.
- **Segredo no log.** O script não imprime credencial: o `gh` lê a sua sozinho e não a ecoa, não há `set -x`, e o `git push origin --delete` mostra a URL do remoto anonimizada pelo próprio git. O que passa de fora é a saída de `gh pr checks` (nomes e URLs de checks), do `gh pr create/merge` e do git. A máscara (bin/forge-fechar:124), sondada em cópia própria, cobre `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`, `github_pat_`, `Bearer <x>`, `token <x>`, `token=<x>` e `token:<x>`. A suposição do pedido (o log não guarda segredo) se sustenta. Modo 600 conferido pelo teste (tests/test_fechar.py, `test_log_em_arquivo_...`) e pelo `umask 077` na pasta e no arquivo.
- **Nome do arquivo.** O pedido entra no nome por `tr -c 'A-Za-z0-9._-' '_'` (bin/forge-fechar:115): sem `/`, não escapa da pasta.

Recomendações (não bloqueiam; dono: tech-lead, num cartão futuro se achar que vale):

- R1 (baixa, esforço P) · bin/forge-fechar:113-116 e 124 · Pasta compartilhada. Sem `TMPDIR` nem `FORGE_FECHAR_LOG_DIR`, a pasta cai em `/tmp/forge-fechar-logs`, nome fixo; o `mkdir -p` aceita pasta já existente de outro usuário, o `: >` segue link simbólico e o `>> "$log"` reabre o caminho a cada linha. Caminho de ataque: outro usuário local da mesma máquina cria a pasta antes e troca o arquivo por um link (anexa linhas num arquivo do dono) ou por um arquivo dele (lê o log, já mascarado). Exige máquina multiusuário e `TMPDIR` vazio; no sandbox do Forge o `TMPDIR` é do usuário. Correção mínima: recusar a pasta se for link ou não for do usuário (`[ -O "$logdir" ] && [ ! -L "$logdir" ]`), criar o arquivo com `mktemp` dentro dela e abrir o descritor uma vez só (`exec 3>>"$log"`).
- R2 (informativa, esforço P) · bin/forge-fechar:124 · A máscara não cobre `GH_TOKEN=<x>` (maiúsculas), `"token": "<x>"` (JSON), credencial em URL (`https://usuario:senha@...`) nem `Basic <x>`. Hoje nada disso é impresso pelo script, por isso é só defesa em profundidade: `[Tt]oken` com `-i`/`[Tt][Oo][Kk][Ee][Nn]`, aspas opcionais, e `s#(://)[^/@[:space:]]+@#\1***@#g`.
- R3 (informativa) · Os logs se acumulam na pasta sem limpeza; como estão mascarados e em modo 600, o risco é só de espaço. Opcional: apagar logs com mais de N dias na partida.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Leitura manual do diff e sonda da expressão da máscara em cópia própria (`git show` para $TMPDIR). Lacunas no ambiente: `shellcheck` e `gitleaks` não estão no PATH (o CI roda o shellcheck); não instalados (`R-CUSTO`).
