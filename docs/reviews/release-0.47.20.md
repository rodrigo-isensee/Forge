---
tipo: review
contrato: 1
pedido: release-0.47.20
branch: melhoria/v0481-release-0-47-20-pareceres
commit: af1ae0f1f6a5d710cab5d81933fa6c0df6340201
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: release-0.47.20

Revalidação por delta (H3, release-0.47.20 E1.13) da volta 1, no head af1ae0f1 do PR #941. A rodada anterior (E1.8, head 779356dc) reprovou pelo A3; a 1.ª rodada (head 1e301536 do #935, hoje a marca 447b4ad2) conferiu os 23 itens, a marca e o anexo do #933 e do #934.

## Delta lido (volta 1)
- `forge-check parecer delta docs/reviews/release-0.47.20.md`: intervalo 779356dc..af1ae0f1, domínio só `CHANGELOG.md`, uma linha a menos: a do #930 (antiga CHANGELOG.md:32). O A3 está resolvido.
- A entrada do #936 (CHANGELOG.md:35, "v0481 E37.1 e E37.26") fica como a única do item e diz o que a versão entrega: Write e Edit barrados na raiz do Forge, a grafia do Bash com o `denyWrite` do SO.
- Ferramentas no head af1ae0f1: `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes"; `git diff --check 779356dc af1ae0f1`: limpo; `python3 -m unittest tests.test_changelog`: 91 testes, OK; seção `[0.47.20]` com 25 linhas `- `.
- CI do PR #941 no head af1ae0f1 (run 46033563926): suíte (5 partes), instalação, passos, python 3.14, verificações longas, teto de pulados e catraca verdes; `bateria` e `bateria (pareceres)` esperam este parecer.

## Delta lido (rodada anterior, head 779356dc)
- `git log 8855671d..779356dc`: #937 (eba76f80), #936 (50e5b609), a marca #935 (447b4ad2) e o anexo #939 (779356dc).
- #937: squash igual ao head a2ef1548; os três pareceres (`v0481-f1p2-c1a.md`) aprovados em c31462e6, que difere do head só neles.
- #936: o patch do squash tem o mesmo `patch-id` do head d4f1f0f1 sobre 8855671d; os três pareceres (`v0481-encolhe-930.md`) aprovados em 27641d2a, que difere do head só neles.
- Anexo #939: toca só `CHANGELOG.md` (+2) e apaga os dois fragmentos; as linhas são iguais às dos fragmentos.

## Regras afrouxadas (tabela do PR da main)
- #936 entra na tabela: afrouxa `R-CONFORMIDADE` (HOOK-NAO-PROTEGE-RAIZ-DO-FORGE), marca no título e rótulo; motivo: a grafia do Bash na raiz do Forge fica com o `denyWrite` do sandbox do SO, Write e Edit seguem barrados; pedido de origem v0481 E46.1. O rótulo pelo time vale pela ordem do dono de 26/11 12:57.
- #937 não afrouxa: rótulo só por arquivo protegido (`bin/forge_pareceres.py`, ADR 0008); liste-o à parte ("rótulo sem afrouxar").

## Achados
- A1 (recomendado) CHANGELOG.md:7 · O PR homolog → main lista 8 regras afrouxadas com motivo e pedido de origem (#909, #918, #920, #928, #929, #931, #932 e #936) e cita o #937 como rótulo sem afrouxar.
- A2 (recomendado) CHANGELOG.md:21 · 6 itens de classe C sem `docs/qa/` na `develop` e o #934 sem parecer; o parecer de QA da release cobre a leva; vira cartão.

## Parecer
Aprovado no head af1ae0f1: o A3 (linha do #930 que afirmava uma guarda removida pelo #936 na mesma versão) foi apagado, e o delta não toca outro arquivo. A1 e A2 seguem recomendados, sem mudança.

- ci: af1ae0f1f6a5d710cab5d81933fa6c0df6340201 verde
