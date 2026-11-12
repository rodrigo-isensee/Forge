---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/v046-mapa-testes
commit: e6565be2d303c831772be74974eb84df2352fb4f
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E22.3, MAPA do forge-testes)

Review do diff `origin/develop...e6565be2` (base `a1318e88`, 1 commit, 22 linhas), em `bin/forge-testes`, `tests/test_testes_tocados.py` e `changelog.d/v046-mapa-testes.md`, lido em worktrees destacadas da base e do head.

## Gatilhos
`R-SEGURANCA`: controle do Forge, o plano de testes do envio (o MAPA do `bin/forge-testes`, lido pelo `planejar` e pelo `--afetados` que o pre-push usa).

## Achados
- A1 (bloqueante) bin/forge-testes:158 · a regra nova de tests/test_ritmo.py tira esse módulo de teste da suíte completa no plano padrão (planejar: completo vira 7 módulos), contra a DECISÃO DO DONO de 2026-10-24 (M8 opção C, não afrouxa) e contra o próprio comentário em :166; afrouxar pede decisão (R-CONFORMIDADE)

## Sondas
- S1 · planejar(["tests/test_ritmo.py"]) do bin/forge-testes na base a1318e88 e no head e6565be2 · espera: completo nos dois (opção C) · obtido: base ('completo', ['tests/test_ritmo.py sem mapa']); head ('dirigido', 7 módulos)

## Detalhe dos achados
A1. Evidência: `bin/forge-testes:157-159` (regra nova) e `bin/forge-testes:166` (comentário que segue dizendo "Módulo de teste no diff não tem regra: cai na suíte completa (M8, opção C)"). A DECISÃO DO DONO de 2026-10-24 (pedido LOTE-M8-PREPUSH-REV, linha 29) diz que todo módulo de teste mudado no diff roda a suíte inteira, e que isso endurece, não afrouxa. O cartão TESTE-RITMO-SEM-MAPA trata como defeito justamente o efeito dessa decisão ("cai na suíte completa"). A origem do cartão é uma melhoria vista da E23.41, não uma decisão do dono; a etapa E22.1 é texto do pedido e também não é decisão do dono. Sonda S1, rodada importando o script nas duas cópias: na base, `planejar(["tests/test_ritmo.py"])` devolve `completo`; no head devolve `dirigido` com `test_ambiente_git, test_apoio_sandbox, test_forge, test_hooks, test_pre_push_trava, test_ritmo, test_testes_tocados`. Combinado com outro caminho (`tests/test_ritmo.py` mais `bin/forge-doutor`), a base dava `completo` e o head dá `dirigido`, com 15 módulos.
Quem usa esse plano: `scripts/conferir-reversao.py:23` (a suíte afetada do revert), a seleção de módulos do `forge-testes --listar` que o `forge-mutante` e o tech-lead seguem (`agents/tech-lead.md:25`) e o `--vermelho` do QA. O pre-push usa o `--afetados`, e esse não perdeu nada (ver abaixo).
Caminho de ataque: não há atacante externo. O risco é o da opção C: o MAPA é estático, e um módulo que passe a importar, carregar pelo nome ou ler o `test_ritmo` de outra forma fica fora do plano sem que nada avise. A conferência de hoje (o `--afetados` e os leitores que achei) bate com os 7 módulos; o que se perde é a garantia para o futuro. O CI do PR continua rodando a suíte inteira, então a severidade é baixa. Bloqueia porque é requisito: o brief pede que nenhuma regra do MAPA deixe de rodar o que antes rodava, e a regra afrouxa uma decisão do dono sem decisão nova.
Correção mínima, à escolha do dono do pedido:
1. Tirar de `bin/forge-testes` a regra `tests/test_ritmo\.py` (linhas 157-159) e, de `tests/test_testes_tocados.py:57-58`, a entrada `"tests/test_ritmo.py"`. A parte do `bin/forge-doutor` fica como está. O `--afetados` já leva o `test_ritmo` e quem varre `tests/` sem a regra.
2. Ou levar ao dono, pelo Jarvis (`R-DECISAO`), a pergunta de rever a opção C para `tests/test_ritmo.py`. Com decisão, a regra fica, o comentário de `:166` ganha a exceção e o PR leva o destaque de afrouxamento.
Esforço: P. Dono: tech-lead (autor da E22.1).

Conferido sem achado:
- **Regra do `bin/forge-doutor`.** Antes rodava 5 módulos; agora roda 9, e os 5 continuam (`test_atualizar, test_doutor, test_forge, test_medidas_m14b, test_novo_projeto`). No `planejar` e no `--afetados`, o plano do head contém o da base: no `--afetados`, a base dava 7 módulos (`test_qa_doutor_f8` e `test_testes_tocados` entravam por citação) e o head dá 10.
- **`--afetados` de `tests/test_ritmo.py`.** Base: `test_ambiente_git, test_forge, test_pre_push_trava, test_ritmo, test_testes_tocados`. Head: esses 5 mais `test_apoio_sandbox` e `test_hooks`. O plano do envio não ficou mais fraco. Os leitores de `tests/` que procurei (`glob`/`rglob` de `test_*.py` e `*.py`, `git ls-files`) estão todos nos 7 módulos. Os outros citam o `test_ritmo` só como dado (`tests/pesos-d4.json`, `tests/mutantes/v0457-e3*.json`) ou listam só os nomes (`tests/test_catraca.py:3490`).
- **Nenhuma outra regra mudou.** O diff do MAPA toca só essas duas entradas. Nenhuma linha de guarda mudou, e por isso não há spec de mutante.
- **O teste novo não lê fora do clone.** `tests/test_testes_tocados.py:88-94` usa `RAIZ = Path(__file__).resolve().parent.parent` (`:20`) e `RAIZ.glob("tests/test_*doutor*.py")`, só para leitura com regex. Nenhum desses arquivos é link (`find -type l` vazio). Não executa nada, não usa rede nem variável de ambiente. Com `test_doutor_branch_atrasada` fora de propósito, ele falha quando aquela branch entrar sem acrescentar o módulo, como o brief descreve. `tests.test_testes_tocados` no head: 150 testes, OK (1 pulado, pré-existente).
- **PA-7.** AR-3, AR-5, AR-7 e AR-11 (os de segurança) não se aplicam: o diff não toca hook, trava de ambiente nem invocação de interpretador.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas no `planejar` e no `--afetados` da base e do head (worktrees destacadas em `$TMPDIR`) e `tests.test_testes_tocados` no head. Lacuna: gitleaks não está no PATH local; o diff não traz configuração nem credencial.
