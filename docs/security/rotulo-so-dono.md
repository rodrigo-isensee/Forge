---
tipo: revisao-seguranca
contrato: 1
pedido: rotulo-so-dono
branch: melhoria/rotulo-so-dono
commit: 6ec509586c79014203222d65760177ab1be9674e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: rotulo-so-dono (revalidação do delta da volta 2)

Escopo: o delta da volta 2, `git diff 2e5cc70d95d1ebfc5cd45953c7bacaa963e4e377 6ec509586c79014203222d65760177ab1be9674e` (`hooks/conformidade.py`, `tests/test_hooks.py`, `tests/config.json`, a fixture renomeada `rotulo-so-dono-remover-rotulo-exige-dono.json`). Este parecer substitui o anterior (reprovado sobre b458a57, B1). Método: leitura estática e sonda local do hook da worktree pelo próprio harness dos testes (`dados_da_sessao_do_forge` e `rodar_dados`: `gh` falso no PATH, sem rede), com 116 execuções (54 linhas na sessão do Forge com a conta `outra-pessoa` e com a do dono, 8 na sessão de projeto), também comparadas ao hook de 2e5cc70; e os 2 testes novos da volta rodados isolados (OK, 5 s). Nenhum rótulo real foi aplicado.

## Gatilhos
`R-SEGURANCA`: hook de controle (conformidade), que guarda o rótulo `afrouxa-regra`, usado pela catraca para afrouxar um portão.

## Achados

## Detalhe dos achados

### B1 (crase escapada em `bash -c`, `sh -c` e `eval`): fechado
`rotulo_no_argumento` (hooks/conformidade.py:1308) confere o argumento de `-c` (:1298) e do `eval` (:1300) como veio e com `` \` `` virado crase, que é o que o shell interno executa. Sonda com a conta `outra-pessoa`, todas barram: os três exemplos do parecer anterior (`` bash -c "echo \`gh pr edit 70 --add-label afrouxa-regra\`" ``, a forma com `sh -c "x=…"` e a com `eval "echo …"`), e também `bash -lc`, `sh -ec`, `` eval echo "\`…\`" ``, `bash -c` dentro de `bash -c` com a crase escapada duas vezes, `--label` em `gh issue edit` e `gh label clone` dentro da crase escapada. Seguem livres, como devem: `` bash -c "echo \`date\`" `` e `` echo "\`…\`" `` (crase literal). A conta do dono libera todas.

### Comentário com aspa: fechado
`conteudos_de_crase` (:241) pula o comentário (`#` no início de palavra, fora de aspas) até o fim da linha, então a aspa de `# don't` não abre aspa simples. Barram: a crase na linha seguinte ao comentário, em atribuição, entre aspas duplas e sozinha na linha (`#'` seguido de crase na linha de baixo). A crase dentro do próprio comentário segue livre, e está certo (o shell não a executa).

### `gh label clone` e `--remove-label`: exigem o dono
`gh label clone` barra com e sem `--force` e com `-R` antes do grupo (:1257). `--remove-label afrouxa-regra`, `--remove-label=AFROUXA-REGRA` e a lista `bug,afrouxa-regra` barram (`rotulos_removidos`, :1236, e :1256), coerentes com o `DELETE` em `issues/<n>/labels/<nome>`, que também barra; `--remove-label bug` e `gh label list` seguem livres. A fixture renomeada para `remover-rotulo-exige-dono` acompanha a mudança (conta ilegível barra).

### Sessão de projeto (R5): fechado
`aninhado` (:756) faz a mesma segunda passada com `` \` `` virado crase. Sonda com o alvo no Forge, todas barram: a crase escapada em `bash -c`, `sh -c` e `eval`, o comentário com aspa e a crase simples; `` bash -c "echo \`date\`" `` segue livre.

### A sonda anterior: nada voltou a passar
As formas de antes repetidas sobre 6ec5095 barram com outra conta e liberam com a do dono: crase direta, em atribuição e entre aspas duplas, crase sem par, `$(...)` e `\$(...)` em `bash -c`, `bash -c` aninhado, heredoc para `bash` (`bash <<X` e `cat <<X | bash`), `env GH_REPO=`, `timeout`, `/usr/bin/gh`, laço, subshell, `-l` e lista por vírgula; GraphQL por `/graphql`, URL completa e `graphql?x=1` (inclusive `updateLabel`); REST com query, percent-encoding e `DELETE`; `gh label create|edit` e `POST labels` com o nome. `gh label create bug` e `--add-label bug` seguem livres.

### Recomendações (não bloqueiam)
- **R7 (baixa) Regressão do delta: `#` dentro de `${...}`.** Evidência: hooks/conformidade.py:241 trata como comentário um `#` precedido de espaço mesmo dentro de expansão de parâmetro, onde o shell não o lê como comentário. `` echo ${x:- #`gh pr edit 70 --add-label afrouxa-regra`} `` sai 0 com a conta `outra-pessoa` em 6ec5095 e barrava em 2e5cc70; o bash real executa a crase (conferido com `echo` no lugar do `gh`). Na sessão de projeto, a mesma linha apontando para o Forge segue barrada. Caminho de ataque: um agente na sessão do Forge escreve a linha de propósito para fugir da guarda; não é escrita comum (ninguém põe espaço e `#` num valor padrão por acaso), é ofuscação, classe que a R-CONTRIB já admite e que o cartão ROTULO-VARIAVEL cobre. Correção mínima: em `conteudos_de_crase`, não abrir comentário dentro de `${`…`}` (contar a profundidade de `${`), ou, mais conservador, com crase depois do `#` e `CITA_ROTULO` no resto da linha, `exigir_dono()`; um caso de teste. Esforço: P. Dono: tech-lead (pode entrar no cartão ROTULO-VARIAVEL ou numa volta curta, a critério do Jarvis).
- **R8 (informativa, anterior a este PR) ANSI-C `$'…'`.** `` echo $'\'' `gh pr edit …` \' `` sai 0 com outra conta em 6ec5095 e já saía em 2e5cc70: o hook e o `shlex` não conhecem o `\'` dentro de `$'…'` e veem a crase como aspa simples. Ofuscação deliberada; mesmo cartão ROTULO-VARIAVEL.
- **R1 (baixa) Rótulo por variável, `xargs`, alias e escape JSON** e **R6 (informativa) profundidade acima de 3:** sem mudança desde o parecer anterior; R1 segue no cartão ROTULO-VARIAVEL.
- **Dono vem do plugin.json, não do remoto:** sem mudança no delta; o registro no corpo do PR (recomendação 4 do review) segue pendente para a abertura do PR.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática, sonda local com `gh` falso pelo harness de `tests/test_hooks.py`, comparação com o hook de 2e5cc70 numa cópia em `$TMPDIR`, os 2 testes novos (`python3`, `git`, `bash` só com `echo`). `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH (lacuna; o delta não traz dependência, workflow nem segredo). O login do dono nos `gh` falsos dos testes não é segredo.
