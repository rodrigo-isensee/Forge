---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-mutante-pulado
commit: 8186cef3fc8174d5303ef9c7f9f668135effd1a2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E13.3, melhoria/v0478-mutante-pulado)

Diff lido: `4182a6b9..8186cef3` (bin/forge-mutante, tests/test_forge_mutante.py, tests/mutantes/v0478-mutante-pulado.json, changelog.d/v0478-mutante-pulado.md). Sem modelo de ameaças próprio da demanda; a ameaça revisada é a do brief: o autor pular um teste de propósito para fugir do veredito "sobreviveu".

## Gatilhos
Gatilhos: controle do Forge (bin/forge-mutante, prova de mutação usada como evidência do QA).

## Conclusão
O pulo não vira atalho. O que o autor ganha ao pular é trocar a saída 1 (sobreviveu) pela 2 (sem veredito), que segue não zero, dita na linha com os IDs pulados e "os que rodaram não o mataram"; a saída 0 (provado) continua exigindo falha por asserção ou erro só sob o mutante. A saída 2 já era alcançável antes por "teste declarado que não rodou", então nada novo se abre.

Caminhos conferidos:
- Pulo com os demais verdes: `bin/forge-mutante:316-317` dá `sem veredito` (saída 2, `:889` e o agregado de `:903`), nunca `sobreviveu`. Teste: `test_teste_declarado_pulado_e_sem_veredito_e_nunca_sobreviveu` e `test_teste_pulado_sai_2_sem_veredito_e_o_sobrevivente_segue_1` (ponta a ponta, saída 2 com a linha).
- Equivalente declarado com pulo: `bin/forge-mutante:883-884` sai antes da conversão em `equivalente`, então o pulo não confirma equivalente (saída 0). Mesmo teste de execução.
- Pulo não esconde morte nem o teste que não rodou: `:310-315` e `test_pulo_nao_esconde_a_morte_nem_o_teste_que_nao_rodou`.
- Controle: `:867-869` passa a aceitar `sem veredito` como "ok", e o veredito vai para a rodada do mutante; um teste que pula no controle e falha sob o mutante só "mata" se detectar a mudança de comportamento, o mesmo que uma asserção comum. Não abre saída 0 falsa.
- Pulo condicionado ao ambiente da cópia (pula só em `$TMPDIR`, fora do CI): escapa da contagem da catraca, mas no `forge-mutante` dá a mesma saída 2 visível; o QA cola a saída e só 0 prova.

Sondas executadas (sem achado, registradas para o QA): carregando `bin/forge-mutante` pelo arquivo e rodando um módulo real pelo `Registro`, o `skipTest` dentro de `subTest` (id `<teste> (i=2)`), o `raise unittest.SkipTest` no corpo e o declarado de classe ou de módulo saem `sem veredito`; o `SkipTest` em `setUpClass` (id `setUpClass (<classe>)`) sai `inválido` (saída 2); `expectedFailure` que falha não é anotado e não muda o veredito. Nenhum caminho deu `sobreviveu` disfarçado em 0.

## Detalhe dos achados
Sem achado no diff. Observação fora do diff (não bloqueia, não é deste pedido): a contagem de pulos da catraca (`tests/catraca.py:515`, `PULOS`) conta `skipTest`, `skip*` e `expectedFailure` por nome de chamada ou decorador, e não conta `raise unittest.SkipTest(...)`; um pulo novo assim não sobe o contador de pulos. Do lado do `forge-mutante` o efeito é só saída 2, por isso fica como melhoria, não achado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff, a sonda acima pela biblioteca padrão e os 3 testes novos do pulo (`python3 -I -m unittest discover -s tests -p test_forge_mutante.py -k pulado -k pulo`: 3 OK). Suíte inteira: só no CI do PR (não rodada aqui). Sem segredo, dependência nem workflow no diff; varredura de segredos e SAST não se aplicam.
