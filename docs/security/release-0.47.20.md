---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.20
branch: melhoria/v0481-release-0-47-20
commit: 1e301536467df853dae1e7229952b930078c979d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: release 0.47.20 (leva contra a main, 23 itens), head 1e301536

Etapa E43.3 do pedido v0481 (pedido da versão: release-0.47.20). Leva `origin/main..1e301536`: 23 itens squash na develop (#909 a #934, menos #911, #912, #915), a marca `3bf1456e` e o anexo `1e301536` (fragmentos do #933 e do #934, trazidos pelo merge `df12c5f5` da develop `8855671d`).

Gatilhos: hooks (`hooks/conformidade.py`, `hooks/estado.py` novo, `hooks/ordens_teto.py` novo, `hooks/vigia.py`, `hooks/hooks.json`), CI/CD (`.github/workflows/ci.yml`, `diario.yml` e `obsoletas.yml` novos), ambiente que roda como root (`.devcontainer/devcontainer.json`, `scripts/preparar-estacao.sh`), controles do Forge (`docs/regras/R-FLUXO.md`, ADR 0003, ADR 0018, `tests/config.json`, `bin/forge-check`, `bin/forge_pareceres.py`, `bin/forge_autorizacao.py`), release usada por todos os projetos.

## Junção: cada item com o parecer próprio
Para cada squash, busquei `refs/pull/<n>/head` e conferi:
- `git merge-tree --write-tree <pai da squash> <head do PR>` dá árvore igual à squash no repositório inteiro: 0 arquivos de diferença nos 23;
- o parecer de segurança do item está `aprovado`, com `pedido: v0481`, e o `commit:` dele é ancestral do head do PR (22 de 22; o #934 não tem parecer, ver abaixo);
- o código no `commit:` do parecer de segurança é o do head. Diferem só #913, #917, #921 e #929. Nos três primeiros, a diferença é só a develop trazida: a contribuição no `commit:` do parecer, refeita sobre o pai da squash, dá a squash, com 0 arquivos de diferença. No #929, sobram `tests/mutantes/v0481-f6-ci-uma-vez-2.json` e `tests/test_suite_partes.py`, de `e8998527` e `700a2fc4`. São só teste (divisão da spec e asserções novas), e review e QA do #929 estão `aprovado` em `700a2fc4`.

| PR | head | squash | parecer de segurança (`commit:`) |
|---|---|---|---|
| #909 | `0bbf6ab8` | `33531eee` | `v0481-pesos-gerados` (`f9fa7be3`) |
| #910 | `e9e23cfd` | `376633b7` | `v0481-s1-status` (`154a36f1`) |
| #914 | `bd1aa546` | `3c833f3f` | `v0481-g2-autoria` (`f0c380e2`) |
| #916 | `072558e6` | `707fea56` | `v0481-g2-publicar-caminho` (`0cdf17c3`) |
| #918 | `5cb4d801` | `c42a580d` | `v0481-rotulo-pelo-time` (`c58e1409`) |
| #919 | `6061916c` | `7ceb445f` | `v0481-g2-mitigacoes` (`d1c2d815`) |
| #922 | `c844bbae` | `f1e4f478` | `v0481-oraculo-hermetico` (`7b2c4cbd`) |
| #917 | `deb56328` | `355bce32` | `v0481-s5-cabecalho` (`c8c2e138`) |
| #921 | `10dc09e1` | `ee05ee84` | `v0481-recibo-contador` (`15759fde`) |
| #923 | `16020058` | `346a7860` | `v0481-g3-entrega-ci` (`18e27eeb`) |
| #920 | `5b2f5603` | `6edd59d2` | `v0481-s1-gancho` (`e4b6bc4a`) |
| #927 | `6d89d684` | `b31f01fd` | `v0481-g3-parte2` (`91e3d5fe`) |
| #926 | `47e4a197` | `0ee707ee` | `v0481-devcontainer-sem-gh` (`a5f6c0f1`) |
| #925 | `348a1f11` | `ad7b7ca2` | `v0481-f1-parecer-fora` (`edaf7bc0`) |
| #929 | `92e15f4c` | `2bdf1a2e` | `v0481-f6-ci-uma-vez` (`5f26b0f9`) |
| #931 | `d2c48315` | `11fc1867` | `v0481-f4-vigia-fluxo` (`dd25e4a8`) |
| #932 | `df545311` | `6716f239` | `v0481-f6-arvore-envio` (`d0f41115`) |
| #924 | `452a9542` | `8ca922ac` | `v0481-f3-develop-no-fim` (`7de82a02`) |
| #928 | `56333823` | `f994c15a` | `v0481-versao-com-20` (`2e6da2d5`) |
| #930 | `8abb84e2` | `cdf7ca7b` | `v0481-hook-raiz-forge` (`3c1bd382`) |
| #913 | `39ac7a52` | `1f8fea65` | `v0481-ci-parecer-nao-cancela` (`7bf55772`) |
| #933 | `f14a55a0` | `996a4812` | `v0481-f5-tamanho-1` (`38acdc43`) |
| #934 | `70e5e938` | `8855671d` | nenhum |

**O #934 entrou sem nenhum parecer** (nem review, nem QA, nem segurança). O corpo do PR diz "entram em seguida", e o dono o mesclou às 10:05 de 27/11 (`mergedBy` pela API). Ele toca só `tests/test_hooks.py:676` e o fragmento, e não toca gatilho do `R-SEGURANCA`. Li o diff nesta rodada. Fora do modo `producao`, o lançador dos testes passa a alargar `PRAZO_DA_SESSAO_S` junto com `PRAZO_DA_DECISAO_S`. A constante de produção (`hooks/_comum.py:2843`, 0,5 s) não muda, e os testes do vigia da sessão rodam em processo, com relógio falso (`tests/test_hooks.py:3410-3525`), fora do lançador. O efeito de segurança é neutro. A falta de review e QA cabe ao `tech-lead` (`R-REVIEW`), não a este parecer.

## Marca, anexo e versão
- **Marca:** `1f8fea65..3bf1456e` toca só os dois `plugin.json`, o `CHANGELOG.md` e os 21 fragmentos apagados.
- **Anexo:** `8855671d..1e301536` toca só os mesmos três arquivos e apaga os fragmentos do #933 e do #934.
- **CHANGELOG:** as 24 linhas dos 23 fragmentos apagados estão no `CHANGELOG.md`, letra a letra. São 24 linhas novas, fora os cabeçalhos, e nenhuma linha sai.
- **Versão:** `0.47.20` em `.claude-plugin/plugin.json:3` e em `dev/.claude-plugin/plugin.json:3`, igual à seção `[0.47.20]` do `CHANGELOG.md`. A `origin/main` está em `0.47.19`. `bin/forge-changelog conferir-release` dá `ok`.
- **Segredos:** nas linhas acrescentadas da leva, a busca pelos padrões de token, chave e chave privada dá 0.

## Superfície protegida de v0.47.19 a 1e301536
- **Workflows:**
  - `obsoletas.yml` (#913) roda só em PR do próprio repositório (`if` em `head.repo.full_name`), sem checkout, com `actions: write` só no job e o token só no passo. Na dúvida (300 arquivos ou mais, ou falha da API), cancela, como antes. O efeito residual é só de disponibilidade.
  - `diario.yml` (#929) roda só por `schedule` e `workflow_dispatch`, com `contents: read` no topo e `issues: write` só no job do cartão. As ações estão fixadas por SHA. O `npm` usa versão fixa e `--allow-scripts` restrito ao pacote.
  - `ci.yml` (#929, #932, #913): o job `arvore-envio` usa o token só no passo de leitura. O concurrency do PR passa a ter grupo por run (`ci.yml`, `group`).
  - Nenhum `pull_request_target`, e nenhum segredo além do `github.token`.
- **Ambiente:** o `postStartCommand` (#926, `.devcontainer/devcontainer.json:30`) clona a `main` do remoto por https, sem credencial, e roda o `preparar-estacao.sh` de lá, nunca o da cópia de trabalho. É a DECISÃO 26/11 22:18.
- **Invariantes:** `tests/config.json` troca 3 invariantes de texto e os motivos delas (#928, a versão com 20 itens), na mesma contagem, sem perder nenhuma. Acrescenta a exceção `npm` para `diario.yml` em `R-NEUTRO` (#929). Nenhum arquivo sai da árvore, fora os fragmentos.
- **Fora do diff:** `.githooks/`, `docs/security/aceites/`, `stacks/` e `tests/catraca.py`.
- **Medida dos hooks:** `bin/forge-check comparar v0.47.19 1e301536` dá `so-aperta: medido base=a2f516d5... head=1e301536... casos=239 aceites-novos=0` (famílias merge-pr, push-forcado e sem-verificar, com 8 casos cada). A medida cobre só a decisão dos hooks que recusam.
- **Hook `estado`** (#920): só números de PR, o sha e o título de commit do último merge entram no contexto. Nenhum texto de PR de terceiro entra (`bin/forge_estado.py:58`, `:151`), e tudo passa por `sem_controle`.

## O que aperta, o neutro e o que afrouxa (para a lista do PR da main)
Nos controles que recusam, a versão só aperta ou é neutra frente à 0.47.19: a medida dá `so-aperta`, e nenhum item faz passar uma entrada que antes era recusada. Na norma, a versão **não é só aperta**. As 7 regras afrouxadas com a marca no título, mais 4 afrouxamentos registrados nos pareceres dos itens, entram por decisão do dono, e não por esta confirmação.

**Afrouxa, as 7 com a marca no título.** O pedido de origem de todas é o v0481.

| Item | O que afrouxa (motivo) | Aceite do dono | Rótulo `afrouxa-regra` |
|---|---|---|---|
| #909 | PR-VERDE C1: o módulo de teste novo sem peso não reprova e vale a mediana (fim do conflito de pesos entre PRs paralelos) | ORDEM 26/11 09:40 e DECISÃO 26/11 10:44, **"até a próxima versão"** | 26/11 15:53Z |
| #918 | ADR 0018, emenda ROTULO-PELO-TIME: ato fixo `rotulo-pelo-time`, só no Forge. **Sem efeito nesta versão:** R1 só vale com R3 na develop (`docs/adr/0018-autorizacao-do-dono-gravada.md:203`), R3 não existe, e a DECISÃO 27/11 09:20 mantém o rótulo proibido ao time | ORDEM 26/11 12:57 | **nenhum**. O PR entrou sem o rótulo, pela conta do dono (26/11 19:37Z) |
| #920 | ADR 0003, itens 1 e 2: o hook `estado` injeta no contexto o `forge-check status`, com leitura de rede no GitHub e prazo de 8 s. Mudam 3 testes de registro dos hooks | ORDEM 25/11 21:40 (S1) | 26/11 19:50Z |
| #928 | ADR 0018, retirada VERSAO-COM-20: sai o ato `corte-diario`, a versão fecha com 20 itens e 3 invariantes de `tests/config.json` são trocadas | DECISÃO 26/11 21:57 | 27/11 11:54Z |
| #929 | O portão do PR roda a suíte uma vez (3.12). A suíte 3.14, o e2e 3.12 e os mutantes vão ao diário da develop. Exceção `R-NEUTRO` para o `npm` em `diario.yml` | DECISÃO 26/11 19:37 (F6) | 27/11 05:04Z |
| #931 | ADR 0003, item 7: o aviso do `vigia` conta PR sem agente e agente preso, também com agente rodando, e o teto do texto sobe de ~200 para 280. Lê só a lista gravada em disco, sem rede | DECISÃO 26/11 19:39 (F4) | 27/11 07:42Z |
| #932 | `R-FLUXO`: o push na develop pula a suíte quando a árvore é a mesma já provada no CI do PR (`arvore-envio`) | DECISÃO 26/11 19:37 (F6: "a develop não repete o que já passou no pedido") | 27/11 11:10Z |

**Afrouxa também, sem a marca no título**, segundo o parecer de segurança de cada item:

| Item | O que afrouxa | Aceite do dono |
|---|---|---|
| #923 e #927 (G3) | No Forge, a entrega deixa de rodar o D2 local (`forge-check pronto`), e a prova passa a ser o CI do PR no head exato. `forge-check pr --previo`: a conferência que falta vira aviso. O #927 devolve à entrega o portão do título do PR e os jobs do agregador | DECISÃO 26/11 18:54 |
| #924 (F3) | A base velha só avisa no pronto, e `R-FLUXO` perde a exceção "base velha" | DECISÃO 26/11 19:31 |
| #921 | Com o arquivo de ordens já acima do teto, a gravação que não cresce passa (ADR 0003, item 3). Foi pedido pela própria segurança (A3) e não abre furo | por desenho, sem regra com ID |

**Aperta ou neutro.** Os outros 12 itens: #910, #913, #914, #916, #917, #919, #922, #925, #926, #930, #933 e #934. Os rótulos que eles têm (11 deles, menos o #917 e o #934) vêm só de tocarem controle; o parecer de cada um diz que só aperta ou é neutro. Os mais fortes:
- #930: a sessão do Forge barra a escrita em `.githooks/` e em `.devcontainer.json`;
- #919: o publicar recusa PR de fork ou de outro repositório;
- #916: o publicar confere o caminho e a autoria;
- #917: o cabeçalho do parecer fecha só na linha `---`;
- #926: o root só roda o script da `main`.

Rótulos: todos os eventos `labeled` foram feitos pela conta do dono. Como o time usa essa conta (DECISÃO 27/11 08:54), o evento não prova quem pôs o rótulo. Nenhum teste foi apagado sem outra guarda no lugar, e nenhuma invariante saiu.

## O corpo do PR da main
A ferramenta **não garante** que o PR da main liste as regras afrouxadas:
- `scripts/promover-homolog.py:222` (`corpo_do_pr`) gera só o checklist do rótulo;
- o R3 da emenda ROTULO-PELO-TIME, a catraca conferir essa lista, não está implementado;
- o corpo do #935 lista os 23 itens, mas não as regras afrouxadas.

Pela ORDEM 26/11 12:57 e pela ORDEM 27/11 10:08 ("Liste nele toda regra afrouxada"), o corpo do PR `homolog` → `main` deve trazer as duas tabelas acima. Cada linha leva o item, o motivo e o pedido de origem (v0481), além dos pontos de "Para o dono". O dono do texto é o Jarvis, ou quem abre o PR da main. Fica como cartão ao `devops-engineer`, para o `promover-homolog.py` montar a lista a partir dos títulos com `[afrouxa-regra` e do rótulo. Esse cartão é o R3 da emenda.

## Riscos aceitos e ferramentas
Nenhum risco aceito novo nem pendente de aceite: o diff não toca `docs/security/aceites/`, e a medida dá `aceites-novos=0`.

**Para o dono, no merge da main (`R-MAIN`, `R-DECISAO`), sem bloquear este parecer:**
- **O #909 foi aceito "até a próxima versão"** (DECISÃO 26/11 10:44). Na 0.47.20, o aceite está no limite: decida se a mediana para módulo novo fica ou volta.
- **O #934 entrou sem review nem QA.** O efeito de segurança é neutro (acima).
- **O #933:** a DECISÃO 27/11 09:20 diz "na próxima versão", e a das 09:21 diz "nesta versão". Vale a mais nova, e ele está na leva.
- **A versão tem 23 itens**, acima dos 20, por ordem do dono (27/11 09:20 e 10:08).

Cartões em aberto, de severidade baixa e sem mudança:
- CATRACA-SALVAR-PROTEGIDO: `hooks/salvar.py`, `hooks/estado.py`, `hooks/ordens_teto.py` e `hooks/vigia.py` ficam fora de `PROTEGIDOS` (`tests/catraca.py:48`). Dono: `devops-engineer`.
- O resíduo do G3 em `hooks/parecer.py:849-866`, registrado no parecer do #927. Dono: o autor do hook.

Rodei localmente, neste head, só leitura e medida:
- `comparar` e `conferir-release`;
- as junções por `merge-tree`;
- a conferência dos fragmentos;
- a busca de segredos por padrões;
- as leituras do GitHub (rótulos, `mergedBy`, check-runs), só leitura.

A suíte inteira vale pelo CI. Lacuna: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint` e `trivy` estão fora do PATH. Os workflows novos foram lidos à mão.

- ci: 1e301536467df853dae1e7229952b930078c979d verde

CI no head `1e301536` (runs 46005741853, 46005741947 e 46005742028): verdes as 5 partes da suíte (3.12), `bateria`, `bateria (pareceres)`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)`, `teto de pulados (python 3.12)`, `árvore já provada na develop`, `cancela runs obsoletos do PR` e `catraca`. Sem vermelho. Os jobs só de push na develop aparecem como `skipped`.
