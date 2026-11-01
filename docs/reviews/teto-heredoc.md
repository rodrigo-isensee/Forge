---
tipo: review
contrato: 1
pedido: teto-heredoc
branch: melhoria/teto-heredoc
commit: c3192f2fff7438da32036402d88a8add0b5e3021
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: teto-heredoc

Etapa E1.2 (R-REVIEW), revisor em instância diferente da do autor (D-ETAPAS-INST = A). Diff lido: `git diff ce57f2d c3192f2` (base `develop` ce57f2d77e3a9b953a3d06de5b91e171b50e1fd8).

## O que a branch entrega
Item E1 do pedido: o `test_muitos_heredocs_recusam_dentro_do_orcamento` (`tests/test_hooks.py:1795`) deixa a montagem do fixture (git init, config, commit, `pid_morto`) fora da janela medida e passa a cobrar duas coisas sobre a execução do hook: parede só do hook `< limite / 2` (5,0 s) e CPU dos filhos (`RUSAGE_CHILDREN`, usuário + sistema) `< limite / 2`. Sem `resource` (Windows) vale só a parede. Mais o fragmento `changelog.d/teto-heredoc.md`.

## Conferência contra o desenho e a DECISÃO TÉCNICA de 18:21
- Parede só do hook abaixo de 5,0 s: sim (`tests/test_hooks.py:1819`); o cinto de 10 s do desenho foi substituído pelo 5,0 s, como a decisão manda. O mutante `sleep(6)` (A2 do modelo de ameaças) reprova pela parede.
- CPU dos filhos abaixo de 5,0 s: sim (`tests/test_hooks.py:1820-1822`).
- Nenhum teto sobe: `limite` continua lido do `hooks/hooks.json` e dividido por 2; nenhum número novo.
- Equivalência com o caminho antigo: `rodar_dados` (`tests/test_hooks.py:782`) fazia pasta temporária, `caso.json`, `Fixture` e `executar_fixture(..., os.getpid())`; o teste faz o mesmo, só separando `Fixture.montar` e passando `montado=` (parâmetro que já existia em `executar_fixture`). As asserções de código 2, stderr de uma linha e `R-MAIN` seguem as mesmas.
- Na janela, `executar_fixture` só cria `tmp/proc` (sem processo) e roda o hook com `rodar` (um `subprocess.run` esperado): o `RUSAGE_CHILDREN` conta o lançador, o hook e os filhos dele. Um filho de outra thread esperado na janela só somaria CPU (falso vermelho, nunca falso verde).
- Hook, `hooks.json`, `tests/config.json` e caminhos de `PROTEGIDOS` (`tests/catraca.py:43`) não mudam.

## Teto por PR (M14)
`git diff --numstat --no-renames ce57f2d...c3192f2`: `tests/test_hooks.py` 23 + 2 = 25 linhas; `changelog.d/teto-heredoc.md` (2) fica fora. 25 de 150, sem linha de exceção necessária, nenhum arquivo de `hooks/`. Um comportamento só (a medida do orçamento de heredocs). Cumpre a M14.

## Ferramentas (citadas, não refeitas)
- Execução local do teste alvo no head revisado: `Ran 1 test in 4.209s` / `OK` (load de 1 min 1,67).
- Suíte e mutação: pre-push verde do autor (histórico do pedido, 18:58); o mutante que deixa o hook lento de verdade é da E1.4 (QA).
- `shellcheck`: não se aplica (nenhum shell no diff).

## Achados
- A1 (recomendado) tests/test_hooks.py:1809 · as quatro linhas que gravam caso.json e criam a Fixture repetem rodar_dados (linha 782); um auxiliar que devolva (fixture, tmp) e seja usado pelos dois evitaria a duplicação.
- A2 (recomendado) tests/test_hooks.py:1797 · a docstring ainda fala só do prazo do hooks.json; uma frase dizendo que a janela mede a parede só do hook e a CPU dos filhos, sem a montagem, poupa a releitura do corpo.

## Parecer
Aprovado. A branch entrega o item E1 conforme o desenho e a DECISÃO TÉCNICA de 18:21: a parede do hook segue abaixo do mesmo 5,0 s, a CPU dos filhos entra com o mesmo teto e só a montagem sai da janela; nada fica mais frouxo para o tempo do hook. Os dois achados são recomendações e não devolvem. Risco residual: sob carga muito alta, a partida do Python do hook ainda conta na parede; se a instabilidade voltar, o caminho é medir de novo, não subir o teto (fora do escopo, decisão do dono de 2026-10-15). Segurança: parecer próprio do security-engineer (E1.3), não refeito aqui.
