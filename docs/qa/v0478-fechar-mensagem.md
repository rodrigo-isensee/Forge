---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-fechar-mensagem
commit: 8989baa06876e4ad25235c846aaf4926f686a1d1
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (FECHAR-PROMOVER-MENSAGEM-PT)

Escopo: `bin/forge-fechar` (P6 da promoção passa `--subject` e `--body` em português ao `gh pr merge --merge`; `mesclar_auto` repassa `"${@:3}"`; o `--squash` do passo 6 não muda).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| FECHAR-PROMOVER-MENSAGEM-PT: título `chore(promoção): <versão> para a homolog (#<n>)` e corpo em português | `Promover.test_merge_da_promocao_leva_titulo_e_corpo_em_portugues_com_o_numero_do_pr` | número do PR criado (42) e do PR reaproveitado (9) | passou |
| Método segue `--merge` preso ao head da marca | `Promover` (asserção ajustada do caminho feliz) | `--match-head-commit` | passou |
| Passo 6 (`--squash`) sem argumentos extras | `tests/test_fechar_lote.py` inteiro | `${@:3}` vazio | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_fechar_lote.py`: Ran 58 tests, OK.
- `bin/forge-mutante tests/mutantes/v0478-fechar-mensagem.json`:
  - `forge-mutante: pedido=v0478-fechar-mensagem rev=3b1e324b285b spec=a2d40490b09e8fb6b4721d52b2e876486e62ef478abb1d536227311d1e84231f`
  - `M1 · morreu · bin/forge-fechar:1118`
  - `M2 · morreu · bin/forge-fechar:783`
  Os dois mutantes cobrem as duas linhas de guarda mudadas no diff; nenhum sobrevivente.
- Não rodados: `forge-mutante --cobertura` e `forge-testes --vermelho` (fila R-TETO ocupada por outra sessão; o hook barrou) e `shellcheck` (ausente no ambiente). A morte de M1 e M2 pelo teste novo mostra que ele falha sem a implementação; a suíte inteira fica no check-run `bateria` do CI do PR.

## Revalidação (head 8989baa0, delta desde 3b1e324b)
- `forge-check parecer delta`: a base `develop` não foi encontrada no clone, e o intervalo saiu inteiro. Do domínio do QA, o que pertence a este pedido é só `tests/mutantes/v047-integracao-em-lote-8.json` (IL-M63 alinhado à linha nova do merge da promoção: `--merge "$sha" --subject`). O resto do intervalo veio da develop trazida pelo `forge-fechar`.
- `bin/forge-mutante tests/mutantes/v047-integracao-em-lote-8.json` (rc 0, 8 mutantes, nenhum sobrevivente):
  - `forge-mutante: pedido=v047 rev=8989baa06876 spec=78ba659ab1be415e5597f6461cdf9e393c4148242635f70574e9f1142636c01a`
  - `IL-M57 · morreu · bin/forge-fechar:119`, `IL-M58 · morreu · :141`, `IL-M59 · morreu · :152`, `IL-M60 · morreu · :153`
  - `IL-M61 · morreu · :1068`, `IL-M62 · morreu · :1123`, `IL-M63 · morreu · :1118`, `IL-M64 · morreu · :1456`
- Sem `--base`: o comando rodou a spec inteira. O parecer anterior (aprovado) segue valendo; nenhum achado novo.
