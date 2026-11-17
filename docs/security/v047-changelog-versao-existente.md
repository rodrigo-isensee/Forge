---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-changelog-versao-existente
commit: 9bf1fa1c63159c0e393ec44723d0e23c8b61ca91
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047 (lote CH1, CHANGELOG-RELEASE-VERSAO-EXISTENTE)

Etapa E2.94. Diff `bf475209..9bf1fa1c`: `bin/forge-changelog` (só o texto da recusa de versão já existente), fragmento em `changelog.d/`, spec de mutantes e dois testes em `tests/test_changelog.py`.

## Gatilhos
`R-SEGURANCA`: `bin/forge-changelog` é sensível da catraca (grava `CHANGELOG.md` e os manifestos de versão na release). A mudança não altera a decisão: a mesma condição recusa, antes de qualquer gravação, e só o texto da saída muda.

Verificado:
- A recusa continua antes de `ler_manifestos`/`gravar_versao`; o teste novo prova `CHANGELOG.md`, `plugin.json` e o fragmento intactos e rc=1.
- `args.versao` entra na mensagem só depois de `re.fullmatch(r"\d+\.\d+\.\d+")` (`bin/forge-changelog:177`): sem caractere de controle nem injeção de terminal na saída.
- Versão vizinha (0.1.1 com 0.1.0 no arquivo) não é recusada (teste novo; o `re.escape` com âncora `\]` segue).
- Mutantes CV-M1 e CV-M2 cobrem a guarda e o texto.

## Achados
- A1 (recomendado) bin/forge-changelog:190 · A recusa manda rodar `release --anexar`, que não existe neste head nem na develop (vem de melhoria/v047-changelog-anexar, ainda fora); quem segue a dica recebe erro de uso. Mesclar a branch do --anexar antes desta, ou condicionar o texto. Sem efeito de segurança.

## Sondas

## Detalhe dos achados
A1 · evidência: `bin/forge-changelog:190`; `grep anexar bin/forge-changelog` só acha a mensagem, o subcomando `release` (`bin/forge-changelog:337-340`) tem só `versao` e `data`; `python3 bin/forge-changelog release --anexar 0.1.0` sai com erro de uso do analisador de argumentos e nada grava. · caminho de ataque: nenhum (o comando sugerido falha fechado) · severidade: informativa · correção mínima: ordem de merge (melhoria/v047-changelog-anexar primeiro) ou texto sem o subcomando até lá · esforço: P · dono: tech-lead.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Rodado: `tests.test_changelog.Release` (24 testes, OK) neste head. A suíte inteira fica com o CI do PR. Ferramentas de segredo e SAST não estão no PATH (lacuna registrada); o diff não traz credencial nem dado pessoal (lido à mão).
