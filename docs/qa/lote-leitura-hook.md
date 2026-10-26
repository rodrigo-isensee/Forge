---
tipo: qa
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: d67f31fdeb1b66b85771a7687b2f2a88e2a63c9a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-26
---
# QA: lote-leitura-hook (revalidação 16: volta I, só testes e specs)

Pedido RET-LEITURA-HOOK-H-REV, E3.1, em paralelo com o review e a segurança (ACELERA-RODADA "A", item 4). Delta sobre `0e8776d` (revalidação 15, que reprovou só por teste): `git diff 0e8776d..d67f31f` toca `tests/test_hooks.py` (+35/-14), `tests/mutantes/lote-leitura-hook-volta.json` (nova) e os documentos de parecer; `hooks/` não mudou (conferido: nenhuma linha em `hooks/` no diff). O comportamento verificado na revalidação 15 (varreduras de 52 390 formas, 0 regressões, sondas vivas, bugs 2 e 3 fechados) segue valendo sobre o mesmo código. Tudo rodado na worktree do head, saídas em `$TMPDIR/qa-engineer-lote-leitura-hook/`.

## Achados

## Fechamento dos achados da revalidação 15
- **A1 (bloqueante) fechado.** `test_alvos_do_tee_atras_do_texto_dividido_aberto` (`tests/test_hooks.py:3432`) cobre mais de um alvo e as opções `-a`, `--append`, `-i` atrás de `env -aS'"' tee`. Prova à mão contra o head (cópias descartáveis com a troca em `hooks/conformidade.py:1714`, só esse teste): X5 (só a primeira palavra depois do `tee`) `FAILED (failures=5)`; X6 (a opção entra como alvo) `FAILED (failures=4)`; head sem mutação `Ran 1 test ... OK`. X5 e X6 morreram.
- **A2 (recomendado) fechado.** `tests/mutantes/lote-leitura-hook-volta.json` declara X1, X3, X5 e X6, e `test_spec_de_mutantes_do_lote_e_valida` agora valida as duas specs (teto de 8, `de` único no arquivo). Conferência da lista contra o diff da volta H: linhas de guarda mudadas são 853 (B1), 1889 (B2), 1899 (X1), 859 (X3), 1923 (B3) e 1714 (B4, X5, X6), todas com mutante.
- **A3 (recomendado) segue como estava:** `docs/hooks.md:95` e o teto K afetam só a autoria, não a recusa; não é bloqueante nem foi pedido corrigir nesta volta.

## Critério -> teste -> resultado
| Critério (RET-LEITURA-HOOK-H, seção 2.B da rev14) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| 1 a 4 e 6 (propriedade, fixtures, varredura, sonda viva, caminho com marcador) | `tests.test_hooks` inteiro (92 testes) e o resultado da revalidação 15 sobre código idêntico | `-S` certo depois de palavra fora da tabela; uma leitura só; aspas abertas; marcador | passou |
| 5 e 7. Mutantes B1 a B4 e spec válida | `forge-mutante` nas duas specs; `test_spec_de_mutantes_do_lote_e_valida` | as linhas de guarda 853, 856, 1714, 1889, 1893, 1896, 1897, 1923 | passou (todos morreram) |
| 5a. Detalhes da regra do `tee` (mais de um alvo, opção do `tee`) | `test_alvos_do_tee_atras_do_texto_dividido_aberto` | mais de um alvo; `-a`, `--append`, `-i` fora | passou (X5 e X6 morrem) |

## Evidência
- `python3 -m unittest tests.test_hooks` (módulo inteiro, head `d67f31f`): `Ran 92 tests in 760.193s`, `OK`, rc=0.
- `bin/forge-mutante tests/mutantes/lote-leitura-hook-volta.json`:
```
forge-mutante: pedido=lote-leitura-hook rev=d67f31fdeb1b spec=5966b4cfc20fda80dc65eea2a7100d378cbd3a8ca373d48b7de62641681c1dc0
X1 · morreu · hooks/_comum.py:1899
X3 · morreu · hooks/conformidade.py:859
X5 · morreu · hooks/conformidade.py:1714
X6 · morreu · hooks/conformidade.py:1714
rc=0
```
- `bin/forge-mutante tests/mutantes/lote-leitura-hook.json`:
```
forge-mutante: pedido=lote-leitura-hook rev=d67f31fdeb1b spec=55a5496ca95f498d3b79d2283ce68fd313127927db8353e955e381aea2d54df2
B1 · morreu · hooks/conformidade.py:853
B2 · morreu · hooks/_comum.py:1889
B3 · morreu · hooks/_comum.py:1923
B4 · morreu · hooks/conformidade.py:1714
M1 · morreu · hooks/_comum.py:1896
M2 · morreu · hooks/_comum.py:1897
M3 · morreu · hooks/_comum.py:1893
M9 · morreu · hooks/conformidade.py:856
rc=0
```
- `scripts/validar-plugin.sh`: `Validation passed`.
- Vermelho antes do verde: o teste novo guarda código que já existia (`hooks/` não mudou na volta), então a base não o faz falhar; a prova de que ele pega defeito são os mutantes X5 e X6 (falha observada acima e na saída do `forge-mutante`), que é a forma que o parecer da revalidação 15 pediu. `forge-testes --vermelho` não dá veredito para `tests.test_hooks` (prazo, como já registrado).
- PA-7 (`docs/engineering/achados-recorrentes.md`): sem linhas; nada a conferir.

## Riscos
- Nenhum bloqueante aberto. A3 (promessa do texto no teto K) fica como recomendação.
- O módulo `test_hooks` leva cerca de 760 s sob a carga desta máquina; segue além do prazo do `forge-testes --vermelho`.
