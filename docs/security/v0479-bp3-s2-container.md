---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s2-container
commit: 1a7d0044c2c06149febad637179499ed729c2438
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-bp3-s2-container (BP3 S2, v0478 E39.15, revalidação no head 1a7d0044)

Volta por delta. As rodadas anteriores estão no git: reprovado no head 14c69010 (`b4f4274d`), aprovado com A3 recomendado no head ed21f2bd (`6995df56`) e aprovado sem achado no head c0087a7a (`19c484c6`). Delta lido: `forge-check parecer delta`, intervalo `c0087a7a..1a7d0044`, sem o que veio da base (merge `807ce884` da `origin/develop`, de `ef7739a` para `0f6034e`). No domínio: só `bin/forge-testes` (commit `1a7d0044`, 2 linhas). Já lido na rodada de c0087a7a e sem mudança: `hooks/conformidade.json`, o patch do dono, `tests/test_conformidade_vscode_container.py` e o mutante M5. Sem bateria local; a suíte inteira fica para o CI.

## Gatilhos
Gatilhos: execução automática de comando do work tree ao abrir a pasta, arquivo de controle do Forge (`hooks/conformidade.json`), sandbox do modelo de projeto (patch do dono), ciclo de vida do container.

## Veredito
**Aprovado**, sem achado aberto. A branch continua só apertando.

O delta só acrescenta `test_conformidade_vscode_container` a duas tuplas de seleção do teste dirigido: `FORGE_CHECK` (`bin/forge-testes:114`) e `REAPROVEITAM_O_LOTE` (`bin/forge-testes:119`, que `JUNTO_DO_MODULO` liga ao `test_hooks`). Nenhum nome sai, nenhuma regex de mapa muda e nenhuma lógica de controle é tocada. O efeito é rodar o teste de abuso em mais seleções: `bin/forge-testes --listar tests/test_hooks.py` e `--listar bin/forge-check` agora o incluem. O mapeamento ao lote do `test_hooks` é correto, porque o módulo reaproveita `test_hooks.Hooks.executar_em_lote` (`tests/test_conformidade_vscode_container.py:46`). O `forge-testes` é filtro do autor e do pre-push, não portão de CI. Mesmo que a seleção falhasse, a proteção não afrouxaria.

Estado dos achados anteriores: A1 (bloqueante), A2 e A3 (recomendados) seguem **resolvidos**. O delta não toca nenhum dos arquivos das correções. A camada `denyWrite` continua dependendo de o dono aplicar o patch revisado (blob `5ed6008b186ca4ae0f7e70a690b9c7a0484bd018`, PP1-APLICADO-PELO-DONO).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check parecer delta` e `bin/forge-testes --listar`. Faltaram no ambiente `gitleaks`, `zizmor`, `actionlint` e `semgrep`. Não instalei nada (`R-CUSTO`).
