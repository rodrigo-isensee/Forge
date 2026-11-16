---
tipo: plano-tecnico
contrato: 1
pedido: v047
estado: proposta
ux: n/a (sem interface; linhas de terminal do forge-check e uma linha de skill)
adrs: [0002, 0003, 0004, 0009, 0011, 0016]
agentes: [forge:tech-lead, forge:security-engineer, forge:qa-engineer, forge:software-architect]
gatilhos_seguranca: [controles-do-forge (hooks/conformidade.py, hooks/agentes.py), autorizacao (papel que grava docs/pedidos/ e docs/briefs/), entrada-nao-confiavel (texto do pedido dentro do brief), docs/regras (R-BRIEF, só se a decisão D1 for alinhar o texto)]
---
# Desenho BRIEF-NAO-SEGURA-VAGAS (lote BR1)

Etapa E2.187 do pedido v047, brief `v047-software-architect-3`, pelo `forge:software-architect`. Só desenho, para o parecer de segurança antes do código. Base: `origin/develop` 4138445e. Parte do desenho aprovado em `docs/propostas/brief-portoes-por-ferramenta.md` (branch `melhoria/v047-brief-portoes`, head 21edf48a: segurança E1.246 aprovada com A8 e A9 recomendados, review E2.107 aprovado com A1 a A6 recomendados) e o enxuga. O que muda em relação a ele está na seção 4, um item por diferença, para a segurança reler só isso.

- **Origem:** ORDEM DO DONO 2026-11-14 15:53 (pedido v047, `## Decisões do usuário`): os briefs dos portões (review, segurança, QA, devops) saem da ferramenta a partir do pedido e do head; o Jarvis escreve à mão só os de autor; quando um agente termina, o próximo brief já está pronto; o selo continua obrigatório.
- **Constituição:** o Forge não tem `docs/constituicao.md`; conferido contra as regras com ID que o desenho toca (`R-BRIEF`, `R-PROVA`, `R-REVIEW`, `R-SEGURANCA`, `R-CONFORMIDADE`, `R-NEUTRO`, `R-CUSTO`): conforme, com o desvio de texto D1 (seção 9) levado ao dono.
- **Afrouxa controle?** Não no código: o hook `conformidade` fecha uma ação nova e o furo do programa opaco; o `brief selar` passa a recusar mais. **Sim, R-BRIEF**, só se o dono escolher alinhar o texto à lista de ids (D1); sem a decisão, o texto fica e o desenho não depende dela.
- **R-CUSTO:** só `git` local e `git ls-remote` contra o GitHub (grátis). Nenhuma API paga, nenhuma sessão do Claude nos testes.

## 1. Problema e evidência

O tempo entre "o autor terminou" e "o portão começou" é gasto pelo Jarvis escrevendo, um por vez, briefs quase todos deriváveis do pedido e do git, e as vagas ficam paradas.

| Fato | Evidência |
|---|---|
| Vagas paradas | ORDEM DO DONO 14/11 14:03: 4 agentes e 46% do processador parado com teto 16 |
| Volume | 198 de 338 briefs do v047 (59%) eram de portão em 14/11, mais 12 do devops com `Etapa: review` (contagem da proposta, seção 1) |
| Texto todo derivável | `docs/briefs/v047-security-engineer-67.md:11-16`: as 5 linhas do Entregar são etapa, clone, pasta e frontmatter do parecer, envio e `arquivos:`; nenhuma decisão do Jarvis |
| Erro de campo derivado | `## Histórico` do v047, 14/11 15:53: ERRO-JARVIS, os briefs de portão não mandavam `pedido: v047` e os pareceres saíram com o nome da branch |
| O gerador de hoje não sela no v047 | o v047 tem 628 etapas e nenhuma com `· feito` (contagem por `^- E\d+\.\d+ \(` em 16/11); a função `linha_de_outra_etapa` do `bin/forge-check` escreve cada etapa aberta com o texto inteiro, muito acima do teto de 10.000 caracteres de `R-BRIEF` (a forma da volta mediu 146 KB, cartão BRIEF-VOLTA-FORA-COMPACTO). O Jarvis compacta à mão em listas de ids, que o selo aceita (este brief: 17 linhas de ids, selado) |
| O gerador deixa lacunas | a função `montar_brief` do `bin/forge-check` deixa `PREENCHER` no Entregar, nos PQ e no `arquivos:`; o selo reprova enquanto restar um |

