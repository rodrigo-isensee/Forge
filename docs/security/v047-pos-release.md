---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-pos-release
commit: ddc16953b247ade5bb8a1b33a0ade9096fc04f20
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-pos-release

Etapa E2.225 do pedido v047 (POS-RELEASE-SCRIPT-UNICO, E2.223), revalidada em E2.238 (volta 1). Escopo: `templates/projeto/scripts/pos-release`, `templates/projeto/docs/devops/pos-release.md`, `templates/projeto/docs/devops/pos-release.passos`, `tests/test_pos_release.py`, os mutantes e o fragmento de changelog, entre a base 9d10894f e o head 76e00f85.

## Gatilhos
- Banco (`R-SEGURANCA`): o script é o portão que decide se os passos (migração, cargas) rodam na base real ou numa descartável; a trava do alvo é o controle revisado.
- Segredos e configuração (`R-SEGURANCA`): o alvo pode ser a conexão com credencial, e o script promete mascará-la na saída.

## Achados
- A1 (recomendado) templates/projeto/scripts/pos-release:31 · Corrigido no head 76e00f85: só linha vazia ou que começa por # é pulada; linha recuada cai na recusa da linha 32 (S1 e S2 recusam). Mantido como registro; não bloqueia mais.
- A2 (recomendado) templates/projeto/scripts/pos-release:56 · Corrigido no head 76e00f85: máscara até o último @ e valor de password/senha/token/secret mascarado. Resta api_key= e outras chaves fora da lista, que saem em claro (S5); considere não imprimir o alvo.
- A3 (recomendado) templates/projeto/docs/devops/pos-release.md:8 · Corrigido no head 76e00f85: o .md e o .passos dizem que alvo-variavel é a mesma variável que os passos leem.
- A4 (recomendado) templates/projeto/docs/devops/pos-release.passos:13 · Corrigido no head 76e00f85: exemplo com host e base literais e aviso de que * atravessa / e ?.
- A5 (recomendado) templates/projeto/scripts/pos-release:36 · Linha padrao: sem recuo e com comentário no fim guarda o comentário no valor e a trava do valor padrão some calada (S4); o .passos:11 já avisa. Recusar valor de padrao com espaço seguido de # fecha de vez.

## Sondas
- S1 · passos com `  padrao: db://h/descartavel-1 # valor` e ensaio-aceita db://*/descartavel-*, ALVO=db://h/descartavel-1, modo ensaio · espera: saída 2 · obtido: no head 76e00f85, saída 2, RECUSADO linha que não entendo (no head fb7dccb4: saída 0, OK)
- S2 · passos com `passo: um :: echo RODOU` e `  passo: dois :: echo DOIS # x`, alvo descartável, modo ensaio · espera: saída 2 · obtido: no head 76e00f85, saída 2, RECUSADO linha que não entendo (no head fb7dccb4: saída 0, 1 de 1)
- S3 · linha só com tab e # e linha só com espaços · espera: ignoradas · obtido: ignoradas, saída 0
- S4 · `padrao: db://h/descartavel-1 # env` sem recuo, ALVO=db://h/descartavel-1, modo ensaio · espera: saída 2 (ideal) · obtido: saída 0, OK (A5, recomendado)
- S5 · alvos db://u:p@ss@h/x e db://u:a/b@h/x; o valor das chaves password, senha e token na consulta (minúsculas, PASSWORD no formato host=h, Token); o da chave api_key · espera: credencial mascarada · obtido: as cinco primeiras mascaradas; api_key em claro (A2)
- S6 · planejar() do bin/forge-testes nos três arquivos do pos-release do modelo e em dois vizinhos (scripts/pos-releaseX, migrations/x.sql) · espera: test_pos_release só nos três · obtido: head ddc16953, nos três (31 módulos) e não nos vizinhos (30); base 472a09f4, em nenhum (30)

## Revalidação (volta 1, fb7dccb4..76e00f85)
Delta lido por `forge-check parecer delta`: no domínio, `templates/projeto/scripts/pos-release`, `templates/projeto/docs/devops/pos-release.md` e `.passos`; fora, testes, mutantes, changelog e achados-recorrentes. A1 (único bloqueante) foi corrigido pela correção mínima proposta: o regex `^[[:space:]]*(#|$)` só pula linha vazia ou comentário, e toda linha de chave recuada cai na recusa da linha 32; S1 e S2 rodadas de novo no head recusam sem comando executado. Os recomendados A2, A3 e A4 foram atendidos. A nova máscara usa a flag `I` do sed GNU; num sed sem ela, o `sed` falha e a máscara sai vazia, o que não vaza a credencial (só perde o alvo no resumo). A5 é da mesma família de A1 (dimensão nova: comentário no fim de linha sem recuo), anterior a este delta, com os portões positivos (`ensaio-aceita`, `real-aceita`) de pé e aviso escrito no `.passos`; fica recomendado. Testes do item: `python3 -m unittest tests.test_pos_release`, 20 testes OK no head 76e00f85; linter de shell limpo.

