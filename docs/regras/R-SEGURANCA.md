---
id: R-SEGURANCA
titulo: Parecer de segurança quando há gatilho
verificada_por: revisão e hook `parecer` (parecer em docs/security/ exigido no PR e no merge na integração, nos gatilhos que o diff mostra ou que o plano técnico marca)
---
# R-SEGURANCA: Parecer de segurança quando há gatilho

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-14.

- Entrega que toca um **gatilho** tem parecer do `security-engineer` em `docs/security/<pedido>.md` (frontmatter da ADR 0004: `tipo: revisao-seguranca`, `parecer: aprovado|reprovado|riscos-aceitos`), em paralelo ao code review (`R-REVIEW`) e antes do QA. Sem gatilho, o plano técnico diz "sem gatilho de segurança" e nada é exigido.
- Gatilhos: autenticação ou autorização; dados pessoais (LGPD); segredos e configuração (`.env*`, variáveis do CI, credenciais); dependência nova ou versão maior; webhook ou endpoint externo; banco (migração, permissão, consulta com entrada); CI/CD (`.github/`); Docker, Compose e IaC; controles do Forge (`hooks/conformidade.json`, `docs/regras/`, `tests/catraca.py`, `tests/config.json`).
- O hook e o `forge-check pr` detectam pelo diff os casos óbvios: arquivo de travas de dependência, `.env*`, pipeline, contêiner e IaC, migração e controles do Forge. Os demais gatilhos o pedido marca em `gatilhos_seguranca` do plano técnico; quem desenha, o `software-architect` com o `security-engineer`, os declara.
- `riscos-aceitos` só vale com `aceite_usuario: sim` no parecer, gravado pelo usuário (`R-DECISAO`). Achado de segurança que bloqueia nunca segue aberto; o médio e o baixo seguem a regra do QA (`R-QA`).
- O parecer só vale gravado pelo papel `seguranca` (hook `conformidade`). O QA e o `tech-lead` não declaram "seguro".
