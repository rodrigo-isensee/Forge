---
tipo: review
contrato: 1
pedido: fechar-log-arquivo
branch: melhoria/fechar-log-arquivo
commit: 12fb5147b5a96c2413b1afc0f924a5a2a3517af1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: o forge-fechar grava o log em arquivo (FECHAR-LOG-ARQUIVO)

Escopo: `26f71895..12fb5147` (2 commits; 4 arquivos: `bin/forge-fechar`, `tests/test_fechar.py`, `docs/fechamento-integrador.md`, `changelog.d/fechar-log-arquivo.md`). O autor foi outra instância (E1.1); este revisor não escreveu o código.

Veredito: **APROVADO**, com 4 recomendações que não bloqueiam.

## Achados

## Conferido
- **E1, log em arquivo** (`bin/forge-fechar:112-127`): a pasta é `${FORGE_FECHAR_LOG_DIR:-${TMPDIR:-/tmp}/forge-fechar-logs}`, criada com `umask 077`. O arquivo também nasce com `umask 077` (modo 600, o teste confere). O nome junta o pedido saneado por `tr -c`, a hora UTC e `$$`, então duas execuções não colidem. `log: <caminho>` é a primeira linha impressa depois das checagens iniciais; um `die` anterior (argumento inválido, fora do repo) não gera log, e o cabeçalho e a doc dizem isso. Cada linha vai à tela sem mudança e ao log com a hora UTC e a máscara. O código de saída se mantém, porque o `exec` não muda o `die`. O `--dry-run` passa pelo mesmo `exec`, então também grava.
- **Ordem dos fds**: o `>(registrar 2)` é criado depois de o fd 1 ir para o primeiro registrador. Ele escreve no fd 2 original, então o stderr continua no stderr (o teste confere com `ghp_...` em `r.stderr`).
- **Máscara** (sonda à parte, com o mesmo `sed`): cobre `ghp_ gho_ ghu_ ghs_ ghr_ github_pat_`, `Bearer <x>`, `token=<x>`, `token: <x>` e `x-access-token:<x>@`. Não cobre maiúsculas (`GH_TOKEN=abc`, `BEARER abc`) nem userinfo de URL que não seja token do GitHub (`https://user:s3cr3t@host`). Pelo que o script roda, nenhum dos dois vazamentos é real: o `gh` lê a credencial sozinho e não a imprime, o `git` anonimiza a URL nas linhas `To ...` e nas mensagens de erro, e nada aqui imprime o ambiente. Ver a recomendação 1; a análise de segurança é do `security-engineer` (E1.3, `R-SEGURANCA`) e não é refeita aqui.
- **Escopo**: os passos, as checagens e o merge não mudaram (o diff no script fica só entre as linhas 20-22 e 112-127). Era o que o pedido mandava deixar de fora.
- **Testes** (E2): 3 casos novos. (a) Um registro por passo de 1 a 7, o caminho na primeira linha, a pasta vinda da variável, a hora em toda linha, a última linha e o modo 600. (b) O stderr vai ao log, o `ghp_` fica mascarado no log e aparece inteiro na tela. (c) O `--dry-run` grava. O `FORGE_FECHAR_LOG_DIR` do `setUp` mantém o log de todos os testes dentro do `tmp` do caso. O teste veio antes do código (commit `ea5968a` antes de `12fb514`). Saída de `python3 -m unittest tests.test_fechar` numa cópia por `git archive 12fb514`: `Ran 57 tests in 27.716s` / `OK`. A suíte completa fica com o QA.
- **Ferramentas**: o Forge não tem `docs/engineering/praticas.md`, então não há regra "ferramenta" a citar. O shellcheck não está instalado nesta máquina, e o CI o roda sobre `bin/` na bateria do PR (pendência para o CI, não para revisão manual).
- **Doc e changelog**: `docs/fechamento-integrador.md` ganhou a seção "Log em arquivo", coerente com o cabeçalho do script. O fragmento `changelog.d/fechar-log-arquivo.md` fica em "Adicionado" e o `CHANGELOG.md` não foi tocado.
- **R-NEUTRO / R-CUSTO**: nada específico de projeto entra, e tudo é local (date, sed), sem rede nem serviço pago.
- **Commits**: `test(fechar)` e `feat(fechar)` em Conventional Commits em português, com o ID do pedido.

## Recomendações (não bloqueiam)
1. `bin/forge-fechar:124` · A máscara depende de maiúsculas e minúsculas e ignora userinfo de URL. · Sugestão: usar `[Tt][Oo][Kk][Ee][Nn]` e `[Bb][Ee][Aa][Rr][Ee][Rr]` (ou o flag `I` do GNU sed) e acrescentar `s#(://[^/:@[:space:]]+:)[^@/[:space:]]+@#\1***@#g`, com um caso no teste para cada. Defesa em profundidade, para o dia em que um passo imprimir algo novo.
2. `bin/forge-fechar:127` · O script não espera os registradores ao sair. Na sonda com o mesmo `exec > >(...) 2> >(...)`, `(./p.sh; echo depois-do-script)` imprimiu `depois-do-script` antes da última linha do script. Quem chama e logo lê o log ou roda outro comando pode ver a cauda atrasada ou o log ainda incompleto. · Sugestão: `trap 'exec >&- 2>&-; wait' EXIT` (bash 5.1 ou mais novo espera as substituições de processo), ou guardar os `$!` e dar `wait` neles.
3. `bin/forge-fechar:127` · Com dois leitores separados, a ordem relativa entre linhas de stdout e de stderr que saem juntas pode mudar na tela, e no log a hora tem só resolução de segundo. Em geral o texto na tela continua igual, mas a ordem pode trocar. · Sugestão: aceitar e registrar na doc, ou marcar o fluxo na linha do log (`[out]`/`[err]`) para ajudar a leitura.
4. `bin/forge-fechar:124` · O padrão `[Tt]oken[[:space:]]+` também mascara prosa (`token mascarado` vira `token ***`). Não vaza nada, mas muda o texto do log. · Sugestão: exigir `[=:]` para `token` e deixar o espaço só para `Bearer`/`token` depois de `Authorization:`.
- Para o `security-engineer` (cartão, não refeito aqui): uma pasta de log que já existe não tem o dono nem o modo conferidos (`mkdir -p` com `umask` só vale quando a pasta é criada). O `: > "$log"` segue symlink. No padrão `${TMPDIR:-/tmp}`, com `/tmp` compartilhado, outro usuário poderia criar a pasta antes.