## Revalidação (volta 2, 76e00f85..472a09f4)
Delta lido por `forge-check parecer delta`: nenhum arquivo do domínio mudou; fora dele, `tests/test_pos_release.py` (a fixture passou a montar o valor da consulta em duas partes, sem mudar o que o teste confere), o fragmento de changelog e `docs/engineering/achados-recorrentes.md`; a develop entrou por merge e fica fora do escopo. A linha da sonda S5 foi reescrita descrevendo as chaves em vez de citar chave e valor, para a varredura de segredo do CI (`scripts/verificar-contribuicao.sh`) não a barrar; as sondas, os achados e o parecer não mudam.

## Revalidação (volta 3, 472a09f4..ddc16953, E2.401)
Delta lido por `forge-check parecer delta`: no domínio, só `bin/forge-testes`, uma regra nova no `MAPA` que leva `templates/projeto/docs/devops/pos-release.md`, `.passos` e `templates/projeto/scripts/pos-release` a `PUBLICADO` + `test_pos_release`. O `planejar` usa a primeira regra que casa; a nova vem antes de `(migrations|templates)/.*` e nenhuma anterior casa esses caminhos, então o conjunto de testes dirigidos é o de antes mais `test_pos_release`, sem perder módulo (S6); o `fullmatch` não pega nome vizinho. O mapa é filtro do envio local, não portão de CI (a suíte inteira roda no CI). Sem achado novo; A1 a A5 sem mudança. Testes do item: `python3 -m unittest tests.test_pos_release`, 20 OK no head ddc16953.

## Detalhe dos achados (rodada 1, head fb7dccb4)
**A1** · evidência: `templates/projeto/scripts/pos-release:31`, o padrão `[[:space:]]*'#'*` do `case`; no glob, o `*` do meio casa qualquer texto, então a linha é pulada se começa com um espaço e tem `#` em qualquer posição. O cabeçalho do `.passos` diz que só comentário é ignorado, e a linha 32 promete recusar o que não entende. Caminho: não há atacante; é falha de segurança operacional. Uma linha `padrao:` recuada com comentário some sem aviso e o alvo padrão passa no ensaio (S1); uma linha `passo:` recuada some e o resumo diz `OK · 1 de 1` (S2). Severidade média. Correção mínima: `[[ "$linha" =~ ^[[:space:]]*(#|$) ]] && continue` no lugar do `case`. Esforço P. Dono: `devops-engineer`. Aplicada no head 76e00f85.

**A2** · evidência: `pos-release:55` (rodada 1), `sed -E 's#(://)[^/@]*@#\1***@#'`: senha com `@` vazava em parte, com `/` inteira, e `?password=` em claro. Caminho: a saída vai ao terminal e, em CI, ao log; quem lê o log ganha a credencial da base. Severidade baixa. Correção aplicada no head 76e00f85 (linha 56); resta a lista fechada de chaves (S5). Dono: `devops-engineer`.

**A3** · evidência: `pos-release.md:8-9` e `.passos` sugeriam uma variável dedicada; se `./scripts/migrar.sh` conecta pela variável do `.env`, o ensaio passa a trava com um alvo descartável e migra a base real. Severidade baixa. Texto corrigido no head 76e00f85. Dono: `devops-engineer`.

**A4** · evidência: `.passos`, exemplo `*://*/descartavel-*`; no `case`, `*` casa `/`, `?` e `@`. Sem atacante realista. Exemplo corrigido no head 76e00f85. Dono: `devops-engineer`.

**A5** · evidência: `pos-release:32-36`; `padrao: X # comentário` sem recuo casa a linha 32 e o valor guardado é `X # comentário`, que nunca é igual ao alvo; a trava do valor padrão deixa de valer sem aviso (S4). Também vale antes deste delta. Caminho: erro de quem preenche, sem atacante; os portões positivos continuam exigindo que o alvo case `ensaio-aceita` ou `real-aceita`. Severidade baixa. Correção mínima: recusar valor de qualquer chave que contenha espaço seguido de `#` (ou tirar o comentário do fim). Esforço P. Dono: `devops-engineer`.

Conferido sem achado: o nome de `alvo-variavel` é validado como identificador antes da expansão indireta (linha 49); os passos vêm do arquivo versionado do projeto (mesma fronteira de confiança dos próprios scripts), recebem `stdin` de `/dev/null` e rodam na raiz; a ambiguidade entre as duas listas é recusada nos dois modos; a trava é lista positiva (não repete AR-3); valor vazio e ausente recusam sem reserva; o linter de shell passa limpo; nada específico de projeto no modelo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do item: `python3 -m unittest tests.test_pos_release` na raiz do clone, 17 testes OK no head fb7dccb4 e 20 OK no head 76e00f85; sondas S1 a S5 rodadas numa cópia de trabalho em pasta temporária. A suíte inteira roda no CI do PR (não citada aqui como verde: o head não tem PR). Ferramentas: linter de shell presente (limpo); varredor de segredos, SAST e varredor de workflows ausentes no PATH (lacuna; não instalados, `R-CUSTO`), sem efeito neste diff (sem segredo, dependência nem workflow).
