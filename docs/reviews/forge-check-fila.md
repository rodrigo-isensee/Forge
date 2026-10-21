---
tipo: review
contrato: 1
pedido: forge-check-fila
branch: melhoria/forge-check-fila
commit: fcaee1006ae30294353bc58e41d8dce9d381eea4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: FORGE-CHECK-FILA (P9), `forge-check fila`

Escopo: `3418377..31ae2cb`, 1 commit, 5 arquivos (`bin/forge-check`, `tests/test_sobreposicao_quadro.py`, `templates/projeto/docs/pedidos/_modelo.md`, `docs/hooks.md`, `changelog.d/forge-check-fila.md`). Quem revisa não é o autor. A referência é a seção "## P9" de `docs/propostas/aq/p8-p9.md` e os itens E1 e E2 do pedido.

Veredito sobre `31ae2cb`: **REPROVADO**, com 1 achado bloqueante. As recomendações estão no fim e não bloqueiam.

## Ferramentas (saída citada)
- `python3 -m unittest tests.test_sobreposicao_quadro`: `Ran 33 tests in 5.092s` / `OK`. Isso inclui T1 a T8, o teto de 15 linhas e o caso de só leitura da classe `Fila`.
- A suíte completa e o `scripts/validar-plugin.sh` ficam com o pre-push, o QA e o CI. Não os refiz aqui.
- O Forge não tem `docs/engineering/praticas.md`. Este review usa o checklist da skill `engineering-practices`.

## O que está conforme
- **Refatoração de `cmd_sobreposicao`.** `arquivos_por_branch` extrai o laço como estava. Sem base, devolve `(None, {})`, e `cmd_sobreposicao` imprime a mesma mensagem de antes. A saída por par e o resumo não mudam, e os testes de `sobreposicao` continuam verdes.
- **Algoritmo, conforme o desenho.** O comando percorre os candidatos de "Pronto para fazer" na ordem do quadro. Ciclo e dependência pendente saem como `espera`. Os demais recebem vaga até `teto - ativos`, e a carga alta (`agentes.carga_alta`, a mesma do hook) zera as vagas. A sobreposição só gera `aviso`. A saída tem no máximo 15 linhas e termina no resumo. Sem `KANBAN.md`, sai uma linha com rc 0, sem criar `docs/kanban/`.
- **Suposições do autor.**
  - A ligação cartão-pedido pela coluna Pedido aceita `p`, `docs/pedidos/p.md` e o caminho entre crases. Conferi no `KANBAN.md` real do Forge, que usa caminho.
  - A branch `melhoria/<ID>` é casada pelo último segmento do nome.
  - Exigir todos os cartões do pedido em "Pronto" é a leitura estrita de "o cartão do pedido citado está em Pronto". Para um comando que só recomenda, é o lado seguro.
  - `expiracao_horas` repete a validação de `Hook.config` (número > 0, padrão 2).
- **Linha do modelo.** O texto-modelo copiado como está vale como "nenhum". Conferi com uma sonda: o `_modelo.md` copiado dá `pode-comecar` sem aviso.
- **Só leitura e sem rede.** O comando só faz `git for-each-ref`, `rev-parse` e `diff` locais, lê `/proc` e lê arquivos. O teste compara a árvore de arquivos antes e depois. Importar `hooks/agentes` repete o padrão já usado em `teto_calculado`.
- **Documentação e changelog.** A linha em `docs/hooks.md` e o uso no cabeçalho de `bin/forge-check` descrevem o comando, e o fragmento `changelog.d/forge-check-fila.md` corresponde à branch.
- **Commit.** Um único commit coerente, em Conventional Commits em português. Não há rede, custo nem termo de projeto (R-CUSTO, R-NEUTRO).

## Achados
(vazio na volta 1: o A1 da rodada anterior foi resolvido, ver "Volta 1")

## Recomendações (não bloqueiam)
- `bin/forge-check:1436` (`cmd_fila`): quando o quadro não tem a coluna "Pronto para fazer" ou a coluna "Pronto", a saída diz só "0 podem começar". O `KANBAN.md` do próprio Forge está nesse caso: tem "A fazer" e "Concluído", e o resultado é `fila: 0 podem começar, 16 vagas de 16`. Um `aviso:` de coluna ausente evitaria a leitura de que a fila está vazia.
- `bin/forge-check:1461`: só a primeira dependência pendente é citada. Isso basta para dizer `espera`, mas listar todas poupa uma rodada a quem vai destravar.
- `bin/forge-check:1451`: `arquivos_por_branch` roda um diff por branch `melhoria/*` mesmo sem nenhum candidato com branch própria. Dá para pular quando nenhum pedido candidato tem branch.
- O hook respeita `FORGE_CARGA_LIVRE=1` e o `fila` não. Isso é coerente, porque o escape é só do dono, mas vale uma linha no cabeçalho do comando.

## Revalidação
Depois da volta, este parecer confere o delta (`forge-check delta --parecer docs/reviews/forge-check-fila.md`): `agentes_vigentes` e o teste novo de worktree.

## Volta 1
Delta lido: `dca6e71..fcaee10` (`git diff`, 3 arquivos: `bin/forge-check`, `docs/hooks.md`, `tests/test_sobreposicao_quadro.py`). Já lido na rodada anterior e não relido: o restante de `cmd_fila`, `arquivos_por_branch`, o modelo do pedido e o changelog.

Veredito sobre `fcaee10`: **APROVADO**, sem achado bloqueante.

- **A1 resolvido.** `agentes_vigentes` lê `agentes.json` por `raiz_principal(raiz)`, o mesmo auxiliar que `caminho_do_pedido` já usa. O teste novo monta um repositório com worktree, grava 2 agentes só na principal e confirma, rodando da worktree, `1 vagas de 3 (2 ativos)`. Falharia com a leitura antiga.
- **Aviso de coluna ausente** (recomendação da rodada anterior, acatada). Sai `aviso:` por coluna que falta, dentro do teto de 15 linhas; teste novo cobre as duas colunas e o resumo.
- **Suposição do autor aceita.** O `.forge/config.json` do teto segue lido da raiz onde o comando roda, como já faz `teto_calculado` (`bin/forge-check:256`, usado pelo `kanban`). Fica coerente com o resto do conferente. Na worktree sem esse arquivo o teto cai no adaptativo; vale, como recomendação, o dono saber disso se fixar `teto_agentes` só na principal.
- **Documentação.** `docs/hooks.md` e o cabeçalho de `bin/forge-check` descrevem a leitura pela principal e o novo aviso.
- **Ferramenta.** `python3 -m unittest tests.test_sobreposicao_quadro`: `Ran 35 tests` / `OK`.
- Recomendação nova, não bloqueia: a linha de uso no cabeçalho de `bin/forge-check` ficou longa; quebrar em duas melhora a leitura.
