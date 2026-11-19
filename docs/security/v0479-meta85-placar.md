---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-placar
commit: 87aff761c47ae4aa8bcf2b81c7565c71888cbcbc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0479-meta85-placar (v0478 E36.3)

Escopo: só o que a branch acrescenta sobre `melhoria/v0479-placar-fases` (42c2a906, já aprovada em `docs/security/v0479-placar-fases.md`): `git diff origin/melhoria/v0479-placar-fases...HEAD`, 3 commits (1e9d2cc9, 648c35e5, 87aff761). No domínio, `bin/forge-placar` (subcomando `fases`); o resto é texto (`docs/melhoria-continua.md`, fragmento de changelog), testes e mutantes.

## Gatilhos
Gatilhos: nenhum (ferramenta local de leitura; sem autenticação, segredo, dependência, CI, rede nem controle do Forge).

## Achados
- A1 (recomendado) bin/forge-placar:662 · uma linha `PARADA` com data impossível (ex.: mês 13) em qualquer pedido derruba o `fases` inteiro com "PARADA deve ser ...", sem dizer o arquivo; sem atacante (o pedido é escrito pelo time), mas a métrica some. Pular a linha e citar o arquivo basta.

## Sondas
- S1 · `--ci` com `{"a":1}` · espera: saída de erro limpa · obtido: `não é uma lista de runs legível`
- S2 · `--ci` com 100000 níveis de `[` · espera: saída de erro limpa · obtido: `não é uma lista de runs legível` (RecursionError captado)
- S3 · `--ci` com `[{"conclusion":"failure","updatedAt":"x"}]` · espera: saída de erro limpa · obtido: `--ci deve ser AAAA-MM-DDTHH:MM`
- S4 · `--desde 2026-11-19T10:00+99:00` · espera: recusa · obtido: `--desde deve ser AAAA-MM-DDTHH:MM`
- S5 · pedido com `PARADA sessão 2026-13-19 10:00 até ...` · espera: linha ignorada · obtido: comando aborta (A1)
- S6 · duas `PARADA sessão` sobrepostas (10:00-11:30 e 11:00-12:00) · espera: 2 h 00 min · obtido: 2 h 00 min

## Detalhe dos achados
Leitura do delta:
- **gh:** o placar não chama o `gh` nem a rede; o `--ci` é um JSON gerado fora (`gh run list ...`) e lido como dado por `ler` + `json.loads` (bin/forge-placar:670-678). Só `conclusion` (comparado a `failure`/`success`) e `updatedAt`/`createdAt` (passados a `fromisoformat`) são usados; nada do run (título, branch, autor) chega à saída. Entrada malformada sai com mensagem fixa (S1-S3). Um JSON forjado só distorce a própria métrica de quem o gerou: sem ganho para atacante.
- **Histórico do pedido:** `paradas_do_historico` (:658-664) reaproveita `historicos` (já lido), casa `PARADA` ancorado com datas só de dígitos e soma intervalos recortados na janela (`minutos_recortados`, :648-655; intervalo invertido não conta). Nada do texto da linha é ecoado: a saída traz só minutos e as fontes fixas de `FONTES_DE_PARADA` (:103-108). O `--raiz-pedidos` continua valendo sobre o `--raiz` (:775), então a fonte é a área do Jarvis.
- **git:** o novo `%cI` e o `PR_DO_MERGE` (`#(\d+)`) só viram ISO e `int`; o `git` segue por lista, sem shell (:554).
- A1: robustez sem caminho de ataque; recomendado ao dono do `bin/forge-placar` (`tech-lead`).

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: leitura do delta e sondas locais em `$TMPDIR` com `python3 -I`. Suíte: não rodada localmente (brief: sem suíte local); a suíte inteira fica com o CI do PR. Varredor de segredos e SAST não estão no PATH: lacuna registrada; o delta não traz credencial.
