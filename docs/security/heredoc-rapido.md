---
tipo: revisao-seguranca
contrato: 1
pedido: heredoc-rapido
branch: melhoria/heredoc-rapido-p2
commit: 11a3bdbaac2c6f53b80dcad437bcd3e9fb2fab38
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-01
---
# Review de segurança: heredoc-rapido, passo 2

Etapa E1.9. Diff lido: `299f01f..11a3bdb` (changelog, `hooks/_comum.py` +23/-10, `tests/test_hooks.py`, 6 fixtures C-8 e `tests/mutantes/heredoc-rapido-p2.json`; o merge da develop não acrescenta código). Modelo de ameaças: `docs/security/ameacas/heredoc-rapido-passo2.md` (C-1 a C-8, F1 a F9). Substitui o parecer do passo 1 (#417), que veio da develop. Revisor diferente do autor.

## Gatilhos
`controles do Forge` (R-SEGURANCA): `hooks/_comum.py` decide o dono de cada heredoc, e dono menor seria bypass de R-MAIN e R-VERIFY.

## Achados
- A1 (recomendado) hooks/_comum.py:1736 · `sem_marcas` vale só com `resto` igual à marcada sem as marcas, e nada na assinatura força isso. Ninguém mais chama com `sem_marcas`; se aparecer outro chamador, a aspa escapada pode ser lida no texto errado. Documentar ou checar no teste.
- A2 (recomendado) tests/mutantes/heredoc-rapido-p2.json:38 · P4 (`sem_marcas` ignorado) é declarado equivalente na decisão e só o tempo o separa. A afirmação confere (ver C-5), mas nenhum teste a trava; o corpus C-1 abaixo não está na suíte. Opcional: incluir o oráculo no corpus.

## Detalhe
**M14 (agents/tech-lead.md:19):** cumpre. Linhas contadas: `hooks/_comum.py` 33 + `tests/test_hooks.py` 27 = 60, abaixo de 150; `tests/hooks/`, `tests/mutantes/` e changelog ficam fora. Um comportamento (leitura mais barata da linha marcada) e uma classe em `hooks/`, sem exceção de teto pedida.

**Controles do modelo:**
- C-1 cumprido. Oráculo diferencial, no mesmo processo, de `tirar_heredocs(c, True)` da develop 299f01f contra a da branch, sobre 3793 entradas (todos os campos `command`, `content` e `new_string` de `tests/hooks/**`, mais um gerador: 7 operadores, `<<-`, delimitador nu, `'X'`, `"X"`, `\X`, `cat<<E`, `2<<E`, dois heredocs, 11 prefixos de posição, `$(`, `"$(`, crase, `<(`, `eval "$(`, `{`, `(`, `$'…\'…'`, `#`, 8 sufixos, `\`⏎`|`, `| bash`, `| sh -s`, `;`, `&&`, fechado e não fechado). Resultado: `resto` e `gravado_e_rodado` iguais em todas; os `lidos` (dono) diferem em 246 casos, todos com `__fh<N>__` ou `__forge_heredoc_<N>__` escrito na própria linha (F8), e em todos o dono novo contém o antigo (maior; a grafia antiga deixou de ser removida, e a nova colide mais fácil, só soma texto). Zero diferenças sem marca escrita pela pessoa; zero dono menor.
- C-2 cumprido. `MARCA = "__fh"` (`:847`), `marca()` escreve (`:822`, `:829`), `MARCAS` procura (`:958`, `:1253`); fonte única. Palavra `[A-Za-z_][A-Za-z0-9_]*`, cercada de espaço, número do operador, terminador `__` (`_1__` não casa com `_12__`). Teste `test_marca_do_heredoc_e_palavra_comum_entre_espacos` (tests/test_hooks.py:1682) confere espaços, classe da palavra, fora de `COMPOSTOS` e contagem.
- C-3 cumprido. Nenhuma linha de falha mudou (`DonosDosHeredocs` intacto); marca não achada continua em `trechos=None`, dono = comando lógico inteiro. Nenhuma ocorrência de dono vazio no oráculo.
- C-4 e C-6 não se aplicam (não há recorte nem cache novo).
- C-5 cumprido. `sem_marcas=resto` só substitui a leitura de `aspa_escapada` (`:1753`). Provado por leitura: marcada e `resto` diferem só no texto de cada marca, e ambos têm um espaço no lugar do operador; a marca é palavra `[A-Za-z0-9_]` entre espaços, sem aspa, `\` nem `$`, então não abre nem fecha `$'…'` e não cola em `\`, `$` ou `'` vizinhos. `comentario_ambiguo`, `corpos_se_leem` e `comandos` continuam lendo a marcada.
- C-7 cumprido. O teste do orçamento mantém os 5,0 s e ganha `x=$(` (recusa pelo teto de palavras) e `|`; ordem das recusas inalterada (fixtures C-8 passam).
- C-8 cumprido. Fixtures a a f existem (`tests/hooks/conformidade/heredoc-marca-c8*.json`); mutantes P1 a P3 com testes, P4 equivalente justificado (A2).

**Lacunas:** `osv-scanner`, `semgrep` e `gitleaks` não rodados (não há dependência nova nem segredo no diff). Sem caminho de ataque realista nos dois achados.
