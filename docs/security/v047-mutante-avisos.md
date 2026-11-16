---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-mutante-avisos
commit: 4553163442c9ff33e3993de0bee982f924a16a5f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (melhoria/v047-mutante-avisos)

Intervalo `origin/develop..4553163` (merge-base e60183d0): `bin/forge-mutante` (modo `--conferir`, aviso de log que não se grava, aviso de teste fora do commit), três specs em `tests/mutantes/`, testes em `tests/test_forge_mutante.py` e o fragmento do changelog. Revisão estática, numa passada (`R-SEGURANCA`, `R-REVIEW`).

## Gatilhos
Ferramenta de controle do Forge que lê entrada do autor da branch (specs JSON, nomes de arquivo do diff, conteúdo de commits) e é rodada por quem revisa. Fronteira: a spec e o conteúdo do commit são do autor; quem roda o `--conferir` é o revisor, na própria máquina.

## Achados
- A1 (recomendado) bin/forge-mutante:663 · linha_base_bate não captura MemoryError/RecursionError do parse: arquivo da base com aninhamento profundo derruba o --conferir com traceback e saída 1 (falha fechada, não aprova); capturar e tratar como não bate ou saída 2, como o resto da entrada inválida

## Sondas

## Detalhe dos achados
**A1.** Evidência: `bin/forge-mutante:658-664` chama `condicoes(texto)` (parse da linguagem) e só captura `ValueError` e `SyntaxError`. Sonda local: o parse de um arquivo com `y = ` seguido de 200 000 operadores unários termina em `MemoryError` no interpretador do ambiente. Caminho de ataque: o autor da branch versiona na base um arquivo assim e aponta uma isenta para ele; o revisor que roda `--conferir` recebe um traceback com saída 1 em vez da saída 2 documentada. Não há ganho para o atacante: a saída não é 0, nada aprova, nada executa; o mesmo comportamento já existe na `--cobertura` (linha 728, pré-existente). Severidade: informativa. Correção mínima: incluir `MemoryError` e `RecursionError` nas exceções da linha 663 (e, por coerência, na 728). Esforço: P. Dono: o autor do `bin/forge-mutante` (`software-engineer` da entrega).

Pontos conferidos sem achado:
- `--conferir` não executa teste nem código da branch: lê specs e arquivos só do commit (`git show <sha>:<caminho>`, prefixo de sha, sem injeção de opção), com `--literal-pathspecs`, `-z` e `--diff-filter=AM` na lista (linha 685) e `SPEC_DO_DIFF` limitando a `tests/mutantes/*.json`.
- Spec passa por `validar_spec` antes do uso (caminho relativo sem `..` nem barra inicial, `de` não vazio e com teto de tamanho, até 16 mutantes e 8 isentas; `linha_base` inteiro limitado); a spec tem teto de 64 KiB e o arquivo da isenta de 1 MiB (`fonte`).
- `teste_no_commit` (linha 763) monta o caminho a partir de id de teste já validado (`tests.` + identificadores), lê só do commit e usa `re.escape` no nome; o texto do aviso só contém esses ids.
- `anotar` (linha 743): capturar `OSError` só troca a queda por aviso no stderr depois do veredito; não muda o código de saída nem o caminho do log.
- Specs novas não trazem mutante que mire arquivo de teste ou fora do repositório; o changelog não traz segredo.

Suíte: a suíte inteira roda no CI do PR; aqui vale a entrega conferida em 45531634 (Jarvis). Rodei os testes novos: `tests.test_forge_mutante.Conferir` (6, OK) e os dois novos de `Execucao` (OK).

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas de varredura de segredos, SAST, dependências e workflows não estão no PATH deste ambiente (lacuna; rodam no CI). O intervalo não toca workflow, dependência nem configuração de CI.
