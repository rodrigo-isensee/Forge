---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-fechar-mensagem
commit: 3b1e324b285bd2037bdc49d928aef599583a972c
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
