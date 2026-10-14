---
tipo: review
contrato: 1
pedido: f1-lote4-custo
branch: melhoria/f1-lote4-custo
commit: 6051057
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Parecer de autor: lote 4 da fonte F1 (custo de tokens lido das transcrições locais)

Escopo: `bin/forge-check` (subcomando `transcricao custo`), `tests/test_forge.py` (classe `CustoDeTokens`), fixtures sintéticas em `tests/transcricoes/uso/`, `docs/transcricoes.md`, `docs/melhoria-continua.md`, `agents/jarvis.md`, `agents/agile-coach.md` e `CHANGELOG.md`.

## Verificações feitas
- **Vermelho antes do verde.** Os 11 testes foram escritos antes do código; sem a mudança, 10 falharam (o 11º, caminho inexistente, passa por acaso por o argparse recusar o subcomando).
- **Sem custo (`R-CUSTO`).** Só disco local, biblioteca padrão, sem rede nem IA.
- **Anonimização.** A saída traz só números, tipo de agente (`forge:*`; o resto vira `<agente>`), modelo validado por regex, hash de 8 hex e `sN`. Teste confere que prompt, caminho e nome de sessão não aparecem. O anúncio vai ao stderr e traz o caminho que o próprio usuário passou.
- **Duplicata de streaming.** Mensagens com o mesmo `message.id` e `requestId` contam uma vez; lançamento de subagente deduplicado por `tool_use.id`.
- **Neutralidade (`R-NEUTRO`).** Fixtures sem nome de projeto nem dado real.
- **Suíte.** `python3 -m unittest discover -s tests`: 321 testes, verdes; `scripts/validar-plugin.sh` passa.

## Limites e riscos
- O formato do `.jsonl` do Claude Code não é contrato público; campos ausentes dão número parcial, sem erro. O leitor novo (`ler_uso`) é separado de `ler_eventos_brutos` para não tocar a verificação de conformidade.
- `tokens_antes` é o contexto comprimido (`preTokens`), não o custo do resumo; o resumo aparece como mensagem da sessão principal.
- Sem sessões de exemplo reais anonimizadas: os campos de subagentes em arquivos separados (`subagents/*.jsonl`) foram tratados pelo `agentId`/`agentType`, a confirmar.
- Mexe em `bin/forge-check` (protegido): o PR pede o rótulo `afrouxa-regra` do dono.

## Review independente
Parecer: **ajustes necessários** (commit revisado 85ece09).

### O que confere
- **Privacidade.** A saída (e as linhas de `--entregas`) traz só `sN`, tipo `forge:*` ou `<agente>`, modelo validado por regex, hash de 8 hex e números. Nenhum texto, caminho ou prompt. O anúncio no stderr repete só o caminho que o usuário passou.
- **Dados reais, só local.** Rodado contra as transcrições desta máquina (1 sessão, 254 arquivos `.jsonl`, 253 deles em `subagents/`, cerca de 97 MB). O formato real dos subagentes funciona: `isSidechain` e `agentId` presentes em todas as mensagens de subagente, ligados ao tipo pelo `tool_result`. Conferência independente com script próprio: 3742 pares `(message.id, requestId)` únicos de subagente contra 3740 mensagens contadas (diferença desprezível); principal + subagentes = total; ordem de grandeza coerente (centenas de milhões de tokens, quase tudo cache de leitura; subagentes cerca de 28% do total). Tempo de 1 s. Nada da saída foi colado aqui.
- **`R-CUSTO` e `R-NEUTRO`.** Só disco local, biblioteca padrão, sem rede; fixtures sintéticas.
- **Bateria local.** 321 testes verdes; `scripts/validar-plugin.sh` passa; catraca `pareceres` e `pr-texto` sem violação; catraca `regras` só reclama de `bin/forge-check` sem o rótulo `afrouxa-regra` (esperado, é do dono); versão inalterada e linha nova em `[Não publicado]`.

### Ajustes
1. **bloqueia** · `bin/forge-check` `cmd_transcricao_custo`/`ler_uso` · arquivo ilegível (`PermissionError`) termina em traceback, ao contrário de `verificar`/`anonimizar`, que tratam `OSError`. Capturar `OSError` ao ler e devolver `custo: arquivo: <erro>` com código 1 (sem o caminho na mensagem, só o `strerror`, ou só o que o usuário passou).
2. **bloqueia** · `ler_uso` · linha malformada e formato desconhecido são ignorados em silêncio: um arquivo de lixo ou sem nenhum `usage` imprime zeros com código 0, indistinguível de uma sessão sem custo. Contar linhas inválidas e mensagens sem `usage` válido e avisar (`custo: aviso: N linhas ignoradas`, e aviso quando nenhuma mensagem com `usage` for encontrada; sair com 1 nesse último caso). Teste para os dois.
3. **recomendado** · `ler_uso` · guarda todos os objetos de todos os arquivos em `objs` (duas passadas): 274 MB de memória para 97 MB de entrada, linear. Para pastas de GB estoura. Processar em streaming (guardar só `tool_use`/`usage` relevantes) ou documentar o limite.
4. **recomendado** · `docs/transcricoes.md` · registrar que o formato dos subagentes agora foi confirmado em dados reais (a ressalva do parecer de autor) e os limites acima.

