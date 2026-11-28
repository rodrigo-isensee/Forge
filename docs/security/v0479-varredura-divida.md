---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-varredura-divida
commit: 5b1ad8ca2cd4c9ecc07c980cf02a16b066884c3f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E95.6, VARREDURA-SEMANAL-DIVIDA, revalidação)

Volta por delta (`R-REVIEW`): a rodada anterior (head `7bfd64e7`, E95.3) fica no git. Delta lido: `forge-check parecer delta` no intervalo `7bfd64e7..5b1ad8ca`; no domínio só `scripts/varredura-divida.py` (o `subprocess.run` de `mutantes()`, `:73-74`); fora do domínio, lidos por conferência do A1: `tests/test_varredura_divida.py` (`rodar()` e o teste novo) e o mutante M23 em `tests/mutantes/varredura-divida.json`.

## Gatilhos
Gatilhos: subprocesso alimentado por dado do repositório (specs de mutante), leitura de pasta do usuário fora do repositório (`~/.forge-contrib/wt`).

## Conclusão
- **A1 (recomendado): resolvido.** O filho agora roda com o interpretador atual e `-B` (`scripts/varredura-divida.py:73`), o que desliga a gravação do cache de bytecode no carregamento de `forge_apoio_testes` pelo `forge-mutante`; a docstring (`:16`, "não grava arquivo") volta a ser verdadeira e o `:68` registra o motivo.
- **Só aperta:** a lista de argumentos continua sem shell; o interpretador passa a ser o mesmo que já roda o script (em vez do resolvido pela linha `#!` do filho), sem nova fonte de entrada, sem rede e sem escrita. O `rodar()` do teste tira as variáveis herdadas do interpretador, então o teste não passa por acaso quando o ambiente já desliga o cache: só o `-B` do script o faz passar. O M23 remove o `-B` e é morto por `test_filho_nao_grava_cache_de_bytecode_no_forge`.
- **Netos:** com `--conferir --todas` o `forge-mutante` sai antes de lançar outro processo do interpretador (`bin/forge-mutante:1153-1156`, `777-800`); a sonda abaixo confirma que nada é gravado.

Sondas (TMPDIR de `mktemp -d`, fora de `~/.forge-contrib`): cópia de `5b1ad8ca` por `git archive` num repositório novo, rodada com `--raiz` nela, sem as variáveis de cache herdadas: rc 0, 33 achados, `git status --porcelain --ignored` vazio, nenhum `__pycache__`. Contraprova com o M23 aplicado à mão (sem `-B`): `!! bin/__pycache__/`. `tests.test_varredura_divida`: 13 testes OK. Suíte inteira: não rodada (brief: sem suíte local); o portão da suíte é o CI do PR.

## Sondas

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, sondas locais em TMPDIR com contraprova do mutante. Varredura de segredo e de dependência não se aplica ao delta (sem segredo, sem dependência nova).
