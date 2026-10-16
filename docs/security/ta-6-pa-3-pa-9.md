---
tipo: revisao-seguranca
contrato: 1
pedido: ta-6-pa-3-pa-9
branch: melhoria/ta-6-sobreposicao-fila-quadro
commit: c7a2b6af58a96ebbe1e9f4566c7411af9dcd116b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-16
---
# Review de segurança: ta-6-pa-3-pa-9

Escopo: `git diff origin/develop...c7a2b6a` (Base-sha 1fd122f), 8 arquivos. Foco em `bin/forge-check` (`sobreposicao`, `movimento`), mais `tests/config.json` e os textos (Jarvis, tech-lead, `R-FLUXO`, kanban-scrum). Ameaça considerada: entrada malformada (nome de branch, cartão, coluna, motivo, `--base`) que leve o comando a executar, escrever fora do arquivo previsto ou corromper o histórico do quadro; e afrouxamento de controle.

## Gatilhos
`R-SEGURANCA`: muda `bin/forge-check` (controle do Forge) e os invariantes em `tests/config.json`.

## Resumo
**Veredito: aprovado.** Nenhum achado crítico, alto, médio ou baixo; duas observações informativas.

## Conferido
- **`sobreposicao` só lê, sem shell nem rede.** `cmd_sobreposicao` e `branches_de_melhoria` (`bin/forge-check:544-573`) usam apenas `git for-each-ref`, `rev-parse --verify` e `git diff --name-only --no-renames`, todos pelo `git()` (`:278`), que usa lista de argumentos (sem `shell=True`), tira `GIT_*` do ambiente e tem timeout. Nada é escrito.
- **Nome de branch sem injeção.** Só entram nomes que começam por `melhoria/` (`:550`), logo nunca com `-` inicial; vão como um argumento de lista, dentro de `refs/heads/...` ou `origin/...`. `--base` passa por `base_da_entrega` (`:400`), que só devolve a base depois de `rev-parse --verify` ou uma constante de `BASES`; testei `--base '--output=...'`: o argparse recusa (rc 2) e nada foi criado. A saída é de arquivos do git já com aspas para nomes especiais.
- **`movimento` só acrescenta a `docs/kanban/historico.md`.** O caminho é fixo (`raiz/docs/kanban/historico.md`, `:581`), sem parte vinda da entrada; o `open` é em modo `"a"` (`:588`) e `mkdir` só do pai fixo. Cartão, `--de`, `--para` e `--motivo` passam por `limpo` (`:578`): `|` vira `/` e todo espaço em branco (inclusive `\n`, `\r`) colapsa em um espaço (testado com `K-1|x\ny`: uma linha só, 5 colunas). Campo vazio sai com rc 1 sem escrever (`:581`, `:2075`). A hora vem do relógio local, não da entrada.
- **Nenhum controle removido ou afrouxado.** `tests/config.json`: só linhas acrescentadas (10, 0 removidas) em kanban-scrum, Jarvis, tech-lead e `R-FLUXO`; `hooks/` e `.github/` intocados. Os textos só acrescentam regras (fila, sobreposição, registro do quadro); a única linha trocada é o exemplo de data em kanban-scrum (ISO 8601).
- **Sem custo (`R-CUSTO`):** só `git` local e biblioteca padrão.

## Achados
### I-TA6-1. Caracteres de controle (ESC) passam pelo `limpo` (informativa)
- **Evidência:** `bin/forge-check:578-579` (`\s+` não cobre `\x1b` nem outros controles).
- **Caminho:** quem roda o comando (o Jarvis, no próprio repositório) pode gravar uma sequência ESC no histórico; ao dar `cat` no terminal, ela é interpretada. Não há atacante externo: a entrada é do operador; o valor é de higiene.
- **Sugestão:** remover `[\x00-\x1f\x7f]` além do espaço em branco.
- **Esforço:** P · **Dono:** tech-lead (próxima fatia, sem bloquear).

### I-TA6-2. `historico.md` que é link simbólico seria seguido (informativa)
- **Evidência:** `bin/forge-check:583-588` (`arq.open("a")` segue o link).
- **Caminho:** só quem já escreve no repositório pode criar o link; ele já escreveria o arquivo-alvo direto. Sem ganho de privilégio.
- **Sugestão:** opcional, recusar `arq.is_symlink()`.
- **Esforço:** P · **Dono:** tech-lead.

## Riscos aceitos e ferramentas
- Riscos aceitos: nenhum; as duas observações são informativas e viram cartões sem aceite do dono.
- Ferramentas: revisão estática do diff; execução local de `movimento` e `sobreposicao` em `$TMPDIR` com entradas incomuns (`|`, quebra de linha, ESC, `--base` com `--`). Lacuna: `gitleaks`, `zizmor` e `semgrep` não estão no PATH (nada varrido por eles; o diff não toca workflow nem traz segredo, conferido por leitura).
