---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-h5-prova-local
commit: c046a44b34066447d9f595b9d31e3679ba2b9fba
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047 (H5, prova local por testes tocados, E2.647)

Escopo: `73a0ab81..c046a44b` (base `develop`), 4 arquivos: `bin/forge-mutante` (sensível da catraca), `tests/test_forge_mutante.py` (classe `LimiteDosModulos`), `tests/mutantes/v047-h5-prova-local.json`, `changelog.d/v047-h5-prova-local.md`.

## Gatilhos
Gatilhos: controle da catraca (`bin/forge-mutante`, modo `--base` da revalidação), execução de subprocesso.

## Leitura
- Direção do limite (`bin/forge-mutante:1047-1054`, `limitar`): só tira testes da lista de cada mutante. Pelo `veredito` (`bin/forge-mutante:294-305`), morte exige falha de um teste que rodou; menos testes só tiram mortes, nunca as criam. Para o mutante comum o efeito é fechar mais (sobrevivente a mais, nunca morte falsa): sem fuga da catraca. O mutante só entra pelo `no_diff` sem mudança (`bin/forge-mutante:960-965`): teste enfraquecido no delta tem o módulo no diff, e o `forge-testes --listar` desse caminho o devolve no plano, então ele continua rodando.
- Falha aberta controlada (`bin/forge-mutante:1027-1038`): erro, prazo de 60 s, suíte completa ou saída fora do formato dão conjunto vazio, e o conjunto vazio deixa o mutante intacto (`:1051`), ou seja, o comportamento anterior, que é o mais estrito. Coberto por `test_listar_que_falha_ou_estoura_o_prazo_nao_limita` e `test_sem_plano_dirigido_roda_os_testes_declarados_inteiros`.
- Subprocesso (`bin/forge-mutante:1032-1033`): lista de argumentos, sem shell, `-I`, caminhos depois de `--`, executável resolvido pelo próprio `__file__` (não pelo PATH nem pela árvore revisada). Nenhuma fronteira nova: o `forge-mutante` já executa os testes da árvore revisada. Regex `PLANO_DIRIGIDO` com `fullmatch` e um só `(.+)`: sem retrocesso catastrófico.
- Casamento de módulo (`bin/forge-mutante:1041-1044`): igualdade exata de prefixos por ponto; `test_forge` não casa `tests.test_forge_lib`.
- Mutante `equivalente` com `testes`: o limite também o alcança (A1). Teste declarado que mata o mutante fora do plano deixa de desmentir o equivalente na revalidação. Sem caminho de ataque: se um teste o mata, a guarda está coberta; o dano é só a declaração velha na spec. Recomendação, não bloqueio.
- Suíte: a branch não tem PR nem execução de CI no head (`gh run list` vazio); a suíte inteira fica para o CI do PR, que é portão do merge. Rodei o teste novo: `LimiteDosModulos`, 4 testes, OK.

## Achados
- A1 (recomendado) bin/forge-mutante:1047 · limitar alcança o mutante equivalente com testes: teste declarado que o mata fora do plano deixa de desmentir o equivalente na revalidação (sonda: limitar corta tests.test_b); excluir do limite o mutante com chave equivalente.

## Sondas

## Detalhe dos achados
A1 · evidência `bin/forge-mutante:1047-1054` e `:868-870` · sonda local: `limitar({'id':'M1','equivalente':<25 car.>,'testes':['tests.test_a.T.t','tests.test_b.T.t']}, {'test_a'})` devolve só `tests.test_a.T.t` · caminho de ataque: nenhum realista (o teste que mata prova cobertura; perde-se só a detecção da declaração vencida) · severidade: informativa · correção mínima: em `limitar`, `if "equivalente" in m: return m` · esforço P · dono: tech-lead (autor do H5).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, execução local da classe nova e uma sonda de função. Sem varredura de segredos nem SAST no PATH conferidos para este delta (sem segredo nem dependência nova no diff).
