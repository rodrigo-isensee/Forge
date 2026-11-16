---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-pos-release
commit: fb7dccb4f31f290b147879709dafff67cebc7038
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-pos-release

Etapa E2.225 do pedido v047 (POS-RELEASE-SCRIPT-UNICO, E2.223). Escopo: `templates/projeto/scripts/pos-release`, `templates/projeto/docs/devops/pos-release.md`, `templates/projeto/docs/devops/pos-release.passos`, `tests/test_pos_release.py`, os mutantes e o fragmento de changelog, entre a base 9d10894f e o head fb7dccb4.

## Gatilhos
- Banco (`R-SEGURANCA`): o script é o portão que decide se os passos (migração, cargas) rodam na base real ou numa descartável; a trava do alvo é o controle revisado.
- Segredos e configuração (`R-SEGURANCA`): o alvo pode ser a conexão com credencial, e o script promete mascará-la na saída.

## Achados
- A1 (bloqueante) templates/projeto/scripts/pos-release:31 · O glob trata como comentário toda linha que começa com espaço e tem # em qualquer lugar: padrao ou passo recuado com comentário no fim some calado; o valor padrão passa e o resumo diz OK com o passo pulado (S1, S2).
- A2 (recomendado) templates/projeto/scripts/pos-release:55 · A máscara só cobre usuário:senha@ sem / nem @ na senha; senha com @ vaza em parte, com / vaza inteira, e senha em parâmetro de consulta ou em chave=valor sai em claro, contra a garantia escrita em docs/devops/pos-release.md:16.
- A3 (recomendado) templates/projeto/docs/devops/pos-release.md:8 · O exemplo usa uma variável própria (ALVO_POS_RELEASE); se os passos leem a conexão de outra variável ou do .env, o script confere um alvo e os passos usam outro. Diga que alvo-variavel é a variável que os passos de fato usam.
- A4 (recomendado) templates/projeto/docs/devops/pos-release.passos:31 · No glob do exemplo o * atravessa / e ?, então *://*/descartavel-* aceita uma base real com sufixo de consulta; recomende regra com host e base literais no ensaio-aceita.

## Sondas
- S1 · passos com `  padrao: db://h/descartavel-1 # valor do env` e ensaio-aceita db://*/descartavel-*, ALVO=db://h/descartavel-1, modo ensaio · espera: rc=2 RECUSADO valor padrão · obtido: rc=0, passo rodou, pos-release: OK
- S2 · passos com `passo: um :: echo RODOU` e `  passo: dois :: echo DOIS # x`, alvo descartável, modo ensaio · espera: rc=2 linha que não entendo, ou 2 de 2 · obtido: rc=0, pos-release: OK · 1 de 1 passos (o passo dois sumiu calado)

## Detalhe dos achados
**A1** · evidência: `templates/projeto/scripts/pos-release:31`, o padrão `[[:space:]]*'#'*` do `case`; no glob, o `*` do meio casa qualquer texto, então a linha é pulada se começa com um espaço e tem `#` em qualquer posição. O cabeçalho do `.passos` (`pos-release.passos:22`) diz que só comentário é ignorado, e a linha 32 promete recusar o que não entende. Caminho: não há atacante; é falha de segurança operacional. O `devops-engineer` ou o dono recua uma linha e põe um comentário no fim; a linha `padrao:` (a trava contra o valor de reserva do `.env.example`) some sem aviso e o alvo padrão passa no ensaio (S1); uma linha `passo:` recuada (por exemplo a migração) some e o resumo diz `OK · 1 de 1`, e o dono acha que a release foi aplicada (S2). Os portões positivos (`ensaio-aceita`, `real-aceita`) continuam valendo, por isso a severidade é **média** e não alta, mas o resumo falso e a trava apagada são defeito de comportamento provado no controle que guarda a base real (`R-SEGURANCA`, gatilho banco). Correção mínima: pular só linha vazia ou cujo primeiro caractere não branco é `#`, por exemplo `[[ "$linha" =~ ^[[:space:]]*(#|$) ]] && continue` no lugar do `case` da linha 31; qualquer outra linha recuada cai na recusa da linha 32. Teste: as duas entradas de S1 e S2 dão rc=2 e nenhum comando roda (mais o mutante que volta o glob antigo). Esforço P. Dono: `devops-engineer` (autor de E2.223).

**A2** · evidência: `pos-release:55`, `sed -E 's#(://)[^/@]*@#\1***@#'`. Sondado: `db://u:p@ss@h/...` sai `db://***@ss@h/...` (parte da senha); `db://u:a/b@h/...` sai inteiro; `...?password=XYZ` sai inteiro. Caminho: a saída vai ao terminal do dono e, se rodar em CI, ao log; quem lê o log ganha a credencial da base. Severidade baixa (senha com `@` ou `/` sem codificação já é URI inválida para a maioria dos clientes; a forma de consulta é válida). Correção mínima: máscara gulosa até o último `@` (`s#(://).*@#\1***@#`) e mascarar `password=`/`senha=` em consulta e em chave=valor, ou não imprimir o alvo, só o nome da variável e a regra que casou. Esforço P. Dono: `devops-engineer`.

**A3** · evidência: `pos-release.md:8-9` e `pos-release.passos:23,29` sugerem uma variável dedicada. Caminho: o projeto preenche `alvo-variavel: ALVO_POS_RELEASE`, mas `./scripts/migrar.sh` conecta pela variável do `.env`; o ensaio passa a trava com um alvo descartável e migra a base real. É exatamente o risco que Q4/Q5 querem fechar. Severidade baixa (o modelo vem vazio e o projeto preenche), por isso recomendação. Correção mínima: uma frase no `.passos` e no `.md`: `alvo-variavel` é a mesma variável que os passos leem, e o passo recebe o alvo dela, sem cair no `.env`. Esforço P. Dono: `devops-engineer`.

**A4** · evidência: `pos-release.passos:31`. No `case`, `*` casa `/`, `?` e `@`; `db://prod/producao?/descartavel-1` casa `*://*/descartavel-*` e não casa `*://*/producao`, logo não é ambíguo e roda no ensaio. Caminho só por erro de digitação ou cópia do alvo; sem atacante realista. Correção: exemplo com host e base literais (`*://host-de-ensaio/descartavel-*`) e uma linha dizendo que `*` atravessa `/`. Esforço P. Dono: `devops-engineer`.

Conferido sem achado: o nome de `alvo-variavel` é validado como identificador antes da expansão indireta (linha 48); os passos vêm do arquivo versionado do projeto (mesma fronteira de confiança dos próprios scripts), recebem `stdin` de `/dev/null` e rodam na raiz; a ambiguidade entre as duas listas é recusada nos dois modos; a trava é lista positiva (não repete AR-3); valor vazio e ausente recusam sem reserva; o linter de shell passa limpo; nada específico de projeto no modelo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do item: `python3 -m unittest tests.test_pos_release` na raiz do clone, 17 testes OK no head fb7dccb4; sondas S1 e S2 rodadas numa cópia do script em pasta temporária. A suíte inteira roda no CI do PR (não citada aqui como verde: o head não tem PR). Ferramentas: linter de shell presente (limpo); varredor de segredos, SAST e varredor de workflows ausentes no PATH (lacuna; não instalados, `R-CUSTO`), sem efeito neste diff (sem segredo, dependência nem workflow).
