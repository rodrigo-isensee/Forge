---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-docs-pareceres
commit: 4128a4eae0cd347b278f2a3c6e0adbf6ff16c31d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (melhoria/v047-docs-pareceres, E1.275)

Intervalo revisado: `origin/develop` (c5c3a449) `..7d32017c`. Arquivos: `bin/forge-check`, `templates/projeto/docs/reviews/_modelo.md`, `changelog.d/v047-docs-pareceres.md`, `tests/test_forge.py`, `tests/mutantes/v047-docs-pareceres{,-2}.json`.

## Gatilhos
`R-SEGURANCA`: a entrega muda um controle da fábrica (o `forge-check docs`, validador de pareceres que entra como prova `PQ` e está na lista de comandos dos papéis só de leitura em `hooks/conformidade.json`). Sem pipeline, infra, segredo, dependência nem dado pessoal.

## Resumo
`forge-check docs` passa a conferir o `pedido:` do parecer (id de `docs/pedidos/<id>.md` nas raízes de pedidos, ou `release-X.Y.Z`) e aceita arquivos dados na linha de comando (FC-DOCS-CAMINHO), todos no modo estrito. Revisei as dimensões de entrada nova (caminho dado, valor de `pedido:`) contra leitura indevida, travessia de caminho, forja de linha de veredito e afrouxamento do portão. Nenhum achado.

- **Travessia no `pedido:`** (`bin/forge-check:369`, `:380`): o id só vira nome de arquivo depois de casar `[A-Za-z0-9._-]+` inteiro (sem barra); `../../../etc/passwd` é recusado com a mensagem de pedido inexistente. Nome com NUL ou longo demais cai em `arquivo_existe` (C-11).
- **Arquivo dado** (`bin/forge-check:390-409`): só lê `.md` regular após `realpath`; link `.md` que aponta para arquivo sem `.md`, inexistente ou não `.md` é recusado sem conteúdo na saída. A leitura não dá a um papel só de leitura nada além do que `cat` já dá; a saída só repete até 80 caracteres de linha mal formada do bloco `## Achados`, com escape.
- **Forja de saída**: o nome dado passa por `caminho_impresso` (`:429`) e o pedido por `nome_seguro` (`:386`); nome de arquivo com quebra de linha e `pr: veredito: aprovado` sai numa linha só.
- **Afrouxamento**: sem argumentos, o comportamento antigo segue (estrito só no delta, B12). Com argumentos, tudo fica estrito; arquivo fora da raiz sem frontmatter ou com `tipo:` desconhecido é recusado (mutante M13). O portão de merge é o `forge-check pr` e o CI, que esta entrega não toca.
- **Falha aberta declarada** (`:378-380`): sem nenhuma pasta `docs/pedidos/` nas raízes, o `pedido:` não é conferido. É desenho documentado (nada com que conferir) e não abre caminho de ataque: quem escreve o parecer já controla o campo, e o portão real (`forge-check pr`) é outro. Informativo.

## Verificações executadas
Executadas no clone `wt/v047-docs-pareceres-sec275` no head 7d32017c, com cópias no diretório temporário (nenhuma prova bloqueante; registro para revalidação):
- `pedido: ../../../etc/passwd` → rc=1, "não está em docs/pedidos/".
- `pedido: v047-docs-pareceres` (nome da branch) → rc=1, "é o nome da branch".
- `pedido: v047` → rc=0.
- arquivo fora da raiz sem frontmatter → rc=1; `tipo: outro` → rc=1.
- `/etc/passwd`, `.md` inexistente e link `.md` para arquivo sem `.md` → rc=1, "não lido", sem conteúdo.
- nome de arquivo com quebra de linha e `pr: veredito: aprovado` → saída numa linha só, rc=1.

