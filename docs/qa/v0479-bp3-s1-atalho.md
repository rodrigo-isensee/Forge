---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s1-atalho
commit: 45f429a4f2cdc300318fda6d84198f4ebce9971d
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E39.13 (atalho durável, BP3 S1)

## Achados
- A1 (resolvido) README.md:43 · o `claude` solto saiu: o parágrafo diz "executável"/"Claude Code"; `test_sessao_automatica.py` passa (13 testes).

## Revalidação (head 7bd41f53 + commit de teste 45f429a4)
`forge-check parecer delta` (3e53ae72..45f429a4): README, changelog, índice, `scripts/jarvis`, `scripts/jarvis-forge`, `scripts/jarvis-comum.sh` (novo, resolvedor e supervisor comuns), specs de mutantes (-1 e -2 reescritas, -3 e -4 removidas), `test_atalho_duravel.py`, `test_doutor.py`, `test_sempre_atual.py` e o oráculo. Mudança de comportamento: janela zero ou texto volta a 1800 (teto de 3 nunca some); 143 (kill de propósito) é parada, não queda.
Oráculo `tests/test_oraculo_sempre_atual.py`: commit meu 45f429a4, uma linha, o Mundo (`atalho_instalado`) copia `scripts/jarvis-comum.sh` para a pasta falsa; sem ela o `scripts/jarvis` copiado não achava o arquivo comum.

## Critério → teste → resultado
| Critério (decisão do dono) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Reabre com `--continue` só em saída anormal (>=128, fora 129/130; 143 é parada) | `test_atalho_duravel.py`, M1 a M3, M24 | 0, <128, 129, 130, 143 | passou |
| Teto de 3 reaberturas em 30 min, depois desiste | `test_atalho_duravel.py`, M4, M5, M9 | 3.ª/4.ª queda | passou |
| Janela zero ou texto volta ao padrão | `test_atalho_duravel.py`, M8, M25 | 0, texto | passou |
| `quedas.log` só com data, projeto, saída, tentativa, ação | `test_atalho_duravel.py` | sem texto do claude | passou |
| Fora do tmux só avisa e abre | `test_atalho_duravel.py`, M16 a M23 | `--sem-tmux`, tmux ausente | passou |
| Abre o executável mais novo (instalador × PATH) | `test_atalho_duravel.py`, M12 a M15 | empate, um candidato, sem `--version` | passou |
| Instruções de abertura sempre em modo auto | `test_sessao_automatica.py`, M26, M27 | linha com `claude` solto | passou |
| Atalhos continuam instaláveis e doutor ok com arquivo comum | `test_sempre_atual.py`, `test_doutor.py` (copiam o comum) | arquivo comum ausente | passou |

## Execução (local, TMPDIR, só arquivos tocados)
- `test_atalho_duravel.py`: 71 testes, OK.
- `test_sessao_automatica.py`: 13 testes, OK.
- `test_sempre_atual.py`: 142 testes, OK (os 6 que falhavam sem o comum passam).
- `test_oraculo_sempre_atual.py`: 59 testes, 39 falhas e 1 erro, todos fora do atalho (dívida pré-existente do pedido v0474: o mesmo `test_idempotente` falha idêntico numa cópia de 004ce869, a base). Vira cartão, não bloqueia esta entrega. Suíte inteira e shellcheck: CI do PR.

## Mutação
`bin/forge-mutante tests/mutantes/v0479-bp3-s1-atalho-1.json tests/mutantes/v0479-bp3-s1-atalho-2.json`: 28 mutantes (M1 a M28), todos `morreu`, rc 0. Conferido à mão contra as guardas de `jarvis-comum.sh` (linhas 75, 79, 82, 92, 66 a 69, 38 a 42): cada uma tem mutante. `--cobertura --base 3e53ae72` devolve `não coberto: scripts/jarvis`, `jarvis-comum.sh` e `jarvis-forge` (shell não é conferido pela ferramenta) e `spec removida` para -3 e -4 (fundidas em -1 e -2).

## Vermelho antes do verde
Vale o do parecer anterior (`forge-testes --vermelho 004ce869`: 43 testes provam a entrega; a única regressão era A1, agora corrigida). Os testes novos desta volta (janela zero, 143) caem sob M24 e M25.

## Bugs
Nenhum arquivo em `docs/qa/bugs/`: A1 corrigido.
