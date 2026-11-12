---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/seguranca-sem-rerrodar
commit: 157c1da96cbf8f49abd3aef4b6e41b9b37cf4a58
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-11
---
# QA: v046 · SEGURANCA-SEM-RERRODAR (E4.1)

Head revisado: 157c1da96cbf8f49abd3aef4b6e41b9b37cf4a58 (base e6e47681; revalidação da volta 2, delta 6b77a7c7..157c1da9; parecer anterior em 6b77a7c7 reprovado por A4). Leitura da branch, sem escrita nela; suíte não rerrodada (o CI do PR é o portão).

## Achados
- A1 (recomendado) skills/cyber-security/SKILL.md:31 · [resolvido em 6b77a7c7: a skill agora traz "rode o teste novo de abuso", alinhada ao agente]
- A4 (bloqueante) agents/security-engineer.md:14 · [resolvido em 157c1da9: "a suíte inteira roda só no CI" voltou aos dois arquivos; test_trechos_obrigatorios passa no head]

## Sondas
- S1 · `git show 6b77a7c7:agents/security-engineer.md` e `:skills/cyber-security/SKILL.md` contra `invariantes[arquivo]` de tests/config.json (re.search, re.S) · espera: todos os trechos presentes · obtido: ['suíte inteira roda só no CI'] ausente nos dois arquivos

## Revalidação (volta 1)
- Observação: a árvore de trabalho do worktree tem correção NÃO commitada ("a suíte inteira roda só no CI; cite..." nos dois arquivos) e o teste passa nela; o head 6b77a7c7 ainda falha. Precisa de commit novo e novo head.
- A2/A3 são de outros pareceres; fora do domínio do QA (nada a reler aqui).
- Delta 8a96dd12..6b77a7c7 lido: 3 arquivos, só texto. Suíte não rerrodada; rodado só o teste afetado, no blob commitado: invariante quebrada (S1).
- `forge-check parecer delta` recusa o caminho (parecer fora de docs/qa da raiz-pedidos do worktree); delta lido por git diff, como o brief mandou.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E4.1: security-engineer e cyber-security citam CI verde ou PQ do autor, sem rerrodar o SHA | leitura do diff (3 arquivos, +4/-2): agents/security-engineer.md:14, skills/cyber-security/SKILL.md:31 | n/a | passou |
| Invariante `suíte inteira roda só no CI` (R-QA) preservada nos dois arquivos | grep do trecho no diff e em tests/config.json (linhas 301 a 716) | trecho protegido não removido | passou |
| Afrouxamento declarado (`afrouxa-regra`) com motivo, medida e volta atrás | changelog.d/seguranca-sem-rerrodar.md | n/a | passou |
| Parecer de segurança segue portão (R-SEGURANCA) | texto do changelog e do agente: só muda o que se rerroda | n/a | passou |

## Cenários e resultado real
- Mudança só de texto em agente e skill; nenhum código, hook, bin ou catraca: mutação e vermelho-antes-do-verde não se aplicam (nenhum teste novo).
- Nenhum teste referencia a frase removida ("testes dos arquivos tocados") para agents/security-engineer.md ou skills/cyber-security (git grep no head).
- Outros textos que mandam rodar testes afetados (tech-lead, qa-engineer, engineering-practices) são de outros papéis e seguem coerentes.
- Lembrete ao PR: o título precisa destacar o afrouxamento (CLAUDE.md, regras protegidas por teste); o CI confere a bateria.

## Revalidação (volta 2, head 157c1da9)
- Delta 6b77a7c7..157c1da9 lido: 2 arquivos, só texto (agents/security-engineer.md:14, skills/cyber-security/SKILL.md:31); frase invariante restaurada nos dois.
- `python3 -m unittest tests.test_forge -k trechos_obrigatorios` no head 157c1da9: `Ran 1 test ... OK` (S1 fechada).
- A4 resolvido; A1 segue resolvido; sem bugs abertos. Suíte inteira: check-run `bateria` do CI do PR.
