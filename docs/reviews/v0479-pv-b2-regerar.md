---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b2-regerar
commit: 8e4888290286ba9a46948d19583ba90e9fc90363
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E57.52 (PR-VERDE B2, regerador; revalidação)

Revalidação pelo delta (`forge-check parecer delta`): `c5815650..8e488829`, no domínio `bin/forge-testes`, `changelog.d/v0479-pv-b2-regerar.md`, `tests/mutantes/v0479-pv-b2-regerar-3.json` e `tests/test_testes_tocados.py`. O resto do parecer anterior (head c5815650) segue de pé.

## Achados
- A1 (recomendado) bin/forge-testes:1005 · a fotografia agora inclui `.forge/run/` (ignorado), que hooks e outras sessões gravam; uma escrita concorrente durante o `--medir` sai 2 como "escreveu fora da lista". Falha fechada, custa uma volta local; vale nomear o caminho de estado de execução na mensagem.

## Parecer
Aprovado. O delta fecha o A1 da segurança: a fotografia passa a ler o ignorado arquivo a arquivo (`--ignored=traditional` com `--untracked-files=all`) e tira só o bytecode por pathspec (`:(exclude,glob)**/__pycache__/**`, que também casa o `__pycache__` da raiz). O texto de uso e o fragmento do changelog descrevem o mesmo comportamento. Volume medido no checkout principal: 31 ignorados, cerca de 590 KB lidos por fotografia; aceitável.

Teste novo `Regerar.test_escrita_em_caminho_ignorado_sai_2_e_o_bytecode_nao`: cobre o ignorado já existente e o novo (sai 2, sem `regerar rc=`) e o `__pycache__` novo (sai 0). Rodado com ambiente limpo: classe `Regerar` 12/12 OK.

Mutantes (`bin/forge-mutante`, 1 processo, no head 8e488829): G17 e G18 morreram (2/2); `--cobertura --base c5815650` saiu 0. Suíte inteira: fica com o CI do PR (`R-REVIEW`), não rerrodada.

Delta lido: c5815650..8e488829 (4 arquivos no domínio).
