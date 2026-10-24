---
tipo: revisao-seguranca
contrato: 1
pedido: lote-s1-scripts
branch: melhoria/lote-s1-scripts
commit: 8e22f173e103f04a77bab9152747f0d79473f9f0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: lote-s1-scripts

Diff revisado: `3c66b881af31817ce5d2dde996c7ca56d54cb511...8e22f173e103f04a77bab9152747f0d79473f9f0` (FECHAR-TOCTOU, FECHAR-DA-RAIZ, CHANGELOG-D-LINK, VALIDAR-AVISO-X). Veredito: aprovado, sem bloqueante.

## Gatilhos
Controle do Forge: `bin/forge-fechar` (pasta do log e limpeza da branch remota), `bin/forge-changelog` (lê, publica e apaga arquivos de `changelog.d/` e grava os manifestos) e `scripts/validar-plugin.sh` (saída do validador).

## Achados

## Detalhe dos achados
Conferências pedidas no brief, com a evidência:

1. **Corrida entre conferir e mudar o modo da pasta do log** (`bin/forge-fechar:166-181`). O chmod agora roda em `(cd -P "$logdir" && [ -O . ] && chmod u=rwx,go=,g-s,u-s .)` (`bin/forge-fechar:178`): o dono é conferido no diretório já aberto e o chmod age sobre `.`, então trocar o caminho por link entre o `cd` e o `chmod` não muda o alvo. Se a troca acontece antes do `cd -P`, o `[ -O . ]` recusa diretório de outro dono. O que resta é trocar por link para outro diretório do **próprio** usuário, e isso exige escrita no diretório pai: os padrões são `$XDG_RUNTIME_DIR` (700 do usuário) ou `/tmp` com sticky bit, onde outro usuário não renomeia a entrada. Sem caminho de ataque realista. Sonda: 4755, 6755, 1755 e 3777 viram 700 com esse chmod (o `u=rwx,go=` também tira o sticky). Informativa: depois do chmod, o `find` de retenção e o `mktemp` (`bin/forge-fechar:183-184`) ainda usam o caminho, não o descritor. Com os pais padrão isso não é explorável; fica como nota, sem cartão.

2. **O teto do delete esconde uma remota viva?** (`bin/forge-fechar:107`, `119-123`, `463-469`). Não. O `timeout` estourado devolve 124 e uma negação devolve diferente de 0. Nos dois casos o `repetir` falha depois de 3 tentativas, `rem_st=pendente`, a mensagem diz "a branch remota continua viva", o comando pendente é impresso e a saída é 3 (`bin/forge-fechar:564`, `746-753`). Sem `timeout` no PATH, roda sem limite, sem falso sucesso. Se o servidor apaga a ref depois que o cliente é morto, o erro é para o lado conservador: a remota sai como pendente quando já sumiu. A faixa (1 a 100) recusa 0, 101 e texto, o que impede desligar o teto pela variável. Teste: `tests/test_fechar_orfao.py`, push que trava, saída 3 e `remota=pendente`.
   Recomendação, sem cartão e sem relação com segurança (vai ao `tech-lead`/QA): com o teto no máximo (100) e a pausa no máximo (30), o pior caso é 3×100+2×30 = 360 s, acima dos 300 s do cartão. O padrão (80 e 3) fica em 246 s e uma linha de registro sai antes. Baixar o teto máximo para 80 fecha a conta.

3. **`changelog.d` ou fragmento por link publica ou apaga fora da raiz?** (`bin/forge-changelog:96-110`, `74`, `162`). Não. `conferir_pasta_de_fragmentos` roda antes de ler, gravar e apagar, tanto no `novo` quanto na `release`. Sondas em repositório descartável, todas recusadas com saída 1 e o alvo externo intacto: `changelog.d` como link para fora; `changelog.d` como link para pasta **dentro** da raiz; links encadeados (`changelog.d` → `changelog.d2` → `docs/l` → fora); fragmento `d.md` como link para uma pasta; e fragmento do `novo` como link quebrado para fora. Esse último fecharia o `write_text` que segue o link, e o glob inclui o link quebrado. Uma subpasta-link dentro de `changelog.d/` não entra, porque o glob `*.md` não desce. Informativa: um **hard link** em `changelog.d/` para um `.md` externo é publicado, e só o nome dentro da raiz é apagado, sem que o arquivo externo se perca. O git não versiona hard link, então ele não chega por PR. Só quem já escreve na árvore local do mantenedor o planta. Sem caminho realista.

4. **A troca da versão grava o campo aninhado?** (`bin/forge-changelog:131-137`). Não. A conferência agora compara o JSON inteiro com `{**dados, "version": versao}`. Sondas: aninhado antes do topo, com o topo diferente ou igual ao alvo e com o aninhado igual ou diferente do alvo, e `"version"` dentro de lista. Todas recusadas com o manifesto intacto. O único caso aceito com aninhado e topo já iguais ao alvo é a no-op, e o arquivo fica igual. `"version"` escapado dentro de string e `"version\u0000"` não casam com a regex, e só o topo muda.

5. **VALIDAR-AVISO-X** (`scripts/validar-plugin.sh:18-32`). O rótulo só troca com código 0 do validador, o texto do aviso segue inteiro e a falha mantém o `✘` e o código. Com `set -euo pipefail`, o primeiro `validar` que falha encerra o script. Não esconde reprovação.

PA-7 (`docs/engineering/achados-recorrentes.md`): a lista está vazia, sem item a conferir.

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: `shellcheck` (os avisos em `bin/forge-fechar:494`, `511` e `518` são de linhas fora do diff), `timeout` do coreutils e os testes do lote (`tests.test_changelog`, `tests.test_fechar_log_check`, `tests.test_fechar_orfao` e `tests.test_forge.ValidarPluginAviso`: 70 testes, OK, 1 pulado), mais as sondas em `$TMPDIR`. Faltaram no PATH, e ficam como lacuna: `gitleaks`, `zizmor` e `semgrep`. O diff não toca workflow nem segredo.
