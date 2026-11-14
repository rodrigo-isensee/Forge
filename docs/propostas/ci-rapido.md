# CI-RAPIDO: PR em até 5 minutos e develop em até 8, sem perder verificação

Pedido v047, etapa E1.242. Só desenho e medidas: nenhum código, nenhum workflow alterado. Para o parecer de segurança (o desenho mexe no CI) e para o dono (`R-CONFORMIDADE`: os checks exigidos são dele). Decisão do dono de 2026-11-14 16:29: leitura (b), o PR segue com a suíte inteira, só mais rápido, em 5 partes equilibradas; sem teste por mapa no PR; `CLAUDE.md` igual; sem o curinga do blob.

## 1. Medidas (API do GitHub, sem log)

Fonte: `gh api repos/<repo>/actions/runs/<id>/jobs` (início e fim de cada job e de cada passo). Repositório público: runner padrão de 4 vCPU, minutos gratuitos (`R-CUSTO` fica em zero).

**Develop (push), os 3 últimos runs verdes do CI** (um job só por versão de Python, `scripts/suite-paralela.py`, 4 processos):

| run | head | Python 3.12 | Python 3.14 | relógio do run |
|---|---|---|---|---|
| 43632222797 | 067b2a9f | 1177 s | 1199 s | 21 min 11 s |
| 43626821213 | 7fff73e4 | 1155 s | 1238 s | 20 min 56 s |
| 43610857016 | 6517ff14 | 1400 s | 1471 s | 24 min 49 s |

Os dois jobs rodam em paralelo; o relógio é o do mais lento mais a fila: 21 a 25 min.

**PR, os 4 últimos runs verdes** (3 partes por Python; os tempos são do passo `Testes do Forge (parte)`):

| run (branch) | relógio | 3.12 partes 1/2/3 | 3.14 partes 1/2/3 | soma 3.12 | soma 3.14 |
|---|---|---|---|---|---|
| 43630134716 (heredocs-orcamento) | 22 min 27 s | 637 / 358 / 388 | 629 / 317 / 418 | 1383 | 1364 |
| 43629475422 (release-0.47.1) | 13 min 53 s | 491 / 255 / 463 | 483 / 257 / 359 | 1209 | 1099 |
| 43626749146 (develop-vermelho) | 11 min 14 s | 634 / 345 / 465 | 502 / 322 / 397 | 1444 | 1221 |
| 43615083858 (fila-suite-espera) | 8 min 25 s | 423 / 237 / 430 | 347 / 430 / 305 | 1090 | 1082 |

Passos baratos: `bateria (passos)` 12 a 23 s, `bateria (pareceres)` 8 a 14 s, `verificações longas` 14 a 18 s, `instalação (python 3.14)` 10 a 19 s, `árvore` 6 a 9 s, `teto de pulados` 6 a 14 s, agregadores 2 a 4 s. Nenhum deles é o caminho crítico.

O que as medidas dizem:

