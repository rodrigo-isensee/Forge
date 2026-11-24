---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-repo-publico-fix
commit: eebdfef67bdc1a2357ab54e65acd937484853afc
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0480-repo-publico-fix (CONFORMIDADE-REPO-CREATE-PUBLICO, v0478 E141.16)

Revalidação por delta do PR #829 no head `eebdfef6` (3ª volta, E141.15, A8 da segurança), contra o meu parecer aprovado no head `708c4bb0` (no git, `6ae3b857`). Delta lido: `forge-check parecer delta docs/reviews/v0480-repo-publico-fix.md`, intervalo `708c4bb0..eebdfef6`; no domínio, `hooks/conformidade.py` (+9 −2: `CRITICO` :63, `GRAPHQL_SEM_TEXTO` :348, `graphql_publica` :3502 e :3504), 14 fixtures (`trava-graphql-*` e `trava-prazo-*`), `tests/mutantes/v0480-repo-publico-fix-8.json` (RP52 a RP56), `tests/test_hooks.py:3073` (piso de 65 para 76 e a medida da S18 sob o prazo), o índice das fixtures e o fragmento do changelog.

## Achados
- A1 (bloqueante) hooks/conformidade.py:63 · O marcador novo pega todo `gh api` com `repos` ou `graphql`, inclusive leitura (GET), e o marcador crítico também liga a recusa de construção não modelada (:2101): `gh api repos/$OWNER/r/pulls`, `${R}`, crase, `\`+LF e `-F n=$N` numa query de leitura passam de 0 para 2 (S1 a S4).

## Sondas
- S1 · `gh api repos/$OWNER/r/pulls` (forge:node-backend e forge:tech-lead) · espera: saída 0, como no pai `789a1174` · obtido: saída 2, "`$OWNER` com ação crítica: o hook não modela"
- S2 · `gh api "repos/${R}/pulls/1/files" --jq '.[].filename'` · espera: saída 0 · obtido: saída 2 (`${`)
- S3 · `gh api graphql -f query='query($n:Int!){viewer{login}}' -F n=$N` · espera: saída 0 · obtido: saída 2 (`$N`)
- S4 · `gh api repos/o/r/commits/` + crase `git rev-parse HEAD` crase, e `gh api repos/o/r/contents/README.md | jq -r .content \` + LF + `| base64 -d` · espera: saída 0 · obtido: saída 2 nas duas (crase; `\ + quebra de linha`)

## Parecer
**Reprovado** pela A1, a pergunta do brief sobre a ampliação do marcador.

**A volta ficou só no A8:** sim. As três mudanças do código são as três correções que a segurança pediu no A8: (1) a string comum casa até o fim com o `"` final opcional (`(?P<fecha>"?)`, :348), então a busca não recomeça a cada `"`, e a string sem fechamento falha fechado (:3504); (2) mais de um `query` entre campos e corpo falha fechado (:3502); (3) o marcador crítico (:63). Nada fora do A8 no delta.

**A1 (o marcador amplia demais).** Sondas com o hook do head e o do pai `789a1174` (`git archive`), montados pela `Fixture` da suíte, nos papéis `forge:node-backend` e `forge:tech-lead`: S1 a S4 saem 0 no pai e 2 no head; os controles `gh api repos/o/r/pulls`, `gh api graphql` com a query literal, `gh repo view ... && echo new` e `gh pr view` saem 0 nos dois. Causa: `CRITICO` não é só o marcador do prazo; ele também liga a recusa de construção não modelada (`nao_modelada` pelo `self.critico`, :2101) e as recusas de heredoc e reavaliação (:2182 a :2196), em todo projeto. A segurança pediu o marcador para as formas que decidem a visibilidade (`user/repos`, `orgs/<o>/repos`, `.../generate`, `repos/<o>/<r>` com PATCH ou PUT, e `gh api graphql`); o `\brepos\b` solto pega toda leitura REST de repositório. Correção sugerida, à escolha do autor com a segurança: estreitar o REST às rotas de criação e ao `repos/<o>/<r>` com método de escrita, e o GraphQL a `mutation` ou aos nomes `createRepository|cloneTemplateRepository|updateRepository`; ou pôr as formas de visibilidade só no marcador do prazo (`MarcadorDaPolitica.marca`, :4400), sem tocar o `CRITICO` das recusas de construção. Em qualquer caso, fixtures `-libera` com S1 a S3 e o mutante da linha.

**Teste `pesado/mesma-sessao-libera` lento no local:** não vem do diff. O delta só muda `hooks/conformidade.py`; o hook `pesado` (`hooks/pesado.py`) não importa o `conformidade` (só `_comum`, `_maquina` e, no registro da recusa, `agentes`), e o comando da fixture (`docker compose up -d`) não passa pelo marcador. É lentidão da máquina local; o CI decide.

**Teto H1:** `hooks/conformidade.py` soma 134 linhas no item contra a base `216413c9` (`git diff --numstat`: 134 +, 0 −), dentro de 150; o resto são fixtures, mutantes e teste.

**Ferramentas (citadas, não refeitas):** `tests.test_hooks.Hooks.test_fixtures_do_repo_publico` rodado no head com ambiente limpo: OK (1 teste, 15,2 s; as 76 fixtures do item e a S18 abaixo de metade do prazo). CI do PR #829 no head `eebdfef6`, na leitura: `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)` e `árvore já provada na develop` verdes; suíte 3.12 e 3.14 pendente; `bateria (pareceres)` e `catraca` vermelhos à espera dos pareceres. A mutação RP52 a RP56 não foi rerrodada (verificador do autor). O A1 recomendado do parecer anterior (mutante do par do CR) segue como cartão, fora desta volta.
