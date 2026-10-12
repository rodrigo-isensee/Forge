---
name: cyber-security
description: Revisão de cibersegurança e boas práticas de um sistema Node/TypeScript + React + banco relacional + Docker + GitHub Actions - modelagem de ameaças, OWASP Top 10 e API Security Top 10, ASVS, cadeia de suprimentos, segredos, LGPD e endurecimento. Use ao revisar o projeto, uma mudança sensível (autenticação, webhook quando houver, banco, CI, Docker, dados pessoais) ou uma dependência nova.
---

# Cibersegurança e boas práticas

## Postura
- Revisão **defensiva e estática**: ler código, configuração, migrações, workflows e documentação. **Não** explorar vulnerabilidade, **não** varrer sistemas externos, **não** copiar nem exibir segredo encontrado (cite só arquivo:linha e o tipo).
- Falso positivo é custo. Para cada achado, mostre um caminho realista de ataque (quem, de onde, o quê ganha). Sem caminho, é recomendação, não vulnerabilidade.
- Cada correção proposta deve ser proporcional: não inflar a arquitetura. Prefira configuração e remoção a mais código.

## Método
1. **Ativos e fronteiras de confiança:** dados pessoais, credenciais (integrações externas), o banco, webhooks (quando houver), o CI, o navegador. Desenhe o fluxo (Mermaid) e as fronteiras.
2. **Ameaças (STRIDE)** por fronteira; priorize por probabilidade × impacto.
3. **Checklists por camada** (abaixo), com evidência `arquivo:linha`.
4. **Severidade:** crítica (exploração remota sem autenticação ou vazamento de dado pessoal/segredo), alta, média, baixa, informativa. Para cada achado: evidência, caminho de ataque, correção mínima, esforço (P/M/G), dono (agente).
5. **Saída:** `docs/security/revisao-de-seguranca.md` (resumo executivo, modelo de ameaças, achados, plano em cartões, riscos aceitos). Atualizar, não duplicar.

## Checklists
**API Node/Fastify:** validação de toda entrada com Zod (corpo, query, parâmetros, cabeçalhos) com `additionalProperties` negado; limites de corpo e de tempo; `@fastify/helmet`, CORS restritivo, rate limit nas rotas públicas e nos webhooks, quando houver; erros sem stack nem detalhes internos; autenticação de webhook, quando houver, por segredo com comparação em tempo constante e checagem **antes** de ler o corpo; sem `eval`/`child_process` com entrada externa; IDs não enumeráveis quando fizer sentido; autorização por rota e por recurso (OWASP API1/API5); logs com **redaction** de dados pessoais e segredos; desligamento limpo; respeito às regras invioláveis de dados do `CLAUDE.md` do projeto.
**Banco (exemplos em PostgreSQL; adapte ao banco do projeto):** papéis com privilégio mínimo (cada componente só com o acesso de que precisa, por exemplo leitura apenas onde só lê), `GRANT` por coluna para dados pessoais, `security_invoker` nas views, `search_path` fixo, consultas parametrizadas (nenhuma concatenação), transações e `SECURITY DEFINER` revisados, backups e dados de teste sem dado real.
**Front/React:** sem `dangerouslySetInnerHTML` com conteúdo não sanitizado; CSP; nada de segredo no bundle (`VITE_*` é público); armazenamento local sem dado sensível; links externos com `rel="noopener"`; geração de documentos (PDF etc.), quando houver, sem injeção; dependências do navegador mínimas.
**Docker/Compose:** imagens com versão fixa (idealmente digest), usuário não root, sistema de arquivos somente leitura quando possível, sem segredo na imagem nem no `Dockerfile`, portas expostas só em `127.0.0.1`, healthchecks, `.dockerignore`.
**GitHub Actions/CI:** `permissions:` mínimas por job, ações fixadas por SHA (ou revisadas via Dependabot), nenhuma `pull_request_target` com checkout de código de fork, segredos só onde necessário, cache sem envenenamento, proteção de branch e revisão obrigatória.
**Cadeia de suprimentos:** `pnpm audit`, lockfile versionado e `--frozen-lockfile`, Dependabot, `overrides` justificados, licenças permissivas, scripts de instalação (`onlyBuiltDependencies`), pacotes recém-publicados ou com um mantenedor só; plugins de terceiros no Claude Code (código que executa na máquina: licença, auditoria, auto-update).
**Segredos e configuração:** `.env` fora do git, `.env.example` sem valores reais, varredura de histórico por segredos, configuração validada na partida, rotação possível.
**LGPD:** base legal e minimização; dado pessoal só onde a regra de negócio exige; acesso restrito e registrado; retenção; direito de eliminação viável com tabelas append-only (documentar a estratégia).
**Regras invioláveis do projeto como requisito de segurança:** trate cada regra do `CLAUDE.md` do projeto (ex.: restrições sobre dados pessoais, segregação de fontes) como requisito a verificar; credenciais só em `.env`.

## Limites
Não altera código de produção: propõe o que mudar e o agente dono implementa; correção de segurança passa por code review e QA como qualquer outra. Dúvida de regra de negócio ou de risco aceito vai ao usuário, com insumos.
