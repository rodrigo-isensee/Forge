# BP15: entrega de produto nos modelos (desenho)

Pedido v0478, etapa E158.1 (cartão BP15-ENTREGA-DE-PRODUTO, origem `docs/propostas/boas-praticas-1911.md`, linha BP15). Só desenho: nenhum modelo de projeto, workflow, script, teste nem CI foi alterado; os modelos ficam fora até o dono aprovar. Público: o dono e o time. Revisão: 2026-12-24. Base lida: develop 789fc141.

Quatro frentes, neutras de stack (ADR 0001) e de projeto (`R-NEUTRO`): (1) preview por PR; (2) feature flag; (3) deploy com rollback; (4) telemetria de uso. Custo zero (`R-CUSTO`): nada aqui exige serviço pago, runner pago, nuvem nem conta nova; onde a única saída gratuita depende do plano do dono, a fatia vira decisão e fica parada até ele responder. Regra do dono de 21/11 (item 3): trava nova de processo só entra se outra sair ou simplificar; cada fatia diz se é trava. Nenhuma abaixo é trava: todas são modelo opcional, copiado pelo `bin/forge-init` e levado pelo `forge-upgrade`.

## 1. O que já existe

| Frente | Evidência | O que cobre |
|---|---|---|
| 1 | `templates/projeto/.github/workflows/ci.yml:1-60` | CI de PR em modelo; suíte só em PR e nas branches do fluxo; nenhum job de preview nem de deploy |
| 1 | `skills/ci-cd/SKILL.md`, "Ambientes e releases" | promoção homologação → produção com aprovação do dono (`environments`); sem texto de preview |
| 2 | `grep -ri "feature flag"` em `skills/`, `agents/`, `docs/regras/`, `stacks/`, `templates/` | nenhuma ocorrência: não há orientação nem modelo |
| 3 | `skills/ci-cd/SKILL.md`, "Princípios" e "Ambientes e releases" | "Reversível", "reimplantar a versão anterior", "confira a migração reversível antes do deploy"; sem roteiro executável |
| 3 | `skills/observabilidade-incidentes/SKILL.md`, "Roteiro de incidente" | conter = reverter a última entrega; remete ao rollback da `ci-cd` |
| 3 | `templates/projeto/scripts/pos-release`, `docs/devops/pos-release.md`, `pos-release.passos` | roteiro pós-release com ensaio em alvo descartável e real, alvo sempre explícito (molde reaproveitável para o rollback) |
| 4 | `skills/observabilidade-incidentes/SKILL.md`, "Logs" e "Métricas e alertas" | quatro sinais do serviço (erro, latência, tráfego, saturação); nada sobre uso do produto |
| 4 | `skills/cyber-security/SKILL.md`, "LGPD" | minimização e base legal; vale como limite da telemetria |

O que falta: modelo de preview, orientação e modelo de flag, roteiro de rollback testável e medida de uso. A skill descreve o princípio; o projeto não recebe peça pronta.

## 2. Fontes atuais (lidas em 2026-11-24)

- GitHub Docs, "Deployment environments" e "Manage environments" (`docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments`): ambientes e regras de proteção valem em repositório público em todos os planos; em repositório **privado**, ambiente exige Pro, Team ou Enterprise, e `required reviewers` e `wait timer` só existem em repositório público nos planos Free, Pro e Team.
- GitHub Docs, "Using custom workflows with GitHub Pages": Pages está em repositório público com Free; em privado, só em plano pago.
- GitHub Docs, "Billing for GitHub Actions": a franquia gratuita hoje é um valor em dinheiro por mês (Free: USD 12 de computação, 500 MB de artefato, 10 GB de cache por repositório), não mais um número fixo de minutos; sair dela é cobrança (`R-CUSTO`).
- OpenFeature, especificação (`openfeature.dev/specification`): API neutra de fornecedor para flag; toda avaliação recebe um valor padrão, usado se o provedor falha.
- OpenTelemetry, "Signals" (`opentelemetry.io/docs/concepts/signals/`): métricas, logs e traces como sinais padrão e neutros de fornecedor.

Consequência para o custo: a única parte que o Forge não consegue entregar gratuita e igual para todo projeto é o **preview hospedado** e a **aprovação do dono por `environments`** em repositório privado. O resto roda só com arquivo no repositório.

