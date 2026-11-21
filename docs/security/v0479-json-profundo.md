---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-json-profundo
commit: fbf2c6f7936daf77344088b10dc39bc31f63a560
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-json-profundo (teto de aninhamento, E44.1)

Escopo: `git diff 004ce869..fbf2c6f7`, 16 arquivos (7 commits). Controle tocado: `hooks/agentes.py` (`ler_estado`), `hooks/_json_raso.py` (novo), `tests/catraca.py` (cópia do teto e `json_raso`), `bin/forge-placar` (`ci_vermelha`). O resto é teste, mutantes, mapa do `forge-testes`, `docs/hooks.md` e fragmento.

Gatilhos: hook de controle (`agentes`, estado ilegível, `R-TETO`), catraca do CI (`R-CONFORMIDADE`, pede `afrouxa-regra` por mudar `tests/catraca.py`), leitura de entrada não confiável (JSON do head do autor).

## Achados

## Sondas

## Detalhe dos achados
Sem achados.

**A mudança só aperta (declaração pedida, `R-CONFORMIDADE`).** Em `tests/catraca.py` nenhuma linha de regra sai: as 8 linhas removidas são as 8 chamadas `json.loads(...)` trocadas por `json_raso(...)` (mesmos argumentos), e entram só `TETO_ANINHAMENTO`, `fundo_demais` e `json_raso` (`tests/catraca.py:98-130`), sem nome colidindo com outro do arquivo. Nenhuma regra, limiar, lista de exceção, dono ou rótulo muda. Cada chamada, acima de 64 níveis, passa a dar `ValueError`, e cada uma segue fechada:
- `json_de` (`tests/catraca.py:136`) devolve `{}`, o mesmo estado que o autor já alcança hoje com um JSON de sintaxe errada; no head, `{}` vira violação: `mudancas_da_politica` acusa cada chave da base (`tests/catraca.py:500`) e `regras_de_config` acusa cada invariante da base (`tests/catraca.py:243-250`). No interpretador antigo, o aninhamento acima de ~9000 dava `RecursionError` fora do `except ValueError` (queda da catraca, também fechada); agora vira violação com mensagem, não liberação.
- `hooks_contados` (`:369`) devolve contagem vazia (hook "removido", barra); `erros_de_forma` (`:419`) devolve "JSON ilegível"; `_specs_do_diff` (`:844`) vira problema.
- Os arquivos de linha de comando (`--mesclados`, `--eventos`, `--execucoes`, `:1943`, `:1998`, `:2009`, `:2014`) não capturam o `ValueError`: a catraca sai com erro, fechada.
- Fora do teto: `:506`/`:508` leem chaves que a própria catraca serializou de dado já conferido, e `:1265` é a resposta da API do GitHub (estrutura do GitHub, sem caminho realista de um autor de PR aninhar ali); ambos documentados no comentário de `tests/catraca.py:93-97`.

No `hooks/agentes.py:415-416`, o teto é uma recusa nova dentro do `try` de `ler_estado`, antes do `json.loads`, e lança `EstadoIlegivel` (recusa com `R-TETO`, como o resto do ilegível); a decodificação dos bytes que falha cai no `except Exception` de `:420` e também vira ilegível. Nada sai do hook além do texto da docstring. No `bin/forge-placar:198-199`, o `--ci` da medida passa a sair com 2 e mensagem fixa em vez de traceback ou de medir em silêncio. Conclusão: a mudança só aperta; nenhum caminho que antes recusava passa a liberar.

**Equivalência do contador com o leitor.** Para JSON válido, `fundo_demais` conta exatamente a profundidade que o leitor constrói: strings delimitadas por `"` com escape de um caractere após `\` (o `\uXXXX` não contém aspas), e só `[`/`{`/`]`/`}` fora de string mudam o nível. Entrada inválida (fechamento antes da abertura, lixo no fim) o leitor recusa de qualquer jeito. Bytes: `json.detect_encoding` + `surrogatepass`, a mesma decodificação do leitor (`hooks/_json_raso.py:79-80`). Custo linear, um passe; o estado tem o teto de 1 MiB antes. A catraca só recebe texto (`ler` usa `text=True`, `read_text`), então a cópia sem o ramo de bytes basta.

Provas lidas e rodadas: `tests/test_json_raso.py` (cópias iguais nos 14 casos, bytes em três codificações), `tests/test_estado_ilegivel.py` (`fechado(65)` e `fechado(5000)` recusados, `fechado(64)` lido) e `tests/test_catraca.py::Hooks::test_json_aninhado_acima_do_teto_e_ilegivel`: 12 testes, OK, no head `fbf2c6f7`. Sonda própria (não prova bloqueante, por isso fora de `## Sondas`): 40000 JSON gerados com profundidade entre 55 e 75, strings com `"`, `\`, `[` e `{` dentro, compactos e indentados, em texto e em UTF-16: `fundo_demais` igual a `profundidade > 64` em todos.

Segredo: 0 ocorrências de token, chave privada ou credencial nas linhas acrescidas do diff.

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. A suíte inteira é do CI do PR; no momento deste parecer não havia execução de CI para a branch, e o merge exige o CI verde. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH; a mudança não toca workflow nem dependência.
