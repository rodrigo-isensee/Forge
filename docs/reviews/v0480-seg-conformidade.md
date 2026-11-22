---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-conformidade
commit: 14696864b679da061fc87f6dda8ad0b7227adb4f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E113.9, melhoria/v0480-seg-conformidade)

Revalidação da volta única (H2/H3, R-REVIEW). Delta lido: `forge-check parecer delta` deste parecer, intervalo `a4266c77..14696864` sem o que veio da `develop`: `hooks/conformidade.py` (S22 no merge, negação e subshell; RESTO-ANULA; `+=`; A20 com lançador), 83 fixtures novas, specs de mutantes `v0480-seg-conformidade{,-2..-5}.json` e três specs antigas acertadas ao texto novo (`impl-furo-hook-a-a3`, `v0435-hooks-n5`, `v047-destino-opaco`), `tests/test_conformidade_seg_v0480.py`, `tests/test_conformidade_verde.py`, `docs/hooks-fixtures.md` e o fragmento do changelog.

## Sondas
- S1 · branch main, forge:tech-lead, `git switch develop; git merge feat` · espera: código 2 · obtido: código 2 (era 0 em a4266c77: A1 fechado)
- S2 · branch main, forge:tech-lead, `git checkout develop || true; git merge feat` · espera: código 2 · obtido: código 2
- S3 · branch main, forge:tech-lead, `(git switch -c x) && git push origin` · espera: código 0 · obtido: código 0 (A2 fechado)
- S4 · branch main, forge:tech-lead, `(git switch develop); git merge feat` · espera: código 2 · obtido: código 2
- S5 · branch main, forge:tech-lead, `git switch develop || git merge feat` · espera: código 2 · obtido: código 2
- S6 · branch main, forge:tech-lead, `git switch -c x && git merge develop` e `git switch -c x; git push origin x` · espera: código 0 · obtido: código 0

## Parecer
Aprovado. A1 (merge com duas candidatas de integração) está fechado: `ramos_em` devolve as candidatas por `por_dureza` e o merge confere cada uma (`merge_na_integracao`, hooks/conformidade.py:2729); push, rebase e N5 seguem pela primeira, que é a mais dura. A2 (subshell que fecha depois da troca) está fechado por `alcance_da_troca`: a cadeia segue pelo `)` só quando o começo do grupo garante, e a branch é estado do repositório, então a troca dentro de `( … )` vale fora dele, como o hook agora modela. As chaves `{ …; } &&` com ação crítica recusam por fixture: falha fechada, aceita.

As três correções fora dos achados conferem: o teto do corpus (o `+=`/`del` sem chamada, comentário na linha), `test_conformidade_verde` (com `;` a troca é incerta, então o commit na main recusa: é o S22 aplicado, não afrouxa) e a A20 com lançador (`valores is None` cai nos corpos de substituição da palavra, só recusa a mais). As specs antigas mudaram só o texto `de`/`para` para casar com a fonte nova, com a mesma guarda.

Verificadores: `python3 -m unittest tests.test_hooks_volta_corpus tests.test_conformidade_verde tests.test_indice_fixtures tests.test_conformidade_seg_v0480` no head 14696864 com o ambiente limpo: 91 testes OK (509 s). Mutação do diff e suíte inteira: do autor e do CI do PR (V2), sem rerrodar aqui.
