# Migração 0.47.1, passo pre-envio

Para projetos criados antes de o modelo trazer o pré-envio (diretriz 23). Cria o modelo de PR `.github/pull_request_template.md`, com as seções que o review e o `forge-check pr` cobram, e o `.githooks/pre-push.local` com o pronto rápido da stack do `CLAUDE.md` (lint, formatação e tipos), que o pre-push roda antes de cada envio que muda código (só texto, parecer ou junção com a develop passa sem ele). Não sobrescreve o que o projeto já tem; stack desconhecida não ganha o `pre-push.local`; rodar de novo não muda nada.
