---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/parecer-ux-livre
commit: a061a495677e611fe38ee127d6b53fb225c02e11
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033, L05 (E9 PARECER-UX-LIVRE)

Revisor: forge:tech-lead, outra instância (D-ETAPAS-INST = A); não sou o autor do a061a49. Base `dc615c2` (Base-sha do brief, igual a `origin/develop` na leitura). Diff lido inteiro: 3 arquivos, um commit.

## Achados
- A1 (recomendado) tests/test_forge.py:4916 · o caso do merge passa sem a entrada em LIVRES (mutante sem docs/ux/ verde) e a develop traz também src/y.txt, então não é "só docs/ux/"; ele prova a comparação por conteúdo do E4, não a LIVRES. Sugestão: tirar src/y.txt ou dizer no nome que guarda o E4.

## Diff contra o Entregar do brief versao-033-tech-lead-58
- `bin/forge-check:141`: só a entrada `"docs/ux/"`, com barra, no fim da tupla; o resto de `LIVRES` e a `livre()` (`:404`) iguais (C-1; T-1 ausente).
- C-2: a `LIVRES` só atua em `commit_vale` (`:459`, `:472`, via `arquivos_divergentes` `:437`), no `pr` (`:759`) e no `delta` (`:1327`); `gatilhos`, `arquivos_da_entrega`, `escopo:` e `PASTA_E_REGRA` não a leem e o diff não os toca (T-2 ausente).
- T-3: o PR leva só o E9 (afrouxa); nada do E2 nem do E3. O rótulo `afrouxa-regra` é do dono (E1.8), fora deste parecer.
- C-4 fora deste diff pela DECISÃO TÉCNICA de 2026-11-04 08:53 (vai ao L08); não cobrado.
- Fragmento `changelog.d/parecer-ux-livre.md` em `### Alterado`, com a consequência do delta registrada.
- Commit em Conventional Commits em português, um comportamento; teto M14: 50 linhas contadas (`bin/` 2, `tests/test_forge.py` 47; fragmento fora), abaixo de 150.

## Os 6 testes novos (classe PareceresComDocsUx), com mutantes do revisor
Rodados numa cópia da árvore em `$TMPDIR`, sem tocar a branch. Na árvore do head: 6 de 6 verdes.

| Mutante em `bin/forge-check` | Testes que reprovam |
|---|---|
| sem a entrada `docs/ux/` | tupla exata, commit só em docs/ux, renome |
| `docs/ux` sem barra | tupla exata, commit só em docs/ux, renome |
| `docs/` no lugar | tupla exata, nomes parecidos (os 3 subtestes) |
| `livre()` ignorando caixa | nomes parecidos (`docs/UX/a.md`) |
| entrada extra `docs/pedidos/` | tupla exata |

- Tupla exata (C-1): confere a tupla inteira, sem amostra; mata sem a entrada, sem barra, mais larga e extra.
- Commit só em docs/ux/ (C-3): o caso liberado; reprova sem a entrada.
- Nomes parecidos (C-3): `docs/ux-x/`, `docs/UX/`, `docs/uxa.md`; teste de abuso, verde sem a entrada por construção, e mata a forma mais larga e a caixa ignorada (T-1).
- Renome de hooks/ para docs/ux/ (C-3): exige `desatualizado: hooks/x.py`; reprova sem a entrada porque a saída cita só o primeiro arquivo divergente (`docs/ux/x.py`). Prova o que diz com a entrada presente.
- docs/ux/ mais um byte em bin/ (C-3): abuso, verde sem a entrada por construção; guarda contra isentar o commit inteiro.
- Merge da develop (C-3): verde também sem a entrada (A1, recomendado; o comportamento pedido vale).

Achados recorrentes (PA-7) conferidos contra o diff: nenhum se aplica (sem shell, sem falso de git ou gh, sem ambiente herdado; o teste roda com `ambiente_limpo()`).

## Verificação
- `python3 -m unittest tests.test_forge.PareceresComDocsUx`: 6 testes, OK.
- `python3 -m unittest tests.test_forge` (D-5 reformulada, só este módulo): 488 testes, OK, no head a061a49.
- `forge-check docs`: rc 0, sem linha sobre este parecer.
- Segurança (E1.4) roda em paralelo, com parecer próprio em `docs/security/`; não refeita aqui. Devops (E1.5) não se aplica: o diff não toca `.github/` nem o pre-push.

## Parecer
Aprovado. A mudança é a mínima da decisão Q12 = A, cumpre C-1 a C-3 sem nenhuma T-n, e os testes matam os mutantes de afrouxamento maior. O A1 é recomendação de clareza do teste e não devolve.
