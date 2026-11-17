---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-ruleset-tags
commit: 378733aee5840aed97052f9411f6b1aa3ebebfa5
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: ruleset de tags v* (v0474, E3.5)

Objeto: `docs/devops/ruleset-tags-v.md` no head 378733ae (único arquivo do diff `bda457e4..378733ae`). Decisão do dono (pedido v0474, 17/11 16:45): só a automação de release cria `v*`; ninguém mais, nem administrador nem a conta do dono que os agentes usam, cria, move ou apaga. Nenhum agente aplica. Leitura no GitHub só por `gh api` GET.

## Gatilhos
Gatilhos: CI e release, proteção de branch e tag, credenciais e tokens, cadeia de suprimentos (tag v* é o que a atualização dos projetos consome).

## Achados
- A1 (bloqueante) docs/devops/ruleset-tags-v.md:80 · Diz que a regra protege de agente, mas o token dos agentes tem admin e escopo workflow: qualquer workflow de qualquer branch pede contents: write e cria v* como github-actions (o bypass); e o admin desliga o ruleset. Declarar o resíduo e propor o fechamento.
- A2 (bloqueante) docs/devops/ruleset-tags-v.md:59 · Caminhos 1 e 2 guardam a chave como segredo do repositório, que todo workflow de qualquer branch lê; o bypass DeployKey vale para toda deploy key, e o admin cria uma. Exigir segredo em environment só da main e dizer o limite da deploy key.
- A3 (recomendado) docs/devops/ruleset-tags-v.md:54 · Conferir na resposta 201 que `bypass_actors` voltou com a integração 15368 (descarte silencioso) antes de esperar a release; hoje o 1º sinal é a release falhar.
- A4 (recomendado) docs/devops/ruleset-tags-v.md:74 · O teste de apagar não roda: com o ruleset valendo, v9.9.9-teste nunca nasce. Criar antes de aplicar uma tag de teste fora de SemVer (ex.: v0-teste-ruleset) num commit antigo e tentar mover e apagar depois.

## Sondas

## Detalhe dos achados

**Conferido e correto (sem achado):** alvo `refs/tags/v*` com `target: tag`, regras `creation`, `update`, `deletion`, `bypass_mode: always`, sem papel admin nem conta no bypass (doc:38-52, passo 3 da tela na linha 67). `release.yml` cria a tag por `gh release create` com `github.token` (`.github/workflows/release.yml:57-71`, `contents: write` só no job `release`, `persist-credentials: false`); a criação por API de release é ator `github-actions`, o mesmo id 15368 dos checks obrigatórios (ruleset 26701749, lido). Com o bypass aceito, `gh release create` passa e o workflow não muda. As 57 tags existentes ficam protegidas contra mover e apagar (contagem conferida por `git/matching-refs/tags/v`). Reversão e custo zero corretos (`R-CUSTO`). Caminho 3 (só `update`/`deletion`) corretamente marcado como abaixo da decisão.

**Aceite do bypass 15368:** não confirmável sem aplicar (só GET permitido). Concordo com o devops: tratar como tentativa. O risco de aplicar é só de disponibilidade (a próxima release falha na tag), não de segurança; A3 antecipa o sinal.

