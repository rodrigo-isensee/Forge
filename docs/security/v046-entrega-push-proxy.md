---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/entrega-push-proxy
commit: 843e6b752849bf4b62fcf3d41dcc83c22a6f74e5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-11
---
# Review de segurança: v046 (E12.1, ENTREGA-PUSH-PROXY)

**Revalidação (volta 1, `a5fec3a0..843e6b75`):** o delta toca `bin/forge-check:475` (`\d` virou `[0-9]`), os `de`/`para` de M3, M4 e M6 em `tests/mutantes/v046-entrega-push-proxy.json` e a contagem 69 em `tests/test_testes_tocados.py:66`. Sonda local no head: `GIT_CONFIG_KEY_٣` não casa; `COUNT`, `KEY_0` e `VALUE_12` casam; `GIT_CONFIG_GLOBAL` e `KEY_` não casam. O `de` de M1 a M6 aparece uma vez em `bin/forge-check`; `tests.test_git_rede_config` passa (6 testes); `Mapa` de `test_testes_tocados` passa com 69. Nada mais mudou, e a análise abaixo continua valendo. Parecer `aprovado`, sem achado aberto.

Diff `11ba4fa6..a5fec3a0`: `bin/forge-check` (`GIT_REDE`, `GIT_CONFIG_DO_AMBIENTE` e o filtro de ambiente do `git()`), `bin/forge-testes` (o MAPA ganhou `test_git_rede_config`), `changelog.d/entrega-push-proxy.md`, `tests/test_git_rede_config.py` e `tests/mutantes/v046-entrega-push-proxy.json`. A leitura foi estática, sobre `git archive` da base e do head em `$TMPDIR`, sem escrever na branch.

## Gatilhos
`R-SEGURANCA`: muda o `git()` de `bin/forge-check`, que é o único ponto que roda git no forge-check, nos hooks (`hooks/_comum.py:220`) e no validador. Ou seja, mexe num controle do Forge e no ambiente que um subprocesso herda.

## Achados
- A1 (recomendado) bin/forge-check:475 · resolvido em 843e6b75: o filtro usa `[0-9]+`; GIT_CONFIG_KEY_٣ não casa mais

## Sondas

## Detalhe dos achados
**A1** · evidência `bin/forge-check:475`, sonda local: `GIT_CONFIG_DO_AMBIENTE.fullmatch("GIT_CONFIG_KEY_٣")` dá True. Não há caminho de ataque: o git só lê `GIT_CONFIG_KEY_<n>` com `n` ASCII de 0 a COUNT-1, e a variável a mais chega ao filho sem efeito. Severidade informativa · correção mínima: `KEY_[0-9]+|VALUE_[0-9]+` · esforço P · dono `tech-lead`.

Verificado sem achado de segurança:
- **Nenhuma outra GIT_* volta.** O filtro (`bin/forge-check:482-484`) só deixa passar o que casa com `fullmatch` nos comandos `ls-remote` e `fetch`. Na sonda, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`, `GIT_CONFIG_NOSYSTEM`, `GIT_CONFIG`, `GIT_CONFIG_KEY_`, `GIT_CONFIG_KEY_0x` e o nome em minúsculas não casam. `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_SSH_COMMAND`, `GIT_ASKPASS` e `GIT_PROXY_COMMAND` continuam fora por não terem o prefixo `GIT_CONFIG_`. Também na sonda, com `GIT_CONFIG_GLOBAL` apontando para um insteadOf, o `ls-remote` do head falha (rc 128). Os comandos locais seguem sem nenhuma GIT_*, e o mutante M2 prova isso. A classificação vê só `args[0]`: uma chamada com opção antes do subcomando (`git(pasta, *opcoes, "ls-files")`, `hooks/conformidade.py:1716`) cai como comando local e não herda nada, o que falha para o lado seguro.
- **Poder novo pela config injetada (credential.helper, core.sshCommand, insteadOf, protocol.ext.allow, core.hooksPath no `fetch`): nenhum.** Quem define `GIT_CONFIG_*` é o dono do ambiente do processo que roda o forge-check. Esse mesmo dono já roda git e qualquer comando direto no Bash. Na base, ele também já redirecionava o `ls-remote` do forge-check por um `~/.gitconfig` (o filtro antigo mantinha `HOME`). A sonda S-a mostra isso: com `HOME` falso e um insteadOf, o `git()` da base devolve rc 0. Em resumo, a prova de push do `entrega` (`bin/forge-check:9254`) e o `remoto_da_branch` (`:7061`) já confiavam no ambiente de quem confere. A mudança não cria essa confiança, só a estende de `HOME` para as variáveis que o próprio git define em `git -c` e que o proxy do sandbox injeta. O ambiente persistente das sessões (`settings.json`, chave `env`) fica protegido do agente pelo sandbox.
- **Os hooks não ganham caminho de rede.** Nos hooks, as chamadas ao `git()` do forge-check são locais: `config --get alias.*` (`hooks/conformidade.py:1619`), `ls-files` (`:1716`) e, pelo `brief_vencido` do hook `agentes`, o `corrigir_derivados`, que só lê refs locais. Nenhum hook chega a `remoto_da_branch` nem a `conferir_provas`. Os hooks do Claude Code herdam o ambiente da sessão, não o do comando do agente. O `.githooks/pre-push:229` e o `hooks/doutor.py` rodam o próprio `ls-remote`, fora deste `git()`. A consulta de fontes (`bin/forge-check:9387`) continua isolada (`GIT_CONFIG_NOSYSTEM`, `GIT_CONFIG_GLOBAL=/dev/null`, só https) e não mudou.
- **Injeção de argumento.** Os dois `ls-remote` passam `origin` e `refs/heads/<branch>`. O prefixo literal impede que um nome de branch vire opção.
- **Teste e mutantes.** `tests/test_git_rede_config.py` (6 testes) passa no head; na base, 4 falham (herda COUNT, herda PARAMETERS, `fetch` e "sem GIT_DIR"). O remoto é local, alcançado só por um insteadOf para `falso://r`, sem rede. Os mutantes M1 a M6 de `tests/mutantes/v046-entrega-push-proxy.json` foram aplicados um a um no head, cada um com os testes declarados, e os 6 morreram. O MAPA (`bin/forge-testes:96`) inclui `test_git_rede_config` em `FORGE_CHECK`.
- **Segredo.** O diff não grava nem imprime credencial. A herança passa o valor ao processo filho e não o escreve em log nem em saída.

Sondas de apoio (nenhuma prova bloqueante, por isso ficam fora do bloco `## Sondas`):
- S-a · base, `HOME=<pasta com .gitconfig de insteadOf>`, `git(w, "ls-remote", "origin", ...)` · espera: rc 0 (redirecionamento já existia) · obtido: rc 0
- S-b · head, `GIT_CONFIG_GLOBAL=<mesmo arquivo>`, `HOME` inexistente · espera: falha · obtido: rc 128
- S-c · head, COUNT/KEY_0/VALUE_0 de insteadOf mais `GIT_SSH_COMMAND` e `GIT_ASKPASS` · espera: rc 0 · obtido: rc 0

## Riscos aceitos e ferramentas
Nenhum risco aceito. Usei leitura estática, `git archive`, o `unittest` do arquivo tocado na base e no head, e a aplicação manual dos 6 mutantes. Não rodei `gitleaks` porque o diff não tem segredo nem fixture de credencial. A suíte inteira fica com o CI do PR.
