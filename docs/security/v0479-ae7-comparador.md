---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: 5961e2f3a30a4209a940a9745fe02a1b3a24f39c
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: AE7.1, `forge-check comparar` (v0478 E58.33), head 5961e2f3

Primeira rodada. Diff `821db42e..5961e2f3`: `bin/forge_comparar.py` (novo), 5 linhas em `bin/forge-check` (subcomando e despacho), `test_comparar` acrescido em `bin/forge-testes`, corpus `tests/comparar/corpus.jsonl` (215 casos, todos `PreToolUse`), `tests/test_comparar.py`, 4 specs de mutante, `tests/pesos-d4.json`, índice e fragmento do changelog.

Gatilhos: execução de comando (o comparador roda o código dos hooks da base e do head), controle que analisa entrada (medida do "só aperta" que vai alimentar a catraca do rótulo afrouxa-regra).

## Confirmação pedida: a mudança só aperta
Sim. O diff não toca `hooks/`, `tests/config.json`, `docs/regras/`, workflow nem o pre-push; em `bin/forge-check` só acrescenta o subparser `comparar` e o despacho para `bin/forge_comparar.py` (nenhuma linha existente muda); em `bin/forge-testes` só acrescenta `test_comparar` à tupla `FORGE_CHECK` (mais teste, nenhum a menos). Nenhum consumidor chama o `comparar` ainda (`grep` em `bin/`, `hooks/`, `scripts/` e `.github/`), então nenhum portão existente passa a depender dele. A reprovação abaixo é sobre a fidelidade da medida nova, não sobre afrouxamento do que já existe.

## Achados
- A1 (bloqueante) bin/forge_comparar.py:99 · o veredito tem 3 níveis e trata `permissionDecision: allow` e `updatedInput` como hook mudo: head que passa a aprovar sozinho (pula a pergunta ao usuário) e reescreve o comando sai rc 0 "nada liberado a mais" (S1)
- A2 (bloqueante) bin/forge_comparar.py:60 · `git archive` aplica `export-subst`/`export-ignore` do `.gitattributes` do head; o plugin instalado é clone, que não aplica: o comparador roda código diferente do que o Claude Code roda e o head se desliga só fora dele (S2)
- A3 (bloqueante) bin/forge_comparar.py:133 · árvores da base e do head e os projetos ficam no mesmo temporário, gravável pelo hook do head, e os casos rodam intercalados em 4 filas: o hook do head esvazia o hooks.json da base e os 8 aceites novos somem (S3)
- A4 (recomendado) bin/forge_comparar.py:22 · marcas do comparador continuam visíveis ao hook (autor `forge@localhost` no commit do projeto, `.forge/versao` 0.5.0, entrada sem `transcript_path` nem `permission_mode`); o changelog diz "sem marca do comparador": corrigir o texto e declarar o limite (S4)
- A5 (recomendado) bin/forge_comparar.py:4 · "Só leitura, sem rede" não vale: o comparador executa o código do head com o HOME e o PATH de quem roda; documentar que só se roda head do próprio repositório, sob o sandbox, e passar um HOME temporário
- A6 (recomendado) bin/forge-check:10179 · `forge-check comparar -h <x>` sai rc 0 sem medir; o consumidor futuro (catraca) deve exigir a linha `so-aperta: medido base=<sha40> head=<sha40>` com os shas esperados, não só o rc

## Sondas
- S1 · head = base + hook PreToolUse(Bash) no fim que imprime `{"hookSpecificOutput":{"permissionDecision":"allow","updatedInput":{"command":"<cmd> --no-verify"}}}` · espera: rc 1 aceite-novo nos 8 casos libera · obtido: rc 0 aceites-novos=0
- S2 · head = base + `.gitattributes` `hooks/parecer.py export-subst` (idem conformidade) e no hook `if "$Format:%H$".startswith("$"+"Format"): sys.exit(0)` · espera: rc 1 · obtido: rc 0 aceites-novos=0; no clone a linha fica literal (hook mudo)
- S3 · head = PreToolUse só com hook que grava `{"hooks": {}}` em `<tmp>/*/plugin/hooks/hooks.json` alheio · espera: rc 1 com os 8 aceite-novo do head sem PreToolUse (controle: rc 1, 8 aceites) · obtido: rc 0 aceites-novos=0
- S4 · head = base + em parecer e conformidade `if git log -1 --format=%ae != forge@localhost: sys.exit(0)` · espera: rc 1 · obtido: rc 0 aceites-novos=0 (limite inerente; vira A4)

