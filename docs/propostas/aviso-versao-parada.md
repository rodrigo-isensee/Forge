# Aviso de versão parada no projeto

Propósito: desenhar como o projeto avisa o dono quando a versão do Forge que ele usa ficou para trás da `main`, sem esperar ele perguntar (cartão AVISO-VERSAO-PARADA-NO-PROJETO, pedido v0478, E69.1). Público: dono do Forge, `tech-lead`, `security-engineer`, `devops-engineer`. Revisão: 2026-11-21.

Estado: proposta. Nada aqui está implementado; a escolha da opção é do dono (`R-DECISAO`).

Legenda: **[COD]** lido no código desta branch (base `bead3e53`); **[INF]** inferência de desenho, a provar na implementação.

## 1. O que já existe e onde a versão fica parada

Três peças cuidam da versão hoje:

| Peça | O que faz | Onde |
|---|---|---|
| `bin/forge-sempre-atual` (ADR 0017) | Atualiza o plugin na abertura pelo atalho `jarvis`, `jarvis-forge` e no postStart do container. Processo do dono, fora do sandbox; nenhum agente atualiza nada. | `scripts/jarvis:29-42` [COD] |
| Doutor, no `Stop` | Uma consulta por dia (`git ls-remote --tags`, 3 s, só https) e cache em `.forge/run/versao-nova`. Avisa por `systemMessage`, que vai ao dono e não ao modelo (ADR 0003). | `hooks/doutor.py:85-127` [COD] |
| Guarda de versão do `forge-check` (VERSAO-DEFASADA) | Lê o cache do doutor e bloqueia `pr`, `entrega` e `brief` no projeto quando há prova positiva de atraso. | pedido `versao-defasada`, decisão de 2026-10-19 |

A versão fica parada sem o dono saber em cinco casos. Os quatro primeiros saem da leitura do código e o quinto do registro da ferramenta:

- **P1. Sessão viva há dias.** Com a sessão tmux do projeto aberta, o `jarvis` só reanexa e não chama a atualização (`scripts/jarvis:41`) [COD]. A sessão continua na versão que carregou.
- **P2. Abertura sem o atalho.** O projeto aberto por `claude` direto, pela IDE ou por `--plugin-dir` nunca passa pela `forge-sempre-atual` [INF: depende de como cada pessoa abre].
- **P3. Adiamento repetido.** A atualização é adiada enquanto houver trabalho em curso. O doutor só avisa a partir do segundo adiamento e uma vez por contagem (`hooks/doutor.py:171-178`) [COD].
- **P4. Falha da ferramenta** (`falhou:origem-da-tag`, `falhou:sem-claude`, `falhou:lista`…). Só fica no `registro.log`, salvo a volta que falha, que gera aviso (`bin/forge_sempre_atual.py:780`) [COD].
- **P5. Fixação do dono.** Há um aviso, uma vez por versão (`bin/forge_sempre_atual.py:605`) [COD]. Este caso é intencional e fica fora deste desenho.

Hoje o aviso do doutor é o mesmo nos casos P1 a P4. Ele diz que a versão "entra sozinha na próxima abertura do Jarvis sem trabalho em curso. Nada a fazer" (`bin/forge_versoes.py:145-164`) e sai **uma vez por versão** (`hooks/doutor.py:116-117`) [COD]. Isso traz três problemas:
- nos casos P1, P2 e P4 o "nada a fazer" é falso;
- depois do primeiro aviso, o atraso fica mudo até sair a versão seguinte;
- ninguém mede quanto tempo o atraso durou.

### Por que o existente não basta
| O que existe | Por que não basta | Evidência |
|---|---|---|
| Aviso do doutor | Uma vez por versão, com o mesmo texto para todas as causas; compara a última tag com a versão que a sessão carregou, mas não diz por que ela não subiu. | `bin/forge_versoes.py:164` e `hooks/doutor.py:116` [COD]. Antes da ADR 0017, um escopo de projeto ficou na 0.45.2 de 10/11 a 15/11, com três versões publicadas depois (ADR 0017, Contexto). |
| `forge-sempre-atual` | Só roda na abertura pelo atalho. Na reanexação e no `claude` direto, não roda. | `scripts/jarvis:41` [COD] |
| Guarda do `forge-check` | Só barra quando o agente tenta `pr`, `entrega` ou `brief`. O dono fica sabendo pelo Jarvis, depois do bloqueio, e não antes. | Decisão do dono de 2026-10-19 no pedido `versao-defasada`. |

