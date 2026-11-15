---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-mutante-diagnostico
commit: ef1fb25b6e21fd7570611f993a7e30db3a478b57
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 mutante-diagnostico (E1.296, lote E1.283)

Intervalo `origin/develop` (c5c3a449)..ef1fb25b: `bin/forge-mutante` (ISENTA-POR-TEXTO, recusa cedo com árvore suja e spec diferente da do commit, linha `por quê` no `--cobertura`, mensagem de specs de pedidos diferentes), 3 specs novas (MD1 a MD20), 17 mutantes de 6 specs antigas realinhados, testes e fragmento de changelog.

## Gatilhos
Guarda do processo (`R-SEGURANCA`): o `forge-mutante` é o portão de prova de mutação; a isenção é o caminho que libera condição sem mutante, e a entrega troca o critério de casamento dela para a condição apagada.

## Achados
- A1 (recomendado) bin/forge-mutante:554 · `dados[ini:fim].count(trecho) == 1` trocado por `>= 1` sobrevive à classe Cobertura inteira (sonda S1): o "trecho uma vez dentro do nó" da isenta pelo texto não tem teste; falta caso com o trecho duas vezes no nó apagado, que deve sair rc 2.
- A2 (recomendado) tests/mutantes/guarda-sem-mutante-4.json:6 · a spec realinhada ainda sai rc 2: M25, M31 e M32 têm `de` que aparece 0 vezes no arquivo (já na develop, não desta entrega); realinhar ou aposentar os três junto com M28 a M30.

## Sondas

## Detalhe dos achados
**Os 17 realinhados não afrouxaram.** Conferi cada par antigo/novo contra o código: M28 (tira a trava do arquivo do mutante), M29 (fronteira de 8 para 7), M30 (aceita `de` repetido), M60, M1, M4, C1, C2, C3, C5, IL4, IL15 e IL6 a IL13 que só mudaram de texto mutam a mesma decisão com o mesmo efeito. IL1, IL5, IL11 e IL12 mudam de alvo porque a regra mudou (linha → texto), e cada um muta a decisão nova correspondente (o caminho pelo texto, a escolha entre texto e trecho único, a condição nova passando `False`, a apagada uma vez passando `falta == 1`). Rodadas no ef1fb25b, árvore limpa: `mutante-isenta-linha` 14/14 mortos, `mutante-isenta-linha-2` 1/1, `mutante-casa-espaco` 6/6, `guarda-sem-mutante-9` 7/7, `lote-mutante` 8/8, `guarda-sem-mutante-4` 5 mortos (M26 a M30) e os 3 inválidos de A2; as 3 specs do pedido, 20/20 mortos (MD1 a MD20).

**ISENTA-POR-TEXTO (`bin/forge-mutante:545-556`, `:614`).** Para a condição apagada uma vez, a isenta deixa de exigir a linha da base e de exigir trecho único no arquivo; basta o trecho uma vez na fatia do nó e a isenta ainda não usada. Caminho de abuso avaliado: um autor que quer passar o portão com menos prova. Ele continua precisando de uma isenta por condição apagada (a trava `usadas`, MD3/IL2, mata), com motivo de 20+ caracteres e impressa `isenta · arq:L(base) · motivo` para o review; a isenta não usada segue rc 2; a apagada duas vezes segue pelo trecho único (MD6); a condição nova segue pelo trecho único no arquivo (MD5, IL11). O que se perde é só a atribuição exata da linha, decisão do pedido (E1.283). Sem caminho de ataque novo. A1 é a lacuna de teste da trava que sobrou.

**Recusa da spec fora do commit (`:820-834`, `:942-947`).** Falha fechada: spec ilegível no commit conta como diferente e, com a árvore suja, recusa antes de rodar. Spec fora da raiz (ou link que resolve para fora) não é conferida, por desenho (MD17); a rodada continua mutando o conteúdo do commit, então uma spec de fora não faz um mutante passar por algo que o commit não tem. Rodar de uma subpasta faz a conferência recusar à toa (o caminho relativo fica errado), também fechado. Informativo.

**Linha `por quê` (`:504-528`, `:611-612`).** Só imprime id da spec e motivo fixo; não lê nem exibe conteúdo além do que a saída já mostrava. `por_que_nao_cobre` agora percorre todas as ocorrências do `de` antes de olhar o arquivo do mutante (custo linear por mutante e condição, arquivo limitado a 1 MiB); custo local, sem ganho para quem abusa. Informativo.

**Mensagem de pedidos diferentes (`:385-390`).** Os caminhos vêm do próprio usuário e saem com `shlex.quote`; só texto em stderr, nada é executado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados no ef1fb25b: os 5 testes novos ou reescritos de `tests.test_forge_mutante` (OK) e as rodadas de mutantes acima; sonda S1 com spec temporária fora do repositório (S1 sobreviveu; o par S2, `any(0 <= p for p in onde)`, morreu). A suíte inteira roda no CI: a branch não tem PR nem rodada de CI, então não foi citada. Ferramentas de varredura de segredo, de dependência e de workflow ausentes no PATH (lacuna registrada); a entrega não toca workflow, dependência nem segredo.
