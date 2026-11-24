# BP2: fila de merge em série e conserto da develop vermelha (desenho, sem código)

Pedido v0478, etapa E38.1 (cartão BP2-FILA-DE-MERGE, que absorve FECHAR-MODO-CONSERTO). Autor: `software-architect`. Data: 2026-11-19. Estado: proposta ao dono.
Propósito: desenhar a BP2 de `docs/propostas/boas-praticas-1911.md` conferida com fontes atuais, antes de qualquer código. Público: o dono, o `tech-lead`, o `devops-engineer` e o `security-engineer`, que dão parecer neste corte.
Conferência com as regras: `R-FLUXO`, `R-MAIN`, `R-VERIFY`, `R-CUSTO`, `R-NEUTRO`, `R-CONFORMIDADE` conferidas abaixo; o desvio está declarado em "Afrouxa?".

## 1. O problema, com os números do estudo

Do estudo de 19/11 (30 horas do Forge, de 16 a 19/11) e do quadro:
- **A develop ficou vermelha 4 vezes**, todas por teste dependente de tempo ou carga (a causa é a BP1; esta BP trata a saída do vermelho).
- **Um único teste instável segurou 4 PRs.** Com a develop vermelha, o passo 6b do `bin/forge-fechar` para todo merge (`bin/forge-fechar:1016-1023`, `ci_antes_do_merge`), inclusive o do PR que conserta a develop.
- **O conserto não entra pelo script:** o #681, verde, ficou parado no 6b (cartão FECHAR-MODO-CONSERTO, `KANBAN.md:81`). A saída foi o dono, **três vezes** (mesmo cartão); a última, a decisão de 2026-11-19 14:59 que autorizou o rerun do run 44574989031 (`docs/pedidos/v0478.md:453`).
- **Teste sobre base velha:** sem "branch atualizada" no ruleset (decisão E8 da 0.45.6, `docs/protecao-de-branch.md:21`), o CI do PR testa o merge com a develop **do momento do evento** (fonte S6); se outro PR entra depois, o passo 6a segue sem conflito (`bin/forge-fechar:34`; `docs/fechamento-integrador.md:20`, "Risco que sobra"). O estudo **não mediu** nenhum vermelho por quebra semântica entre dois PRs: é prevenção, não dor medida. Esta parte entra depois do conserto (ordem na seção 6).

## 2. O que a prática diz hoje (fontes, conferidas em 2026-11-19)

| # | Fonte | Data | O que vale para o Forge |
|---|---|---|---|
| S1 | GitHub Docs, trecho reutilizável `data/reusables/gated-features/merge-queue.md` (repositório `github/docs`, ramo `main`) | lido 2026-11-19 | "Pull request merge queues are available in any public repository owned by an organization, or in private repositories owned" por organização com GitHub Enterprise Cloud. **Repositório de conta pessoal não tem a fila.** |
| S2 | GitHub Docs, "Managing a merge queue" | lido 2026-11-19 | O workflow precisa do evento `merge_group`; a fila espera os checks exigidos; opções: método (merge, rebase, squash), concorrência de 1 a 100, tamanho mínimo e máximo do grupo, espera, "só mesclar PR que não falha", prazo do check; ramos temporários `gh-readonly-queue/{base}`; não funciona com regra de proteção que usa curinga. |
| S3 | GitHub Docs, "Merging a pull request with a merge queue" | lido 2026-11-19 | Sai da fila por falha do CI no grupo, prazo, pedido ou proteção não resolvida; o administrador pode mesclar fora da fila só se a proteção permitir desvio; o `gh` não tira PR da fila. |
| S4 | GitHub Docs, "About protected branches" (seção "Require merge queue") | lido 2026-11-19 | A fila dá o mesmo que "Require branches to be up to date before merging", sem o autor ter de atualizar a branch e esperar os checks de novo. |
| S5 | GitHub Docs, "Available rules for rulesets" | lido 2026-11-19 | Com "Require branches to be up to date" marcado, a branch **tem de** estar em dia com a base para o merge. Vale em conta pessoal. |
| S6 | GitHub Docs, "Events that trigger workflows" | lido 2026-11-19 | No `pull_request`, `GITHUB_SHA` é o último commit de merge de `refs/pull/N/merge`; com conflito, o workflow não roda. No `merge_group`, o check exigido só é reportado se o workflow tem esse gatilho; sem ele o merge falha. |
| S7 | GitHub Changelog, "Pull request merge queue is now generally available" | publicado 2023-07-12, lido 2026-11-19 | Disponível em repositórios públicos de organização e no Enterprise Cloud; pular a fila é só de administrador por padrão. |
| S8 | GitLab Docs, "Merge trains" | lido 2026-11-19 (cita a versão 19.3) | Cada MR é testado sobre a base mais os da frente; o que falha sai e os de trás recomeçam sem ele. "Merge immediately" existe para o caso crítico, à custa de recomeçar o trem. Só nos planos Premium e Ultimate: não serve ao Forge (`R-CUSTO`), serve de referência para o conserto. |
| S9 | Repositório `bors-ng/bors-ng` | arquivado em 2024-04-04, lido 2026-11-19 | O robô de fila clássico está descontinuado e manda usar a fila nativa do GitHub. |

