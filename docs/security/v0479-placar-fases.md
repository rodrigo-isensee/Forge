---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-placar-fases
commit: c08aee63c9d6161a53a2ead78cf2af20551a1221
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0479-placar-fases (v0478 E20.15, revalidação)

Volta por delta (`R-REVIEW`): `forge-check parecer delta` de `b8fb44f6..c08aee63` (ver a revalidação E20.15; a do E20.7 está no git). A rodada anterior (E20.3) fica no git e não se recopia.

## Achados
- A2 (recomendado) bin/forge-placar:197 · STRING_JSON é quadrático em string sem fecho com muitas aspas escapadas (`"` + `\"`*40000, 80 KB: 26 s); só em JSON inválido (truncado), nunca no válido do `gh`; sem ganho de atacante, não bloqueia

## Revalidação E20.15 (delta `b8fb44f6..c08aee63`, só `bin/forge-placar`)
`fundo_demais` (:196-203) conta `[` e `{` fora das strings antes do `json.loads` (:213-214). Pontos pedidos:
- Contagem enganável por aspas escapadas: não. O regex de string trata `\"` e `\\` certo (S4, S5). Em JSON válido as aspas alinham, então a contagem é exata; em inválido o `json.loads` recusa. O erro possível é só para mais (colchete em string não fechada conta), que recusa a mais, não a menos.
- Custo do regex: linear em JSON válido e em `"` ou `[` repetidos (4e4 caracteres: 0,0 s). Quadrático só em string não fechada com `\"` repetido (S9), ver A2. Correção mínima (dono: autor): varredura linear de um passe no lugar do regex, ou limite de tamanho do arquivo antes.
- Falha fechada: sim. Acima de 64 sai com 2 antes do decodificador (S6, S7); a captura de `RecursionError` saiu, e com no máximo 64 níveis a pilha do decodificador não estoura. 64 níveis exatos passam (S8).
Achado anterior A1 segue corrigido. Gatilhos: nenhum (inalterado).

## Gatilhos
Gatilhos: nenhum (ferramenta local de leitura; sem autenticação, segredo, dependência, CI, rede nem controle do Forge).

## Sondas
- S1 · `--prs` com `[{"mergedAt":"2026-13-45T00:00:00Z"}]` · espera: código 2 · obtido: código 2, `tem mergedAt inválido: 2026-13-45`
- S2 · `--prs` com 100000 níveis de `[` · espera: código 2 · obtido: código 2, `não é JSON legível`
- S3 · repositório com squashes `t (#7)` (com `refs/pull/7/head`), `u (#١٢)` e `v (#99)` (sem ref) · espera: só #7 medido, os outros em `sem_fases`, nada ecoado do assunto · obtido: item `#7`, `sem_fases: 2`, código 0

- S4 · `fundo_demais('["a\\"' + '['*70 + '"]')` · espera: False (colchetes dentro da string) · obtido: False
- S5 · `fundo_demais('["\\\\"' + '['*70 + ']')` · espera: True (a string fechou) · obtido: True
- S6 · `bin/forge-placar --prs` com `'['*65 + ']'*65` · espera: código 2 · obtido: código 2, `aninhado acima de 64 níveis`
- S7 · `--prs` com 100000 `[` · espera: código 2 · obtido: código 2
- S8 · `--prs` com 64 níveis e com `[{"mergedAt":"2026-11-10T00:00:00Z","body":"## Sem teste\n[[[ \" ]]]"}]` · espera: código 0 · obtido: código 0 nos dois
- S9 · `'"' + '\\"'*n` com n=1e4, 2e4, 4e4 · espera: tempo linear · obtido: 1,6 s, 6,4 s, 26,3 s (quadrático)

## Detalhe
Achados anteriores:
- A1 (recomendado, E20.3): corrigido. bin/forge-placar:201 capta `RecursionError` e :210-213 trata `ValueError` com saída 2 (S1, S2). O valor ecoado na mensagem é `quando[:10]`, já casado por `DATA` (dígitos e hífens), então não leva caractere de controle ao terminal.

Leitura nova do delta:
- `refs/pull/N/head` a partir do assunto (bin/forge-placar:94, :589-598): o assunto vem do histórico (título do PR, escolhido por quem abre o PR), mas só o grupo `\d+` ancorado no fim chega ao git, e o nome da ref é montado como `refs/pull/<dígitos>/head`; não começa por `-`, não admite `..`, `:`, espaço nem `^`. `rev-parse -q --verify` e `log base..ponta` vão por lista, sem shell. Dígito Unicode (`\d` do Python) dá uma ref inexistente e cai em `sem_fases` (S3). O pior que um título forjado faz é apontar o item para outro PR já buscado localmente, o que só distorce a métrica do próprio placar: sem ganho para atacante, não é achado.
- Os commits de `refs/pull/N/head` podem vir de fork; o placar só lê metadados e nomes de arquivo (`log --name-only`) e blobs por `git show <sha>:<nome>` (já lido na E20.3), sem executar nada além de filtro ou textconv que o operador configure localmente.
- O nome do item squash é `#<dígitos>`; a saída de texto e o `--json` não trazem o assunto.

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: leitura do delta e sondas locais em `$TMPDIR` com `python3 -I`. Suíte: não rodada localmente (brief: sem suíte local); a suíte inteira fica com o CI do PR. Varredor de segredos e SAST não estão no PATH: lacuna registrada; o delta não traz credencial.
