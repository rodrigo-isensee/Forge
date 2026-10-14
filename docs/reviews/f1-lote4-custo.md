---
tipo: review
contrato: 1
pedido: f1-lote4-custo
branch: melhoria/f1-lote4-custo
commit: 85ece09
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
