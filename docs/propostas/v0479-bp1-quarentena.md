---
tipo: plano-tecnico
contrato: 1
pedido: v0478
estado: proposta
ux: nenhum (sem interface; ferramenta, CI e testes)
adrs: [0018]
agentes: [tech-lead, qa-engineer, security-engineer, devops-engineer]
gatilhos_seguranca: [autorizacao, ci-cd, controles-do-forge]  # R-SEGURANCA: OK do dono (ADR 0018), .github/, tests/catraca.py, tests/config.json, docs/regras/, hooks/
---
# BP1: quarentena de teste instável com prazo e cartão, e relógio injetado nos testes de tempo

Pedido v0478, etapa E37.1 (software-architect). Só desenho: nenhum código, nenhum workflow, nenhum teste alterado. Fonte do pedido: `docs/propostas/boas-praticas-1911.md` (BP1 e riscos) e a ordem do dono de 19/11 17:27 (BP1 absorve TESTES-PRAZO-VARREDURA). Prática marcada (M): conferida com fontes atuais na seção 2.

Conformidade: o teste nunca é apagado; o `teto_pulados` vale; cada quarentena tem OK do dono por teste e prazo (`R-CONFORMIDADE`, `R-DECISAO`). Neutro (`R-NEUTRO`) e sem custo em dinheiro (`R-CUSTO`: repositório público, minutos do runner padrão gratuitos, como mede `docs/propostas/ci-rapido.md`; nenhuma ferramenta paga, nem o Trunk nem outro serviço).

Afrouxa? **Sim, em três pontos**, cada um vai ao dono (seção 7):
- a quarentena tira um teste do portão por até um prazo (`R-CONFORMIDADE`; `teto_pulados` de `tests/config.json`);
- o texto de `agents/qa-engineer.md:27` ("Nunca marca teste como `skip`...") ganha a exceção da quarentena;
- se o dono escolher a D5 (a), o teto de CPU do corpus (PROP-TEMPO-CPU, decisão de 2026-10-27) deixa de reprovar.

## 1. O problema, com os números

Do estudo (19/11, 30 h de Forge, 16 a 19/11):
- a develop ficou vermelha 4 vezes por teste dependente de tempo ou de carga;
- um único teste instável segurou 4 PRs;
- uma promoção ficou travada uma noite.

Do repositório (árvore da `melhoria/v0479-estabilidade-bp`, 19/11):
- **Caso 1, teto de CPU do corpus** (`tests/test_hooks_volta_corpus.py:121`, `test_corpus_nos_dois_hooks`): o CI da develop deu 180,55 s contra o limite de 180 s (run 44574989031, commit eca1d21b). Para passar, o dono teve de autorizar um rerun (DECISÃO DO DONO de 19/11 14:59). É orçamento de desempenho dentro da suíte funcional: o limite já multiplica por um fator de carga de 1 a 2 (`limite_de_cpu_do_corpus_sob_carga`) e mesmo assim estourou por 0,3%.
- **Caso 2, sonda S1** (`tests/test_hooks.py:1315`, `test_liberar_ou_provar_a_carga_recusa_a_sonda_s1`): o git falso dorme de verdade 4 s + 3,8 s, e o vigia real do hook (`signal.setitimer`, `PRAZO_DO_MERGE_S = 8.0` em `hooks/_comum.py:2811`) tem de vencer. A folga é de 0,2 s em 8 s (2,5%). O resultado depende de quanto a máquina gasta no resto do hook, e a heurística `carga_explica_a_recusa` (PRAZO-CARGA) tenta separar carga de defeito depois do fato.
- **Tamanho da varredura**: 242 chamadas diretas de `time.sleep(`, `time.monotonic(`, `time.time(`, `datetime.now(` e `perf_counter(` em 57 arquivos de `tests/`, contadas por grep e incluindo specs de mutante e fixtures. Nenhuma guarda impede a próxima.
- **Histórico**: `R-TETO` registra 121 linhas FLAKY e 7 falhas de envio por carga no estudo 0.43.1, e tem a reversão "se passar de 21 FLAKY em 7 dias". Os cartões FLAKY-CARGA, FLAKY-G1-CARGA, FLAKY-CTRLC-TROCA e FLAKY-1 foram consertados um a um, sem um caminho comum.