Não conferido nesta etapa: aplicativos de fila de terceiros. Ficam fora de qualquer forma: são serviço externo com escrita no repositório (ADR 0008) e podem ter plano pago (`R-CUSTO`).

Conclusão das fontes:
1. A fila nativa do GitHub é a prática atual, mas **exige organização**. O Forge mora em conta pessoal (`docs/adr/0009-conformidade-dos-agentes.md:89`). Uma organização gratuita com repositório público a teria sem custo (S1).
2. Em conta pessoal, o equivalente do servidor é "branch atualizada" (S4, S5), que o dono desligou na E8 da 0.45.6 para não repetir a bateria a cada PR.
3. O conserto da integração vermelha é um caso previsto pelas filas (S8: "merge immediately"; S3: desvio só de administrador). No Forge não há desvio para ninguém (`R-CONTRIB`, "Nenhum portão tem exceção"); então o conserto não pula a fila nem os portões: ele é o **único** que a fila aceita enquanto a develop está vermelha.

## 3. Desenho

### 3.1 Conserto da develop vermelha (F1, absorve FECHAR-MODO-CONSERTO)

Onde: `bin/forge-fechar`, opção nova `--conserto <run>` (o número do run vermelho do push na develop, só dígitos). Sem a opção, o 6b continua como hoje: develop vermelha para tudo.

Com `--conserto`, o 6b libera o merge **só** se todas as condições valem; qualquer leitura que falha para (falha fechada):
- **C1, o vermelho é o do topo:** o run é do evento `push` na develop, no topo lido do servidor agora, e está concluído com falha (não pendente nem cancelado). O topo é relido antes do merge; se andou, para.
- **C2, pareceres e cadeia de sempre:** passos 1, 1c, 2, 4 e 5 sem mudança: `forge-check pr` com os pareceres da classe aprovados para o head, a catraca e a bateria verdes. Nada é dispensado.
- **C3, preso ao commit revisado:** o merge usa `--match-head-commit` com o head conferido (H). Se o 2b trouxe a base, o head novo (M) só vale com `M^1 = H`, `M^2 = topo` e a árvore de M igual à do `git merge-tree` dos dois: é o commit que o próprio script gera, conferível sem confiança.
- **C4, os testes que falharam passaram no PR:** os IDs vêm das anotações `::error` que `scripts/falhas-no-resumo.py` já grava nos jobs do run vermelho (leitura pela API de check runs, sem log). Cada ID não pode constar nos pulados do CI do PR (artefatos `pulados-*` do run do PR, só leitura). Árvore provada na develop (SP4) conta como passou. Mais de 10 falhas num passo (o GitHub só mostra 10 anotações de erro por passo) para e pede a leitura do log.
- **C5, o PR tem relação com o vermelho:** o diff do PR toca o arquivo de um teste que falhou, ou um arquivo mudado entre o último push verde da develop e o topo, ou é a reversão (`git revert`) de um merge desse intervalo. Sem relação, para (decisão D2).
- **C6, um conserto por vez e prova depois:** o passo 8 acompanha o CI do push no merge; não verde sai com código 5 e a develop continua fechada para tudo que não é conserto.
- **C7, registro:** linha no log e no `## Histórico` do pedido: `conserto da develop: run <R>, topo <T7>, PR #<n>, head <H7>`.

Fora do conserto: `--lote` e `--armar` são recusados com `--conserto` (o conserto é acompanhado até o fim). A reversão impressa hoje pelo passo 8 (`reversao`, `bin/forge-fechar:1009`) passa a sair com o comando do fechamento com `--conserto`.

### 3.2 Fila em série: cada PR testado sobre a develop atual (F2)

