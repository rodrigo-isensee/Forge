---
tipo: review
contrato: 1
pedido: pre-push-ff
branch: melhoria/pre-push-ff
commit: 2910e1e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review: pre-push recusa envio não fast-forward (ADR 0009, R-VERIFY)

Escopo: `.githooks/pre-push`, `templates/projeto/.githooks/pre-push`, `tests/test_forge.py` (classe `HookPrePush`) e `CHANGELOG.md`, diff `origin/develop..2910e1e`.

## Resultado dos casos
Executados em repositório temporário (bare + cópia de trabalho, hook do modelo, removido ao fim) e nos 6 testes de `HookPrePush` (verdes).

| Caso | Resultado |
|---|---|
| Fast-forward em branch existente | passa |
| Amend + `--force` | recusado (R-VERIFY) |
| `+refspec` | recusado (R-VERIFY) |
| Branch nova (remote_sha zerado) | passa |
| Apagar branch (local_sha zerado) | passa |
| Tag nova, tag leve ou anotada, apagar tag | passa |
| Mover tag para fora do histórico (`-f`) | recusado, com mensagem de "branch/rebase" |
| Remoto com commit que o local não tem (sem fetch) | recusado (fecha por segurança), com mensagem enganosa |

## Achados
### Recomendado
- `.githooks/pre-push:9` e `templates/projeto/.githooks/pre-push:9`: quando `$remote_sha` não existe no clone, `merge-base --is-ancestor` falha (código 128) e o `2>/dev/null` o trata como "reescrito". O comportamento (recusar quando não dá para verificar) é seguro e sem erro de objeto desconhecido, mas a mensagem manda fazer rebase, quando o correto é `git fetch`. Sugestão: antes, `git cat-file -e "${remote_sha}^{commit}" 2>/dev/null || { echo "...não foi possível verificar: rode git fetch e tente de novo" >&2; exit 1; }`, e documentar no cabeçalho que o objeto ausente é recusado de propósito. Não bloqueia.
- Mesma mensagem para `refs/tags/*`: fala em "branch" e "rebase". Ou restringir a checagem a `refs/heads/*`, ou texto neutro ("referência"). Recomendado escolher conscientemente se mover tag é tratado como reescrita (hoje é recusado, o que é coerente com a regra).
- Sem teste para o remoto desconhecido nem para apagar branch/tag; o primeiro fixa a decisão segura acima.

### Observações (sem ação)
- Desempenho: um `merge-base --is-ancestor` por ref enviada, sem varredura; custo desprezível, e roda antes dos testes pesados do hook da fábrica.
- Compatibilidade: a checagem fica antes do `pre-push.local` do modelo, que continua rodando só quando o envio é aceito; o bloqueio da `main` no modelo (e de develop/homolog na fábrica) segue intacto e agora também vale em ordem (não fast-forward é recusado primeiro). Projetos que já usavam `--force-with-lease` em branch própria passam a ser barrados: está documentado no CHANGELOG, é a intenção do pedido.
- Duplicação do bloco entre os dois hooks é aceitável (o modelo é copiado para os projetos e não pode depender da fábrica).

## Parecer
Aprovado. Os ajustes recomendados podem entrar neste PR ou em seguida; nenhum bloqueia.
