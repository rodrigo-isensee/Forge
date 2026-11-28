---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-prazo-unico-estavel
commit: 08e2525e442b1754e2df6e066afb1948d175f422
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E124.2, PrazoUnico determinístico)

Diff revisado (`48d6f4b8..08e2525e`): `tests/test_fechar_checks_do_head.py` (classe `PrazoUnico`) e o fragmento `changelog.d/v0480-prazo-unico-estavel.md`. Nenhum código de `bin/` mudou; não há guarda nova, então não há mutante novo a declarar.

## O teste ficou mais frouxo?
Não. O que muda e o que fica:
- **Antes:** `--espera 1`; o passo 4 lia os checks pela `checks_seq` (1.ª leitura sem a catraca, 2.ª com tudo verde) e gastava o prazo numa volta de 1 s do laço. Sob carga, o passo 4 podia estourar o prazo antes de chegar ao passo 6 (falha "ausente após 1s"), e a asserção só exigia o trecho "o check obrigatório catraca do head", comum às duas mensagens de recusa do passo 6 (terminado fora de success e prazo esgotado).
- **Agora:** `--espera 3`; o `gh` falso dorme 3 s na leitura dos checks e responde tudo verde. O passo 4 passa numa leitura só (`checks_do_head` só confere o prazo com exigido pendente), com `inicio=$SECONDS` antes da leitura; `SECONDS` é inteiro e o sono de 3 s garante `SECONDS - inicio >= 3` no passo 6, sem depender de carga (carga só alonga).
- **Asserções mais fortes:** a mensagem inteira do passo 6 com o sha de 12, `lida: in_progress/-` e `após 3s`; exatamente 1 `gh pr checks` (o passo 4 não relê); exatamente 1 leitura de check-runs (o passo 6 não espera); a linha "checks verdes (exigidos em pass" no stdout (prova que o passo 4 passou); nenhum merge.
- **Mutante VU4** (`falta_e ini=$SECONDS`, prazo recomeçado no passo 6): com prazo novo de 3 s e intervalo 1 s, o passo 6 relê os check-runs, e a contagem 1 e o `após 3s` quebram. Rodado: morreu.
- O falso (checklist 12): o `DORME` entra antes da `LEITURA` com `assertEqual(count, 1)`, a mesma trava do `FecharEsperaCatraca`; a forma do `gh pr checks` continua conferida pelo `exit 64` do falso base. Não ficou mais permissivo que o script.

## Verificação
- Ferramenta: `bin/forge-mutante --ids VU4 tests/mutantes/v0480-seg-quarentena-fechar.json` em 08e2525e: `VU4 · morreu · bin/forge-fechar:867`.
- Teste do item: `python3 -m unittest tests.test_fechar_checks_do_head.PrazoUnico` verde 4 vezes, 3 delas em paralelo com 2 laços de CPU ocupada.
- Suíte inteira: fica no CI do PR (`R-REVIEW`), não rerrodada aqui.

## Parecer
Aprovado. A troca tira a dependência de tempo de máquina sem perder o que o teste prova (o prazo do passo 6 conta do início do passo 4) e aperta as asserções. Commit e mensagem limpos (Conventional Commits, etapa citada); fragmento de changelog presente.
