# PR-VERDE-DE-PRIMEIRA: PR verde na 1.ª execução do CI, de ~57% para 85%

Pedido PR-VERDE-DE-PRIMEIRA (ordem do dono de 20/11 10:41, registrada no v0478), etapa E54.2. Só desenho: nenhum código, nenhum workflow nem hook alterado. Público: o dono (decisões da seção 5), o `tech-lead` e o `devops-engineer` (corte da seção 4), o `security-engineer` (gatilhos: CI, catraca, hook, autorização) e o `qa-engineer`. Neutro (`R-NEUTRO`, ADR 0001): vale para o Forge e para os projetos; nos projetos, os comandos vêm do `stacks/<nome>/pronto.md` e do `CLAUDE.md` deles. Regras citadas só pelo ID.

## 1. Problema medido

**Medida do Controlador (de partida):** desde 17/11, 52 de 121 execuções de CI de PR vermelhas (43%); cada branch roda o CI cerca de 4 vezes; PR verde na 1.ª execução: ~57%. Meta: 85%.

**Causas, na ordem do Controlador, e o que já existe para cada uma (conferido no código desta base):**

| # | Causa | O que existe hoje | Por que não basta (evidência) |
|---|---|---|---|
| 1 | Catraca esperando o rótulo `afrouxa-regra`, que "cai" a cada envio | O rótulo do dono vale se aplicado depois do último push ou se os arquivos vigiados e o diff efetivo são os do head rotulado (P9, `tests/catraca.py:1115` e `:1209`). A concessão gravada do dono (ADR 0018) cobre `pr:N` e é lida só no hook local e, quando a G1.4 entrar, no corpo do PR | O rótulo é um **evento posterior** à abertura do PR: a 1.ª execução da catraca (`opened`) roda sempre sem ele e fica vermelha em todo PR que afrouxa ou aperta controle (a catraca não distingue). E o PR que muda arquivo vigiado depois do rótulo perde o rótulo (`protegidos_como_no_rotulo`), justamente o caso dos PRs de controle. A concessão `pr:N` só existe depois de o PR ter número, logo depois da 1.ª execução |
| 2 | Testes que dependem de tempo ou carga | BP1 (quarentena com relógio injetado; absorveu a TESTES-PRAZO-VARREDURA) | Fora deste pedido; é dependência da meta (seção 6, R1) |
| 3 | Índices, mapas e contagens desatualizados (casos de 20/11: teto de caracteres de agente, specs de mutante com `de` fora da fonte, índice do Forge, mapa do `forge-testes`, peso de módulo novo em `tests/pesos-d4.json`, tipo do changelog) | Geradores e conferências soltos: `scripts/indice-forge.py --conferir`, `bin/forge-testes --texto` (mapa e orçamentos de texto), `bin/forge-changelog conferir` (este já no envio), `scripts/suite-paralela.py --medir` (peso). O envio local roda só as checagens baratas (`.githooks/pre-push:338`, ENVIO-LEVE) | Só o changelog está no envio. Índice, mapa, orçamento, pesos e specs só se conferem no CI (o `--texto` é opt-in, à mão). Nenhuma ferramenta regera o derivado na entrega: o autor descobre no CI e faz um envio a mais |
| 4 | Registros compartilhados entre PRs paralelos | O changelog já é dividido por item (`changelog.d/`); o índice já tirou contagens para não enfileirar trilhas (review A1 de v0478, `scripts/indice-forge.py:8`) | Restam registros globais com limite somado: a regra de no máximo 20% de módulos sem peso (`tests/test_forge.py:7237`), as specs de mutante varridas contra a fonte atual (AR-12, 5 vezes) e os tetos de `docs/regras/orcamento.json`. Dois PRs verdes sozinhos ficam vermelhos juntos, e o vermelho cai no PR que chega depois |
| 5 | Python 3.12 × 3.14 | O CI roda as duas versões (`.github/workflows/ci.yml`, jobs `partes-doze` e `partes-quatorze`) | O autor roda, quando roda, só o `python3` da máquina; a diferença aparece no CI |

