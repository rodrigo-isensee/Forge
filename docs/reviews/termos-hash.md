---
tipo: review
contrato: 1
pedido: termos-hash
branch: melhoria/termos-hash
commit: 6a79fef
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review: termos proibidos guardados só como hash (ADR 0008)

Escopo: `tests/config.json`, `tests/neutralidade.py`, `tests/test_forge.py`, `tests/catraca.py`, `tests/test_catraca.py`, docs e `CHANGELOG.md`, diff `origin/develop..a213b8e`. Nenhum termo é citado aqui; a lista antiga é tratada por "termo nº N".

## Verificações feitas
- **Equivalência com as regex antigas.** As 8 regex de `origin/develop` foram confrontadas com as 11 entradas novas: `entradas_da_regex` cobre as 8 por inteiro (palavra, trecho, classe expandida e par) e todas as entradas esperadas existem na config. Executei o detector novo e as regex antigas (`re.I`) nos 448 arquivos versionados: nenhuma divergência.
- **Normalização.** Minúsculas e sem acento via NFKD; casa mais do que `re.I` (acentuado e variante de compatibilidade), nunca menos.
- **Janelas e limites.** `palavra` equivale a `\b..\b` (tokens `\w+`, mesmo conceito de `\b`); `trecho` varre as janelas de tamanho `n` em cada token; `par` exige exatamente um espaço entre tokens, equivalente a ` ?` mais o caso sem espaço, coberto pela entrada `trecho` gêmea. Testado em `test_detector_por_hash`.
- **Nenhum caminho imprime o termo.** Teste de neutralidade mostra só conjunto de sha256; a catraca mostra índice e 8 hex. O teste de catraca confere que o texto não aparece.
- **Catraca.** Remover ou alterar (tipo, `n`, sha) de entrada de hash barra; acréscimo passa. Transição claro para hash só passa com cobertura total; regex complexa e cobertura parcial barram (testes cobrem palavra, par, classe e incompleta).
- **Desempenho.** Varredura dos 448 arquivos em cerca de 0,55 s; `tests.test_catraca` (73 testes) em 6 s. Sem preocupação.

## Achados
### Bloqueia
Nenhum.

### Recomendado
1. `tests/catraca.py:PROTEGIDOS`: `tests/neutralidade.py` não está na lista de arquivos protegidos. Enfraquecer `normalizar` ou `termos_achados` (por exemplo, não normalizar, ou ignorar `par`) reduziria a detecção sem a catraca perceber; só `test_detector_por_hash` o protege, e ele pode ser editado junto. Sugestão: incluir `tests/neutralidade.py` em `PROTEGIDOS`.
2. Limite do método, a registrar na ADR 0008 ou em `R-NEUTRO.md`: hash sem sal de termo curto (3 letras) e o campo `n` (tamanho) são recuperáveis por força bruta. O ganho é não expor o nome em claro e não imprimi-lo, não segredo criptográfico. Texto de uma frase basta.

### Observação
- `entradas_da_regex` só entende o formato da lista antiga; regra nova fora dele barra na transição por desenho. Aceitável, pois a transição é única.

## Parecer
Aprovado. A detecção por hash é equivalente à das regex e não ficou mais fraca; os itens recomendados podem entrar neste PR ou em seguida, a critério do autor.

## Revalidação (6a79fef)

Escopo: `503830f..6a79fef` (commits `a9c0d45`..`6a79fef` do autor): `tests/neutralidade.py` incluído em `PROTEGIDOS` (`tests/catraca.py`), teste `test_detector_de_neutralidade_e_protegido`, e a frase da ADR 0008, seção 5, com o limite do hash. Suíte: 190 testes verdes. Parecer: **aprovado**.

| Achado | Situação | Evidência |
|---|---|---|
| Recomendado 1: `tests/neutralidade.py` fora de `PROTEGIDOS` | corrigido | `PROTEGIDOS` inclui `tests/neutralidade.py`; o teste novo troca `normalizar` sem rótulo e espera `R-CONFORMIDADE` com `mudança em tests/neutralidade.py`; contra o `tests/catraca.py` de `503830f` o teste falha (cobertura real, não só verde) |
| Recomendado 2: limite do hash (termo curto e `n`) | corrigido | ADR 0008, seção 5, item (a): força bruta sobre hash sem sal de termo curto e sobre `n` (tamanho em caracteres, ou par de tamanhos), declarado como proteção contra leitura casual, com o histórico condicionado ao item (b). Conferido em `tests/config.json`: `n` é o tamanho, então a descrição está certa |
| Observação: regra nova fora do formato antigo barra na transição | mantida | aceitável, como antes |

### Verificações
- Nenhum termo novo em claro: a frase da ADR e a entrada do CHANGELOG falam em "termo curto" e no campo `n`, sem citar nenhum termo.
- Editar `tests/neutralidade.py` sem o rótulo e a ADR barra com `R-CONFORMIDADE`; o teste confere a mensagem.
- Sem alteração de detecção: o diff não toca `tests/neutralidade.py` nem `tests/config.json`.

### Pendências (não bloqueiam)
- Nada novo. O CHANGELOG segue com a entrada no bloco de catraca, antes de "Pendências registradas".
