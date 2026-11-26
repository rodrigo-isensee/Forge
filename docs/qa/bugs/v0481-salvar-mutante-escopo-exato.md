# v0481-salvar-mutante-escopo-exato - M8 e M9 sobrevivem: escopo exato x prefixo sem teste
- Severidade: média
- Responsável sugerido: autor dos testes do hook (`tests/test_hooks.py`)
- Ambiente: melhoria/v0481-d6-resto @ 1afd54b5f

## Passos para reproduzir
`bin/forge-mutante --processos 4 tests/mutantes/v0481-d6-resto*.json`

## Resultado esperado
M8 e M9 (item sem `/` é caminho exato, não prefixo) morrem em `test_salva_e_envia_so_o_escopo`.

## Resultado obtido
`M8 · sobreviveu` e `M9 · sobreviveu`. No 9a708f86 morriam.

## Evidência
Com `--untracked-files=no`, `docs/a.md2` e `docs/b.md` do teste são não rastreados e o `status` não os vê; a fronteira prefixo x exato ficou sem arquivo que a exerça. Correção: `docs/a.md2` entra rastreado no `setUp` e é mudado no teste.
