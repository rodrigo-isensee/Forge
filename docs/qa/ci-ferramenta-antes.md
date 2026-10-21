---
tipo: qa
contrato: 1
pedido: ci-ferramenta-antes
branch: melhoria/ci-ferramenta-antes
commit: 07bfbe856be86649836f0bdce50cb83874a6e2c5
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# Parecer de QA: ferramenta e checagens baratas antes dos testes no CI (CI-FERRAMENTA-ANTES)

Escopo: nova ordem do job `bateria` em `.github/workflows/ci.yml` (instalação e conferência do Claude Code, validação do plugin, changelog, release, "nada pula degrau", segredos e parecer antes de "Testes do Forge") e o teste `test_bateria_ferramenta_e_checagens_baratas_antes_dos_testes`. Sem UI: E2E de navegador e acessibilidade não se aplicam. Sem rede (R-CUSTO); o passo de instalação não roda aqui e depende da bateria do PR.

## Critério, teste e resultado
| Critério | Teste ou conferência | Fronteira protegida | Resultado |
|---|---|---|---|
| Ferramenta e checagens baratas antes dos testes | `tests/test_ci_local.py::test_bateria_ferramenta_e_checagens_baratas_antes_dos_testes` (posição de cada passo menor que a de "Testes do Forge"; CLI antes do validate) | ordem dos passos | passou |
| "Testes do Forge" obrigatório e igual | leitura do diff: comando `python3 -m unittest discover -s tests -v`, mesmo `if` (`!cancelled()` e pesada); teste afirma sem `for ` nem `\|\|` no `run` | sem reexecução de teste | passou |
| Sem `continue-on-error`, `[skip ci]` ou reexecução | `grep` no ci.yml (zero ocorrências de `continue-on-error`, `skip ci`, `retry`) e asserção no teste | n/a | passou |
| Instalação falha o passo se as duas tentativas falharem | sonda em `$TMPDIR`: `bash -e -c 'i(){ false; }; i \|\| { echo r; i; }; echo NAO'` imprime só `r`, rc=1 (o `echo NAO` não roda; `claude --version` também não rodaria) | segunda falha derruba o passo | passou |
| Nova tentativa só na instalação | leitura: `instalar \|\| { ...; sleep 5; instalar; }` só em `npm install`; `claude --version` confere a versão fixa 2.1.296 | uma tentativa extra | passou |

## Execução (head e24f3dcc, código 07bfbe85)
- `python3 -m unittest discover -s tests -q`: 1195 testes, OK (408 s).
- `python3 -m unittest tests.test_ci_local -q`: 50 testes, OK.
- `scripts/validar-plugin.sh`: Validation passed (rc 0).
- Vermelho antes do verde: o teste novo, rodado numa cópia em `$TMPDIR` com o `ci.yml` da develop no lugar do novo, falha (ordem antiga); com o `ci.yml` do PR passa.

## Recomendação (não bloqueia; comum aos pareceres de review, segurança e devops)
- `.github/workflows/ci.yml` (passo "Claude Code CLI"): a nova tentativa roda em qualquer falha do `npm install`, mas a mensagem diz "(rede)". Ajustar a mensagem ("falha de rede é a causa esperada") ou repetir só quando o log trouxer `ECONNRESET|ETIMEDOUT|EAI_AGAIN|ENOTFOUND`. Candidato também: shellcheck, actionlint e zizmor antes dos testes, em outra melhoria.

## Achados