1. **O trabalho cabe na soma, não na divisão.** Um job de suíte inteira (develop) leva 1155 a 1471 s e as 3 partes do PR somam 1082 a 1444 s: o custo é linear e cada parte nova é um runner novo. Média da soma por versão: 1236 s (mín. 1082, máx. 1444); a variação do mesmo código entre runs é de cerca de 14%.
2. **A divisão atual não equilibra, e o erro é sistemático.** Os pesos preveem 949 / 950 / 950 (LPT sobre `tests/pesos-d4.json`), mas a parte 1 leva 1,8 vez a parte 2 nos 4 runs do 3.12 (637/358, 491/255, 634/345, 423/237) e em 3 dos 4 do 3.14. Ruído de runner não repete 4 vezes; é peso errado. Causa estrutural: `scripts/suite-partes.py` (`pesos_por_modulo`) soma as chaves `módulo.Classe.teste` e reparte **módulos inteiros**; `test_hooks` pesa 680 s de 2848 (23,9%) e cai inteiro numa parte.
3. **Teto de granularidade por módulo.** Com 5 partes, uma parte ideal tem 20% do trabalho; o módulo `test_hooks` sozinho tem 23,9%. Simulei a LPT por módulo sobre o arquivo de pesos: 3 partes dão [949, 950, 950]; 5 partes dão [680, 542, 542, 542, 542]. A parte do `test_hooks` fica 19% acima da média mesmo com pesos perfeitos: 0,239 x 1236 = 296 s, acima dos 264 s que o PR comporta (conta abaixo). Cinco partes por módulo **não** chegam a 5 min.
4. **O resumo do job não sai pela API.** Conferi: `GET /repos/<repo>/check-runs/<job>` devolve `output.summary: null` e o objeto do job só tem passos, tempos e conclusão. O `$GITHUB_STEP_SUMMARY` (hoje com as 10 unidades mais lentas, `montar_resumo` em `scripts/suite-paralela.py:638`) só se vê na página do run, contra o que a decisão de 14/11 supôs. As **anotações** de check run saem pela API sem blob (`GET /repos/<repo>/check-runs/<job>/annotations`, conferido com 200 e os campos `title`, `message`, `raw_details`). O desenho usa anotação. Tentar o log do job (`GET /repos/<repo>/actions/jobs/<id>/logs`) deu 302 para `productionresultssa5.blob.core.windows.net` e o proxy negou: é o host exato daquela chamada, não pedido agora porque o desenho não precisa dele.
5. **Não há tempo por teste medido no CI.** O único tempo por unidade é o de `tests/pesos-d4.json` (182 unidades, soma 2848 s), regravado na máquina de quem roda `FORGE_SUITE_MEDIR=1` (12 núcleos aqui, contra 4 vCPU do runner). Os 20 mais lentos abaixo vêm dele e são **hipótese** até a primeira rodada com anotação.
6. **Fila de runners.** No run 43630134716 a parte 3/3 do 3.12 começou às 19:11:20, 5 min depois das outras (19:06), e o agregador `bateria` abriu 8 min depois do último `teto de pulados`. O plano gratuito limita 20 jobs simultâneos; este run tem 6 partes e 8 jobs leves, e o push na develop corria junto. Ver riscos (S11).

## 2. Desenho

### 2.1 A develop em partes, como o PR

Hoje: `rapida` e `rapida-quatorze` (um job de suíte inteira por Python, `if: push na develop`, `timeout-minutes: 30`). Depois:

- Dois jobs de matriz na develop, `rapida-doze` e `rapida-quatorze`, `parte: [1, 2, 3, 4, 5]`, cada perna `python3 scripts/suite-partes.py --parte K/5` com o mesmo preparo do PR (checkout, setup-python, passo `env -a`), `fail-fast: false`, `permissions: contents: read`, `timeout-minutes` 15 (medido mais folga, ver conta).
- Cada perna grava os pulados (`FORGE_SUITE_PULADOS`) e os sobe como artefato de 1 dia, como no PR (T3).
- **Um job agregador por Python com o nome exato de hoje**, `checagem rápida (push na develop)` e `checagem rápida (push na develop, python 3.14)`: `needs` das 5 pernas, `if: always()`, baixa os 5 artefatos, roda `suite-partes.py --somar-pulados 5 <pasta>` e só passa com as 5 pernas em `success` e o teto de pulados verde (nunca `skipped`, como o agregador `bateria`). Assim `scripts/arvore-testada.py` (`JOBS_DE_PROVA`, igualdade exata de nome, `conclusion == success`, `head_sha`, `run_id`) **não muda**: a prova da promoção continua sendo um job de nome fixo cujo sucesso implica 5 pernas verdes e a divisão completa. Os nomes das pernas levam "parte K/5" e não colidem com o do agregador.
- A matriz do PR e a da develop usam a mesma divisão (`--parte K/5` sobre a mesma árvore dá a mesma partição); o `arvore` e a promoção seguem como estão: a suíte inteira no PR, na develop e na promoção, sem mapa.
- Sem `needs` entre a develop e os jobs de PR (a develop não roda `bateria (passos)` nem `arvore`; eles seguem `if` de PR).

