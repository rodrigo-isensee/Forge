---
id: R-SEGURANCA
titulo: Parecer de segurança quando há gatilho
verificada_por: revisão e hook `parecer` (parecer em docs/security/ exigido no PR e no merge na integração, nos gatilhos que o diff mostra ou que o plano técnico marca)
---
# R-SEGURANCA: Parecer de segurança quando há gatilho

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-14.

- Entrega que toca um **gatilho** tem parecer do `security-engineer` em `docs/security/<pedido>.md` (frontmatter da ADR 0004: `tipo: revisao-seguranca`, `parecer: aprovado|reprovado|riscos-aceitos`), em paralelo ao code review (`R-REVIEW`) e antes do QA. Sem gatilho, o plano técnico diz "sem gatilho de segurança" e nada é exigido.
- Gatilhos: autenticação ou autorização; dados pessoais (LGPD); segredos e configuração (`.env*`, variáveis do CI, credenciais); dependência nova ou versão maior; webhook ou endpoint externo; banco (migração, permissão, consulta com entrada); CI/CD (`.github/`); Docker, Compose e IaC; controles do Forge (`hooks/conformidade.json`, `docs/regras/`, `tests/catraca.py`, `tests/config.json`).
- O hook e o `forge-check pr` detectam pelo diff os casos óbvios: arquivo de travas ou manifesto de dependência (por padrão de nome, de qualquer stack), `.env*`, pipeline, contêiner e IaC (`*.tf`, `*.tfvars`, pastas `infra/`, `deploy/`, `terraform/`, `k8s/`, `helm/`), migração e controles do Forge. Os demais gatilhos o pedido marca em `gatilhos_seguranca` do plano técnico; quem desenha, o `software-architect` com o `security-engineer`, os declara.
- `riscos-aceitos` só vale com o **aceite do usuário** em `docs/security/aceites/<pedido>.md` (frontmatter `pedido: <pedido>` e `aceite: sim`), escrito à mão por ele (`R-DECISAO`): nenhum agente grava essa pasta (hook `conformidade`, `quem: []`), nem o `seguranca`. Sem o arquivo, o `forge-check pr` reprova; `aceite_usuario` no parecer não vale. O aceite fica no repositório, com o commit e o autor do usuário. Achado de segurança que bloqueia nunca segue aberto; o médio e o baixo seguem a regra do QA (`R-QA`).
- O parecer só vale gravado pelo papel `seguranca` (hook `conformidade`). O QA e o `tech-lead` não declaram "seguro".
- **Dependabot:** em branch `dependabot/*` que só toca travas e manifestos, basta o parecer de devops; o de segurança só é exigido quando as mensagens dos commits mostram versão maior (`from 1.x to 2.x`) ou não mostram versão nenhuma (falha fechada). Atualização que o diff não revela (dependência que muda de dono, pacote novo dentro de um grupo) segue por orientação ao devops: na dúvida, peça o parecer de segurança.
- O diff é lido com `--no-renames`: renomear um arquivo de gatilho não o esconde.
