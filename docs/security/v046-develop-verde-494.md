---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/develop-verde-494
commit: 2e8eb8b5165d9b7fac3eab78fbf9c627cdaebf35
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-11
---
# Review de segurança: v046 (E18.5, develop verde, head 2e8eb8b5)

Estático, lido por `git show`/`git archive` do commit, sem escrever na branch. Delta contra `2b896503`: `tests/test_catraca.py` (+3/-2), `docs/hooks-fixtures.md` (índice gerado), `changelog.d/develop-verde-494.md`. Nenhum código de produção, hook nem workflow mudou.

## Gatilhos
`R-SEGURANCA`: toca teste de uma guarda do CI (injeção de expressão do workflow em `run:` no passo que roda a catraca de pareceres). Sem segredo, sem permissão, sem `ci.yml` alterado.

## Achados
- A1 (recomendado) tests/test_catraca.py:2065 · a guarda de `${{` em `run:` cobre só o passo de pareceres; hoje nenhum `run:` do ci.yml tem `${{` (sondado), mas nada trava um novo; generalizar a todos os passos.

## Sondas

## Detalhe dos achados
**Foco 1, a guarda mantém o alcance.** O corte `re.split(r"\n\n  [a-z-]+:\n", passo, maxsplit=1)[0]` (linha 2061) remove só o que vem depois da fronteira do job. Sondagem no `ci.yml` do head: o passo tem 2313 caracteres antes do corte e 1030 depois; o resto cortado começa em `\n\n  verificacoes:\n    name: bateria (verificações longas)`; não há linha em branco dentro do passo, então o corte não o encurta (termina em `python3 "$script" --modo pareceres ...`, a última linha). As três asserções seguem sobre o passo inteiro: `HEAD_REPO` e `BASE_REPO` no `env` e `assertNotIn("${{", ...run...)`. Antes do corte, o `run:` lido incluía o job seguinte (daí o vermelho); agora lê só o próprio passo, que é o que a guarda quer. Falha segura: se o job seguinte deixar de ser separado por linha em branco, o corte não ocorre e o teste volta a ler demais (vermelho, não verde falso). Se o passo deixar de ser o último do job, o corte pega até a fronteira do job: lê mais, nunca menos.
Os três testes do `Workflows` e o da guarda passam no head (`Ran 7 tests ... OK`, extraído para diretório temporário).
**Foco 2, nada escapa no ci.yml.** Varredura de todas as linhas dentro de blocos `run:` do `ci.yml` no head: nenhuma ocorrência de `${{`. Os valores do contexto do evento (`head_ref`, `head.repo.full_name`, `user.login`) entram só por `env:` (linhas 547-552, 499-500), nunca interpolados no script. O job `verificacoes` (e o `run:` de 650) também está limpo, mas já não é coberto por este teste depois do corte: ver A1 (hoje sem risco, só falta o trava).
**Foco 3, o 20 na lista de tempos não afrouxa.** O job `verificacoes` já existia com `timeout-minutes: 20` (ci.yml:570, vindo do #493); a lista do teste ficou desatualizada e o 20 só a alinha ao workflow. A asserção continua `assertEqual` com a lista inteira em ordem: qualquer teto novo, trocado ou removido continua barrando. O teto do job é razoável (igual ao da bateria). Não é afrouxamento.
**Foco 4, `docs/hooks-fixtures.md`.** Mudança é só contagem (2257 para 2260 fixtures, linha `pesado`) e uma linha de prefixo; cabeçalho diz "Gerado por scripts/indice-fixtures.py", consistente com a saída do gerador; sem conteúdo executável.
A1: severidade informativa; correção mínima: iterar todos os passos do `ci.yml` e exigir que nenhum bloco `run:` contenha `${{`; esforço P; dono `devops-engineer` com o `qa-engineer` no teste.

## Riscos aceitos e ferramentas
Nenhum risco aceito. `zizmor` e `actionlint` não rodados localmente nesta passada (não conferi se estão no PATH além do teste e da sondagem manual); o CI cobre. Nenhuma ferramenta instalada.