### 2.2 Pesos refeitos e 5 partes: a conta

Modelo medido (run 43626749146, o mais limpo, e conferido nos outros): relógio do PR = passos baratos até o início das partes (1 a 23 s, mediana 13) + preparo do job (9 s, dos quais `env -a` 3 a 5 s) + T da parte mais lenta + `teto de pulados` e agregador (12 s). Arredondo: **PR = T + 36 s; develop = T + 20 s** (sem o portão de passos).

| meta | T permitido |
|---|---|
| PR 300 s | T <= 264 s |
| develop 480 s | T <= 460 s |

Trabalho por versão de Python: W médio 1236 s, pior medido 1444 s, melhor 1082 s. Com divisão perfeita em N partes:

| N | W médio / N | W pior / N | PR (médio / pior) | develop (médio / pior) |
|---|---|---|---|---|
| 3 | 412 s | 481 s | 448 s / 517 s | 432 s / 501 s |
| 4 | 309 s | 361 s | 345 s / 397 s | 329 s / 381 s |
| 5 | 247 s | 289 s | 283 s (4:43) / 325 s (5:25) | 267 s (4:27) / 309 s (5:09) |
| 6 | 206 s | 241 s | 242 s / 277 s | 226 s / 261 s |

Leitura:

- **Develop em 8 min:** 5 partes dão 4:27 no médio e 5:09 no pior, com folga de 2:50; 3 partes passariam no médio (7:12) e estourariam no pior (8:21). A develop usa as mesmas 5 partes do PR (uma definição só).
- **PR em 5 min:** 5 partes só chegam se o desequilíbrio ficar abaixo de 7% (247 s contra 264 s) e mesmo assim o pior run medido (1444 s) dá 5:25. A meta de 5 min é atingível **no caso médio** com divisão por unidade; **não é garantida** pela divisão sozinha, porque a variação entre runs do mesmo código é de 14%. Para ter margem, o item 2.3 corta W: 25% a menos nos 20 mais lentos (57% do peso) tira 14% de W, e então 1444 s viram 1242 s, 248 s por parte e 284 s de relógio (4:44) no pior caso. Se com a divisão certa e a aceleração o PR ainda passar de 5 min, o dono pediu os números de novo (ordem de 14/11): o relatório da rodada de calibração os traz.

O que muda para a conta fechar:

1. **Dividir por unidade, não por módulo.** `suite-partes.py --parte K/5` passa a usar as unidades de `suite-paralela.planejar` (a mesma partição que o suite-paralela já usa entre os 4 processos: `módulo`, `módulo.Classe` ou `módulo.Classe.teste` conforme as chaves de `tests/pesos-d4.json`), em LPT sobre 5 partes. `test_hooks` deixa de ser um bloco de 680 e vira 6 unidades de 17 a 199. A guarda de completude fica e passa a valer por ID: a união das 5 partes é o `discover` inteiro, cada teste uma vez, falha fechada. Simulei o LPT por unidade sobre o arquivo de pesos: 5 partes de 569,6 a 569,7 s de peso, desequilíbrio previsto de 0% (a maior unidade, 199, é 35% de uma parte e ainda cabe).
2. **Pesos refeitos pelo CI, não pela máquina de quem escreve.** Rodada de calibração: as 10 pernas (5 por Python) gravam, em **anotação** do check run, o tempo de cada unidade que rodaram (JSON de uma linha com nomes e segundos; a primeira rodada confirma o limite real de tamanho da anotação e, se cortar, grava em blocos). Um script pequeno (`scripts/pesos-do-ci.py`, a escrever) lê as anotações pela API (`gh api .../check-runs/<job>/annotations`, sem blob), junta 3.12 e 3.14 pela média e gera o `tests/pesos-d4.json` novo para o dev da stack conferir e commitar. **Nenhum workflow grava no repositório** (`R-MAIN`, `R-VERIFY`). Chave ausente continua valendo a mediana, como hoje.
3. **Manutenção:** um checkpoint por release (junto da medida de minutos do `ci-cd`): refaz os pesos e confere o desequilíbrio; subiu mais de 15% entre partes, abre cartão.
4. **O resumo continua**, com as 20 mais lentas (hoje 10) e a soma por parte para o humano. A fonte para quem mede é a anotação.