Lacuna: a evidência acima vem da leitura do código e da ADR 0017, sem execução nova. A primeira tarefa da implementação (seção 8, T1) reproduz P1 e P2 numa fixture e grava a saída. Sem essa reprodução, o desenho não entra.

## 2. Requisitos
- RF1. O projeto avisa o dono quando a versão **carregada na sessão** está atrás da última tag `vX.Y.Z`, que é a da `main` (as tags `v*` nascem do `release.yml` no push da `main`, ADR 0017 item 2).
- RF2. O aviso diz a causa e o comando exato para o dono atualizar. O agente nunca atualiza nada (pedido `versao-defasada`, Fora do escopo; R-CONFORMIDADE).
- RF3. O aviso não se repete a cada turno e também não fica mudo enquanto o atraso durar.
- RF4. O aviso funciona sem rede, só com o que já está na máquina, e diz quando não conseguiu conferir.
- RF5. Mede, para cada versão, os dias entre a `main` subir e o aviso chegar ao dono.
- RNF. Custo zero (`R-CUSTO`): só o `git ls-remote` público que já existe, nenhuma API paga e nenhum token do modelo. Neutro (`R-NEUTRO`): o endereço vem do `repository` do `plugin.json` e nenhum projeto é citado. Sem mexer em `hooks/conformidade.py` nem em `bin/forge-check`, que estão pausados até a promoção da 0.47.13.

Suposições:
- S1. Pelo contrato dos hooks e pela ADR 0003, a `systemMessage` do `Stop` aparece para o dono e não entra no contexto do modelo [COD: `hooks/doutor.py:8`].
- S2. "Versão da main" é a maior tag `v*` publicada. Entre o merge na `main` e a tag passam minutos (`release.yml`) [INF].

## 3. De onde vêm as duas versões, sem custo e sem rede obrigatória

| Dado | Fonte primária, sem rede | Fonte de reserva |
|---|---|---|
| Versão **carregada** na sessão | `plugin.json` da raiz do plugin que roda o hook (`versao_do_plugin`, `bin/forge_versoes.py:35`) [COD] | — |
| Versão **instalada** no escopo | `~/.claude/plugins/installed_plugins.json`, entrada `forge@forge` do escopo do usuário e do projeto, lida como a `forge-sempre-atual` já lê (`projectPath`, `bin/forge_sempre_atual.py:361`) [COD] | — |
| Versão da **main** | Cache `.forge/run/versao-nova` (`ultima`, `data`), da última consulta que deu certo | Estado da `forge-sempre-atual` (`~/.claude/plugins/data/forge-forge/forge/sempre-atual/`), que traz a última tag vista na abertura |
| Causa | Estado e `registro.log` da `forge-sempre-atual`: adiado, falhou, fixado ou a última abertura que rodou | Sem o estado: causa "abertura sem o atalho" |

A rede aparece só no `git ls-remote --tags` que o doutor já faz, uma vez por dia. Nada novo vai à rede. Se a consulta falhar, o aviso usa o valor guardado e mostra a data dele (seção 6).

Comparar a versão **carregada** com a **instalada** separa P1 de P2:
- carregada < instalada: o plugin já subiu, mas a sessão é antiga (P1);
- instalada < main: o plugin não subiu (P2, P3 ou P4, conforme o estado da ferramenta).

## 4. O texto do aviso, por causa

Uma linha só, na mesma `systemMessage` do doutor, que já junta os avisos com " · ". `<n>` é o número de dias desde que a versão foi vista pela primeira vez (seção 7).

| Causa | Texto |
|---|---|
| P1 sessão antiga | `Forge parado há <n> dias: esta sessão usa a <carregada> e a instalada já é a <instalada>. Para atualizar: digite /exit e rode jarvis no terminal.` |
| P2 sem o atalho | `Forge parado há <n> dias: você usa a <carregada> e a main está na <main>. Para atualizar: feche esta sessão e abra pelo jarvis; ou, num terminal fora do Claude: forge atualizar` |
| P3 adiado | `Forge parado há <n> dias na <carregada> (main na <main>): a atualização foi adiada <k> vezes por trabalho em curso. Para atualizar: quando o trabalho parar, digite /exit e rode jarvis.` |
| P4 falha | `Forge parado há <n> dias na <carregada> (main na <main>): a atualização automática falhou (<etapa>). Para atualizar, num terminal fora do Claude: forge atualizar` |
| Sem conferir | `Forge: versão não conferida há <d> dias (sem rede); a última main vista foi a <main> em <data>.` |

