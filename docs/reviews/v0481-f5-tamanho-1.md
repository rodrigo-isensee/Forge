---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f5-tamanho-1
commit: 473004fedf0cbbd2a4618452b28ba6fc6802daa0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E38.8, #933, F5.1 o aviso de tamanho traz o corte sugerido), 1ª rodada completa

Revisor: outra instância do `tech-lead`, não a autora do F5.1. Diff lido: `6716f239..473004fe` (base do merge da `develop` na branch), 8 arquivos. Código: `bin/forge-check` +30 e `bin/forge_tamanho.py` +46, 76 linhas pela conta do H1, dentro do teto de 150. O resto é teste, specs de mutante, uma frase da skill e o fragmento do changelog.

- ci: 473004fedf0cbbd2a4618452b28ba6fc6802daa0 verde

## Achados
- A1 (recomendado) bin/forge_tamanho.py:55 · A docstring diz "a linha def/class de cima mais próxima", mas sem `.gitattributes` o git usa a heurística padrão: a linha sem recuo mais próxima. Método cai no `class`, função nova no bloco anterior e constante vira contexto (o teste :319 mostra `bin/app:x`). Ajuste docstring e skill (:20).

## Parecer
**Aprovado.** O PR faz o que a linha F5.1 do desenho pede (`docs/arquitetura/f5-tamanho-pela-ferramenta.md`, seção 7). Ganham `forge_tamanho.py` as funções puras `linhas_por_funcao`, `corte_sugerido`, `texto_do_corte` e `recusa_de_abertura`. Ganha o `forge-check` o `corte_do_intervalo` e o `tamanho_na_abertura`, no bloco do `tamanho_do_pr`. O aviso do `pr` e do `pr --previo` passa a imprimir o corte. Os testes `NoPr` seguem sem mudança de comportamento.

**CI (G3):** li o `gh pr checks 933` no head `473004fe` (run 45992098024). Estão verdes as 5 partes da suíte 3.12, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)`, `teto de pulados (python 3.12)` e `árvore já provada na develop`. Ficam fora da conta `bateria`, `bateria (pareceres)` e `catraca`, que esperam os pareceres e o rótulo.

**Leitura (checklist):**
- **Correção da conta:** `linhas_por_funcao` soma `b + d` de cada `@@ -a,b +c,d @@`. Contagem omitida vale 1, e `0` explícito vale 0 (a string `"0"` é verdadeira no `or`). A soma por arquivo bate com o `--numstat`, então o corte do arquivo grande fecha no mesmo total do H1. O binário (`-`) dá 0 linhas e fica fora do corte.
- **Empacotamento:** `corte_sugerido` faz o first-fit decrescente, com empate pelo nome (ordem estável). A unidade acima do teto abre PR próprio marcado `CORTE_A_MAO`, e nenhuma outra cabe nele, porque `p[0] + linhas > teto`.
- **Falha fechada:** em `tamanho_na_abertura`, o numstat que falha recusa com `R-REVIEW` e manda rodar o `git fetch`. O `-U0` que falha só tira o corte (`None`), e a recusa sai sem ele. No `tamanho_do_pr`, o corte `None` ou `[]` não imprime nada, e o resto do fluxo fica igual.
- **Segurança:** o git é chamado por lista de argumentos, com o nome depois de `--`, com `--no-ext-diff`, `--no-textconv` e `--no-color`, e o numstat vem com `-z`. Não há shell nem caminho escolhido pelo agente. O parecer de segurança é do `security-engineer`.
- **Escopo:** `tamanho_na_abertura` ainda não tem chamador em produção. É a base do F5.2 (hook) e do F5.3 (catraca), como o desenho corta (seção 7, "Ordem"), e já tem teste próprio. Não conta como código morto deste item.
- **Commits:** seguem Conventional Commits em português. O merge da `develop` (`fcfce71e`) entrou sem conflito, e o `473004fe` ajusta o caso sintético à guarda C-2 que veio com ele.

**Verificado local** (só o que o diff toca):
- `python3 -m unittest tests.test_forge_tamanho`: 37 testes, OK (5,3 s).
- `bin/forge-mutante --processos 1` nas 3 specs (`v0481-f5-tamanho-1.json`, `-2.json` e `-3.json`): morreram os 17 (M1 a M17). M13 e M17 morreram por erro, porque o mutante derruba o código seguinte (`None` no numstat, `pr` sem lista). Mesmo assim, o ramo vigiado tem teste de comportamento em `test_git_que_falha_recusa_e_o_corte_que_falha_sai_sem_ele` e `test_agrupa_o_maior_primeiro_no_primeiro_pr_em_que_cabe`.
- `bin/forge-mutante --cobertura --base 6716f239`: 14 linhas de guarda, todas cobertas, nenhuma descoberta.
- `bin/forge-mutante --conferir --base 6716f239`: o trecho de cada spec está no lugar.

**Sonda do A1** (repositório temporário, sem `.gitattributes`): adicionei linhas em dois métodos de `class C` e uma função nova `novo()` depois dela. O `git diff -U0` deu os três cabeçalhos `@@ ... @@ class C:`. O corte é só sugestão e o total não muda, por isso o achado é recomendado.
