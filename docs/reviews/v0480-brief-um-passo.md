---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-brief-um-passo
commit: e3eb537e61918a03c557abeea98728d2170bb956
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Code review: receita do envio de parecer, um passo por chamada (PR #816)

Escopo: pedido v0478, etapa E130.3 (`R-REVIEW`), sobre E130.1. Item só de texto, um parecer só (sem QA nem segurança). Li o diff inteiro, `git diff 0e59c446..e3eb537e`: 1 commit, 6 arquivos, +20 −6 (`agents/tech-lead.md`, `agents/qa-engineer.md`, `agents/security-engineer.md`, `skills/briefs-e-conferencia/SKILL.md`, a receita nova `skills/briefs-e-conferencia/envio-de-parecer.md` e o fragmento `changelog.d/v0480-brief-um-passo.md`). Nenhum código, guarda ou teste no diff: sem mutante a declarar, teto H1 não se aplica (0 linhas de código).

## Achados
- A1 (recomendado) agents/qa-engineer.md:19 · o ponteiro à receita, aqui e em tech-lead.md:18 e security-engineer.md:16, não traz o caminho `${CLAUDE_PLUGIN_ROOT}/skills/briefs-e-conferencia/envio-de-parecer.md` e nenhum dos três carrega essa skill; o caminho cabe quando o teto der folga (hoje 2 e 4 caracteres)
- A2 (recomendado) agents/tech-lead.md:18 · sem a condição "atrás do remoto" (o mesmo em security-engineer.md:16), "Um passo por chamada e `git pull --rebase origin <branch>`" pode ser lido como pull em todo envio; a condição só está na receita, item 3
- A3 (recomendado) skills/briefs-e-conferencia/envio-de-parecer.md:8 · a receita vale para QA, segurança e devops, mas o exemplo de commit fixa `docs(review)` e o add da linha 7 fixa `docs/reviews/`; trocar por `<tipo>` e `docs/<pasta do portão>/<pedido>.md`
- A4 (recomendado) agents/devops-engineer.md:18 · a receita se diz dos portões com devops, mas o devops-engineer não ganhou o ponteiro nem o `pull --rebase origin <branch>`; alinhar numa próxima passada

## Diretriz 25: o que saiu tem o mesmo sentido num arquivo lido
Conferi cada trecho tirado do texto dos agentes e da SKILL:
- **Lista de pastas de controle** (`bin/`, `hooks/`, `.githooks/`, `tests/catraca.py`), tirada de `agents/qa-engineer.md:21`: está igual em `skills/qa-testing/SKILL.md:93` ("Mutantes declarados nos pedidos de controle"), e `qa-testing` está no `skills:` do frontmatter do qa-engineer, que a carrega. Mesmo sentido, lido.
- **`git add <caminho>` explícito**, tirado dos três agentes: está na receita, item 2 (linha 7: "o seu caminho, explícito; nada de `git add .` nem `-A`"), mais forte que antes. A restrição de fundo (só o parecer) ficou no agente ("só ele" e, na segurança, a lista de pastas intacta).
- **Envio atrás do remoto** (tech-lead "Atrás do remoto: `git pull --rebase` e reenvie"; segurança "recusado por corrida (`behind`)"): o comando ficou no agente, agora com `origin <branch>`; a condição foi para a receita, item 3 (A2).
- **Aviso de achado de 300 caracteres e regra pelo ID**, tirado de `skills/briefs-e-conferencia/SKILL.md:27`: está na receita, item 1, com o mesmo texto. O Jarvis lê a SKILL (`agents/jarvis.md:29`, caminho completo) e ela o manda à receita "nesta skill", o mesmo padrão já usado para `autor-ate-o-merge.md` na linha 24. Além disso, os três agentes seguem com o limite de 300 e o `R-REVIEW` no próprio texto (bloco `Achados`).
- **"ao terminar"/"quando terminar"**: só redação; o "envie" ficou.
- **"durante a implementação" → "na implementação"** (`qa-engineer.md:13`): mesmo sentido.

Conclusão: nada saiu sem destino, e o sentido se mantém. O alcance da receita pelos três portões depende de achar o arquivo pelo nome e pela pasta da skill (a pasta de skill carregada dá a raiz do plugin) ou pelo brief do Jarvis, que a SKILL manda avisar; é o A1, recomendado, porque o que obriga (só o parecer, envio, pull com `origin <branch>`) ficou no texto do agente e o que só a receita traz é o modo de fazer. O caminho completo não cabe hoje: `medir()` de `tests/test_orcamento_instrucao.py` dá tech-lead 8613 de 8615 e qa-engineer 3958 de 3962 caracteres; subir o teto é afrouxar e pede o dono (`docs/regras/orcamento.json`).

## Invariantes e testes
- Trechos de `invariantes` (`tests/config.json`): o único que toca as linhas mudadas é "Commite o parecer na branch revisada" (linhas 383, 404, 417 e 560 do config), presente nos três agentes. `RegrasInviolaveis`, `RegrasComId`, `Neutralidade`, `NeutralidadeDoNucleo` e `TextosDoAgenteEDaRegra` de `tests/test_forge.py`: `Ran 15 tests … OK`.
- Testes dos arquivos tocados (escolhidos da lista de `bin/forge-testes --listar`): `test_orcamento_instrucao`, `test_metricas_texto`, `test_jarvis_nucleo`, `test_citacao`, `test_clareza`, `test_frontmatter_agentes`: `Ran 75 tests … OK`.
- Suíte inteira: só no CI do PR. Na leitura, `bateria (pareceres)` passou e as partes da `suíte` estavam pendentes no run 45273179485; o merge espera o verde.
- A receita não tem teste próprio; é texto de modo de fazer ("É receita, não regra"), sem guarda nova, então não pede mutante nem `## Sem teste`.

## Parecer
Aprovado. O item faz o que E130.1 pede: receita curta, um passo por chamada, ponteiro de uma linha nos três portões, dentro dos tetos, e a diretriz 25 se cumpre trecho a trecho. Commit único em Conventional Commits, em português, com fragmento em `changelog.d/`. Os quatro achados são recomendados e viram cartão depois do merge.
