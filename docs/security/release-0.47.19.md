---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.19
branch: melhoria/v0481-release-04719-anexo-2
commit: 17395e4d905fdbf24bbe21451050873b77261ba6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: release 0.47.19 (versão inteira, 19 itens), renovada no segundo anexo 17395e4d

Etapa E12.43 do pedido v0481. Esta rodada renova o parecer para o head do #911. A rodada E12.34 (aprovada em `0157977e`, com 18 itens) fica no git.

Delta lido desde ela, fora dos pareceres:
- o #908 (squash `d1ffc325`, mesclado pela conta do dono às 10:24): `scripts/indice-fixtures.py`, `docs/hooks-fixtures.md`, `tests/test_indice_fixtures.py` e `tests/mutantes/v0481-fixtures-gerada.json`;
- o segundo anexo (`17395e4d`): `CHANGELOG.md`, 2 linhas novas e 1 trocada, e o fragmento do #908 apagado.

A versão fica assim:
- os **10 itens da marca** (#874, #877, #885, #886, #890, #892, #895, #896, #897, #898);
- os **9 itens dos anexos** (#875, #901, #903, #904, entre o corte `cc4376fe` e a squash da marca `020e4af7`; #878, #902, #888, #906, #908, depois dela);
- a **marca** (`020e4af7`, #905), o **1º anexo** (`53e879cf`, #907) e o **2º anexo** (#911, `docs/security/v0481-release-04719-anexo-2.md`), todos só metadado de versão.

Gatilhos: hooks (`hooks/salvar.py` novo, fora do sandbox; `hooks/conformidade.py`, `hooks/_comum.py`, `hooks/conformidade.json`, `hooks/hooks.json`), controles do Forge (`bin/forge-check`, `bin/forge-fechar`, `bin/forge_autorizacao.py`, `bin/forge_pareceres.py`, `bin/forge_pronto.py`, `tests/catraca.py`, `scripts/indice-fixtures.py` na bateria), regras com ID e ADRs (`docs/regras/R-FLUXO.md`, `docs/regras/R-QA.md`, ADR 0003, ADR 0018), release usada por todos os projetos.

## Junção: cada item com o parecer próprio
**10 itens da marca** (rodada anterior, sem mudança):
- Para cada um, `git merge-tree --write-tree <pai da squash> <head do PR>` dá a mesma árvore da squash nos caminhos de código.
- Segurança, review e QA estão `aprovado`, e o `commit:` de cada parecer é ancestral do head.
- Exceções, só de teste e cobertas pelo review e pelo QA: #886 (`dba51ddf`, M3 realinhado) e #892 (`2259b235`, teste e M5).
- Ficou com o QA: o #896 entrou sem `docs/qa/v0481-copia-base-fechada.md` na develop.

**9 itens dos anexos.** Os 8 do 1º anexo vêm da rodada anterior, sem mudança; o #908 é desta rodada. Busquei `refs/pull/<n>/head` para `FETCH_HEAD`, sem ref nova, e conferi três pontos:
- a árvore do merge do pai da squash com o head do PR é igual à squash nos caminhos de código (`bin`, `hooks`, `scripts`, `.githooks`, `.github`, `tests`, `agents`, `skills`, `docs/regras`, `docs/adr`, `templates`, `patches`, `stacks`, `dev`, `.claude-plugin`): 0 arquivos de diferença nos 9;
- o `commit:` do parecer de segurança de cada item é ancestral do head;
- a contribuição de código no `commit:` do parecer, refeita sobre o mesmo pai, é igual à squash: 0 arquivos de diferença nos 9.

| PR | head | squash | parecer de segurança (`commit:`) |
|---|---|---|---|
| #875 | `32806f3b` | `d4b2747e` | `v0481-ae2-quadro-anda` (`59add013`) |
| #901 | `1a81a31d` | `6af477fc` | `v0481-autorizacoes-fixas` (`39b5b066`) |
| #903 | `6231abb7` | `02a94e31` | `v0481-d2-no-brief` (`6c2bbf42`) |
| #904 | `75e6a1cd` | `f23ebba8` | `v0481-entrega-desde-revisar` (`3b5fde5f`) |
| #878 | `7839d20c` | `22ceb2c8` | `v0481-g2-1-publicar` (`f3258bb8`) |
| #902 | `be41a1e8` | `604f3069` | `v0481-voltas-alinhada` (`6c709157`) |
| #888 | `1d085aaa` | `cfd83b72` | `v0481-prazo-forge` (`07a1bf5c`) |
| #906 | `e3f7ba5c` | `8ae4d6c6` | `v0481-rotulo-base-alheia` (`5c21b249`) |
| #908 | `90b57d7d` | `d1ffc325` | `v0481-fixtures-gerada` (`de272439`) |

Os 9 pareceres estão `aprovado`, com `pedido: v0481`. No #908, o pai da squash é `8ae4d6c6` (o #906), e não a base do PR (`cfd83b72`). A junção com esse pai dá 0 arquivos de diferença também no repositório inteiro. De `de272439` a `90b57d7d`, os commits só tocam os três pareceres do #908, e review e QA do #908 estão `aprovado` no mesmo `de272439`.

## Marca, anexo e versão
- **Marca:** `cc4376fe..9487d956` toca só os dois `plugin.json`, o `CHANGELOG.md` e os 10 fragmentos apagados, e é idêntica à saída de `forge-changelog release 0.47.19 2026-11-26`.
- **Anexos:**
  - o 1º anexo acrescentou 15 linhas à seção `[0.47.19]`: as 14 dos 8 fragmentos apagados, idênticas, e a linha do anexo;
  - o 2º anexo (`53e879cf..17395e4d`) acrescenta a linha do #908 (`CHANGELOG.md:26`), idêntica ao fragmento apagado, e troca a linha do anexo (`CHANGELOG.md:24`), que agora diz "os 9 itens" e cita o #908 e o E12.40;
  - nenhuma linha da marca sai.
- **Texto, sem efeito de segurança:**
  - a linha do #877 ainda diz "à espera do dono", embora o dono já tenha aprovado.
- **Versão:** `0.47.19` em `.claude-plugin/plugin.json:3` e em `dev/.claude-plugin/plugin.json:3`, igual a `CHANGELOG.md:7`. A `origin/main` está em `0.47.18` (`52dc3dcd`). `bin/forge-changelog conferir-release` dá `ok`, e `tests.test_changelog` com `tests.test_indice_fixtures` roda 101 testes, OK.
- **Segredos:** nas linhas acrescentadas, a única ocorrência dos padrões de token e chave é o texto de fixture da rodada anterior (`ghp_` seguido de `A`s), sem segredo real. Os dois anexos dão 0.

## Superfície protegida de v0.47.18 a 17395e4d
- **Arquivos tocados:**
  - `agents/jarvis.md` (#902);
  - `docs/adr/0003` (#877) e `docs/adr/0018` (#901);
  - `docs/regras/R-FLUXO.md` (#903) e `docs/regras/R-QA.md` (#902);
  - `hooks/_comum.py`, `hooks/conformidade.json`, `hooks/conformidade.py`, `hooks/hooks.json` e `hooks/salvar.py`;
  - `scripts/indice-fixtures.py` (#908);
  - `tests/catraca.py`.
- **Fora do diff:** nada em `.github/`, `.devcontainer/`, `.githooks/`, `docs/security/aceites/`, `templates/` ou `stacks/`. `tests/config.json` também não está no diff, então nenhuma invariante sai.
- **Medida dos hooks:** `bin/forge-check comparar v0.47.18 17395e4d` dá `so-aperta: medido base=52dc3dcd... head=17395e4d... casos=239 aceites-novos=0` (famílias merge-pr, push-forcado e sem-verificar, com 8 casos cada). A medida cobre só a decisão dos hooks que recusam.

## O que aperta, o neutro e o que afrouxa (para o rótulo afrouxa-regra da promoção)
Nos controles que recusam, a versão só aperta ou é neutra frente à 0.47.18: a medida dá `so-aperta`, e nenhum item faz passar uma entrada que antes era recusada. Na norma, porém, a versão **não é só aperta**. Onze dos 19 itens afrouxam regra escrita ou teste e entram por decisão do dono, não por esta confirmação.

**Aperta:**
- **#885 e #886:** o texto da recusa e o `diretorio_comum` leem `.forge/perfil`, `.git`, `gitdir` e `commondir` sem esperar FIFO e só se forem arquivo regular. Antes, um FIFO liberava push na main e `--force` pelo prazo.
- **#888:** na sessão do Forge, o prazo vencido recusa a linha com ação crítica (push na main, `--force`, `--no-verify`, caminho de controle). O `gh pr merge` tem prazo de 7,5 s, contado da partida do processo. `mkfifo` e `mknod` no `.git` são recusados.
- **#878:** na sessão de projeto, o hook barra `forge-check parecer publicar` com alvo no Forge (`R-CONTRIB`). Entram quatro regras de dono para `.forge/pareceres/*/`, e `bin/forge_pareceres.py` passa a estar em `PROTEGIDOS`.
- **#903:** a entrega com o D2 vermelho volta. O D2 roda com o `forge-check` de um clone da develop, e não com o da branch.
- **#904:** o Desde exige que o conjunto de portões selados seja igual ao conjunto de pareceres do head. Qualquer veredito trocado faz voltar ao Desde de sempre, incluindo parecer apagado, `_*.md` ou `contrato: 0`.
- **#902:** a saída da volta é sanitizada. A entrega recusa teste removido ou enfraquecido no diff da volta, e da 3ª volta em diante só se corrige o que o portão apontou.
- **#906:** um teste por `ast` prende a igualdade entre as listas `ACEITES` da catraca e do `forge-check` (mutante RB3).
- **#875:** o quadro não move mais o cabeçalho nem o separador, e um UTF-8 inválido não reescreve o quadro.
- **#898:** o `--dry-run` sem `origin/<branch>` sai com código 1.
- **#874:** o aviso de tamanho sai a 80%, e o arquivo não segue link.
- **#908:** o índice versionado deixa de carregar descrições e listas de regras e cartões das fixtures, então há menos texto livre no núcleo (`R-NEUTRO`). O teste novo da junção roda o `git` isolado da configuração da estação. `--detalhe --conferir` juntos são recusados com rc 2 (mutante M1 morto, `scripts/indice-fixtures.py:119`).

**Neutro:**
- #885: `modo_por_grupo` com todos os grupos em `barrar`, falhando fechado;
- #897: só mensagem;
- #892: só a linha `docs: ok`;
- #896: só a linha do sha;
- #908: o `--detalhe` só lê e imprime;
- #875 (o movimento do cartão), a marca e os dois anexos, que são só metadado.

**Afrouxa, com o aceite do dono:**

| Item | O que afrouxa | Aceite do dono | Rótulo `afrouxa-regra` posto pela conta do dono (UTC) |
|---|---|---|---|
| #877 | hook `salvar` fora do sandbox, commit WIP local sem os hooks do git (exceção ao `R-VERIFY`, emenda da ADR 0003) | DECISÃO 25/11 07:37 e 17:37 | autorização gravada de 25/11 21:39 ("autorizo rotulo afrouxa regra pr 877, pr 888") |
| #895 | forma `via` da linha do CI no parecer | DECISÃO 25/11 07:27 | já com rótulo na marca |
| #901 | atos fixos `corte-diario` e `so-aperta-com-seguranca`, sem prazo; corte abaixo do teto do contador (emenda da ADR 0018) | ORDEM 25/11 07:52 e DECISÃO 26/11 09:45 (só aperta, permanente; o rótulo do que afrouxa continua do dono) | 26/11 10:38 |
| #903 | `R-FLUXO`: a exceção "base velha" para trazer a integração antes do merge | ORDEM 25/11 07:52 (D2 obrigatório, de que a exceção decorre) | 26/11 10:38 |
| #904 | o Desde da entrega parte do `commit:` aprovado (`conferida..revisado` não é relido) | opção A, DECISÃO 25/11 21:15 | 26/11 10:38 |
| #902 | `R-QA`: voltas sem teto e sem o dono | ORDEM 25/11 07:31 e DECISÃO 25/11 17:07 | 26/11 11:27 e 11:29 |
| #888 | margem do prazo das travas de recurso | DECISÃO 25/11 21:15 | 26/11 00:25 e 10:38; autorização gravada de 25/11 21:39 |
| #906 | o rótulo `afrouxa-regra` continua valendo depois de trazer a base sem mudar o diff, e o parecer de segurança da branch sai da comparação (`aceites/` continua dentro) | decisão do dono de 24/11, repetida na DECISÃO 26/11 07:50 | 26/11 12:47 |
| #875 | rótulo só por tocar `bin/forge-check` (a segurança disse que só aperta) | DECISÃO 25/11 21:52 | 26/11 00:29 e 10:38 |
| #878 | rótulo por tocar controles (`bin/forge-check`, `hooks/conformidade.py`, `PROTEGIDOS`); só acrescenta | DECISÃO 25/11 21:52 | 26/11 00:25, 10:38 e 11:26 |
| #908 | o teste `test_conta_todo_caso_do_corpus` é renomeado e perde a asserção do total de fixtures (é por isso que a catraca pede o rótulo); o índice não confere mais a contagem, que é documentação e não controle; o corpus segue rodando inteiro em `tests/test_hooks.py` | DECISÃO 26/11 08:44 (tabela gerada, sem edição à mão) e 09:45 (fila) | 26/11 12:47 |

O dono mesclou os 9 itens dos anexos na develop em 26/11, entre 07:50 e 10:24 locais (`mergedBy` conferido pela API). No #908, o rótulo é de 09:47 locais, antes dos três pareceres. Os envios seguintes só trouxeram pareceres, e o diff do item não mudou.

**Afrouxa, por desenho, sem regra com ID:** #890. O `--limpar` remove o clone de parecer já mesclado, e só a tag `arquivo/*` deixa de prender o clone. Não há caminho de ataque realista.

Nenhuma invariante saiu, e nenhum teste foi apagado sem outra guarda no lugar. No #908, a asserção da contagem dá lugar às asserções da lista exata de prefixos por hook e da ausência de contagem. O PR da promoção pede o rótulo `afrouxa-regra` do dono, e o aviso de marco precisa listar os 11 itens acima como itens que afrouxam.

## Riscos aceitos e ferramentas
Nenhum risco aceito novo nem pendente de aceite: o diff não toca `docs/security/aceites/`, e a medida dá `aceites-novos=0`.

**Para o dono, no merge da main (`R-MAIN`, `R-DECISAO`), sem bloquear este parecer:**
- **O #906 entra na 0.47.19 contra a DECISÃO de 26/11 09:37** ("O #906 fica para a 0.47.20"). O dono mesclou o #906 na develop às 09:50, depois dessa decisão, então o código já está no commit que será promovido. Anexá-lo às notas é o correto para a segurança: um afrouxamento que entra calado seria pior.
- **A inclusão nas notas não tem a palavra do dono.** Ela tem só "sem objeção" a uma recomendação do Jarvis (Histórico, 09:53), e silêncio não é aceite. A confirmação cabe ao dono, no merge da main.
- **O #908 também entra na 0.47.19 sem decisão expressa.** O dono o mesclou às 10:24, antes do 1º anexo e da promoção. Sem ele nas notas, `scripts/promover-homolog.py --conferir-ref` recusa a promoção pelo fragmento pendente. O código já está no commit que será promovido, então anexá-lo é o correto, pelo mesmo motivo do #906.
- **A autorização de main é anterior aos anexos.** A autorização de 25/11 21:32 ("autorizo mesclar main versao 0.47.19 ate amanha") foi dada quando a versão tinha 10 itens; agora são 19.

Cartão em aberto da rodada anterior: CATRACA-SALVAR-PROTEGIDO. `hooks/salvar.py` continua fora de `PROTEGIDOS` (`tests/catraca.py:48`). A severidade é baixa, e o dono do cartão é o `devops-engineer`.

Rodei localmente, neste head, só o seguinte:
- `comparar`, `conferir-release`, `tests.test_changelog` e `tests.test_indice_fixtures` (101 testes, OK), e `scripts/indice-fixtures.py --conferir` (`em dia`);
- `bin/forge-mutante tests/mutantes/v0481-fixtures-gerada.json`: `M1 · morreu`;
- a junção do #908 por `merge-tree`;
- a leitura do rótulo e do merge do #908 pela API (só leitura).

A suíte inteira vale pelo CI. Lacuna: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint` e `trivy` estão fora do PATH. O diff da versão não toca workflow nem dependência, e a busca de segredos foi feita por padrões.

- ci: 17395e4d905fdbf24bbe21451050873b77261ba6 verde

CI no head `17395e4d` (runs 45834666619 e 45834666443): as 10 partes da suíte (3.12 e 3.14), `bateria`, `bateria (pareceres)`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, os dois `teto de pulados`, `instalação`, `árvore já provada` e a `catraca` estão verdes, sem vermelho.
