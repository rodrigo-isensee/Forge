---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-tempo-fixture
commit: 57150d5ee607032f8e302e5319882ed3eeb0edac
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0480-tempo-fixture (PR #850, v0478 E164.4)

Escopo do diff `8f37daf8..57150d5e` no domínio: só a 1ª alternativa do `CRITICO` em `hooks/conformidade.py:65` (o par programa e ação). O resto do padrão não muda. Fora do domínio: o fragmento do changelog e `tests/mutantes/v0480-tempo-fixture.json`. Relidos os usos do padrão: `:2199`, `:2207`, `:2213`, `:2245`, `CRITICO_COM_CONTROLE` (`:3982`), o padrão com `PEDIDO_OU_BRIEF` (`:4045`) e `MARCADOR` (`:4440`). Todos usam só o resultado booleano de `search`, sem `pos`, sem grupo e sem trecho, e todos compilam com `re.I`.

**Só aperta ou neutro: neutro (a mesma decisão), provado por escrito e por sonda.**
- **Antes:** a linha é crítica se tem algum `git` ou `gh` como palavra e, depois dele na mesma linha física (sem `\n`), uma das ações como palavra.
- **Agora:** a busca parte só do início de cada linha (`(?<![^\n])`, que vale na posição 0 e depois de cada `\n`). O grupo atômico fixa o 1.º `git`/`gh` como palavra da linha, e a ação pode vir em qualquer ponto depois dele.
- **Por que nada sai do crítico:** se a linha tem um `git`/`gh` na posição i com a ação depois dele, o 1.º `git`/`gh` da linha começa em i0 ≤ i. Como as duas ocorrências precisam de `\b` nas duas pontas, elas não se sobrepõem, então o 1.º termina antes do fim do de i. A ação que vinha depois do de i vem também depois do 1.º. O grupo atômico não perde nada: na mesma posição, `git` e `gh` não casam os dois, e o `[^\n]*` de fora continua livre para voltar. O inverso é imediato, então o conjunto de linhas marcadas é o mesmo.
- **Dimensões pedidas no brief:**
  - prefixos antes do programa (`sudo`, `env`, `a=b`, `-C x`, `/usr/bin/git`, `$(`, crase, `{`, `(`);
  - várias linhas (`\n`, `\r\n`, `\\` + `\n`): o `\r`, o `\x85`, o ` `, o `\x0b` e o `\x0c` são meio de linha nos dois padrões, porque os dois usam `[^\n]`;
  - separadores do shell (`;`, `&&`, `||`, `|`, `&`, `#`);
  - falsos vizinhos (`xgit`, `gitx`, `_gh`, `gh_`, `git-`, `-push`, `pushgit`);
  - caixa e Unicode (`GIT`, `Gh`, `PUSH`, `ı`, `K` Kelvin, `ẞ`, `é`).
  Esses itens entraram no gerador de forma combinada. Sem divergência.

Sondas (script local, só biblioteca padrão; nenhuma prova bloqueante):
- **Equivalência:** compara o padrão antigo, montado de novo com o mesmo resto, com o `CRITICO` importado do head. Cobre todas as cadeias de 1 a 6 peças de `{git, gh, push, \n, espaço, x, _, -, \r, é}` e mais 300 mil cadeias sorteadas de 1 a 14 peças das 60 da lista acima. Resultado: 1.411.110 casos e 0 divergências. O mesmo vale para `CRITICO_COM_CONTROLE`: 50 mil casos e 0 divergências.
- **Tempo** (CPU de um `search` sem casar):

  | Entrada | Antes | Agora |
  |---|---|---|
  | 8 KB de `gh repo ` | 0,142 s | 0,0004 s |
  | 8 KB de `git ` | 0,282 s | 0,0003 s |
  | 10 linhas de 500 `gh ` | 0,159 s | 0,0007 s |
  | 8 KB sem programa, ou com o programa no início | < 0,001 s | < 0,001 s |

  O resto do padrão (`\bpr\b.*\bcreate\b`) não muda, e o teto de caracteres e o prazo da linha continuam valendo.
- **Versão do interpretador:** o grupo atômico pede a versão 3.11 ou mais nova. O pré-requisito do Forge é a 3.12 (README:13), e o `forge-init` e o `forge-doutor` conferem a versão. O CI roda na 3.12 e na 3.14. Não abre falha aberta nova.

Suíte: rodei localmente os testes do padrão tocado, todos OK (3 testes, 18,9 s):
- `tests.test_hooks.Hooks.test_marcador_critico_tambem_na_forma_juntada`, o teste do mutante TF1;
- `test_critico_ou_alias_marca_na_duvida`;
- `test_t6_a_leitura_ve_a_acao_sem_marcador_com_cada_variante`.

A suíte inteira é do CI. Na leitura, o run do head `57150d5e` tinha `bateria (passos)`, `verificações longas`, `instalação (python 3.14)` e `árvore já provada` verdes. As partes da suíte estavam pendentes, e `bateria (pareceres)` e `catraca` estavam vermelhas à espera dos pareceres.

## Gatilhos
Gatilhos: controle de acesso do agente (hook de conformidade, marcador da ação crítica que decide o prazo vencido e o erro interno).

## Detalhe dos achados
Sem achado nesta rodada.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: um script local de equivalência e de tempo, com a biblioteca padrão, e o `unittest`. Nada instalado.