## 2. O que já existe e por que não basta

Existe e é reaproveitado, sem cópia (funções do `bin/forge-check`, citadas pelo nome): `montar_brief`, `sha_a_revisar`, `classe_da_entrega` e `pareceres_exigidos`, `exigidos_do_pr`, `commit_vale`, `conferencia_do_head`, `parecer_delta`, `cmd_brief_selar`, `gravar_brief` (arquivo aberto com `x`), `gravar_no_historico` (`flock`), `interpolacao_segura`, `caractere_disfarcado`, `cmd_fila` (vagas por `teto_calculado` menos `agentes_vigentes`), o hook `agentes` (selo e hash no disparo, Z10).

Não basta (evidência na tabela da seção 1 e no código):
- `brief gerar --etapa review|seguranca|qa` sai com `PREENCHER` e um destino por vez; o Jarvis roda `forge-check classe`, escolhe os destinos, abre a etapa no pedido à mão e repete por portão.
- O `Fora do escopo` literal não cabe no teto num pedido grande (628 etapas no v047).
- Nada liga "entrega conferida" a "brief do portão pronto"; o `forge-check fila` lista cartões, não briefs.
- O portão de devops não tem etapa: `ETAPAS_DE_PARECER` tem três cópias (duas no `bin/forge-check`, junto de `sha_a_revisar` e de `linha_de_outra_etapa`, e uma no `hooks/agentes.py`, junto da checagem Z10 do brief de escrita) e nenhuma tem `devops`.
- O hook `conformidade` não vê ação nova do `brief` como escrita: a função `grava_no_pedido` do `hooks/conformidade.py` só conhece `selar`, o método `forge_check_grava` só `--gravar`, e a lista do papel só de leitura libera `forge-check brief` inteiro (`hooks/conformidade.json:111`). Sonda S3 da proposta: `brief portoes` passaria em qualquer papel.
- O programa opaco já fura a política hoje, na `develop`: `args_do_forge_check` (`hooks/conformidade.py`) só devolve os argumentos do opaco com `anotar --tipo` ou `--gravar`; sondas S2 e S6 a S11 da proposta (`$(command -v forge-check) brief selar`, `pausa`, `recado` no papel de autor: rc 0). Não há cartão no quadro para esse furo.

## 3. Opções

| | O1: proposta inteira | O2: gerador enxuto (recomendada) | O3: só tirar o `PREENCHER` |
|---|---|---|---|
| O quê | 5 PRs: opaco; faixa de ids no corte e texto de `R-BRIEF`; `ETAPAS_DE_PARECER`; `brief portoes` com selo de reprodução; `brief fila` e `entrega --portoes` | 4 PRs: opaco; `ETAPAS_DE_PARECER` e o brief no registro do hook `agentes`; `brief portoes` que grava as etapas e sela na mesma execução; briefs prontos no `forge-check fila` | `gerar --etapa` de portão sai completo; o Jarvis abre a etapa e sela à mão |
| Ação nova no hook | `portoes`, `fila`, `entrega --portoes` | só `portoes` | nenhuma |
| Mexe em guarda existente | `conferir_corte` (faixa), `cmd_brief_selar` (reprodução com rede) | `cmd_brief_selar` só recusa mais (Gerado-por fora da execução) | nenhuma |
| Regra protegida | `R-BRIEF` (faixa), obrigatório | nenhuma; `R-BRIEF` só se D1 | nenhuma |
| Atende à ordem | sim | sim | em parte: o brief não está pronto quando o autor termina; a etapa segue à mão |
| Esforço relativo | G+ | G | M |
| Risco | maior superfície no hook; selo depende de rede e de determinismo byte a byte | o selo deixa de exigir leitura do Jarvis (T3, como em O1) | baixo; ganho parcial |

