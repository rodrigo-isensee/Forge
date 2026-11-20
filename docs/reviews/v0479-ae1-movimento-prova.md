---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae1-movimento-prova
commit: 8bdb976e63e52fb1deaba33e99999f86bc373595
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E58.26 (AE1.2, movimento para Pronto ou Fechado exige prova; E58.24 no forge-fechar)

Diff revisado: `ed5bfa02..8bdb976e` (2 commits: 64c1d555 E58.19, 8bdb976e E58.24). Código: `bin/forge-check` (`cmd_movimento`, `--prova`), `bin/forge_onde.py` (`prova_do_movimento`, `prova_git`, `citacao`), `bin/forge-fechar` (`prova_cartao`); uso em `skills/kanban-scrum/SKILL.md`; fragmento de changelog; 5 specs de mutante (35 mutantes); testes em `tests/test_forge_onde.py`, `tests/test_sobreposicao_quadro.py`, `tests/test_fechar_move_cartao.py`.

## Ferramenta (citada, sem refazer)
- Módulos do item: `python3 -m unittest tests.test_forge_onde tests.test_fechar_move_cartao tests.test_sobreposicao_quadro tests.test_orcamento_instrucao`: 134 testes, OK.
- `bin/forge-testes --listar --base ed5bfa02`: `suíte completa (tests/test_fechar_move_cartao.py sem mapa)`; a escolha por módulo não cobre o diff, e um módulo vizinho cai (A1).
- Orçamento de instrução do Jarvis (`tests/test_orcamento_instrucao.py`, medido nesta árvore): total 40566 de teto 40566 (base ed5bfa02: 40530; +36 da linha nova da `kanban-scrum`).
- Suíte inteira: fica com o CI do PR (`R-REVIEW`); sem PR nesta etapa.

## Leitura
- `cmd_movimento`: `--prova` só e sempre com Pronto ou Fechado*; recusa não grava; `nao-verificavel` grava em "Aguardando sua validação" e sai com rc 1, sem a coluna nada grava. Bate com o desenho (`docs/propostas/v0479-melhorias-anti-erro.md:145` e a reversão da linha 237).
- `prova_git`: PR exige `estado=MERGED base=develop` e a develop com o commit; `citacao` reusa a regra do ID inteiro do AE1.1. `rodar:` recusa slug fora da forma e link simbólico; `juntado:` recusa o próprio cartão e cartão em coluna final. Casos de borda do desenho cobertos por teste de comportamento.
- Mutantes: um por guarda, nenhum lendo texto da fonte.
- Commits em Conventional Commits em português; fragmento presente.

## Achados
- A1 (bloqueante) tests/test_fechar_forge_check_real.py:123 · Regressão: com o forge-check real, forge-fechar --cartao K-1 sai com 3 e "não movi o cartão K-1"; na base ed5bfa02 o mesmo teste passa. O pr:#7 não se confere (gh do PATH sem a leitura do PR e PR sem o ID). Corrigir e rodar este módulo.
- A2 (recomendado) bin/forge-fechar:284 · O PR que o forge-fechar abre não cita os --cartao (título = branch, corpo sem o ID): no uso real o pr:#N é recusado e todo --cartao vira pendência. Escrever `Cartão: <ID>` no corpo quando houver --cartao (o AE2 prevê esse formato).
- A3 (recomendado) docs/fechamento-integrador.md:28 · O comando documentado do --cartao segue sem --prova; atualizar para `--prova pr:#<n>` (ou `commit:<head>` com o head já na base) e citar a recusa quando o PR não cita o cartão.

## Sondas
- S1 · python3 -m unittest tests.test_fechar_forge_check_real (head 8bdb976e) · espera: OK, como na base ed5bfa02 · obtido: FAILED (failures=1), MoverCartaoComOForgeCheckReal: AssertionError 3 != 0, aviso: não movi o cartão K-1 para Pronto ... --prova pr:#7

## Integração com o AE1.4 (orçamento do Jarvis)
O AE1.2 deixa o total do Jarvis em 40566, igual ao teto (`docs/regras/orcamento.json`). O AE1.4 (`melhoria/v0479-ae1-medida-afirmacao`, head d2a83789) mede 40558 sozinho (+28 em `agents/jarvis.md`). Juntos, medidos nesta revisão (árvore do AE1.4 com a `kanban-scrum` deste head): 40594, 28 acima do teto; `tests/test_orcamento_instrucao.py` reprova. Quem integrar por último: depois do merge da develop, rode `python3 -m unittest tests.test_orcamento_instrucao` e corte pelo menos 28 caracteres do que o Jarvis carrega (por exemplo, a frase nova da `kanban-scrum` pode ir para o `--help` do `movimento`, que já a diz); subir o teto é afrouxar e pede o dono.

## Parecer
Reprovado por A1: o complemento E58.24 deixa vermelho o teste do forge-fechar com o forge-check real, o mesmo caso que ele dizia consertar. O núcleo do AE1.2 (forge-check e forge_onde) está correto e bem coberto. A2 e A3 não bloqueiam; A2 é a causa provável no uso real e cabe na mesma volta se o autor quiser.
