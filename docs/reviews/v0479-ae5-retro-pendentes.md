---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae5-retro-pendentes
commit: c38abefad5b1b87c04628b6524c579f87b6bd529
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E58.63 e revalidação E58.67, AE5.1 `forge-check retro --pendentes` e o campo `Cobre:`)

Intervalo lido: `821db42e..600bbecf` (3 commits). Desenho: `docs/propostas/v0479-melhorias-anti-erro.md`, AE5 (a).

## Achados
- A1 (recomendado) bin/forge-check:5835 · Comentário HTML de várias linhas conta como corpo: seção só com `<!--`, `lead`, `-->` cobre a versão (sonda: rc 0, pendentes=0). O modelo usa comentário de uma linha; ignorar o miolo até `-->` fecha a brecha.

## Parecer
Aprovado. Faz o que o AE5 (a) pede, nem mais: lista as tags `vX.Y.Z` alcançáveis da main com mais de 24 h sem retro que as cubra, e a retro declara `Cobre:` no cabeçalho, várias versões por retro. O relógio é argumento (`--agora`), sem leitura da hora; entrada ilegível sai 2; `--main` aceita só ref sem opção (`REF_DA_MAIN` exige primeiro caractere alfanumérico); link, pasta, arquivo acima do teto e pasta de retros que é link não cobrem. As retros vêm do `--raiz-pedidos` quando dado (pasta de controle) e as tags do git de `--raiz`. A exigência das quatro seções com corpo vai além do texto do desenho, mas serve ao objetivo (retro vazia não quita a cobrança) e está documentada no modelo. A integração com a auditoria (AE6) e o recibo das 8h fica para o item do AE6.

Tamanho (H1): cerca de 70 linhas de código em `bin/forge-check`, um comportamento. Modelo igual em `docs/retrospectivas/_modelo.md` e `templates/projeto/docs/retrospectivas/_modelo.md`, com teste de igualdade. `test_retro_pendentes` entrou no mapa do `bin/forge-testes` (FORGE_CHECK e LEITORES_DE_TEXTO) e nos pesos D4; fragmento em `changelog.d/`.

Execução no head 600bbecf:
- `python3 -m unittest tests.test_retro_pendentes`: 18 testes, OK. Os subprocessos limpam o ambiente e chamam Python com `-I`.
- `bin/forge-mutante` nos três arquivos `tests/mutantes/v0478-ae5-retro-pendentes*.json`: 24 de 24 morreram (8 por arquivo), uma guarda por mutante.
- `python3 -m unittest tests.test_forge.Neutralidade`: 3 testes, OK (`R-NEUTRO`).
- Nomes de função de módulo do `bin/forge-check`: `grep -oP '^def \K\w+' | sort | uniq -d` vazio. Constantes repetidas no módulo: só `ETAPAS_DE_PARECER` e `ID_DE_PEDIDO`, que já se repetem na base `821db42e`; nenhuma vem deste diff.
- Suíte completa: fica no CI do PR (`R-REVIEW`); a branch ainda não tem PR, então não há CI a citar.

A1 é recomendado: não há gatilho no modelo nem no fluxo atual (as retros seguem o modelo de comentário de uma linha), e vira cartão depois do merge.

## Revalidação no head e375c67a (E58.67)
Delta lido só por `forge-check parecer delta docs/reviews/v0479-ae5-retro-pendentes.md`: intervalo `600bbecf..e375c67a`, no domínio `bin/forge-check`, `changelog.d/v0479-ae5-retro-pendentes.md`, `tests/mutantes/v0478-ae5-retro-pendentes{,-3,-4}.json` e `tests/test_retro_pendentes.py`; saída `revalida: sim`.

- `_texto_da_retro` abre a retro uma vez com `O_NOFOLLOW | O_NONBLOCK`, confere `S_ISREG` pelo `fstat` do descritor (fecha o descritor no ramo de recusa), lê até `TETO_DA_RETRO + 1` e devolve None acima do teto: fecha a janela entre conferir e ler, o FIFO sem escritor e o arquivo que cresce depois do `stat`. `stat` já é importado no módulo.
- `docs/` que é link também fica fora (`pasta.parent.is_symlink()`), com teste próprio.
- O teste das 24 h compara código e linhas inteiras; a base de saída vazia falha por asserção, não por índice.
- Nomes de função de módulo do `bin/forge-check`: `grep -oP '^def \K\w+' bin/forge-check | sort | uniq -d` vazio.
- `python3 -m unittest tests.test_retro_pendentes` (ambiente limpo): 20 testes, OK.
- `bin/forge-mutante --processos 1 --ids M5,M6,M18,M25,M26,M27,M28,M29` nos três arquivos de mutantes tocados: 8 de 8 morreram (M5 e M27 em 5826, M26 em 5829, M6 em 5834, M28 em 5841, M18 e M25 em 5882, M29 em 5883).
- Suíte completa: fica no CI do PR (`R-REVIEW`).

Segue aprovado; A1 continua recomendado, sem mudança no delta.

