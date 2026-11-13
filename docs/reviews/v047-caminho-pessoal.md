---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-caminho-pessoal
commit: 700913201442a8d57dd0e021ca72d3944b7fa63f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047 (E5.4, caminho pessoal)

## Achados
- A1 (recomendado) scripts/verificar-contribuicao.sh:55 · a troca do home do runner por `@` age em qualquer posição: um caminho cujo nome de usuário é `home`, seguido de `runner/`, perde o trecho pessoal e passa; ancorar a troca (início de linha ou caractere que não é de nome antes de `/home`).

## Sondas

## Parecer
Aprovado no head 70091320 (classe C). O diff tem 4 arquivos e 2 linhas de código no script (comentário e a guarda da linha 55), um teste novo e a spec de 3 mutantes.

- Escopo: a base 9b2c6474 já recusava os 4 caminhos (1c06dc18); a entrega só tira o home do runner do CI do texto antes do padrão. Ficam recusados o nome que só começa com runner, o caminho de runner sob o diretório de usuários do Mac e outro caminho pessoal na mesma linha (a troca de todas as ocorrências é só da string exata).
- Teste: `test_home_do_runner_passa_mas_nome_que_o_contem_ou_o_segue_falha` falha na base (script de 9b2c6474 restaurado, 1 falha) e passa no head; a classe `VerificarContribuicao` inteira passa (15 testes). Verificação de comportamento por subprocesso, não de texto da fonte.
- Guarda: uma linha de guarda mudada (55), 3 mutantes declarados (CP-M1 sem a troca, CP-M2 sem a barra final, CP-M3 invertida); `forge-mutante` os mata, os três. `shellcheck` limpo.
- `--cobertura` acusa `não coberto: scripts/verificar-contribuicao.sh` porque, por desenho do `forge-mutante`, só Python tem a condição analisada; shell sai `não coberto` por arquivo, sem olhar linha (cabeçalho da ferramenta). Não é falha dos mutantes: eles cobrem a linha 55 e morreram. Fica como declarado, não provado pela ferramenta.
- Mecanismo: reaproveita a varredura existente, sem lista nova; afrouxa só o home do runner do CI, com teste dos limites (R-DECISAO sem exigência adicional). CI do PR: não há PR ainda; só os testes afetados rodaram aqui.
