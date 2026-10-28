---
tipo: revisao-seguranca
contrato: 1
pedido: pr-verde-lote-check
branch: melhoria/pr-verde-lote-check
commit: 044ef1d4ae7ce8f7136ef07fd4c0b810e8d91616
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: pr-verde-lote-check

Pedido PR-VERDE-LOTE-CHECK (G1, G2, G6 e D4 do ESTUDO-PR-VERDE), revisado no pedido PR-VERDE-LOTE-CHECK-REV (E2.1), rodada 2 (revalidação por delta). O parecer anterior estava em `26d2260eecbc01712927cfdaa67003df6b0ec107` e foi gravado no commit `cc82b460ce7e1ef5366c9eba4aa32f02c0f88023`. Delta revisto: `26d2260..044ef1d`, com `bin/forge-check`, os testes e os mutantes `M9` a `M16`. Veredito: **aprovado**. Os dois bloqueantes (A1 e A2) estão corrigidos, com teste e mutante, e o A3 caiu junto com o A2. Os A4 e A5 seguem como recomendação, em prosa.

## Gatilhos
- `controles do Forge`: `bin/forge-check`, um arquivo protegido (portões `entrega`, `pr`, `delta` e `brief`).

## Achados

## Detalhe dos achados
**A1, resolvido (G2, `bin/forge-check:991-994`).** No merge da base, o escopo agora é `(diff(p1,M) ∩ diff(p2,M)) ∪ (diff(mb,p2) ∩ diff(p2,M))`, a correção mínima pedida. Se o `merge-base` falhar, o código usa `diff(p2,M)` inteiro, o que é falha fechada.
- Sondas em `$TMPDIR/security-engineer-pr-verde-lote-check/` (`sonda_g2_sem_desde.py` e `sonda_g2_v2.py`), rodadas nas etapas `codigo`, `review` e `pr`:
  - `merge -s ours` com parecer depois: lista `src/app.txt +1 -1` e `d.txt +0 -1`.
  - Risco declarado pelo autor, o head é o próprio `merge -s ours` sem commit depois: lista `a.txt`, `src/app.txt` e `d.txt`.
  - Conflito resolvido com "o meu lado" (`checkout --ours`): lista `src/app.txt`.
  - Merge limpo seguido de um `merge -s ours` de uma correção nova da base: lista `src/app.txt`.
  - Merge limpo, inclusive com o head no merge: o que a base trouxe continua fora do escopo, como pede o G2.
- Nenhum caminho novo abre. O termo novo só acrescenta nomes ao escopo, nunca tira.
- Cobertura: o teste `test_merge_que_descarta_a_base_mostra_o_que_ela_desfez` e o mutante M14, que rodei aqui e que morre.

**A2, resolvido (D4, `bin/forge-check:388-390`, com uso em `:421`, `:423`, `:456` e `:1151`).** A função `livre` casa por igualdade a entrada sem `/` no fim e só a com `/` por prefixo. Ela vale no `commit_vale`, no merge simulado (o `arquivos_divergentes`, que trocou o pathspec `:(exclude)` pelo filtro em Python, com resultado equivalente e mais estrito) e no `cmd_delta`.
- Sonda `sonda_d4.py`: `changelog.d/ramo.md.md`, `changelog.d/ramo.mdx/codigo.py` e `changelog.d/ramo.md~` voltam a desatualizar o parecer.
- O fragmento `changelog.d/{pedido}.md` (`:706`) é comparado com o nome normalizado pelo git. Um `pedido` com `../` ou `/` não casa com nenhum outro caminho.
- Cobertura: o teste `test_d4_so_o_caminho_exato_do_fragmento_sai_do_hash`, o teste do merge simulado com `--base` e o mutante M15, que morre.

**A3, resolvido junto com o A2.** `KANBAN.md` (`:125`) passou a casar pelo caminho exato, e `KANBAN.md.x` volta a contar.

**A4, recomendado e mantido (`bin/forge-check:493`).** Já existia antes desta entrega. Com `--desde` posterior ao merge `-s ours`, ou com o `Base-sha` anterior ao avanço da base, a reversão não aparece no `entrega`. Na sonda, o resultado foi o mesmo antes e depois da entrega. A dimensão fica para um cartão próprio: comparar o head com a base atual.
- Severidade: baixa. Dono: `tech-lead`.

**A5, recomendado e mantido (`bin/forge-check:706`).** O fragmento livre sai do argumento do `pr`, não da branch. Usar `branch_da_convencao` quando houver.
- Severidade: informativa. Dono: `tech-lead`.

**Conferido sem achado no delta:**
- **`CAMINHO_NO_PQ` (`:4384`):** o lookahead do curinga só deixa de cobrar um caminho com glob, e o G1 só acrescenta reprovação. O custo é quadrático no tamanho de um trecho entre crases: com 16 mil caracteres adversos, de 0,4 a 1,7 s. A entrada é o brief escrito pelo Jarvis, então não há caminho de ataque realista.
- **G6:** o caso do brief do `-REV` de outra branch (`tests/test_forge.py:4656-4665`) continua anexando a remoção, e o mutante M11 cobre esse caso.
- **Testes do item:** 163 testes passam, em `test_portao_diff_proprio`, `test_conferencia_base_dono`, `test_etapa_do_brief` e `test_volta_por_delta`.
- **PA-7** (`docs/engineering/achados-recorrentes.md`): a lista está vazia, então não há item a conferir.

## Riscos aceitos e ferramentas
- Nenhum risco aceito.
- Ferramentas: revisão estática, `forge-check delta`, `forge-mutante` (M14 e M15) e sondas locais em repositórios temporários.
- Lacuna: `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH. A entrega não toca workflow nem dependência.