**Medida que falta:** o `bin/forge-placar` mede a primeira rodada dos **pareceres** (`primeira_rodada`, `bin/forge-placar:613`), não a do CI. A medida de 57% foi feita à mão pelo Controlador. Sem medida por ferramenta não há leitura da meta nem critério de reversão; o item M1 vem primeiro.

## 2. Opções e recomendação

### PV-A: OK do dono gravado e preso ao commit, lido pela catraca
- **A-a (recomendada): arquivo de autorização versionado na branch, preso ao commit revisado.** O dono dá o OK antes de o PR abrir, citando o item com marcador (`item <CARTAO>`). O `forge-check autorizacao gravar` (SIEG-G1, G1.2) grava a concessão com o alvo `item:<CARTAO>` e o campo `Commit: <sha40>`, que precisa ser o head com os pareceres aprovados. O `declarar` escreve a cópia da concessão (mensagem inteira, `Sha256`, `Commit`, `Ramo`, validade) num arquivo da branch, numa pasta que só o subcomando grava (proteção por caminho no hook, como as pastas de parecer). A catraca lê esse arquivo **do head** e libera pelas mesmas funções do P9, com o `Commit` gravado no lugar do commit do rótulo: arquivos vigiados ou diff efetivo iguais aos do commit, nenhuma violação nova. O PR abre já com o arquivo, e a 1.ª execução fica verde. Envio que não muda o conteúdo vigiado não derruba o OK; envio que muda pede OK novo, como hoje.
- **A-b: declaração no corpo do PR na criação** (ADR 0018 item 10, com o alvo `item:` em vez de `pr:N`). Mesmo efeito na 1.ª execução, sem commit a mais. Contra: a barreira local teria de analisar o texto do `gh pr create|edit --body`, a classe com mais burlas registradas (AR-11, AR-13, AR-14, AR-15); a proteção por caminho é a forma já provada.
- **A-c: manter o rótulo e aplicá-lo na criação do PR** (`--label`). Não resolve: o evento `labeled` chega depois do `opened`, e o envio que muda arquivo vigiado continua derrubando o rótulo.
- **Recusada: catraca neutra ou pulada sem rótulo** (job com `if:` ou conclusão `neutral`). Check exigido pulado ou neutro conta como passado na proteção de branch do GitHub: afrouxa o portão (`R-CONFORMIDADE`).

A-a reabre uma alternativa que a ADR 0018 recusou ("registro versionado no repositório"). O motivo da recusa era a origem: o CI não distingue a conta do dono da conta dos agentes. Isso continua valendo e continua limite declarado (o CI confere forma, coerência e conteúdo; a origem só se confere na camada local). O motivo novo é **tempo e conteúdo**: o OK precisa existir antes da 1.ª execução e ficar preso ao commit, não ao evento. Por isso é emenda da ADR 0018 e da ADR 0008 (seção 3), com decisão do dono (D1, D2).

**Junto com SIEG-G1 e AE7:** o PV-A depende da G1.2 (gravar) e substitui, para o rótulo, a G1.4 (declaração no corpo). A AE7 ("só aperta" medido pelo HOOK-COMPARA-BASE) entra como dado no arquivo de autorização: o `declarar` grava a medida do "só aperta" do commit, para o dono e a segurança lerem; ela não dispensa o OK (isso é a AUTONOMIA-POR-HISTORICO, adiada pelo dono).

### PV-B: a ferramenta regera e o envio confere em segundos
- **B-a (recomendada): uma conferência de registros só de leitura, rodada no envio, e um regerador separado, rodado pelo autor antes da entrega.** A conferência junta o que já existe (índice `--conferir`, mapa e orçamentos do `--texto`, specs de mutante dos arquivos tocados, módulo de teste novo sem peso, changelog) num comando com orçamento de tempo medido. O regerador chama os geradores que já existem só para os derivados cuja fonte o diff tocou, numa lista fechada, e mostra o diff para o autor commitar. O `forge-check entrega` passa a cobrar a conferência verde (só lê o log, forma META85). O `forge-check` segue só leitura.
- **B-b: o CI regera e commita na branch.** Precisa de token com escrita no CI (gatilho de segurança, `R-SEGURANCA`) e faz um commit de robô a cada PR, o que derruba a P9 e o OK do PV-A. Recusada.
- **B-c: só texto ("rode o `--texto` antes")**. É o estado de hoje; os seis casos de 20/11 passaram por ele.

