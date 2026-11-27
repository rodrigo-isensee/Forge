### Alterado
- F3 do estudo de atrito (v0481 E30.1): a develop entra na branch uma vez, no fechamento (forge-fechar, passo 2b), e o merge limpo não pede parecer novo; o forge-check pronto só avisa a base velha e confere contra o ponto de partida da branch.

### Corrigido
- F3 (v0481 E30.4): o merge da base que a descarta (-s ours, conflito resolvido com o lado da branch) desatualiza os pareceres, porque com o head que trouxe a base o forge-check pr sempre compara com o merge simulado; a regra da volta 3 (R-QA) compara os testes com o início mais a base trazida e não acusa o teste que a develop tirou.