Hoje o Forge não tem quarentena. Teste instável na develop só tem três saídas: conserto às pressas, rerun com OK do dono ou develop vermelha até o conserto. A suíte não se mexe sem rótulo, e isso é intencional:
- a catraca conta `skip` pela AST (`tests/catraca.py:516`, `regra_testes_enfraquecidos`);
- `teto_pulados` (hoje 1) só cai (`regra_teto_pulados`);
- `testes_fora_do_ci` exige motivo e rótulo.

## 2. Conferência com fontes atuais (M)

| Fonte | Data | O que diz | Como entra no desenho |
|---|---|---|---|
| Martin Fowler, "Eradicating Non-Determinism in Tests", martinfowler.com/articles/nonDeterminism.html | publicado em 14/04/2011; consultado em 19/11/2026 | Quarentena separada da suíte sã, com limite de número (exemplo: 8 testes) ou de tempo (exemplo: no máximo uma semana). Embrulhar o relógio do sistema para poder trocá-lo nos testes, reiniciando o stub a cada teste. Uma checagem por código ou regex que reprova chamada direta ao relógio. | Teto de entradas e prazo de 7 dias (D2, D3); costura de relógio (seção 4); guarda estática do tempo real (Q9) |
| Atlassian Engineering, "Taming test flakiness" (Flakinator), atlassian.com/blog/atlassian-engineering/taming-test-flakiness-how-we-built-a-scalable-tool-to-detect-and-manage-flaky-tests | publicado em 08/12/2025; consultado em 19/11/2026 | Detecta por rerun no mesmo build (para no primeiro "flip") e por histórico. A quarentena tira o teste do pipeline, mas ele continua rodando em job dedicado. Abre ticket com dono e prazo; volta à suíte depois de um período saudável. | Prova de instabilidade = falha e verde na mesma árvore; cartão com prazo; job informativo que segue rodando os testes em quarentena (Q5) |
| Trunk Docs, "Quarantining", docs.trunk.io/flaky-tests/quarantining | sem data na página; consultado em 19/11/2026 | Auto-quarantine opcional. O teste segue rodando e enviando resultado, só a falha não reprova. "Broken tests are not quarantine candidates." Override exige comentário e fica em log de auditoria. | Teste quebrado (falha sempre) não entra, só o que alterna; toda entrada tem motivo e trilha. O serviço em si fica fora (`R-CUSTO`). |
| GitLab Docs, "Quarantining tests" e "Unhealthy tests", docs.gitlab.com/development/testing_guide/quarantining_tests/ | sem data na página; consultado em 19/11/2026 | Metadado `quarantine:` com a URL do issue e um `type` (`:flaky`, `:bug`, `:test_environment`...). O teste roda local, mas sai do CI. Quarentena quando o teste instável bloqueia a branch principal. | Campo obrigatório `cartao` e campo `classe` por entrada |
| *Software Engineering at Google*, cap. 11 ("Testing Overview"), abseil.io/resources/swe-book/html/ch11.html | livro de 2020; consultado em 19/11/2026 | Teste pequeno não pode dormir nem fazer chamada bloqueante. Perto de 1% de instabilidade os testes perdem valor (Google: cerca de 0,15%). Rerun só adia a causa. | Rerun não é conserto; o S1 passa a ser teste pequeno com relógio falso |
| *Software Engineering at Google*, cap. 14 ("Larger Testing"), abseil.io/resources/swe-book/html/ch14.html | livro de 2020; consultado em 19/11/2026 | Testes com sono e timeout "will all start failing when the fleet running those tests becomes overloaded". Teste não hermético quase não tem como ser determinístico. | Diagnóstico dos casos 1 e 2: prazo real e CPU real sob runner disputado |
| Go Blog, "Testing concurrent code with testing/synctest", go.dev/blog/synctest; notas do Go 1.25, go.dev/doc/go1.25 | 19/02/2025 (experimental no 1.24); GA no Go 1.25, agosto de 2025; consultado em 19/11/2026 | Relógio falso numa "bolha": o tempo só avança quando todos estão bloqueados. Sono e timer resolvem na hora, de forma determinística. | Prova de que a prática atual é relógio virtual na linguagem e não tolerância maior. No Python (biblioteca padrão), o equivalente é a injeção de dependência. |
| Python 3.15 docs, `unittest.mock`, "Where to patch", docs.python.org/3/library/unittest.mock.html | documentação 3.15.2; consultado em 19/11/2026 | Fazer o patch onde o nome é procurado, não onde é definido. | O `mock.patch(_relogio)` de hoje (`tests/test_hooks.py:105`) só alcança o teste, não o subprocesso do hook. Por isso a costura entra no `_comum` (seção 4). |

