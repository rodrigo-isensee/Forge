---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-afetados-catraca-custo
commit: ecc3b7429450779edbda367bb40ddf834e4417d4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048 (#960, AFETADOS-CATRACA-E-CUSTO), volta 1

E9.9, revalidação por delta no head ecc3b742 (rodada anterior: parecer aprovado no f4ae675c, no git). Delta lido por `forge-check parecer delta`: no domínio só `bin/forge-testes`; relidos também, fora do domínio, `tests/test_afetados_catraca_custo.py` e `tests/test_forge_mutante.py` (classe `ContratoDoListar`), e o consumidor `.githooks/pre-push` (função `afetados`, que lê o stdout do `--listar` com o stderr descartado).

## Gatilhos
Gatilhos: código de controle (bin/forge-testes, sensível da catraca), hook de envio (plano do pre-push opt-in).

## Sondas

## Detalhe dos achados
Achados anteriores:
- **A1 (catraca apagada ou em link): resolvido.** `custo_e_catraca` (bin/forge-testes:587) pede a catraca quando ela é link (com qualquer diff) ou some e está no diff; `catraca_rodavel` (bin/forge-testes:597) impede a execução, e o código de saída fica 1 (bin/forge-testes:1381) com o aviso no stderr (bin/forge-testes:1368). Sondas numa cópia descartável, base ed6e6dbf: catraca apagada num commit, `--afetados --listar` no modo do diff traz a catraca e o aviso "apagado ou trocado por link"; `--afetados -- tests/catraca.py` dá rc 1 com o mesmo aviso; link com diff só em `docs/README.md` traz o aviso no `--listar`. Testes: `test_catraca_em_link_pede_a_catraca_e_nao_e_rodavel`, `test_catraca_apagada_no_diff_pede_a_catraca`, `test_catraca_em_link_reprova_sem_executar` (rc 1 e a catraca não executada).
- **A2 (scripts/ fora da catraca): resolvido.** `scripts/` em `PASTAS_DA_CATRACA` (bin/forge-testes:553). Sonda: commit de `scripts/novo-sonda.sh` com `claude -p "oi"`; o `--listar` agora traz "catraca no diff", e a catraca, que o plano executa, dá rc 1 com `R-CUSTO: claude-print em scripts/novo-sonda.sh:2`. Teste: `scripts/outro.py` em `test_hooks_bin_e_protegidos_levam_a_catraca_e_o_custo`. `.github/` fora dos protegidos segue fora da catraca local; o CI a roda, e já era a letra do E9.1 (sem achado).

Delta novo:
- **Linha da catraca no stderr.** O pre-push descarta o stderr do `--listar` e casa só o começo do stdout ("forge-testes: dirigido ("), então o plano com catraca continua executado; o `modulos_listados` do forge-mutante volta a ler o recorte (contrato em `ContratoDoListar`). Os dois testes que mudaram (`test_catraca_em_link_*`, `test_o_resto_fica_como_esta` sem `scripts/outro.py`) fixavam a falha aberta da rodada anterior; trocá-los fecha a falha, não afrouxa.
- **Catraca apagada só na árvore, fora do diff (observação, sem achado).** Com caminhos explícitos (o modo do pre-push) e `tests/catraca.py` apagado na árvore sem commit, `--afetados --listar -- bin/forge-check` segue sem catraca e sem aviso, rc 0: a ferramenta não distingue esse caso do projeto sem catraca. Sem caminho de ataque: o commit enviado tem a catraca, o envio local é opt-in e o CI roda a catraca da base. No modo do diff (sem caminhos) o mesmo caso é pego, porque o `git diff` lista a remoção.
- Nenhum caminho novo vira execução: `catraca_rodavel` só lê o tipo do arquivo, e a execução segue com argv em lista, `-I`, sem shell.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Testes rodados no head: `tests.test_afetados_catraca_custo` e `tests.test_forge_mutante.ContratoDoListar`, 23 testes, OK. Suíte inteira: CI do #960 no ecc3b742 (run 46159710035), suíte 1/5 a 5/5, teto de pulados, instalação, catraca e catraca (conferência) verdes; vermelhos só `bateria (pareceres)` e o agregado `bateria`, pelo parecer de QA reprovado no f4ae675c, que espera a revalidação. Ferramentas ausentes no PATH (lacuna, não instaladas): varredor de segredo, SAST, auditor de dependências e linters de workflow; o delta não toca workflow nem dependência.