### PV-C: registros compartilhados sem conflito entre PRs
- **Pesos (recomendada C-a):** o PR não edita `tests/pesos-d4.json` à mão. Módulo novo sem peso vale a mediana (já é assim na divisão); a regra global de 20% vira regra por PR: "o PR não aumenta o número de módulos sem peso além dos que ele cria e mede com `--medir`" e a regeração dos pesos pelos tempos do CI (`scripts/pesos-do-ci.py`, já existe) passa a ser passo da marca de versão, uma vez por versão. Alternativa C-b, pesos divididos por módulo (um arquivo por módulo): resolve o conflito textual, mas não o limite somado e cria cerca de 150 arquivos. Recusada.
- **Specs de mutante:** quem muda a linha atualiza a spec (como pede o AR-12); a conferência do PV-B acha, em segundos, toda spec cujo `arquivo` o diff tocou e cujo `de` deixou de ocorrer exatamente uma vez. Recusada: validar a spec só contra o commit do item dela (spec antiga deixaria de provar algo; afrouxa `R-QA`).
- **Tetos somados (orçamento de agente, teto de pulados):** a conferência do PV-B roda contra a `origin/develop` atual (busca antes), e a fila de merge da BP2 (re-teste quando a base andou, decisão do dono de 20/11 07:47, D3) pega o que dois PRs juntos passam. Nada novo aqui além do item B1.
- **Índice:** continua versionado (o brief o cita); muda só quando arquivo entra ou sai, e o regerador do PV-B o refaz depois do rebase.

### PV-D: o autor roda os testes afetados no 3.12 e no 3.14
- **D-a (recomendada): na entrega, não no envio.** O plano dos afetados (`bin/forge-testes --afetados`) roda uma vez por versão de Python declarada (no Forge, as do CI; nos projetos, as do `pronto.md` da stack), em série, pela fila pesada (`R-TETO`), e grava um log por versão na forma META85 (`head=` e `rc=`). O `forge-check entrega` cobra os logs. O envio continua leve (ENVIO-LEVE, decisão do dono de 11/11).
- **D-b: no envio** (`FORGE_PREPUSH_SUITE`). Contraria o ENVIO-LEVE e dobra a carga a cada envio; recusada.
- Intérprete ausente: o cartão de ambiente (AMBIENTE-SOBREVIVE-RECRIACAO) instala as duas versões ao subir o container, sem custo (`R-CUSTO`). Enquanto não instala, D5.

## 3. Por que o existente não basta (mecanismos novos)
- **Campo `Commit` e alvo `item:` na concessão; pasta de autorização na branch (PV-A):** o rótulo e a concessão `pr:N` existem e foram lidos (`tests/catraca.py:1104`, ADR 0018 item 9); os dois só passam a existir depois da 1.ª execução, que é o que a meta mede. Evidência: causa 1 da medida, a primeira do Controlador.
- **Conferência de registros e regerador (PV-B):** os geradores e conferências existem (tabela da seção 1), mas soltos e fora do envio; os seis casos de 20/11 chegaram ao CI.
- **Medida de CI na 1.ª execução (M1):** o placar só mede a primeira rodada de pareceres (`bin/forge-placar:613`).
- Nada novo em PV-C além da regra de pesos por PR, que troca o texto de um teste (D4).

## 4. Corte em itens (até 150 linhas de código e até 10 arquivos cada; testes, specs e fragmento contam nos arquivos)

