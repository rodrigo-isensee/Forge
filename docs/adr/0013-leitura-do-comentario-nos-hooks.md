# 0013 - Leitura do comentário nos hooks: só onde se prova, com a leitura antiga como piso

Estado: proposta. Data: 2026-10-21.
Propósito: decidir onde a leitura dos hooks abre um comentário (`#`) e o que cada hook faz com a linha que não consegue ler, fechando por construção, e não caso a caso, a classe de brechas da HOOK-COMENTARIO-SHLEX. Público: quem mantém os hooks e quem revisa a segurança deles. Revisão: 2026-11-21.

Emenda a ADR 0011, item 2 (a última frase: "o comentário que engole a quebra de linha fica fechado por esta regra, sem mexer no `shlex`"). Origem: desenho do `software-architect` (E0.3 do pedido `docs/pedidos/hook-comentario-shlex.md`), depois de cinco reprovações.

## Contexto
O `shlex` lê como comentário um `#` em qualquer ponto da palavra e engole a quebra de linha que o encerra. Com isso, `cat a#&&git push origin main` e `echo a#; git push --force origin main` passavam pelos hooks na develop. As voltas 0 a 4 trocaram isso por "`#` no início de palavra" com uma lista negra de contextos (`SEM_COMENTARIO`: `((`, `=~`, extglob) e trataram a linha ilegível (`ValueError`) só no `conformidade`. As cinco reprovações caem em duas classes:

| Classe | Achados | Mecanismo |
|---|---|---|
| C1. O hook lê menos que o bash: abre comentário num `#` que o bash lê como texto | `((#x))`, `(#b)`, `$(…)#b`, `@(a\|#b)`, `${x:- #b}`, crase, `((1 #x))`, `=~ ( #b)` | lista negra de contextos; cada volta acrescentou o contexto que o parecer anterior achou |
| C2. A linha que o hook não lê é liberada | `; (true)#'`, `# it's` depois de `((`, `$'it\'s'`, a barra no fim | `except ValueError` de cada chamador, cada um com a sua política |

Reprodução no primeiro passo da volta 5 (código de saída do hook; base develop `10c838f`, volta 4 `f02f482`):

| Risco | Linha | `10c838f` | `f02f482` |
|---|---|---|---|
| P1 (regressão da volta 0 a 4) | `parecer`: `gh pr merge feature/x --repo rodrigo-isensee/Forge --merge; (true)#'` com o review reprovado | 2 | 0 |
| P2 | `a\ #b; git push origin ${B:-main}` | 0 | 0 |
| P3 | `echo $[1 #x]; gh repo delete dono/proj --yes` | 0 | 0 |
| piso | `gh repo # x⏎delete dono/proj --yes` | 2 | 0 |

## Decisão
1. **Regra positiva do comentário (gramática G).** A posição de um `#` abre comentário se, e só se: (a) a varredura da linha, da esquerda para a direita, só passou por construções de G até ele; (b) ele está fora de aspas e não escapado; (c) ele está no início de palavra (começo da linha, ou logo depois de espaço, tab, quebra de linha, `;`, `&` ou `|` lidos pela própria varredura). G, por inclusão: letras e dígitos; espaço, tab, quebra de linha, `;`, `&`, `|`; `_ . / : = @ , + % - ~ ^ * ? [ ] { } !`; `<` e `>` (depois deles, um `#` encerra a varredura, porque o bash começa palavra nova ali); o `#` no meio de palavra; aspas simples fechadas; aspas duplas fechadas com caracteres comuns, `\` seguido de um caractere que não é quebra de linha e `$` de nome ou parâmetro especial; fora de aspas, o mesmo `\` e o mesmo `$`; o comentário provado, pulado até a quebra de linha. O que não está em G encerra a varredura, e daí até o fim da linha nenhum `#` abre comentário: crase, `(` e `)`, `$` seguido de outra coisa (`${`, `$[`, `$'`, `$"`), `=~`, `<<`, `\` no fim ou antes da quebra de linha, aspas sem fechar, `\r` e os demais caracteres de controle ou invisíveis. Um contexto do bash que ninguém listou também começa fora de G: a omissão desliga o comentário, não o liga (`hooks/_comum.py`: `varrer_comentarios`, `comentarios`).
2. **Comentário que o hook não prova e que mudaria outra linha.** Depois do ponto em que a varredura parou, um `#` que o bash pode ler como comentário (depois de espaço, tab, quebra de linha, `;`, `&`, `|`, `<`, `>`, `(` ou `)`) seguido, na mesma linha física, de aspa, crase ou `\` no fim, com outra linha depois, deixa a linha ilegível (`comentario_ambiguo`). Lido como palavra, ele levaria a aspa ou a barra para a linha seguinte e esconderia dela o que o bash roda (`echo ${x} # a\⏎gh repo delete …`).
3. **Leitura antiga como piso (I2).** Se a linha tem `#` e a leitura da develop (o `#` do `shlex`, `fichas(…, legado=True)`) fecha e dá outro resultado, as checagens rodam também sobre ela. Toda linha que a develop recusava continua recusada, por construção.
4. **Uma porta só.** `leituras(comando)` devolve `partes` (a leitura fiel e, se diferir, a antiga) e `ilegivel` (a fiel não fecha ou cai no item 2). Nenhum hook chama `comandos` direto; `segmentos`, `INICIO_DE_PALAVRA`, `SEM_COMENTARIO` e `abre_comentario` saem. A guarda `construcao_nao_modelada` e a `conteudos_de_crase` usam o mesmo conjunto de `comentarios`, calculado sobre a mesma linha.
5. **O que cada chamador faz com as leituras:**