Regras do texto:
- Só comandos que a pessoa roda: `/exit`, `jarvis` e `forge atualizar`. O `forge atualizar` recusa rodar dentro do Claude (`bin/forge_versoes.py:526`) [COD], então um agente não consegue rodá-lo. O agente não recebe nenhum comando.
- P5 (fixação do dono) segue com o aviso da `forge-sempre-atual`, uma vez por versão, e fica fora desta regra.
- O texto "Nada a fazer" sai de `SUPERFICIES["projeto"]` só no caso de atraso. O aviso de "saiu a versão nova", no dia em que ela aparece e antes de qualquer abertura, continua igual.
- Na sessão do Forge (superfície `forge`) vale a decisão D de 2026-10-20 (só avisa). A mesma regra se aplica, com o comando de `jarvis-forge`.

## 5. Quando avisa e como não repetir

- **Onde:** no `Stop` do doutor, que já roda e já tem a trava e o cache. O `SessionStart` fica fora porque o stdout dele vira contexto do modelo (ADR 0003, `hooks/doutor.py:5`).
- **Quando:**
  - no dia em que a versão nova é vista, o aviso de hoje ("saiu a versão", sem mudança);
  - **a partir de 2 dias** com a sessão ainda atrás, o aviso de parado, com a causa;
  - depois, **um por dia** enquanto o atraso durar.
- **Não repete:** o cache ganha `parado_avisado_em` (a data). Com a mesma data no cache, fica em silêncio. Se outra sessão do mesmo projeto já avisou hoje, também fica em silêncio, porque a trava do hook é por projeto. Se a causa mudar no mesmo dia (de P3 para P4, por exemplo), avisa mais uma vez.
- **Para:** quando a versão carregada alcança a última vista. O registro grava o fechamento (seção 7).
- **N = 2 dias:** P1 é o caso mais comum, e um dia de sessão viva é normal. Dois dias já é uma sessão esquecida. O N fica numa constante do hook, não em configuração do projeto, para o projeto não conseguir desligar o aviso. Quem muda o N é o dono, por PR no Forge.

## 6. Sem rede
- A consulta falha e o cache tem `ultima` de outro dia: o aviso de parado continua com esse valor, porque continua sendo prova positiva de atraso (a tag existia).
- O texto diz "a main vista em <data>". A falha não marca o dia (`hooks/doutor.py:107-110`) [COD].
- Sem cache nenhum (projeto que nunca chegou à rede): o aviso "versão não conferida", **uma vez por semana**. Esse é o resíduo que o pedido `versao-defasada` já registrou ("projeto que nunca consultou a rede").
- Consulta desligada (`FORGE_VERIFICAR_VERSAO=0`): o aviso diz que está desligada, uma vez por semana, como o `forge-check` já faz para o R1 da VERSAO-DEFASADA. Nada fica mudo.

## 7. A medida
**Medida do cartão:** dias entre a `main` subir e o aviso chegar ao dono, por versão.

O `ls-remote` não traz a data da tag. A medida usa dois instantes que o projeto conhece sem rede nova:
- `vista_em`: a primeira consulta que viu a tag. É um limite superior da publicação, porque a consulta é diária quando há sessão;
- `publicada_em`: a data de `## [X.Y.Z] - AAAA-MM-DD` no `CHANGELOG.md` da versão nova. Ela fica legível quando a versão é instalada. É a data da marca, que vem antes da `main` e por isso subestima o atraso.

Registro: uma linha por evento em `.forge/run/versao-parada.log`, no formato `versao · vista_em · avisada_em · causa · alcancada_em`. Cada linha guarda:
- **atraso do aviso** = `avisada_em − vista_em`. O alvo é ≤ 2 dias;
- **dias parado** = `alcancada_em − vista_em`.

Esta é uma leitura nova. O `forge doutor` mostra a mediana das duas medidas nas últimas 5 versões, sem token. O arquivo só mede e não decide nada: um agente que o grave estraga só a medida. Se o `security-engineer` pedir trava, ele vai a `quem: []` na E69 seguinte, e não aqui, porque `hooks/conformidade.json` está pausado.

Alternativa para a medida, não recomendada agora: ler a data da release no feed público `releases.atom` do repositório. É grátis e sem token, mas faz mais uma ida à rede por dia. Só entra se a leitura mostrar que `vista_em` erra por mais de 1 dia.