| Item | Papel | Arquivos | Linhas (código) | Depende de | Casos de abuso que cabem ao item |
|---|---|---|---|---|---|
| M1 medida | tech-lead + qa | `bin/forge-placar`, um módulo de teste, spec de mutante, fragmento (4) | ~90 | — | execução cancelada contada como verde; 1.º head errado (PR reaberto, branch reescrita); workflow fora da lista dos exigidos contado; resposta da API ilegível vira verde (falha fechada: sai `lacuna`) |
| A1 ADR | software-architect + security | emenda da ADR 0018 e da ADR 0008 seção 3 (2) | 0 | D1, D2 | — (o parecer de segurança registra o modelo de ameaças dos itens A2 a A5) |
| A2 concessão presa ao commit | tech-lead + security + qa | `bin/forge_autorizacao.py`, módulo de gravar da G1.2, testes, spec, fragmento (5) | ~110 | A1; SIEG-G1 G1.2 na develop | alvo `item:` sem marcador ou fora da frase do ato (A2 da ADR 0018); `Commit` que não é o head com os pareceres aprovados; `Commit` abreviado ou de outra branch; mensagem com ressalva nascendo ativa |
| A3 declarar em arquivo | tech-lead + security + qa | `bin/forge-check` (subcomando), `hooks/conformidade.json` (caminho protegido nas três grafias, `quem: []`), testes, spec, fragmento (5) | ~80 | A2 | escrita direta por Write, Edit ou Bash (`find -delete`, `tar`, `cp`, link) na pasta; arquivo de autorização copiado de outro item; `python3` sem `-I` (AR-5); pasta do git diferente da do Bash (AR-7) |
| A4 catraca lê o arquivo | tech-lead + devops + security + qa | `tests/catraca.py`, `tests/test_catraca.py`, spec, fragmento (4) | ~120 | A3 | arquivo já presente na base (não vale, como a spec da base); `Ramo` diferente do PR; `Commit` cujo conteúdo vigiado difere do head; validade vencida no instante da execução; `Sha256` que não bate; link ou arquivo não comum; verde sem o texto fixo "forma conferida; origem só na camada local"; custo (`R-CUSTO`) liberado pelo arquivo (não pode, como o rótulo). Nota: a catraca roda o script da base, então o primeiro PR que usa o arquivo é o seguinte ao A4 |
| A5 abrir o PR depois do OK | tech-lead + qa | `bin/forge-fechar`, `agents/tech-lead.md`, testes, fragmento (4) | ~70 | A4, D3 | PR aberto com violação liberável e sem arquivo de autorização; catraca local que não consegue rodar tratada como "sem violação" (falha fechada: não abre) |
| B1 conferência de registros | tech-lead + qa | `bin/forge-testes` (modo de registros), testes, spec, fragmento (4) | ~120 | — | conferência que grava algo (só leitura); ambiente do CI herdado no teste (AR-4); spec tocada e não conferida; base local velha (busca a `origin/develop` antes; sem rede, aviso, o CI confere) |
| B2 regerador | tech-lead + qa | `bin/forge-testes` (modo de regerar) ou script próprio, testes, fragmento (3 a 4) | ~90 | B1 | escrita fora da lista fechada de derivados; seguir link; regerar arquivo de controle (`tests/config.json`, `docs/regras/`) |
| B3 envio confere | devops (patch) + security | `docs/devops/v0479-pv-b-pre-push.patch` e o documento dele, com o comando exato de aplicar e de testar (2); o dono aplica (arquivo em vigor, ordem de 18/11 13:18) | ~25 no patch | B1, D6 | ferramenta presente com saída fora de 0 e 1 tratada como verde (aviso e segue só quando ausente, como as checagens de hoje); conferência que pula as checagens que já existem; `--no-verify` |
| B4 entrega cobra | tech-lead + qa | `bin/forge-check` (entrega), gerador do brief, testes, fragmento (4) | ~60 | B1, META85-ENTREGA-COM-MUTANTES | log de outro head; `rc=` diferente de 0 aceito; log ausente aceito na etapa `codigo` |
| C1 pesos por PR | tech-lead + qa | `tests/test_forge.py` (classe dos pesos), `scripts/suite-paralela.py` (só a mensagem), `skills/` da release (passo de regerar os pesos), fragmento (4) | ~40 | D4 | PR que tira peso de módulo existente; módulo novo sem medida aceito; regra global sumindo sem a regra por PR |
| D1 afetados por versão | devops + qa | `bin/forge-testes` (versões), configuração das versões, testes, fragmento (4) | ~100 | B1 (mesmo arquivo: em série) | versão lida do ambiente do comando em vez da configuração; intérprete ausente tratado como verde; duas baterias ao mesmo tempo (fila pesada, `R-TETO`) |
| D2 entrega cobra as versões | tech-lead + qa | `bin/forge-check` (entrega), testes, fragmento (3) | ~40 | D1, B4 (mesmo arquivo: em série) | um log só para as duas versões; log de versão que não está na configuração |
| D3 modelo de projeto | tech-lead | `templates/projeto/` (texto do `CLAUDE.md` e do hook do modelo: comando de conferência de registros e versões de Python vindos do projeto), `stacks/*/pronto.md` (campo das versões) (até 6) | ~30 | B3, D1 | termo de projeto ou stack fixa no núcleo (`R-NEUTRO`) |