## 3. Corte (fatias independentes, nesta ordem)

**C1, rollback executável (não é trava).** `templates/projeto/docs/devops/rollback.md` e `rollback.passos`, no mesmo molde do `pos-release`: o alvo é sempre explícito, sem valor padrão; ensaio só em descartável, real só no real; para no primeiro erro e termina com uma linha de resumo. Passos: (1) ler a versão anterior da tag `vX.Y.Z` anterior; (2) reimplantar o mesmo artefato (a promoção é de artefato imutável, `ci-cd`, "Princípios"); (3) health check e smoke test; (4) registrar versão e hora. Migração: o plano de entrega só vai a produção com a volta da migração escrita pelo dev da stack (já é regra da `ci-cd`; o modelo ganha uma linha de conferência no `pull_request_template.md`). Dono: `devops-engineer`. Vai primeiro porque é o único que reduz risco já existente e não depende de plano nem de ferramenta.
- Pronto quando: (a) o ensaio roda num alvo descartável e termina `rollback: OK`; (b) alvo vazio ou igual ao real recusa com saída 2 sem rodar passo; (c) `shellcheck` e `bash -n` verdes; (d) o roteiro cita a skill `observabilidade-incidentes` como gatilho; (e) o teste de neutralidade segue verde.

**C2, feature flag mínima (não é trava).** Orientação em `skills/engineering-practices/SKILL.md` (o texto do princípio, uma fonte só) e modelo `templates/projeto/docs/engineering/feature-flags.md`: a flag é arquivo de configuração versionado (chave, dono, data de criação, data de remoção, valor padrão), lido na partida; o padrão é **desligada**; flag com data vencida é achado de review; toda flag nasce com cartão de remoção. A interface segue a forma da OpenFeature (avaliar com valor padrão) sem exigir a biblioteca, que é escolha da stack (`stacks/<stack>/`, não aqui). Sem serviço de flag hospedado (custo e dado de usuário fora). Dono: `devops-engineer` (modelo) e `software-architect` (quando a flag muda contrato).
- Pronto quando: (a) o modelo traz a tabela de flags com os cinco campos e o procedimento de remoção; (b) a skill ganha no máximo dez linhas; (c) nenhum nome de biblioteca ou linguagem no texto do núcleo; (d) nenhum teste novo de recusa (é orientação).

**C3, telemetria de uso sem dado pessoal (não é trava).** `templates/projeto/docs/devops/uso.md`: o que medir (ativações por função, erro por função, tempo até a primeira ação útil; contagem, nunca conteúdo), onde fica (log estruturado do serviço, já exigido pela skill de observabilidade; leitura por consulta local, sem painel hospedado) e o limite (sem identificador de pessoa, sem corpo de requisição; agregado por dia). A skill `observabilidade-incidentes` ganha um parágrafo: sinais de uso ao lado dos quatro sinais do serviço, com a mesma regra de nada pessoal. Dono: `devops-engineer`; o `security-engineer` valida o limite (LGPD, `cyber-security`).
- Pronto quando: (a) o modelo lista as métricas permitidas e as proibidas; (b) o parágrafo da skill tem no máximo seis linhas; (c) a lista de campos proibidos reproduz o conjunto inteiro da skill de LGPD, sem amostra; (d) parecer de segurança aprovado.

**C4, preview por PR (depende do dono; ver decisão D1).** Há duas saídas sem custo e uma com dependência de plano:
- **C4a, preview como artefato do CI (sempre gratuita).** Job opcional no `ci.yml` do modelo que constrói e anexa o resultado (pacote estático ou relatório) como artefato do run, com `retention-days: 3` (franquia de 500 MB no Free): o revisor baixa e abre localmente. `permissions: contents: read`; sem segredo; sem `pull_request_target`; só PR do próprio repositório (`github.event.pull_request.head.repo.full_name == github.repository`). Gasta minutos do run que já existe, não um run novo.
- **C4b, preview hospedado (Pages).** Gratuito só em repositório público; em privado exige plano pago, o que é custo (`R-CUSTO`). Fica **fora** do modelo até o dono autorizar plano ou tornar o projeto público; entra então como workflow à parte, sem escrever na `main` (`R-MAIN`).
- Dono: `devops-engineer`; o parecer de devops cobre `.github/`. A mudança de workflow segue pelo caminho do `tech-lead` e do dono (o token do bot não tem o escopo `workflow`).
- Pronto quando (C4a): (a) `actionlint` e `zizmor` verdes; (b) PR de fork não roda o job; (c) o artefato some em 3 dias; (d) o minuto medido por `forge-cota-ci` não sobe mais que 20% numa release (senão cartão de melhoria, `ci-cd`, "Tempo e dependências").

