---
tipo: review
contrato: 1
pedido: hist-voltas-esperas
branch: melhoria/hist-voltas-esperas
commit: 27f86b680d95cf26083be9515bfdef20c47048ef
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