### 2.3 Os 20 mais lentos e como acelerar sem tirar caso nem afrouxar asserção

Fonte: `tests/pesos-d4.json` (segundos na máquina do autor; hipótese até a calibração). Somados valem 1630,5 s de 2848,4 (57,2%).

| # | unidade | s | o que o código sugere | como acelerar |
|---|---|---|---|---|
| 1 | test_hooks.Hooks.test_fixtures | 198,9 | um teste percorre todas as fixtures (`executar_em_lote`) | fatiar em N métodos pelo índice da fixture (`i % N`) com asserção de que a união das fatias é o conjunto inteiro: mesmos casos, mesma asserção, unidades de ~40 s que a LPT espalha |
| 2 | test_hooks.Hooks.test_t1_variantes_que_o_bash_ignora_... | 157,2 | corpus de variantes em laço | mesma fatia por variante ou família |
| 3 | test_hooks (restante do módulo) | 135,4 | 3296 linhas, 22 subprocessos, 11 `git init` | `setUpClass` com um repositório-modelo copiado por teste (cópia de diretório no lugar de `git init` e commits), onde o teste não é sobre o `init` |
| 4 | test_forge (restante) | 127,2 | 7482 linhas, 81 subprocessos, 23 `git init` | mesmo repositório-modelo; abrir por classe (`ConferenciaPresaAoHead`, `ForgeCheck` etc. já têm chave própria) |
| 5 | test_hooks.Hooks.test_donos_dos_heredocs_iguais_aos_da_base | 122,8 | compara o hook com a base em corpus | fatia do corpus como no 1 |
| 6 | test_catraca | 109,4 | 3679 linhas, 19 subprocessos | abrir por classe nos pesos (hoje uma unidade) |
| 7 | test_fechar_espera_catraca | 84,8 | 190 linhas, zero subprocesso, esperas reais de 2 a 4 s com `FORGE_FECHAR_INTERVALO=1` | relógio injetável no lugar do tempo real: o teste conta leituras de check (`leituras_de_checks`), a asserção fica; só o tempo some |
| 8 | test_volta_por_delta | 74,2 | 1401 linhas | abrir por classe |
| 9 | test_hooks_volta_corpus...test_corpus_nos_dois_hooks | 61,9 | corpus nos dois hooks | fatia do corpus (junto do TESTE-CPU-CORPUS) |
| 10 | test_atualizar | 60,5 | 23 subprocessos, 2 `sleep` | repositório-modelo; `sleep` por relógio injetado |
| 11 | test_conf_escopo | 56,6 | sem subprocesso, laços de casos | CPU puro: perfilar (`cProfile`) e tirar o custo repetido de preparar cada caso |
| 12 | test_entrega_git_falha | 55,8 | 2 subprocessos | perfilar; provável espera de timeout real |
| 13 | test_hooks_volta_lancador...sem_marcador_atras_de_lancador... | 55,8 | propriedade sobre alfabeto | fatia do espaço de casos |
| 14 | test_hooks_volta_lancador...leitura_a_mais_que_falha... | 54,4 | idem | idem |
| 15 | test_qa_lote_l08 | 53,5 | 32 testes, `forge-check` real em subprocesso | repositório-modelo; o subprocesso fica (o teste é sobre o binário) |
| 16 | test_fechar | 49,7 | 1149 linhas | abrir por classe |
| 17 | test_suite_paralela | 46,9 | 14 subprocessos, 11 `sleep` | relógio injetado onde o teste não mede tempo |
| 18 | test_doutor | 42,8 | 23 subprocessos | repositório-modelo |
| 19 | test_etapa_do_brief | 42,2 | 3 `git init` | idem |
| 20 | test_hooks_volta_propriedades | 40,5 | propriedades | fatia do espaço de casos |

