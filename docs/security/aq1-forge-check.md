---
tipo: revisao-seguranca
contrato: 1
pedido: aq1-forge-check
branch: melhoria/aq1-forge-check
commit: 3bb7aea754d47291d1b3697234fedf790e1bdf4c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: aq1-forge-check

Diff revisado: `a83de9e...7ae7606` (bin/forge-check, agents/conferente.md, agents/jarvis.md, docs/engineering/achados-recorrentes.md, docs/melhoria-continua.md, changelog.d, testes e mutantes). Revalidação por delta dos dois merges da develop (b3791ed e f232e06): `7ae7606..3bb7aea`, com o `forge-check delta` sobre este parecer.

## Gatilhos
`R-SEGURANCA`, controles do Forge: o `forge-check brief` (decisões cobradas, conferência da volta), o formato dos achados recorrentes lido pelo `brief gerar`, o `escape registrar` e o texto do conferente e da autoconferência do Jarvis.

## Achados

## Detalhe dos achados
Sem bloqueante. O que se conferiu, e com que prova:

- **`Depende de:` não abre leitura fora de `docs/pedidos/`.** `bin/forge-check:4251` monta `docs/pedidos/<id>.md` com o id já reduzido ao nome (`id_do_pedido`, `bin/forge-check:1656`), exige `REGISTRO_VALIDO` (lista positiva `[A-Za-z0-9._-]+`) e lê por `ler_registro` (`bin/forge-check:4199`), que resolve o caminho e recusa link para fora da raiz ou de `docs/pedidos/`. Sondas locais (fora do repositório, em `$TMPDIR`), sobre a raiz sintética da classe `DecisoesCobradas`: `../../<caminho absoluto>`, caminho absoluto, `~/x/../fora`, symlink em `docs/pedidos/` para arquivo fora da raiz e symlink para `docs/adr/`. Nas cinco, nenhuma decisão do arquivo externo entrou nas fontes; a saída é `dependência sem registro legível` (informativo). Nome com ESC e U+202E sai escapado (`nome_seguro(sem_controle(...))`).
- **O `brief` continua reprovando o que reprovava.** A dependência só soma fontes e cobranças: ela roda depois das citações (a citação numa linha do dono continua reprovando quando o registro falta), divide o `TETO_DE_FONTES` (excedido, reprova) e o registro grande demais reprova. No `-REV`/`-PR` cujo `Depende de:` é o próprio pedido de origem, o G1 pula a leitura repetida (`rel in vistos`, `bin/forge-check:4276`) e a dependência já trouxe as decisões, ou reprovou por tamanho. `conferir_volta` ganha uma reprovação (`bin/forge-check:1477`), independente do `--ref`, e não remove nenhuma. O texto do conferente troca "decisão registrada ou item do escopo" por "DECISÃO TÉCNICA no Histórico": fica mais estrito.
- **Regex dos achados recorrentes** (`bin/forge-check:2127`): o lookahead limita a classe a 70 caracteres de uma lista positiva, sem espaço duplo nem final, e o `fullmatch` vale por linha. Sonda de retrocesso com corpos de 1.000 a 100.000 caracteres (`a`, `a `, `a-`, `a b ` e `última` longa): nenhuma passou de 1 ms de CPU. O resultado é aviso em stderr e não decide portão.
- **`escape registrar --origem`**: valor conferido contra a lista positiva `ORIGENS` antes de gravar (`bin/forge-check:2539`); na leitura, `origem_do_escape` (`bin/forge-check:2518`) só conta valor da lista, e a `nota` continua sem `|` nem quebra de linha. Uma coluna não se forja pela outra.
- PA-7 (`docs/engineering/achados-recorrentes.md`): AR-3 (lista negativa em trava): as validações novas usam lista positiva. AR-5 (python sem `-I` em caminho que decide): não há shell nem hook novo no diff. AR-1, AR-2 e AR-4 são de QA e de review e ficam fora deste parecer.
- Testes do item rodados: `tests.test_erros_no_brief` e `tests.test_medidas_m14b` (74 OK) e a classe `DecisoesCobradas` com as sondas (34 OK).

