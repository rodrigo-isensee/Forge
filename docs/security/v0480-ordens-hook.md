---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: a6e0d1014e2643e21e1b261154a1ce9160c87662
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E140.8, delta do #805 depois do merge da develop)

Revalidação por delta (`forge-check parecer delta`, intervalo 35211762..a6e0d101, sem o que veio da base 216413c9). No domínio: `hooks/conformidade.py` e `tests/test_hooks.py`. Fora do domínio: `docs/indice-forge.md` e `tests/mutantes/v0480-ordens-hook-3.json` a `-6.json` (os mutantes da guarda saíram com ela para a develop, `-6` renomeado para `v0480-ordens-guarda-2.json`). A rodada anterior (no head 35211762) fica no git.

Gatilhos: hook novo que injeta contexto na sessão principal (`ordens`) e hook de controle (`conformidade`).

**Lido no delta:** `git diff 216413c9 a6e0d101 -- hooks/conformidade.py hooks/_comum.py` vazio: o `conformidade` do PR é byte a byte o da develop. A única linha que muda nele desde 35211762 (`hooks/conformidade.py:1612`, o filtro `em_qualquer_lugar` antes de ler a cópia principal) veio do #814 pela develop, com o parecer próprio (`docs/security/v0480-develop-verde-ordens.md`, commit 6ce3a41a); a guarda das ordens veio do #811 (`docs/security/v0480-ordens-guarda.md`, commit 9e460e4f). Em `tests/test_hooks.py`, a do PR é só o comentário da linha 1791 (o nome novo do arquivo de mutantes); a classe `GuardaDasOrdens` vem da develop. `hooks/ordens.py` e `hooks/hooks.json` não mudam desde 35211762.

**Só aperta, por escrito (corte 2 sozinho, regra do dono até 27/11):** no controle de bloqueio, o corte 2 só aperta ou é neutro: não muda nenhuma guarda (o `conformidade` é o da develop), e o `ordens.py` sai sempre com 0 e não decide nada, então nenhuma entrada antes recusada passa a ser aceita. A proteção do arquivo que ele lê já está na develop: `.forge/ordens/` só do jarvis (`hooks/conformidade.json:66`), casada também relativa à cópia principal (`PELA_COPIA_PRINCIPAL`, `hooks/conformidade.py:3823`), e `~/.forge-contrib/docs/ordens/` no controle (`hooks/conformidade.py:3826` e `:3829`). Portanto, sozinho sobre a develop, o corte 2 não abre fonte sem dono. **Não é "só aperta" na regra normativa:** o corte 2 afrouxa o item 1 da ADR 0003 (um hook passa a injetar contexto no `SessionStart` e no `UserPromptSubmit`), como dizem a emenda e o fragmento do changelog. Esse afrouxamento é o motivo do rótulo `afrouxa-regra`, autorizado para este item pela DECISÃO DO DONO de 2026-11-23 15:25 (Decisão 2, opção 2a), e não pela confirmação de "só aperta".

Estado dos achados anteriores: A1 a A4 seguem resolvidos (o `ordens.py` e a política não mudaram no PR; a parte da guarda está na develop com os pareceres citados). O cartão CONFORMIDADE-CURINGA-PASTA segue aberto, da base, sem relação com este delta.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: `forge-check parecer delta`; `git diff` contra a base e contra 35211762; `python3 -m unittest tests.test_hooks.GuardaDasOrdens tests.test_doutor.HookDoutor` no head: 20 testes, OK; `python3 -m unittest tests.test_hooks.Hooks.test_hooks_json tests.test_hooks.Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia tests.test_hooks.Hooks.test_politica_de_conformidade_malformada_bloqueia`: 3 testes, OK. A suíte inteira não foi rodada (brief: sem suíte local); vale o CI do PR.