A coluna "o que o código sugere" vem de contagem de `subprocess`, `git init` e `sleep` em cada arquivo e de leitura rápida, não de perfil: o perfil é o primeiro passo de cada item.

Regras da aceleração (as mesmas para todas): a lista de casos e as asserções não encolhem (a fatia carrega uma asserção de completude da união); `skipTest` e `assertGreaterEqual` de mínimo de fixtures ficam como estão; nenhum `continue-on-error`, nenhum teste pulado (`R-VERIFY`); cada troca de `sleep` por relógio injetado traz um teste do próprio relógio. O autor da mudança é o dev da stack (o `devops-engineer` não edita teste). O `qa-engineer` confere por mutação que a asserção da fatia mata a fatia perdida.

Ordem de ganho: itens 1, 2, 5, 9, 13, 14, 20 (fatia: cerca de 650 s de peso viram unidades de 30 a 50 s; ganho de equilíbrio, sem mudar o trabalho total) e 7 (85 s de espera morta, ganho real de CPU). Os itens por classe (4, 6, 8, 16) só abrem o peso; os de `git init` (3, 4, 10, 15, 18, 19) dão o ganho de trabalho total, de que a meta de 25% nos 20 mais lentos depende.

### 2.4 O CI do modelo de projeto

`templates/projeto/` hoje **não traz workflow** (só `.github/dependabot.yml`, `pull_request_template.md` e o texto de `docs/engineering/protecao-de-branch.md`); o CI do projeto nasce do `devops-engineer` pela skill `ci-cd` e por `stacks/<stack>/pronto.md`, seção "CI". Muda só texto de insumo, nada executável:

- `skills/ci-cd/SKILL.md`, "Tempo e dependências": o orçamento (tempo-alvo do PR e da integração, trabalho dividido em partes iguais por unidade de teste e não por arquivo), a conta T = alvo menos overhead (36 s no PR, 20 s na integração) e a regra "agregador com o nome do check exigido, pernas com nome livre".
- `stacks/python/pronto.md` e `stacks/node-react/pronto.md`, seção "CI": suíte em partes por unidade (pytest com `pytest-split` por peso, vitest `--shard K/N`; só ferramenta gratuita, `R-CUSTO`), pesos regravados por release, agregador que reprova perna pulada ou cancelada.
- `templates/projeto/docs/engineering/protecao-de-branch.md`: os checks exigidos são os agregadores; renomear perna de matriz não mexe na proteção.
- Dependabot e `R-FLUXO` não mudam.

## 3. Segurança: riscos e ameaças para o parecer