Recomendada: **O2**. Entrega o mesmo resultado de O1 com uma ação nova no hook em vez de três, sem mudar o corte nem a regra, e com um selo mais simples de provar (seção 4, Δ1). O3 fica como reversão (seção 10).

## 4. Diferenças em relação à proposta aprovada (para a segurança reler)

- **Δ1 Selo na mesma execução, no lugar do selo de reprodução.** O `brief portoes` monta o texto em memória, grava com `x` e chama `cmd_brief_selar` no mesmo processo, que confere que os bytes do disco são os da memória antes de gravar o selo (senão apaga o arquivo e recusa). O `brief selar` chamado da linha de comando **recusa** brief com `Gerado-por:` (rc 1, "gerado: rode brief portoes de novo ou tire a linha Gerado-por e sele como brief de autor"). Efeito igual ao da reprodução (o que leva `Gerado-por:` é exatamente o que o modelo revisado produziu; editar depois quebra o hash e o hook `agentes` recusa), sem regenerar no selo e sem rede no selo. Fecha por construção o A3 da segurança e os A4 e A5 do review (o `selar` nunca lê a branch local para brief gerado).
- **Δ2 Sem `--head`** (review A6): o head é sempre o `head_enviado` de agora.
- **Δ3 Pré-condição pela `conferencia_do_head(raiz, P, ref=origin/B, branch=B)`** (review A1), a mesma do merge, no lugar da igualdade com a última `entrega conferida`.
- **Δ4 Estado de cada portão pela mesma regra do `forge-check pr`** (review A2): extrair de `cmd_pr` a função `estado_dos_portoes(raiz, P, ref, branch, base)` que devolve `[(tipo, estado, parecer, commit)]`, com estado `ausente`, `desatualizado`, `em-dia` ou `reprovado`, e fazer o `cmd_pr` usá-la sem mudar a saída. `ausente` gera brief novo; `desatualizado` gera revalidação pelo `parecer delta`; `em-dia` imprime `portão em dia`; `reprovado` não gera (é volta do autor: imprime o comando `brief gerar --volta`).
- **Δ5 `## Ler` sem `forge-check proximo`** (review A3, cartão PROXIMO-POR-ETAPA: passa de 120 s no v047): o brief traz etapa, passo e dono no Entregar.
- **Δ6 `Fora do escopo` por lista de ids, sem faixa.** 40 ids por linha, `- E1.1, E1.2, … · outras delegações`, a forma que o Jarvis já usa e que `referencias_do_item` (`bin/forge-check`) e o `conferir_corte` já aceitam. No v047, cerca de 5 KB. Sem mudança no corte nem em `R-BRIEF` (o texto diverge do código desde já; D1).
- **Δ7 Sem `entrega --portoes`.** O Jarvis encadeia os dois comandos numa linha (`forge-check entrega --pedido P … && forge-check brief portoes --pedido P --branch B`). Some a regra do hook para `--portoes` com `--so-leitura` (sonda S5) e a combinação recusada no argparse.
- **Δ8 Sem `brief fila`.** Os briefs prontos saem numa seção do `forge-check fila`, que já é só leitura, sem rede, e já conta as vagas. `BRIEF_ACOES` fica `("gerar", "selar", "mensagem", "portoes")`.
- **Δ9 Branch validada por componente.** `NOME_SEGURO_DE_BRIEF` não aceita `/`; a proposta o aplicava à branch inteira. Regra: `git check-ref-format --branch B` e cada componente separado por `/` casa `NOME_SEGURO_DE_BRIEF`; o nome do arquivo do parecer usa o slug (B sem `melhoria/`).
- **Δ10 PQ do CI por texto fixo** (review A4): sem `linha_do_ci_do_parecer` nem `gh` no modelo.
- **Δ11 Corpus do opaco** com os recomendados da segurança: o rc esperado de cada escrita pelo opaco é o da forma direta no mesmo papel (A8: `rodar`, `meta` e `medida` passam na forma direta do autor); o critério do opaco olha a palavra original, antes do `lstrip` da crase (no `hooks/conformidade.py`, onde o `prog` sai da primeira palavra sem a crase, A9).
- **Δ12 Linha do clone no Entregar** (ORDEM DO DONO 13/11 13:57, cartão CLONE-NOME-UNICO): no Forge, o comando do clone local em `~/.forge-contrib/wt/<slug>-<papel>-<etapa>`, nome único; nos projetos, a worktree da sessão.
- **Δ13 Fila sem rede** (diverge do review A5, que pedia `head_enviado`): a validade na fila compara com `origin/B` local, para o `forge-check fila` manter o contrato P9 (sem rede). Risco residual igual ao T5 já aceito: push depois do último fetch; o parecer grava o `commit:` do brief e o `forge-check pr` aponta o delta. A skill manda `git fetch` antes da fila.

