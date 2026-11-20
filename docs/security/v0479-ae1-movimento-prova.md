---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae1-movimento-prova
commit: 8bdb976e63e52fb1deaba33e99999f86bc373595
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-ae1-movimento-prova (AE1.2, v0478 E58.27)

Escopo: `ed5bfa02..8bdb976e` (bin/forge-check `cmd_movimento`, bin/forge_onde.py `prova_git` e `prova_do_movimento`, bin/forge-fechar `--cartao`, testes, specs de mutante, skill do quadro, fragmento do changelog). Referência: desenho `docs/propostas/v0479-melhorias-anti-erro.md` (AE1, tabela da seção 4, linha AE1.2: "prova de outro cartão; PR mesclado em outra base; `rodar:` com slug de outra raiz ou link simbólico; `juntado:` em cartão fechado ou nele mesmo"), aceito pelo dono em 2026-11-20 13:51.

## Gatilhos
Gatilhos: controle que analisa entrada (prova do movimento), ferramenta que lê o git e o GitHub, trava do fluxo do quadro (R-SEGURANCA).

## Achados
- A1 (bloqueante) bin/forge_onde.py:185 · `rodar:<slug>` não se prende ao cartão nem à raiz do quadro: qualquer run.json com rc 0 (até `true`, fora de git, head vazio) prova qualquer cartão, o mesmo slug serve a dois cartões e o slug gravado em outra raiz vale (S1, S2), contra o desenho do AE1.2.
- A2 (recomendado) bin/forge-check:4911 · `pr:` e `commit:` leem o git e o gh do diretório atual sem conferir qual repositório é: um clone local com `origin/develop` próprio prova `commit:` de qualquer cartão (S3); a linha gravada não diz de que repositório a prova veio.
- A3 (recomendado) bin/forge_onde.py:196 · `juntado:<ID>` aceita qualquer cartão ativo, inclusive um criado segundos antes pelo próprio `movimento` (S4); segue o desenho aceito, mas a linha não deixa a auditoria cobrar o destino.

## Sondas
- S1 · `forge-check --raiz <q> rodar qualquer -- true` e depois `movimento ALVO-2 ... --para Pronto --prova rodar:qualquer` e `movimento ALVO-3 ... --prova rodar:qualquer` · espera: recusa (prova sem vínculo com o cartão) · obtido: rc 0 nos dois, `prova: rodar:qualquer rc=0 head=`
- S2 · `forge-check --raiz <outro-clone> rodar outra-raiz -- true`; no mesmo diretório, `forge-check --raiz <q> movimento ALVO-6 --de "Em andamento" --para Pronto --prova rodar:outra-raiz` · espera: recusa (slug de outra raiz) · obtido: rc 0, Pronto gravado
- S3 · clone local de um repositório recém-criado com branch develop e commit `feat: ALVO-4 feito`; nele, `forge-check --raiz <q> movimento ALVO-4 ... --para Pronto --prova commit:80a60ebf...` · espera: recusa · obtido: rc 0, `onde: develop sim`
- S4 · `movimento FANTASMA --de — --para Entrada` e em seguida `movimento ALVO-1 --de "Em andamento" --para Pronto --prova juntado:FANTASMA` · espera: recusa · obtido: rc 0, `prova: juntado:FANTASMA (em Entrada)`

