---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-comando-pronto
commit: 4b75cbd1359d2af46c95a40a546cb453f4cf4b1f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-comando-pronto, revalidação (v0478 E66.9)

Volta por delta sobre o parecer aprovado no `34b6bf7b` (rodada anterior no git).

## Gatilhos
Gatilhos: teste que executa as ferramentas da fábrica (`bin/forge-*`) em subprocesso; texto do Jarvis sobre comandos de controle.

## Delta lido
- `forge-check parecer delta`: intervalo `34b6bf7b..925e9671`, sem o que veio da develop; fora do domínio só `tests/test_qa_lote_l09.py`; "nenhum arquivo do domínio mudou".
- `c6984fb3`: merge da `origin/develop` (`c8e8a08d`, já revisada na develop), sem conflito.
- `4b75cbd1`: `tests/test_qa_lote_l09.py`, uma linha: a asserção passa a exigir o comando completo `forge-check brief mensagem --arquivo <brief> --pedido <p>` no texto da skill. Só aperta a cobrança; sem subprocesso, sem I/O novo.
- Já lido e sem mudança desde o `34b6bf7b`: `tests/test_comando_pronto.py`, `bin/forge-testes`, as skills e o fragmento de changelog.

## Detalhe dos achados
Sem achado bloqueante nem recomendado; o parecer anterior não tinha achado pendente.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: só no CI (PR #757, em execução no `925e9671` na hora deste parecer); rodado localmente só `tests.test_qa_lote_l09` (4 testes OK). `gitleaks` ausente no PATH (lacuna); o delta não contém credencial, lido à mão.
