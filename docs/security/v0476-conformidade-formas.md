---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0476-conformidade-formas
commit: eb18768bd45af2addb34c9603b5de85d305837f0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0476-conformidade-formas (v0474 E3.50, parecer E3.96)

Delta revisado: `3d8ad440..eb18768b` (19 arquivos). Foco: `hooks/conformidade.py` e `hooks/_comum.py` (controle, ADR 0011).

## Gatilhos
Gatilhos: hook de controle (`hooks/conformidade.py`, `hooks/_comum.py`), texto do brief que cita a forma aceita (`bin/forge-check`), receita de comando de skill (`skills/esperar-estado/SKILL.md`).

## Achados

## Sondas

## Detalhe dos achados
Nenhum achado. O que foi conferido:

- **Decisão do hook inalterada.** No `hooks/conformidade.py` só mudam textos de recusa: `forma_aceita` (`hooks/conformidade.py:811`) é função pura que escolhe a mensagem pelo `achado`; `nao_modelada` (`:1886`) chama `barrar` nas mesmas condições de antes; em `gramatica_de_leitura` (`:1891`) o contorno passa a ser montado antes do `if sinal is not None`, mas o `barrar` segue dentro dele, sem novo retorno nem desvio; a recusa de aspas sem par (`:1807`) só troca o texto. No `hooks/_comum.py:675` entra a constante de texto `FORMA_DO_HEREDOC`; `HEREDOC_MODELADO`, `CASE`, a gramática do item 1 e a lista do item 2 da ADR 0011 não mudam. `hooks/conformidade.json` idêntico à base.
- **Nenhuma liberação nova (prova diferencial).** As 10 fixtures `tests/hooks/conformidade/e350-*.json` rodadas contra os hooks da base `3d8ad440` (cópia da árvore do head com `hooks/` da base): as 5 de `libera` saem rc 0 também na base (já passavam) e as 5 de `bloqueia` saem rc 2 na base, falhando só na asserção do texto novo da mensagem. No head, as 10 passam. Logo o delta não converte recusa em liberação: nada mais frouxo que a ADR 0011.
- **Conteúdo das mensagens.** As formas oferecidas (valor literal no lugar da variável; `$` só entre aspas simples; heredoc com delimitador entre aspas, sem `-`) estão dentro do que a ADR 0011 já aceita; nenhuma ensina contorno de controle. O texto de `FORMA_DO_HEREDOC` é mais estreito que `HEREDOC_MODELADO` (cita só `EOF`/`FIM` e aspas simples): sem efeito de segurança; precisão de texto, se quiserem, é do `tech-lead`.
- **`bin/forge-check:6544` (`forma_do_heredoc`).** Importa `_comum` de `PLUGIN/hooks` (caminho resolvido a partir do próprio script, não do diretório corrente) e remove a entrada do `sys.path` no `finally`; o módulo só define constantes e funções no topo, sem efeito colateral de import. Sem superfície nova.
- **Skill `esperar-estado`.** A receita nova, com o caminho literal, já passava na base (fixture `e350-laco-do-log-da-skill-com-caminho-literal-libera`); a antiga com `$log` segue recusada com marcador crítico (`e350-laco-do-log-com-variavel-bloqueia`).
- **Mutantes** (`tests/mutantes/pn5-espera-envio.json`, `tests/mutantes/v0476-conformidade-formas.json`): só acompanham o texto novo; não tocam controle.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não conferida aqui (sem execução do CI visível para esta branch no momento da leitura; o CI do PR é o portão do merge). Rodados localmente: `tests.test_hooks.Hooks.test_fixtures_do_e350` no head (OK) e contra os hooks da base (5 falhas, todas de texto de mensagem nas fixtures de recusa). Ferramentas de varredura: não aplicáveis a delta só de texto e de teste; nada instalado.
