---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/doutor-f8-caminho
commit: c5eb2465b09751cc80ea316d131844960cd95f36
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Code review: melhoria/doutor-f8-caminho (N-DOUTOR-F8-CAMINHO)

Escopo: `b45e40a...85c5b80`, um commit (85c5b80) com `bin/forge-doutor`, `tests/test_doutor_protecao_gh.py` e `changelog.d/doutor-f8-caminho.md`. É a parte do F8 que saiu de `melhoria/doutor-034` pelo A1 do parecer `docs/reviews/doutor-034.md` (rodada 1, 4bfc92e). O texto do aviso já tinha sido lido lá. Aqui é novo só o A2 daquele parecer, a escolha do arquivo citado. `85c5b80` parte de b45e40a e não contém o 5bd8bdc (`git merge-base --is-ancestor` falso).

## Teto e comportamentos (M14)
`git diff --numstat --no-renames b45e40a...85c5b80`: `bin/forge-doutor` 4 e `tests/test_doutor_protecao_gh.py` 12, 16 linhas contadas (o fragmento fica fora). Um comportamento só, e nada em `hooks/`.

## Correção
`bin/forge-doutor:378`: `guia` cita o primeiro passo a passo que existe na raiz do projeto. A ordem é `docs/engineering/protecao-de-branch.md` (o que o `forge-init` cria desde o N-TPL-a) e depois `docs/protecao-de-branch.md` (o do clone do Forge). Sem nenhum dos dois, cita só a skill `ci-cd`, como antes. O A2 da rodada 1 do doutor-034 está resolvido. O cálculo sai uma vez, fora do laço dos ramos, e a mensagem continua citando `ci-cd` nos três casos. `is_file()` só decide que texto sai: nenhum conteúdo do arquivo é lido.

## Testes
- `python3 -I -m unittest discover -s tests -p test_doutor_protecao_gh.py` no HEAD 85c5b80: 15 testes, OK.
- O teste reprova sem a mudança. Com `bin/forge-doutor` da base b45e40a e os testes do HEAD, `test_o_aviso_cita_o_passo_a_passo_so_se_o_arquivo_existe_na_raiz` falha nos dois subtestes. Com o `bin/forge-doutor` da rodada 1 (9db3c4b, caminho fixo), falham o `assertNotIn` novo de `test_main_sem_protecao_vira_problema_que_cita_a_branch_e_a_skill_ci_cd` (projeto sem o arquivo) e o subteste `docs/protecao-de-branch.md`. Os dois sentidos estão cobertos. Depois da prova, o arquivo voltou ao HEAD (`git status` limpo).
- Ferramentas: não há shell no diff. Não veio spec de mutação, mas as duas provas acima matam as mutações óbvias (caminho fixo, sem o caminho, uma das duas entradas da lista). Não abro achado por isso.

## Revalidação (rodada 2, teste do QA, c5eb246)
Delta lido: só `tests/test_qa_doutor_f8.py` (85 linhas, novo no c5eb246). Os pareceres em `docs/` ficam fora. `bin/forge-doutor` e `tests/test_doutor_protecao_gh.py` são os mesmos de 85c5b80 (já lidos).

- Teto (M14): `bin/forge-doutor` 4, `tests/test_doutor_protecao_gh.py` 12 e `tests/test_qa_doutor_f8.py` 85, 101 linhas. Um comportamento, nada em `hooks/`.
- Leitura: roda o `bin/forge-doutor` completo, com o `gh` falso da classe `Protecao` (rota exata da API de proteção, já lida na rodada 1). Cobre nenhum arquivo, cada caminho sozinho, a precedência do de `docs/engineering`, diretório e link pendente com o nome (`is_file` falso), as três branches citando o guia e o silêncio com as branches protegidas.
- `python3 -I -m unittest discover -s tests -p test_qa_doutor_f8.py`: 7 testes, OK. Com `bin/forge-doutor` de b45e40a, 4 de 7 caem: os que exigem o caminho. Os de só a skill, borda e silêncio são guardas e passam na base. Arquivo restaurado (`git status` limpo).

## Achados
- A1 (recomendado) bin/forge-doutor:378 · a linha do `guia` passa de 135 colunas; quebrar a tupla de caminhos numa constante (por exemplo, PASSO_A_PASSO_PROTECAO) deixa o texto e a ordem legíveis

## Parecer
Aprovado. Faz o que o cartão pede, mais o recomendado A2 da rodada 1 do doutor-034. Os testes reprovam sem a mudança nos dois sentidos, e o PR tem 16 linhas e um comportamento só. O A1 é de forma e não devolve. Não toca `hooks/`. O parecer de segurança do F8 fica com o `security-engineer`, se o Jarvis o pedir (mensagem de um script, gatilho leve no cartão).
