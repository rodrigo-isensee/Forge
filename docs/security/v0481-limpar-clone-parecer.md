---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-limpar-clone-parecer
commit: fe1f22755cdaf735ba4738b0f59cb7e1b0eb2068
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (#890, E14.8)

`forge-fechar --limpar` reconhece o clone de parecer já mesclado; classe C. Diff lido: `bin/forge-fechar` (limpar_clones, 651, 691 a 696), `docs/fechamento-integrador.md` passo 7, os dois testes e o arquivo de mutantes.

## Gatilhos
Gatilhos: apagar dados (o `rm -rf` do clone em `~/.forge-contrib/wt`), controle de conformidade (teste de guarda renomeado com a garantia invertida).

## O que aperta, o que é neutro, o que afrouxa
- **Aperta (cobertura):** `test_commit_do_clone_depois_do_head_mesclado_fica` prova que o commit feito no clone depois do head mesclado fica pendente; nada de comportamento fica mais estrito.
- **Neutro:** `^$merged_heads` na conta de `fora` (`bin/forge-fechar:696`). O commit ancestral do `headRefOid` de um PR MERGED já está no PR (`refs/pull/<n>/head` na origin) e no conteúdo do squash; os heads vêm do `gh` (PR MERGED na base), a busca é desta cópia e a falha dela faz o `rev-list --stdin` falhar (`erro`, fica pendente): falha fechada mantida. O caso de PR de fork com o mesmo nome de branch já existia em `sha_confere` e exige merge de quem mantém o repositório. A troca `tag v9` por `branch v9` em `tag_com_ref_velha` mantém o teste E128.2 com sentido. Stash, nota e branch local continuam contando.
- **Afrouxa:** `--exclude='refs/tags/*'` (`bin/forge-fechar:692`) tira da conta **toda** tag local, de qualquer nome, leve ou anotada, não só a `arquivo/*` que a origin apagou. Commit que existe só numa tag local, nunca enviada, é apagado com o clone (A1, sondas S1 e S2). A garantia de antes era requisito de segurança: achado A2 do parecer `docs/security/v0476-mp6.md` (MP6), provado pelo `test_commit_so_em_tag_local_fica`, que este diff renomeou e inverteu.
- **Catraca:** não pede o rótulo do dono. `python3 tests/catraca.py --base origin/develop --ramo melhoria/v0481-limpar-clone-parecer` sai 0 e `perdas_dos_testes` devolve lista vazia; o check `catraca` do PR está `pass`. Motivo: o teste antigo tinha 0 asserções contadas (a asserção mora no ajudante `fica`), e o novo `test_commit_do_clone_depois_do_head_mesclado_fica`, também com 0, vira o "gêmeo renomeado" (`mesmas_assercoes`). O afrouxamento passa em silêncio; por isso é bloqueante aqui (`R-CONFORMIDADE`).

## Achados
- A1 (bloqueante) bin/forge-fechar:692 · --exclude='refs/tags/*' tira da conta toda tag local (qualquer nome, leve ou anotada): o commit só numa tag nunca enviada é apagado pelo rm -rf (S1, S2). Desfaz o A2 do parecer v0476-mp6 e a catraca não pede o rótulo. Restrinja a refs/tags/arquivo/* e restaure o teste da base.

## Sondas
- S1 · python3 /root/.forge-contrib/wt/_sec-v0481-limpar-sonda.py -v Sonda (S1: commit vazio no clone destacado, git tag t-local, volta a melhoria/x, --limpar) · espera: rc=3 clone=pendente, clone existe · obtido: rc=0 clone=ok, clone apagado (na base 8833d0f6: rc=3 clone=pendente)
- S2 · mesma sonda, S2: git tag -a -m marco marco-local num commit não enviado · espera: rc=3 clone=pendente, clone existe · obtido: rc=0 clone=ok, clone apagado (na base 8833d0f6: rc=3 clone=pendente)

## Detalhe dos achados
**A1.** Evidência: `bin/forge-fechar:692` (`rev-list --exclude='refs/tags/*' --all --not --remotes`); `tests/test_forge_fechar.py:152` (o teste renomeado agora exige `clone=ok` para a tag local); `docs/fechamento-integrador.md:27` e `changelog.d/v0481-limpar-clone-parecer.md:2` dizem "a tag local (a `arquivo/*` que a origin apagou)", mas o código exclui todas.
Caminho: sem atacante externo; é perda de integridade e disponibilidade do trabalho local. Um agente ou o dono marca um commit com uma tag local (marco, cópia de segurança antes de um rebase) e volta à branch; o `--limpar` do fechamento, rodado por outro agente, apaga o clone e o commit sem pendência nem leitura. Irrecuperável (o reflog vai junto com a pasta).
Severidade: média (perda de dado local sem aviso; probabilidade baixa, impacto alto e silencioso).
Correção mínima (P, dono: `tech-lead`, autor do #890): em `bin/forge-fechar:692`, trocar `--exclude='refs/tags/*'` por `--exclude='refs/tags/arquivo/*'` (só o espaço das tags de arquivo da origin, que é o caso do clone de parecer); restaurar `test_commit_so_em_tag_local_fica` como na base (tag `t-local`, `self.fica`) ao lado do novo, renomeado para dizer `arquivo/*`; acertar o texto da doc (linha 27) e do changelog; no mutante M1, o `para` volta a `--all` e o M1b troca `arquivo/*` por `*` e é morto pelo teste restaurado. Resíduo aceitável: tag local nunca enviada criada no espaço `arquivo/*`, que é da origin. Excluir todas as tags continua possível, mas é afrouxamento de garantia de segurança: decisão do dono (`R-DECISAO`), com o rótulo `afrouxa-regra` no PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados no clone revisado (fe1f2275): `python3 -m unittest tests.test_forge_fechar.LimparClones tests.test_fechar_limpar_clone` (28 OK); a catraca local (rc 0, sem perdas); a sonda S1/S2 no head e na base. Suíte inteira: o CI do #890 estava com as partes da suíte pendentes e `bateria (pareceres)` vermelho (pareceres ainda ausentes) na leitura; com o parecer reprovado, não muda a decisão, e a volta cita o CI verde. Ferramentas fora do PATH: gitleaks, shellcheck, semgrep, zizmor (lacuna; o diff não toca segredo nem workflow).
