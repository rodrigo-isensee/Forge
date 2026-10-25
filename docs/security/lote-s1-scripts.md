---
tipo: revisao-seguranca
contrato: 1
pedido: lote-s1-scripts
branch: melhoria/lote-s1-scripts
commit: 979c1ffd8ef43e608aca0f792c56afa4dd6d27d6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: lote-s1-scripts

Diff revisado: `3c66b881af31817ce5d2dde996c7ca56d54cb511...979c1ffd8ef43e608aca0f792c56afa4dd6d27d6` (FECHAR-TOCTOU, FECHAR-DA-RAIZ, CHANGELOG-D-LINK, VALIDAR-AVISO-X). Revalidação 2, por delta sobre o parecer anterior (`8e22f17`): `forge-check delta` lista `bin/forge-fechar:25`, `106-107` e `466-477`, `docs/fechamento-integrador.md:20,52,58,71`, as duas specs de `tests/mutantes/` e `tests/test_fechar_orfao.py`. Veredito: aprovado, sem bloqueante.

## Gatilhos
Controle do Forge: `bin/forge-fechar` (pasta do log e limpeza da branch remota), `bin/forge-changelog` (lê, publica e apaga arquivos de `changelog.d/` e grava os manifestos) e `scripts/validar-plugin.sh` (saída do validador).

## Achados
- A1 (recomendado) bin/forge-fechar:467 · o `git ls-remote origin refs/heads/<ref>` casa pelo fim do nome: outra branch terminada em `/refs/heads/<ref>` faz a conferência dizer que a remota continua viva quando ela já sumiu; erro conservador (pendente, saída 3), sem caminho de ataque; filtrar a coluna 2 igual a `refs/heads/<ref>` deixa a mensagem exata (vai ao `tech-lead`)

## Detalhe dos achados
Conferências pedidas no brief, com a evidência:

1. **Corrida entre conferir e mudar o modo da pasta do log** (`bin/forge-fechar:166-181`). O chmod agora roda em `(cd -P "$logdir" && [ -O . ] && chmod u=rwx,go=,g-s,u-s .)` (`bin/forge-fechar:178`): o dono é conferido no diretório já aberto e o chmod age sobre `.`, então trocar o caminho por link entre o `cd` e o `chmod` não muda o alvo. Se a troca acontece antes do `cd -P`, o `[ -O . ]` recusa diretório de outro dono. O que resta é trocar por link para outro diretório do **próprio** usuário, e isso exige escrita no diretório pai: os padrões são `$XDG_RUNTIME_DIR` (700 do usuário) ou `/tmp` com sticky bit, onde outro usuário não renomeia a entrada. Sem caminho de ataque realista. Sonda: 4755, 6755, 1755 e 3777 viram 700 com esse chmod (o `u=rwx,go=` também tira o sticky). Informativa: depois do chmod, o `find` de retenção e o `mktemp` (`bin/forge-fechar:183-184`) ainda usam o caminho, não o descritor. Com os pais padrão isso não é explorável; fica como nota, sem cartão.

2. **O teto do delete esconde uma remota viva?** (`bin/forge-fechar:107`, `119-123`, `463-469`). Não. O `timeout` estourado devolve 124 e uma negação devolve diferente de 0. Nos dois casos o `repetir` falha depois de 3 tentativas, `rem_st=pendente`, a mensagem diz "a branch remota continua viva", o comando pendente é impresso e a saída é 3 (`bin/forge-fechar:564`, `746-753`). Sem `timeout` no PATH, roda sem limite, sem falso sucesso. Se o servidor apaga a ref depois que o cliente é morto, o erro é para o lado conservador: a remota sai como pendente quando já sumiu. A faixa (1 a 100) recusa 0, 101 e texto, o que impede desligar o teto pela variável. Teste: `tests/test_fechar_orfao.py`, push que trava, saída 3 e `remota=pendente`.
   Recomendação, sem cartão e sem relação com segurança (vai ao `tech-lead`/QA): com o teto no máximo (100) e a pausa no máximo (30), o pior caso é 3×100+2×30 = 360 s, acima dos 300 s do cartão. O padrão (80 e 3) fica em 246 s e uma linha de registro sai antes. Baixar o teto máximo para 80 fecha a conta.

3. **`changelog.d` ou fragmento por link publica ou apaga fora da raiz?** (`bin/forge-changelog:96-110`, `74`, `162`). Não. `conferir_pasta_de_fragmentos` roda antes de ler, gravar e apagar, tanto no `novo` quanto na `release`. Sondas em repositório descartável, todas recusadas com saída 1 e o alvo externo intacto: `changelog.d` como link para fora; `changelog.d` como link para pasta **dentro** da raiz; links encadeados (`changelog.d` → `changelog.d2` → `docs/l` → fora); fragmento `d.md` como link para uma pasta; e fragmento do `novo` como link quebrado para fora. Esse último fecharia o `write_text` que segue o link, e o glob inclui o link quebrado. Uma subpasta-link dentro de `changelog.d/` não entra, porque o glob `*.md` não desce. Informativa: um **hard link** em `changelog.d/` para um `.md` externo é publicado, e só o nome dentro da raiz é apagado, sem que o arquivo externo se perca. O git não versiona hard link, então ele não chega por PR. Só quem já escreve na árvore local do mantenedor o planta. Sem caminho realista.

