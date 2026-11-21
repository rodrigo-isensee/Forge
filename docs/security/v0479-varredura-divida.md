---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-varredura-divida
commit: 7bfd64e7d4e2d43daa0cb412ee647684ae70c76c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E95.3, VARREDURA-SEMANAL-DIVIDA)

Escopo: `scripts/varredura-divida.py` (novo), o caminho `--conferir --todas` de `bin/forge-mutante` que ele chama, `tests/test_varredura_divida.py`, as specs de mutante e o mapa de `bin/forge-testes`. Diff `9d5dcb6e..7bfd64e7`.

## Gatilhos
Gatilhos: subprocesso alimentado por dado do repositório (nomes de ref remota, specs de mutante), leitura de pasta do usuário fora do repositório (`~/.forge-contrib/wt`).

## Conclusão
- **Só lê:** o script não abre arquivo para escrita, não apaga, não busca no remoto e não abre cartão; os subprocessos são `git` de leitura (`rev-parse`, `for-each-ref`), `du -sk` e `bin/forge-mutante --conferir --todas`, que lê objetos do commit (`git ls-tree`, `git show`) e sai antes do registro em `.forge/run/` (`bin/forge-mutante:1153-1156`, `777-800`). Única escrita observada: o cache de bytecode que o interpretador cria em `bin/__pycache__/` ao carregar `forge_apoio_testes` dentro do `forge-mutante` (ignorado pelo `.gitignore:1`); ver A1.
- **Sem rede nem custo (`R-CUSTO`):** importações só da biblioteca padrão (`scripts/varredura-divida.py:19-25`), nenhum socket, nenhum `fetch`/`push`.
- **Injeção:** todo subprocesso usa lista de argumentos, sem shell (`:34`, `:72`, `:104`); o nome de branch entra só como texto na saída e na sugestão de cartão, que é prosa e não comando executado. Nomes com `;`, `|`, `&`, crase, aspas e `${IFS}` saem literais e nada executa (sonda abaixo). O próprio git recusa nome com caractere de controle, espaço, `$(` e o que começa com `-`.
- **Links nas cópias:** `du -sk` não segue link (nem o da linha de comando nem os internos): pasta com link para 30 MB fora dela deu `0 MB`, e `du -skL` da mesma pasta deu 30720 KB. O `glob("*")` de `:103` só conta pastas (segue link para contar, sem ler nada dela).

Sondas executadas (TMPDIR de `mktemp -d`, fora de `~/.forge-contrib`): repositório com branches `x;touch${IFS}PWNED`, `` `id` ``, `a|b&c`, `q'"r` e uma com marca bidirecional, rodado com `--dias -1`: 5 linhas `branch-mesclada` com o nome literal, nenhum arquivo `PWNED` criado, rc 0; `find -newer` depois da varredura: nada gravado na pasta de teste nem na cópia revisada, exceto o cache de bytecode de A1. `tests/test_varredura_divida.py`: 12 testes OK. Suíte inteira: não rodada (brief: sem suíte local); o portão da suíte é o CI do PR.

## Achados
- A1 (recomendado) scripts/varredura-divida.py:72 · o forge-mutante chamado grava cache de bytecode em bin/__pycache__ ao carregar forge_apoio_testes, contra o "não grava arquivo" de :16; correção: rodar o filho com o interpretador atual e -B (ou a variável que desliga o cache) no env do subprocess.run.

## Sondas

## Detalhe dos achados
**A1** · evidência: `scripts/varredura-divida.py:72` chama `bin/forge-mutante`, que carrega `bin/forge_apoio_testes.py` por `importlib` (`bin/forge-mutante:118`); depois da varredura com `--raiz` na cópia do Forge apareceu o cache de bytecode desse módulo em `bin/__pycache__/`. A docstring (`:16`) promete "não grava arquivo". · caminho de ataque: nenhum realista (arquivo de cache, ignorado pelo git, dentro do próprio plugin; em cópia só de leitura a gravação falha em silêncio). É divergência entre a promessa de só leitura e o efeito. · severidade: informativa · correção mínima: em `:72`, invocar `[sys.executable, "-B", str(FORGE / "bin" / "forge-mutante"), ...]` ou passar `env={**os.environ, <variável que desliga o cache de bytecode>: "1"}`; alternativa aceita: ajustar a docstring para dizer que o cache do interpretador pode ser criado. · esforço: P · dono: autor da E95.1.

Observação sem achado: nome de branch com caractere Unicode de controle de direção (permitido pelo git) aparece cru no terminal e pode embaralhar a exibição da linha. Quem cria branch no `origin` já tem escrita no repositório, e a linha não é executada; sem caminho de ataque, fica só registrada.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do código, sondas locais em TMPDIR, `find -newer`, `du -skL` como contraprova. `gitleaks`, Semgrep e afins não se aplicam ao diff (sem segredo, sem dependência nova).
