---
tipo: review
contrato: 1
pedido: vv-2
branch: melhoria/vv-2
commit: 6396f2da9d1344b665ed829634fc84d3670e0499
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-19
---
# Code review: VV-2 (volta por delta)

Rodada 2 (E2.1, revalidação só do delta da volta 1): `29fea96..6396f2d`, 6 commits, 13 arquivos, 121+/11-. A rodada 1 (`7226ba7...e925152`, reprovada por A1 e A2) fica resumida no fim; o que ela aprovou fora do delta não foi relido. Revisor diferente do autor da volta (D-ETAPAS-INST).

Ferramentas rodadas nesta rodada, em 6396f2d: `python3 -m unittest tests.test_volta_por_delta tests.test_hooks tests.test_testes_tocados` → `Ran 98 tests ... OK` (rc 0); `forge-check docs` → rc 0; `git merge-tree --write-tree origin/develop HEAD` (develop em 092af03, não contida na branch) → rc 0, merge limpo. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO; o QA os refaz no head; `forge-testes --base 29fea96 --listar` pede a suíte completa porque o delta toca `bin/forge-testes`). Segurança (S-A1 a S-A5): parecer próprio do `security-engineer`, não refeito aqui; só confiro que o código da S-A1 não quebra o que eu aprovei.

## Achados da rodada 1, fechamento
| Achado | Estado | Reprodução nesta rodada | rc novo |
|---|---|---|---|
| R-A1 (bloqueante) modelos de parecer sem o bloco no formato | fechado | R1 com uma linha `A1 (bloqueante) x.py:1 · teste` inserida no `## Achados` de `templates/projeto/docs/{security,reviews,qa}/_modelo.md` e `docs/security/_modelo.md` → `problemas_do_bloco` devolve `[]` nos quatro; `python3 -m unittest tests.test_volta_por_delta.BriefDeVolta.test_parecer_escrito_pelo_modelo_passa_no_gerar_volta` | 0 |
| R-A2 (bloqueante) `brief --anterior` fora de `~/.forge-contrib` | fechado | R2 (`forge-check brief ~/.forge-contrib/docs/briefs/vv-2-tech-lead-2.md ... --anterior ~/.forge-contrib/docs/briefs/vv-2-tech-lead-1.md`) → `resultado: aprovado`; `...BriefAnterior.test_anterior_na_raiz_de_brief_do_forge` (inclui o caso fora de `docs/briefs/`, que segue rc 2) | 0 (antes 2) |
| R-A3 (recomendado) `-z` em `arquivos_da_entrega` sem teste nem changelog | fechado | `...Entrega.test_nome_acentuado_chega_sem_aspas_e_o_fragmento_do_changelog_conta` (`docs/decisões.md` sem aspas, com e sem `--desde`); linha nova em `changelog.d/vv-2.md` | 0 |
| R-A4 (recomendado) `Volta-de:` sem `--ref` sem tratamento | fechado | `agents/conferente.md:25`: "é `não verificável` no veredito, peça a ref"; `...TextoDosAgentes.test_desde_vem_da_mensagem_do_jarvis_e_o_texto_do_hook_e_exato` | 0 |

Sobre o "tratar o formato antigo" de R-A1: não foi feito e não bloqueia. Os pareceres antigos (`docs/security/aq.md` e afins, de pedidos fechados) seguem fora do formato (R1 neles ainda lista as linhas de tabela), mas o `forge-check docs` passa (rc 0) e o `gerar --volta` só lê pareceres do pedido em curso na ref; num parecer antigo ele recusa com rc 2 (falha fechada, nada some em silêncio). Com os modelos corrigidos, todo parecer novo nasce no formato.

## Suposições do autor (volta 1)
1. Modelos de devops fora: aceita. `docs/devops/_modelo.md` e `templates/projeto/docs/devops/_modelo.md` não têm `## Achados` (`grep -n Achados` vazio), então não há colisão, e o `gerar --volta` não lê `docs/devops/`.
2. `--destino-arquivo` por nome inteiro: aceita. `FORGE_CHECK_GRAVA_EXATA` compara `a.split("=", 1)[0]`, então `--destino` (opção real do `brief`) volta a passar e `--destino-arquivo` e `--destino-arquivo=x` são barrados; fixtures `conferente-brief-destino-libera.json` e `...-arquivo-bloqueia.json`, rc 0 na `tests.test_hooks`. Risco residual baixo: quando a opção existir, a abreviação do argparse (`--destino-a`) também a alcançaria; o comentário em `hooks/conformidade.py:128` já diz que o nome que gravar nasce na lista por prefixo, e aí ele sai da lista exata.
3. Não existem `docs/reviews/_modelo.md` nem `docs/qa/_modelo.md` no Forge: aceita (`ls` → "No such file or directory" nos dois); só `docs/security/_modelo.md` existe na raiz, e foi corrigido igual ao do modelo de projeto.

## Delta lido
- `bin/forge-check:2680`: `--anterior` pelo `caminho_de_brief`, a mesma função do `--volta`; correto e mínimo. A E5 (`pq_de_merge`, 79d42f9) não é tocada pelo delta (o único trecho alterado de `bin/forge-check` é a linha 2680).
- `bin/forge-testes`: as duas entradas novas vêm antes de `(migrations|templates)/.*` e de `(agents|skills|docs)/.*`, e o mapa usa a primeira que casa: os modelos ganham `test_volta_por_delta` sem perder o `PUBLICADO`/`CONTEUDO`. Correto (DECISÃO TÉCNICA do Jarvis no pedido).
- Modelos: o bloco `## Achados` fica vazio no modelo, com a regra de formato no texto de instrução e a prosa movida para `## Detalhe dos achados` (segurança) e `## Parecer` (review); o QA ganha o bloco. O teste fixa um único cabeçalho `## Achados` por modelo.
- `agents/conferente.md` e `agents/jarvis.md` (`Desde:` da mensagem, conferido contra o Histórico; texto do hook exato): coerentes com o código e cobertos por teste de texto. São S-A2 e S-A5, do `security-engineer`.
- Commits: um por achado, Conventional Commits em português, cada um citando o achado que fecha. Sem achado novo no delta.

## Achados

## Parecer
**Aprovado.** Os dois bloqueantes e os dois recomendados da rodada 1 estão fechados, cada um com teste que falharia sem a correção; o delta não toca a E5, não afrouxa nenhum portão (a S-A1 só deixa de barrar a opção legítima `--destino`, e a futura `--destino-arquivo` continua barrada) e não traz achado novo.
Para a E2.4: a develop andou para 092af03 e o merge é limpo (`merge-tree` rc 0); trazê-la uma vez antes do QA, conforme R-FLUXO.

Rodada 1 (e925152, reprovado): A1 modelos de parecer em colisão com o `## Achados` de máquina; A2 `brief --anterior` só na raiz; A3 `-z` sem teste; A4 `Volta-de:` sem `--ref`. Texto completo no histórico deste arquivo (`git show 25970f2:docs/reviews/vv-2.md`).