Sem validação local registrada no PR: só se aprova depois dos ajustes 1 e 2.

## Re-review independente
Parecer: **reprovado** (commit revisado 6051057). Os dois bloqueios do review anterior e os recomendados 3 e 4 estão resolvidos; a correção, porém, introduz um teste com pulo que faz a catraca falhar.

### Ajustes do review anterior
1. **Resolvido** · arquivo ilegível. `ler_uso` captura `OSError` na leitura (`bin/forge-check:949-951`); `ruim.jsonl` com `chmod 0` vira `custo: aviso: arquivo ilegivel (Permission denied); pulado`, sem traceback, e o restante é somado (exit 0). Confirmado à mão.
2. **Resolvido** · linhas ignoradas e sem `usage`. `custo: aviso: N linhas ignoradas` em stderr e exit 1 com "nenhuma mensagem com usage encontrada" (`bin/forge-check:1057-1061`). Confirmado à mão com lixo puro (exit 1).
3. **Resolvido** · memória. `ler_uso` lê linha a linha e guarda só as mensagens com `usage` e os `tool_use` de `Agent`/`Task`.
4. **Resolvido** · `docs/transcricoes.md` registra a confirmação do formato dos subagentes e os limites.

### Desvio do dicionário de chaves
Aceitável. A chave continua `(message.id, requestId)` (ou `("#", pos)` sem id), e a atribuição `mensagens[chave] = ...` mantém o "vale a última". Ficou só a posição da primeira ocorrência na ordem do dict, que não afeta somas. O tipo do agente é resolvido no fim (`resolvidas`), então não há dependência de ordem entre arquivos. Ressalva: nenhum teste prova o "vale a última" (ver recomendado C).

### Bloqueio novo
A. **bloqueia** · `tests/test_forge.py:1733` · `@unittest.skipIf(root)` no teste do arquivo ilegível. A catraca (`--modo regras`, por AST) conta pulos: subiram de 0 para 2, violação de R-CONFORMIDADE, e o job `catraca` do CI fica vermelho. Sugestão: remover o decorador e fazer o teste determinístico sem pular (por exemplo, fazer `open` falhar por outro meio que não dependa de ser root, ou testar a leitura de um arquivo que não existe mais entre a listagem e a leitura). Não usar `skipTest` (também conta como pulo).

Observação fora do código: a mesma catraca marca `bin/forge-check` sem o rótulo `afrouxa-regra`. Isso é decisão do dono (R-DECISAO), não correção de código.

### Recomendados
B. **recomendado** · `tests/test_forge.py:1747` · `assertNotIn("ruim", ...)` pode, com probabilidade mínima, casar com o nome aleatório do diretório temporário. Sugestão: afirmar `assertNotIn("ruim.jsonl", saida + erro)`, que é o nome do arquivo que não pode vazar.
C. **recomendado** · `tests/test_forge.py:1665` · a duplicata de streaming da fixture `sessao-a.jsonl` tem o mesmo `usage` nas duas linhas (`output_tokens` 50 e 50), então nada prova "vale a última". Sugestão: duas linhas com mesmo `message.id` e `requestId` e `output_tokens` diferentes; afirmar o último.
D. **recomendado** · `bin/forge-check:933` e `:955` · `ilegiveis` é contado e devolvido, mas ninguém lê (código morto). Remover, ou usar no aviso final.
E. **recomendado** · `bin/forge-check:952` · `tipo_do_agente.get(agente)` vale também para mensagens da sessão principal (`lado` falso). Hoje não muda a saída (`resumir_custo` e `linhas_de_entregas` só usam `tipo` quando `lado`), mas o contrato ficou implícito. Sugestão: resolver o tipo só quando `lado`.
F. **nit** · `bin/forge-check:951` diz "pulado", mas um arquivo com erro no meio da leitura já somou as linhas lidas antes do erro. Sugestão: "lido até o erro" ou, mais simples, aceitar e documentar. Também `1 linhas ignoradas` (plural): "1 linha".

### Bateria local no 6051057
- `python3 -m unittest discover -s tests`: 324 testes, OK (53 s).
- `scripts/validar-plugin.sh`: exit 0, "Validation passed".
- `tests/catraca.py --modo regras --base b5e5d3d` (base = `develop`): exit 1. Duas violações: o `skipIf` (bloqueio A) e `bin/forge-check` sem `afrouxa-regra` (dono).
- `tests/catraca.py --modo pareceres --base b5e5d3d --head 6051057 --ramo melhoria/f1-lote4-custo --base-ref develop --autor <autor> --pr 113`: exit 1, porque o último parecer deste arquivo é reprovado. Passa só com parecer aprovado no commit revisado.
- `tests/catraca.py --modo pr-texto` (corpo do PR via `gh`): exit 0.
- Versão e changelog: `plugin.json` continua em 0.12.0; uma linha nova em `[Não publicado]` (ok).

### Próximo passo
Autor corrige A (e, se quiser, B a E), faz push e pede novo re-review. Não há validação local registrada no PR: só se aprova depois de A.