**Outros caminhos de um agente com a conta do dono, depois do ruleset:**
- `git push origin vX`, `gh api -X POST .../git/refs`, `gh release create` ou `POST .../releases` pela conta do dono: barrados pelo ruleset (a conta não está no bypass). Hoje o hook `conformidade` já barra `gh api` mutante em `git/refs`, `contents/` e `rulesets` (`hooks/conformidade.py:148`, `:3046-3051`), mas não `gh release create` nem `git push` de tag nova (o pre-push só barra mover tag, `.githooks/pre-push:156`): o ruleset fecha esses dois.
- `workflow_dispatch`: `release.yml` não tem; `ci.yml:25` tem, mas todo job é `contents: read`. Só vira caminho junto com a edição de workflow (abaixo).
- Editar workflow (A1): `gh auth status` lido mostra no token dos agentes os escopos `repo`, `workflow`, `admin:public_key`, `delete_repo` e outros; a conta tem `permissions.admin: true`. Um workflow novo ou editado numa branch `melhoria/*` (por push ou PR do próprio repositório) declara `permissions: contents: write` (o padrão `read` do repositório, lido em `actions/permissions/workflow`, só vale quando o workflow não declara) e roda `gh release create vX` com `github.token`: o ator é `github-actions`, que está no bypass. O ruleset não distingue o workflow nem a branch de origem. Além disso, o admin desativa o ruleset por API (o hook barra `gh api`, mas não uma chamada HTTP direta com o mesmo token) e os rulesets de branch dão bypass `always` ao papel admin (ids 25432260 e 26701749), então a conta empurra direto na `main`.
  Caminho de ataque: agente desviado (injeção de instrução vinda de conteúdo de um projeto, ou erro) cria `v9.99.0` num commit qualquer; a atualização automática dos N projetos consome tags `v*` (`bin/forge_versoes.py:100-110`). Severidade: alta pelo impacto (cadeia de suprimentos de todos os projetos); probabilidade baixa, exige ação deliberada em vários passos e contra os hooks. Não é introduzido por este documento, mas o documento afirma o contrário (linha 80) e o dono decide com essa informação.
  Correção mínima (devops, texto): substituir a frase da linha 80 por um parágrafo "Resíduo" que diga que, enquanto os agentes usarem um token com administração e escopo `workflow`, a regra barra o engano e o comando direto, não um agente que edite workflow ou desative o ruleset; e indicar o fechamento, sem custo: os agentes passam a usar um token de acesso fino (fine-grained) só deste repositório, com Contents e Pull requests em escrita e **sem** Administration nem Workflows; o token com admin fica só com o dono, fora da sessão dos agentes. Decisão do dono (`R-DECISAO`). Esforço P (texto); a troca de token é do dono.

**A2, alternativas:** App próprio (caminho 1): grátis; segredo = chave privada do App. Guardado como segredo do repositório, qualquer workflow de qualquer branch o lê no evento `push` ou `pull_request` do próprio repositório, e o resíduo de A1 se repete com o App. Correção mínima: o segredo vai num environment (ex.: `release`) com regra de branch de implantação só `main`, e o job `release` declara `environment: release` (environments são gratuitos em repositório público; hoje há 0, lido). Deploy key (caminho 2): grátis; segredo = chave privada SSH, com o mesmo cuidado do environment; e, pelo que a documentação do GitHub descreve, o bypass `DeployKey` vale para todas as deploy keys do repositório, e a conta admin (escopo `admin:public_key`/`repo`) cadastra uma nova: preferir o App. Nos dois, a proteção só fecha junto com o token fino de A1 (sem admin, o agente não troca a regra do environment). Esforço P (texto); dono: devops.

**A3:** depois do POST, `gh api repos/<repo>/rulesets/<id> --jq .bypass_actors` deve trazer `{"actor_id":15368,"actor_type":"Integration","bypass_mode":"always"}`; vazio = não aceito, seguir para o caminho 1 antes da release.

**A4:** a tag de teste fora de SemVer não é lida como versão (`bin/forge_versoes.py:30-32` exige `vX.Y.Z` inteiro), então não chega aos projetos mesmo se o teste falhar; apagar a tag de teste ao fim exige desativar o ruleset por um instante, feito pelo dono.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `gh api` GET (rulesets, ruleset 26701749 e 25432260, `actions/permissions`, `actions/permissions/workflow`, environments, keys, `git/matching-refs/tags/v`), `gh auth status` (escopos; o valor do token não foi exibido), leitura estática dos workflows e do hook. Lacunas: gitleaks, zizmor e actionlint fora do PATH (não se aplicam a um documento sem segredo nem workflow alterado). Suíte: o diff é só documentação; sem teste novo de abuso a rodar.
