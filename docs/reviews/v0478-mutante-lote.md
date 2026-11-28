---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-mutante-lote
commit: 5520fd0d156beede30c54efb16227559be919e85
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E17.6, melhoria/v0478-mutante-lote)

Revalidação (H3, `R-REVIEW`) no head 5520fd0d. Delta lido só por `forge-check parecer delta docs/reviews/v0478-mutante-lote.md`: intervalo `b11631b2..5520fd0d`, domínio código e testes; no domínio `bin/forge-mutante`, `changelog.d/v0478-mutante-lote.md`, `tests/mutantes/guarda-sem-mutante-9.json`, `tests/mutantes/mutante-isenta-linha.json`, `tests/mutantes/v0478-mutante-lote{,-2,-3}.json` e `tests/test_forge_mutante.py`. Os merges `bdbf2872` e `b39110b2` trazem só pareceres (E17.3, E17.4), fora do domínio.

## Sondas
- S1 · spec sem M1 e M2, isenta de trecho `args.ids is not None`; `--cobertura --base 0c47762a` · espera: rc 1 (duas guardas distintas) · obtido: rc 1, `sem mutante` em :1151 e :1192 e `isenta velha`

## Parecer
Aprovado. Os achados A1 e A2 do parecer anterior (b11631b2) estão resolvidos na forma pedida pela segurança: a isenta da condição nova vale só para as cópias da mesma condição (`irmas`, nós das condições novas de mesmo texto), exige o trecho dentro do nó e toda ocorrência dele no arquivo dentro de uma dessas cópias. Trecho comum a condições diferentes, cópia fora do hunk e comentário não isentam mais; a S1 refeita, que antes saía rc 0, agora sai rc 1 com as duas guardas `sem mutante` e a isenta velha. O caso legítimo (duas cópias idênticas da mesma condição, uma isenta) segue rc 0 pelo teste de E17.1, sem afrouxar: a isenta só cobre texto que é literalmente a mesma guarda.

`cabe` e `ocorrencias` são pequenas e de um propósito; `nova=None` como sentinela deixa o modo explícito. Guardas mudadas com um mutante por linha: M7 (`if nova is not None`), M8 e M9 (`no_no and all`), M11 (`c[0] == texto`), M18 (`cabe`), M12 com `None`; M58 e IL11 realinhados à fonte nova. O teste novo cobre os três ramos de falha por subTest e reseta a base entre eles. O changelog descreve o comportamento novo. Tamanho do delta: cerca de 20 linhas de código, dentro do teto (H1).

Ferramentas: `bin/forge-mutante --ids` no head: M7, M8 (v0478-mutante-lote), M9, M11 (-2) e M18 (-3) morreram. Rodei só o teste novo e o de E17.1 (`OK`, 2 testes); a suíte inteira fica no CI do PR.
