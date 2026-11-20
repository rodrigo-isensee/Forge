# AE2 (o quadro anda com os PRs) e CONTADOR-DA-VERSAO (pedido v0478, E54.1)

Desenho antes do código, pedido MELHORIAS-ANTI-ERRO (item AE2) e cartão CONTADOR-DA-VERSAO (diretriz 37; ordens do dono
de 20/11 08:44, 09:45 e 09:56 no `## Histórico` do v0478). As duas coisas usam **a mesma contagem**: "quais cartões foram
entregues por PR mesclado na develop desde a marca". O AE2 grava essa contagem no quadro; o contador a lê e a resume.

Neutro (`R-NEUTRO`, ADR 0001): vale para o Forge e para todo projeto. Nada aqui cita stack, projeto ou nome de cartão
real; o que muda entre o Forge e um projeto é só onde está o quadro (no Forge, a pasta de controle, passada por
`--raiz-pedidos`; no projeto, a raiz do repositório), que o `forge-check` já resolve. Custo: só `git` local e arquivos
(`R-CUSTO`); nenhuma chamada ao GitHub é obrigatória.

**Afrouxa:** não. Todos os itens acrescentam cobrança (citação do cartão no PR, nascimento pela ferramenta, linha do
contador medida) ou automatizam um registro que hoje é manual; nenhum texto de `docs/regras/`, item de
`tests/config.json` ou controle sai ou muda de sentido.

## 1. Problema medido

Fonte: cabeçalho do `KANBAN.md` e `## Histórico` do v0478 na pasta de controle (números copiados de lá, não recontados).

| Data | Fato registrado | O que mostra |
|---|---|---|
| 16/11 21:46 (E2.522) | 19 cartões entregues ainda em colunas abertas, achados cruzando o quadro com a develop | o merge não move o cartão |
| 18/11 13:10 (E11.1) | 55 cartões entregues até a 0.47.7 saíram para Pronto numa faxina | idem, acumulado por dias |
| 19/11 21:55 (E11.2) | 22 cartões entregues e abertos; 90 cartões sem linha no histórico; 8 colunas divergentes; `forge-check kanban` "sem divergência de coluna" na mesma rodada | o `kanban` atual não vê cartão entregue aberto nem cartão sem histórico |
| 20/11 08:44 (ordem do dono) | 10 cartões abertos às 8h30 sem linha no histórico; para a ferramenta, um deles continuava Pronto | o cartão nasce à mão, fora da ferramenta |
| 20/11 09:45 e 09:56 (ordens do dono) | o recibo deve mostrar "<versão>: N de 20"; até existir a ferramenta, o contador é conferido "pelo git" à mão | a contagem é de memória ou manual |

Custo do problema: três faxinas de quadro em quatro dias (E2.522, E11.1, E11.2), cada uma uma etapa de agente, e uma
ordem do dono só para gravar linhas que faltavam.

## 2. Por que o existente não basta

| Já existe | Faz | Não faz (evidência) |
|---|---|---|
| `forge-check movimento` | grava a linha do movimento com hora real | só roda quando alguém lembra; os 22 + 19 + 55 cartões acima ficaram sem a linha de Pronto |
| `forge-check kanban` | colunas, ID repetido, responsável, WIP | não cruza com o histórico nem com a develop: saiu "sem divergência de coluna" em 19/11 com 22 entregues abertos |
| `forge-check kanban --gerar` | refaz o quadro do histórico; avisa "cartão sem movimento no histórico" e "quadro editado fora do movimento" | só avisa, e só quando alguém roda o `--gerar`; os 10 cartões de 20/11 entraram assim |
| `forge-check dora` | vazão por semana, das tags e do quadro | não dá a versão em curso, o teto, o backlog por coluna nem a previsão diária |
| `forge-check metricas` | tempos e voltas por pedido | idem; é por pedido, não por versão |
| leitura do assunto `Merge pull request #N from <dono>/<branch>` (função das etapas do `proximo`) | acha a branch de cada merge | não liga merge a cartão: hoje nenhum PR cita cartão de forma legível por ferramenta |
| `hooks/meta.py` (`medir_mensagem`) | mede forma da mensagem ao dono em `mensagens.jsonl` | não sabe se a mensagem traz a linha do contador |

Conclusão: falta o elo "PR → cartão" legível por ferramenta. Com ele, o resto reaproveita o que existe (`movimento`,
`montar_quadro`, a leitura de merges, `.forge/config.json`, a medida do `meta.py`).

