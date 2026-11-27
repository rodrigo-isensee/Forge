---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.20
branch: melhoria/v0481-release-0-47-20-pareceres
commit: 779356dcee5f1c840e328dc6efbd3fa9275e8d77
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: release 0.47.20 (leva contra a main), revalidação por delta no head 779356dc

Etapa E1.9 do pedido release-0.47.20. A rodada anterior (head `1e301536`, 23 itens, `so-aperta` nos hooks, tabelas de afrouxamento) fica no git, no squash `447b4ad2` (#935). Esta rodada lê só o delta `8855671d..779356dc`: #937 (`eba76f80`), #936 (`50e5b609`), a marca (`447b4ad2`, #935) e o anexo (`779356dc`, #939). As conclusões da rodada anterior valem para o resto da leva.

## Gatilhos
Gatilhos: hook de conformidade com guarda afrouxada (#936), controles do Forge e autorização do parecer como status (#937, `bin/forge_pareceres.py`), release usada por todos os projetos.

## Achados
- A1 (recomendado) CHANGELOG.md:32 · A entrada do #930 na seção 0.47.20 ainda diz que o hook barra o texto de interpretador e o destino em variável na raiz do Forge. O #936 tirou essa guarda (linha 36). As notas da main prometem uma guarda que não existe mais.

## Detalhe dos achados
**A1.** Evidência: `CHANGELOG.md:32` ("o texto de interpretador (`python3 -c`, `node -e`, heredoc) ... também pelo destino em variável") e `CHANGELOG.md:36` (o #936: "a grafia do Bash ... fica com o sandbox do SO"). Caminho: quem lê as notas da 0.47.20 confia numa guarda do hook que saiu, e numa estação sem o `denyWrite` (A18 de `docs/security/v0481-hook-raiz-forge.md`) a escrita por variável ou interpretador na raiz passa. Severidade: baixa. A falha é de documentação e não abre caminho novo. Correção mínima: reescrever a linha 32 com o escopo final (Write, Edit, MultiEdit e o caminho literal no Bash; a grafia fica com o `denyWrite`) ou juntar as linhas 32 e 36 numa só. Esforço P. Dono: `tech-lead`, o autor do anexo, antes do PR da main.

## Delta lido
**Junção.** Busquei `refs/pull/<n>/head` dos PRs. `git merge-tree --write-tree <pai da squash> <head do PR>` dá árvore igual à squash, com 0 arquivos de diferença, no #937, no #936, no #935 e no #939. O `commit:` de cada parecer de segurança dos itens é ancestral do head do PR, e o código nele é o do head, sem diferença fora de `docs/`:
- #937: `v0481-f1p2-c1a`, `c31462e6`;
- #936: `v0481-encolhe-930`, `27641d2a`.

O head do #935 difere de `1e301536` (o head da rodada anterior) só nos quatro pareceres da release. A árvore do head do #939 (`f61936bf`) é igual à de `779356dc` (`55e6a11c`).

**#936 (encolher o #930).** Saem do hook a leitura da grafia do Bash na raiz do Forge (destino em variável, colagem, texto de interpretador), 19 fixtures `raiz-forge-*`, as specs `v0481-hook-raiz-forge-4` e `-5` e mutantes das specs `v0481-hook-raiz-forge`, `-2` e `-3`. O erro interno passa a fechar só no Write, no Edit, no MultiEdit e no NotebookEdit. Ficam o Write, o Edit e o caminho literal no Bash. `docs/hooks.md:69` registra o limite: a estação sem o `denyWrite` dessas entradas fica sem a guarda da grafia. O parecer do item mostra, com a mesma entrada na base e no head, que só mudaram as grafias que saíram por decisão. Neste head, `tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge` e `tests.test_forge_pareceres` passam: 88 testes, OK.

**#937 (F1 parte 2, C1a).** A conta aceita estreita de "a conta da sessão" para "a dona do `origin`". O `publicar` grava um registro de cada publicação, e o `ler` recusa status sem esse registro, sempre com falha fechada. A spec `tests/mutantes/v0481-f1-parecer-fora-3.json` saiu inteira:
- M18 e M19 saem com o parâmetro `contas`;
- M17 (`if dela:`, `bin/forge_pareceres.py:220`) e M20 (a `Recusa` de `:223`) perdem a declaração, mas o código delas segue igual. Rodei os dois contra este head com os testes declarados da base, e os dois morreram.

Logo a retirada não abre furo. Os 4 testes com o valor esperado trocado provam a mesma propriedade pela conta da base, e o login vazio passa a ser recusado também no `publicar` e no `agregado`. Seguem abertos como cartões os A1 e A2 do parecer do item:
- A1: a regra `quem: []` de `~/.forge-contrib/.forge/run/` é pré-requisito do C2a;
- A2: a lista M1.4 da base fica para antes do D5.

Hoje nenhum dos dois é explorável, porque o `ler` não tem chamador.

**Marca e anexo.** A marca toca só os dois `plugin.json`, o `CHANGELOG.md`, os pareceres da release e 22 fragmentos apagados. O anexo toca só o `CHANGELOG.md` e apaga `changelog.d/v0481-encolhe-930.md` e `changelog.d/v0481-f1p2-c1a.md`. As duas linhas desses fragmentos estão no `CHANGELOG.md`, letra a letra, e nenhuma linha sai. A versão é `0.47.20` nos dois manifestos, e a `origin/main` está em `0.47.19`. `bin/forge-changelog conferir-release` dá `ok`. Nas linhas acrescentadas de `origin/main..779356dc`, a busca pelos padrões de token, chave e chave privada dá 0.

**Medida dos hooks.** `bin/forge-check comparar v0.47.19 779356dc` dá `so-aperta`, com `casos=239 aceites-novos=0` (merge-pr, push-forcado e sem-verificar, 8 casos cada). A medida não cobre a família da raiz do Forge, e por isso o #936 entra pela catraca, não por ela.

## Regras afrouxadas: o que muda na lista do PR da main
**O #936 entra na tabela "Afrouxa, com a marca no título"**, que passa de 7 para 8 linhas:

| Item | O que afrouxa (motivo) | Aceite do dono | Rótulo `afrouxa-regra` |
|---|---|---|---|
| #936 | HOOK-NAO-PROTEGE-RAIZ-DO-FORGE (do #930): sai a guarda da grafia do Bash na raiz do Forge (variável, colagem, interpretador) e o erro interno do Bash, com 19 fixtures, 2 specs de mutantes apagadas e 3 encolhidas. Ficam o Write, o Edit e o caminho literal. A grafia fica com o `denyWrite` do sandbox, e o limite fica em `docs/hooks.md:69`. O pedido de origem é o v0481 (E37.26 e E46.1) | ORDEM 27/11 10:08 ("depois o encolhimento do #930") | 27/11 15:11:59Z (posto 13:26Z, tirado 15:11:51Z, reposto) |

**O #937 não afrouxa.** O rótulo `afrouxa-regra` (27/11 15:12:02Z) vem só de ele tocar arquivo protegido (catraca, valores esperados trocados). A conta aceita fica mais estreita, o registro é exigência nova, e a spec retirada não perde guarda (M17 e M20 morrem). Ele entra em "Aperta ou neutro", que passa a ter 13 itens.

As outras linhas das tabelas e os pontos "Para o dono" da rodada anterior seguem iguais. O corpo do PR da main precisa trazer a tabela com o #936. Segue em aberto o cartão do R3 (`scripts/promover-homolog.py:222` não monta a lista). **Para o dono, a mais:** o A18 de `docs/security/v0481-hook-raiz-forge.md` segue aberto. Depois do #936, a guarda da grafia na raiz depende só do `denyWrite`, que hoje está em `.claude/settings.local.json` (não versionado), e não em `.claude/settings.json`.

## Riscos aceitos e ferramentas
Não há risco aceito novo, e o delta não toca `docs/security/aceites/`. Rodei localmente, só para leitura e medida:
- as junções;
- `comparar` e `conferir-release`;
- os dois mutantes retirados (M17 e M20), de uma spec em pasta temporária;
- os testes afetados;
- a busca de segredos por padrões;
- as leituras no GitHub (PRs, rótulos e check-runs).

A suíte inteira vale pelo CI do PR #939, no head `f61936bf`, de árvore igual a `779356dc` (run 46027786545). Estão verdes:
- `suíte (python 3.12)` partes 1 a 5;
- `bateria`, `bateria (pareceres)`, `bateria (passos)`, `bateria (verificações longas)` e `bateria (python 3.14)`;
- `instalação (python 3.14)`, `teto de pulados` e `árvore já provada na develop`;
- `catraca` (run 46027786397) e `cancela runs obsoletos do PR`.

No push da develop (`779356dc`), `árvore do PR já provada` e `checagem rápida` estão verdes. Lacuna: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint` e `trivy` estão fora do PATH, e o delta não toca workflow nem dependência.
