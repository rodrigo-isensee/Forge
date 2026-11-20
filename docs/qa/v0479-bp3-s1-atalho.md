---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s1-atalho
commit: e686f2eb464aafc1dc03b9622a1fc45c640ab18f
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E39.13 (atalho durável, BP3 S1)

## Resolvido
A1 (README.md:43, `claude` solto): o parágrafo diz "executável" e "Claude Code"; `test_sessao_automatica.py` passa (13 testes).

## Revalidação 2 (head e686f2eb)
`forge-check parecer delta` (45f429a4..e686f2eb): `scripts/jarvis` e `scripts/jarvis-forge` (`aqui=` guardado antes do cd, usado no source, na raiz da atualização e no `eu=`), `jarvis-comum.sh` (janela de 1 a 6 dígitos sem zero à esquerda), `bin/forge-testes` (README mapeia `test_atalho_duravel`), changelog, spec de mutantes -3 e `test_atalho_duravel.py` (8 testes de caminho relativo, 1 de janela válida e inválida).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A3: pasta do script vem do próprio script, chamado por caminho relativo | `ChamadaPorCaminhoRelativo` e `...Forge` (4 cada), M29 a M34 | arquivo comum falso no projeto, ferramenta do projeto, `eu=` absoluto | passou |
| Janela só de 1 a 6 dígitos sem zero à esquerda | `test_janela_so_aceita_de_um_a_seis_digitos_sem_zero_a_esquerda`, M35 | 1, 999999, 1234567, 08, 09, 010, 20 dígitos, negativo, decimal, espaço | passou |

Execução local (TMPDIR): `test_atalho_duravel` 81 testes OK; `test_sempre_atual` 142 OK; `test_testes_tocados` 164 OK (1 skip já existente). Suíte inteira e shellcheck: CI do PR.

Mutação: `bin/forge-mutante --base 45f429a4 ...-1.json ...-2.json ...-3.json`: `base=45f429a4f2cdc300318fda6d84198f4ebce9971d mb=45f429a4f2cdc300318fda6d84198f4ebce9971d rev=e686f2eb464aafc1dc03b9622a1fc45c640ab18f`; 35 mutantes (M1 a M35), todos `morreu`, rc 0. M29 a M35 cobrem uma guarda mudada cada (source, raiz da atualização e `eu=` nos dois atalhos, e o `case` da janela).

Vermelho: `forge-testes --vermelho 004ce869 --modulos test_atalho_duravel`: `vermelho: base=004ce869d641 head=e686f2eb464a`, rc 0; `contagem: prova (API ausente)=79; prova (asserção)=2`; os 8 de caminho relativo e o de janela provam (H=ok, B=erro).

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
