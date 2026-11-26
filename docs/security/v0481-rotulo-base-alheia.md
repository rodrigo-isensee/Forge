---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-rotulo-base-alheia
commit: 5c21b249e8612ceda94e015fd436cba2156ce757
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E17.8, #906, volta por delta)

Gatilhos: controle do Forge (a catraca, `tests/catraca.py`, PROTEGIDO), validade do rótulo `afrouxa-regra` (ADR 0008), aceite do usuário (`docs/security/aceites/`).

## Delta lido
`forge-check parecer delta` (`48034214..5c21b249`): no domínio, só `tests/test_catraca.py` (+9, teste de paridade); fora, `tests/mutantes/v0481-rotulo-base-alheia.json` (RB3) e os pareceres de review e QA. Nenhum código de controle mudou (`tests/catraca.py` e `bin/forge-check` iguais ao `48034214`).

## Achados anteriores
- A1 (recomendado, resolvido): `test_aceites_da_catraca_igual_ao_aceites_do_usuario_do_forge_check` (`tests/test_catraca.py:3181`) lê `ACEITES_DO_USUARIO` do `bin/forge-check:2298` por `ast` (sem executar o arquivo), exige uma atribuição só no topo do módulo e faz `assertEqual` com `catraca.ACEITES` (`tests/catraca.py:45`). A igualdade é simétrica: pasta nova só no `forge-check`, ou só na catraca, derruba o teste; sumir ou duplicar a atribuição também. RB3 (`tests/catraca.py:45`, `aceites/` para `aceite/`) morre por ele.

## O que aperta, o neutro e o que afrouxa
- **Aperta:** a deriva entre as duas listas de aceite, antes silenciosa, agora quebra a suíte (o mutante RB3 prova que o teste a vê).
- **Neutro:** o resto do delta (spec de mutante, pareceres de review e QA); o comportamento da catraca e do `forge-check` não muda.
- **Afrouxa:** nada no delta. O afrouxamento do item (pareceres de `docs/security/` fora de `aceites/` livres no `mesmo_diff`) é o da 1ª rodada, decidido pelo dono, sem mudança.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `python3 -m unittest tests.test_catraca.RotuloSobreviveAoConteudo` no `5c21b249` (24 testes, OK); `forge-mutante tests/mutantes/v0481-rotulo-base-alheia.json` (`RB1 · morreu · tests/catraca.py:1394`, `RB2 · morreu · tests/catraca.py:44`, `RB3 · morreu · tests/catraca.py:45`). CI do #906 no `5c21b249` na leitura: `bateria (passos)`, `bateria (verificações longas)`, `instalação`, `árvore já provada na develop` verdes; `catraca` vermelha por R-CONFORMIDADE (mudança em `tests/catraca.py` sem o rótulo do dono, esperado até o rótulo); `bateria (pareceres)` vermelha, com o log indisponível enquanto o run segue (os pareceres ainda estavam no `48034214`); suíte pendente. Sem linha `ci:` verde: o merge depende da suíte verde e do rótulo.
