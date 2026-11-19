---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 946926e92ace7f084937459bd12ecea1e096c980
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0478 (guardas do hook `parecer`, E3.32, "Só aperta?")

Volta por delta, com a pergunta do dono (19/11 08:54) sobre o rótulo `afrouxa-regra`. Rodada anterior: `commit 460a8a00` (E3.29, aprovado com A11), no git. Delta lido (`forge-check parecer delta`, `460a8a00..946926e9`): nenhum arquivo do domínio mudou (só os pareceres de review, QA e este). Para a pergunta do dono, relido o diff inteiro do domínio contra a `origin/develop` (`4182a6b9`): `hooks/parecer.py`, `hooks/_gh_api.py` (novo), `bin/forge-testes`, `tests/test_hooks.py` e os mutantes.

Gatilhos: hook de controle (`hooks/parecer.py`, `hooks/_gh_api.py`) que guarda o portão de parecer de todos os projetos e do Forge.

## Achados
- A11 (recomendado) docs/hooks.md:41 · Limites declarados da D4 seguem abertos (nome por expansão na aritmética e valor avaliado como expressão), aceitos pelo critério da D7; o dono confirma pelo Jarvis. Sem mudança desde o parecer `460a8a00`.
- A12 (recomendado) hooks/parecer.py:1286 · Com a sessão numa cópia alheia, `export HOME; cd ~/clone && gh pr ready x` e `: ${HOME:=/x}; cd ~/clone && gh pr ready x` recusavam na develop e passam aqui: a mexida nova deixa a pasta desconhecida e o gh cai na pasta da chamada.

## Sondas

## Só aperta?
**Não.** A mudança aperta quase tudo, mas há dois grupos de entradas que a `origin/develop` recusava e este head aceita. Pelo pedido do dono, o rótulo `afrouxa-regra` espera a decisão dele.

Provas de que aperta (o que antes era recusado continua recusado):
- Nenhuma fixture da develop mudou nem saiu (`git diff --diff-filter=DMR origin/develop...HEAD -- tests/hooks/` vazio). As 529 fixtures do `parecer` que vêm da develop (407 de recusa) rodaram neste head pelo `Fixture` de `tests/test_hooks.py`: OK, 162 s, nenhuma falha.
- As 54 fixtures novas rodaram contra o `hooks/parecer.py` da develop (cópia por `git archive`). As 15 de libera também liberam lá: nenhum legítimo novo era recusado. Das de recusa, 39 não recusavam assim na develop (38 davam 0; 1 recusava com outra mensagem): é o que a mudança passou a recusar.
- Mudanças só de aperto, lidas no código: `mexidas_na_linha` (`hooks/parecer.py:638`) devolve um superconjunto das mexidas de antes (o `sem_condicao` não tira nenhum comando de `LE_VARIAVEL`; `NOMEIA`, `builtin`/`command`, `source`/`.` e `GIT_*` só somam; o `split("=")` contém o `split("=", 1)[0]` de antes); `mexidas_do_texto` (`:681`) só soma; o bloqueio de nome de comando incerto, `arquivo_trocado_na_linha` e `graphql_no_clone` só recusam a mais; `repo_da_url` só acrescenta repositório ao `aponta_para_o_forge`; `pasta_do_gh` só troca a pasta quando `hook.projeto` da pasta do gh é None, caso em que `pull_request`, `pronto_de_pr` e `merge_de_pr` da develop saíam sem conferir: ou recusa, ou confere no clone da sessão, ou devolve a mesma pasta. No `_gh_api.py`, `~` e curinga no caminho passam a ilegíveis.

O que antes era recusado e agora é aceito:
1. **Pasta desconhecida que cai na pasta da chamada (A12).** As mexidas novas de `HOME` e `CDPATH` (`export HOME`, `${HOME:=v}`, aritmética, `source`, `builtin`, nome por expansão) deixam sem resolver o `cd ~/…` ou o `cd` relativo que a develop resolvia. Sem pasta, o gh vale na pasta da chamada (`hooks/parecer.py:1286`), e numa sessão em cópia alheia o `pasta_do_gh` a devolve (`:1063`), que não é projeto: libera. Sondas, com `CLAUDE_PROJECT_DIR` e pasta da chamada na cópia alheia, `HOME={tmp}` e o clone em `{tmp}/proj` com `feature/x` sem parecer: `: ${HOME:=/x}; cd ~/proj && gh pr ready feature/x` e `export HOME; cd ~/proj && gh pr ready feature/x` dão 2 na develop e 0 aqui. O controle `cd ~/proj && gh pr ready feature/x` dá 2 nos dois. Com a sessão no clone, as mesmas linhas dão 2 aqui.
2. **Leitura do arquivo do `gh api` corrigida (GH-API-LEITURA-UNICA).** O hook passou a ler o mesmo arquivo que o gh: `--input=@q.json` lê `@q.json`, não `q.json`; em `-F c=x=@y` o hook lê `y` (o gh manda o texto `x=@y`, sem arquivo). Sondas no clone: `gh api graphql --input=@q.json` com `q.json` mutante e `@q.json` de leitura; o mesmo sem `q.json`; e `gh api graphql -F query=x=@y` sem o arquivo `x=@y`: 2 na develop, 0 aqui. O gh, nesses três, não manda a mutação: era recusa a mais da develop, não contorno. Em troca, `--input=@q.json` com `@q.json` mutante, que a develop liberava, agora recusa (fixture `leitura-api-arroba-no-input-bloqueia`).

## Detalhe dos achados
**A12 (baixa, recomendado).** Evidência: `hooks/parecer.py:1286` (`raiz_gh = pasta or hook.cwd()`, linha que já existe na develop) e `hooks/parecer.py:1063` (sessão sem clone e em cópia de trabalho devolve a pasta). Caminho de ataque: o agente, numa sessão aberta num repositório que não é projeto do Forge, entra no clone com `cd ~/…` e roda `gh pr ready` ou `gh pr merge` sem parecer, com uma mexida de `HOME` antes. Não dá capacidade nova: `HOME={tmp}; cd ~/proj && gh pr ready feature/x` e `declare HOME; cd ~/proj && gh pr merge feature/x` já davam 0 na develop e seguem dando 0 aqui (mesmas sondas). A mudança só põe mais formas de linha na mesma brecha. Por isso fica como recomendado, sem bloquear: o código não passa a aceitar uma ação que antes ficava fora de alcance. A brecha só fecha quando a pasta desconhecida para de cair na pasta da chamada. Correção mínima: em `pasta_do_gh`, com `resolvida` falso, recusar antes do `return pasta` de `:1063` (a pasta real do gh pode ser um clone ou projeto), com fixtures das quatro formas (`HOME=`, `declare HOME`, `export HOME`, `${HOME:=v}`) na sessão em cópia alheia e um legítimo (`gh pr ready x` na cópia alheia, sem `cd`). Esforço P. Dono: autor do pedido; se o dono preferir, fica para um pedido próprio, porque a brecha está na develop.

## Estado dos achados anteriores
- **A11:** aberto como recomendado, sem delta.
- **A1 a A10:** fechados; o delta não toca neles.

## Riscos aceitos e ferramentas
Nenhum risco aceito neste parecer. As sondas foram fixtures locais fora do repositório, montadas pelo `Fixture` de `tests/test_hooks.py`: a develop rodou da cópia por `git archive HEAD` com o `hooks/parecer.py` de `origin/develop` e sem `hooks/_gh_api.py`. A suíte inteira roda no CI; o brief não cita CI deste head. Lacuna: `gitleaks` e `semgrep` não estão no PATH. O diff não traz segredo nem dependência.
