---
tipo: review
contrato: 1
pedido: v0457
branch: melhoria/ci-tempo-314
commit: c7a397269130d4d7a58d0d91aa93b2afa91bc232
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v0457 (E23.13, CI-TEMPO-314)

Diff d3453407..65f402e7 (3 arquivos, +6/-4; 8 linhas de código e teste, dentro da orientação M14): `timeout-minutes` de `rapida` (.github/workflows/ci.yml:37) e `rapida-quatorze` (:79) de 20 para 30, a lista de tetos em tests/test_catraca.py:3322 e o fragmento changelog.d/ci-tempo-314.md. Instância que não fez a entrega; os commits posteriores da branch (1f4cb184, 5237e994, ed412ebe) só trazem pareceres.

Conferido:
- Nomes dos jobs intactos: `scripts/arvore-testada.py:29` (JOBS_DE_PROVA) segue achando as duas provas; não dividir o job foi a escolha certa.
- Nenhuma linha de guarda (`if`, `||`, `&&`, `exit`, `raise`) mudou; sem mutante exigido pela catraca. `test_catraca.Workflows` (6 testes) verde no head.
- Medida (gh run view, jobs "checagem rápida" da develop): 3.12 em 12,9 / 15,1 / 15,9 min nos 3 runs citados e 12,7 a 18,0 min antes; um run (43109809984) cortou as duas versões nos 20 min. 3.14 em 16,1 a 16,5 min até 43099085052 (11/11) e cancelada aos 20,2 min em 43206261879, 43212986502 e 43219346032. A duração real da 3.14 hoje é desconhecida (> 20 min): 25 não daria folga comprovada; 30 é o menor valor redondo defensável. Custo zero (repositório público, `R-CUSTO`).
- Portão: o teto de tempo não é teste nem check exigido; subir o teto não tira teste nem portão (`R-VERIFY`). Mas a catraca acusa `R-CONFORMIDADE: mudança em .github/workflows/ci.yml` (arquivo de controle): o PR só passa com o rótulo `afrouxa-regra` do dono, aplicado depois do último push. Não há invariante afrouxado, então o título não pede o destaque de afrouxamento; o corpo do PR deve dizer que o rótulo é exigido só por tocar o ci.yml.
- Texto antigo (AR-9): nenhum outro texto vivo cita 20 min para as checagens rápidas.
- Fora da entrega: o `forge-check pr v0457` acusa `revisao-devops: sem parecer para o pedido v0457`; docs/devops/ci-tempo-314.md está com `pedido: ci-tempo-314` no frontmatter (cabe ao devops corrigir).

## Revalidação (E23.20)
- Merge da origin/develop (47d701f7) sem conflito no head c7a39726. `forge-check parecer delta docs/reviews/ci-tempo-314.md`: intervalo 65f402e7..c7a39726, escopo sem o que veio da base, `delta: nenhum arquivo do domínio mudou`. O patch da branch contra a develop segue o mesmo (ci.yml e tests/test_catraca.py idênticos). Parecer mantido.

## Achados
- A1 (recomendado) .github/workflows/ci.yml:37 · O comentário diz 3.12 13-20 e 3.14 17-20+ e folga de 50%; a medida dá 3.12 12,7-18 (um corte nos 20) e 3.14 16,1-16,5 até 11/11, depois mais de 20. A folga é sobre o teto antigo, não sobre a 3.14 real, desconhecida. Anotar a duração no 1º push com 30.
- A2 (recomendado) .github/workflows/ci.yml:79 · A 3.14 passou de 16,5 min (43099085052) para mais de 20 em menos de um dia; subir o teto absorve a piora sem achar a causa. Abrir cartão para medir por módulo qual teste cresceu e, com a duração real lida, dizer quando o teto volta a 25 (critério de reversão).

## Sondas

## Parecer
Aprovado. A mudança faz o que a E23.11 pede, sem tirar teste nem portão, com 30 min como menor teto com folga diante da 3.14 sem duração conhecida. A1 e A2 são recomendados e não devolvem. O merge depende do rótulo `afrouxa-regra` do dono (catraca, `R-CONFORMIDADE`) e da conferência de entrega do head.