## 3. Opções e recomendação

### 3.1 Onde o PR cita o cartão
- **A (recomendada): trailer de commit `Cartão: <ID>`** em algum commit do PR (o intervalo `merge^1..merge^2`; no
  squash, o corpo do commit, onde o GitHub concatena as mensagens). Lido só com `git`, offline, igual no Forge e no
  projeto, e sobrevive ao apagar da branch.
- B: corpo do PR. Exige `gh` e rede a cada contagem; o histórico some se o PR for editado; fora do git.
- C: nome da branch. Não comporta lote (até 4 cartões por PR, ordem de 20/11 09:45) e quebra com branch renomeada.

### 3.2 Quem move o cartão no merge
- **A (recomendada): `forge-check quadro sincronizar`**, idempotente, local: lê os merges da develop desde a última
  sincronização, tira os trailers e chama o mesmo `movimento` para o Pronto, com `PR #N merge <sha12>` no motivo. Roda
  pelo tech-lead depois de cada merge e pelo Jarvis a cada marco; o contador mostra `sincronizar: N pendentes` quando
  falta, então o esquecimento aparece em todo recibo.
- B: ação do CI no merge. No Forge o quadro não está no repositório (pasta de controle local), então o CI não o alcança;
  no projeto, o CI teria de commitar na develop, o que fere `R-FLUXO`.
- C: hook no `gh pr merge`. Não vê o merge feito pelo dono na interface do GitHub.

### 3.3 Cartão só nasce pela ferramenta
- **A (recomendada):** o `forge-check kanban` (a checagem, não só o `--gerar`) reprova cartão aberto do `KANBAN.md`
  sem nenhuma linha no `docs/kanban/historico.md`. O nascimento é o `movimento --de —` que já existe.
- B: hook que bloqueia edição do `KANBAN.md`. O quadro tem texto livre (cabeçalho, plano de versões, decisões) que se
  edita à mão; bloquearia o legítimo.

### 3.4 Prova de que o recibo traz a linha
- **A (recomendada):** o `forge-check contador` grava a linha que imprimiu em `.forge/run/contador.jsonl` (hora, linha,
  sha256); a medida do `meta.py` acusa `contador: ausente` (a mensagem não tem linha na forma) ou `contador: diferente`
  (tem a forma mas não é nenhuma linha gravada nas últimas 24 h, ou seja, escrita de memória). Só mede, nunca barra o Stop.
- B: o hook recalcula o contador no Stop. Põe `git` e a leitura do histórico inteiro no caminho de toda mensagem.

## 4. Desenho

### 4.1 A contagem (o núcleo comum)
- **Marca:** a última tag `v<maior>.<menor>.<patch>` alcançável de `origin/develop` (sem tag: o primeiro commit, rótulo
  `antes da primeira versão`). **Versão em curso:** a marca com o patch + 1 (decisão D4).
- **PRs mesclados:** merges da primeira linha de `origin/develop` em `<marca>..origin/develop` cujo assunto é
  `Merge pull request #N from ...`, mais os commits de squash com `(#N)` no fim do assunto.
- **Cartões de um PR:** trailers `Cartão: <ID>` (entrega) e `Cartão-parcial: <ID>` (cita, não entrega; decisão D3) no
  intervalo do PR. ID na forma do atributo de pedido do `movimento` (letras, números, `.`, `_`, `-`; até 80).
- **Entregues desde a marca:** conjunto de IDs com `Cartão:` nos PRs acima (cartão em dois PRs conta uma vez).
- Uma função, um módulo (`bin/forge_contador.py`), usada pelo `contador`, pelo `quadro sincronizar`, pela checagem de
  citação e pela medida. É a regra "mesma contagem" do cartão, garantida por construção.

### 4.2 `forge-check contador` (só leitura do git e do histórico; grava só o seu registro em `.forge/run/`)
Saída, uma linha (forma da ordem do dono de 20/11 09:56):

`<versão>: <entregues> de <teto> · backlog: <N> abertos (Entrada <X> · Pronto para fazer <Y> · em curso <Z> · esperando o dono <W>) · hoje: +<novos>, −<fechados> · faltam <V> versões · previsão <DD/MM>`

- **Abertos por coluna:** do `montar_quadro` sobre o histórico (nunca do texto do quadro); grupos na decisão D7.
- **Hoje:** `novos` = linhas do dia com `De` = `—`; `fechados` = cartões cuja linha do dia vai para Pronto ou Fechado sem
  entrega pela primeira vez (D5). Dia no fuso da máquina, como o `dora`.
