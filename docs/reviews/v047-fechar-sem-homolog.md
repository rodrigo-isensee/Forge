---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-fechar-sem-homolog
commit: e3e38dc8f2716cce938fee31019f87ae37703de8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (FE1, FECHAR-SEM-HOMOLOG-LOCAL), etapa E2.122

Parecer completo (não havia parecer anterior nesta branch), no head e3e38dc8 sobre a base bf475209. Revisor: instância que não fez a entrega.

## Escopo lido
- `bin/forge-fechar`: passo 1c busca só `refs/heads/homolog` quando a `origin/homolog` falta no clone (busca que falha avisa e o `promover-homolog` decide); passo 2 com a branch remota ausente e o head conferido já em `$alvo` (na base, ou PR MERGED do próprio repositório com a mesma base e o mesmo head) segue sem pedir push. Remota com outro head continua parando (guarda `-z`).
- `tests/test_fechar.py`: 7 testes novos, com o ramo de falha de cada guarda (sem PR, PR aberto, de fork, outra base, outro head; busca que falha com promover 1 e 0; remota com outro head).
- `tests/mutantes/v047-fechar-sem-homolog.json`: 8 mutantes, um por linha de guarda mudada (821, 822, 832, 835 x4 condições, 1175). Conferi a lista das guardas à mão: o `--cobertura` não analisa shell (`não coberto: bin/forge-fechar`, como documentado).
- Entregar: FECHAR-SEM-HOMOLOG-LOCAL no e3e38dc8; TESTE-FECHAR-L5-CORRIDA sem commit nesta branch, registrado no histórico como já resolvido no 32f1628a, que é ancestral da base (conferido com `git merge-base --is-ancestor`). Sem item pendente.
- Tamanho (M14): 115 linhas de código e teste (`bin/` 22, `tests/test_fechar.py` 93); dentro do teto, um comportamento (fechamento sem estado local).
- Achados recorrentes (PA-7): AR-1 e AR-2 conferidos (lista completa, ramo de falha testado); AR-6 (máscara do shell): o `|| echo` da busca é intencional e documentado, e o `ler | awk` do `ja_no_alvo` falha fechado (leitura que falha conta como não mesclado); AR-4: os testes usam o `self.env` já limpo do setUp. Sem classe repetida neste diff.
- Regras: R-FLUXO e R-MAIN preservadas (só dispensa o push quando o merge já está provado pelo sha exato); R-VERIFY sem força. Checklist 12: o falso do `gh pr list` não filtra por `--head`, mas o script não depende do nome: exige `headRefOid` igual ao sha conferido e `isCrossRepository` diferente de true, e os testes cobrem os dois.

## Ferramentas (saída citada)
- Testes do item: `python3 -m unittest tests.test_fechar -k ...` (os 7 novos) · `Ran 7 tests ... OK`.
- Mutação dirigida: `bin/forge-mutante tests/mutantes/v047-fechar-sem-homolog.json --base bf475209 --processos 1` · FH-M1 a FH-M8 `morreu`, rc=0.
- `shellcheck bin/forge-fechar` · rc=0.
- Suíte inteira: fica no CI do PR (não rerrodada aqui).

## Achados
- A1 (recomendado) bin/forge-fechar:821 · o git fetch da homolog no 1c não tem prazo, e o 1c limita o promover a 300 s; rede presa trava o fechamento antes do prazo. Sugestão: timeout no fetch, com o mesmo aviso no rc 124.
- A2 (recomendado) bin/forge-fechar:814 · o comentário do promovivel ainda diz "(só leitura)", mas agora ele pode escrever refs/remotes/origin/homolog; ajuste o texto para não contradizer a linha 816.

## Sondas

## Parecer
Aprovado. Os dois comportamentos fazem o que o item FECHAR-SEM-HOMOLOG-LOCAL pede: o 1c deixa de falhar só por clone sem a homolog, e o passo 2 não pede push de branch que o GitHub apagou depois do merge provado pelo sha exato. Todas as guardas novas têm mutante morto e teste do ramo de falha. Os dois achados são recomendados e não devolvem.
