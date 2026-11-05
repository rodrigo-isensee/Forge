---
tipo: review
contrato: 1
pedido: versao-034
branch: melhoria/testes-sem-claude-ancestral
commit: 9a08b1c860fc0c24f47467429018020680ba5811
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: TESTES-SEM-CLAUDE-ANCESTRAL (versao-033)

Escopo: `origin/develop...9a08b1c` (`tests/sem_claude_ancestral.py` novo, `tests/test_atualizar.py`, `tests/test_sugerir.py`, fragmento `changelog.d/`). Teto M14: 84 linhas de código e teste, dentro; um comportamento só. A guarda de produção `dentro_do_claude` (`bin/forge_versoes.py`) não mudou, conforme a DECISÃO TÉCNICA do pedido.

## Verificado na prática
- Os 3 módulos de dentro desta sessão do Claude: `test_sugerir` 37 OK, `test_atualizar` 80 OK, `test_sessao_versao_carregada` 5 OK (rc=0 nos três).
- Mutante manual do lançador (cortar todos os ancestrais, `lambda pid: (0, "")`): o teste novo `Dentro.test_o_lancador_dos_testes_nao_esconde_um_claude_abaixo_do_teste` falha (1 falha, 1 erro); com o original, passa. O teste prova o que diz: o `claude` falso fica entre o pid do teste e o script, sem as variáveis do Claude no ambiente, e a recusa vem da mensagem de `recusar_dentro_do_claude` (única fonte de "fora do Claude" em `bin/`).
- Hook `conformidade` com o lançador chamando `bin/forge-atualizar`, `forge-voltar-versao` (caminho do plugin) e `forge-sugerir --fila`: os três recusados por R-CONFORMIDADE (rc=2), pelo nome do script.
- Sonda temporária em `bin/` (apagada) rodada pelo lançador com `--ate $$` e sem as variáveis do Claude: `dentro_do_claude()` dá False. O lançador esconde o `claude` de quem o chama com um pid escolhido; ver A1.

## Foco do pedido
- Desligar a guarda em produção: o lançador não cria capacidade nova (um `python3 -c` que troca `forge_versoes.dentro_do_claude` faz o mesmo desde antes), nenhum script de `bin/` o lê, e o hook barra o uso com os nomes reais. Mas ele vai no pacote do plugin (`tests/` é publicado) e é uma ferramenta pronta e documentada para isso: A1, recomendado.
- Teste novo: prova (mutante acima).
- Troca passada aos filhos: restrita a `Popen` com lista cujo `args[0]` é o mesmo `sys.executable` e cujo script está na mesma pasta do script lançado; texto de shell e outros programas passam intactos. O único uso real é `forge-atualizar:179` chamando `forge-voltar-versao`, e o `--ate` repassado é o mesmo pid do teste. Correta.

## Achados
- A1 (recomendado) tests/sem_claude_ancestral.py:27 · O lançador vai no plugin e, com --ate no shell do agente e sem as variáveis do Claude, esconde o claude (sonda provou). Sugestão: só aceitar --ate igual ao pai direto rodando unittest, ou citar a A1 ao security-engineer.
- A2 (recomendado) tests/test_atualizar.py:706 · Com o defeito (mutante), o timeout=60 mata só o sh "claude"; o forge-atualizar sob pty.spawn fica órfão esperando a pergunta (achei 3 vivos). Sugestão: start_new_session=True e matar o grupo no timeout.

## Parecer
Aprovado. O conserto fica nos testes, a guarda de produção segue igual, o teste novo pega o mutante que esconderia um `claude` abaixo do teste e a propagação aos filhos é restrita ao mesmo `bin/`. A1 e A2 são endurecimento, não devolvem; A2 só aparece com o defeito presente. Sobre A1: o hook já barra o uso direto pelos nomes, e o desvio por ofuscação existia antes sem o lançador. Segurança tem parecer próprio em paralelo.
