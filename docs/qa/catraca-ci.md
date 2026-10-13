---
tipo: qa
contrato: 1
pedido: catraca-ci
branch: melhoria/catraca-ci
commit: 57b77c1
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 2
data: 2026-10-13
---
# QA: catraca anti-piora do CI (ADR 0008, seção 3)

Ambiente: clone descartável da branch no commit 57b77c1; cada cenário é um commit sobre a base 57b77c1, rodando `python3 tests/catraca.py --base 57b77c1` (nos cenários de renomeação e de `tests/catraca.py`, a cópia da base do script, como o CI a vê). Nada que custe uso de IA foi executado.

## Suíte
| Verificação | Resultado |
|---|---|
| `python3 -m unittest discover -s tests` | 129 testes, OK |
| shellcheck (lista do job `shell`) | sem achados |
| `claude plugin validate . --strict` | passou |
| `bash tests/e2e-instalacao.sh` | ok (8 agentes, 9 skills) |

## Job `catraca`
| ID | Cenário | Esperado | Obtido |
|---|---|---|---|
| CT-01 | Remover item de `invariantes` | barra | barra (R-CONFORMIDADE, exit 1) |
| CT-02 | Remover um `test_*` | barra | barra (129 para 128) |
| CT-03 | Subir `limite_linhas.agente` | barra | barra (110 para 160) |
| CT-04 | `ANTHROPIC_API_KEY` em `scripts/jarvis` | barra | barra (R-CUSTO, linha indicada) |
| CT-05 | `claude -p` em `bin/forge-init` | barra | barra |
| CT-06 | `secrets.FOO` em `ci.yml` | barra | barra (R-CUSTO e mudança em workflow) |
| CT-07 | Editar `.github/workflows/ci.yml`, sem rótulo | barra | barra |
| CT-08 | Editar `tests/catraca.py` | barra | barra |
| CT-09 | Remover hook de `hooks/hooks.json` | barra | barra |
| CT-10 | Remover uma fixture de `tests/hooks/` | barra | barra (77 para 76) |
| CT-11 | Mudar `dono` | barra | barra |
| CT-12 | Remover item de `termos_proibidos` | barra | barra |
| CT-13 | Texto de doc neutro | passa | passa (exit 0) |
| CT-14 | PR de release (versão 0.7.0 e fecha `[Não publicado]`) | passa | passa |
| CT-15 | Renomear `tests/catraca.py` | barra | exit 0 (BUG-01; no CI o job falha só porque o script some e devolve 2) |
| CT-16 | Mover `.github/workflows/ci.yml` para `.github/ci-desligado.yml` (desliga o CI) | barra | exit 0 (BUG-01) |
| CT-17 | Renomear `docs/regras/R-REVIEW.md` (arquivo protegido) | barra | catraca exit 0 (BUG-02); `unittest` falha (10 falhas, 1 erro) |
| CT-18 | Renomear `agents/jarvis.md` (tem invariantes) | barra | catraca exit 0 (BUG-02); `unittest` falha |
| CT-19 | Apagar `docs/regras/R-QA.md` | barra | catraca exit 0 (BUG-02), só os testes pegam |
| CT-20 | Renomear arquivo de teste sem perder `test_*` | passa | passa |

Rótulo `afrouxa-regra` não foi exercitado contra a API real (sem token); a função `rotulo_liberado` é coberta pelos testes unitários.

## Job `pr-texto`
| ID | Cenário | Resultado |
|---|---|---|
| CT-21 | Corpo vazio | barra (as duas seções) |
| CT-22 | "Como medir" com título e sem texto | barra |
| CT-23 | "Como medir" só com comentário HTML | barra |
| CT-24 | Template cru sem preencher | barra |
| CT-25 | Seções preenchidas | passa |
| CT-26 | `### Como medir` (nível 3) | barra |
| CT-27 | "Como medir" com texto vazio de sentido (`ok`) | passa (BUG-03) |

## Job `pareceres`
| ID | Cenário | Resultado |
|---|---|---|
| CT-28 | PR para `develop` toca `hooks/`, sem parecer | barra (R-REVIEW) |
| CT-29 | Idem para `homolog` | barra (review e QA) |
| CT-30 | Review aprovado, base `develop` | passa |
| CT-31 | Review aprovado sem QA, base `homolog` | barra (falta QA) |
| CT-32 | Review e QA aprovados, base `homolog` | passa |
| CT-33 | Ramo `melhoria/catraca-ci` contra `develop` | barra: não há parecer de review de `catraca-ci` com `branch` igual no momento (esperado até o review chegar) |

## Job `segredos`
CT-34: caminho pessoal no diff barra (`docs/melhoria-continua.md:21`, valor não impresso). OK.

## Bugs
### BUG-01 (alta): renomear/mover arquivo protegido escapa da regra de protegidos
Responsável: autor de `tests/catraca.py` (tech-lead).
Passos: partir de 57b77c1; `git mv .github/workflows/ci.yml .github/ci-desligado.yml`; commitar; `python3 tests/catraca.py --base 57b77c1`.
Esperado: barrar ("mudança em .github/workflows/ci.yml"). Obtido: exit 0, sem saída. O CI inteiro deixa de rodar, e o mesmo vale para mover arquivos de `.github/rulesets/` ou `CODEOWNERS`.
Causa: `git diff --name-only` com detecção de renomeação lista só o caminho novo. Em `regra_protegidos` e em `violacoes_de_pareceres` (que também usa `SENSIVEIS`) falta `--no-renames` (com ele a saída traz o caminho antigo, verificado).
### BUG-02 (baixa): a catraca não detecta apagar/renomear arquivo que carrega invariantes ou regras
Passos: `git rm docs/regras/R-QA.md` ou `git mv agents/jarvis.md agents/jarvis-novo.md`; rodar a catraca.
Esperado: barrar. Obtido: exit 0; só `unittest` falha. Baixa porque o job de testes cobre, mas a catraca, que vale "para todos", depende dele estar verde e não ser alterado.
### BUG-03 (baixa): `pr-texto` aceita qualquer texto
Uma seção "Como medir" com `ok` passa. Aceitável como mínimo; sugerir tamanho mínimo ou revisão humana.

## Parecer
Reprovado por BUG-01 (alto): um PR consegue desligar o CI sem a catraca notar. Corrigir e reexecutar CT-15 a CT-17. Os demais cenários passam.
