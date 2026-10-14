---
tipo: review
contrato: 1
pedido: f1-lote4-custo
branch: melhoria/f1-lote4-custo
commit: bcde5d4
parecer: aprovado
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
