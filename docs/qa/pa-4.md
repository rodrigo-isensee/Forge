---
tipo: qa
contrato: 1
pedido: pa-4
branch: melhoria/pa-4-parecer-commitado
commit: 54bfcf9d56fb9f7f1f18c4ca9edca84947f9703f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-16
---
# QA - PA-4 (`forge-check pr` exige o parecer commitado)

Revalidação proporcional (escopo declarado `completo` porque a tabela abaixo mantém o parecer anterior e acrescenta a volta do autor). Código testado: 54bfcf9 (implementação bb4b4b6, 0925835, 4a28e23 + voltas do autor da2f537, 7424d5c, 54bfcf9) sobre a base b38cd28. O HEAD da branch (daeba40) só acrescenta revalidações de review e segurança (`docs/reviews/pa-4.md`, `docs/security/pa-4.md`, ambos `aprovado`, `commit: 54bfcf9`); nenhum código além do testado. Pré-condição conferida: review e segurança aprovados em 54bfcf9; `forge-check pr pa-4 --ref HEAD --base origin/develop` só reclamou do parecer de QA desatualizado.

Obrigações e mutação do parecer anterior (EX-b, EX-c, EX-d, EX-g, EX-i; M1 a M4) não mudaram: a volta 54bfcf9 só toca a ajuda (`help=` do subparser `pr` e a lista geral), sem alterar `parecer_commitado`. Repetidos aqui só EX-a, EX-e e EX-f, e o BUG-1.

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1 | Suíte verde | `python3 -m unittest discover -s tests -q` | n/a | 727 testes, OK (146 s) |
| PQ-2 | Plugin válido | `scripts/validar-plugin.sh` | n/a | "Validation passed" |
| EX-a | `pr` sem `--ref` recusa o parecer só no disco | repositório temporário, parecer novo não rastreado | parecer novo | rc=1, uma linha por parecer (review e QA); repetido em 54bfcf9 |
| EX-b | Recusa o parecer só no índice (`git add` sem commit) | idem, após `git add` | índice != HEAD | rc=1, mesma mensagem |
| EX-c | Recusa o parecer editado depois do commit | commit, depois acrescenta uma linha ao QA | disco != HEAD | rc=1, só o arquivo editado é citado |
| EX-d | `--skip-worktree` e `--assume-unchanged` não escondem a edição | aplica cada marca e edita; `git status` fica vazio | índice enganado | rc=1 nos dois, mesma mensagem |
| EX-e | Aceita o parecer commitado e igual ao disco | commit dos dois pareceres | igualdade byte a byte | rc=0, sem saída; repetido em 54bfcf9 |
| EX-f | Com `--ref` o disco é ignorado | `--ref melhoria/x` de outra branch, com o parecer do disco editado e com ele apagado | ref lida só do git | rc=0 nos dois casos; repetido em 54bfcf9 |
| EX-g | Mensagem de recusa diz o que fazer | texto das recusas acima | n/a | cita o arquivo, "quem o emitiu o commita na branch revisada, só esse arquivo, no mesmo push da entrega" e o R-ID do tipo (R-REVIEW, R-QA) |
| EX-h | `--help` geral e `pr --help` citam a exigência | `bin/forge-check --help`; `bin/forge-check pr --help` | n/a | os dois citam ("pr  pareceres de review e QA de um pedido; sem --ref, o parecer do disco precisa estar commitado, igual ao do HEAD"); BUG-1 fechado |
| EX-i | Sem rótulo "(PA-4)" nas instruções | `grep -n '(PA-4)' agents/*.md` | n/a | vazio (rc=1 do grep) |

## Mutação manual
Sem alteração de `parecer_commitado` desde o parecer anterior, os mutantes M1 a M4 (todos mortos, 2/2/3/1 falhas em `tests.test_forge.ForgeCheck`) continuam valendo. Vermelho antes do verde: M1 é o código sem a obrigação; os testes novos falharam nele.

## Bugs
- **BUG-1 (baixa, corrigido em 54bfcf9):** `bin/forge-check --help` não citava a exigência. Conferido: `bin/forge-check --help` agora lista `pr` com "sem --ref, o parecer do disco precisa estar commitado, igual ao do HEAD". Nenhum bug aberto.
- Observação (sem bug): para parecer commitado e depois editado, a mensagem diz "ausente no commit (HEAD)", impreciso (o conteúdo difere, o arquivo existe). O bloqueio e o arquivo citado estão corretos; só o texto. Fica como sugestão ao `tech-lead` para outro cartão.

## Veredito
Aprovado, sem bug aberto. Todas as obrigações com evidência; o portão recusa as formas de parecer fora do commit e não regride com `--ref`. Não declara segurança; o parecer de segurança é de `docs/security/pa-4.md`.
