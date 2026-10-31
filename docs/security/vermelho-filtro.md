---
tipo: revisao-seguranca
contrato: 1
pedido: vermelho-filtro
branch: melhoria/vermelho-filtro
commit: 21a4caa312799f62bfd9e31cb8dd687218c16d59
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-30
---
# Review de segurança: vermelho-filtro

Escopo: `git diff 9e6fa28978d742bbdd47975a34c7e1795919ea70 21a4caa312799f62bfd9e31cb8dd687218c16d59` (commits f20bd58, 5b0e48d, 21a4caa): `bin/forge-testes`, `tests/test_testes_tocados.py`, `tests/mutantes/vermelho-filtro.json`, `changelog.d/vermelho-filtro.md`.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): a prova do vermelho de `forge-testes --vermelho`, que o QA cola no parecer como evidência (`agents/qa-engineer.md:19`). Não toca `hooks/`, `.githooks/`, `.github/`, a Catraca nem caminho de `PROTEGIDOS`.

## Achados

## Detalhe dos achados
Sem achado bloqueante nem recomendação.

O que foi conferido, com evidência:
- **Filtro novo** (`bin/forge-testes:417`): sem `--modulos`, os caminhos que casam `TESTE_DO_DIFF` (`bin/forge-testes:55`: módulos de teste, `tests/config.json` e os dados em `tests/fixtures/`, `tests/hooks/`, `tests/transcricoes/`, `tests/migracoes/`, `tests/mutantes/`) saem do `planejar`, salvo os de `ALTERA_O_MAPA` (`bin/forge-testes:126`). `tests/config.json` continua levando à suíte completa; `bin/forge-testes` nunca casou `TESTE_DO_DIFF` e segue no `planejar`. Os dados de teste ficam no HEAD nas duas cópias (`mantidos`, `bin/forge-testes:402`; só `producao` volta à base, `bin/forge-testes:227`), então não mudam o resultado base contra HEAD: tirá-los do plano não esconde prova nem cria prova falsa.
- **Falha fechada preservada:** diff só de dados de teste dá plano dirigido vazio, nenhum módulo roda e a saída é código 1 com "nenhum teste prova a mudança" (`bin/forge-testes:470`), não um verde. Caminho sem mapa, módulo ausente e `ALTERA_O_MAPA` continuam levando à suíte completa (`bin/forge-testes:160`), agora com a linha de motivo (`bin/forge-testes:419`).
- **Superfície de ataque:** o `--vermelho` é evidência, não portão; nenhum consumidor em `hooks/`, `.githooks/`, `.github/`, `bin/forge-fechar` nem na Catraca lê a sua saída. Quem poderia abusar do filtro é o próprio autor do diff, e o máximo que ganharia é uma evidência mais curta que o QA e o CI (suíte completa) conferem de novo. A linha nova imprime nomes de caminho do diff, que já eram impressos em "revertidos à base"; nenhuma entrada nova.
- **Testes e mutantes:** módulo `tests.test_testes_tocados` com 85 testes OK; `bin/forge-mutante tests/mutantes/vermelho-filtro.json` com M1 a M4 mortos (`bin/forge-testes:417`, `:417`, `:419`, `:418`); `bin/forge-mutante --cobertura --base 9e6fa28` dá as condições mudadas (`:417`, `:418`) como cobertas. A guarda de `--modulos` (sem mudança) tem teste próprio.
- **M14** (`agents/tech-lead.md:19`): cumpre. `git diff --numstat --no-renames` contra a base: `bin/forge-testes` 7+2 e `tests/test_testes_tocados.py` 42+0, 51 linhas contadas (fora a spec em `tests/mutantes/` e o fragmento em `changelog.d/`); um comportamento só; nada em `hooks/` nem em `PROTEGIDOS`.
- **Segredos:** nenhum segredo nem credencial no diff (leitura e busca por padrão no diff inteiro).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, a suíte do módulo tocado, `bin/forge-mutante` (spec e `--cobertura`). Lacuna: `gitleaks` e Semgrep não estão no PATH deste ambiente; o diff é pequeno e foi lido por inteiro.
