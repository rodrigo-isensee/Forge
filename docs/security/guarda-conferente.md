---
tipo: revisao-seguranca
contrato: 1
pedido: guarda-conferente
branch: melhoria/guarda-conferente
commit: b050d634b5e34cd4844ac80e0e21f3ed98df8906
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: guarda-conferente (M6)

Escopo: `git diff f911dfa0b2ebd9692d45c374f9ff4bab8523ed6b b050d634b5e34cd4844ac80e0e21f3ed98df8906` (`hooks/agentes.py`, `tests/test_guarda_conferente.py`, `changelog.d/guarda-conferente.md`), mais `hooks/hooks.json` (onde o hook entra) e a seção M6 da proposta aq.

**Veredito: aprovado.** A entrega só acrescenta uma recusa (R-BRIEF) antes do lançamento do `forge:conferente`; não remove nem relaxa nenhuma trava existente (R-TETO segue igual) e não muda nada para outros agentes. Ficam duas recomendações de severidade baixa e dois pontos informativos, nenhum bloqueante.

## Gatilhos
Controle do Forge: hook de bloqueio novo no `PreToolUse` de `Agent|Task` (`hooks/hooks.json:5-17` chama `hooks/agentes.py`). Sem segredo, rede, dependência nova nem workflow.

## Modelo de ameaça (resumo)
- **Ativo:** a conferência independente do brief e da entrega (R-BRIEF, R-PROVA) e o custo de tokens de cada rodada.
- **Ator:** o próprio orquestrador da sessão, que monta a mensagem à mão por engano ou para encurtar o caminho. Não há ator externo: o hook lê só o `tool_input` local.
- **STRIDE:** Tampering/Elevation (mensagem fora da forma que passa pela guarda); Denial (recusa falsa de mensagem legítima, que travaria a conferência); efeito colateral em outros agentes (reserva de vaga, duplicado, teto).
- **Defesa em profundidade:** o contorno da guarda não abre caminho novo, porque o conferente continua recusando a mensagem sem forma (`forma: modo ausente`, `aviso: mensagem sem Brief-sha256`) e confere arquivo e hash no disco. A guarda só antecipa a recusa.

## Sondas
Funções tiradas com `git show b050d63:hooks/agentes.py` para um diretório em `$TMPDIR` (Python `-I`), sem tocar o HEAD da worktree; e `python3 -m unittest tests.test_guarda_conferente` na worktree (14 testes, OK).

| Cenário | Resultado | Leitura |
|---|---|---|
| Cabeçalho correto, Arquivo relativo e absoluto, vários blocos, CRLF | passa | conforme E1 |
| `Modo: brief`, espaço antes de `modo:`, BOM, linha antes do modo | recusa | mais estrito que o conferente; seguro |
| Hash em maiúsculas, 63 ou 65 hex, não hex | recusa | `(?![0-9A-Za-z])` fecha o 65 |
| `Arquivo:` e `Brief-sha256:` só dentro do corpo do brief | passa | só forma (decisão do dono); o conferente pega |
| `Arquivo: /tmp/xdocs/briefs/a` | passa | só forma; o conferente confere o caminho |
| Caminho absoluto com espaço (`.../Usuário Padrão/.../docs/briefs/x.md`) | **recusa** | ver R1 |
| `prompt` ausente ou não texto | recusa | `str(prompt or "")` não levanta exceção |
| Linha de 2 MB e 200 mil linhas `Arquivo:` | 0,04 s e 0,08 s | sem ReDoS; o regex é ancorado por linha |
| Outro `subagent_type` sem cabeçalho | passa | sem efeito em outros agentes |

Leitura do fluxo: a recusa (`hooks/agentes.py:124-127`) roda antes do duplicado, da carga e do teto e antes do `append` da reserva; `bloquear` sai por `SystemExit`, que o `executar` não engole (pega só `Exception`) e que libera a trava ao sair do `with`. Recusa não prende vaga nem grava `agentes.json`.

## Achados

## Detalhe dos achados
- **R1 (recomendado, baixa) `hooks/agentes.py:103`.** `ARQUIVO_DA_MENSAGEM` exige o caminho sem espaço até `docs/briefs/`, e `forge-check brief mensagem` imprime o `Arquivo:` absoluto sem aspas (`bin/forge-check:3287`, `caminho_impresso`). Projeto em pasta com espaço (comum em `/mnt/c/Users/...` no WSL) tem a saída oficial recusada, e a frase da recusa manda reenviar a mesma saída: laço. Sem caminho de ataque (falha fechada, só disponibilidade); contorno existe (Arquivo relativo passa). Correção mínima: aceitar o resto da linha (`^Arquivo:[ \t]*.*docs/briefs/\S`), mais um teste com espaço no caminho. Esforço P. Dono: tech-lead.
- **R2 (recomendado, baixa) `hooks/agentes.py:124`.** A guarda compara `subagent_type` só com `forge:conferente` exato; se a plataforma aceitar o nome sem o prefixo do plugin (o próprio `iniciar`, `hooks/agentes.py:158`, já trata o tipo com e sem prefixo no `SubagentStart`), a chamada `conferente` passa sem a guarda. Impacto: só se perde a economia; o conferente ainda recusa. Correção mínima: comparar `tipo.split(":")[-1] == "conferente"` e cobrir no teste. Esforço P. Dono: tech-lead.
- **I1 (informativo).** `Arquivo:` e `Brief-sha256:` são procurados na mensagem inteira, inclusive dentro do bloco `<<<BRIEF`; é coerente com a decisão do dono (só forma, vários blocos) e o conferente confere o cabeçalho de fato.
- **I2 (informativo).** O hook `agentes` não é crítico (falha aberta, ADR 0003); a função nova não tem caminho de exceção realista, então isso não cria contorno.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas locais em `$TMPDIR` e o teste novo. Fora do PATH: `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner`, `trivy` (lacuna; a entrega não toca dependência, workflow nem segredo).
