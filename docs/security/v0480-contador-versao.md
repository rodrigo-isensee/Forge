---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-contador-versao
commit: fb4d5390b925256caa28286bef2f997d8af66489
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E103.4, CONTADOR-DA-VERSAO)

Escopo: `900bfdfe..fb4d5390` (8 arquivos: `bin/forge-contador`, `tests/test_forge_contador.py`, três specs de mutantes, `tests/pesos-d4.json`, a linha da skill `fluxo-do-pedido` e o fragmento do changelog).

## Gatilhos
Gatilhos: nenhum (sem autenticação, segredo, dependência, rede, CI, banco nem controle do Forge; `tests/pesos-d4.json` não é caminho protegido).

## Achados

## Sondas

## Detalhe dos achados
Sem achado de segurança. O que foi conferido:

- **Execução de processo:** `bin/forge-contador:31-35` e `:40` chamam o git por lista de argumentos, sem shell; não há `eval`, `exec` nem interpolação em comando. Os subcomandos são só leitura (`rev-parse`, `show <ref>:<caminho>`, `ls-tree`, `tag --merged --list`); nenhum escreve no repositório nem fala com remoto.
- **Injeção de opção pelo `--ref`:** `--ref=--output=<dir>/x` cai em `git tag --merged`, que recusa o nome malformado (sai 2, nenhum arquivo criado; reproduzido). O argv é de quem roda a ferramenta, a mesma pessoa ou agente que já executa git; sem fronteira de confiança, não há caminho de ataque. Endurecimento opcional (sem bloqueio): validar o ref com `rev-parse --verify` antes de usá-lo, como `ref_padrao` já faz.
- **Entradas de arquivo:** `.forge/config.json`, o quadro e o histórico são do próprio projeto; `teto_versao` aceita só inteiro positivo (`:71`, rejeita `true`); a versão passa pela expressão ancorada `VERSAO` (`:24`, `:52`). A saída imprime só números, a versão validada e os nomes de coluna do quadro do próprio projeto.
- **Sem rede:** nenhum módulo de rede importado; o git só lê objetos locais (num clone parcial, um blob faltante dispararia busca preguiçosa no remoto; não é o caso das cópias do Forge, fica como observação).
- **Robustez (domínio do review e do QA, não segurança):** `--data 9999-12-31` com vazão positiva dá `OverflowError` e quadro com byte não UTF-8 dá `UnicodeDecodeError`, ambos traceback com saída 1 em vez da 2 do contrato (`:112`, `:118`). Sem impacto de segurança; repassado ao `tech-lead` e ao `qa-engineer`.
- **Teste:** `tests/test_forge_contador.py` usa diretório temporário, ambiente git limpo (`GIT_*` removidos) e modo isolado do interpretador; sem rede. Rodado localmente o teste novo: 16 testes, OK. A suíte inteira fica no CI.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática do diff e sondas locais na cópia; o varredor de segredos não está no PATH desta estação (lacuna registrada, sem instalação); o diff não traz credencial nem padrão de segredo à leitura.
