---
tipo: qa
contrato: 1
pedido: hook-conformidade
branch: melhoria/hook-conformidade
commit: 226cfba
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-13
---
# QA: hook `conformidade` (ADR 0009)

Links: `docs/adr/0009-conformidade-dos-agentes.md` (seção 3, matriz, com o ajuste: o `jarvis` mescla em `develop`/`homolog`, com parecer, e edita o `CLAUDE.md` do projeto), `docs/hooks.md` (seção do hook `conformidade`), `docs/reviews/hook-conformidade.md`.

## Escopo
Cobre: o hook `hooks/conformidade.py` com a política `hooks/conformidade.json`, executado de verdade num projeto temporário com `.forge/versao`, com o JSON de entrada no stdin e um papel por vez (`agent_type`). Não cobre: ativação no próprio Forge (sem `.forge/versao`, ADR 0008, 4.4), o sandbox da ADR 0009 (seção 5), o rótulo/CI. Nada que custe uso de IA foi executado. Ambiente: clone descartável de `melhoria/hook-conformidade` em 226cfba.

## Suíte
| Verificação | Resultado |
|---|---|
| `python3 -m unittest discover -s tests` | 96 testes, OK |
| shellcheck (lista do job `shell`) | sem achados |
| `claude plugin validate . --strict` | passou |
| `bash tests/e2e-instalacao.sh` | ok (8 agentes, 9 skills) |

## Cenários (hook executado fora dos fixtures)
| ID | Papel | Ação | Esperado | Obtido |
|---|---|---|---|---|
| CT-01 | dev | `npm test && git add -A && git commit` | passa | passa (exit 0, sem saída) |
| CT-02 | dev | `gh pr merge feature/x --squash` (base `develop`) | barra | barra: `R-CONFORMIDADE: gh pr merge é de tech-lead/jarvis` |
| CT-03 | qa | Write `docs/qa/x.md` | passa | passa |
| CT-04 | qa | Write `docs/reviews/x.md` | barra | barra: parecer de review é do tech-lead |
| CT-05 | tech-lead | Write `docs/reviews/x.md` | passa | passa |
| CT-06 | jarvis | Edit `CLAUDE.md` | passa | passa |
| CT-07 | jarvis | Edit `.claude/settings.json` | barra | barra: arquivo em vigor |
| CT-08 | dev | `sed -i ... .forge/config.json` | barra | barra |
| CT-09 | dev | `env FOO=1 git push --force origin feature/x` | barra | barra: `R-VERIFY` |
| CT-10 | dev | `git config user.name x` | barra | barra (use `--worktree`) |
| CT-11 | dev | Write de JS com `a.push(1)`, `.forge/config.json` inválido (`[1,2]`) | passa | passa; erro interno só em `.forge/run/erros.log` |
| CT-12 | dev | Projeto sem `.forge/versao`, `git push --force origin develop` | exit 0, sem saída | exit 0, sem saída |

Extras:
| ID | Cenário | Obtido |
|---|---|---|
| CT-13 | dev: `git push origin develop` / `git push -u origin feature/x` / `git commit -n` | barra / passa / barra (`R-VERIFY`) |
| CT-14 | `sudo -u x git push origin develop`; `env -i bash -c 'git push origin develop'` (B3) | barram |
| CT-15 | tech-lead grava `.githooks/pre-push`; dev grava `docs/qa/../reviews/y.md` (travessia) | barram |
| CT-16 | qa: `npm install lodash` / `npm ci` | barra / passa |
| CT-17 | dev grava `~/.claude/CLAUDE.md` (R2) | barra |
| CT-18 | Config inválida: Edit com `merge(a,b)`, `npm test -- merge.spec.ts`, Write com `a.push(1)` e `mergeSort` no conteúdo (B1) | passam |
| CT-19 | Config inválida: `git push origin develop`, Write em `.githooks/` (falha fechada) | barram com "erro interno ... ação crítica" |
| CT-20 | `gh pr merge 3` (só número) pelo dev | passa no `conformidade`; o `parecer` barra: `R-CONTRIB: PR indicado só por número` (conforme `docs/hooks.md`) |
| CT-21 | tech-lead e jarvis: `gh pr merge feature/x` (base `develop`) | passam no papel |
| CT-22 | Clone do Forge: tech-lead grava `docs/regras/` em `develop` / dev grava em `melhoria/*` | barra / barra |
| CT-23 | Clone do Forge, `git merge melhoria/x` sem parecer, jarvis e tech-lead | `parecer` barra os dois (`R-REVIEW`) |

## Desempenho
Mediana de 20 chamadas (`npm test && git commit`, dev): 71 ms (p90 87 ms; `python3` vazio: 31 ms nesta máquina). Dentro do orçamento de 100 ms da ADR 0009.

## Achados
Nenhum defeito novo. Observações, sem bug:
- **N1 (já no review):** o merge do `jarvis` vale também num clone do Forge no papel; o `parecer` segue exigindo os pareceres (CT-23), e a R-CONTRIB (226cfba) distingue a sessão que mantém o Forge das de projeto. A confirmação da matriz é do `software-architect`.
- **B4 do review (autoria `t <t@t>`):** os commits da branch seguem com autor `t`; é ajuste do usuário (limpar `[user]` do `.git/config` e reescrever a autoria antes do push), não defeito de código, e fica fora desta aprovação de QA.
- `gh pr merge <número>` por qualquer papel depende do `parecer` (CT-20); se o hook `parecer` for desativado, o `conformidade` sozinho não barra o dev nesse caso.

## Parecer
Aprovado em 226cfba: suíte verde, todos os cenários dos papéis conferem com a matriz da ADR 0009 (com o ajuste do `jarvis`), a falha fechada é seletiva, o projeto sem `.forge/versao` fica intocado e o custo é de 71 ms. Nenhum bug aberto.
