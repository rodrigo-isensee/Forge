---
tipo: review
contrato: 1
pedido: hist-voltas-esperas
branch: melhoria/hist-voltas-esperas
commit: d623eaf3234393d585d3212b0364a9da9f5f2be9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: hist-voltas-esperas

## Achados
- A1 (recomendado) bin/forge-check:5184 · `--kanban` sem `--pedido` é aceito e ignorado em silêncio; vale recusar ou avisar (não devolve)

## Parecer
Aprovado. Diff de 75 linhas de código e teste (teto M14: 400), sem mexer em `hooks/` nem em `PROTEGIDOS`.
- Casamento por motivo: `cita_o_pedido` exige palavra inteira (sem letra, dígito, `_` ou `-` colado, nem `.` antes; ponto final de frase não cola). Conferido com sondas: `ped-d.`, `(ped-d)`, `ped-d, x` casam; `x.ped-d`, `ped-dx`, `ped-d-2`, `ped-d.md` não. A chave de `motivos` é o nome em minúscula, igual ao `casefold()` de `cartoes_do_pedido`; `m[3]` é o motivo na tupla (hora, de, para, motivo).
- Coluna Pedido: `cartoes_do_quadro(raiz, kanban)` troca a leitura pelo arquivo dado e mantém raiz e cópia principal sem `--kanban`.
- Saída `cartoes:` impressa depois do filtro, com `sem_controle`; rc 1 e a mensagem nova cobrem pedido sem cartão.
- Argumentos opcionais de `cartoes_do_pedido`: a chamada de `janela_do_pedido` (bin/forge-check:3435) segue sem eles e `voltas` mantém o comportamento anterior.
- `agents/jarvis.md`: a frase nova (movimento `volta <n>` e `Aguardando o dono` na ida e na volta) está no ponto que já manda registrar as esperas, sem afrouxar regra.
- Testes: `tests.test_medidas_m14b` 33 OK; os cinco casos novos cobrem soma, `--kanban`, motivo, palavra inteira e caso sem casamento; mutantes H1 a H7 declarados em `tests/mutantes/hist-voltas-esperas.json`. Suíte completa do pre-push (2186, rc 0) é do autor, conforme decisão técnica do Jarvis.
- Fragmento `changelog.d/hist-voltas-esperas.md` presente; neutralidade e custo sem achado. Sem achado de segurança (leitura apenas). Classe de achado sem repetição, sem linha AR.

## Revalidação (volta 1, por delta)
- `forge-check delta --parecer` sobre o parecer anterior (27f86b6..d623eaf) lista só `tests/mutantes/hist-voltas-esperas.json:74-83` (mutante H8) e `tests/test_medidas_m14b.py:147-151` (teste do id colado atrás); lidos. Já lido, sem mudança: `bin/forge-check`, `agents/jarvis.md`, changelog e demais testes.
- Teste novo cobre `xped-d`, `1ped-d`, `a.ped-d` e `x-ped-d` (rc 1); o `de` do H8 existe literal em `bin/forge-check:3407`. `bin/forge-mutante`: H1 a H8 todos `morreu`. `tests.test_medidas_m14b.Esperas`: 10 OK. Delta só de teste e spec (10+5 linhas), sem regressão do aprovado; o bloqueante A1 do QA (id colado atrás sem mutante) está fechado do lado do review.
- A1 recomendado segue aberto, não devolve. Sem repetição de classe, sem linha AR.