O GitHub Actions não tem quarentena nativa: a página de jobs consultada em 19/11/2026 não traz o recurso. O mecanismo fica no runner da suíte, que já é nosso (`scripts/suite-partes.py`, `scripts/suite-paralela.py`).

**Leitura das fontes, aplicada ao Forge:**
1. A quarentena é prática corrente (Atlassian 2025, Trunk e GitLab hoje). As três exigem rastreio (cartão), prazo ou saída por saúde, e manter o teste rodando fora do portão.
2. A "automática" das ferramentas de mercado pula sem pessoa no meio. Aqui isso contraria o risco do estudo e `R-CONFORMIDADE`. A automação cobre tudo até o OK; o OK é do dono (D1).
3. Para tempo, a prática atual é tirar o relógio real do teste (Fowler; synctest GA em 2025), não alargar a tolerância. A heurística PRAZO-CARGA alarga a tolerância.

## 3. Desenho da quarentena

### 3.1 Registro: `tests/quarentena.json` (dado, não código)
Uma entrada por teste:

| campo | regra |
|---|---|
| `teste` | id completo `modulo.Classe.metodo`, que tem de existir no discover (catraca, AST) |
| `classe` | `relogio`, `carga`, `ordem`, `rede-local` ou `desconhecida`, a taxonomia do GitLab enxugada |
| `cartao` | id do cartão aberto junto (obrigatório) |
| `prova` | `run:<id>` da falha e `run:<id>` do verde **na mesma árvore** (tree-sha), ou `local:<n verdes>/<n>` do `forge-testes --repetir` |
| `desde` | data UTC de entrada |
| `prazo` | data UTC; no máximo `desde` + 7 dias (D3) |
| `autorizacao` | `A-<n>` da ADR 0018, com ato `rotulo-afrouxa-regra` e alvo `pr:<N>` do próprio PR da quarentena |

Regras:
- Um teste por PR de quarentena. Assim o OK por PR da ADR 0018 é o OK por teste, sem ato novo.
- A autorização permanente de rótulo do dono (19/11 13:08) não cobre a quarentena: a ADR 0018 não aceita alvo genérico, e o desenho exige `pr:<N>` (D1).
- Teste que falha sempre não entra ("broken tests are not quarantine candidates"): a prova exige ao menos um verde e uma falha na mesma árvore.

### 3.2 Runner (o que muda em `scripts/suite-paralela.py` e `scripts/suite-partes.py`)
- Carregam as entradas **ativas**: data do runner (UTC) até o `prazo`, inclusive. A data vem de uma função injetável, e os testes do runner usam data falsa.
- Tiram do plano os ids ativos e os somam aos pulados da parte (`FORGE_SUITE_PULADOS`). O `--somar-pulados` segue comparando o total com `teto_pulados`: **o teto vale**.
- A guarda de completude ("a divisão cobre todo o discover") conta o id em quarentena como coberto e pulado, nunca como ausente.
- O resumo do job lista cada teste em quarentena com cartão e prazo.
- **Entrada vencida volta sozinha ao portão.** O runner deixa de excluí-la e o teste roda e reprova como qualquer outro. O vencimento só aperta: nenhuma ação humana é necessária para o controle voltar (D3).
- Arquivo ilegível, entrada com campo faltando ou id que não existe: o runner não exclui nada e avisa. Falha fechada: na dúvida, o teste roda.