## 5. O desenho (O2)

```
forge-check brief portoes --pedido P --branch B [--classe auto|T|N|C] [--so-mostrar] [--sem-selar]
```

Ordem dentro de uma execução, falha fechada em cada passo (rc 1, nada sobra gravado em `docs/briefs/`):
1. Valida `P` (`NOME_SEGURO_DE_BRIEF`) e `B` (Δ9).
2. `head_enviado(raiz, B)`: `git -C <raiz> ls-remote origin refs/heads/B` igual a `origin/B` e ao head local (se existir). Diferente, ausente ou sem rede: recusa.
3. `conferencia_do_head` vazia sobre `origin/B` (Δ3).
4. Classe por `classe_da_entrega` e exigidos por `exigidos_do_pr` (a soma com o plano técnico, a mesma do `pr`); `--classe` só sobe (T < N < C).
5. `estado_dos_portoes` (Δ4) decide o que gerar.
6. `gravar_etapas_geradas` (seção 5.2) grava todas as etapas de uma vez, sob a trava do pedido.
7. Relê o pedido, monta cada brief em memória pelo `MODELO_PORTOES = 1`, grava com `x` e sela na mesma execução (Δ1) com todas as checagens do `cmd_brief_selar`, inclusive a E8 (decisão do dono sem a conferência do Jarvis, `pendencias_da_conferencia`: é a "decisão E8 pendente" da seção 7). Um que reprova: apaga os briefs desta execução e recusa; as etapas gravadas no passo 6 ficam no pedido e a próxima execução as reaproveita pela chave (branch, tipo, sha12) da seção 5.2.

Saída: uma linha por brief, `brief pronto: docs/briefs/<P>-<papel>-<n>.md sha256 <hash> · <tipo> · <novo|revalidação> · Revisar-sha <sha12>`, as linhas `portão em dia: <tipo> <parecer>` e uma linha de resumo. `--so-mostrar` imprime sem gravar nada (nem etapa). `--sem-selar` grava sem `Gerado-por:` para o caminho de hoje (leitura e selo à mão). rc 0 tudo pronto; 1 recusa; 2 uso.

### 5.1 Tabela dos portões e campos

| Parecer exigido | Destino | `Etapa:` | Pasta |
|---|---|---|---|
| `review` | `forge:tech-lead` | `review` | `docs/reviews/` |
| `qa` | `forge:qa-engineer` | `qa` | `docs/qa/` |
| `revisao-seguranca` | `forge:security-engineer` | `seguranca` | `docs/security/` |
| `revisao-devops` | `forge:devops-engineer` | `devops` (nova) | `docs/devops/` |

Campos, todos calculados: `Pedido:` e `pedido:` do frontmatter = o `id:` do pedido `P` (é o que a função `cmd_pr` do `bin/forge-check` compara); `Revisar-sha:` e `commit:` = `sha_a_revisar(origin/B)`; parecer em `<pasta>/<slug>.md`; `Cobre:` = a etapa gravada; `Gerado-por: forge-check brief portoes modelo 1` no cabeçalho selado. Do texto do pedido entra só a linha da etapa coberta, entre aspas, com `sem_controle` e reprovada por `caractere_disfarcado`. As decisões vão por referência, como hoje.