**Paralelismo (uma trilha por arquivo):** M1, A1, B1 e C1 começam juntos. A2 → A3 → A4 → A5 em série (mesma cadeia). B2 e D1 dividem `bin/forge-testes` com B1: em série depois dele. B4 e D2 dividem `bin/forge-check` entre si e com A3: em série. B3 sai assim que o B1 entra. QA escreve os testes a partir do cartão em paralelo ao autor (ordem do dono de 19/11 14:52); parecer de segurança em A2, A3, A4, B3 e D1 (gatilhos: autorização, hook, CI, catraca).

## 5. Decisões que dependem do dono (`R-DECISAO`)
- **D1. Forma do OK preso ao commit.** a) arquivo de autorização versionado na branch, alvo `item:<CARTAO>` e `Commit:` do head revisado, lido pela catraca no head (recomendo: verde na 1.ª execução e barreira por caminho, a forma já provada); b) declaração no corpo do PR na criação, com o mesmo alvo; c) manter o rótulo. Afrouxa? Não: a liberação continua exigindo concessão do dono e conteúdo igual ao revisado. Mas troca o texto de controle da ADR 0008 (seção 3) e da ADR 0018 (itens 2, 10 e Alternativas): "sim, troca de texto de controle", por isso vem ao dono.
- **D2. O rótulo depois do PV-A.** a) a catraca aceita o arquivo e o rótulo por 14 dias depois de o A4 entrar; depois, só o arquivo (recomendo: aperta, porque o rótulo sozinho deixa de liberar, e a transição não trava PR em curso nem promoção); b) os dois para sempre.
- **D3. Abrir o PR só depois do OK** quando a catraca local acusa violação liberável. Recomendo sim: sem isso a 1.ª execução segue vermelha nesses PRs. Custo: o pedido do OK sai antes do PR, com o head revisado e o motivo em uma linha.
- **D4. Pesos: trocar a regra global de 20% sem peso pela regra por PR** e regerar os pesos na marca de cada versão. Recomendo sim. Afrouxa? Aperta no PR (nenhum módulo novo sem medida), mas troca o texto de um teste: a catraca pode pedir o rótulo; vale a autorização do dono para o que só aperta, com a confirmação escrita da segurança.
- **D5. Intérprete ausente na máquina do autor.** a) a entrega fica pendente até o cartão de ambiente instalar as duas versões (recomendo, depois do AMBIENTE-SOBREVIVE-RECRIACAO); b) só aviso.
- **D6. Aplicar o patch do envio (B3).** É ação do dono, no molde do PP1 e da A3: o `devops-engineer` entrega o patch, o comando de aplicar e o de testar.
- **D7. Definição da medida.** PR verde na 1.ª execução = no 1.º head do PR, a 1.ª execução de cada workflow exigido (CI e Catraca) termina `success`; cancelada por envio novo não conta como verde nem como vermelha; PR do dependabot fora. Recomendo esta, lida pelo M1 por dia e por semana.

