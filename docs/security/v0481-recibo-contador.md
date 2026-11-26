---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-recibo-contador
commit: 15759fded5e6f6a78cd9992ef0e62098eaded9fa
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (#921, ordens_teto), volta 1 por delta (E20.21)

Delta lido: `forge-check parecer delta docs/security/v0481-recibo-contador.md` (bc9b1d1f..15759fde; desde o parecer a1b62cab). No domínio: `hooks/ordens_teto.py`, a emenda da ADR 0003 item 3 e `bin/forge-testes`. Fora do domínio, lido só para fechar A1 e A4: `tests/mutantes/v0481-recibo-contador-2.json` (M16) e `tests/test_hook_ordens_teto.py`. A 1ª rodada fica no git (a1b62cab).

## Gatilhos
Gatilhos: hook de controle no PreToolUse (Write, Edit, MultiEdit), emenda da ADR 0003 item 3, arquivo que vira contexto da sessão principal

## Achados anteriores
- A1 (bloqueante) corrigido: o mutante M16 da guarda `__main__` está em `tests/mutantes/v0481-recibo-contador-2.json:76`; catraca verde no head (run 45891172795).
- A2 (recomendado) corrigido: `hooks/ordens_teto.py:41-42` devolve o `new_string` quando o trecho é vazio e o texto é vazio, e `:54` trata o arquivo ausente (`lexists` falso) como texto vazio; o arquivo vazio já chega como "" de `ler_ordens`. Teste: `Criacao` (ausente, vazio e MultiEdit que cria e soma as trocas seguintes), recusa a 16 e passa a 15.
- A3 (recomendado) corrigido: `hooks/ordens_teto.py:69-76,89`, `nao_cresce` deixa passar quando linhas e caracteres não crescem frente ao arquivo atual. Teste: `AcimaDoTeto` (encurta passa, cresce recusa, mesmas linhas com mais caracteres recusa, mais linhas com menos caracteres recusa, Write que encurta passa).
- A4 (recomendado) corrigido: `NoForge` monta clone com o manifesto do Forge e casa temporária com `~/.forge-contrib/docs/ordens/`; 16 recusa, 15 passa, e o arquivo de projeto dentro do clone não é fonte.

## O que aperta, o neutro e o que afrouxa
- **Aperta:** a criação pelo Edit (trecho vazio em arquivo ausente ou vazio), inclusive o 1.º item do MultiEdit, agora conta e recusa acima do teto (A2); antes passava calada.
- **Neutro:** `bin/forge-testes` só põe `test_hook_ordens_teto` no mapa `FORGE_CHECK`; o trecho vazio sobre texto não vazio continua passando (a ferramenta falha sozinha); arquivo ilegível, link para fora da base ou acima de 64 KiB seguem sem conta, como na 1ª rodada; `tamanho` só fatora a conta de caracteres da mensagem.
- **Afrouxa (deliberado, pedido no A3):** com o arquivo já acima do teto, a gravação que não cresce linhas nem caracteres passa, onde antes recusava. Não abre furo: se o arquivo atual está no teto (até 15 linhas e 2000 caracteres), todo texto acima do teto cresce em ao menos uma das duas contas, então `nao_cresce` dá falso e a recusa vale; acima do teto só se chega por fora das ferramentas (o editor do dono ou o Bash, que o `conformidade` reserva ao Jarvis), e a sequência de gravações que passam é monótona, nunca cresce. O `ordens` segue cortando com o aviso até caber. A emenda da ADR descreve as duas mudanças e não tira texto.

## Verificação
Testes: `python3 -m unittest tests.test_hook_ordens_teto` no clone do head 15759fde, 23 testes, OK (casos de abuso de A2, A3 e A4 inclusos). Suíte inteira: CI do head 15759fde (run 45891106581) com as 10 partes da suíte, passos, verificações longas, instalação, teto de pulados e catraca verdes; `bateria (pareceres)` e o agregador `bateria` vermelhos só pela falta dos pareceres ("pareceres: failure", o resto success), que não conta contra o autor.

Limite sem achado (proporcionalidade): link simbólico pendurado dentro da base faz `lexists` verdadeiro e `ler_ordens` None, e o Edit passa sem conta; criar o link exige o Bash na pasta das ordens, só do Jarvis, como o link duro da 1ª rodada.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática do delta e o teste do hook. Faltaram no ambiente (lacuna, nada instalado): gitleaks, semgrep, zizmor, actionlint e osv-scanner; o delta não traz segredo, dependência nem workflow.
