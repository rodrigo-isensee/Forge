---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae2-contador
commit: 78d374c304596115ba438a93173bd8f3a0aec554
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E54.7, desenho do AE2 e do contador no head 78d374c3)

Diff contra a base 5ccac0bf: `docs/propostas/v0479-ae2-contador.md` (202 linhas, só texto) e o fragmento `changelog.d/v0479-ae2-contador.md`. Classe T, sem código; sem suíte local e sem CI (sem PR), pelo brief. Desenho já aceito pelo dono (DECISÃO DO DONO de 20/11 13:51, D1 a D9); o review confere a forma e os fatos citados, não reabre as decisões.

Conferido contra o repositório: `montar_quadro`, `_ler_regular` e `chave_do_cartao` existem em `bin/forge-check`; `medir_mensagem` e `TETO_DA_MEDIDA` em `hooks/meta.py`; `templates/projeto/.github/pull_request_template.md` existe (o "se existir" do C8 se resolve). A develop integra por squash (`(#N)` no fim do assunto, últimos 8 da primeira linha), caso que a seção 4.1 já cobre. Por que o existente não basta, critério de reversão com fato observável, medida de sucesso, `Afrouxa: não`, casos de abuso por item e gatilhos de segurança (`R-SEGURANCA`) presentes (`R-DECISAO`). Neutro (`R-NEUTRO`): sem stack, projeto ou cartão real.

## Achados
- A1 (recomendado) docs/propostas/v0479-ae2-contador.md:79 · A marca "última tag alcançável de origin/develop" é falsa no fluxo develop → homolog → main: v0.47.11 não é ancestral da develop (review do C1, A1, S1 a S3). Emendar a 4.1: maior tag na forma entre todas e `<tag>..origin/develop`, antes ou junto da volta do C1.

## Sondas

## Parecer
Aprovado. O desenho entra na develop como documento; a emenda da seção 4.1 pode vir depois, por PR próprio do arquiteto.

Por que o A1 não bloqueia: (1) é um documento de proposta, que não roda; o defeito só tem efeito no código do C1, e lá já está bloqueado pelo review do C1 (`docs/reviews/v0479-ae2-c1-contagem.md`, A1), com a correção sugerida; (2) o próprio desenho previu o caso: o critério de reversão (b) da seção 8 disparou e reabriu o C1, como o texto manda; (3) o registro do pedido (20/11 14:39 e 14:52) já atribui a emenda da 4.1 ao arquiteto e decide que os três desenhos entram na develop antes das emendas, para que as ADR e emendas citem um arquivo que exista na develop. Segurar este PR só trocaria a ordem sem ganho.

Condição para o lote: a emenda da 4.1 entra na develop antes ou junto da volta do C1, para que código e desenho não divirjam na develop. Sondas confirmadas aqui: `git merge-base --is-ancestor v0.47.11 origin/develop` sai 1 (não ancestral), igual à S2 do review do C1.
