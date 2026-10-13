---
tipo: review
contrato: 1
pedido: catraca-rotulo-escopo
branch: melhoria/catraca-rotulo-escopo
commit: 199290b
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