Recomendação (D1): **a fila mora no `bin/forge-fechar`**, com o servidor como está. Três peças:
- **Base testada (CI):** o job `bateria (passos)` do PR grava uma anotação `base-testada <sha>` com o primeiro pai do commit de merge do checkout (`git rev-parse HEAD^1`, o mesmo que os passos de changelog e segredo já usam). É a prova de sobre qual develop o PR foi testado.
- **Passo 6c, base testada é o topo:** depois do 6a e do 6b, o script lê a anotação do head conferido e compara com o topo da develop no servidor. Igual, mescla. Diferente, traz a base pelo caminho H4 que já existe (commit de merge com a árvore do `merge-tree`, `git push origin` de sempre, sem forçar nem pular o pre-push) e espera o CI do head novo. Hoje o H4 roda "uma vez por cadeia" (`bin/forge-fechar:10`, `--trazida`); passa a um teto de 3 voltas, e no teto para e devolve ao `tech-lead`.
- **Trava da fila:** só um fechamento por vez entre o 6c e o merge. Duas camadas: trava local (`flock` num arquivo em pasta do próprio usuário, modo 700, a mesma regra da pasta de log) e trava no servidor, só leitura: se outro PR para a develop já tem auto-merge armado, espera. O `--armar` continua valendo, mas o PR armado **é** a trava: ninguém mais mescla até ele entrar ou sair.

Lote (diretriz 26): continua como exceção declarada. O lote já exige o CI da develop verde antes, itens sem arquivo em comum e um CI acompanhado no fim com reversão do lote inteiro; os itens dele não passam pelo 6c (D4).

O que muda no modelo de projeto (neutro, todos os projetos):
- `templates/projeto/.github/workflows/ci.yml` ganha o gatilho `merge_group` (sem efeito onde a fila não existe; liga a fila nativa onde o repositório é de organização).
- `templates/projeto/docs/engineering/protecao-de-branch.md` passa a dizer: repositório de organização usa a fila nativa (S1, S2); conta pessoal usa o passo à mão do `tech-lead` (o mesmo 6c: o CI do PR rodou sobre o topo? senão traga a base) e, se o dono quiser o servidor barrando, "branch atualizada" (S5).
- O conserto da integração vermelha vira texto da `R-FLUXO`, "No Forge e no projeto", com as mesmas condições C1 a C6 em linguagem de passo à mão.

### 3.3 O que não muda
Hooks: nenhum. O hook `parecer` continua exigindo os pareceres no `gh pr merge`. Rulesets: nenhum agente os altera (`R-CONFORMIDADE`); se o dono escolher a opção (b) de D1, ele mesmo marca a caixa, pelo passo a passo. `main` e `homolog`: intocadas (`R-MAIN`).

## 4. Por que o existente não basta
- **6b (FECHAR-ESPERA-CI-DEVELOP):** barra o merge com a develop vermelha, inclusive o conserto. Evidência de execução: #681 verde parado no 6b; três intervenções do dono; o rerun autorizado às 14:59 de 19/11 (run 44574989031).
- **Reversão impressa no passo 8:** só imprime o comando; o PR da reversão cai no mesmo 6b.
- **2b e 6a (H4 e E8):** trazem a base uma vez, antes do PR, e no 6a seguem sem conflito: o PR que testou sobre uma develop velha entra (`docs/fechamento-integrador.md:20`).
- **"Fila de integração" da `R-FLUXO`:** ordena só PRs com arquivo em comum (`forge-check sobreposicao`); não diz sobre qual base o PR foi testado.
- **Fila nativa do GitHub:** não existe em conta pessoal (S1).

## 5. Riscos
- **R1, conserto falso:** um PR qualquer, verde, declarado conserto com a develop vermelha por teste instável. Mitigação: C4 e C5; o passo 8 mostra se a develop voltou ao verde.
- **R2, tempo:** o re-teste custa uma bateria de PR a mais (8 a 22 min nos runs medidos em `docs/propostas/ci-rapido.md`, antes do CI-RAPIDO) sempre que outro PR entra no meio. A trava serializa a espera; hoje o 6b já serializa em parte.
- **R3, trava presa:** processo morto com a trava local. Mitigação: `flock` some com o processo; a trava do servidor é o estado do PR, lido a cada vez.
- **R4, merge fora do script:** o `gh pr merge` à mão não passa pelo 6c. Mitigação parcial: o hook `parecer` continua; o critério de reversão de D1 mede.
- **R5, anotações:** a API mostra até 10 anotações de erro por passo; acima disso C4 para (falha fechada, custa uma leitura do log).
- **R6, mudança no CI:** a anotação `base-testada` e o `merge_group` no modelo pedem parecer de devops e de segurança (`R-SEGURANCA`: CI).

## 6. Corte em itens (até 150 linhas de código e 10 arquivos cada; H1)

Ordem: F1 primeiro (a dor medida), F2 depois. Em paralelo só I3 e I6 (arquivos diferentes de tudo).