## Revalidação no head 2d378b98 (E58.88)
Delta lido só por `forge-check parecer delta docs/reviews/v0479-ae5-retro-pendentes.md`: intervalo `e375c67a..2d378b98`, no domínio `bin/forge-check`, `bin/forge-testes`, `tests/pesos-d4.json` e `tests/test_reval_delta.py`; saída `revalida: sim`.

- O merge da develop `f324dfa4` (pais `d7751096`, `c9d69234`) não tem resolução à mão: `git show --remerge-diff f324dfa4` vazio. `bin/forge-testes`, `tests/pesos-d4.json` e as funções de entrega e `remoto_da_branch` do `bin/forge-check` vêm da develop (PRs #752, #755 e #757), fora deste parecer.
- `git diff c9d69234 HEAD -- bin/forge-check` tem as mesmas linhas mudadas do patch aprovado contra a base antiga `821db42e`, salvo a docstring de `cmd_retro_pendentes`, que troca o caminho `docs/retrospectivas/` por prosa (sem efeito no comportamento).
- `tests/test_reval_delta.py` ganha a entrada `("tests/test_retro_pendentes.py", "docs/retrospectivas/"): (1, "teste-le")` na guarda C-2: o teste cita o caminho uma vez (`test_retro_pendentes.py:115`, a igualdade dos dois modelos), contagem e classe batem.
- `python3 -m unittest tests.test_reval_delta tests.test_retro_pendentes` (ambiente limpo): 30 testes, OK.
- Suíte completa: fica no CI do PR (`R-REVIEW`).

Segue aprovado; A1 continua recomendado, sem mudança no delta.

## Revalidação no head 8d2efa1f (E58.104)
Delta lido só por `forge-check parecer delta docs/reviews/v0479-ae5-retro-pendentes.md`: intervalo `2d378b98..8d2efa1f`, sem a base; no domínio `bin/forge-check`, `tests/mutantes/v0478-ae5-retro-pendentes{,-2,-3}.json` e `tests/test_reval_delta.py`; saída `revalida: sim`.

- Os merges da develop `1fb80933` e `26b75512` não têm resolução à mão (`git show --remerge-diff` vazio nos dois). A contagem 15 para 16 de `tests/test_forge.py` × `README.md` em `tests/test_reval_delta.py` vem da develop (`origin/develop` b18d3ea já traz 16), fora deste parecer.
- `8d2efa1f`: `COBRE_DA_RETRO`, `VERSAO_DA_TAG` e `REF_DA_MAIN` passam a texto e os quatro usos (`bin/forge-check:5896`, `5909`, `5917`, `5927`) chamam `re.match`/`re.fullmatch` com o padrão; nenhum uso de método (`.match`, `.fullmatch`) sobra nas três constantes. Mesmas expressões, mesmo comportamento; o cache do `re` cobre o uso repetido no laço das tags.
- Mutantes M7, M13, M14 e M15 (de `-2`) e M17 (de `-3`) ganham o `de` nas linhas novas; `bin/forge-mutante --processos 1 --ids M7,M13,M14,M15,M17` nos três arquivos: 5 de 5 morreram (5896, 5917 três vezes, 5927).
- `python3 -m unittest tests.test_retro_pendentes tests.test_hooks_volta_corpus tests.test_reval_delta`: 63 testes; com `env -i` o `test_corpus_nos_dois_hooks` falha por 2 subprocessos acima do teto (4633 contra 4631), e falha igual na `origin/develop` b18d3ea com o mesmo `env -i`, logo não vem do delta; no ambiente da sessão o teste passa.
- Suíte completa: fica no CI do PR (`R-REVIEW`).

Segue aprovado; A1 continua recomendado, sem mudança no delta.

## Revalidação no head c38abefa (E58.113)
Delta lido só por `forge-check parecer delta docs/reviews/v0479-ae5-retro-pendentes.md`: intervalo `8d2efa1f..c38abefa`, sem a base; no domínio `bin/forge-check`, `bin/forge-testes`, `tests/pesos-d4.json` e `tests/test_reval_delta.py`.

- O merge `c38abefa` (pais `568daf8a`, `8caa7f3d`, a develop com o PR #763) tem uma resolução à mão só: `git show --remerge-diff c38abefa` mostra o conflito em `bin/forge-testes`, e a tupla `FORGE_CHECK` resolvida é a união dos dois lados (`test_retro_pendentes` desta branch e `test_comparar` da develop), sem outra mudança na linha.
- O subcomando `comparar` do `bin/forge-check`, o peso `test_comparar` em `tests/pesos-d4.json` e a citação de `bin/forge_comparar.py` em `tests/test_reval_delta.py` vêm da develop (#763) por fusão automática, fora deste parecer.
- `bin/forge-testes --registros --base origin/develop`: rc=0 (9 conferências e o peso dos módulos novos).
- `tests.test_testes_tocados` (ambiente limpo, `python3 -I`): 196 testes, OK (1 pulado).
- Suíte completa: fica no CI do PR (`R-REVIEW`).

Segue aprovado; A1 continua recomendado, sem mudança no delta.

## Sondas