## Detalhe dos achados
**A1.** Evidência: `bin/forge_onde.py:185-195` só confere a forma do slug, que o arquivo existe sem link e que `rc == 0`; o `run.json` é lido em `Path.cwd()` (`bin/forge-check:4911`), não na raiz do quadro, e nada o liga ao cartão. O próprio teste aceita um run.json escrito à mão com `{"rc": 0, "head": "abc"}` (`tests/test_forge_onde.py:419-427`): não se conferem os logs dos passos nem a forma do head, diferente de `forge_run.ler` (`bin/forge_run.py:94-115`). Caminho: o agente que fecha um cartão (Jarvis ou subagente) reaproveita uma execução verde qualquer, de outro cartão ou de outro clone, e o cartão vai a Pronto com "prova conferida"; é o erro que o AE1 existe para impedir ("prova de outro cartão", "slug de outra raiz" na tabela do desenho). A escrita à mão em `.forge/` é contida pelo hook `conformidade` (limite aceito: protege contra engano); o reaproveitamento usa só ferramentas legítimas. Severidade: média (integridade do quadro, sem dado nem segredo). Correção mínima: (1) o slug precisa citar o cartão (`citacao(cartao)` sobre o slug em maiúsculas, ou o slug começar por `<id-em-minúsculas>-`); (2) o run.json tem `head` sha40 e `passos` com os logs presentes na mesma pasta, sem link (reusar `forge_run.ler` ou a mesma checagem); (3) a raiz lida é a do repositório do código cuja origem é a mesma da prova `pr:`/`commit:` (ver A2) e a linha gravada leva o slug, o head inteiro e a raiz; (4) testes: slug de outro cartão recusa, run.json sem logs recusa, run de outra raiz recusa. Esforço: P. Dono: o backend da stack (autor do AE1.2).

**A2.** Evidência: `bin/forge-check:4911` passa `Path.cwd()` a `prova_do_movimento`; `presenca` (`bin/forge_onde.py:45-60`) confia em `refs/remotes/origin/develop` do clone que estiver no diretório atual. O quadro do Forge fica num repositório separado (a origem de `~/.forge-contrib` não é a do Forge), então ler no `--raiz` não serve; ler no diretório atual é escolha do desenho. Caminho: só fabricação deliberada (um clone qualquer com `develop` local) ou engano de diretório (rodar o `movimento` dentro do clone de outro projeto, onde um commit cite um ID igual); sem caminho realista de agente honesto, por isso recomendado. Correção mínima: gravar na linha o `git remote get-url origin` do diretório lido e recusar quando a origem não é URL do GitHub (caminho local ou `file://`), e o `pr:` ler o gh com o mesmo repositório (`--repo` igual à origem). Esforço: P. Dono: o backend da stack.

**A3.** Evidência: `bin/forge_onde.py:196-200` aceita destino que tenha uma linha com hora no histórico e não esteja em coluna final; o teste do próprio item cria o destino na hora (`tests/test_sobreposicao_quadro.py`, `K-ATIVO` e `K-2`). Segue o desenho aceito ("cartão destino existe e está ativo"), por isso não bloqueia. Caminho: cartão encerrado como "juntado" a um cartão que nunca será feito, sem rastro que a auditoria (AE6) cobre. Correção mínima: recusar destino cuja primeira linha no histórico seja posterior à última linha do cartão movido e registrar o destino de forma que a auditoria AE6 liste o `juntado:` cujo destino não chega a Pronto com prova (cartão no AE6.1). Esforço: P. Dono: o backend da stack.

**Sem achado:** `pr:` de outro cartão (título e corpo sem o ID inteiro recusam, `prova_git`, teste `test_pr_de_outro_cartao_recusa`); PR mesclado em outra base (`estado=MERGED base=develop` exigido na linha lida e o merge commit ancestral de `origin/develop`); commit fora da develop, inexistente ou com forma de opção (`tipo_do_alvo` recusa `-x` e `..`; `--end-of-options` no `rev-parse`); `gh` ou `git` fora do ar vira `nao-verificavel` e o cartão vai a "Aguardando sua validação", nunca a Pronto; texto lido do gh e do git sai por `sem_controle`/`limpo` antes da linha do histórico (sem quebra de tabela nem controle); `forge-fechar` passa a prova com `printf %q` no comando de pendência. O corpo do PR pode ser editado depois do merge para citar o ID: exige ato deliberado sobre o GitHub e fica no histórico de edição do PR; registrado, sem achado.

## Verificação
Rodados no head 8bdb976e: `tests.test_forge_onde`, `tests.test_sobreposicao_quadro`, `tests.test_fechar_move_cartao` (126 testes, OK). A suíte inteira não foi conferida: a branch não tem PR nem execução do CI no head; o portão final depende do CI verde no head corrigido.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e sondas locais em diretório temporário. O `gh` está sem credencial no ambiente da revisão (sem leitura de PR real); `pr:` foi avaliado pelo código e pelos testes com gh simulado.