## 8. Opções

| Opção | O que é | Cobre | Custo | Afrouxa |
|---|---|---|---|---|
| **A (recomendada)** | Seções 3 a 7 no doutor e em `bin/forge_versoes.py`: causa, comando, um aviso por dia a partir de 2 dias, sem rede com o valor guardado e a medida. | P1 a P4 em qualquer forma de abrir o Claude no projeto | Rede: zero a mais (o mesmo `ls-remote` diário). Tokens: zero (a `systemMessage` não vai ao modelo). Tempo por `Stop`: leitura de 2 JSON locais, < 10 ms [INF]. Trabalho: médio (hook e `bin/`, com segurança e QA). | não |
| B | Só no atalho: na reanexação, o `jarvis` imprime no terminal a versão carregada × a instalada × a última vista no estado da ferramenta, com o comando. | Só P1, e só quando a pessoa reanexa pelo atalho | Zero de rede e de tokens. Trabalho: pequeno (só `scripts/jarvis`, sem hook). | não |
| C | Avisar o Jarvis (contexto do modelo ou saída do `forge-check`) para ele falar com o dono. | P1 a P4, mas só quando o Jarvis fala | Tokens recorrentes em toda sessão atrasada. Exige `bin/forge-check` (pausado) ou emenda à ADR 0003. É a VD-4, já descartada em 2026-10-19. | sim, ADR 0003 item 1 (o hook sem violação não fala ao modelo) |

Recomendação: **A**, e **B** junto se o dono quiser o aviso também no terminal antes de reanexar. As duas não se sobrepõem: B avisa antes de abrir e A avisa durante a sessão, e o cache de A evita a repetição no mesmo dia. C fica fora.

## 9. Riscos
- R1. **Ruído.** Um aviso por dia pode virar hábito de ignorar. Mitigação: só a partir de 2 dias, com causa e comando; e a leitura da medida (critério de reversão abaixo).
- R2. **`installed_plugins.json` é um arquivo interno da CLI** e o formato pode mudar. Leitura em falha deixa de lado a distinção P1/P2 e cai no texto P2, que também está certo.
- R3. **Gatilho de segurança:** o desenho mexe em hook (`hooks/doutor.py`) e lê arquivo do usuário fora do projeto. Ele só lê, nunca grava fora de `.forge/run/`, e não segue link (como `avisos_do_sempre_atual`, `hooks/doutor.py:186-192`). O parecer do `security-engineer` é portão da implementação.
- R4. **AR-9 (limite antigo no texto):** o README diz que o Jarvis avisa "uma vez por dia" quando sai versão nova e que ela "entra sozinha na próxima abertura" (`README.md:82`), mas o código avisa uma vez por versão (`hooks/doutor.py:116-117`); o texto precisa mudar junto.

Critério de reversão: duas versões seguidas com mediana de **dias parado** sem queda em relação às duas anteriores, com o aviso de parado entregue (linha `avisada_em` presente). O aviso não muda o comportamento e volta à regra de uma vez por versão.

## 10. Divisão de tarefas (opção A)
| # | Agente | O quê | Depende |
|---|---|---|---|
| T1 | `qa-engineer` | Fixture que reproduz P1 (carregada < instalada) e P2 (instalada < cache), com a saída atual do doutor gravada como prova da lacuna (seção 1). | — |
| T2 | `security-engineer` | Modelo de ameaça curto: leitura de `installed_plugins.json` e do estado da ferramenta (link, dono, tamanho), texto do aviso sem dado do arquivo além das versões validadas por `versao_de`. | — (paralelo a T1) |
| T3 | `tech-lead` | Implementação em `hooks/doutor.py` e `bin/forge_versoes.py` (causa, texto, N = 2, `parado_avisado_em`, sem rede, `versao-parada.log`), mais `README.md` e `docs/hooks.md`; fragmento `changelog.d/`. | T1, T2 |
| T4 | `tech-lead` (outra instância), `security-engineer`, `qa-engineer` | Portões da classe (hook e `bin/`), com mutantes nos ramos de causa e de sem rede (AR-1, AR-2). | T3 |
| T5 (se B) | `tech-lead` | `scripts/jarvis` na reanexação; parecer de `devops-engineer` (atalho). | paralelo a T3 |

Afrouxa: não. Nada sai de `docs/regras/`, de `tests/config.json` nem de controle. O texto "Nada a fazer" muda só no caso de atraso, e nenhum agente ganha escrita nem comando novo.