O Entregar é fixo por tipo (constante no código), com: a linha da etapa; o clone (Δ12); o parecer na pasta com `pedido:` e `commit:` literais; o intervalo `Base-sha..Revisar-sha` (ou o `parecer delta` na revalidação); "commit só do parecer; `git push origin B`, sem `-u`; remoto avançou: merge, sem rebase nem force; sem PR"; `arquivos: <pasta>/<slug>.md`. O devops grava só o parecer, como os outros (fronteira Z10).

### 5.2 Etapa gravada no pedido (opção 3.3b da proposta, aceita pela segurança no A2)

Mantida como na proposta, com três guardas: id calculado e linha gravada sob o mesmo `flock` do pedido; linha por expressão fechada, `^- E\d+\.\d+ \((tech-lead|qa-engineer|security-engineer|devops-engineer)\): \[branch <B>\] parecer de (review|qa|seguranca|devops) no código [0-9a-f]{12}, instância que não fez a entrega \(gerado\)$`, com `<B>` escapado e o par papel e tipo da tabela; todas as etapas antes do primeiro brief, e reaproveitamento pela chave (branch, tipo, sha12). Grupo `n`: o da última etapa que cita `[branch B]`; sem ela, recusa.

### 5.3 Hook `conformidade` (no mesmo PR do subcomando)

Da proposta, seção 3.4, reduzido a uma ação: `BRIEF_ACOES` no `bin/forge-check` usada pelo despacho (palavra solta fora dela, sem `/` e sem `.md`, sai com rc 2); no hook, `BRIEF_NO_HOOK = {"mensagem": "le", "gerar": "grava com --gravar", "selar": "grava", "portoes": "grava salvo --so-mostrar"}`, procurado em todas as palavras livres depois de `brief`; `--so-mostrar` lê só pela abreviação que o argparse resolve, sem `=` e antes de `--`; destinos `docs/pedidos/` e `docs/briefs/` nas duas raízes, então só o `jarvis` roda. Teste cruzado com o argparse: `set(BRIEF_ACOES) == set(BRIEF_NO_HOOK)` e as abreviações de `--so-mostrar` geradas do parser.

### 5.4 Fila

O `forge-check fila` ganha, antes dos cartões, a seção dos briefs prontos: os selados com `Gerado-por:` de `docs/briefs/` (raiz do projeto e `RAIZES_DE_BRIEF`), em ordem de selo, que ainda valem (`Revisar-sha` igual a `sha_a_revisar(origin/B)` e o portão ainda não em dia) e não foram disparados (o registro do hook `agentes` não cita o caminho e o sha256). Até as vagas da mesma conta; o resto sai como `espera: teto`. Vencido sai como `vencido: rode brief portoes de novo`. Uma linha por brief com o comando `forge-check brief mensagem` do disparo. A fila não lança agente.

### 5.5 Hook `agentes`

`ETAPAS_DE_PARECER` com fonte única no `bin/forge-check` (a do hook lê `forge_check().ETAPAS_DE_PARECER`, já carregado no `hooks/agentes.py` quando o brief é lido) e `devops` nela. Não afrouxa o Z10: os briefs de devops já saíam com `Etapa: review`. O registro do agente ganha `brief: {caminho, sha256}` quando o prompt cita um brief selado.

## 6. Arquivos que o código vai tocar

| Parte | Arquivos | Classe |
|---|---|---|
| P0 opaco | `hooks/conformidade.py` (`args_do_forge_check`, ponto de chamada), corpus e teste novos em `tests/`, `tests/mutantes/v047-brief-vagas-opaco.json` | C |
| PA fonte única | `bin/forge-check` (`ETAPAS_DE_PARECER`), `hooks/agentes.py` (cópia sai, `brief` no registro), `tests/test_agentes_hash_brief.py`, `tests/test_etapa_do_brief.py`, mutantes | C |
| PB subcomando | `bin/forge-check` (`brief portoes`, `estado_dos_portoes` extraída de `cmd_pr`, `head_enviado`, `gravar_etapas_geradas`, `MODELO_PORTOES`, `BRIEF_ACOES`, recusa de `Gerado-por:` no `cmd_brief_selar`), `hooks/conformidade.py` (`grava_no_pedido`, `forge_check_grava`), `tests/test_brief_portoes.py`, `tests/test_conformidade_brief_portoes.py`, mapa de testes, mutantes | C |
| PC fila e texto | `bin/forge-check` (`cmd_fila`), `skills/briefs-e-conferencia/SKILL.md` (passo 21: `entrega … && brief portoes`, depois `git fetch` e `forge-check fila` a cada agente que termina), `tests/test_brief_portoes.py`, mutantes | C |

