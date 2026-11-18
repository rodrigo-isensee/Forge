---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-cota
commit: e0ac850854ef8d5efc64507f04379864c893f803
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0475-ci-cota (E3.59, cobre E3.42)

Gatilhos: credencial de integração externa (token do `gh`), custo (R-CUSTO), comando sugerido ao dono.

## Resumo
`bin/forge-cota-ci` faz só leitura: chama `gh api <endpoint>` sem `-X`, `--method`, `-f`, `-F` nem `--input` (bin/forge-cota-ci:28), logo GET; usa a credencial que o `gh` já tem e não lê, grava nem exibe token. Lista de argumentos sem shell (bin/forge-cota-ci:20, :28), com timeout de 60 s. Nenhum workflow a chama (grep na branch: só skills, changelog e testes), então não consome minuto do Actions nem segredo do CI; os testes usam `gh` falso, sem rede (tests/test_cota_ci.py:16-25). A saída ao dono é só os dois números e o percentual (bin/forge-cota-ci:54-57) ou a 1ª linha do stderr do `gh` e o comando sugerido (bin/forge-cota-ci:89-90). Aprovado, com duas recomendações.

## Achados
- A1 (recomendado) bin/forge-cota-ci:90 · a mensagem sugere `gh auth refresh -s user`: amplia o token que os agentes usam (conta do dono) com escrita de perfil, contra o "sem escopo novo" do changelog e da skill ci-cd; trocar pela tela de cobrança do GitHub ou avisar o efeito.
- A2 (recomendado) bin/forge-cota-ci:21 · o dono vindo do origin ou de --dono entra cru no comando impresso para o dono copiar (`$(id)` sai literal); validar contra o formato de login do GitHub (letras, dígitos, hífen) e cair em não verificável.
- A3 (recomendado) tests/test_cota_ci.py:24 · nenhum teste prova que a chamada ao gh é só `api <endpoint>` (GET); um gh falso que registra os argumentos e recusa método ou campo trava a garantia de só leitura.

## Sondas

## Detalhe dos achados
**A1.** Evidência: bin/forge-cota-ci:90. Caminho: o Jarvis repassa a mensagem; o dono roda `gh auth refresh -s user` na máquina em que os agentes usam a mesma conta (decisão do dono de 17/11 20:45: "os agentes usam a minha conta"), e o token passa a ter escopo `user`, que inclui escrita de perfil e e-mails, além do que a ferramenta precisa. Não há ação automática: o dono decide, por isso não bloqueia. Severidade: baixa. Correção mínima: trocar a dica por "veja em Settings > Billing no navegador" ou, se mantida, dizer que amplia o token dos agentes e que é decisão do dono (R-DECISAO). Esforço P. Dono: devops-engineer.

**A2.** Evidência: bin/forge-cota-ci:21 (regex `[^/]+` aceita `$`, `(`, espaço, `?`) e :89-90. Reproduzido com `gh` falso: `--dono '$(id)'` e origin `https://github.com/$(id)x/repo` imprimem `gh api /users/$(id)/settings/billing/actions`. Caminho: exige controle do `origin` local ou do argumento, que já são do usuário; a chamada em si é lista de argumentos e GET, sem injeção. Risco só no copiar e colar do comando sugerido. Severidade: informativa. Correção mínima: `re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", dono)` senão `não verificável`. Esforço P. Dono: devops-engineer.

**A3.** Evidência: tests/test_cota_ci.py:16-25 (o `gh` falso ignora os argumentos). Caminho: regressão futura que acrescente método ou campo passa na suíte. Severidade: informativa. Correção mínima: o `gh` falso grava `$*` num arquivo e o teste confere igual a `api /users/dono-x/settings/billing/actions`. Esforço P. Dono: qa-engineer.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Lido: diff 2fa505d7..e0ac8508 inteiro (bin/forge-cota-ci, tests/test_cota_ci.py, tests/mutantes/v0475-ci-cota.json, skills/ci-cd, skills/esperar-estado, changelog.d). Rodado: `python3 -m unittest test_cota_ci` (11 testes, OK) e as sondas de A2 com `gh` falso, sem rede. Suíte inteira: sem rodada de CI nem PR na branch neste head; fica para o CI do PR (R-REVIEW). Ferramentas ausentes do PATH: gitleaks, zizmor, actionlint, semgrep (lacuna; nenhum workflow mudou).