| Chamador | Fiel ilegível | Antiga ilegível | Duas leituras |
|---|---|---|---|
| `conformidade` `Guarda.bash`, fora do papel só de leitura | recusa (volta 4, mantida) | ignora, como a develop | as checagens rodam sobre cada uma, com estado novo (`ambiente`, `cd`, branch); a pasta dos corpos de heredoc e o ambiente que segue são os da fiel |
| `conformidade` `Guarda.bash`, papel só de leitura | como antes (a gramática do nível 0 já recusou `#` e aspas sem par) | não ocorre | não ocorre |
| `conformidade` `rotulo_na_sessao_do_forge` | exige a conta do dono se a linha cita o rótulo | ignora | confere as duas |
| `conformidade` `alvos_de_escrita` (autoria) | sem alvos dela | sem alvos dela | união dos alvos |
| `parecer.principal` | recusa (`R-REVIEW`): a linha passou no `PREFILTRO` e o hook não a lê | ignora | confere as duas |
| `pesado.pesado` | se a antiga também não lê, libera, como a develop (a trava de recurso fica aberta na dúvida) | idem | pesado se qualquer uma for |

6. **Testes que fecham a classe, abaixo de 30 s** (`tests/test_hooks.py`), no lugar do teste gerado de 3 min da volta 4:
   - T1, inclusão no leitor: para cada linha das fixtures de recusa de Bash de `conformidade`, `parecer` e `pesado` e cada variante de `VARIANTES_QUE_O_BASH_IGNORA` (11 prefixos e 5 sufixos), todo comando da leitura fiel continua lido, ou a variante é ilegível;
   - T2, ligação leitor → recusa pelo hook real: dez famílias de recusa (`FAMILIAS_DE_RECUSA`) × sete mecanismos (`MECANISMOS_DO_COMENTARIO`) saem 2, menos o `$'…'` no `pesado` (item 5);
   - T3, oráculo do bash: em cada `#` que `comentarios` marca, o texto do comentário trocado por aspas e crase sem par continua aceito pelo `bash -n`; os modelos fora de G não marcam nada; os de G marcam;
   - T4, estrutural: `comandos` só é usada por `leituras` e `fichas` só por `comandos`; ninguém importa nenhuma das duas fora de `_comum.py`.

## Alternativas
| Forma | Fecha C1? | Fecha C2? | Por que não |
|---|---|---|---|
| Fichas do `shlex` (develop) | não | não | é o furo original |
| Lista negra `SEM_COMENTARIO` (volta 4) | não: A7 e P3 seguem abertos | só no `conformidade` | cada volta acha um contexto novo; o P1 veio dela |
| Grossa do A7 (`\$\{` e crase na lista negra) | não: `$[` e P2 ficam abertos | idem | continua lista negra |
| Fina do A7 (o leitor acompanha `${` e crase abertos) | não: enumera contextos | idem | custo por contexto, sem fim |
| **G + piso da leitura antiga + leitura única (esta)** | sim, por construção, conferida pelo T3 | sim, nos três hooks | recusa a mais rara (abaixo) |

## Consequências
- Melhora: fecham A7, P1, P2 e P3 e o caso da junção de linhas (`gh repo # x⏎delete …`); no `parecer`, também os furos da base `gh pr merge x; echo $'it\'s'` e o corpo de heredoc com apóstrofo; na sessão do Forge, o rótulo depois de `((#x))` ou dentro de `${…}`. A suíte perde cerca de 2,5 min (T1 a T4 somam cerca de 8 s).
- Piora (recusa a mais): linha com construção fora de G **antes** do `#` e comentário com aspa sem par, ou com comentário que leva aspa ou `\` para outra linha (`x=$(date) # it's`). O `parecer` recusa `gh pr create --body-file - <<'EOF'` com aspa sem par no corpo; o contorno é `--body-file <arquivo>`. Comparada à volta 4, passa a liberar `ls # it's ((` (o `((` está no comentário), como a develop.
- A manter: G em `hooks/_comum.py` (`LITERAIS_DE_G`, `SEPARADORES_DE_G`, `PARAMETRO`); ampliar G exige um modelo novo no T3.
- Fora desta decisão: o `tirar_heredocs` (`hooks/conformidade.py`) acha `<<` dentro de comentário e de aspas e toma por corpo as linhas que o bash executa; é anterior à develop e vira cartão próprio.

## Por que o existente não basta
O mecanismo novo é interno (`leituras` e `comentarios`); não é hook, regra, campo nem agente. O existente para a mesma necessidade é a lista negra `SEM_COMENTARIO` mais o `except ValueError` de cada chamador. A execução mostra que não basta: cinco reprovações seguidas, cada uma com um contexto novo (pedido, histórico de 04:50 a 09:14 de 2026-10-21); 146 de 448 recusas saem 0 com um sufixo na volta 3 e 147 de 499 com um prefixo na volta 4 (sondas da segurança); e a tabela do Contexto, em que a `f02f482` libera no `parecer` o merge que a develop recusava.

## Critério de reversão
Mais de 5 recusas legítimas pelo motivo "aspas sem par na leitura do hook, ou # que ele não prova ser comentário" (ou pelo `R-REVIEW` equivalente do `parecer`) nas quatro semanas seguintes ao merge na `main`, contadas pelo verificador (ADR 0007) ou relatadas em PR de retroalimentação. Atingido, a gramática G é ampliada pela construção que gerou as recusas, com o T3 provando a ampliação; não se volta à lista negra.

## Leituras
| Data | Medida | Veredito (manter, ajustar, reverter) |
|---|---|---|
| 2026-11-21 | recusas legítimas por linha que o hook não lê ou por comentário lido como palavra desde a 0.27.1 | pendente |