- **Backlog crescendo:** com `novos > fechados`, a linha leva o marcador de alerta e o texto `backlog crescendo` da ordem
  do dono e a previsão vira `sem data enquanto crescer`.
- **Versões:** `ceil(abertos / teto)`. **Teto:** `teto_da_versao` do `.forge/config.json` do projeto, padrão 20 pelo
  modelo; valor fora de inteiro 1..200 usa o padrão e avisa em stderr (a lição do CONFIG-TETO-SEM-GUARDA).
- **Previsão:** `hoje + ceil(abertos / vazão)`, com a vazão = média de entregas por dia nos últimos 3 dias (D6); vazão 0
  dá `sem data`.
- **Divergência:** cartões com `Cartão:` mesclado e fora do Pronto saem como sufixo `· sincronizar: <n> pendentes`.
- **rc:** 0 com a linha; 2 com `contador: não verificável: <motivo>` (sem git, sem `origin/develop`, histórico ilegível).
  Nunca imprime número inventado.

### 4.3 AE2: citação, movimento e nascimento
- **Citação (pre-push barato e CI):** branch de item (a que vai para a branch de integração; release e promoção ficam
  de fora) sem nenhum trailer `Cartão:` ou `Cartão-parcial:` no intervalo desde a base reprova, com a mensagem de como
  citar. No envio local também se confere que o ID existe no histórico do quadro (no Forge, pela pasta de controle;
  sem quadro legível, só a forma). No CI só a forma, porque no Forge o quadro não está no repositório.
- **Movimento (`forge-check quadro sincronizar`):** para cada PR mesclado ainda não sincronizado (a chave é o sha do
  merge no motivo da linha), cada `Cartão:` vira `movimento <ID> --de <coluna atual> --para Pronto --motivo "PR #N merge
  <sha12>"`; `Cartão-parcial:` vira só uma linha de nota na coluna atual. Cartão já em Pronto ou Fechado sem entrega:
  nada. ID sem cartão no histórico: aviso e nada gravado. Grava sob a trava do quadro que o `--gerar` já usa e termina
  com o `kanban --gerar`. O commit da pasta de controle é do AE3 (fora daqui).
- **Nascimento:** `forge-check kanban` sai com violação `cartão <ID> no quadro sem linha no histórico; nasça pelo
  forge-check movimento --de —` para todo cartão fora de Pronto e Fechado sem entrega sem linha no histórico (D8).

### 4.4 O Jarvis e o modelo de projeto
- `agents/jarvis.md` e `skills/falar-com-o-dono/toda-mensagem.md`: todo recibo e aviso de marco traz, copiada, a linha
  do `forge-check contador` (nunca escrita à mão); o tech-lead roda `quadro sincronizar` depois de cada merge e o Jarvis
  a cada marco. Regras citadas pelo ID (`R-PROVA`, `R-DECISAO`), sem copiar texto.
- Modelo: `templates/projeto/.forge/config.json` ganha `teto_da_versao: 20`; o modelo de PR e o `KANBAN.md` do modelo
  ganham uma linha de instrução (trailer e nascimento). Chega aos projetos pela atualização normal.

## 5. Corte em itens (até 150 linhas de código e até 10 arquivos cada)

Papel do autor: `forge:tech-lead` (dono dos dois cartões) ou quem ele designar; review, QA e segurança pela classe do
diff (`forge-check classe`). Linhas = código de produção estimado, sem testes.

