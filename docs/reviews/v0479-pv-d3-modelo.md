---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-d3-modelo
commit: 60be3dffce7a93a6d1ee0434efb632ecbcc54eba
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 E57.77 (PR-VERDE D3, modelo de projeto)

Diff revisado: `8ee73d15..146b4050` (2 commits; `templates/projeto/.githooks/pre-push`, `templates/projeto/CLAUDE.md`, `stacks/python/pronto.md`, `stacks/node-react/pronto.md`, `tests/test_prepush_so_docs.py`, `tests/mutantes/v0479-pv-d3-modelo.json`, `tests/mutantes/v0479-pv-d3-modelo-2.json`, `changelog.d/v0479-pv-d3-modelo.md`). Código: +38 linhas no hook do modelo (H1 dentro do teto).

## Ferramenta (citada, sem refazer)
- `bin/forge-mutante --processos 1 tests/mutantes/v0479-pv-d3-modelo.json tests/mutantes/v0479-pv-d3-modelo-2.json` (rev 146b40503055): M1 a M9 morreram (`templates/projeto/.githooks/pre-push:325,326,335,339,340,341,343,346,351`).
- `bin/forge-mutante --cobertura --base 8ee73d15`: `não coberto: templates/projeto/.githooks/pre-push` (shell fica fora da ferramenta). Conferido à mão: as 9 linhas de guarda do trecho novo (325, 326, 335, 339, 340, 341, 343, 346, 351) têm um mutante cada.
- Teste do item: `python3 -m unittest tests.test_prepush_so_docs.ConferenciaDeRegistros`: 9 testes, OK. Suíte inteira: fica com o CI do PR (`R-REVIEW`).
- shellcheck: ausente nesta máquina (`command -v shellcheck` vazio); a regra é "ferramenta" (`docs/engineering/praticas.md`, passo "shellcheck (scripts e hooks)" do `.github/workflows/ci.yml`), que pega o hook do modelo pelo shebang. Pendência do CI do PR, não revisão manual.

## Desvios relatados pelo autor, julgados contra `docs/propostas/v0479-pr-verde-de-primeira.md`
1. **8 arquivos em vez de 6:** aceito. O cabeçalho da seção 4 do desenho fixa o teto em 10 arquivos por item, contando testes, specs e fragmento; o "(até 6)" da linha D3 é estimativa. Os 2 a mais são a segunda spec, obrigatória porque o trecho tem 9 guardas (passou de 8, abre `-2.json`), e o módulo de teste.
2. **No projeto, versões só no texto, sem `--versoes`:** aceito. O desenho pede para o D3 só "texto do `CLAUDE.md` e do hook do modelo" e o "campo das versões" no `pronto.md`. O `forge-testes --versoes` do D1 é da fábrica: lê `python-version` do `.github/workflows/ci.yml` do Forge e roda o plano de afetados do Forge (`bin/forge-testes:1060-1085`); não vale para o projeto, que não tem esse plano. O texto pede um log por versão com `head=` e `rc=` e trata intérprete ausente como não verde, coerente com D1 e D5.
3. **shellcheck ausente:** aceito como pendência do CI (acima); o desvio não esconde nada que o CI não confira antes do merge.

## Leitura
- Faz o que o cartão pede: chave opcional `registros` do `.forge/config.json`, rodada da raiz em todo envio de branch (também o só de texto, porque vem depois da etapa local e não sai antes), falha fechada para saída fora de 0, chave inválida e prazo inválido. Sem variável que pule.
- `R-NEUTRO`: nada de linguagem no núcleo do modelo; Python e Node só em `stacks/`. O `python3 -I` do hook já era usado no mesmo arquivo.
- Segurança: config que é link não é lido; a chave é comando do próprio repositório, que já é dono do hook; stdin fechado. Parecer de segurança não é exigido para D3 pela seção 4.
- Testes: cada guarda tem teste do ramo de falha por comportamento (envio real ao remoto falso), sem ler o texto da fonte; o `FORGE_REGISTROS_PRAZO` herdado é limpo no `setUp`.
- Commits: Conventional Commits em português, um comportamento por commit.

## Revalidação no head 60be3dff (E57.85)
Delta lido: `forge-check parecer delta docs/reviews/v0479-pv-d3-modelo.md`, intervalo `146b4050..60be3dff`, 4 arquivos no domínio (`templates/projeto/.githooks/pre-push`, `tests/test_prepush_so_docs.py`, `tests/mutantes/v0479-pv-d3-modelo-2.json`, `changelog.d/v0479-pv-d3-modelo.md`); nada fora dele relido.
- Hook: `9>&-` nas duas chamadas do comando de registros (`pre-push:347` e `:349`), como a etapa já faz (`:154`). O descritor 8 da fila já fecha em `fila_sair` (`:223`) antes, então só o 9 chegava ao comando.
- Teste `TravaDaChecagem.test_trava_nao_passa_para_os_registros`: por comportamento, com e sem `timeout` no PATH; o comando deixa um `setsid sleep` vivo e o segundo envio com `FORGE_PREPUSH_ESPERA=1` sai 0; os pids são mortos no `finally`. Rodado: 1 teste, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0479-pv-d3-modelo-2.json` (rev 60be3dffce7a): M9, M10 e M11 morreram (`pre-push:346,347,349`). Um mutante por guarda mudada.
- Changelog: o fragmento cita o comportamento novo (E57.83). Suíte inteira: CI do PR (`R-REVIEW`).

## Achados
- A1 (recomendado) templates/projeto/.githooks/pre-push:332 · config.json ilegível (JSON quebrado ou raiz que não é objeto) só avisa e o envio segue sem a conferência; o desenho (B3) admite aviso só para ferramenta ausente. Avaliar barrar quando a chave não se lê, num cartão depois do merge.

## Sondas

## Parecer
Aprovado no head 146b4050 e revalidado no head 60be3dff (delta sem achado novo). Os três desvios cabem no desenho (seção 4 e linha D3); o único achado é recomendado e vira cartão depois do merge. Pendência: shellcheck no CI do PR.
