---
tipo: review
contrato: 1
pedido: catraca-rotulo-escopo
branch: melhoria/catraca-rotulo-escopo
commit: 0dc9ce9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review (parecer de autor): catraca protege os hooks que decidem, limita os pareceres ignorados e barra violação vinda da base

Escopo: `origin/develop..199290b` (1 commit): `tests/catraca.py`, `tests/test_catraca.py`, ADR 0008, `CHANGELOG.md`. Referências: R-CONFORMIDADE, R-REVIEW, ADR 0008, review independente de `docs/reviews/rotulo-sobrevive-merge.md` (desvios 1 e 2).

Este é o parecer do autor. O PR muda `tests/catraca.py` (protegido): falta a review independente e o rótulo `afrouxa-regra` do dono. No CI roda a catraca da base, então este PR é julgado pela regra antiga.

## Desenho
1. **Controles que decidem:** `PROTEGIDOS` ganha `hooks/parecer.py` (`e_clone_do_forge`, a decisão do parecer), `hooks/_comum.py` (`falhar_fechado`, `executar`) e `bin/forge-check`. O `forge-check` entrou depois de conferir o código: o hook `parecer` decide o bloqueio por `pedidos_da_branch` e `cmd_pr` dele, e o modo `pareceres` da catraca também. Ficaram de fora `agentes.py`, `pesado.py` e `quadro.py` (R-TETO e R-WIP, operacionais, e já dependem de `_comum.py`) e o `vigia.py` (só avisa). `hooks/hooks.json` e `hooks/conformidade.json` já têm regras próprias.
2. **Pareceres ignorados (desvio 1):** `pareceres_do_pedido` devolve os caminhos exatos que podem mudar depois do rótulo: os de `docs/reviews/` e `docs/qa/` que o PR já tocava no head rotulado (sobre o merge-base dele) e os filhos diretos dessas pastas cujo nome é o último segmento da branch (`melhoria/x` → `x.md`). Esses caminhos vão ao `mesmo_diff` no lugar dos prefixos. Caminho com curinga (`* ? [ ] \`) nunca é ignorado, porque o pathspec do git o trataria como padrão. A branch vem de `--ramo` (`HEAD_REF`) ou, sem ele, do `head.ref` do PR pela API (`ramo_do_pr`, mesma chamada gratuita e só leitura que `execucoes_do_pr` já fazia, agora numa função só). Se a API falhar, a branch fica vazia e só vale o que o PR já tocava, o que é mais estrito. A primeira versão passava `HEAD_REF` no `catraca.yml`, mas o push foi recusado porque o token local não tem o escopo `workflow`, e a API resolve o mesmo sem mexer em workflow.
3. **Violação vinda da base (desvio 2):** com o diff igual, `rotulo_vale_pelo_conteudo` calcula as violações do head rotulado sobre o merge-base dele e exige que as atuais estejam contidas nelas, como multiconjunto. A chave é o texto antes de `. Por quê:` (regra, o quê e caminho) com os números trocados por `N`, porque contagens e linhas mudam com a base.

## Vermelho e verde
Os testes foram escritos antes da mudança. Sem ela, 10 falhas: 3 subtestes de protegidos, 3 subtestes de parecer de outro pedido, parecer de outro pedido que já existia na base, parecer novo sem ramo, nome com curinga e violação nova vinda da base. Depois, sem `ramo_do_pr`, mais 1 falha e 1 erro: a branch pela API em `main` e a função `ramo_do_pr`. Com a mudança, `python3 -m unittest discover -s tests` dá 278 OK e `scripts/validar-plugin.sh` passa. O teste `test_commit_so_de_parecer_mantem_o_rotulo` passou a informar a branch (`melhoria/ped`), porque o parecer que ele cria tem o nome do pedido. Não houve afrouxamento: sem a branch, o mesmo caso agora invalida o rótulo (`test_sem_ramo_parecer_novo_depois_do_rotulo_invalida`).

## Checklist
1. Faz o pedido, nem mais nem menos. O `bin/forge-check` em `PROTEGIDOS` é a única extensão, e decorre da conferência pedida no item 1.
2. Respeita ADR 0008 e R-CUSTO (só biblioteca padrão, nenhuma API nova). `hooks/conformidade.py` não foi tocado.
3. As funções são pequenas, com nomes que dizem o que fazem.
4. Falha fechada: sem `sha`, diff diferente ou violação nova, o rótulo não vale.
5. Segurança: o nome da branch (escolhido pelo autor do PR, como sempre) só amplia os pareceres ignorados para os arquivos com o mesmo nome, e não entra no pathspec como padrão.
6. Custo: a catraca calcula as violações duas vezes só quando há violação e rótulo pelo conteúdo.
7. Os testes cobrem os três itens e as bordas: parecer já existente na base, sem ramo, curinga e número que muda com a base.
9. Um commit coerente, com `git add` explícito.

## Riscos
- Mudar `bin/forge-check` passa a exigir o rótulo do dono. Isso traz mais atrito para mudanças de validação de documentos.
- A chave sem números pode confundir duas violações que diferem só pelo número, como o termo nº 3 e o nº 4 de `termos_proibidos`. O efeito é aceitar como já vista uma violação que mudou de índice com a base. Esse caso é raro, porque o prefixo do hash continua na chave.
- No caminho "rótulo depois do último push", a contenção não é aplicada. O pedido limita o item 3 ao merge da base, e nesse caminho o head do PR é o que o dono viu.
- Os pareceres do QA em `docs/qa/bugs/` não casam pelo nome da branch, só se o PR já os tocava.

Parecer de autor: **aprovado**, com a pendência da review independente e do rótulo do dono.

## Review independente
Revisor: forge:tech-lead (sessão separada da do autor). Escopo: `origin/develop..0dc9ce9`.

**Testes:** `python3 -m unittest discover -s tests` no checkout de `0dc9ce9`: 278 testes, OK (178 s). Sondas extras, fora do repositório, sobre o harness `RotuloSobreviveAoConteudo`, com os resultados abaixo.

### Desvios tentados
1. **Nome da branch casando com o parecer de outro pedido: confirmado, gravidade baixa, recomendado.** A base tem `docs/reviews/antigo.md`. Rotulado sem tocá-lo, o PR na branch `qualquer/antigo` reescreve o arquivo depois do rótulo e a catraca dá rc 0. Basta o último segmento da branch, com qualquer prefixo. O alcance é só o texto de pareceres (`docs/reviews/`, `docs/qa/`, incluindo `_modelo.md` com a branch `x/_modelo`). Qualquer violação de regra continua recalculada e barrada: na sonda, parecer junto com `invariantes` esvaziado dá rc 1. O nome é fixado antes do rótulo, e a renomeação depois dele cai no modo estrito (desvio 4).
2. **Parecer tocado de fachada: confirmado, gravidade baixa, recomendado.** O PR acrescenta uma linha em branco em `docs/reviews/antigo.md`, que já existe na base, antes do rótulo. Depois do rótulo, reescreve o arquivo inteiro e a catraca dá rc 0. O toque aparece no diff que o dono viu, e o alcance é o mesmo do item 1. **Sugestão para os itens 1 e 2**, em `pareceres_do_pedido`: ignorar só os pareceres **ausentes no merge-base do head rotulado**, ou seja, criados pelo PR. O histórico de outros pedidos fica sempre comparado, e o fluxo legítimo (parecer de autor e review independente no arquivo novo do pedido) não muda.
3. **Normalização dos números: risco residual, gravidade baixa, recomendado.** `\b\d+\b` troca também (a) números dentro do texto dos invariantes (`invariante removido de f: até 3 tentativas` e `... 5 tentativas` viram a mesma chave), (b) o prefixo do sha256 em `termos_proibidos_hash` quando ele sai só com dígitos (cerca de 2% dos hashes) e (c) números de ADR no caminho (`0008-...`). Para esconder uma violação, é preciso que a antiga suma e outra, com a mesma chave, apareça só pela base, com o patch do PR idêntico byte a byte. Como `mesmo_diff` é estrito no texto do patch, não encontrei sequência prática. A contagem de multiconjunto pega a violação acrescentada. **Sugestão:** normalizar só as contagens conhecidas (`de N para N`, `nº N`) e preservar padrão e caminho.
4. **Branch vinda da API: seguro.** Num PR de fork, `pull_requests` das execuções vem vazio, então `commit_do_rotulo` dá None e só vale o caminho "depois do último push". Na renomeação da branch depois do rótulo, as execuções antigas mantêm o `head_branch` antigo, a consulta pelo nome novo não acha a execução do rótulo, dá None e cai no modo estrito. Quando a API falha, `ramo_do_pr` devolve `""` e `execucoes_do_pr` devolve None, então o caminho pelo conteúdo nem é avaliado: é de fato o modo mais estrito. Na sonda, `--execucoes []` dá rc 1. Ponto menor: `ramo_do_pr` é chamado duas vezes (dentro de `execucoes_do_pr` e no `main`). Uma corrida com renomeação entre as chamadas só torna o resultado mais estrito. Sugiro chamar uma vez só (higiene).
5. **Rótulo depois do último push: seguro quanto ao head, com risco residual anterior a este PR.** O head é o que o dono viu. O que sobra: se a base mudar depois do rótulo, sem push no PR (por exemplo, a base passa a proteger um arquivo que o PR apaga), uma nova execução por `edited` ou `reopened` roda sobre o merge commit novo e libera também a violação vinda da base, sem a contenção. Sem nova execução, o check verde antigo continua valendo do mesmo jeito: os rulesets não estão ativos no plano atual (a API responde 403), então "exigir branch atualizada" não é imposto. Não é regressão. **Sugestão:** aplicar `violacoes_novas` também nesse caminho, comparando com as violações de `HEAD_SHA` sobre o merge-base dele, o que custa uma chamada a `violacoes_das_regras`.

### Regressão
- As regras do #57 (protegidos, falha fechada, custo fora do rótulo) e do #65 (rótulo pelo conteúdo, instante do servidor, reescrita, `[skip ci]`) continuam com os testes de antes. O único teste alterado (`test_commit_so_de_parecer_mantem_o_rotulo`) passou a informar a branch, e o caso sem branch ficou mais estrito (`test_sem_ramo_parecer_novo_depois_do_rotulo_invalida`).
- Release (`plugin.json`, `CHANGELOG.md`), sincronização da `main` e PR só de docs não tocam `PROTEGIDOS` e seguem sem exigir rótulo. O atrito novo é previsível: mudanças em `bin/forge-check`, `hooks/parecer.py` e `hooks/_comum.py` (9 commits recentes) passam a pedir o rótulo do dono no PR da `develop` e de novo nas promoções, porque a regra roda em todo PR, como já acontece com `tests/catraca.py`.
- R-CUSTO: só a mesma API gratuita e somente leitura. R-NEUTRO: nada específico de projeto.

### Veredito
**Aprovado com recomendações.** Nenhum desvio permite passar violação de regra que o dono não viu com o rótulo. Os itens 1 e 2 permitem reescrever o texto de pareceres de outros pedidos depois do rótulo (baixa). O item 3 é teórico (baixa), e o resíduo do item 5 é anterior a este PR. Os três ficam como recomendações para um PR seguinte, sem bloquear este. Pendência para o merge: o rótulo `afrouxa-regra` do dono, porque o PR muda `tests/catraca.py`.
