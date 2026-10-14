---
name: engineering-practices
description: Boas práticas de desenvolvimento e modelagem do time (conforme a stack do projeto, banco relacional) - padrões de código, checklist de code review, modelagem e migrações, git e commits, pull request e proteção da main. Use ao escrever, revisar ou commitar código e ao modelar ou migrar banco.
---

# Boas práticas de engenharia

Mantidas pelo `tech-lead` e pelo `software-architect`. Ajustes específicos do projeto ficam em `docs/engineering/praticas.md` e prevalecem sobre este arquivo; decisões estruturais ficam em ADR.

## Código (conforme a stack do projeto)
- Linguagem, tipagem, lint e formatação seguem a stack declarada no `CLAUDE.md` (`${CLAUDE_PLUGIN_ROOT}/stacks/<stack>/pronto.md`); tipagem no modo mais estrito, sem escapes sem comentário explicando.
- Tipos e contratos compartilhados entre as camadas numa fonte única; nada de tipo duplicado à mão.
- Funções pequenas, com um propósito; nomes que dizem o que fazem; sem abreviação obscura.
- Regra de negócio isolada de framework (services puros, testáveis sem HTTP nem banco).
- Erros explícitos: nada de `catch` vazio; erro de domínio tipado; log com contexto.
- Sem código morto, sem depuração esquecida, sem TODO sem cartão no quadro.
- Dependência nova só com motivo: tamanho, manutenção ativa, licença; registrar no PR.
- Lint e formatação automáticos; o CI falha se não passar.

## Modelagem e banco (relacional; o banco do projeto é decidido em ADR)
- `snake_case`; tabelas no plural ou com prefixo de camada (`stg_`, `dim_`, `fato_`, `ref_`); chave primária `id` ou chave natural explícita.
- Motor, codificação de caracteres e tipo de data conforme a ADR do banco; datas em UTC.
- Toda chave estrangeira com índice; todo filtro de painel coberto por índice; `EXPLAIN` registrado para consultas principais.
- Idempotência por restrição única na chave natural da origem.
- Histórico nunca sobrescrito: eventos append-only ou versões (SCD2).
- **Migrações versionadas**, uma mudança por migração, sempre com caminho de volta; nunca editar migração já aplicada.
- Revisão de modelagem pelo tech lead e pelo arquiteto antes de escrever a migração.

## Testes
- Toda regra de cálculo com teste unitário e casos de borda documentados.
- Teste novo para todo bug corrigido (falha antes, passa depois).
- Testes determinísticos: sem dependência de hora atual nem de ordem de execução.

## Checklist de code review
Cada regra do `docs/engineering/praticas.md` do projeto diz quem a decide: "decidida por: `<comando>`" (ferramenta) ou "decidida por: leitura". O review **lê só as regras "leitura" que alcançam os arquivos do diff** e **cita a saída dos comandos das regras "ferramenta"**, sem refazê-las (regra 5 de `docs/economia-de-tokens.md`). Regra "ferramenta" sem comando configurado vira pendência no parecer, não revisão manual. O checklist abaixo vale para o que é de leitura.

1. Faz o que o cartão/especificação pede — nem mais, nem menos?
2. Segue a arquitetura e os ADRs? Respeita as regras invioláveis do `CLAUDE.md` e as regras da fábrica (`docs/regras/`)?
3. Legível sem explicação? Nomes, tamanho das funções, duplicação.
4. Tipos corretos, entradas validadas, erros tratados?
5. Segurança: segredos, injeção, autorização, dados pessoais.
6. Performance: consultas com índice, N+1, renderizações desnecessárias, tamanho do bundle — dentro do orçamento?
7. Testes cobrem o comportamento novo e os casos de borda?
8. Acessibilidade (front): semântica, foco, contraste.
9. Commits limpos e mensagem clara?

Parecer: **aprovado** ou **ajustes necessários** (arquivo:linha · problema · sugestão · severidade: bloqueia / recomendado).

## Git e commits
- Branches: `R-FLUXO` branches e promoção (prefixos `feature/`, `fix/`, `docs/`, `chore/`, `refactor/` + slug).
- Conventional Commits em português: `tipo(escopo): descrição no imperativo`. Tipos: feat, fix, docs, test, refactor, perf, chore, ci.
- Um commit por mudança coerente; o projeto compila e os testes passam em cada commit.
- Antes de commitar: `git status` e `git diff --staged`. Nunca versionar `.env`, segredos, dependências instaladas, builds, relatórios de teste.
- Para trazer a `main`: `git fetch` + `git merge origin/main` na sua branch (`R-MAIN`). `R-VERIFY` nunca `--no-verify` nem `--force`.

## Pull request e a main
- `R-MAIN` a main é do usuário (hook `pre-push` em `.githooks/` incluído).
- Descrição do PR: objetivo e link do pedido · o que mudou · decisões técnicas e ADRs · como testar · parecer do QA (link) · parecer de code review (link) · riscos e pendências.
