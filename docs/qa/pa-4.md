---
tipo: qa
contrato: 1
pedido: pa-4
branch: melhoria/pa-4-parecer-commitado
commit: 7424d5c2a9ed7c74b62cbc19d3964f8a492d40d1
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 1
aceite_usuario: sim
data: 2026-10-16
---
# QA - PA-4 (`forge-check pr` exige o parecer commitado)

Sem UX nem API. Código testado: 7424d5c (implementação bb4b4b6, 0925835, 4a28e23 + volta do autor da2f537, 7424d5c) sobre a base b38cd28. O HEAD da branch (6355de0) só acrescenta as revalidações de review e segurança (2 arquivos em `docs/reviews/` e `docs/security/`, ambos `aprovado`, `commit: 7424d5c`); não há código diferente do testado. Pré-condição conferida: review e segurança aprovados; `forge-check pr pa-4 --ref HEAD --base origin/develop` antes deste parecer só reclamou do parecer de QA ausente.

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1 | Suíte verde | `python3 -m unittest discover -s tests -q` | n/a | 726 testes, OK (187 s) |
| PQ-2 | Plugin válido | `scripts/validar-plugin.sh` | n/a | "Validation passed" |
| EX-a | `pr` sem `--ref` recusa o parecer só no disco | repositório temporário, parecer novo não rastreado | parecer novo | rc=1, uma linha por parecer (review e QA) |
| EX-b | Recusa o parecer só no índice (`git add` sem commit) | idem, após `git add` | índice != HEAD | rc=1, mesma mensagem |
| EX-c | Recusa o parecer editado depois do commit | commit, depois acrescenta uma linha ao QA | disco != HEAD | rc=1, só o arquivo editado é citado |
| EX-d | `--skip-worktree` e `--assume-unchanged` não escondem a edição | aplica cada marca e edita; `git status` fica vazio | índice enganado | rc=1 nos dois, mesma mensagem |
| EX-e | Aceita o parecer commitado e igual ao disco | commit dos dois pareceres | igualdade byte a byte | rc=0, sem saída |
| EX-f | Com `--ref` o disco é ignorado | `--ref melhoria/x` de outra branch, com o parecer do disco editado e com ele apagado | ref lida só do git | rc=0 nos dois casos |
| EX-g | Mensagem de recusa diz o que fazer | texto das recusas acima | n/a | cita o arquivo, "quem o emitiu o commita na branch revisada, só esse arquivo, no mesmo push da entrega" e o R-ID do tipo (R-REVIEW, R-QA) |
| EX-h | `--help` e ajuda do `pr` citam a exigência | `bin/forge-check --help`; `bin/forge-check pr --help` | n/a | `pr --help` cita ("sem --ref, o parecer do disco precisa estar commitado, igual ao do HEAD"); `--help` geral **não** cita: ver BUG-1 |
| EX-i | Sem rótulo "(PA-4)" nas instruções | `grep -n '(PA-4)' agents/*.md` | n/a | vazio (rc=1 do grep) |

## Mutação manual no arquivo alterado
Sem ferramenta de mutação para o Python da fábrica; mutei à mão, em cópia temporária do HEAD (`git archive`), `bin/forge-check` e rodei `python3 -m unittest tests.test_forge.ForgeCheck -q` (base: 43 testes, OK).
| Mutante | Resultado |
|---|---|
| M1 `parecer_commitado` sempre devolve True (equivale a não ter a implementação) | morto (2 falhas) |
| M2 desliga a conferência (`if False and ...`) | morto (2 falhas) |
| M3 confere também com `--ref` (remove `ref is None`) | morto (3 falhas) |
| M4 falha do git com HEAD legível passa a liberar | morto (1 falha) |

Vermelho antes do verde: o M1 é o código sem a obrigação; os testes novos (`test_pr_parecer_so_na_arvore_de_trabalho_falha`, `test_pr_parecer_editado_nao_escapa_por_skip_worktree_nem_assume_unchanged`, `test_pr_com_ref_nao_olha_a_arvore_de_trabalho`) falharam nele.

## Bugs
- **BUG-1 (baixa, aberto):** `bin/forge-check --help` não cita a exigência de parecer commitado. A frase está na docstring do módulo (comentário de leitura do fonte) e na ajuda do `pr --ref`, mas a ajuda geral só mostra a descrição "Valida o contrato entre agentes (ADR 0004)" e o `pr` nem aparece com texto na lista de subcomandos (já era assim antes do PA-4; o `pr --ref` e o `pr --base` seguem o mesmo padrão). Passos: `bin/forge-check --help | grep -i commit` retorna vazio. Esperado (brief E2-h): a ajuda cita a exigência. Obtido: só `pr --help` a cita. Sem risco ao portão: a mensagem de recusa e `pr --help` orientam o usuário. Responsável sugerido: `tech-lead` (autor do `bin/forge-check`), com `help=` no subparser `pr`. Depende de aceite do usuário (`aceite_usuario: sim`), pois o pedido e as obrigações do E1 não exigem a ajuda geral.

## Veredito
Aprovado, com 1 bug baixo aberto (BUG-1, aceite do usuário). Todas as obrigações com evidência; o portão recusa as quatro formas de parecer fora do commit e não regride com `--ref`. Não declara segurança; o parecer de segurança é de `docs/security/pa-4.md`.
