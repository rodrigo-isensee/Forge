# v0481-salvar-segredo-em-commit-anterior - branch nova envia commit anterior sem varredura de segredo
- Severidade: alta
- Responsável sugerido: desenvolvedor do hook (`hooks/salvar.py`)
- Ambiente: melhoria/v0481-d6-resto @ 1afd54b5f, python3, git local

## Passos para reproduzir
1. Remoto com `develop`; cópia numa branch nova (sem `refs/remotes/origin/<branch>`).
2. Commit local anterior com `ghp_` e 30 `A` em `b.txt`, nunca enviado.
3. Mudança rastreada em `a.txt` (no escopo); `salvar.salvar(copia, branch, ["a.txt"])`.

## Resultado esperado
A varredura cobre tudo o que o push envia; achado: sem envio, commit na cópia.

## Resultado obtido
`enviado`; o remoto tem os commits `segredo` e `base`. Na branch nova a base da varredura é `HEAD^` (só o commit WIP, `hooks/salvar.py:145`).

## Evidência
Sonda com repositório bare e clone em `$TMPDIR`; saída: `melhoria/x b258bdc 1 arquivo(s) enviado` e `git log` do remoto com `827df30 segredo`. Correção sugerida: na branch nova, base `origin/develop` (como o pre-push), não `HEAD^`.