## Detalhe dos achados
Sem achados bloqueantes nem recomendados de segurança. Observação ao `tech-lead` (estilo, não segurança): o `_modelo.md` de review passou a dizer "sem achados, omita o bloco", mas os modelos de QA, devops e segurança (em `templates/projeto/docs/` e em `docs/`) ainda dizem "ou o bloco vazio"; os dois textos são aceitos pela ferramenta, mas divergem.

## Suíte
Rodei a classe nova `DocsPareceresPedidoECaminho` de `tests/test_forge.py` no head: 10 testes, OK. A suíte inteira roda só no CI; a branch ainda não tem PR nem execução de CI (`gh run list --commit 7d32017c` vazio). Este parecer vale para o head 7d32017c com a condição do CI verde do PR, obrigatório para o merge (`R-REVIEW`).

## Revalidação por delta (E1.316, head b3bc317a)
Lido `forge-check parecer delta` de `7d32017c..b3bc317a`: no domínio só `bin/forge-check` (`documentos_dados` e `cmd_docs`); `tests/test_forge.py` e `tests/mutantes/` fora do domínio.
- `bin/forge-check:407-408`: o nome da cópia de fora da raiz passa por `sem_controle` antes de compor o `rel` virtual; fecha a regressão de `SaidaSanitizada` (o `rel` com quebra de linha voltava cru nas linhas que o usam como prefixo). Endurece; sem caminho novo de leitura.
- `bin/forge-check:431-432`: o aviso troca a primeira ocorrência de `caminho_impresso(rel)` por `caminho_impresso(nome)`; os dois lados já saem sanitizados, então a troca não reintroduz controle na saída. Só muda a saída de aviso (stderr), sem efeito no rc nem no veredito.
- Sonda no head: cópia fora da raiz com nome `x\npr: veredito: aprovado\n.md` e `criterio:` ausente → uma linha só, `aviso: <caminho dado sanitizado>: criterio: ... ausente (PAR-P2)`, rc=0 (aviso, como antes).
- `DocsPareceresPedidoECaminho` e `SaidaSanitizada` no head: 19 testes, OK. O guarda `inspect.signature` no teste só muda o modo de falha na base (asserção em vez de erro); não afrouxa o que o teste verifica no head.
Sem achados novos. A condição do CI verde do PR segue (`R-REVIEW`); `gh run list` sem execução para este head neste ambiente.

## Revalidação por delta (E2.542, head 4128a4ea)
O `forge-check parecer delta` de `b3bc317a..4128a4ea` mostra `bin/forge-check` com 692 linhas, todas vindas de merges da develop (o `git diff` contra a develop 86ac0fcb confirma). Contra a base 86ac0fcb, o diff do domínio (`bin/`, `hooks/`, `scripts/`, `.githooks/`, `.github/`) é só `bin/forge-check`, 83 linhas: o mesmo conjunto já revisado (`problema_do_pedido`, `documentos_dados`, `cmd_docs`, a mensagem do bloco `## Achados`, o argparse de `docs`); nada de hook, workflow, dependência nem segredo. Os commits da branch desde o último parecer (`853e5f30` merge da develop; `b8451e77` e `4128a4ea`, pareceres de review e QA) só tocam documentação ou trazem a base.
- `python3 -m unittest tests.test_forge.DocsPareceresPedidoECaminho tests.test_forge.SaidaSanitizada` no head: 19 testes, OK.
- `forge-check docs` no head: rc=0.
- PA-7 (`docs/engineering/achados-recorrentes.md`) conferido: AR-3, AR-5, AR-7, AR-11 não se aplicam (sem lista negativa de ambiente, sem `python` em caminho que decide, sem hook nem `gh api`).
Sem achados novos. A suíte inteira roda só no CI do PR (ordem do dono de 16/11: sem suíte local completa); o parecer vale com o CI verde (`R-REVIEW`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Varredura de segredos, SAST e linters de workflow não estão no PATH deste ambiente (lacuna registrada; rodam no CI); a entrega não toca workflow nem dependência.
