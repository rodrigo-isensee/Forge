---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-perfil-fifo
commit: dba51ddfb97745dfcab0f74df93471e376aaf8fc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E7.33, code review por delta do #886, de afa98e1a a dba51ddf, classe C)

Escopo: revalidação pelo delta, só a spec M3. `forge-check parecer delta docs/reviews/v0481-perfil-fifo.md` (parecer anterior no 517f80fd): o delta no domínio é só `tests/mutantes/v0475-mp1-mp7.json`, `revalida: sim`. O commit dba51ddf (E7.31) muda 2 linhas dessa spec; `git diff afa98e1a dba51ddf -- hooks/` vazio.

## O que foi conferido
- **Guarda e testes da M3 iguais:** no diff, só o `de` e o `para` da M3 mudam; `id`, `guarda`, `arquivo` e os dois `testes` (`test_ativos_em_link_fifo_grande_ou_com_nomes_demais_nao_mede` e `test_ativos_em_fifo_com_escritor_e_json_valido_nao_vale`) seguem os mesmos. A guarda é a mesma de `hooks/_comum.py:123` (`S_ISREG` do leitor de ATIVOS).
- **Par único:** o `de` novo (`if not stat.S_ISREG(os.fstat(fd).st_mode):` com o `return None` da linha seguinte) aparece 1 vez em `hooks/_comum.py`; o trecho de uma linha antigo também casava a guarda de `ler_marca_do_git` (`hooks/_comum.py:158`, seguida de `raise OSError`), que o par agora exclui. M1 a M8 da spec seguem com 1 ocorrência cada.
- **A M3 morre:** `bin/forge-mutante tests/mutantes/v0475-mp1-mp7.json --ids M3` no dba51ddf: `M3 · morreu · hooks/_comum.py:123`.
- **`bin/forge-mutante --conferir --todas` igual à base:** saída no dba51ddf e no Base-sha 5fb8e328 idênticas (`diff` vazio, 26 linhas, código 1 nos dois); os trechos repetidos listados são de outras specs (`acelera-p3c`, `hk3-parecer-pasta-14`, `v0457-escopo-ponto-3`, `z075-prepush-relogio`) e já estavam na base; nenhuma linha de `v0475-mp1-mp7`.
- **CI do #886 no dba51ddf** (runs 45599610109 e 45599609810, `headSha` conferido): as 10 partes da suíte, os dois tetos de pulados, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação` e `árvore já provada na develop` verdes. Vermelhos só `bateria (pareceres)` (parecer de review no 517f80fd, que este regrava), `bateria` (o agregado: `pareceres: failure`, o resto `success`) e `catraca` (rótulo `afrouxa-regra` do dono para `hooks/_comum.py` e `hooks/conformidade.py`).
- **Commit:** Conventional Commits em português, mensagem com o motivo.

- ci: dba51ddfb97745dfcab0f74df93471e376aaf8fc verde

## Achados
- A2 (recomendado) hooks/_comum.py:2728 · `Hook.iniciante` (`perguntar`, escrita do perfil, meta.py:355) segue com `git rev-parse` e `read_text`: FIFO no perfil faz `reset --hard` e `clean -fd` no projeto esperarem 3,2 s e recusarem pelo prazo. Cartão: delegar a `perfil_iniciante`. Mantido da volta anterior.
- A4 (recomendado) hooks/conformidade.py:1577 · o `com_trecho` roda fora do `try`: se o alarme vence ali, o `PrazoVencido` chega ao `prazo_vencido`, que libera na sessão do Forge. Janela curta e já existente, sem gatilho provado. Mantido da volta anterior.

## Parecer
Aprovado no dba51ddf. O delta só troca o trecho da M3 pelo par único, sem mudar guarda nem testes; a M3 morre e o `--conferir --todas` fica igual à base. A2 e A4 seguem recomendados e viram cartão depois do merge. Para integrar faltam os outros pareceres no head e o rótulo `afrouxa-regra` do dono.
