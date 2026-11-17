---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-h4-atualiza-branch
commit: ecc079920274ff207f217372c8708bef6e990899
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474 (H4, forge-fechar traz a develop por merge)

Revalidação por delta (E1.47). Rodada anterior: aprovado em 07009e3e (commit f8f88fa6, no git). Delta lido: `forge-check parecer delta` de 07009e3e..ecc07992, sem o que veio da develop; no domínio só `bin/forge-fechar:789`; fora dele, `tests/mutantes/v047-h4-atualiza-branch.json` (M6 acompanha a linha nova). Junções f1e1ac05 e 80dd1720 (passo 2b do forge-fechar): `git show --remerge-diff` vazio nas duas, sem resolução à mão nem mudança além da develop.

## Achados
- A1 (recomendado) bin/forge-fechar:767 · aberto, sem mudança: o merge-tree que vira commit enviado lê os atributos locais (merge=union torna limpo um conflito); use a árvore vazia como fonte de atributos, como a juncao_limpa (bin/forge-check:2538)

## Sondas

## Gatilhos
Gatilhos: controle do Forge (forge-fechar: envio a branch remota, cadeia de pareceres, R-VERIFY, R-FLUXO).

## Verificado no delta (sem achado)
- bin/forge-fechar:789: `[ -d "$arvore_lock" ]` → `test -d "$arvore_lock"`, mesma semântica no bash (builtins `test` e `[` idênticos); a guarda da worktree limpa e o fast-forward seguem iguais, e o caminho `update-ref` com compare-and-swap continua no `else`. O mutante M6 aponta a linha nova e o teste dele segue citado.
- Junções da develop: remerge-diff vazio (árvore exata do merge-tree); o conteúdo da develop é revisado no PR de origem de cada item, fora deste parecer.

## Detalhe dos achados
A1. Estado: aberto, recomendado, sem mudança (detalhe completo no commit b0f9652d). Severidade baixa; barreira: a catraca do CI refaz a junção no servidor sem os atributos locais. Correção mínima: `git --attr-source=<árvore vazia> merge-tree ...` em `conflito_com`. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check parecer delta`, `git show --remerge-diff` e leitura do diff; rodado local `tests.test_fechar_base_andou` (cobre a linha pelo M6): OK. Suíte no CI do PR 633 no head ecc07992 (run 44109839130): as 10 partes da suíte, catraca, instalação e bateria longa verdes; `bateria (pareceres)` vermelha à espera dos pareceres deste head.
