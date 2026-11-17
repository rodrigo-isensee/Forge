---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-changelog-versao-existente
commit: 65858294a2fdcf877bde823a2589fdbaf2009dba
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (lote CH1, CHANGELOG-RELEASE-VERSAO-EXISTENTE)

Etapa E2.544 (revalidação por delta no head 65858294, depois da atualização com a develop). Parecer anterior: E2.94, commit 9bf1fa1c. O delta de domínio desde então é só `bin/forge-changelog`, e o que veio da base (`release --anexar`, vindo da develop) não é delta do item. O item, contra a develop, tem 26 linhas: 6 em `bin/forge-changelog` (texto da recusa) e 20 em `tests/test_changelog.py`.

## Gatilhos
`R-SEGURANCA`: `bin/forge-changelog` é sensível da catraca (grava `CHANGELOG.md` e os manifestos de versão na release). A mudança não altera a decisão: a mesma condição recusa, antes de qualquer gravação, e só o texto da saída muda.

Verificado no head:
- A recusa de versão já existente (`bin/forge-changelog:195`) continua antes de `ler_manifestos`/`gravar_versao`; o teste do item prova `CHANGELOG.md`, `plugin.json` e o fragmento intactos e rc=1.
- `args.versao` entra na mensagem só depois de `re.fullmatch(r"\d+\.\d+\.\d+")` (`bin/forge-changelog:188`): sem caractere de controle nem injeção de terminal na saída. A busca usa `re.escape` com âncora `\]`.
- O `--anexar` da base é recusado com `release <versão> <data>` junto (`bin/forge-changelog:182-183`), valida a versão e o caminho (`conferir_caminho`) e só grava `CHANGELOG.md`; a dica da recusa agora aponta para um subcomando que existe.

## Achados

## Sondas

## Detalhe dos achados
O A1 do parecer anterior (dica de `--anexar` inexistente) está resolvido: o subcomando existe na base e neste head (`grep anexar bin/forge-changelog`, linhas 8, 181-187, 396). Nenhum achado novo.

Sem achados abertos.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Rodado neste head, depois do merge da develop: `python3 -m unittest tests.test_changelog` (89 testes, OK). A suíte inteira fica com o CI do PR. Ferramentas de segredo e SAST não estão no PATH (lacuna registrada); o diff não traz credencial nem dado pessoal (lido à mão).
