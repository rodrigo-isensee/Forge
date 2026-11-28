# Índice das fixtures dos hooks

<!-- Gerado por scripts/indice-fixtures.py; não edite à mão. Rode o script quando surgir prefixo ou hook novo. -->

O corpus de `tests/hooks/<hook>/<caso>.json` roda em `tests/test_hooks.py` (ADR 0003): cada caso dá a entrada de uma chamada ao hook e o código e a saída que ele tem de dar. Aqui, por hook, os prefixos do nome do caso (até o primeiro `-`), em ordem alfabética e sem contagem: caso novo num prefixo que já existe não muda este arquivo, e PRs paralelos se juntam sem conflito nele. As contagens, as regras `R-*`, os cartões e um exemplo por grupo saem de `python3 scripts/indice-fixtures.py --detalhe`, sem gravar.

## `agentes`

- `autor-*`
- `bloqueia-*`
- `carga-*`
- `config-*`
- `desligado-*`
- `duplicado-*`
- `erro-*`
- `errointerno-*`
- `estado-*`
- `expirado-*`
- `ferramenta-*`
- `fim-*`
- `inicio-*`
- `lanca-*`
- `load-*`
- `memoria-*`
- `mesmo-*`
- `namespace-*`
- `nproc-*`
- `outra-*`
- `outro-*`
- `pid-*`
- `piso-*`
- `registro-*`
- `reserva-*`
- `ritmo-*`
- `sem-*`
- `sessao-*`
- `teto-*`
- `vigia-*`
- `worktree-*`

## `ambiente`

- `erro-*`
- `fora-*`
- `sem-*`

## `conformidade`

- `aceite-*`
- `amend-*`
- `api-*`
- `aq-*`
- `ar-*`
- `aritmetica-*`
- `ativar-*`
- `atribuicao-*`
- `autoria-*`
- `b10-*`
- `b4-*`
- `b5-*`
- `b6-*`
- `b7-*`
- `b8-*`
- `brief-*`
- `c1b3-*`
- `codigo-*`
- `comentario-*`
- `commit-*`
- `conferente-*`
- `continuacao-*`
- `contrib-*`
- `cpb-*`
- `crase-*`
- `d-*`
- `desenho-*`
- `dir36-*`
- `e-*`
- `e350-*`
- `e51-*`
- `env-*`
- `erro-*`
- `errointerno-*`
- `estadoclone-*`
- `expandir-*`
- `extglob-*`
- `f-*`
- `fc-*`
- `ferramenta-*`
- `fifo-*`
- `fila22-*`
- `flag-*`
- `g-*`
- `gh-*`
- `git-*`
- `gitcomum-*`
- `gravar-*`
- `grupo-*`
- `guarda-*`
- `heredoc-*`
- `home-*`
- `hook-*`
- `i-*`
- `idx-*`
- `j-*`
- `k-*`
- `kanban-*`
- `lancador-*`
- `leitura-*`
- `m1-*`
- `m42-*`
- `merge-*`
- `mit-*`
- `n-*`
- `n1-*`
- `n2-*`
- `n3-*`
- `n5-*`
- `n5r-*`
- `nao-*`
- `o-*`
- `opaco-*`
- `oraculo-*`
- `ordens-*`
- `pacote-*`
- `parecer-*`
- `pasta-*`
- `pedido-*`
- `pn7-*`
- `politica-*`
- `pp-*`
- `pr-*`
- `profundidade-*`
- `projeto-*`
- `protegido-*`
- `push-*`
- `r10-*`
- `r7-*`
- `raiz-*`
- `regra-*`
- `rm-*`
- `rotulo-*`
- `rverify-*`
- `segmento-*`
- `sem-*`
- `shell-*`
- `so-*`
- `sparse-*`
- `sub-*`
- `subst-*`
- `tagv-*`
- `trava-*`
- `v0453-*`
- `versao-*`
- `vigia-*`
- `vigor-*`

## `decisao`

- `duas-*`
- `erro-*`
- `sem-*`
- `uma-*`

## `doutor`

- `abrir-*`
- `erro-*`
- `sem-*`

## `estado`

- `erro-*`
- `outra-*`
- `outro-*`
- `sem-*`

## `meta`

- `ainda-*`
- `desarmado-*`
- `entregue-*`
- `erro-*`
- `espera-*`
- `falha-*`
- `jargao-*`
- `mensagem-*`
- `mp1-*`
- `notas-*`
- `pausado-*`
- `pergunta-*`
- `quarta-*`
- `sem-*`
- `v0454-*`

## `ordens`

- `arquivo-*`
- `erro-*`
- `idioma-*`
- `injeta-*`
- `link-*`
- `s5-*`
- `sem-*`
- `sessao-*`
- `sessionstart-*`
- `teto-*`
- `vazio-*`

## `ordens_teto`

- `bloqueia-*`
- `dentro-*`
- `erro-*`
- `outra-*`
- `outro-*`
- `sem-*`

## `parecer`

- `api-*`
- `atualiza-*`
- `checkout-*`
- `comando-*`
- `continuacao-*`
- `erro-*`
- `fila27-*`
- `forge-*`
- `gh-*`
- `graphql-*`
- `guarda-*`
- `heredoc-*`
- `hook-*`
- `incidente-*`
- `leitura-*`
- `merge-*`
- `pasta-*`
- `pn7-*`
- `pr-*`
- `pull-*`
- `sem-*`
- `subst-*`
- `switch-*`
- `texto-*`
- `v0454-*`
- `v0455-*`
- `v0456-*`
- `v0480-*`

## `pesado`

- `aguardando-*`
- `citar-*`
- `comando-*`
- `erro-*`
- `expirado-*`
- `falha-*`
- `forgetestes-*`
- `lancador-*`
- `lista-*`
- `livre-*`
- `mesma-*`
- `mutacao-*`
- `outra-*`
- `outro-*`
- `permissao-*`
- `pid-*`
- `pos-*`
- `sem-*`
- `teste-*`
- `teto-*`
- `vigia-*`

## `quadro`

- `caminho-*`
- `erro-*`
- `kanban-*`
- `outro-*`
- `quadro-*`
- `sem-*`
- `wip-*`

## `salvar`

- `erro-*`
- `sem-*`
- `stop-*`

## `vigia`

- `bloqueio-*`
- `compactacao-*`
- `contorno-*`
- `corrigir-*`
- `d-*`
- `e51-*`
- `em-*`
- `entrada-*`
- `erro-*`
- `erros-*`
- `f-*`
- `g-*`
- `git-*`
- `inicio-*`
- `leitura-*`
- `medida-*`
- `merge-*`
- `nova-*`
- `r9-*`
- `repete-*`
- `repetir-*`
- `sem-*`
- `settings-*`
- `sparse-*`
- `subagente-*`
- `time-*`
- `versao-*`
