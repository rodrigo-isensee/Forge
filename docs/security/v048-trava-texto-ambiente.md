---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-trava-texto-ambiente
commit: 2ba3d2d0a724d5e0a1903968a1982ed0177f24bb
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v048-trava-texto-ambiente (#949, TRAVA-TEXTO-LIMITE-AMBIENTE)

1ª rodada completa (E1.4), classe C (teste de controle). Delta lido desde a base `b3dfe154`: `tests/test_pre_push_trava.py` (+8/-2), `tests/mutantes/v048-trava-texto-ambiente.json` (novo), `changelog.d/v048-trava-texto-ambiente.md` (novo). Nenhuma linha de `.githooks/pre-push` mudou.

## Gatilhos
Gatilhos: controle do Forge (teste da guarda C-14 do hook pre-push: texto de arquivo de outro processo levado ao terminal)

## Achados

## Sondas

## Detalhe dos achados
Sem achado. O que foi conferido:

- **O teste não afrouxou a guarda.** Os três asserts do `--status` (sem ESC, sem BEL, até 320) ficaram intactos (`tests/test_pre_push_trava.py:609-611`); o da fila mantém o limite de 600 e a ausência de ESC (`:615-616`). A trava ficou mais dura: o espaço depois do BEL faz o segundo campo lido por `mostrar_fila` (`.githooks/pre-push:501`) ser `[2J` seguido de ~190 `A`, o que exercita o corte `${pid:0:12}` (`:506`) que antes não tinha cobertura.
- **O regex não abre saída sem limite.** `AVISO_DE_LOCALE` (`tests/test_pre_push_trava.py:26`) só remove linha inteira que contém `: line <n>: warning: setlocale: `; `.` não casa `\n`, então não atravessa linhas. O texto da trava chega ao stderr filtrado por `tr -cd '[:print:]'` (`.githooks/pre-push:60`), sem quebra de linha, dentro de uma linha que começa com `pre-push: fila`, e o conteúdo gravado pelo teste não traz o marcador: nenhuma linha com texto da trava casa o regex. Para um mutante esconder o vazamento, o hook teria de escrever o texto da trava na mesma linha de um aviso de locale do bash, o que não é caminho realista.
- **Mutantes mortos** (rodados nesta cópia, um por vez, com o hook restaurado depois): M1 (sem `tr`) falha no `assertNotIn("\x1b")`; M2 (`head -c 2000000`) falha com 1048686 > 320; M3 (`${pid}` sem corte) falha com 666 > 600, o assert novo da fila.
- **Formato do aviso conferido:** `LANG=pt_BR.UTF-8 bash -c 'f(){ local LC_COLLATE=C; }; f'` escreve `bash: line 1: warning: setlocale: LC_COLLATE: cannot change locale (pt_BR.UTF-8): ...`, que o regex casa e remove sem tocar a linha seguinte.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: CI do head `2ba3d2d0` todo verde (`gh pr checks 949`, rc=0, incluindo a instalação de ponta a ponta). Teste afetado rodado localmente: OK em 1,9 s. Ferramentas de varredura de segredos, de workflows e de SAST não estão no PATH desta estação (lacuna registrada; o delta é só teste e JSON, sem segredo nem workflow).
