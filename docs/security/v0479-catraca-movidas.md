---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-catraca-movidas
commit: 6c1f86913acbbd8185b4dba9c1b7985c5f457f5b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0479-catraca-movidas

Escopo: `tests/catraca.py:862-873` (regra MUTANTES-SPEC-HOOKS passa as saídas por `fm.movidas` antes de filtrar as faltas), o teste novo em `tests/test_catraca.py:920-936` e a spec `tests/mutantes/v0479-catraca-movidas.json`. Pedido v0478, etapa E28.3, base 2904a68a.

## Gatilhos
Gatilhos: controle do CI (catraca, regra de guarda de código de controle)

## Achados

## Sondas

## Detalhe dos achados
Pergunta do brief: um PR consegue apagar uma guarda e fazê-la passar por "movida"? Leitura e sondas (harness `GuardasDosHooks`, em arquivo de teste fora do repo, 21 testes ok):

- **Destino fora do controle** (`docs/y.py`, não é classe C): o destino não entra em `hooks` (`guardas_do_diff`, `tests/catraca.py:835-844`), não gera `coberta`, a apagada segue `apagada` e barra (S1 abaixo).
- **Destino em arquivo de teste**: a spec é inválida (arquivo de teste não se muta) e a apagada barra (S2).
- **Um destino para duas apagadas** (mesmo texto apagado em `hooks/x.py` e `hooks/z.py`, uma coberta em `hooks/y.py`): `movidas` consome o destino (`bin/forge-mutante:670-672`); só uma sai movida, a outra barra (S3).
- **Destino ilegível**: a falha de leitura barra e o arquivo não entra em `por_arquivo`; o alinhamento `zip(lidos, por_arquivo)` se mantém e a apagada barra (S6).
- **Destino só `isenta` ou `só equivalente`**: `movidas` só conta linha `coberta` (`bin/forge-mutante:663`); leitura.
- **Mesmo texto em código morto** (`hooks/y.py` com a condição numa função nunca chamada e mutante declarado): passa (S4). Não é risco novo: tornar a guarda inalcançável sem tocar o texto da condição (um `return` antes do `if`) já passava antes desta mudança (S5), porque a regra compara condições, não alcance; e o mutante no código morto não é morto pelo teste listado quando o QA o executa (a cobertura é "declarado, não provado" em toda condição coberta, não só nas movidas). Mesma semântica do `forge-mutante --cobertura`, que é a fonte única. Sem caminho de ataque marginal; fica como observação, sem achado.
- **Autojulgamento**: o CI roda a catraca e o `bin/forge-mutante` da base (`.github/workflows/catraca.yml:32-46`); o PR não muda o critério que o julga. A base 2904a68a já tem `analisar_com_textos` e `movidas`.

Sondas executadas (nenhuma prova bloqueante, por isso fora do bloco `## Sondas`): S1 destino `docs/y.py` → `apagada · hooks/x.py:2(base)`; S2 destino `tests/test_y.py` → spec inválida + apagada; S3 duas apagadas, um destino → uma `apagada · hooks/z.py:2(base)`; S4 código morto → `[]`; S5 `return` antes do `if`, sem spec → `[]`; S6 destino com erro de sintaxe → "não consegui analisar" + apagada.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira não rodada localmente (fica com o CI do PR); rodados só os testes de `GuardasDosHooks` e as sondas acima. Sem segredo no diff (leitura; o diff tem 4 arquivos de código, teste, spec e fragmento de changelog).