| Item | Papel | Arquivos | Linhas | Depende de | Casos de abuso que cabem ao item |
|---|---|---|---|---|---|
| C1 núcleo da contagem | tech-lead | `bin/forge_contador.py`, `tests/test_contador.py`, `tests/mutantes/<spec>.json` | ~110 | — | trailer com `\|`, controle, `Cf` ou acima de 80 caracteres (recusado, nunca vai à linha do histórico); mais de 10 trailers num PR (só os 10 primeiros, aviso); assunto de merge forjado fora da primeira linha (só a primeira linha de `origin/develop` conta); tag fora da forma `v<n>.<n>.<n>` ignorada; ref com `-` no começo (`--end-of-options`); `git` que trava (o timeout do `git()`) |
| C2 `forge-check contador` | tech-lead | `bin/forge-check`, `bin/forge_contador.py`, `tests/test_contador.py`, `tests/mutantes/<spec>.json` | ~130 | C1, C3 | histórico por link simbólico ou acima do teto (leitura do `_ler_regular`, rc 2); `.forge/run/contador.jsonl` por link (`O_NOFOLLOW`, só acréscimo); data futura no histórico (não conta como hoje); divisão por vazão 0 |
| C3 teto na configuração | tech-lead | `templates/projeto/.forge/config.json`, `bin/forge_contador.py`, `tests/test_contador.py` | ~25 | — | `teto_da_versao` booleano, negativo, 0, texto ou 10⁹ (padrão e aviso); config que não é objeto JSON (padrão e aviso, sem traceback) |
| C4 citação no envio e no CI | tech-lead + devops-engineer | `.githooks/pre-push`, `.github/workflows/ci.yml`, `templates/projeto/.github/workflows/ci.yml`, `bin/forge_contador.py`, `tests/test_contador.py`, `tests/test_prepush_*.py` | ~70 | C1 | PR sem trailer passando por branch de nome de release (a isenção é pela base de destino, não pelo nome); título ou corpo do PR com trailer (só commit vale); ID citado que não existe no quadro (recusa local); variável do CI injetada no comando (ID lido do git, nunca de `${{ }}` em `run:`) |
| C5 `quadro sincronizar` | tech-lead | `bin/forge-check`, `bin/forge_contador.py`, `tests/test_contador.py`, `tests/mutantes/<spec>.json` | ~120 | C1 | rodar duas vezes (idempotente pelo sha do merge); duas sessões juntas (trava do quadro); PR que cita cartão Fechado sem entrega (não reabre, aviso); cartão de outro pedido citado por engano (move, com o PR no motivo para reverter por `movimento`); historico.md por link (recusa do `movimento`) |
| C6 nascimento no `kanban` | tech-lead | `bin/forge-check`, `tests/test_kanban*.py` | ~35 | — | cartão com ID que só difere em maiúsculas do histórico (casa pela `chave_do_cartao`); linha de histórico fora da forma não conta como nascimento |
| C7 medida da linha no recibo | tech-lead + security-engineer | `hooks/meta.py`, `tests/test_meta.py`, `tests/hooks/meta/<3 fixtures>.json`, `skills/falar-com-o-dono/SKILL.md` | ~50 | C2 | linha copiada de outro dia (`diferente`); `contador.jsonl` gigante (lê só o fim, até o `TETO_DA_MEDIDA`); arquivo ausente ou ilegível (`sem_medida`, nunca acusa nem barra); a falha da medida nunca troca a decisão do Stop (o `finally` que já existe) |
| C8 textos e modelo | tech-lead | `agents/jarvis.md`, `skills/falar-com-o-dono/toda-mensagem.md`, `agents/tech-lead.md`, `templates/projeto/KANBAN.md`, `templates/projeto/.github/pull_request_template.md` (se existir; senão a skill de PR), `changelog.d/<branch>.md` | 0 | C2, C5 | texto que manda escrever a linha "de cabeça" (a medida acusa); regra copiada em vez de citada pelo ID (teste de citação) |

Ordem: C1, C3 e C6 em paralelo; depois C2, C4 e C5 em paralelo; depois C7 e C8. Cada item é um PR (ou lote do mesmo
arquivo), com fragmento de changelog.

## 6. Critério de parada

- bloqueia: PR de item sem trailer de cartão, e cartão aberto no quadro sem linha no histórico.
- sem-citacao · branch de item cujo intervalo desde a base não tem `Cartão:` nem `Cartão-parcial:` · oráculo: `tests/test_contador.py` (caso sem trailer reprova; com trailer passa)
- citacao-fora-da-forma · trailer com ID fora da forma ou com controle · oráculo: `tests/test_contador.py` (tabela de IDs recusados)
- cartao-sem-nascimento · cartão aberto no `KANBAN.md` sem linha no histórico · oráculo: `forge-check kanban` com quadro de teste (rc 1 e a linha da violação)
- gatilho · oráculo: `forge-check contador` sobre um repositório de teste com 2 merges citando 3 cartões depois de uma tag devolve `…: 3 de 20` e, depois do `quadro sincronizar`, `sincronizar` some da linha

## 7. Decisões que dependem do dono

1. **D1 citação:** trailer de commit `Cartão: <ID>` (A) ou corpo do PR (B). Recomendo A: só git, offline, igual no
   Forge e nos projetos.