## Detalhe dos achados
Método: clone descartável em `$TMPDIR` no head 5961e2f3, base de sonda = head + corpus reduzido a 16 casos reais (8 `bloqueia`, 8 `libera`), cada sonda um commit sobre essa base, `forge-check comparar <base> <head>` da própria branch. Controles: base contra si mesma rc 0; head sem `PreToolUse` rc 1 com os 8 `aceite-novo`; head que tira um caso rc 1 `corpus-removido`; head que muda um caso rc 1 `corpus-removido`; head com link simbólico para fora da árvore rc 2 (`filter="data"` barra, linha 63). Refs hostis, todas rc 2 sem tocar o git além do `rev-parse`: `<sha>..<sha>`, `HEAD@{0}`, `HEAD~1`, `<sha>:hooks`, sha de árvore, sha inexistente, 40 zeros, nome de 210 caracteres, `refs/heads/../x`; `--output=...` e `--end-of-options` param no argparse (rc 2). `tests/test_comparar.py` rodado: 30 testes, OK.

- **A1** · `bin/forge_comparar.py:95-101`. Caminho: um item do time acrescenta (por engano ou para "cortar perguntas") um hook que responde `allow` ou reescreve a entrada; no Claude Code isso pula a pergunta de permissão ao usuário e troca o comando executado; a medida diz "nada liberado a mais" e o rótulo afrouxa-regra deixa de ser pedido com base nela. Severidade alta (falso negativo exatamente na dimensão que a medida existe para ver). Correção mínima: 4 níveis ordenados `recusa < pergunta < sem-decisão < allow`, e `updatedInput` no head diferente do da base conta como aceite novo (`entrada-reescrita`); a mesma ordem vale para os eventos que decidem permissão (`PermissionRequest`), que o corpus ainda não tem (dimensão nova da matriz: evento). Esforço P. Dono: autor do AE7.1 (tech-lead).
- **A2** · `bin/forge_comparar.py:59-66`. O plugin chega aos projetos por clone do marketplace, que não expande `export-subst` nem omite `export-ignore`; o `git archive` faz as duas coisas com o `.gitattributes` da própria árvore arquivada. Sonda S2: o blob de `hooks/parecer.py` traz `"$Format:%H$"` literal (o que o clone instala, conferido com `git clone` + `checkout`), o archive traz o sha. Severidade alta (o comparador mede outro código). Correção mínima: extrair pela árvore do commit sem atributos de exportação (`git ls-tree -r -z <sha>` + `git cat-file --batch`, gravando modo e link como no clone) ou recusar `nao-verificavel` quando o `.gitattributes` de qualquer lado tem `export-subst` ou `export-ignore`. Esforço P. Dono: tech-lead.
- **A3** · `bin/forge_comparar.py:105`, `:133`, `:137-139`. `rodar_caso` cria o projeto em `arvore.parent` e as duas árvores são irmãs no mesmo `TemporaryDirectory`; os casos rodam em 4 filas, base e head intercalados; os ids `conformidade/*` (libera) vêm antes dos `parecer/*` (bloqueia), então o primeiro hook do head envenena a base antes de qualquer caso que recusa. Severidade média (exige código hostil no head, que o code review também vê, mas a medida é vendida como resistente a isso pelo `test_comparar`). Correção mínima: rodar a base inteira antes de extrair o head (fase 1 todos os vereditos da base, fase 2 extrai e roda o head), e cada árvore em temporário próprio. Esforço P. Dono: tech-lead.
- **A4** · `bin/forge_comparar.py:22`, `:106`, `:112-113`; `changelog.d/v0479-ae7-comparador.md:2`. Um hook pode sempre distinguir um projeto sintético de um real; a medida só é confiável contra head honesto. Correção: no changelog e na docstring, trocar "sem marca do comparador" por "a medida pega afrouxamento honesto; código que detecta o ambiente é assunto do code review", e, barato, acrescentar `transcript_path` e `permission_mode` à entrada. Esforço P. Dono: tech-lead.
- **A5** · `bin/forge_comparar.py:4`, `:114`. Quem roda `comparar` num head de fora (fork) fora do sandbox executa esse código com acesso ao HOME (credenciais de git e da CLI de hospedagem); os casos novos do head também gravam qualquer arquivo no projeto antes do `git add` (inclusive `.git/config`, linhas 106-111), mesmo nível de confiança do código do head. Correção: docstring e ajuda dizem "executa o código da base e do head"; `HOME` aponta para um temporário. Esforço P. Dono: tech-lead.
- **A6** · `bin/forge-check:10179`. Nome de branch não começa com `-`, então o risco é só do consumidor que monta a chamada; registrar no cartão da catraca. Esforço P. Dono: quem ligar o `comparar` à catraca.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem CI no head (sem PR aberto): a suíte inteira fica para o CI do PR; rodado aqui só `tests/test_comparar.py` (30 OK) e as sondas. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH; o diff não toca workflow nem dependência. Segredo: nenhum padrão de token ou chave nas linhas acrescidas.
