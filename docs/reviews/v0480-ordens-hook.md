---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: c63e96158e67cb61056a5552a12ed7a3f7354925
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E123.4, hook ordens e laço das fixtures do vigia)

Diff `48d6f4b86..c63e9615` (2 commits: `af76641f5` itens 1 a 6, `c63e96158` item 7), conferido contra a emenda "ordens em vigor" da ADR 0003.

## Achados
- A1 (bloqueante) templates/projeto/.forge/ordens-em-vigor.md:1 · o forge-init copia o modelo a todo projeto; o cabeçalho não é vazio e o hook o injeta a cada mensagem (243 bytes sem ordem nenhuma, S1). Contraria a emenda (ausente custa zero; vazio é silêncio). Retire o arquivo do modelo: o Jarvis o cria na 1ª ordem.
- A2 (recomendado) tests/test_hooks.py:891 · o ramo `contexto` do laço das fixtures afrouxa "hook nunca escreve no stdout" para o ordens, e a seção "Afrouxa" da emenda não o lista entre as invariantes que mudam; inclua-o na emenda.
- A3 (recomendado) hooks/ordens.py:58 · a emenda (item 3) e a fixture injeta-no-userpromptsubmit citam `sem_controle`, que junta a sequência de controles num espaço só; aqui cada controle vira um espaço (tab+ESC dá dois). Alinhe o critério ou o texto da emenda.

## Sondas
- S1 · projeto git com `.forge/versao` e só o `.forge/ordens-em-vigor.md` do modelo, `{"hook_event_name":"UserPromptSubmit",...}` em `hooks/ordens.py` · espera: stdout vazio, saída 0 · obtido: linha fixa mais o cabeçalho do modelo (243 bytes), saída 0

## Conferência contra a emenda
- Invariantes listadas e mudadas: `test_hooks_json` (UserPromptSubmit só com `ordens.py`; `ordens.py` permitido no SessionStart), `test_cada_hook_tem_caso_que_passa_e_que_bloqueia` (`ordens` em `{0}`, com sem-forge-versao, erro-interno, teto e arquivo ausente), `test_doutor` linha 608 (único comando no UserPromptSubmit é o `ordens.py`), laço das fixtures do item 7 (`decision`/`reason` só no Stop sem `stop_hook_active`, `fullmatch` do texto fixo, comentário trocado, 4 fixtures novas). `tests/config.json` intocado: nenhum trecho de `invariantes` sai.
- Mudança fora da lista: só o ramo `contexto` (A2). `test_vigia_parado.py` perde só um `import subprocess` sem uso.
- Itens 1 a 6: fonte única e só leitura (`O_NOFOLLOW`, `O_NONBLOCK`, regular, 64 KiB, base por `realpath`), texto puro com linha fixa, teto 15/2000 com aviso, saída sempre 0 com erro ao `erros.log`, sem git nem rede, dono único `jarvis` nos dois caminhos do `conformidade.json`. Matchers `startup|resume|compact` e UserPromptSubmit sem matcher.
- Guardas: 14 mutantes declarados (8 + 6) cobrem cada guarda de `hooks/ordens.py`, cada um com teste de comportamento do ramo de falha; não os rerrodei (V2, do autor).
- Commits: os 2 do Entregar presentes, Conventional Commits, `[afrouxa-regra: ADR 0003 item 1]` no título.

## Provas
- `python3 -s -E -m unittest tests.test_vigia_parado tests.test_doutor tests.test_indice_forge tests.test_hooks.OrdensEmVigor tests.test_hooks.VigiaTimeParadoNasFixtures tests.test_hooks.Hooks.test_hooks_json tests.test_hooks.Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia` (ambiente limpo por `env -i`): `Ran 187 tests in 160.823s OK`; inclui as fixtures de `tests/hooks/ordens` (10) e `tests/hooks/vigia/time-parado-*` (4).
- Suíte inteira: fica no CI do PR (não rerrodada).

## Parecer
Reprovado por A1: o código do hook segue a emenda, mas o modelo de projeto faz todo projeto novo pagar a injeção a cada mensagem sem ordem nenhuma. Correção curta: apagar `templates/projeto/.forge/ordens-em-vigor.md` (ou o hook ignorar linhas de comentário, com mutante e fixture). A2 e A3 são recomendados e viram cartão depois do merge.