**C5, deploy promovido com aprovação (depende do dono; ver decisão D2).** O modelo de deploy usa `environments` (homologação, produção) com aprovação do dono, como pede a `ci-cd`. Pela fonte da seção 2, isso só funciona em repositório privado com plano pago, e `required reviewers` não existe para privado nos planos Free, Pro e Team. Sem decisão do dono, **nenhum workflow de deploy entra no modelo**: o rollback (C1) e o roteiro de promoção ficam manuais e documentados. Dono: o dono configura `environments` (`R-CONFORMIDADE`); o `devops-engineer` propõe.

## 4. Casos de abuso (para o `qa-engineer`, quando cada fatia for aberta)

- C1: alvo igual ao padrão do projeto, ou variável vazia · `rollback` → script · recusa com saída 2, nenhum passo roda.
- C1: passo do meio falha · script · para, diz qual foi e quantos não rodaram.
- C2: flag com data de remoção vencida · review · achado `recomendado`, não bloqueio.
- C3: evento de uso com e-mail, IP ou corpo de requisição · log → consulta · fora da lista permitida; o review de segurança recusa.
- C4a: PR de fork com workflow que lê segredo · PR → CI · o job não roda e nenhum segredo chega ao código do fork.
- C4a: artefato de preview com chave ou `.env` dentro · CI → artefato · a varredura de segredo do projeto (BP10, C2) pega antes do envio; o job só empacota o que o build gera.

## 5. Decisões do dono

- **D1, preview por PR (`R-DECISAO`).** Opções: (a) só C4a, artefato no CI, custo zero; (b) C4a mais C4b, e o projeto passa a ser público ou o dono contrata plano que habilite Pages em privado (custo, `R-CUSTO`); (c) sem preview. Recomendação: **(a)**. Vale em qualquer plano, não expõe o produto e não cria hospedagem.
- **D2, deploy com aprovação (`R-DECISAO`).** A aprovação do dono por `environments` em repositório privado pede plano Pro, Team ou Enterprise, e `required reviewers` pode pedir Enterprise (fonte da seção 2; confira o plano de cada projeto antes). Opções: (a) manter promoção manual com roteiro escrito e rollback ensaiado (C1), sem workflow de deploy no modelo; (b) o dono habilitar `environments` onde o plano permitir e o modelo ganhar o workflow de deploy; (c) tornar projeto público, o que muda a regra de segredo (BP10). Recomendação: **(a) agora**, **(b) por projeto**, quando o dono decidir pagar; sem nenhuma dependência de nuvem no modelo (a nuvem e o provedor são ADR do projeto, `software-architect`).
- **D3, ordem e alcance.** Opções: (a) C1, depois C2 e C3, C4 conforme D1; (b) todas juntas. Recomendação: **(a)**, uma PR por fatia (cada uma independente, revisão curta). C1 primeiro porque corrige um risco que já existe.
- **D4, onde mora o texto de flag e de uso.** Opções: (a) parágrafos curtos nas skills `engineering-practices` e `observabilidade-incidentes` mais os modelos do projeto; (b) skill nova. Recomendação: **(a)**: não cria arquivo nem agente novos e o teste `AntiDuplicacao` segue valendo (uma fonte por regra, ADR 0002).

## 6. Fora do corte

Serviço de flag hospedado, plataforma de analytics, APM e painel hospedado (custo e dado de usuário em terceiro); escolha de biblioteca de flag, de telemetria ou de provedor de nuvem (ADR do projeto e `stacks/<stack>/`); blue/green e canário (exigem topologia e custo de duas instâncias; reavaliar quando um projeto tiver produção real); preview com dado de produção (nunca: o preview usa dado de teste); alterar `environments` ou proteção de branch por `gh api` (`R-CONFORMIDADE`).
