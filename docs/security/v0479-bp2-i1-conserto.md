---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp2-i1-conserto
commit: d816262d85319c97fed47261d3179f485df5bf08
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-bp2-i1-conserto (BP2 I1, `forge-fechar --conserto`, E38.6)

Escopo lido: `git diff 004ce869..d816262d` em `bin/forge-fechar`, `docs/fechamento-integrador.md`, `changelog.d/`, e o que o conserto lê do CI (`.github/workflows/ci.yml`, `scripts/falhas-no-resumo.py`, `scripts/suite-partes.py`, `scripts/suite-paralela.py`). Os testes e mutantes novos (`tests/test_fechar.py`, `tests/mutantes/fechar-conserto*.json`) foram lidos por amostra, sem rodar a suíte (brief: sem baterias).

## Gatilhos
Gatilhos: controle do Forge (portão de merge na develop), afrouxa-regra (R-FLUXO, decisão D5 do dono), CI e fluxo de branches.

## Confirmação pedida pela D5 (por escrito)
**Preso ao commit revisado: confirmado.** O passo 1 confere os pareceres no `sha_conferido`, o passo 2 exige o remoto igual a ele (`bin/forge-fechar:1440`) e o merge sai com `--match-head-commit "$remoto_sha"` (`bin/forge-fechar:830`, chamado na linha 1622), caminho que o `--conserto` não muda. Com a base trazida pelo 2b, o C3 (`bin/forge-fechar:1069-1078`) só aceita o head M com `M^1` igual ao head que o pai conferiu (`FORGE_FECHAR_CONSERTO_H`, `bin/forge-fechar:900`, lido só com a marca do pai), `M^2` igual ao topo do C1 e a árvore igual à do `merge-tree` dos dois: o commit que o próprio script gera. Quem forjar a marca e o `FORGE_FECHAR_CONSERTO_H` no ambiente é o mesmo ator local que já roda o script, e o M ainda passa pelo passo 1 (pareceres) e pelo `--match-head-commit`: não ganha nada além do caminho sem conserto.

**Com a mesma falha declarada: confirmado no vínculo do run, não confirmado na prova de que os testes passaram.** O C1 (`bin/forge-fechar:1052-1059`) prende o run declarado ao evento `push` na develop, ao topo lido do servidor e à conclusão `failure`, e o passo 6 relê o topo antes do merge (`bin/forge-fechar:1620-1621`, antes do merge na linha 1622): o run declarado é o vermelho do topo. Já o C4 trata como "passou no PR" todo teste que não aparece pelo próprio id nos pulados, e há duas formas de ele não ter passado sem aparecer (A1, provado; A2). Enquanto o A1 não for corrigido, a segurança não confirma que o conserto entra com a mesma falha resolvida, só que entra declarando o run certo.

## Achados
- A1 (bloqueante) bin/forge-fechar:1109 · C4 falha aberto: teste pulado por classe (setUpClass) ou por módulo tem nos pulados o id `setUpClass (mod.Classe)` ou `<carregador>.ModuleSkipped.mod`, não o id do teste; o grep não acha e o teste que falhou no run conta como passado no PR (S1).
- A2 (recomendado) bin/forge-fechar:1108 · C4 conta como passado o teste que falhou no run e foi apagado no PR (não aparece nos pulados); o C5 ainda aceita por tocar o arquivo do teste. Exija o método do id no arquivo do módulo no head (git grep no remoto_sha) ou pare.

## Sondas
- S1 · pulados `{"pulados_ids": ["setUpClass (test_m.C)", "unittest.loader.ModuleSkipped.test_n"]}` e ids test_m.C.test_a, test_n.K.test_c no grep de bin/forge-fechar:1109 · espera: pulado (para) · obtido: não achado (segue como passou), nos dois

## Detalhe dos achados
**A1.** Evidência: `bin/forge-fechar:1108-1110` procura só `"<id>"` e `"<id> ("` nos artefatos `pulados-*`. Os ids dos pulados vêm de `t.id()` (`scripts/suite-paralela.py:322`); a sonda S1, rodada com o carregador padrão da stack, deu `['setUpClass (test_m.C)', 'test_m.D.test_b', '<carregador>.ModuleSkipped.test_n']` para um `SkipTest` no `setUpClass`, um decorador de classe e um `SkipTest` no import do módulo: só o decorador de classe gera o id do teste. Caminho de ataque: o agente que escreve o "conserto" pula a classe ou o módulo do teste vermelho em vez de consertar; o CI do PR fica verde (um pulado a mais, dentro do teto), o C4 não acha o id e o C5 aceita (o diff toca o arquivo do teste); o merge entra com a develop vermelha justamente pelo caminho que o C4 existe para fechar. Severidade: média (afrouxa o portão da develop; os pareceres do passo 1 continuam como defesa). Correção mínima: no laço do C4, para cada id `mod.Classe.metodo`, parar também se os pulados tiverem `"setUpClass (mod.Classe)"`, `"tearDownClass (mod.Classe)"`, `"setUpModule (mod)"`, `"tearDownModule (mod)"` ou um id que termine em `.ModuleSkipped.mod`; mais um caso em `tests/test_fechar.py` para cada forma e um mutante que volte ao grep só pelo id. Esforço: P. Dono: tech-lead (autor do I1).

**A2.** Evidência: `bin/forge-fechar:1108` só consulta os pulados; não há leitura de que o id ainda existe no head. Caminho: o conserto apaga o teste vermelho (ou o método); o CI do PR fica verde, o C4 não acha o id nos pulados e o C5 aceita por tocar o arquivo. Os pareceres do passo 1 veriam a remoção, por isso é recomendado. Correção mínima: com o arquivo do teste já calculado em `conserto_arqs`, `git grep -q -w "def <metodo>" "$remoto_sha" -- <arquivo>`; sem achar, parar pedindo a leitura (falha fechada). Esforço: P. Dono: tech-lead.

Conferido sem achado: o número do run, os ids de job e os shas do `git log` são validados por forma antes do uso (`bin/forge-fechar:134`, `1086`, `1101`, `1123`, `1127`); nada lido do GitHub é avaliado pelo shell (o texto das anotações só passa por `sed`, `awk` e `grep -F`); a pasta dos pulados é temporária e apagada em todo caminho; `--conserto` recusa `--lote` e `--armar`; o C7 grava com `--literal` e a pendência sai com `%q`; toda leitura que falha para sem mesclar.

## Riscos aceitos e ferramentas
Sem risco aceito. Risco residual registrado, não achado: entre a releitura do topo no passo 6 e o `gh pr merge --auto` sobra uma janela curta; a develop vermelha para todo outro merge pelo 6b, então só outro conserto caberia nela. O C5 aceita qualquer arquivo mudado desde o último verde: é a D2 do dono ("C1 a C7 como estão"), não achado.
Ferramentas: leitura estática e a sonda S1 local; o analisador de segredos, o de workflows e o lint de shell não estão no PATH desta estação (lacuna, sem instalação, `R-CUSTO`). Suíte: não rodada aqui (brief); o CI do PR é o portão dela.
