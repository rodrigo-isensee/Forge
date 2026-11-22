---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-meta-notas
commit: e31f2416990cc6ed223b76584141805061eea624
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E109.8, revalidação da volta do A1)

Revalidação por delta (`R-REVIEW`, H3) da rodada anterior (parecer no head 064e58ce, no git).

Gatilhos: hook (`hooks/meta.py`, Stop) que lê o transcrito e grava `.forge/run/notas.json`.

## Delta lido
`forge-check parecer delta docs/security/v0480-meta-notas.md`, intervalo 064e58ce..e31f2416: no domínio só `hooks/meta.py` (gravação da marca em `try/except OSError` com `hook.registrar_erro`). Fora do domínio: `changelog.d/v0480-meta-notas.md`, `tests/test_meta.py`, `tests/mutantes/v0478-meta-notas-3.json`. Conferido também `Hook.registrar_erro` (`hooks/_comum.py:2737-2757`): grava tipo e mensagem do erro (até 300 caracteres, o caminho local, sem texto de nota) e engole a própria falha.

## Achados anteriores
- A1 (recomendado) corrigido em `hooks/meta.py:323-326`: falha ao gravar `notas.json` vai ao `erros.log` e a contagem segue, então a linha de `mensagens.jsonl` é gravada. Sonda S1 da rodada anterior repetida pelo teste `test_marca_que_nao_grava_nao_perde_a_linha_da_medida` (`tests/test_meta.py:448-452`, notas.json como pasta): linha `(1, True)` gravada e `[IsADirectoryError]` registrado. A sobra `notas.json.<pid>.tmp` quando o `os.replace` falha é a mesma da rodada anterior (sai na próxima gravação do mesmo pid), sem ganho para atacante.

Nenhum achado novo no delta.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodado: `python3 -m unittest tests.test_meta` (50 testes, OK) e o teste novo isolado (OK). Suíte inteira: fica para o CI do PR (por brief; sem PR). `gitleaks` e `semgrep` não estão no PATH: lacuna registrada.