| Item | Agente | O quê | Arquivos | Linhas de código (estimativa) | Pareceres |
|---|---|---|---|---|---|
| I1 | `tech-lead` | `--conserto`: C1, C3, C4, C5, C6, C7 e recusa com `--lote` e `--armar` | `bin/forge-fechar`, `tests/test_fechar.py`, `tests/mutantes/fechar-conserto.json`, `docs/fechamento-integrador.md`, `changelog.d/<branch>.md` | 120 a 140 (se passar de 150: I1a leitura de C1 e C4; I1b C5 e a liberação do 6b) | review, QA, segurança; rótulo `afrouxa-regra` |
| I2 | `tech-lead` | conserto na `R-FLUXO` (Forge e projeto), uma linha em `agents/tech-lead.md`, invariante novo do texto do conserto | `docs/regras/R-FLUXO.md`, `agents/tech-lead.md`, `tests/config.json`, `changelog.d/<branch>.md` | 0 (texto) | review, segurança; rótulo `afrouxa-regra` |
| I3 | `devops-engineer` | anotação `base-testada` no job `bateria (passos)` | `.github/workflows/ci.yml`, `tests/test_ci_local.py` (se o passo tem hash fixado), `changelog.d/<branch>.md` | 10 | devops, segurança, review |
| I4 | `tech-lead` | trava local e no servidor; passo 6c; teto de 3 voltas do H4; lote isento | `bin/forge-fechar`, `tests/test_fechar.py`, `tests/mutantes/fechar-fila.json`, `docs/fechamento-integrador.md`, `changelog.d/<branch>.md` | 130 a 150 (se passar: I4a trava; I4b 6c e voltas) | review, QA, segurança, devops |
| I5 | `tech-lead` | fila na `R-FLUXO`; "Limites" de `docs/protecao-de-branch.md`; texto do modelo de projeto | `docs/regras/R-FLUXO.md`, `docs/protecao-de-branch.md`, `templates/projeto/docs/engineering/protecao-de-branch.md`, `tests/test_modelos_projeto.py`, `changelog.d/<branch>.md` | 0 (texto e teste) | review, devops |
| I6 | `devops-engineer` | `merge_group` no CI do modelo de projeto, com a base do evento | `templates/projeto/.github/workflows/ci.yml`, `tests/test_modelos_projeto.py`, `changelog.d/<branch>.md` | 10 | devops, segurança, review |

O `qa-engineer` escreve ou confere os testes de cada item com o ramo de falha de cada condição e os mutantes (AR-1, AR-2 dos achados recorrentes).

Corte por arquivo (quem toca o quê, para não haver dois itens abertos no mesmo arquivo):

| Arquivo | Itens, em ordem |
|---|---|
| `bin/forge-fechar` | I1, depois I4 (mesma trilha de FECHAR-1C-DUPLO e FECHAR-LIMPA-CLONE-ANCESTRAL, `KANBAN.md:87` e `:111`: um de cada vez) |
| `tests/test_fechar.py` | I1, I4 |
| `docs/fechamento-integrador.md` | I1, I4 |
| `docs/regras/R-FLUXO.md` | I2, I5 |
| `tests/test_modelos_projeto.py` | I5, I6 |
| `.github/workflows/ci.yml` | I3 |
| demais | um item cada |

## 7. Critério de parada
- bloqueia: merge na develop de PR testado sobre base diferente do topo, e merge com a develop vermelha que não seja conserto preso ao commit revisado, com os pareceres aprovados e os testes que falharam passando no PR.
- C-VERMELHA-COMUM · PR sem `--conserto` com o CI do topo vermelho · oráculo: casos do 6b em `tests/test_fechar.py` (os de hoje, sem mudança)
- C-CONSERTO-SEM-PROVA · `--conserto` com run que não é do topo, não vermelho, teste que falhou pulado ou ausente no PR, ou diff sem relação · oráculo: um caso por condição em `tests/test_fechar.py` (I1)
- C-CONSERTO-DESPRENDIDO · head diferente do conferido, ou M que não é merge de (H, topo) com a árvore do `merge-tree` · oráculo: `tests/test_fechar.py` (I1)
- C-TOPO · anotação `base-testada` diferente do topo, ausente ou ilegível · oráculo: `tests/test_fechar.py` (I4)
- C-TRAVA · segundo fechamento com a trava local tomada ou outro PR armado na develop · oráculo: teste com dois processos em `tests/test_fechar.py` (I4)
- C-LEITURA · qualquer leitura que falha em C1 a C5 ou no 6c para sem mesclar · oráculo: `tests/test_fechar.py` com o `gh` falso devolvendo erro
- gatilho · oráculo: `bin/forge-mutante` sobre `tests/mutantes/fechar-conserto.json` e `tests/mutantes/fechar-fila.json`, todos os mutantes mortos

