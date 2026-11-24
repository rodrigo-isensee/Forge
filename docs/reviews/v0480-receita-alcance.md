---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-receita-alcance
commit: f56597cbefd9f17b22078b21773cacbbdddc735c
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E146.2, PR #835)

Diff lido: `9d239dda..f56597cb`, 6 arquivos, +15 -11 (4 agentes de portão, a receita `skills/briefs-e-conferencia/envio-de-parecer.md` e o fragmento do changelog). Só texto, sem guarda: sem mutante; teto H1 não se aplica.

## Achados
- A1 (bloqueante) changelog.d/v0480-receita-alcance.md:1 · Cabeçalho `### Mudado` é tipo inválido: o passo "mudança na fábrica exige fragmento em changelog.d" do CI (run 45320358469, bateria (passos)) falha com "tipo 'Mudado' inválido (use Adicionado, Alterado, Corrigido)". Troque por `### Alterado`.

## Conferência trecho a trecho (diretriz 25)
Cada frase tirada de um agente e onde ela continua, num arquivo que o agente lê pelo ponteiro `${CLAUDE_PLUGIN_ROOT}/skills/briefs-e-conferencia/envio-de-parecer.md` (mesma forma dos ponteiros já usados nos agentes, como `autor-ate-o-merge.md`):
- devops "Modelo em `docs/devops/_modelo.md`" → receita, item 1 ("a partir do `_modelo.md` da pasta do portão (no Forge, em `templates/projeto/`)") com a pasta `docs/devops/` na linha das pastas; `templates/projeto/docs/devops/_modelo.md` existe.
- devops "`forge-check docs` valida" e QA "`forge-check docs` valida" → receita, item 1.
- devops "o arquivo do parecer, com `git add <caminho>` explícito" → receita, item 2 (`git add docs/<pasta do portão>/<pedido>.md`, sem `.` nem `-A`).
- devops "Validade presa ao domínio (`R-REVIEW`)" e tech-lead "Validade presa ao domínio: `R-REVIEW`." → receita, parágrafo de abertura ("a validade do parecer, presa ao domínio, segue no `R-REVIEW`"); o security-engineer mantém a sua.
- QA "(até 300 caracteres)" → receita, item 1 ("Achado até 300 caracteres"); o tech-lead e o security-engineer mantêm o formato no próprio texto.
- devops "envie quando terminar" → "envie": a perda de "quando terminar" não muda o ato.
Nada se perdeu.

## Invariantes e envio
- `tests/config.json` `invariantes`: os 10, 8, 15 e 30 padrões de `agents/devops-engineer.md`, `qa-engineer.md`, `security-engineer.md` e `tech-lead.md` casam no head (conferido por `re.search` em cada um); a receita não tem invariante.
- Envio pela receita nos quatro agentes: "um passo por chamada", ponteiro por caminho, "atrás do remoto, `git pull --rebase origin <branch>`" (condição de volta, achado A2 do #816); Write no item 1 da receita; commit com `docs(<portão>)` e várias `-m`.
- Tamanho: os agentes caíram ou subiram pouco (devops 5155→5133, QA 4043→4029, tech-lead 8798→8793, segurança 6776→6811 caracteres); a medida do PR cita `medir()` com folga em todos; nenhum teto subiu.

## Testes
- `bin/forge-testes --base 9d239dda` (38 módulos afetados, 914 testes no log): falhas só em `test_oraculo_sempre_atual` (git e escrita de arquivo barrados pelo sandbox local) e `test_forge.ForgeCheck.test_raiz_depois_do_subcomando_e_git_isolado` (`gh` sem rede, já anotada no PR); nenhuma lê os arquivos do diff. O CI decide.
- CI do PR no head f56597cb: `bateria (passos)` vermelho pelo A1; `bateria` e `bateria (python 3.14)` vermelhos por dependência dele; as partes da suíte nem rodaram. A suíte verde no CI fica pendente para depois da correção.

## Parecer
Reprovado só pelo A1: defeito provado pelo CI, o merge não passa com ele. O mérito (receita alcançando os quatro portões por caminho, trechos movidos sem perda, invariantes e tetos intactos) está aprovado; na volta, basta o delta do fragmento e o CI verde.