## Revalidação por delta (7ae7606..3bb7aea)
- **O patch do lote não mudou com os merges.** Comparei, linha a linha, as linhas `+`/`-` de `a83de9e...7ae7606` com as de `f232e06..3bb7aea` em `bin/forge-check`, `agents/conferente.md`, `agents/jarvis.md` e nos testes: `bin/forge-check`, `agents/conferente.md`, `tests/test_forge.py` e `tests/test_medidas_m14b.py` são idênticos. Em `agents/jarvis.md`, a linha resolvida mantém as duas frases do lote ("dos pedidos do seu `Depende de:`", "cada recomendação incluída tem a sua DECISÃO TÉCNICA no Histórico") e a da develop (aviso do pre-push no brief de parecer). Em `tests/test_erros_no_brief.py`, só a lista esperada ganha o `review` da linha que a develop trouxe (3bb7aea).
- **O `forge-check brief` reprova o que reprovava.** O que a develop trouxe ao `bin/forge-check` (HIST e GUARDA) não toca `tem_decisao_tecnica` (`bin/forge-check:1316`), `conferir_volta` (`bin/forge-check:1448`, a reprovação da recomendação sem DECISÃO TÉCNICA segue com ou sem `--ref`), `decisoes_cobradas` (`bin/forge-check:4229`) nem o regex dos achados (`bin/forge-check:2128`). O GUARDA só acrescenta um PQ da `--cobertura` ao que o `gerar_volta` escreve (`bin/forge-check:1433`), sem tirar cobrança; o HIST mexe no `esperas` e no `cartoes_do_quadro`/`cartoes_do_pedido` (só leitura, saída com `sem_controle`), fora do caminho do `brief`. Não há caminho novo que passe sem decisão. Testes do item no head: `tests.test_erros_no_brief` e `tests.test_medidas_m14b` (79 OK), `DecisoesCobradas` (30 OK), `DecisoesNaVolta` e `VoltaComRecomendacao` (15 OK).
- **`docs/engineering/achados-recorrentes.md`.** A linha da develop (`mascara-do-shell-esconde-codigo`) ficou como AR-6, e as AR-1 a AR-5 do lote ficaram com os seus números; as cinco seguem o formato do regex. É dado lido como aviso, não decide portão. Os pareceres antigos que citam "AR-1" para essa classe passam a apontar a outra linha: é rastreabilidade, sem caminho de ataque.
- O resto do delta (`bin/forge-mutante`, pareceres, mutantes, CHANGELOG, versão) veio da develop já revisado nos PRs dela e não é deste lote.

Recomendações do parecer anterior, que seguem (não bloqueiam e não devolvem):

1. **Id do achado sem a origem** (`bin/forge-check:1316`, `tem_decisao_tecnica`). A DECISÃO TÉCNICA é casada só pelo id (`R2`, `A1`). Uma linha de uma rodada anterior ("DECISÃO TÉCNICA ... R1") cobre o `R1` de um parecer novo ou de outro tipo. Caminho: o Jarvis inclui na volta uma recomendação nova com id que já foi decidido e o comando não cobra a decisão dela; a falha é de processo, sem atacante externo, e o conferente ainda lê a linha. Severidade baixa. Correção mínima: exigir também o tipo ou o sha curto da marca (`incluído <tipo> <sha7> <id>`) na linha da decisão, e o PREENCHER do `gerar --volta` já pedir essa forma. Esforço P. Dono: tech-lead.
2. **Dependência ilegível só informa** (`bin/forge-check:4278`). `ler_registro` devolve `ausente` tanto para o arquivo que falta quanto para o link que sai de `docs/pedidos/`. Na dependência, os dois casos viram informativo. Caminho: um `Depende de:` que aponta um symlink para fora some das cobranças em silêncio. A leitura fica recusada, então não vaza nada, mas a anomalia não aparece como anomalia. Severidade baixa. Correção mínima: separar `fora` de `ausente` em `ler_registro` e reprovar o `fora` também na dependência. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Análise estática e sondas locais sobre raiz sintética em `$TMPDIR`. Faltaram no PATH, e a lacuna fica registrada: `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint`. O diff não toca workflow, dependência nem segredo.
