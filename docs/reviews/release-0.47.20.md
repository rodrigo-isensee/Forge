---
tipo: review
contrato: 1
pedido: release-0.47.20
branch: melhoria/v0481-release-0-47-20-pareceres
commit: 779356dcee5f1c840e328dc6efbd3fa9275e8d77
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: release-0.47.20

Revalidação por delta (H3, release-0.47.20 E1.8) da versão 0.47.20 contra a main, no head 779356dc da `develop`. A 1.ª rodada (aprovada no head 1e301536 do PR #935, hoje a marca 447b4ad2 na `develop`) conferiu os 23 itens, a marca e o anexo do #933 e do #934; este parecer lê só o que entrou depois.

## Delta lido
- `forge-check parecer delta docs/reviews/release-0.47.20.md`: "commit 1e301536… não existe" (o #935 entrou por squash como 447b4ad2); o delta lido é o do brief, `git log 8855671d..779356dc`: #937 (eba76f80), #936 (50e5b609), a marca #935 (447b4ad2) e o anexo #939 (779356dc).
- #937: squash igual ao head a2ef1548 (`git diff a2ef1548 eba76f80` vazio); os três pareceres (`docs/reviews|qa|security/v0481-f1p2-c1a.md`) aprovados em c31462e6, que difere do head só nesses três arquivos.
- #936: o patch do squash (`git diff eba76f80 50e5b609`) tem o mesmo `patch-id` do head d4f1f0f1 sobre 8855671d (1fcdd456); os três pareceres (`v0481-encolhe-930.md`) aprovados em 27641d2a, que difere do head só nos três pareceres.
- Anexo #939: `git diff 447b4ad2 779356dc` toca só `CHANGELOG.md` (+2) e apaga `changelog.d/v0481-encolhe-930.md` e `changelog.d/v0481-f1p2-c1a.md`; as duas linhas são iguais às dos fragmentos (CHANGELOG.md:16 e :36).
- CI: o head do #939 (f61936bf) tem a mesma árvore de 779356dc (`git diff` vazio) e todos os checks verdes, a suíte (5 partes) e a instalação incluídas; o run do push na `develop` em 779356dc (46029535472) passou em "árvore do PR já provada" e na checagem rápida.
- Ferramentas no head 779356dc: `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `git diff --check 447b4ad2 779356dc`: limpo; `python3 -m unittest tests.test_changelog`: 91 testes, OK; as duas `plugin.json` em 0.47.20; seção `[0.47.20]` com 26 linhas `- `.

## Regras afrouxadas (tabela do PR da main)
- #936 entra na tabela: afrouxa `R-CONFORMIDADE` (HOOK-NAO-PROTEGE-RAIZ-DO-FORGE), marca no título e rótulo; motivo: a grafia do Bash na raiz do Forge fica com o `denyWrite` do sandbox do SO, Write e Edit seguem barrados; pedido de origem v0481 E46.1. O rótulo pelo time vale pela ordem do dono de 26/11 12:57.
- #937 não afrouxa: rótulo só por arquivo protegido (`bin/forge_pareceres.py`, ADR 0008), a conta aceita fica mais estreita e o registro é exigência nova. Liste-o à parte ("rótulo sem afrouxar"), para a tabela fechar com os rótulos da versão. Não tira trava antiga, então não abre o intervalo que a ordem de 27/11 12:37 proíbe (o A1 da segurança do item fica para o C1b).

## Achados
- A1 (recomendado) CHANGELOG.md:7 · Atualiza o A1 da 1.ª rodada: o PR homolog → main lista 8 regras afrouxadas com motivo e pedido de origem (#909, #918, #920, #928, #929, #931, #932 e agora #936) e cita o #937 como rótulo sem afrouxar.
- A2 (recomendado) CHANGELOG.md:21 · Segue o A2 da 1.ª rodada: 6 itens de classe C sem `docs/qa/` na `develop` e o #934 sem parecer; o parecer de QA da release cobre a leva; vira cartão.
- A3 (bloqueante) CHANGELOG.md:32 · A linha do #930 diz que a raiz do Forge barra a escrita pelo Bash por variável e por texto de interpretador; o #936 tirou isso na mesma versão, e o fragmento dele (CHANGELOG.md:36) era "a entrada do #930 corrigida" (corpo do #936). O anexo somou em vez de trocar. Apagar a linha 32.

## Parecer
Reprovado pelo A3: o código do delta é o que os três portões de cada item aprovaram, e o anexo traz os dois fragmentos iguais, mas a seção `[0.47.20]` afirma uma guarda que a própria versão removeu. Conserto: um anexo que apague CHANGELOG.md:32; na volta, só essa linha é relida.

- ci: 779356dcee5f1c840e328dc6efbd3fa9275e8d77 verde
