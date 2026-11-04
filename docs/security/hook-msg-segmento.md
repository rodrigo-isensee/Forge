---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/hook-msg-segmento
commit: a83e730c3480e822271d0d0944e909fdaec442a9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: hook-msg-segmento (HOOK-MSG-SEGMENTO, frente 0.34, volta 2)

Revalidação do HEAD `aa2f1ea`, sobre `melhoria/k2-rec-glob` (`ec09530`). Dois commits de código: `9ee4f05` (o trecho na recusa, igual ao `9b10b25` da volta 1) e `aa2f1ea` (a máscara pedida no A1 da volta 1: `mascarado` e `TOKEN_DO_GITHUB` em `hooks/conformidade.py`).

## Gatilhos
Controles do Forge (texto da recusa do hook `conformidade`, que volta ao modelo e à pessoa): R-SEGURANCA.

## Achados
- A1 (recomendado) hooks/conformidade.py:1807 · a máscara cobre NOME=valor e ghp_/gho_/ghu_/ghs_/ghr_/github_pat_, mas não o valor depois de = em palavra que não é atribuição (http.extraHeader=Authorization: Basic …, --push-option=token=…) nem a senha de URL fora desses prefixos

## Detalhe dos achados
**A máscara não quebra a decisão.** `mascarado` e `com_trecho` só montam texto depois de a recusa já estar decidida, com operações de `str` que não levantam exceção. Comparei 11 recusas lado a lado com `melhoria/k2-rec-glob` (R-MAIN com `GH_TOKEN=`, com `env GH_TOKEN=`, com token na URL, com `-c http.extraHeader`, com `--push-option`, com `A=1 B=2`, além de R-VERIFY e de apagar o repositório): o código e o motivo são os mesmos, só com o trecho a mais. A máscara roda antes do corte em 50 caracteres, então o corte não expõe o valor.
**O que a máscara cobre.** `GH_TOKEN=***`, `env GH_TOKEN=***`, `https://x:ghp_***@…`, `--push-option=token=ghp_***`, `GH_TOKEN=***` com valor fora dos prefixos do GitHub (`glpat-…`) e o token `ghp_` solto como argumento.
**A1, o que ainda passa.** `git -c http.extraHeader='Authorization: Basic <b64>' push origin main` recusa por R-MAIN e cita `http.extraHeader=Authorization: Basic c2Vn…`, com os primeiros caracteres do valor. O nome antes de `=` tem ponto, então não conta como atribuição. Caminho de ataque: nenhum público novo, porque o comando já está na transcrição e na tela, e `barrar` não grava log. Por isso fica como recomendação. Correção mínima: em `mascarado`, mascarar o que vem depois do primeiro `=` de qualquer palavra que tenha `=`, a userinfo de URL (`://usuário:senha@`) e o que vem depois de `Authorization:`, `Bearer` e `Basic`. Severidade: baixa. Esforço: P. Dono: o autor da trilha.
O restante segue como na volta 1. Os controles e formatos saem do trecho, a crase vira `'` e o `Corrigir:` do hook nunca é cortado. O `Corrigir:` que vem escrito no comando fica dentro do trecho, entre crases, e a mensagem não ensina contorno novo.
A pilha herda os bloqueantes A1 a A3 de `docs/security/hook-continuacao-linha.md`. Este commit não os toca nem os agrava.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados (D-5): `tests.test_hooks.Hooks.test_fixtures`, `test_fixtures_da_trilha_034`, `test_trecho_so_entra_se_a_linha_inteira_cabe` e os testes novos da pilha. `gitleaks` e `semgrep` fora do PATH (lacuna; não instalados, R-CUSTO).
Resultado: `test_fixtures`, `test_fixtures_da_trilha_034` e os testes novos da pilha passaram (Ran 9 tests, um deles é um nome errado no comando do revisor, que o unittest acusa como ERROR do loader; não é falha do código). Parecer concluído depois da troca de conta, sobre o mesmo HEAD.

Atualização (2026-11-04): só o `commit:` passa ao HEAD `a83e730`, reaplicado sobre a hook-continuacao-linha `a04096b`. O delta é o mesmo deste parecer; comparei com diff e só mudam os números de linha e o contexto. O veredito não muda. A pilha agora herda os bloqueantes A5 e A6 de `docs/security/hook-continuacao-linha.md` (volta 2), no lugar dos A1 a A3.