### 3.3 Catraca (`tests/catraca.py`, modo `pareceres`, com o rótulo)
- Entrada nova, alterada ou prorrogada em `tests/quarentena.json` barra sem o rótulo `afrouxa-regra` (mesmo padrão de `testes_fora_do_ci`). Com o rótulo, a declaração da ADR 0018 tem de cobrir o PR (G1.4).
- `teto_pulados` pode subir no máximo o número de entradas novas do PR. Quem sobe o teto sem entrada nova continua barrado como hoje.
- Entrada removida exige queda do `teto_pulados` na mesma medida. Sem isso a folga sobra para outro pulo; é regra nova, que só aperta.
- `teto_quarentena` (novo campo de `tests/config.json`, inteiro, só cai sem rótulo) limita as entradas simultâneas (D2).
- Teste em quarentena cujo `def` some barra: a regra de testes no CI (I7b) já cobre, e entra um caso de teste para isso. **O teste nunca é apagado.**
- A AST não ganha `skip`: a contagem de `regra_testes_enfraquecidos` fica igual, e a quarentena não precisa de decorador no código.

### 3.4 Ferramenta: `forge-check quarentena`
- `propor <teste> --run <id>`:
  - lê pelo `gh run` (só leitura, sem custo) a falha e o verde na mesma árvore;
  - recusa sem a prova;
  - abre a branch `melhoria/quarentena-<teste-curto>`;
  - escreve a entrada, o fragmento de changelog e o cartão (com o defeito, a classe e o prazo);
  - sobe o `teto_pulados` em 1;
  - prepara a pergunta ao dono (`R-DECISAO`) com o comando `forge-check autorizacao gravar` da ADR 0018. Não grava autorização: quem grava é a sessão principal com a mensagem do dono.
- `ler`: lista ativas, vencidas e a vencer em 2 dias. O `forge-check proximo` e o Jarvis mostram o aviso no começo da sessão.
- `bin/forge-testes --repetir N -k <teste>`: roda um teste N vezes pela fila e pela trava de `R-TETO` e devolve "verdes/N". Serve de prova local de instabilidade e de prova de conserto (saída da quarentena: N=20 verdes).

### 3.5 CI: job `quarentena (informativa)` (devops-engineer)
- Roda só os ids ativos, 5 vezes, no push da develop, e publica a taxa no resumo.
- Fica **fora** de todo `needs` de agregador: não reprova nada e não segura merge (é a "quarantine pipeline" da Atlassian).
- Sem entradas ativas, sai em segundos. Teto de 10 min.

### 3.6 Saída da quarentena
- PR de conserto: remove a entrada, desce o `teto_pulados` e traz `forge-testes --repetir 20` verde na prova (R-PROVA). Como só aperta, não precisa de rótulo.
- Prorrogação: no máximo uma, com OK novo (outro `A-<n>`, outro PR).
- Vencida sem conserto: volta ao portão (3.2), e o cartão sobe na fila com a develop vermelha como evidência.

## 4. Desenho do relógio injetado (testes herméticos)

### 4.1 Costura no hook (`hooks/_comum.py`)
- `executar(...)` ganha dois parâmetros, **só por palavra-chave**, com o padrão real:
  - `relogio=time.monotonic`;
  - `armar=signal.setitimer`, que no teste vira um vigia falso.
- `vigia_de_prazo` e `estender_prazo` passam a ler `relogio` e `armar` do contexto, em vez de chamar `time` e `signal` direto. O sono do git falso, num teste em processo, avança o relógio falso e dispara `PrazoVencido` quando passa do prazo armado, o que reproduz o sinal.
- **Segurança da costura** (para o `security-engineer`; é controle):
  - nenhuma variável de ambiente, argumento de linha de comando ou arquivo liga o relógio falso; ele só existe dentro do processo de teste que importa o módulo;
  - o `__main__` de cada hook não passa `relogio` nem `armar`. Isso é conferido por AST, estendendo `test_driver_do_lote_chama_o_executar_como_o_main_de_cada_hook`, que já fixa os argumentos;
  - o driver do lote (`DRIVER_DOS_HOOKS`) também não os passa.
  - Por isso o hook real em produção não tem caminho novo de entrada.
- O `_relogio` de `tests/test_hooks.py:105` (patch do lado do teste) fica só para a medida do arnês, não para a decisão do hook.

### 4.2 S1 em duas provas, nenhuma asserção a menos (a catraca conta asserções)
- **Pequena, determinística** (relógio falso, em processo):
  - git de 4 s + 3,8 s, mais o custo simulado do hook de 0,3 s: recusa com a mensagem do vigia;
  - de 4 s + 3,6 s com custo zero: libera;
  - fronteira exata em 8,0 s.
  - Roda em milissegundos e não depende da carga.
