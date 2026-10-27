---
tipo: revisao-seguranca
contrato: 1
pedido: hook-ansi-c
branch: melhoria/hook-ansi-c
commit: 3707e280ce4e3ff11bc28b79b6ab75820d920b27
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: hook-ansi-c

Escopo: o diff `770c19a...3707e28` (`hooks/_comum.py`, `tests/test_hook_ansi_c.py`, `tests/mutantes/hook-ansi-c.json`, `changelog.d/hook-ansi-c.md`). Método: leitura dos chamadores de `leituras()` e sondas diferenciais base × head com o hook real (`conformidade` como um agente de papel `dev` (o padrão), `security-engineer` e `conferente`; `parecer` como `tech-lead`; `pesado.pesado` direto), mais o bash real numa pasta temporária com `.env` falso, para provar o que ele roda.

## Gatilhos
Controle do Forge (`hooks/`): o leitor comum dos hooks `conformidade`, `parecer` e `pesado`. O `agentes` não lê linha de Bash (só `Agent`/`Task`, `hooks/agentes.py:26`), então os três que usam `leituras()` são `conformidade`, `parecer` e `pesado`.

## Achados
- A1 (bloqueante) hooks/conformidade.py:831 · segurança com gatilho: a mesma classe ($'…' com \' dentro) num nível aninhado passa: bash -c "echo \$'it\\'s'; cat .env \\'" e o eval com o mesmo texto saem 0 e o bash lê .env; com rm -rf .git \\' apaga .git
- A2 (recomendado) hooks/pesado.py:90 · regressão da trava R-TETO: <pesado> && echo $'a\'b' \' era pesado na base e deixa de ser (leituras() volta ilegível e sem partes); a ADR 0013 aceita liberar na dúvida

## Detalhe dos achados
**O que a entrega fecha (conferido):** no nível 0, os dois casos do cartão (`echo $'it\'s'; cat .env\'` e `echo $'it\'s'; rm -rf .git \'`) saíam 0 na base e saem 2 na head, com "aspas sem par na leitura do hook". O mesmo vale para `true && … &&`, `|`, `x=$'…'`, a quebra de linha, `\\\'`, `#` no fim, dentro de `"$( … )"`, de crase, de `bash -c '<texto entre aspas simples>'`, de `eval '<texto>'` e do corpo de `bash <<'EOF'`, e para `cat .env \'` (palavra separada, que o bash lê como o `.env` de verdade). O `parecer` já recusava a variante com `gh pr merge` (base 2, head 2). O papel só de leitura (`conferente`) não muda: a gramática dele já recusa `$`. O corpus de legítimos (`$'a\nb'`, `$'a\\'`, `$'\x41'`, `"$'\''"`, `'a'\''b'`, `git status|log|diff`, `cat`, `grep`, `gh pr view`) sai igual nas duas pontas. A detecção (`hooks/_comum.py:1043`) só marca `\'` dentro do estado `ansi`; o `\\` consome os dois caracteres, então `$'a\\'` não é marcado. Fora do `pesado` (A2), nenhum chamador perde recusa: `conformidade.conferir_linha` recusa a linha ilegível fora do papel só de leitura (`hooks/conformidade.py:685-706`); `rotulo_na_sessao_do_forge` exige o dono se o texto cita o rótulo (`hooks/conformidade.py:1387`); `DonosDosHeredocs` usa o comando lógico inteiro (`hooks/_comum.py:916-931`); e a `autoria` (`hooks/conformidade.py:1698-1712`, só no PostToolUse) deixa de achar alvo, o que faz o `forge-check pr` recusar o parecer. Assim ela falha fechado.

**A1.** Evidência: `hooks/conformidade.py:831` (`aninhado`), chamado em `:922` (`bash|sh -c`) e `:924` (`eval`). O texto interno é o valor do `shlex`, que entre aspas duplas mantém `\$` (o bash entrega `$`). O shell de dentro recebe `echo $'it\'s'; cat .env \'`, a linha do cartão, mas o hook relê `echo \$'it\'s'; …`. Para os dois leitores (`fichas` e `palavras_do_texto`), `\$'it\'` é um dólar escapado seguido de aspas simples, sem `ansi`, e `aspa_escapada` fica falso. O tratamento atual cobre só a crase (`:832`, `` \` ``). Sondas (`$TMPDIR/security-engineer-hook-ansi-c/saida-4.txt`): base 0 e head 0 para `bash -c "echo \$'it\\'s'; cat .env \\'"`, `bash -c "… rm -rf .git \\'"` e `eval "… cat .env \\'"`. O bash real imprime o `.env` falso e apaga `.git`. Caminho de ataque: um agente de papel `dev` (erro ou instrução injetada num arquivo lido) roda pela ferramenta Bash a variante aninhada da linha do cartão. Ele lê os segredos do `.env` ou apaga o `.git` do projeto, as duas coisas que o cartão quer barrar. Isso não é regressão (a base também sai 0), mas é a mesma família do cartão numa posição (nível aninhado entre aspas duplas) que a correção não cobre, e o pedido exige que a citação ANSI-C seja lida como o bash. Severidade: alta (vazamento de segredo por um controle do Forge). Correção mínima, à escolha do dono:
- (a) Em `aninhado`, reler também `comando.replace("\\$", "$")`, como já se faz com `` \` `` em `:832`. É a correção exata, mas toca `hooks/conformidade.py`, que está com o HOOK-CD. Fazer isso agora pede decisão (`R-DECISAO`).
- (b) Dentro de `hooks/_comum.py`: `palavras_do_texto` também marca `aspa_escapada` quando um `\$` é seguido de aspas simples cujo conteúdo tem `\` antes do `'` que fecha. O `leituras` então falha fechado. É conservador (recusa a mais só nessa grafia, rara em uso legítimo) e fica no arquivo e na classe deste pedido.

Em qualquer das duas, o teste entra como nova dimensão da matriz (posição: argumento de `bash -c`/`sh -c`/`eval` entre aspas duplas) e precisa de mutante. Esforço P. Dono: `tech-lead` (autor da branch).

**A2.** Evidência: `hooks/pesado.py:90` lê só `leituras(comando).partes`. Com `aspa_escapada`, a leitura fiel vira `None` e, sem `#`, não há leitura antiga. A linha `<pesado> && echo $'a\'b' \'` era lida pelo `shlex`, que via o `<pesado>` (um padrão da lista do hook), e `pesado.pesado` dava True na base. Na head dá False. Caminho: um agente roda a suíte pesada em paralelo com outra, o que é risco de recurso (`R-TETO`), não de segurança. A ADR 0013 (tabela 2.4) aceita que o `pesado` libere na dúvida. Correção mínima, se o dono quiser manter o piso: o `pesado` usa os inícios de `palavras_do_texto(comando).simples` quando `leituras().ilegivel`. Esforço P. Dono: `tech-lead`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Se o usuário preferir mesclar só o nível 0 agora e levar A1 a um cartão depois do HOOK-CD, o parecer precisa virar `riscos-aceitos` com aceite dele em `docs/security/aceites/hook-ansi-c.md` (`R-SEGURANCA`, `R-DECISAO`). Ferramentas: só leitura e sondas locais com Python e bash, sem rede. `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH (lacuna registrada). O diff não toca dependência, workflow nem segredo.
