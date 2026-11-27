---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: 10c1b834b6fb062bfb2f9b7d9020dbbcbe828abf
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E37.6, HOOK-NAO-PROTEGE-RAIZ-DO-FORGE, PR #930, volta 1)

Revalidação por delta (H3) do head `10c1b834`, sobre o parecer reprovado de `baffa052`. O critério é o mesmo da 1ª rodada, sem `critério mudou:`.

## Achados
- A1 (recomendado) hooks/conformidade.py:4317 · vem da 1ª rodada e fica fora do delta: `rm -rf .` na raiz passa (rc 0), como no projeto. Não é regressão; vira cartão para os dois.

## Sondas

## Parecer
**Aprovado.** Os dois bloqueantes da 1ª rodada (o CI vermelho) estão resolvidos, e o CI do head está verde.

- **Delta lido** (`forge-check parecer delta docs/reviews/v0481-hook-raiz-forge.md`, intervalo `baffa052..10c1b834`):
  - `hooks/conformidade.py`: `EM_VIGOR_NA_RAIZ` com `.devcontainer/`, `.devcontainer.json` e `.claude-plugin/`; `MOTIVO_EM_VIGOR`; `EM_VIGOR_NO_TEXTO`; `GuardaDaProva.checar_texto`; `GuardaDaProva.destino_opaco`; a recusa própria em `checar_caminho` e em `barrar`; o ramo do erro interno em `prova_fora_de_projeto`.
  - `tests/test_hooks.py`, com os mínimos 17 e 28.
  - A fixture `estadoclone-rm-git-bloqueia` e as 26 fixtures `raiz-forge-*` novas (45 no total).
  - `docs/hooks-fixtures.md`, `docs/hooks.md` e o fragmento do changelog.
  - As specs de mutante `v0481-hook-raiz-forge{,-2,-3}.json` e o M19 de `v0479-entrega-parecer-mesclado-4.json`.
  - Os commits de parecer do intervalo (`03e1d065`, `d4a8a3b2`, `ebaaf3c0`) ficam fora do domínio.
- **A1 e A2 da 1ª rodada:** a fixture `estadoclone-rm-git-bloqueia` agora espera o motivo da entrada `.git`, e a recusa continua (rc 2). O índice lista `raiz-*`, e `test_indice_fixtures` passa.
- **Escopo (item 1):** o delta faz o que pedem os achados A1, A2, A3 e A5 da segurança. O efeito colateral do A1 está declarado na docstring e no commit: o texto de interpretador que escreve e cita uma entrada também é recusado na cópia de `wt/`, onde a saída é o Write ou o Edit. O falso positivo só alcança texto de interpretador com escrita (`ESCRITA_NO_TEXTO`). A leitura continua livre (fixture `raiz-forge-python-c-leitura-githooks-libera`).
- **Tamanho (H1):** o delta tem cerca de 45 linhas de código e o item, cerca de 65. Fica dentro do teto e é um comportamento só (o que está em vigor na raiz do Forge).
- **Legibilidade (item 3):** `destino_opaco` reaproveita `valores_da_palavra` e `opaco_sem_resto` do pai, sem duplicar o cálculo. O ramo do erro interno segue o padrão do estado dos hooks, logo acima dele.
- **Guardas e mutantes (item 7):** cada linha de guarda nova ou mudada tem um mutante declarado.
  - `bin/forge-mutante --processos 1` nas três specs `v0481-hook-raiz-forge*`: os 22 morreram (RF1 a RF5, RF7, RF8, RE1 a RE5, RT1, RT2, RD1 a RD6, RX1 e RX2).
  - Spec `v0479-entrega-parecer-mesclado-4.json`, com o M19 realinhado à linha `achado = achado or self.parecer_no_topo(caminho)`: M19 a M24 morreram.
  - Testes afetados (`test_fixtures_da_raiz_do_forge`, `test_fixtures_do_parecer_pelo_papel` e `test_indice_fixtures`): 12 testes OK, rodados sob a trava `trava-teste-a.lock`.
  - As fixtures exercitam o comportamento sem ler a fonte, e o lote afirma os mínimos.
- **Commits (item 9):** `8bd71b5c` (fix) e `10c1b834` (test) seguem Conventional Commits em português e trazem o cartão e a etapa.
- **CI (`gh pr checks 930`, head `10c1b834`):** estão verdes a suíte 3.12 e a 3.14 (partes 1 a 5), `instalação`, `bateria (passos)`, `bateria (verificações longas)`, `teto de pulados` e `árvore já provada na develop`. Ficam de fora só `bateria`, `bateria (pareceres)` e `catraca`, que esperam o parecer ou o rótulo.
- ci: 10c1b834b6fb062bfb2f9b7d9020dbbcbe828abf verde