- **Real, na direção robusta**: um teste com vigia real e `sleep` real, com razão larga (prazo de 0,5 s contra sono de 5 s), que só afirma a **recusa**. A carga só alonga o sono, e o resultado não muda. A Google mostra que a direção "libera dentro do prazo" é a que falha sob carga; essa direção fica só na prova pequena.
- A heurística PRAZO-CARGA (`carga_explica_a_recusa`) continua nos testes de fixtures reais que ainda dependem dela, e cada um vira item da varredura.

### 4.3 Orçamento de CPU do corpus (caso 1)
Relógio injetado não resolve orçamento de CPU: é medida de desempenho, não de tempo de decisão. Duas saídas, à escolha do dono (D5):
- **(a) Recomendada:**
  - o portão passa a um orçamento **determinístico**: contagem de passos do analisador por texto, por exemplo regex avaliadas e corpos de heredoc montados. O `qa-engineer` desenha o contador na Q8;
  - os segundos de CPU viram medida informativa no resumo do job, com alarme quando passam do limite em 3 runs seguidos da develop.
  - Afrouxa a PROP-TEMPO-CPU (2026-10-27).
- **(b)** Fica como está e entra em quarentena na próxima falha (D1 a D3).

### 4.4 Varredura (absorve TESTES-PRAZO-VARREDURA)
- **Guarda estática** `tests/test_tempo_nos_testes.py`: lê `tests/*.py` por AST e lista as chamadas diretas a `time.sleep`, `time.monotonic`, `time.time`, `time.perf_counter` e `datetime.now`/`utcnow`. É o "regex check" de Fowler.
- **Lista de permitidos** `tempo_real_permitido` em `tests/config.json`: `arquivo` → motivo (mínimo de 20 caracteres, como `testes_fora_do_ci`).
  - Nasce com o inventário de hoje.
  - Só cai sem rótulo (catraca); chamada nova fora da lista reprova.
  - Specs de mutante e fixtures ficam fora (não são teste).
- **Conversão por classe**, um cartão por classe e cada item dentro dos limites da seção 5:
  - (R) data de parede para datar: relógio injetado;
  - (S) sono para esperar evento: espera por evento ou sondagem com prazo largo, que só afirma na direção robusta;
  - (P) prazo de controle: costura da 4.1;
  - (C) orçamento de CPU ou tempo: 4.3.

## 5. Corte em itens (até 150 linhas e 10 arquivos cada; agente e arquivos)