| # | ameaça | onde | mitigação no desenho |
|---|---|---|---|
| S1 | Prova forjada na promoção: job de nome parecido com `checagem rápida (push na develop)` em verde sem as 5 pernas | `scripts/arvore-testada.py` (`JOBS_DE_PROVA`, nome exato, `success`, `head_sha`) | O agregador mantém o nome exato e só passa com as 5 pernas `success` (`if: always()`, nunca `skipped`); o nome da perna inclui "parte K/5" e difere. Teste de comportamento pede 3 casos: perna vermelha, pulada, cancelada |
| S2 | N divergente: matriz de 5 e `--parte K/N` ou `--somar-pulados N` com outro N, e a suíte rodaria a menos | matriz, `--parte`, agregador | N escrito uma vez e conferido por `tests/test_ci_local.py` contra o tamanho da matriz e contra os dois argumentos; `--parte` já falha fechado se a divisão não cobre o `discover` |
| S3 | Entrada não confiável em `run:` | todos | só `matrix.parte` (literal numérico fixo no YAML, não vem de PR) em `env:`; nada de título de PR, nome de branch ou `head_ref` interpolados; `zizmor` e `actionlint` do job de passos continuam |
| S4 | Permissões | pernas e agregador da develop | `permissions: contents: read` por job, sem `actions: read` (só o `arvore` o tem) e sem `checks`; o artefato é do mesmo run (sem escopo extra); token nunca no passo da suíte |
| S5 | Artefato dos pulados adulterado ou trocado | upload e download de artefato | nomes por Python e parte, retenção de 1 dia, `if-no-files-found: error`; o agregador soma exatamente 5 arquivos, K de 1 a 5 uma vez só (regra já existente do `--somar-pulados`: parte faltando ou repetida reprova) |
| S6 | Anotação como canal: nome de teste com `::` injetando comando de workflow | calibração | só nomes de unidade (`[A-Za-z0-9_.]`) e números, saneados antes de sair; nunca mensagem de falha nem variável de ambiente; o `montar_resumo` já se limita a "nomes de unidade e números" e a regra se mantém |
| S7 | Cache | todo o desenho | sem `actions/cache` novo; sem cache de fork para branch protegida; nenhuma dependência nova (biblioteca padrão) |
| S8 | `pull_request_target` | todo o desenho | não entra; a develop só em `push` |
| S9 | Divisão por unidade esconder teste (um ID fora de toda parte) | `suite-partes.py` | guarda de completude por ID, falha fechada, com teste que remove um ID e exige vermelho |
| S10 | Pesos regravados pelo CI | `scripts/pesos-do-ci.py` | nenhum workflow grava (`R-MAIN`); o script roda na máquina de quem entrega, lê só a API, e o resultado vira commit revisado |
| S11 | Fila de runners | limite de 20 jobs do plano gratuito | PR (10 partes mais 8 jobs leves = 18) e develop (12) juntos passam de 20 e enfileiram; `concurrency` por ref já cancela o obsoleto; se a fila aparecer na medida pós-mudança, fundir `teto de pulados` ao agregador é a próxima alavanca; nada de runner pago (`R-CUSTO`) |
| S12 | Afrouxar verificação para ganhar tempo | revisão | proibido: nada de `continue-on-error`, `[skip ci]`, teste pulado, asserção encurtada ou matriz reduzida (`R-VERIFY`); o ganho vem de dividir melhor e de tirar espera morta |

Checks exigidos (ruleset `checks-obrigatorios-develop-main`, lido pela API): `bateria`, `bateria (python 3.14)`, `catraca`. Os nomes das pernas ("suíte (python 3.12, parte K/N)") não são exigidos, então trocar 3 por 5 não pede mudança do dono; renomear um agregador pede (`R-CONFORMIDADE`), e o desenho não renomeia nenhum.

## 4. Fora desta etapa e próximos passos

- Código: `suite-partes.py` por unidade, a anotação de tempos, `pesos-do-ci.py`, a edição do `ci.yml` (branch `melhoria/*`; o token do bot não tem o escopo `workflow`, o envio é do dono), a aceleração dos testes (dev da stack) e o parecer de devops do `ci.yml` (`docs/devops/`). Mudança em arquivo protegido de `.github/` pede o rótulo `afrouxa-regra` do dono no PR.
- Ordem sugerida: (1) anotação de tempos e rodada de calibração, (2) divisão por unidade com pesos do CI, (3) develop em partes com o agregador de nome fixo, (4) aceleração dos 20 mais lentos, (5) medida final por `gh run list` com os números para o dono.
- Fora do cartão por decisão do dono: teste afetado por mapa no PR. Se as 5 partes não chegarem a 5 min, o relatório traz os números ao dono.