## 6. Riscos e reversão
- **R1. A meta depende da causa 2**, fora deste pedido (BP1). Com o PV inteiro entregue e os testes de tempo ainda instáveis, a meta pode não chegar a 85%. O M1 separa o vermelho por job, para a leitura não atribuir ao PV o que é da BP1.
- **R2. Arquivo de autorização forjado por agente com a conta do dono.** Limite já declarado na ADR 0018: o CI confere forma, coerência e conteúdo, não origem. A barreira é o caminho protegido (A3) e a trava de escrita do sandbox (A3 da v0478); a segurança confirma por escrito antes do A4.
- **R3. Envio mais lento.** A conferência do B1 tem orçamento medido (meta: p95 abaixo de 20 s na máquina do time, medido no próprio item); passou, o item corta a conferência mais lenta para o CI e registra.
- **R4. Carga da máquina com duas versões de Python.** O D1 roda pela fila pesada e em série; com a carga acima do limite da ordem do dono de 20/11 07:55, espera.
- **R5. Transição do rótulo (D2).** PR em curso com rótulo segue valendo nos 14 dias; promoção (S-16) idem.

**Critério de reversão:** se, 14 dias depois do A4 e do B3 na `develop`, o M1 mostrar PR verde na 1.ª execução abaixo de 70% com a fatia da catraca e dos registros acima de 10% dos vermelhos, ou houver 1 caso de catraca verde por arquivo de autorização cujo conteúdo vigiado difere do `Commit`, o item correspondente volta ao desenho: o A4 sai (a catraca volta ao rótulo, que continua aceito na transição) ou a conferência do B1 sai do envio, sem tirar a conferência do CI.

## 7. Critério de parada
- bloqueia: catraca verde sem concessão do dono que cubra o item e o conteúdo vigiado do head; arquivo de autorização gravado fora do subcomando; envio com registro desatualizado que a conferência acharia; entrega de código sem os logs das versões de Python
- ok-sem-conteudo · arquivo de autorização aceito com `Commit` cujos arquivos vigiados ou diff efetivo diferem do head, com `Ramo` de outro PR, já presente na base, vencido, com `Sha256` que não bate ou link · oráculo: python3 -m unittest tests.test_catraca
- escrita-direta · escrita por Write, Edit ou Bash na pasta de autorização fora do subcomando, em qualquer grafia · oráculo: python3 -m unittest tests.test_conformidade_autorizacao
- concessao-solta · concessão de alvo `item:` sem marcador, fora da frase do ato, ou com `Commit` que não é o head com os pareceres aprovados · oráculo: python3 -m unittest tests.test_autorizacao_gravar
- registro-no-ci · índice, mapa, orçamento, spec de mutante do arquivo tocado, módulo novo sem peso ou changelog que o CI reprova e a conferência de registros aprova · oráculo: python3 -m unittest tests.test_testes_tocados
- versao-faltando · entrega de código aceita sem o log de uma das versões de Python declaradas, ou com log de outro head ou `rc` diferente de 0 · oráculo: python3 -m unittest tests.test_selo_e_entrega
- gatilho · oráculo: python3 -m unittest tests.test_catraca tests.test_conformidade_autorizacao tests.test_autorizacao_gravar tests.test_testes_tocados tests.test_selo_e_entrega

Os módulos `tests.test_autorizacao_gravar` e `tests.test_conformidade_autorizacao` ainda não existem nesta base: nascem na G1.2 e na G1.3 do SIEG-G1 (ADR 0018, Critério de parada), das quais o A2 e o A3 dependem. Até lá, essas duas classes não têm oráculo executável, e o A2 não começa.

## 8. Fora deste desenho
- Testes de tempo e carga (BP1); fila de merge (BP2); autonomia por histórico (adiada pelo dono); prova de origem no CI (token separado para os agentes, acesso do dono, ADR 0018).