| Item | Agente | O quê | Arquivos | Depende de |
|---|---|---|---|---|
| Q0 | security-engineer | Modelo de ameaças da quarentena (quem escreve a lista, leitura da lista no head ou na base, D6) e da costura do relógio | `docs/security/ameacas/bp1-quarentena.md` | — |
| Q1 | tech-lead | Formato e leitor puro (`carregar`, `validar`, `ativas(hoje)`, `vencidas`), com data injetada nos testes | `bin/forge_quarentena.py` (~80), `tests/test_forge_quarentena.py` (~70), `tests/quarentena.json` (vazio), `changelog.d/` | Q0 |
| Q2 | tech-lead + devops-engineer | O runner exclui as ativas, conta como pulados e mantém a completude | `scripts/suite-paralela.py`, `scripts/suite-partes.py`, `tests/test_suite_partes.py`, `tests/test_suite_paralela.py`, `changelog.d/` | Q1 |
| Q3 | tech-lead + security-engineer | Catraca: entrada nova pede rótulo; teto sobe só com entrada nova e desce com a saída; `teto_quarentena`; mutantes nos ramos de falha (AR-1, AR-2) | `tests/catraca.py`, `tests/test_catraca.py`, `tests/config.json`, `tests/mutantes/bp1-catraca.json`, `changelog.d/` | Q1 (paralelo a Q2) |
| Q4 | tech-lead | `forge-check quarentena propor/ler`, aviso no `proximo`, `forge-testes --repetir` | `bin/forge-check`, `bin/forge_quarentena.py`, `bin/forge-testes`, `tests/test_forge_check_quarentena.py`, `tests/test_forge_testes.py`, `changelog.d/` | Q2, Q3 |
| Q5 | devops-engineer | Job `quarentena (informativa)`, fora dos agregadores; hash do `run` em `tests/test_ci_local.py` | `.github/workflows/ci.yml`, `tests/test_ci_local.py`, `changelog.d/` | Q2 |
| Q6 | tech-lead (parecer do security-engineer) | Costura `relogio`/`armar` no `_comum`; AST do `__main__` e do driver sem a costura; mutante | `hooks/_comum.py`, `tests/test_hooks.py`, `tests/test_hooks_volta_corpus.py`, `tests/mutantes/bp1-costura.json`, `changelog.d/` | Q0 (paralelo a Q1 a Q5) |
| Q7 | tech-lead + qa-engineer | S1 em duas provas (4.2), sem asserção a menos | `tests/test_hooks.py`, `tests/fixtures/hooks/parecer/*` (até 3), `changelog.d/` | Q6 |
| Q8 | qa-engineer, depois tech-lead | Corpus: contador determinístico e CPU informativa (só com D5 = a) | `tests/apoio_volta_unica.py`, `tests/test_hooks_volta_corpus.py`, `tests/test_medida_cpu.py`, `.github/workflows/ci.yml` (resumo), `changelog.d/` | D5, Q6 |
| Q9 | qa-engineer + tech-lead | Guarda estática do tempo real e `tempo_real_permitido` (só cai); regra da catraca | `tests/test_tempo_nos_testes.py`, `tests/config.json`, `tests/catraca.py`, `tests/test_catraca.py`, `changelog.d/` | Q3 |
| Q9.n | tech-lead | Conversão por classe (R, S, P, C), um cartão por classe; cada um tira linhas da lista | até 10 arquivos de `tests/` por item | Q9 |
| Q10 | tech-lead | Textos neutros: `agents/qa-engineer.md:27` (exceção da quarentena), `skills/qa-testing/SKILL.md` (quarentena e tempo nos testes), `templates/projeto/docs/engineering/praticas.md`, `docs/regras/R-QA.md` (uma linha com o ID, se o dono aprovar a D7) | 4 a 5 arquivos | Q3, D7 |

Ordem e paralelo:
- Q0 primeiro.
- Depois, Q1 e Q6 em paralelo.
- Depois de Q1: Q2 e Q3 em paralelo.
- Depois: Q4 e Q5. Q7 sai depois de Q6.
- Q8 sai depois da D5. Q9 depois de Q3; Q10 por último.
- Cada item deixa a suíte verde sozinho.
- O `qa-engineer` dá parecer em todos; o `security-engineer`, em Q3, Q6 e Q9 (controle e hook).

**Modelo de projeto (neutro).** O formato do registro, as regras (prazo, OK, teto, cartão, voltar ao portão) e a guarda de tempo valem para qualquer stack. A exclusão por id e a contagem de pulados dependem do runner de cada linguagem e ficam em `stacks/<nome>/pronto.md` (ADR 0001), sem framework fixo no núcleo. A chegada aos projetos é pela migração da ADR 0005 (D8).

## 6. Riscos

| Risco | Efeito | Mitigação |
|---|---|---|
| Quarentena vira depósito (Fowler) | Defeito real escondido | Teto de entradas (D2); prazo de 7 dias com volta automática ao portão; job informativo segue medindo; cartão obrigatório |
| Teste com defeito real tratado como instável | Defeito escapa | A prova exige falha e verde na mesma árvore; teste que falha sempre não entra; OK do dono por teste |
| Autor põe entrada para ficar verde | Afrouxa sem OK | A catraca barra entrada nova sem rótulo e declaração da ADR 0018; o runner que lê o head só deixa a parte verde, não o merge (D6, Q0) |
| Costura de relógio vira desvio do vigia | Hook libera depois do prazo | Só por palavra-chave e em processo, sem variável nem argumento; AST do `__main__` e do driver; mutante; parecer de segurança (Q6) |
| Prova pequena com relógio falso diverge do sinal real | Falso verde | Mantém uma prova real na direção robusta (4.2) |
| Data do runner errada | Entrada vence cedo ou tarde | Vencer cedo só aperta; tarde fica limitado pelo prazo de 7 dias e pelo relógio do runner do GitHub. O relógio local do Forge já é conferido (RELOGIO-WSL). |
| Contador determinístico (D5 = a) não acompanha o custo real | Regressão de desempenho passa | CPU segue medida e publicada, com alarme por tendência; a D5 tem reversão |
| BP2 (fila de merge) muda o mesmo agregador | Conflito de desenho | Q5 fica fora dos `needs`; o PR de quarentena é também o caminho de conserto da develop que a BP2 trata |

