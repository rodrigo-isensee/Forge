---
tipo: qa
contrato: 1
pedido: pendencias-0.7.0
branch: melhoria/pendencias-hooks-0.7
commit: 4d4d7fb
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-13
---
# QA - pendências dos hooks e migração 0.7.0

## Escopo
Itens de `[Não publicado]` do CHANGELOG: migração 0.7.0, lista de pesados na stack, `git checkout <ref> <arquivo>` no hook `parecer`, mensagens do hook `agentes` e "Limites conhecidos" de `docs/hooks.md`. Tudo executado em projetos temporários (removidos ao fim); nenhuma sessão `claude` foi aberta.

## Suíte
| Verificação | Resultado |
|---|---|
| `python3 -m unittest discover -s tests` | 88 testes, OK |
| shellcheck (lista do CI) | sem avisos |
| `claude plugin validate . --strict` | passou |
| `bash tests/e2e-instalacao.sh` | ok (8 agentes, 9 skills, projeto inicializado) |

## Cenários e resultado real
| ID | Cenário | Resultado |
|---|---|---|
| MIG-01 | 0.5.0, `teto_agentes: 3` (com `pesados` e `outra`) | chave removida, demais chaves intactas, commit da migração e commit de versão; versão 0.7.0 |
| MIG-02 | `teto_agentes: 4` | fica |
| MIG-03 | `teto_agentes: "3"` (texto) | fica |
| MIG-04 | sem a chave / sem `config.json` | nada muda, sem erro; só registra a versão |
| MIG-05 | 2ª execução | "já está na versão 0.7.0; nada a fazer", código 0, árvore limpa; rodar `migrar` direto de novo deixa o arquivo idêntico |
| MIG-06 | árvore suja | recusa, código 2 |
| MIG-07 | só existe `main` | recusa, código 2, nada alterado; com `develop` existente parte dela, nunca da `main` |
| INI-01 | `forge-init --stack node-react` em projeto novo | `.forge/config.json` com `pesados` da stack (3 itens, igual a `stacks/node-react/pesados.json`); o modelo traz `"pesados": []` |
| INI-02 | `forge-init` em projeto existente (sem `--forcar`) | `config.json` mantido, lista própria preservada |
| PAR-01 | branch de trabalho: `git checkout develop app.js && git merge feature/x` | liberado (código 0); idem com `--`, com dois arquivos e `checkout -b nova develop` |
| PAR-02 | `git checkout develop && git merge feature/x` sem parecer | bloqueado (código 2, R-REVIEW) |
| PAR-03 | na `develop`, `git merge feature/x` sem parecer | bloqueado |
| AGE-01 | sem `/proc` (FORGE_PROC vazio), teto 3 | mensagem "padrão 3" |
| AGE-02 | sem `/proc` e `teto_maximo: 2` | "padrão 3, limitado por teto_maximo 2" |
| AGE-03 | com `/proc` simulado, teto adaptativo 5 / 2 | sem "padrão 3" |
| AGE-04 | `teto_maximo` maior ou igual ao adaptativo | sem "limitado por teto_maximo" |
| AGE-05 | `/proc` com conteúdo ilegível | cai no fallback, "padrão 3" |
| AGE-06 | `teto_agentes: 4` fixo | "fixo em .forge/config.json" |
| DOC-01 | `docs/hooks.md` | trata `teto_agentes` e `teto_maximo` de acordo com o hook; "Limites conhecidos" coerente com o comportamento |

## Observações (não são defeitos)
- `forge-init --forcar` em projeto existente regrava `.forge/config.json` e substitui a lista `pesados` própria pela da stack. É o que `--forcar` documenta (sobrescrever); sem ele a lista é mantida.
- A migração só trata o inteiro `3`; `3.0` e `true` não são cobertos de propósito (`type(valor) is int`).

## Bugs
Nenhum.

## Resultado da execução
2026-10-13, WSL, commit 4d4d7fb: todos os cenários passaram; zero bugs. Parecer: aprovado.