## 8. Afrouxa?
- I1 e I2: **sim, `R-FLUXO`** ("Lote e CI" e o 6b de `docs/fechamento-integrador.md`: hoje a develop vermelha para todo merge; passa a aceitar o conserto). A ordem do dono de 19/11 17:27 pede isso; o rótulo `afrouxa-regra` vai no PR de cada um (D5).
- I4 e I5: apertam (cada PR testado sobre o topo), mas I5 troca texto da `R-FLUXO`: **sim, `R-FLUXO`** pela regra de texto; vai ao dono com o PR.
- I3 e I6: não.

## 9. Neutro e sem custo
- `R-NEUTRO`: nada de projeto, stack ou nome; o conserto e a fila valem para qualquer repositório com CI no GitHub; os projetos seguem à mão (o script é do Forge) ou pela fila nativa quando são de organização.
- `R-CUSTO`: zero. Actions em repositório público é gratuito; organização gratuita também; nenhum serviço de terceiro. Em repositório **privado** de projeto, o re-teste gasta minutos da cota gratuita do plano: o texto do modelo avisa.

## 10. Decisões do dono (a de maior peso primeiro)

**D1. Onde mora a fila.**
- (a) Fila nativa do GitHub, passando o Forge para uma organização gratuita (repositório público, sem custo; S1). Pede `merge_group` no `ci.yml` e na catraca (hoje só `pull_request`), e a mudança de endereço do marketplace para todos os projetos.
- (b) "Branch atualizada" no ruleset `portoes` (o servidor barra; S5), revertendo a E8 da 0.45.6; o lote da diretriz 26 deixa de funcionar como hoje (cada item vira re-teste).
- (c) Fila no `bin/forge-fechar` (seção 3.2), servidor como está.
- **Recomendação: (c).** Atende "cada PR testado sobre a develop atual" sem custo, sem mudar endereço nem ruleset e sem quebrar o lote. `reabre se:` o Forge passar para uma organização (por exemplo pela BP9), e então (a); ou um merge fora do script quebrar a develop sem conflito, e então (b).

**D2. Condições do conserto.** Aceitar C1 a C7 como estão, inclusive C5 (relação do diff com o vermelho)? **Recomendação: sim.** Sem C5, qualquer PR verde entra com a develop vermelha por teste instável. `reabre se:` C5 recusar um conserto legítimo 2 vezes em 30 dias.

**D3. Re-teste quando a base andou.** Sempre (recomendado), ou só quando a base nova tem arquivo em comum com o PR (mais barato, mantém o risco aceito na E8)? **Recomendação: sempre**, que é a prática (S4, S8). `reabre se:` o tempo do PR verde até a develop subir mais de 30% em 30 dias sem nenhum re-teste vermelho.

**D4. Lote sob a fila.** Manter o lote como exceção declarada (recomendado), suspender o lote, ou depois testar o lote junto num ramo temporário (como os grupos da fila nativa, S2)? **Recomendação: manter como exceção agora.** `reabre se:` um lote verde no fim deixar a develop vermelha.

**D5. Rótulo `afrouxa-regra` em I1, I2 e I5.** A autorização de 19/11 13:08 deixou o alcance a confirmar ("aperto e correção, ou também o que aceita mais"); o conserto aceita mais. **Recomendação: o dono aplica ou confirma o rótulo nesses três PRs.**

**D6. Modelo de projeto.** O `merge_group` no CI do modelo e o texto da proteção oferecendo a fila nativa para repositório de organização (I5, I6)? **Recomendação: sim** (neutro, sem custo, sem efeito onde a fila não existe).

## 11. Critério de reversão e leituras
Critério de reversão do F1: um conserto mesclado pelo `--conserto` deixar a develop vermelha **pela mesma falha** do run declarado. Do F2: em 30 dias, o 6c não pegar nenhuma base velha que deu vermelho no re-teste e o tempo do PR verde até a develop subir mais de 30%; então o 6c volta a só registrar.

| Data | Medida | Veredito (manter, ajustar, reverter) |
|---|---|---|
| 2026-12-19 | consertos pelo `--conserto`, quantos voltaram ao verde; ajudas do dono para sair do vermelho (base: 3 em 30 h) | pendente |
| 2026-12-19 | re-testes do 6c e quantos deram vermelho; tempo do PR verde até a develop (base: 30 a 40 min) | pendente |
