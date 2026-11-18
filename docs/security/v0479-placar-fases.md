---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-placar-fases
commit: 94728c4f44a2e4c492ff3020459e01a14dee9c52
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0479-placar-fases (v0478 E20.7, revalidação)

Volta por delta (`R-REVIEW`): `forge-check parecer delta` de `23431487..94728c4f`; no domínio, só `bin/forge-placar` e `docs/melhoria-continua.md` (texto que descreve o squash, sem efeito de controle). A rodada anterior (E20.3) fica no git e não se recopia.

## Gatilhos
Gatilhos: nenhum (ferramenta local de leitura; sem autenticação, segredo, dependência, CI, rede nem controle do Forge).

## Sondas
- S1 · `--prs` com `[{"mergedAt":"2026-13-45T00:00:00Z"}]` · espera: código 2 · obtido: código 2, `tem mergedAt inválido: 2026-13-45`
- S2 · `--prs` com 100000 níveis de `[` · espera: código 2 · obtido: código 2, `não é JSON legível`
- S3 · repositório com squashes `t (#7)` (com `refs/pull/7/head`), `u (#١٢)` e `v (#99)` (sem ref) · espera: só #7 medido, os outros em `sem_fases`, nada ecoado do assunto · obtido: item `#7`, `sem_fases: 2`, código 0

## Detalhe
Achados anteriores:
- A1 (recomendado, E20.3): corrigido. bin/forge-placar:201 capta `RecursionError` e :210-213 trata `ValueError` com saída 2 (S1, S2). O valor ecoado na mensagem é `quando[:10]`, já casado por `DATA` (dígitos e hífens), então não leva caractere de controle ao terminal.

Leitura nova do delta:
- `refs/pull/N/head` a partir do assunto (bin/forge-placar:94, :589-598): o assunto vem do histórico (título do PR, escolhido por quem abre o PR), mas só o grupo `\d+` ancorado no fim chega ao git, e o nome da ref é montado como `refs/pull/<dígitos>/head`; não começa por `-`, não admite `..`, `:`, espaço nem `^`. `rev-parse -q --verify` e `log base..ponta` vão por lista, sem shell. Dígito Unicode (`\d` do Python) dá uma ref inexistente e cai em `sem_fases` (S3). O pior que um título forjado faz é apontar o item para outro PR já buscado localmente, o que só distorce a métrica do próprio placar: sem ganho para atacante, não é achado.
- Os commits de `refs/pull/N/head` podem vir de fork; o placar só lê metadados e nomes de arquivo (`log --name-only`) e blobs por `git show <sha>:<nome>` (já lido na E20.3), sem executar nada além de filtro ou textconv que o operador configure localmente.
- O nome do item squash é `#<dígitos>`; a saída de texto e o `--json` não trazem o assunto.

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: leitura do delta e sondas locais em `$TMPDIR` com `python3 -I`. Suíte: não rodada localmente (brief: sem suíte local); a suíte inteira fica com o CI do PR. Varredor de segredos e SAST não estão no PATH: lacuna registrada; o delta não traz credencial.