2. **D2 destino no merge:** Pronto (A) ou "Aguardando sua validação" quando o cartão pede validação do dono (B).
   Recomendo A no padrão, com a coluna de destino em `.forge/config.json` (`coluna_do_merge`, padrão Pronto) para o
   projeto que valida com o usuário antes do Pronto.
3. **D3 entrega parcial:** trailer `Cartão-parcial:` que cita sem mover (A) ou só entrega inteira (B). Recomendo A: os
   5 parciais de 19/11 mostram que o caso existe.
4. **D4 nome da versão em curso:** última tag com patch + 1 (A) ou a versão do plano no quadro (B). Recomendo A: o plano
   é texto livre, a tag é fato.
5. **D5 o que é "fechado" no dia:** Pronto e Fechado sem entrega no saldo do dia, só Pronto na vazão (A) ou os dois nos
   dois (B). Recomendo A: uma triagem que fecha 49 cartões num dia (E11.3) não é vazão de entrega.
6. **D6 "últimos 3 dias":** os 3 dias mais recentes com ao menos uma entrega, sem contar hoje (A), ou os 3 dias corridos
   (B). Recomendo A, que é a leitura de "3 dias bons" da ordem de 20/11 09:43; o rótulo da linha diz qual.
7. **D7 grupos de colunas:** em curso = Empatizar e definir, Idear e prototipar, Validação do usuário, Em andamento,
   Code review, QA; esperando o dono = Aguardando sua validação, Aguardando o dono, Bloqueado. Recomendo assim, com o
   mapa numa constante única do módulo.
8. **D8 rigor do nascimento:** violação (rc 1) no `forge-check kanban` (A) ou só aviso (B). Recomendo A: os 10 cartões
   de 20/11 08:44 e os 90 de 19/11 mostram que aviso não basta.
9. **D9 cartões por PR:** aviso acima de 4 (a ordem de 20/11 09:45) e teto duro de 10 contra abuso. Recomendo assim.

## 8. Riscos e reversão

| Risco | Efeito | Tratamento |
|---|---|---|
| squash merge com mensagem editada perde o trailer | cartão não move nem conta | o `contador` mostra o PR sem cartão (`sem cartão: #N`); o tech-lead move pelo `movimento` com o PR no motivo |
| merge feito pelo dono na interface sem sincronizar depois | quadro atrasado | `sincronizar: N pendentes` em todo recibo até alguém rodar |
| PR revertido | cartão fica em Pronto | fora do escopo; o revert cita o cartão e o tech-lead o reabre pelo `movimento` (cartão de melhoria se repetir) |
| cartão errado citado | cartão vai a Pronto sem entrega | o motivo leva o PR; reabrir pelo `movimento`; o escape registra (`forge-check escape registrar`) |
| `.forge/run/contador.jsonl` gravado à mão | a medida diz `igual` para linha forjada | só medida, nunca portão; a linha é refeita pela ferramenta na conferência |
| quadro no Forge fora do repositório | CI não confere existência do cartão | o envio local confere; o CI confere a forma |
| projeto sem tag | marca no primeiro commit | rótulo `antes da primeira versão` |

**Reversão:** cada item é um PR e sai por revert sem afetar os outros (C6 e C4 são os únicos que barram; revertê-los
volta ao estado de hoje). **Critério de reversão (fato observável):** (a) duas entradas em `docs/kanban/escapes.md`
com causa "cartão movido pelo sincronizar sem entrega" em 14 dias fazem o `sincronizar` passar a só imprimir os
movimentos, sem gravar; (b) a primeira conferência em que a linha do `contador` diverge da contagem pelo git à mão (a
forma provisória da ordem de 20/11 09:56) reabre o C1 antes de qualquer outro item seguir.

**Medida de sucesso:** em 7 dias depois do C5 e do C6, nenhuma faxina de quadro (etapa do tipo E11.x) e zero cartão
aberto sem linha no histórico na saída do `forge-check kanban`; a medida do C7 com `contador: ausente` em menos de 5 %
das mensagens.

## 9. Gatilhos de segurança

Hook (`hooks/meta.py`), envio (`.githooks/pre-push`), CI e texto de fonte não confiável (trailer de commit) que vai ao
histórico do quadro: o `security-engineer` revisa C4, C5 e C7 (`R-SEGURANCA`); os casos de abuso da tabela da seção 5
são o ponto de partida do modelo de ameaças dele.
