# Segurança — stack node-react

Checklists por camada que a skill `cyber-security` manda aplicar quando o projeto declara a stack `node-react`. Mesma evidência (`arquivo:linha`) e mesma severidade da skill.

## API Node/Fastify
Validação de toda entrada com Zod (corpo, query, parâmetros, cabeçalhos) com `additionalProperties` negado; limites de corpo e de tempo; `@fastify/helmet`, CORS restritivo, rate limit nas rotas públicas e nos webhooks, quando houver; erros sem stack nem detalhes internos; autenticação de webhook, quando houver, por segredo com comparação em tempo constante e checagem **antes** de ler o corpo; sem `eval`/`child_process` com entrada externa; IDs não enumeráveis quando fizer sentido; autorização por rota e por recurso (OWASP API1/API5); logs com **redaction** de dados pessoais e segredos; desligamento limpo; respeito às regras invioláveis de dados do `CLAUDE.md` do projeto.

## Banco (exemplos em PostgreSQL; adapte ao banco do projeto)
Papéis com privilégio mínimo (cada componente só com o acesso de que precisa, por exemplo leitura apenas onde só lê), `GRANT` por coluna para dados pessoais, `security_invoker` nas views, `search_path` fixo, consultas parametrizadas (nenhuma concatenação), transações e `SECURITY DEFINER` revisados, backups e dados de teste sem dado real.

## Front/React
Sem `dangerouslySetInnerHTML` com conteúdo não sanitizado; CSP; nada de segredo no bundle (`VITE_*` é público); armazenamento local sem dado sensível; links externos com `rel="noopener"`; geração de documentos (PDF etc.), quando houver, sem injeção; dependências do navegador mínimas.

## Cadeia de suprimentos (pnpm)
`pnpm audit`, lockfile versionado e `--frozen-lockfile`, Dependabot, `overrides` justificados, licenças permissivas, scripts de instalação (`onlyBuiltDependencies`), pacotes recém-publicados ou com um mantenedor só.
