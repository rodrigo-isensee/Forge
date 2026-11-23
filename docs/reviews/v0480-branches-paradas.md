---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-branches-paradas
commit: 91787589122a55fef84899098648dbf34130e8aa
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E117.6, PR #807, pareceres pós-merge das branches paradas)

Escopo: `8773be38..91787589` (Base-sha do brief), 4 commits, 3 arquivos, só texto: `docs/reviews/v0457-e3cfg.md`, `docs/reviews/v0474-pos-merge-631.md` (novo) e `changelog.d/v0480-branches-paradas.md` (novo). Classe T, um parecer só (G1 do dono).

## O que foi conferido
- **Blob igual à fonte, sem merge da branch:** `git rev-parse` dá o mesmo blob nos dois lados. `ca41aab3:docs/reviews/v0457-e3cfg.md` e `HEAD:` são `836bb86b`. `04505d4e:docs/reviews/v0474-pos-merge-631.md` e `HEAD:` são `03da5835`. `ca41aab3` só está em `origin/melhoria/v0457-e3cfg` e `04505d4e` só em `origin/melhoria/v0474-pos-merge-631`. Nenhum commit do PR é merge.
- **`commit:` de cada parecer aponta código que está na develop:** a linha que `caff7afe` acrescenta ao `MAPA` está em `origin/develop:bin/forge-testes:242`. O PR 531 está `MERGED`, com head `df242407` e squash `2b454e7e`. `01b4e8ae` é ancestral da `origin/develop`. A troca `5842f35d` → `caff7afe` no v0457 sobe o parecer para a revalidação que a develop não tinha, e o texto novo é só a seção `## Revalidação`.
- **Por que só 2 dos 7 arquivos da tabela da E117.3:** o PR traz só os pareceres de review. Os de QA e de segurança são do domínio de outros papéis, o que bate com o escopo do brief ("os dois pareceres de review e o fragmento").
- **Formato:** `forge-check docs` sai 0 e `git diff --check 8773be38..HEAD` sai limpo. `forge-check parecer delta docs/reviews/v0457-e3cfg.md` responde "caff7af não é ancestral de 9178758". Isso é esperado, porque o parecer foi feito na branch parada e o código entrou por squash. Não há delta a ler.
- **Testes dos arquivos tocados** (ambiente limpo, `TMPDIR` próprio): `python3 -m unittest tests.test_changelog tests.test_reval_delta tests.test_citacao` passou, com 109 testes OK. A suíte inteira não foi rerrodada: o CI do #807 no head 91787589 está verde, com `suíte (python 3.14)` partes 1 a 5, `teto de pulados` e `árvore já provada na develop` em pass.
- **Guardas e tamanho:** o diff não tem código, então não há guarda nem mutante a declarar e são 0 linhas de código.

## Achados
- A1 (recomendado) changelog.d/v0480-branches-paradas.md:2 · a linha da E117.3 descreve ordem de integração e cartões que vivem na pasta de controle, fora do repositório, e diz "as 6 pós-merge num PR só de docs", mas o #807 traz 2 de 7 arquivos; tirar a linha ou dizer só o que entra no plugin

## Sondas

## Parecer
Aprovado. Os dois pareceres são cópias exatas dos blobs citados e foram trazidos sem merge das branches paradas. Cada `commit:` aponta código que já está na develop, e o formato passa no `forge-check docs`. A1 é texto de changelog: não devolve e vira cartão depois do merge.