`agents/jarvis.md` não muda (está no teto; a skill é o detalhe, diretriz 25). Cada PR com fragmento em `changelog.d/`. Nada específico de projeto (`R-NEUTRO`): pastas de parecer do modelo e catraca do projeto (sem catraca, classe C).

## 7. Testes e mutantes previstos

Todos em subprocesso com ambiente limpo e `python3 -I` (`AR-4`, `AR-5`), num repositório temporário com remoto local (sem rede real).

- **P0:** produto escritas × formas (11 × 9 = 99 casos no mínimo, afirmado no teste) com rc igual ao da forma direta no mesmo papel (Δ11); leituras nas 9 formas passam; sessão principal passa; crase pela palavra original. Mutantes: ramo do opaco devolve `None`; interpretador sem o ramo do opaco; só a primeira palavra opaca; opaco pelo `prog` sem crase.
- **PA:** sem literal da tupla no hook; `Etapa: devops` é parecer no hook e no gerador; registro grava `brief`. Mutantes: `devops` fora da constante; registro sem `brief`.
- **PB:** ouro (classe N gera review e QA; C gera review, segurança e QA; infraestrutura soma devops; sem `PREENCHER`; `pedido:` e `commit:` certos; menos de 10.000 caracteres sobre um pedido de 700 etapas); revalidação por `desatualizado`; `em-dia` não gera; `reprovado` não gera e imprime a volta; cruzamento `estado_dos_portoes` × `cmd_pr` (o conjunto que o `pr` reprova é o que o gerador gera); recusas sem entrega conferida, `ls-remote` diferente, remoto inacessível, `--classe` abaixo, branch com componente fora da forma, caractere disfarçado na etapa, decisão E8 pendente (nada sobra); `brief selar` de `Gerado-por:` recusa; arquivo alterado entre gravar e selar recusa e apaga; duas execuções paralelas não repetem id; segunda execução reaproveita a etapa; hook (formas e papéis da proposta, seção 3.4, sem as de `--portoes` e `fila`). Mutantes, um por guarda: conferência do head; `ls-remote` igual a `origin/B`; local igual ao remoto; classe só sobe; `em-dia`; `reprovado`; caractere disfarçado; recusa do `selar` de `Gerado-por:`; bytes do disco iguais aos da memória; apagar o que reprovou; expressão fechada; etapa da branch existe; chave natural; palavra solta rc 2; ação do `brief` grava salvo leitura; `--so-mostrar` lê; destino `docs/briefs/`.
- **PC:** ordem de selo; vencido não sai como pronto; disparado some; vagas zero não lista; brief sem `Gerado-por:` não entra. Mutantes: vencido na fila; disparado na fila.

Mutantes em `tests/mutantes/v047-brief-vagas[-N].json`, até 8 por arquivo (`AR-1`), escritos no mesmo commit da linha vigiada (`AR-12`).

## 8. Achados recorrentes (PA-7), conferidos

`AR-1` seção 7; `AR-2` cada recusa tem teste de comportamento; `AR-3` leitura por lista fechada no hook e opaco sem lista; `AR-4` e `AR-5` seção 7; `AR-6` o modelo não põe `|| true` nem `2>/dev/null` nos PQ; `AR-7` todo `git` do gerador com `-C <raiz>`, nunca o diretório corrente; `AR-8` envolvedores na sonda S11 do corpus P0; `AR-9` a skill cita `R-BRIEF`, sem repetir o teto; `AR-10` o PQ do brief só leva valores de `interpolacao_segura`; `AR-11` teste cruzado com o argparse; `AR-12` seção 7; `AR-13` a branch passa por `check-ref-format`, que recusa `*`, `?` e `[` (o `ls-remote` do PQ não vira padrão).

