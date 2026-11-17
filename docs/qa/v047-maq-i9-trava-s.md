---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-maq-i9-trava-s
commit: 07319ed9b506d894403898f7efde8e3ce08090bb
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047 MAQ-I9 fatia 2 (TRAVA_S 600 para 1200)

## Achados

## Critério → teste → resultado
Pedido de correção sem especificação de UX; a obrigação é a do item (trava com PID vivo vale até 1.200 s, PID morto solta na hora, `expiracao_horas` menor limita, a fila segue).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| PID vivo, 700 s: segue ocupado, vai para a fila | `TravaDeVinteMinutos.test_pid_vivo_ha_mais_de_10_min_segue_ocupado_e_vai_para_a_fila` | logo acima do valor antigo (600 s) | passou; cai na base |
| PID vivo, 1300 s: solta | `TravaDeVinteMinutos.test_pid_vivo_ha_mais_de_20_min_solta` | logo acima do novo teto | passou (mata M2) |
| `expiracao_horas` 0,25 (900 s) vale sobre 1.200 s | `TravaDeVinteMinutos.test_expiracao_menor_limita_os_20_min` | teto menor | passou |
| `bin/forge-pesado status` lê a mesma constante | `ForgePesado.test_trava_vencida_fica_livre` (1201 s) | logo fora do limite | passou |
| Fixture do hook, 1300 s sem Post: libera | `tests/hooks/pesado/sem-post-expira-em-20-min.json` | renomeado de 10 min | passou |

## Cenários e resultado real
- Testes dos arquivos tocados, com TMPDIR: `python3 -m unittest tests.test_pesado_fila tests.test_forge_pesado`: `Ran 23 tests ... OK`.
- Vermelho antes do verde (manual, cópia em `$TMPDIR` com `hooks/pesado.py` da base 73a0ab81 e os testes do head): `FAIL: test_pid_vivo_ha_mais_de_10_min_segue_ocupado_e_vai_para_a_fila`; `Ran 23 tests`, `FAILED (failures=1)`. O `forge-testes --vermelho` passou ao segundo plano sem veredito (prazo), então não o cito como prova.
- Mutantes: `bin/forge-mutante tests/mutantes/v047-maq-i9-trava-s.json`:
  `forge-mutante: pedido=v047-maq-i9-trava-s rev=8bff4e7dbb0a spec=53fa32a2...`; `M1 · morreu · hooks/pesado.py:33`; `M2 · morreu · hooks/pesado.py:33`. Linha de guarda mudada no diff: uma (`TRAVA_S`), coberta pelos dois mutantes. `--cobertura --base 73a0ab81` não lista condição sem mutante.
- A suíte inteira não rodou local; vale o check-run `bateria` do mesmo sha no CI do PR.
- Sem bugs; nada a registrar em `docs/qa/bugs/`.

## Revalidação (delta 8bff4e7d → 07319ed9)
- `forge-check parecer delta`: no domínio do QA, só `docs/hooks.md` mudou (10 → 20 minutos, 1.200 s, em 4 linhas); nenhum código, teste ou fixture tocado.
- `grep` em `docs/hooks.md`: nenhum "10 minutos" nem "600 s" restante sobre a trava; `hooks/pesado.py:33` `TRAVA_S = 1200` confere com a doc.
- Testes dos arquivos tocados (`tests.test_pesado_fila tests.test_forge_pesado`), com TMPDIR: `Ran 23 tests ... OK`.
- Vermelho, mutantes e CI: valem os do parecer anterior (código inalterado); suíte inteira, check-run `bateria` do mesmo sha.
