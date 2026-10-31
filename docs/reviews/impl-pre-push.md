---
tipo: review
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c3
commit: e945d099c2c7b783e3e72b115e0f14c7065f192c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-pre-push, branch c3 (SUITE-INICIO-ATOMICO)

Diff lido: `234dbe0..e945d09` (2 commits: `5a89d72` hook e teste, `e945d09` fragmento).

## O que entrega
Item E2 do pedido, a parte C3 do desenho (`docs/propostas/lotes-1030/pre-push.md`, E2b): com a suíte rodando, o `--status` acrescenta a linha que aponta o caminho atômico `.githooks/pre-push --suite`. Só texto, sem mecanismo novo; o rc do `--status` não muda. O teste `test_status_acompanha_a_trava` passa a exigir a dica (vermelho antes, como o desenho pede).

## M14 (decisão M14, agents/tech-lead.md:19)
- Linhas contadas (`git diff --numstat --no-renames 234dbe0 e945d09`): `.githooks/pre-push` 1, `tests/test_pre_push_trava.py` 1; total 2, abaixo de 150. O fragmento `changelog.d/` fica fora.
- Um comportamento só (a dica do `--suite`). Toca `.githooks/` e não usa exceção de teto. Cumpre.

## Regras de ferramenta
- Suíte: a branch está no `origin` com o head revisado, logo o pre-push (suíte inteira, porque o diff toca `.githooks/`) passou no envio do autor; o CI do PR repete.
- shellcheck: não disponível nesta máquina; fica para o job do CI (`tests/test_pre_push_shellcheck.py` e o passo do CI). Pendência, não review manual.
- Mutação: não há `tests/mutantes/impl-pre-push*.json` na branch. Pendência do autor (V2); a mudança é uma linha de texto, sem condição para mutar.

## Leitura
- Escopo exato do C3 (linha `:97` e o teste); revertido sozinho, some só a dica. R-NEUTRO e R-CUSTO preservados; nenhum invariante tocado.
- A dica sai antes da linha de estado; leitores atuais usam `assertIn` e o rc, então nada quebra.

## Achados
- A1 (recomendado) .githooks/pre-push:97 · A dica sai antes de "suíte do Forge rodando"; pôr depois da linha de estado mantém o estado como primeira linha para quem lê só a primeira (head -1). Não quebra leitor atual.

## Parecer
Aprovado. Entrega o C3 do E2 como desenhado, dentro da M14. A recomendação A1 não devolve.
