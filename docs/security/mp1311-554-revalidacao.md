---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.1
branch: melhoria/mp1311-554-revalidacao
commit: 6e837bf759ebc43e4f960d6cf348ef1e42e7d1d4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: release 0.47.1, delta 5b10ba81..6e837bf7 (E2.45)

branch: melhoria/mp1311-554-revalidacao · head revisado: 6e837bf759ebc43e4f960d6cf348ef1e42e7d1d4

Escopo: revalidação incremental do parecer `docs/security/release-0.47.1-b.md` (head 5b10ba81, aprovado). Este parecer cobre só o intervalo `5b10ba81..6e837bf7`; o resto da release segue coberto por aquele.

## Gatilhos
`R-SEGURANCA`: a release publica a versão usada por todos os projetos (hooks, CI, `bin/`, migração e modelo de projeto, conforme o parecer anterior). O delta em si não toca nenhum desses pontos.

## Achados

## Sondas

## Detalhe dos achados
Verificações estáticas e locais no clone da branch:
- `git diff --name-only 5b10ba81 6e837bf7 -- . ':!docs'`: 0 arquivos. O delta é só de pareceres: `docs/qa/mp1311-pre-envio-fabrica.md`, `docs/qa/release-0.47.1-b.md`, `docs/reviews/mp1311-pre-envio-fabrica.md`, `docs/reviews/release-0.47.1-b.md` e `docs/security/release-0.47.1-b.md`. Sem código, hook, workflow, migração nem modelo de projeto.
- O merge do PR 562 (c5c3a449, a develop) é ancestral do head; `git diff --name-only c5c3a449 6e837bf7 -- . ':!docs'`: 0 arquivos, então o código promovido é o mesmo revisado no parecer anterior.
- Nada grava em `docs/security/aceites/`; nenhum parecer do delta muda para `riscos-aceitos`.
- Commits posteriores ao head revisado (48f028e7, fbec6294) também só tocam `docs/` (pareceres de review e QA desta revalidação).
- Varredura do diff `5b10ba81..HEAD` por padrões de segredo (token de forja, chave de nuvem, chave privada, token de chat) e por caminho pessoal: só a menção textual já existente no parecer anterior, sem valor real.

Suíte inteira: roda no CI do PR da release; o delta não muda nada que ela exercite, e este parecer não substitui o CI verde do head promovido.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lacuna: `gitleaks`, `actionlint` e `zizmor` ausentes do PATH; substituídos pela leitura do diff e pela varredura por padrões.