## 7. Decisões do dono (a de maior peso primeiro, com recomendação)

1. **D1, o que é "automática".**
   - (a) Detecção, entrada, cartão, branch e PR são automáticos. O teste só sai do portão com o merge do PR com rótulo e `A-<n>` da ADR 0018 para aquele PR (um teste por PR); a autorização permanente de 19/11 13:08 não cobre.
   - (b) O teste pula na hora por até 24 h e o OK vem depois.
   - **Recomendo (a).** A (b) afrouxa sem OK, contra o risco que o próprio estudo registra.
2. **D2, teto.**
   - (a) A quarentena conta no `teto_pulados` (sobe 1 por entrada no PR com o OK, desce na saída), com `teto_quarentena` = 3 entradas ao mesmo tempo.
   - (b) Teto separado, sem mexer no `teto_pulados`.
   - **Recomendo (a)**: o teto que já vale continua a ser o único total de pulados. Com o 3, a quarentena fica abaixo do exemplo de Fowler (8) para uma suíte de cerca de 1.200 testes.
3. **D6, de onde o runner lê a lista.**
   - (a) Do head do PR: o PR de quarentena fica verde, e a catraca barra o merge sem rótulo e autorização.
   - (b) Da base, como `testes_fora_do_ci`: o PR de quarentena fica vermelho até o merge e depende do conserto com a develop vermelha (BP2).
   - **Recomendo (a)**, condicionada ao parecer do `security-engineer` na Q0.
4. **D3, prazo e vencimento.**
   - (a) Prazo de 7 dias, uma prorrogação com OK novo; a entrada vencida volta sozinha ao portão.
   - (b) A entrada vencida reprova todo PR até a decisão.
   - **Recomendo (a)**: só aperta e não trava o time inteiro.
5. **D5, orçamento de CPU do corpus.**
   - (a) O portão passa a contador determinístico, e os segundos de CPU ficam informativos com alarme. Afrouxa: sim, PROP-TEMPO-CPU (2026-10-27) e `test_corpus_nos_dois_hooks`.
   - (b) Fica como está e entra em quarentena quando falhar.
   - **Recomendo (a)**, se o contador da Q8 reprovar um mutante de custo (texto que dobra o trabalho do analisador). Sem isso, (b).
6. **D4, costura de relógio no hook.** O `_comum.executar` ganha `relogio` e `armar`, só por palavra-chave, como em 4.1. Os hooks estão em vigor e são do dono (`R-CONFORMIDADE`). **Recomendo sim**, com o parecer de segurança da Q6.
7. **D7, textos.** `agents/qa-engineer.md:27` ganha "salvo pela quarentena com OK do dono e prazo (`tests/quarentena.json`)". `R-QA` ganha uma linha com o ID. Afrouxa: sim, texto de controle. **Recomendo sim**: sem isso o texto do agente contradiz o mecanismo.
8. **D8, projetos.** Os projetos recebem a BP1 pela migração da ADR 0005 depois de 14 dias de uso no Forge, ou junto. **Recomendo depois de 14 dias**, com a medida da seção 8.

Para cada recusa ou adiamento, quem propõe registra na linha `DECISÃO DO DONO` o "reabre se":
- D1 (b) recusada: reabre se a develop ficar vermelha mais de 2 vezes numa semana com o OK pendente;
- D5 (a) recusada: reabre se o teto de CPU do corpus pedir rerun 2 vezes em 7 dias.

## 8. Critério de reversão e medida
- **Medida**, pelo placar e pelos resumos do CI, nos 30 dias depois da Q5:
  - vezes que a develop ficou vermelha por teste de tempo ou carga (base: 4 em 30 h);
  - PRs segurados por teste alheio (base: 4);
  - entradas abertas, vencidas e consertadas.
- **Reverter a quarentena se**:
  - um defeito escapar para a `main` coberto por teste que estava em quarentena; ou
  - mais da metade das entradas vencerem sem conserto em 30 dias (a quarentena virou depósito).
