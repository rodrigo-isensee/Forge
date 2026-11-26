---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.19
branch: melhoria/v0481-release-04719-anexo
commit: 0157977e02dc38058c1b762b01d301985f85573f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: release 0.47.19 (versão inteira, 18 itens), revalidada no anexo 0157977e

Etapa E12.34 do pedido v0481, volta por delta de `da7b59be..0157977e`. O delta de código é só `CHANGELOG.md:24`, +1 −1, a linha do anexo (E12.31); o resto são os pareceres da rodada E12.28 a E12.30. O delta é neutro: é só texto e não toca nenhum controle. A rodada E12.30, aprovada em `da7b59be`, fica no git. Ela vem do parecer da marca (E12.25, aprovado em `9487d956`, commit `cfc7bd6d` da branch `melhoria/marca-0.47.19`, que não entrou na develop) e o estende para a versão inteira:
- os **10 itens da marca** (#874, #877, #885, #886, #890, #892, #895, #896, #897, #898), lidos na rodada anterior, com a conclusão abaixo;
- os **8 itens do anexo** (#875, #901, #903, #904, entre o corte `cc4376fe` e a squash da marca `020e4af7`; #878, #902, #888, #906, depois dela);
- a **marca** (`020e4af7`, #905) e o **anexo** (`docs/security/v0481-release-04719-anexo.md`, só metadado de versão).

Gatilhos: hooks (`hooks/salvar.py` novo, fora do sandbox; `hooks/conformidade.py`, `hooks/_comum.py`, `hooks/conformidade.json`, `hooks/hooks.json`), controles do Forge (`bin/forge-check`, `bin/forge-fechar`, `bin/forge_autorizacao.py`, `bin/forge_pareceres.py`, `bin/forge_pronto.py`, `tests/catraca.py`), regras com ID e ADRs (`docs/regras/R-FLUXO.md`, `docs/regras/R-QA.md`, ADR 0003, ADR 0018), release usada por todos os projetos.

## Junção: cada item com o parecer próprio
**10 itens da marca** (rodada anterior, sem mudança):
- Para cada um, `git merge-tree --write-tree <pai da squash> <head do PR>` dá a mesma árvore da squash nos caminhos de código.
- Segurança, review e QA estão `aprovado`, e o `commit:` de cada parecer é ancestral do head.
- Exceções, só de teste e cobertas pelo review e pelo QA: #886 (`dba51ddf`, M3 realinhado) e #892 (`2259b235`, teste e M5).
- Ficou com o QA: o #896 entrou sem `docs/qa/v0481-copia-base-fechada.md` na develop.

**8 itens do anexo** (esta rodada). Busquei `refs/pull/<n>/head` para `FETCH_HEAD`, sem ref nova, e conferi três pontos:
- a árvore do merge do pai da squash com o head do PR é igual à squash nos caminhos de código (`bin`, `hooks`, `scripts`, `.githooks`, `.github`, `tests`, `agents`, `skills`, `docs/regras`, `docs/adr`, `templates`, `patches`, `stacks`, `dev`, `.claude-plugin`): 0 arquivos de diferença nos 8;
- o `commit:` do parecer de segurança de cada item é ancestral do head;
- a contribuição de código no `commit:` do parecer, refeita sobre o mesmo pai, é igual à squash: 0 arquivos de diferença nos 8.

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

Os 8 pareceres estão `aprovado`, com `pedido: v0481`.

## Marca, anexo e versão
- **Marca:** `cc4376fe..9487d956` toca só os dois `plugin.json`, o `CHANGELOG.md` e os 10 fragmentos apagados, e é idêntica à saída de `forge-changelog release 0.47.19 2026-11-26`.
- **Anexo:** 15 linhas novas (de `8ae4d6c6` a `0157977e`) na seção `[0.47.19]`. São as 14 dos 8 fragmentos apagados, idênticas, mais a linha do anexo. Nenhuma linha da marca sai.
- **Texto, sem efeito de segurança:**
  - a linha do anexo (`CHANGELOG.md:24`) agora diz "os 8 itens" e cita o #906 e o E12.27 (A1 do review, resolvido em `0157977e`);
  - a linha do #877 ainda diz "à espera do dono", embora o dono já tenha aprovado.
- **Versão:** `0.47.19` em `.claude-plugin/plugin.json:3` e em `dev/.claude-plugin/plugin.json:3`, igual a `CHANGELOG.md:7`. A `origin/main` está em `0.47.18` (`52dc3dcd`). `bin/forge-changelog conferir-release` dá `ok`, e `tests.test_changelog` roda 91 testes, OK.
- **Segredos:** nas linhas acrescentadas, a única ocorrência dos padrões de token e chave é o texto de fixture da rodada anterior (`ghp_` seguido de `A`s), sem segredo real. O anexo dá 0.

## Superfície protegida de v0.47.18 a 0157977e
- **Arquivos tocados:**
  - `agents/jarvis.md` (#902);
  - `docs/adr/0003` (#877) e `docs/adr/0018` (#901);
  - `docs/regras/R-FLUXO.md` (#903) e `docs/regras/R-QA.md` (#902);
  - `hooks/_comum.py`, `hooks/conformidade.json`, `hooks/conformidade.py`, `hooks/hooks.json` e `hooks/salvar.py`;
  - `tests/catraca.py`.
- **Fora do diff:** nada em `.github/`, `.devcontainer/`, `.githooks/`, `scripts/`, `docs/security/aceites/`, `templates/` ou `stacks/`. `tests/config.json` também não está no diff, então nenhuma invariante sai.
- **Medida dos hooks:** `bin/forge-check comparar v0.47.18 0157977e` dá `so-aperta: medido base=52dc3dcd... head=0157977e... casos=239 aceites-novos=0` (famílias merge-pr, push-forcado e sem-verificar, com 8 casos cada). A medida cobre só a decisão dos hooks que recusam.

## O que aperta, o neutro e o que afrouxa (para o rótulo afrouxa-regra da promoção)
Nos controles que recusam, a versão só aperta ou é neutra frente à 0.47.18: a medida dá `so-aperta`, e nenhum item faz passar uma entrada que antes era recusada. Na norma, porém, a versão **não é só aperta**. Dez dos 18 itens afrouxam regra escrita e entram por decisão do dono, não por esta confirmação.

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

**Neutro:**
- #885: `modo_por_grupo` com todos os grupos em `barrar`, falhando fechado;
- #897: só mensagem;
- #892: só a linha `docs: ok`;
- #896: só a linha do sha;
- #875 (o movimento do cartão) e a marca e o anexo, que são só metadado.

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

O dono mesclou os 8 itens do anexo na develop em 26/11, entre 07:50 e 09:50 locais (`mergedBy` conferido pela API).

**Afrouxa, por desenho, sem regra com ID:** #890. O `--limpar` remove o clone de parecer já mesclado, e só a tag `arquivo/*` deixa de prender o clone. Não há caminho de ataque realista.

Nenhum teste foi apagado sem guarda mais estrita no lugar e nenhuma invariante saiu. O PR da promoção pede o rótulo `afrouxa-regra` do dono, e o aviso de marco precisa listar os 10 itens acima como itens que afrouxam.

## Riscos aceitos e ferramentas
Nenhum risco aceito novo nem pendente de aceite: o diff não toca `docs/security/aceites/`, e a medida dá `aceites-novos=0`.

**Para o dono, no merge da main (`R-MAIN`, `R-DECISAO`), sem bloquear este parecer:**
- **O #906 entra na 0.47.19 contra a DECISÃO de 26/11 09:37** ("O #906 fica para a 0.47.20"). O dono mesclou o #906 na develop às 09:50, depois dessa decisão, então o código já está no commit que será promovido. Anexá-lo às notas é o correto para a segurança: um afrouxamento que entra calado seria pior.
- **A inclusão nas notas não tem a palavra do dono.** Ela tem só "sem objeção" a uma recomendação do Jarvis (Histórico, 09:53), e silêncio não é aceite. A confirmação cabe ao dono, no merge da main.
- **A autorização de main é anterior ao anexo.** A autorização de 25/11 21:32 ("autorizo mesclar main versao 0.47.19 ate amanha") foi dada quando a versão tinha 10 itens.

Cartão em aberto da rodada anterior: CATRACA-SALVAR-PROTEGIDO. `hooks/salvar.py` continua fora de `PROTEGIDOS` (`tests/catraca.py:48`). A severidade é baixa, e o dono do cartão é o `devops-engineer`.

Rodei localmente só o seguinte:
- `comparar`, `conferir-release` e `tests.test_changelog` (91 testes, OK);
- a junção por `merge-tree`;
- a leitura dos rótulos e dos merges pela API (só leitura).

A suíte inteira vale pelo CI. Lacuna: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint` e `trivy` estão fora do PATH. O diff não toca workflow nem dependência, e a busca de segredos foi feita por padrões.

CI no head `0157977e` (run 45826880513): a `bateria (pareceres)` está vermelha porque os pareceres de review e de QA estão `reprovado` em `da7b59be`. Reproduzi com `tests/catraca.py --modo pareceres`. As voltas desses pareceres correm em paralelo a esta, e por isso esta rodada não grava a linha `- ci:`.
