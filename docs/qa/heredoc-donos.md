---
tipo: qa
contrato: 1
pedido: heredoc-donos
branch: melhoria/heredoc-donos
commit: f16b60eb3d9045948fc1fef7e16cb74e7607a103
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-03
---
# QA: heredoc-donos

Base 032b4cbf691719c356676ab2b7ed717afbaa6335, head f16b60eb3d9045948fc1fef7e16cb74e7607a103 (6 commits, `hooks/_comum.py`, `hooks/conformidade.py`, `tests/test_hooks.py`, 4 fixtures, `tests/mutantes/heredoc-donos.json`). Sem UI: E2E de navegador e acessibilidade não se aplicam. O pedido não tem especificação de UX com `CA-n`; as obrigações são as do pedido (E1, PQ-1) e as decisões C-1 a C-5 do modelo de ameaças, mais a decisão do dono P-HEREDOC-DONOS-C4 = A. Diff conferido contra o escopo: nada fora de E1.

## Achados
- A1 (recomendado) hooks/conformidade.py:769 · o `return` do ramo ilegível (papel só de leitura, ou aninhado sem apontar ao Forge) sai sem descontar `corpos_pendentes` somado na linha 747; só pesa no prazo vencido, no sentido de recusar (falha fechado); sem prova de defeito de comportamento.
- A2 (recomendado) tests/test_hooks.py:1845 · as formas `python3 -` x1000 e x3000 repetem um dono só e passam também na base (0,2 s e 0,45 s medidos nela); guardam a recusa, não o custo quadrático; as formas `./x{i}`, `sh -s a{i}` e `python3 - a{i}` é que provam.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1/PQ-1: 1000 e 3000 donos distintos decidem em menos de 5,0 s e a linha com `bash` gravando `.github/` recusa | test_muitos_heredocs_recusam_dentro_do_orcamento (6 formas novas) + 4 fixtures | máximo (3000 donos), limite do orçamento | passou |
| C-1: a recusa não muda (leitura em partes igual à do texto inteiro) | test_donos_em_partes_leem_como_o_texto_inteiro (oráculo, mais de 1500 textos, mais fixtures e corpus de recusas) | prefixo com dúvida, atribuição antes do comando, `\\`, aspa sem par | passou |
| T2/C-5: sem fronteira limpa o dono se lê inteiro e conta o prefixo no teto | test_fronteira_limpa_e_o_teto_dos_donos_sem_fronteira | teto de caracteres, aspa/`$(`/`\\` abertos | passou |
| C-4 (decisão A do dono): prazo vencido com corpo pendente recusa, sem marcador crítico; sem pendente ou em PostToolUse libera | test_prazo_vencido_com_corpo_de_heredoc_pendente_recusa | zero pendente, 2 pendentes, PostToolUse | passou |
| Nada mais quebrou | tests.test_hooks inteiro | n/a | passou |

## Evidência
Máquina: no início da suíte o load estava em 15 (outra fase rodando); a regra de load abaixo de 7 não foi atendida nessa rodada, e o resultado vale como pior caso (passou mesmo assim). Os mutantes e o vermelho rodaram com load abaixo de 3.

**tests.test_hooks sobre f16b60e:** `Ran 70 tests in 582.762s`, `OK`. A suíte inteira de todos os módulos é a do pre-push do autor e do CI (D-5 reformulada); o QA rodou o módulo que o diff toca.

**Orçamento medido (limite 5,0 s, parede e CPU):**
| Forma | 1000 donos | 3000 donos |
|---|---|---|
| `./x{i}` | 0,21 s | 0,60 s |
| `sh -s a{i}` | 0,29 s | 0,77 s |
| `python3 -` | 0,22 s | 0,46 s |
| `python3 - a{i}` | 0,29 s | 0,89 s |
Crescimento 3000/1000 de 2,1 a 3,1 (linear, e não os 128 s da base com 3000).

**Mutantes** (`bin/forge-mutante tests/mutantes/heredoc-donos.json`, rc=0): D1 a D16, todos `morreu`. Conferência da lista contra o diff com `bin/forge-mutante --cobertura --base 032b4cb` (rc=0): cobertas as linhas de guarda _comum.py:968 (D10), 980 (D9), 983 (D8), 1468 (D5), 1477 (D16), 1484 (D7), 2490 (D11), 2493 (D12), conformidade.py:72 (D4); a 1466 vem isenta (ramo rápido, resultado igual ao do todo, provado pelo oráculo C-1). Pelas leituras do diff, D1, D2, D3, D6 (_comum.py:928-929, 1467, 1476) e D13, D14, D15 (conformidade.py:747, 799) cobrem o restante. Sem linha de guarda sem mutante.

**Vermelho antes do verde:** `forge-testes --vermelho 032b4cbf691719c356676ab2b7ed717afbaa6335 --modulos test_hooks`:
```
vermelho: base=032b4cbf6917 head=f16b60eb3d90 módulos=test_hooks (restrito por --modulos)
revertidos à base: changelog.d/heredoc-donos.md, hooks/_comum.py, hooks/conformidade.py
test_hooks · sem veredito (prazo, sinal ou executor sem registro em H,B)
sem veredito: volta ao autor; não vale como vermelho nem como já falhava.
rc=2
```
rc=2 como o autor relatou (o teste do orçamento na base passa de 300 s). Para não deixar o vermelho sem prova, rodei os testes novos à parte numa cópia em $TMPDIR com só os dois hooks da base (`git show 032b4cb:hooks/...`):
- test_donos_em_partes_leem_como_o_texto_inteiro: ERROR, `module 'conformidade' has no attribute 'interpreta_o_corpo'`.
- test_fronteira_limpa_e_o_teto_dos_donos_sem_fronteira: ERROR, `module '_comum' has no attribute 'fronteira_limpa'`.
- test_prazo_vencido_com_corpo_de_heredoc_pendente_recusa: ERROR, `'Hook' object has no attribute 'corpos_pendentes'`.
- test_muitos_heredocs_recusam_dentro_do_orcamento: `Ran 1 test in 310.364s, FAILED (failures=6)`: as formas `./x{i}`, `sh -s a{i}` e `python3 - a{i}` x1000 e x3000 caem (a base libera pelo prazo: `'.github/ (papel: dev)' not found in 'R-CONFORMIDADE: linha longa demais ...'`).
Os três primeiros caem por símbolo ausente (vermelho fraco em si); o peso do comportamento está nos mutantes D1 a D16 e na falha das 6 formas do orçamento.

**scripts/verificar-contribuicao.sh origin/develop:** `ok: nenhum segredo nem caminho pessoal no diff contra origin/develop.`, rc=0.

**PA-7 (docs/engineering/achados-recorrentes.md):** AR-1 (lista de mutantes incompleta): conferida acima, sem linha de guarda sem mutante. AR-2 (ramo de falha sem teste): o ramo de falha novo (prazo vencido com corpo pendente) tem teste de comportamento (C-4) e mutantes D11 a D15. Nenhuma linha nova a gravar.

## Cenários e resultado real
Caminho feliz: corpos de heredoc comuns (`cat`, `git commit -F -`) liberam como antes (fixtures do módulo e corpus, no oráculo). Bordas: 1, 2, 5 e 12 donos; prefixos com aspa, `$(` e `\\` abertos; separadores de linha, `&&`, `|`. Erro: prazo vencido com 2 corpos pendentes recusa com "separe o comando em chamadas menores"; marcador crítico segue com a mensagem antiga. Permissão: `PostToolUse` não recusa; sessão não vigiada não recusa.