4. **A troca da versão grava o campo aninhado?** (`bin/forge-changelog:131-137`). Não. A conferência agora compara o JSON inteiro com `{**dados, "version": versao}`. Sondas: aninhado antes do topo, com o topo diferente ou igual ao alvo e com o aninhado igual ou diferente do alvo, e `"version"` dentro de lista. Todas recusadas com o manifesto intacto. O único caso aceito com aninhado e topo já iguais ao alvo é a no-op, e o arquivo fica igual. `"version"` escapado dentro de string e `"version\u0000"` não casam com a regex, e só o topo muda.

5. **VALIDAR-AVISO-X** (`scripts/validar-plugin.sh:18-32`). O rótulo só troca com código 0 do validador, o texto do aviso segue inteiro e a falha mantém o `✘` e o código. Com `set -euo pipefail`, o primeiro `validar` que falha encerra o script. Não esconde reprovação.

PA-7 (`docs/engineering/achados-recorrentes.md`): a lista está vazia, sem item a conferir.

## Revalidação 2 (delta 61cd772..979c1ff)
6. **Nota (a), pior caso abaixo de 300 s** (`bin/forge-fechar:107`, `120-123`, `466-477`). Fechada. A faixa agora é 1 a 75 (padrão 75); 76, 100, 101, 0 e texto são recusados antes do passo 1 (teste `test_teto_do_delete_fora_da_faixa_e_recusado_e_o_pior_caso_das_tres_tentativas_fica_em_300s`, mutante V1). Pior caso da limpeza remota: 3 x 75 + 2 x 30 (pausa máxima, `dormir`) + 10 (conferência) = 295 s, e a linha `registro: apagando ...` sai antes. O `timeout` sem `-k` só não corta processo que ignora `TERM`; o `git push` e o `pre-push` (`.githooks/pre-push:252-257`, sai 1 no `TERM`) morrem com ele, e o `timeout` sinaliza o grupo inteiro. Fora da conta e fora do delta: o primeiro `ls-remote` (`bin/forge-fechar:453`) não tem teto (já era assim na base); sem `timeout` no PATH, nada tem teto (R2 do review).
7. **A releitura depois do corte pode dar saída 0 com a remota viva?** (`bin/forge-fechar:467-477`). Não, nos três casos pedidos, com sonda em repositório descartável (`$TMPDIR/security-engineer-lote-s1-scripts/sonda-lsremote-v2`):
   - leitura que falha: remota inacessível devolve 128 e o corte do `com_teto 10` devolve 124; os dois caem no `else`, `rem_st=pendente` e saída 3, sem dizer "viva" nem "apagada" (teste `test_corte_com_a_conferencia_da_remota_falhando...`, mutante V3);
   - ref com outro sha (alguém enviou depois do corte): a saída não fica vazia, então vai a `pendente` com "continua viva"; o script não repete o delete sobre o sha novo, que não foi conferido;
   - remota trocada: o `ls-remote` usa a mesma `origin` do delete; trocar a URL entre os dois exige escrita no `.git/config` local (protegido no sandbox), sem atacante realista. Informativa: com `remote.origin.pushurl` diferente da `url`, o delete vai a um servidor e as duas leituras a outro; isso já valia para a conferência de sha antes do delete (`:453`) e não é do delta.
   Só a saída vazia com código 0 vira `remota=ok`, e o `ls-remote` só devolve vazio quando nenhuma ref casa com o padrão; como o casamento é pelo fim do nome, o erro possível é o inverso (A1, conservador). Nome de ref com `*`, `?` ou `[` não existe (`git check-ref-format`), então o padrão não vira curinga.
8. **Doc e specs.** `docs/fechamento-integrador.md:20,52,58,71` descrevem o comportamento novo (teto 1 a 75, `u-s`, `cd -P` com `[ -O . ]`, a conferência por `ls-remote`), sem afrouxar nada. As specs de mutantes são dado de teste, sem comando executável além do executor `unittest`.

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: `shellcheck` 0.11 (os avisos, agora em `bin/forge-fechar:504`, `521` e `528`, são as mesmas linhas fora do diff, deslocadas), `timeout` do coreutils e os testes do lote (`tests.test_changelog`, `tests.test_fechar_log_check`, `tests.test_fechar_orfao` e `tests.test_forge.ValidarPluginAviso`: 70 testes, OK, 1 pulado; na revalidação 2, `tests.test_fechar_orfao`, `tests.test_fechar_log_check` e `tests.test_changelog`: 71 testes, OK, 1 pulado), mais as sondas em `$TMPDIR`. Faltaram no PATH, e ficam como lacuna: `gitleaks`, `zizmor` e `semgrep`. O diff não toca workflow nem segredo.
