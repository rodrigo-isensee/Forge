---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-dir28-sandbox
commit: 4568c9b7276e6aa2edcbb4818e7ef09c08253aeb
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 E151.4 (PR #847, diretriz 28 no Jarvis)

Diff lido: `e15c8566..4568c9b7` (5 arquivos: `agents/jarvis.md`, `skills/falar-com-o-dono/nao-trava.md`, `tests/fixtures/diretrizes-do-dono.json`, `tests/test_jarvis_nucleo.py`, fragmento de changelog).

## Gatilhos
Gatilhos: texto de agente sobre controle de execução (sandbox do Bash, modo de permissão).

## Veredito por mudança: só aperta ou neutro
- `agents/jarvis.md:17` (aperta): o Jarvis passa a conferir o sandbox no primeiro comando e, se falhar, **para** e dá ao dono o comando de reabrir. Antes a regra só estava no modelo de projeto (`templates/projeto/CLAUDE.md:11`); o Forge e projetos com `CLAUDE.md` antigo seguiam sem ela. Falha de sandbox deixa de ser caminho para continuar sem isolamento.
- `skills/falar-com-o-dono/nao-trava.md:13-17` (aperta): o detalhe manda reabrir com `jarvis` ou `claude --agent forge:jarvis --permission-mode auto`, o mesmo que `scripts/jarvis:49` e `scripts/jarvis-forge:232` já usam; diz que o dono nunca aprova comando a comando nem escolhe "sempre permitir". Não ensina contornar o sandbox: não cita desligar o sandbox, executar fora dele, `--dangerously-skip-permissions` nem regra de permissão ampla; o erro citado (`uid_map`) é só o sinal para parar.
- `agents/jarvis.md:17` (neutro): o resumo de "vários projetos" perdeu os exemplos de prefixo; o detalhe segue em `skills/falar-com-o-dono/varios-projetos.md:11,17` e a linha manda lê-lo. `agents/jarvis.md:26` (neutro): encurta a menção ao conteúdo de `fluxo-do-pedido`, sem regra a menos.
- `tests/test_jarvis_nucleo.py` e a fixture (aperta): a diretriz 28 vira de fábrica com trecho protegido e o teto de pendentes desce de 8 para 7; o teste `SandboxNoPrimeiroComando` prende a regra no Jarvis e as frases de "não aprova comando a comando" e do modo automático na skill.

## Achados

## Sondas

## Detalhe dos achados
Sem achado. Teste do arquivo tocado: `python3 -m unittest tests.test_jarvis_nucleo` → 45 testes, OK (local, no head 4568c9b7). A suíte inteira é do CI do PR #847.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática do texto; nenhuma ferramenta de varredura se aplica a um diff só de texto e teste.