## 9. Riscos e decisões em aberto

- **D1 (dono):** o texto de `R-BRIEF` diz "com o trecho literal" e o selo aceita ids desde já. Recomendação: alinhar para "pelo trecho literal ou pelo id" num PR próprio com destaque (troca texto de `docs/regras/`: sim, R-BRIEF). Sem a decisão, o gerador usa a forma que o selo já aceita e o Jarvis já usa; reabre se: um parecer de review apontar a divergência como bloqueante.
- T3 (selo sem leitura do Jarvis) é aceito pela ordem do dono de 14/11 15:53; `R-BRIEF` não exige leitura humana.
- Modelo errado vale para todos os briefs até a correção: teste de ouro e `MODELO_PORTOES` versionado.
- Extrair `estado_dos_portoes` mexe no portão do merge: a saída do `pr` não muda (testes do `pr` sem alteração) e o teste cruzado amarra os dois.
- Tempo: meta de até 30 s para três portões no v047, medida pelo Jarvis na primeira semana; o `forge-check proximo` lento mostra que o pedido grande custa.
- `agentes.json` perdido: a fila pode repetir um brief já disparado; o parecer na `origin/B` é a segunda prova; parecer duplicado é custo, não defeito.
- Permissão do papel do portão para criar o clone do Δ12 em `~/.forge-contrib/wt/`: a verificar na PB por sonda; se o hook recusar, a linha vira "clone pronto" e o Jarvis o cria no disparo.

## 10. Medida e reversão

- Medida: tempo entre a `entrega conferida` e o disparo do primeiro portão (`## Histórico` e `agentes.json`), nos dois pedidos seguintes, antes e depois; fração de briefs de portão com `Gerado-por:`. Meta: mediana abaixo de 2 minutos e nenhum `pedido:` ou `commit:` errado em parecer.
- Critério de reversão: em 30 dias, um parecer com campo errado vindo do modelo, ou a mediana sem cair. Reversão: `--sem-selar` com leitura do Jarvis (O3), sem tirar código.

## 11. Divisão de tarefas

1. P0 (`tech-lead`) e PA (`tech-lead`, outro autor): em paralelo, arquivos diferentes; portões review, segurança e QA em cada um.
2. PB depois de P0 (mesmo `hooks/conformidade.py`) e de PA (`devops` na constante); portões review, segurança e QA.
3. PC depois de PB; portões review, segurança e QA.
4. ADR do selo na mesma execução (próximo número livre na `develop`) pelo `software-architect`, no PR da PB.
5. Cartão novo para o furo do opaco (P0), que hoje não está no quadro: o Jarvis o abre.

## Critério de parada

- bloqueia: papel que não é o jarvis grava em docs/pedidos/ ou docs/briefs/ pelo forge-check (brief portoes, abreviação, programa opaco ou interpretador), ou um brief com Gerado-por é selado fora da execução que o gerou
- acao-brief · ação do brief que grava classificada como leitura no hook · oráculo: python3 -m unittest tests.test_conformidade_brief_portoes
- abreviacao · opção abreviada lida diferente pelo hook e pelo argparse · oráculo: python3 -m unittest tests.test_conformidade_brief_portoes
- opaco · forge-check por substituição, crase, variável ou interpretador fora da política do papel · oráculo: python3 -m unittest tests.test_conformidade_opaco
- selo-fora · brief com Gerado-por selado pelo brief selar da linha de comando ou com bytes diferentes dos gerados · oráculo: python3 -m unittest tests.test_brief_portoes
- etapa-forjada · linha gravada em Etapas fora da expressão fechada ou com id repetido · oráculo: python3 -m unittest tests.test_brief_portoes
- injecao-pedido · texto do pedido fora das aspas no brief gerado · oráculo: python3 -m unittest tests.test_brief_portoes
- gatilho · oráculo: python3 -m unittest tests.test_conformidade_opaco tests.test_conformidade_brief_portoes tests.test_brief_portoes
