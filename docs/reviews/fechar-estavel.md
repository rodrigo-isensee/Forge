---
tipo: review
contrato: 1
pedido: fechar-estavel
branch: melhoria/fechar-estavel
commit: 6a1f2b3fee83ca24ea8ba1e24da2ea2f7e97ef0d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Review: FECHAR-ESTAVEL, o forge-fechar não duplica PR, aguenta 502 e tem o item do rótulo no modelo de PR

Escopo: `ef71b3c..6a1f2b3` (base real ef71b3c08913cf119396559c23fa9b0478e4607a, pela DECISÃO TÉCNICA do pedido), 5 arquivos em 3 commits (`f1dcc98` script e testes, `345d987` modelo de PR, `6a1f2b3` doc). O revisor não é o autor (D-ETAPAS-INST). Comparei o diff com o Escopo E1 a E5 do pedido, com o Fora do escopo (catraca e `bin/forge-check` intocados; push de código e merge sem repetição) e com a decisão do dono de 2026-10-15 (`R-CUSTO`, nada afrouxa).

Veredito sobre `6a1f2b3`: **APROVADO**, sem achados que bloqueiem.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_fechar` numa cópia do `6a1f2b3` em `$TMPDIR`: `Ran 47 tests in 5.527s` / `OK`.
- Vermelho antes do verde: os testes do `6a1f2b3` sobre a árvore do `ef71b3c`: `FAILED (failures=10, errors=1)`. O erro é de `test_pr_em_rascunho_vira_pronto_antes_do_merge`, teste antigo que quebra só porque o `gh` falso agora devolve três campos na leitura do passo 6 (acoplamento do falso ao `--jq` novo, esperado). Dos 15 testes novos, 10 falham e 5 passam no script antigo (ver Detalhe, A4).
- A suíte completa roda no `pre-push` deste envio (trava de `R-TETO`); `scripts/validar-plugin.sh` fica com o QA e o CI.
- Segurança (E1.3, `R-SEGURANCA`) e devops (E1.4, `.github/pull_request_template.md`) têm pareceres próprios em paralelo; não os refiz.

## Conferência do diff
1. **E1, passo 3 sem PR para head já mesclado:** `bin/forge-fechar:147` testa `git merge-base --is-ancestor` do head remoto contra `origin/develop` (ref local, sem fetch: base velha só dá falso negativo e cai na leitura dos PRs); `:151` lê `gh pr list --head --state all` e reconhece `MERGED` com a mesma base e o mesmo `headRefOid` (o caso #234/#235, squash vazio). PR mesclado com outro head não impede o PR novo (`test_pr_mesclado_com_outro_head_nao_impede_o_pr_novo`). Com `ja_mesclado=1` os passos 4 a 6 não rodam e vai à limpeza. Confere.
2. **E1, passo 6 com MERGED como sucesso:** `:215` aceita o PR já `MERGED` sem repetir o merge; merge que devolve erro lê o estado uma vez (com `ler`) e só segue se `MERGED`; a conferência final do estado continua. Base `main` e outra base seguem recusadas antes de tudo (`R-MAIN`). Confere.
3. **E2, repetição só no idempotente:** `ler` (`:63`) cobre as leituras dos passos 3, 5 e 6; o passo 4 tem contador próprio de 3 leituras seguidas sem estado (zera a cada leitura válida); `repetir` só envolve `git push origin --delete` (`:233`). `gh pr create`, `gh pr ready` e `gh pr merge` são chamados direto, sem laço; o push de código não existe no script. Todas as falhas esgotadas param (falha fechada), e a do `push --delete` só avisa, como antes. Confere.
4. **E3, item do rótulo igual:** a linha de `.github/pull_request_template.md` é a mesma do corpo gerado (`bin/forge-fechar:95`, com as crases escapadas), desmarcada; `test_modelo_de_pr_traz_o_item_do_rotulo_desmarcado_igual_ao_do_script` confere a igualdade e a unicidade. O item desmarcado não dispara o passo 5 (só `[x]`/`[X]`). Confere.
5. **E4, fonte da regra do título:** `docs/fechamento-integrador.md:17` passa a apontar os invariantes do `CLAUDE.md` do Forge (seção das regras protegidas por teste, que exige o destaque no título), não a `R-CONFORMIDADE`. Conferi a fonte no `CLAUDE.md`. A doc ganhou ainda a seção do erro passageiro, coerente com o código. Confere.
6. **E5, testes provam o que dizem:** os 15 novos usam `gh` e `git` falsos (o `git` falso só intercepta `push origin --delete` e delega ao real), com contagem de chamadas a `pr create`, `pr merge`, `pr list` e `push --delete`; cada teste de repetição tem o par que esgota as 3 tentativas e para. O fragmento `changelog.d/fechar-estavel.md` é neutro (`R-NEUTRO`), tipo `Corrigido`, sem editar o `CHANGELOG.md` nem a versão.
7. **Regras e commits:** nenhum invariante de `tests/config.json`, `docs/regras/`, `hooks/` nem `tests/catraca.py` mudou; o modelo de PR só ganha um item (aperta, não afrouxa), mas está em `.github/`, que pede o rótulo do dono no PR (Suposições do pedido). Nada pago (`R-CUSTO`). Três commits coerentes, Conventional Commits em português.

## Achados

## Detalhe dos achados
- A1 (recomendado) `tests/test_fechar.py:345` · o nome `test_estado_desconhecido_e_relido_e_merged_nao_abre_pr_nem_mescla_de_novo` diz que não abre PR, mas o teste afirma uma criação e um merge; o que ele prova é a releitura do estado depois do merge. Sugestão: renomear para `test_estado_desconhecido_depois_do_merge_e_relido_sem_repetir_o_merge`.
- A2 (recomendado) `bin/forge-fechar:65` · `ler` descarta o stderr de todas as tentativas, então a parada por 3 falhas não mostra o erro do `gh` (502, autenticação, PR inexistente). Sugestão: guardar o stderr da última tentativa e anexá-lo ao `die`.
- A3 (recomendado) `bin/forge-fechar:215` · o caminho do PR que já consta `MERGED` na leitura do passo 6 (mesclado por outro entre o passo 3 e o 6) não tem teste próprio; os testes chegam ao `MERGED` pelo passo 3 ou depois do merge. Sugestão: um teste com `estado` = `MERGED` e PR aberto no passo 3 que afirme zero merges.
- A4 (recomendado, registro) `tests/test_fechar.py:443` · o brief fala em 3 testes que também passam no script antigo; medi 5 (`..._nas_tres_leituras_...`, `..._outro_head_...`, `..._checks_em_tres_leituras_...`, `..._no_merge_nao_repete_...`, `..._nunca_passam_pela_repeticao`), todos guardas legítimos de propriedades que o script antigo já tinha. O guarda estático da linha 443 é por linha e por nome de função: um embrulho com outro nome passaria; serve como alarme, não como prova.

## Parecer
Aprovado. E1 a E5 cumpridos no código, na doc e nos testes; a repetição não cobre operação que muda o PR. As quatro recomendações não bloqueiam e podem ir num pedido seguinte.
