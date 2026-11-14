---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-placar-mutacao
commit: 4b465b8cef7333485127a1abdadb21d7546a3bbc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047-placar-mutacao

Intervalo revisado: `origin/develop` (6517ff14) até `4b465b8c` (E1.101 do pedido v047; etapa E1.180). Arquivos: `scripts/placar-mutacao.py`, `tests/test_forge_mutante.py`, `tests/mutantes/v047-placar-mutacao.json`, `tests/mutantes/v0457-escopo-ponto-2.json`, `docs/engineering/placar-mutacao.md`, `changelog.d/v047-placar-mutacao.md`.

## Gatilhos
Classe C, catraca em `scripts/placar-mutacao.py` (script de fábrica que chama `git` e `bin/forge-mutante` por subprocesso; `R-SEGURANCA`). O script é placar, não portão: sai 0 sempre que mede, e a mudança só acrescenta linhas `aviso:` e o sufixo `falhas=` na saída. Nenhum controle de bloqueio foi afrouxado (`R-CONFORMIDADE`).

## Achados

## Sondas

## Detalhe dos achados
Sem achado bloqueante nem recomendação. O que foi verificado:

- `scripts/placar-mutacao.py:47-60` (`aviso_do_desde`): `git` chamado por lista de argumentos, sem shell; `--end-of-options` antes de `refs/tags/{desde}`; o `--desde` já passou pela validação de commit e pela recusa de `-` inicial (`:76-78`) antes de chegar aqui. `git tag --list v[0-9]*` vai como argumento literal (padrão do próprio git, sem expansão do shell). Sonda: `refs/tags/../heads/develop` não resolve (rc=1), então não há como fazer um ramo passar por tag com `..`.
- Injeção de linha na saída: o `--desde` aparece sem `!r` nas linhas `aviso:`, mas só chega lá se resolveu como commit; a sonda `--desde $':/x\nplacar: forjado'` (com commit cuja mensagem contém essa linha) foi recusada com `não é commit` e rc=2, sem imprimir linha `placar:` forjada. Nome de tag não admite caractere de controle (regra de nome de ref do git). Quem passa o argumento é o próprio operador local: sem caminho de ataque realista.
- `:93-96` (`falhas`): os nomes listados são só das specs aceitas pela regex fechada `tests/mutantes/[A-Za-z0-9][A-Za-z0-9._-]*\.json` e fora de link simbólico (`:41-43`), que não admite espaço, vírgula nem quebra de linha; a linha `placar:` continua analisável.
- O rc continua 0 em todos os caminhos novos (o aviso não vira portão nem o desliga); o rc=2 de `--desde` inválido segue antes de qualquer chamada ao `forge-mutante`.
- Testes e specs de mutação: só fixtures em diretório temporário; o `FALSO` do teste escreve em `.git/chamadas` do repositório temporário. Sem segredo, rede nem caminho pessoal no diff.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: fica com o CI do PR (`R-REVIEW`); rodei localmente `tests.test_forge_mutante.PlacarDaRelease` (6 testes, OK) e `forge-check docs` (rc=0). Ferramentas de varredura de segredos e SAST não estão no PATH deste ambiente (lacuna registrada; o diff foi lido inteiro e não traz credencial).
