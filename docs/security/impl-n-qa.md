---
tipo: revisao-seguranca
contrato: 1
pedido: impl-n-qa
branch: melhoria/impl-n-qa4
commit: 738cfff89e751d0543ff977bde075c0ea45ffe13
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-22
---
# Review de segurança: impl-n-qa (E1.3, branch refeita melhoria/impl-n-qa4)

Escopo: `git diff a3dbe226f71fa60a9ed4ce540a9ff0a3d73d385c 738cfff89e751d0543ff977bde075c0ea45ffe13` (76670d1 item 34 com a R3 e o A1, 66fdc39 item 65, bd1b485 item 36, 738cfff fragmento), contra o adendo `docs/security/ameacas/n-qa.md` (V1 a V19, CA-1 a CA-22). O EXT-1 está fora do lote (espera a P-1 do dono); V8, V9 e V16 a V19 não se aplicam, salvo o texto da matriz do item 36. Diferença para a entrega revisada antes (1230d12, parecer 9e74609): só `bin/forge-testes` (a marca `herdada` em `da_base` e a leitura da base em `testes_da_base`), seis testes novos em `tests/test_testes_tocados.py` e uma frase em `skills/qa-testing/SKILL.md`, tudo dentro do commit do item 34; o resto é igual, e as conclusões dos pareceres e1a61a7 e 9e74609 sobre ele valem aqui.

## Gatilhos
Nenhum arquivo da lista da `R-SEGURANCA` é tocado: `tests/config.json` só ganha invariantes (nenhum sai nem afrouxa), e `hooks/`, `.githooks/`, `bin/forge-check` e `tests/catraca.py` ficam iguais. O parecer vem do plano (`gatilhos_seguranca`), porque as duas ferramentas gravam arquivos, executam o código da branch e produzem a prova que os portões colam.

## Achados

## Detalhe dos achados
Sem achado bloqueante. Conferências pedidas pelo brief e recomendações abaixo.

**A1 do parecer anterior (9e74609): corrigido dentro do commit do item 34 (76670d1).**
- `testes_da_base` (`bin/forge-testes:306-326`) lê a versão da base do módulo de teste por `git ls-tree` e `git show` e tira os `Classe.teste` por `ast`, sem executar nada; segue a herança entre classes do próprio módulo, com guarda contra ciclo. Módulo que a base não tem devolve conjunto vazio (`:312`, todos novos, a R3 segue); base ilegível (erro do git, sintaxe, bytes inválidos) devolve `TodosExistiam` (`:315`), e ninguém ganha prova herdada (falha fechada).
- `da_base` (`:328-340`) só marca `herdada` a entrada que não é do próprio teste (carga, `setUpClass`, `setUpModule`); a do próprio teste continua vencendo. `classificar` (`:281`) dá `não prova (herdada da base)`, que não conta como prova nem como sem veredito.
- Sondas em `$TMPDIR/sec5q.*` (repositório de brinquedo, com o `bin/forge-testes` de 738cfff): só `import novo` no topo de módulo existente, sem teste novo, sai 1 com `não prova (herdada da base)` (antes saía 0); herança dentro do módulo (`class T(M, TestCase)`, com o teste em `M`) sai 1. Os testes de borda pedidos pela DECISÃO TÉCNICA de 10:55 estão em `tests/test_testes_tocados.py:520-538` (import no topo, `setUpClass`, `setUpModule`, todos com saída 1; teste novo ao lado do existente sai 0 e o existente fica neutro).
- Conferi também a cobertura da leitura por `ast` contra o carregador real em toda a suíte do Forge (cópia por `git archive 738cfff` em `$TMPDIR/sec5.*`): 0 ids de teste fora do conjunto lido da própria árvore, então nenhum módulo do Forge de hoje tem teste que a leitura classifique como novo sem ser.

**R3 do parecer e1a61a7 continua corrigida.** Módulo de teste novo que importa no topo um arquivo novo dá `prova (API ausente)` com saída 0 (CA-5, `tests/test_testes_tocados.py:497`); erro de sintaxe do módulo continua sem veredito (CA-4, `:343`).

**Nenhuma asserção afrouxada.** Entre 1230d12 e 738cfff, o único trecho removido em `tests/` e `skills/` é a linha da skill substituída pela mesma linha com uma frase a mais; nenhum teste perdeu asserção.

**Testes sem rede (`R-CUSTO`).** Os módulos novos só usam repositórios locais em pasta temporária; nenhuma chamada de rede.

**Caminho restante de "prova (API ausente)" sem teste novo de verdade (pergunta do brief).** Existe, em três formas, e nenhuma é bloqueante pelo critério de proporcionalidade: nenhuma acontece sem uma mudança deliberada de estrutura do teste, e nenhum módulo do Forge de hoje tem a terceira forma (conferido acima).
- **R8. Média. Herança de outro módulo cai como teste novo** (`bin/forge-testes:321`): só a base que é nome de classe do próprio módulo é seguida; a que vem por import (`from apoio import M`, `ap.Base`) é ignorada, e o teste herdado conta como novo. Sonda: classe existente que herda o teste de um módulo de apoio, entrega que só acrescenta `import novo`, saída 0 com `prova (API ausente)`. É o caminho do A1 anterior para essa forma de módulo, e falha aberta, ao contrário do `TodosExistiam`. Correção mínima: classe com base que não se resolve no módulo conta todos os testes dela como já existentes (falha fechada). Esforço P. Dono: tech-lead. Recomendo entrar antes do N-HOOK1, que usa esta prova.
- **R9. Baixa. Classe ou módulo renomeado conta como novo** (sondas S1 e S2): renomear a classe, ou mover o módulo, e acrescentar `import novo` dá saída 0 sem asserção nova, porque a identidade do teste é o nome. Pede refatoração junto com o import, e a linha listada mostra o id novo, que o QA confere contra o diff. Correção possível: tratar como existente o método cujo corpo (`ast.dump`) já está em algum módulo de teste da base. Esforço P a M. Dono: tech-lead.
- **R10. Informativa, no sentido contrário (falha fechada).** Teste que já existia e passa a afirmar o comportamento novo, com o import novo, sai `não prova (herdada da base)`; o autor precisa de um teste com nome novo. Não abre caminho de ataque; vale uma frase na skill `qa-testing`.

As R1, R2, R4, R5 e R6 de e1a61a7 e a R7 de 9e74609 seguem abertas (o código delas não mudou); a R2 (o que a "API ausente" prova) cobre também a R9. A janela da V6 (b), o hook `pesado` sem reconhecer o `--vermelho` e o `forge-mutante`, continua registrada para o lote dos hooks.

## Riscos aceitos e ferramentas
Sem risco aceito. Leitura estática do diff e sondas locais em `$TMPDIR` (repositórios de brinquedo e uma cópia por `git archive`), fora da worktree; a árvore da worktree só ganhou este arquivo. A suíte do Forge não rodou aqui (`R-TETO`); ela roda no pre-push. Nenhuma ferramenta de varredura foi usada nem instalada (`R-CUSTO`).