- **Reverter a D5 (a) se** uma regressão de CPU acima de 20% chegar à develop sem o contador reprovar.

## 9. Por que o existente não basta (mecanismos novos: registro, `forge-check quarentena`, job informativo, guarda de tempo, costura)
- **Rerun com OK do dono** (o que existe): custou um OK em 19/11 14:59 (run 44574989031) e não deixa rastro, prazo nem cartão; o próximo vermelho pede outro OK.
- **`testes_fora_do_ci`**: tira um **arquivo** inteiro do CI, sem prazo e sem contar no teto de pulados. A granularidade e a duração estão erradas para um teste instável.
- **`skip` no código**: a catraca o conta como enfraquecimento. Fica no fonte sem prazo, e ninguém o tira quando o motivo some.
- **PRAZO-CARGA** (`carga_explica_a_recusa`): tolerância depois do fato, que a literatura (Google, cap. 14) aponta como o padrão que falha quando o runner enche. O S1 com 2,5% de folga seguiu instável depois dela.
- **`mock.patch` do `_relogio` no teste**: não alcança o subprocesso do hook, onde a decisão roda (seção 2, "Where to patch").
- **Nenhuma guarda impede tempo real novo**: 242 chamadas em 57 arquivos, sem lista nem catraca.

Evidência de execução: o run 44574989031 (180,55 contra 180), a DECISÃO DO DONO de 19/11 14:59 e as 4 develops vermelhas em 30 h do estudo de 19/11.

## Critério de parada
- bloqueia: develop vermelha por teste cuja falha não se repete na mesma árvore, sem caminho com prazo e OK, e teste cuja decisão depende do relógio real da máquina
- Q-ENTRADA · entrada nova, alterada ou prorrogada em `tests/quarentena.json` sem rótulo e sem declaração da ADR 0018 que cubra o PR · oráculo: `python3 -m unittest tests.test_catraca` (casos novos da Q3)
- Q-TETO · pulados mais quarentena ativa acima do `teto_pulados`, entradas acima do `teto_quarentena`, teto que não desce na saída · oráculo: `python3 -m unittest tests.test_suite_partes tests.test_suite_paralela tests.test_catraca`
- Q-PRAZO · entrada vencida ainda excluída, ou entrada ilegível que exclui · oráculo: `python3 -m unittest tests.test_forge_quarentena` (data injetada)
- Q-APAGA · teste em quarentena cujo `def` some ou sai do discover · oráculo: `python3 -m unittest tests.test_catraca` (regra I7b com caso novo)
- R-COSTURA · `relogio` ou `armar` passados pelo `__main__` de um hook, pelo driver do lote ou por qualquer entrada externa · oráculo: `python3 -m unittest tests.test_hooks_volta_corpus` (AST do driver estendida) e mutante da Q6 por `bin/forge-mutante`
- R-SONO · chamada nova de tempo real em `tests/*.py` fora de `tempo_real_permitido` · oráculo: `python3 -m unittest tests.test_tempo_nos_testes`
- gatilho · oráculo: `python3 -m unittest tests.test_catraca tests.test_forge_quarentena tests.test_tempo_nos_testes tests.test_hooks_volta_corpus`

## Leituras
| Arquivo | Para quê |
|---|---|
| `docs/propostas/boas-praticas-1911.md` | BP1, números e riscos |
| `tests/catraca.py:516-565, 653-760` | Contagem de `skip`, `testes_fora_do_ci`, `teto_pulados` |
| `.github/workflows/ci.yml` | Partes, teto de pulados, agregadores, resumo PRAZO-CARGA |
| `tests/test_hooks.py:105, 1189-1323` | `_relogio`, `liberar_ou_provar_a_carga`, S1 |
| `tests/test_hooks_volta_corpus.py:84-128`, `tests/apoio_volta_unica.py:77-115` | Driver do lote, teto de CPU do corpus |
| `hooks/_comum.py:2800-2895` | Vigia de prazo e `executar` |
| `docs/adr/0018-autorizacao-do-dono-gravada.md` | OK do dono por PR |
| `docs/regras/R-CONFORMIDADE.md`, `docs/regras/R-TETO.md`, `agents/qa-engineer.md:27` | Controles e texto afetados |
