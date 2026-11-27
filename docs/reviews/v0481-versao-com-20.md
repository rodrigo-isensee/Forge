---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-versao-com-20
commit: b19c7f53a1a564059901a406a0e7ddf74ae63b24
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481

Code review por delta (E36.6) da volta 1 do #928. Delta lido: `forge-check parecer delta docs/reviews/v0481-versao-com-20.md`, intervalo `6e77f72a..b19c7f53`, 11 arquivos no domínio (`agents/tech-lead.md`, `bin/forge_autorizacao.py`, ADR 0018, `skills/falar-com-o-dono/nao-trava.md`, `templates/projeto/CLAUDE.md`, `tests/config.json`, os dois `tests/mutantes/v0481-autorizacoes-fixas*.json`, `tests/test_autorizacao.py`, `tests/test_autorizacao_gravar.py`, `tests/test_fechar_corte.py`). A reprovação do QA e da segurança (M6 sobrevivente; textos com "até 2 por dia") é do domínio deles; aqui, o código e os testes do delta.

- ci: b19c7f53a1a564059901a406a0e7ddf74ae63b24 verde

## Achados
- A1 (recomendado) tests/config.json:849 · O delta troca o invariante de `templates/projeto/CLAUDE.md` (linha 656), mas o motivo em `invariantes_motivo_trecho` segue com a chave do texto velho ("até 2 por dia"), que não casa mais com invariante nenhum; o `problemas_de_motivo` só conta trechos. Trocar a chave e o `porque` pelo texto novo.

## Parecer
Aprovado no meu domínio; o A1 vira cartão depois do merge, junto do A4 da 1.ª rodada (`--promover` conferir `N de 20`).

- **Recomendados da 1.ª rodada.** A1: a ADR 0018 (R1, linha 209) compara com o `--ato so-aperta-com-seguranca` e cita a Retirada. A2: as guardas de M7 e M8 falam do ato sem prazo, sem o corte. A3: `cmd_corte` virou `cmd_ler_ato`, com a chamada de `executar` e o M9 acompanhando; nenhum `cmd_corte` sobra na árvore. Resolvidos.
- **M6 (A1 do QA e da segurança).** O teste troca a frase por "pode mesclar a main 0.47.3, o time decide": `time` e `decide` só existem no `VOCABULARIO_FIXO`, e o teste afirma isso nos dois vocabulários antes de gravar, então a troca `if True` do M6 faz a frase nascer sem pendência. Rodei na fila (`flock trava-teste-a`): `M6 · morreu · bin/forge_autorizacao.py:378`; M7, M8 e M9 também morrem (M7 por erro do teste declarado, que conta como morto).
- **Textos (A2 do QA).** `agents/tech-lead.md`, `nao-trava.md` e `templates/projeto/CLAUDE.md` dizem "20 itens, sem versão por dia"; o invariante de `tests/config.json:656` acompanha o modelo, e `grep` em `agents/`, `skills/`, `templates/`, `bin/`, `hooks/` e `scripts/` não acha mais "2 por dia". O invariante novo aperta (diz o teto), não afrouxa.
- **Testes.** `python3 -m unittest tests.test_autorizacao tests.test_autorizacao_gravar tests.test_fechar_corte`: 101 testes OK; `tests.test_forge -k invariante`: OK. As linhas de sonda nos testes são comentário e docstring, sem efeito.
- **Tamanho (H1).** Código fora testes e documentação: 2 linhas em `bin/` (renome).
- **CI.** `gh api .../commits/b19c7f53/check-runs`: suíte (3.12 e 3.14, 5 partes cada), bateria (python 3.14), bateria (passos), bateria (verificações longas), instalação (python 3.14), teto de pulados e "árvore já provada na develop" em `success`; `bateria`, `bateria (pareceres)` e `catraca` esperam os pareceres (G3).
- **Commits.** Três commits em Conventional Commits em português, com pedido e etapa.
