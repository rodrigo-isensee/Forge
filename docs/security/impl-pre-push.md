---
tipo: revisao-seguranca
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c4
commit: ddb7768b06e3dd2e3a75a70dad96d830ceefc411
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-pre-push (branch c4)

Diff revisado: `234dbe0..ddb7768` (primeira revisão em `9cdd920`) (código em `a515d73`, fragmento em `aff0ec2`, parecer do code review em `9cdd920`). Análise estática contra o modelo de ameaças `docs/security/ameacas/pre-push.md` (controles C-9 a C-13 e C-15, casos de abuso 7 a 11; Q-S1 = B).

Aprovado **com a condição de ordem** já registrada no A1 do code review: a c4 só entra na develop junto com a c6 (C-14) ou depois dela. Ver A1 abaixo.

## Revalidação no head ddb7768 (volta por delta)
`forge-check delta --parecer` listou `tests/test_pre_push_trava.py` +5 -1, trechos 535-538 e 540 (commit `14b155b`, subcaso "comum link pendente" do C-9, A1 do QA). Li esses trechos e a volta do QA: só teste, nenhum código de produção nem controle mudou; o caso exerce o `-L` de `.githooks/pre-push:18-19` já conferido (link quebrado dá rc 1 sem recuo) e fecha o abuso 7 para o link pendente. Sem novo caminho de ataque. A ordem do A1 está cumprida: a c6 (C-14) já entrou na develop (3c35fcd, PR 397). Linhas de A2 e A3 deslocadas pelo delta (555 e 601). Parecer segue aprovado.

## Gatilhos
`R-SEGURANCA`: controle do Forge (`.githooks/pre-push`), pasta da trava e fronteira do sandbox (ADR 0009).

## Item entregue e M14
- Entrega o E3 do pedido (TRAVA-SANDBOX, C4 do desenho) sem o C-14, que foi para a c6.
- M14: 146 linhas de código e teste (`.githooks/pre-push` 20; `tests/test_pre_push_trava.py` 118; 2 em cada um de `tests/test_pre_push_afetados.py`, `tests/test_pre_push_parecer.py`, `tests/test_pre_push_parecer_curto.py` e `tests/test_suite_paralela.py`), abaixo do teto; um comportamento só (trava e fila na pasta comum, com o `HOME` temporário dos testes como condição dele). Cumpre.

## Conferência dos controles
- C-9: `.githooks/pre-push:18-19` usa `-e` ou `-L` e, com a pasta comum presente, ela é o único candidato. Arquivo no lugar, link quebrado ou pasta sem escrita não passam em `-d`/`-w` e dão rc 1 sem tentar `XDG_RUNTIME_DIR` nem `TMPDIR`. Só `HOME` vazio ou pasta comum ausente mantém a ordem antiga.
- C-10: a subpasta comum passa pelas mesmas conferências da de recuo (mesmo laço); link para pasta em `~/.forge-contrib` é aceito, como o modelo prevê. A conferência do modo vem do C1 (c1), que está no mesmo laço e passa a valer para a comum quando as duas estiverem juntas.
- C-11: o `--status` resolve a mesma trava (`:96`); sem subpasta, devolve o caminho sem criar nada; teste `test_status_com_pasta_comum_e_sem_subpasta_nao_cria_nada`.
- C-12 (Q-S1 = B): `:179` deriva as provas de `trava_arquivo criar legado`, que ignora a pasta comum; se falhar, `verde` e `dirigida` ficam vazias, `tem_prova` falha e `anotar` não grava (`[ -n "$1" ]`): falha fechado, a suíte inteira roda. Teste T-C4g presente.
- C-13: os cinco módulos que rodam o hook ganham `HOME` temporário; teste estrutural `tests/test_pre_push_trava.py:590-597`.
- C-15: o fragmento avisa da transição das worktrees abertas.
- Casos de abuso 7, 8, 9, 10 e 11 cobertos por `test_pasta_comum_presente_e_recusada_nao_recua`, `test_dentro_e_fora_do_sandbox_usam_a_mesma_trava`, `test_prova_de_um_lado_nao_dispensa_a_suite_no_outro` e o teste estrutural; o modo frouxo do caso 7 depende do C1 (A2).

## Achados
- A1 (recomendado) .githooks/pre-push:106 · Sem o C-14, o texto da trava gravado de dentro do sandbox é impresso sem filtro no terminal de fora (:106, :226). A c4 só entra na develop junto com a c6 ou depois dela (ordem do A1 do code review). Dono: tech-lead.
- A2 (recomendado) tests/test_pre_push_trava.py:555 · O assertIn(codigo, (1, 2)) só cabe enquanto a c2 não está na base, e falta o subteste de modo 0o777 da T-C4b (C1). Juntas c1, c2 e c4: fixar rc 2 e acrescentar o subteste. Dono: tech-lead.
- A3 (recomendado) tests/test_pre_push_trava.py:601 · O teste do C-13 aceita HOME= em qualquer ponto do módulo e só reconhece a forma [str(HOOK). Endurecer: exigir HOME no dict passado ao processo do hook. Dono: tech-lead.

## Detalhe dos achados
- A1: evidência `.githooks/pre-push:106` e `:226` (`cat "$trava"` sem filtro). Caminho: um comando de dentro do sandbox grava sequência de escape na trava comum; o `--status` ou o aviso de espera de fora a imprime no terminal do dono (A5 do modelo). Severidade baixa. Correção mínima: a c6 (C-14: até 200 bytes, sem caracteres de controle) entra antes ou com a c4; nenhuma mudança nesta branch. Esforço P. Dono `tech-lead` (integração). Se a ordem não puder ser mantida, a c4 volta à segurança antes do merge.
- A2: evidência `tests/test_pre_push_trava.py:535-552`. Sem caminho de ataque (lacuna de cobertura; o código fecha os dois casos depois da junção). Severidade informativa. Correção mínima: `assertEqual(codigo, 2)` e um subteste com a subpasta comum em 0o777. Esforço P. Dono `tech-lead`.
- A3: evidência `tests/test_pre_push_trava.py:592-597`. Sem caminho de ataque; um teste novo que rode o hook por `["bash", str(HOOK)]` ou que defina `HOME` só em outro ambiente passaria e voltaria a tocar a trava real (T-4d). Severidade baixa. Correção mínima: ampliar o padrão de execução e conferir o `HOME` no ambiente passado. Esforço P. Dono `tech-lead`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Leitura do diff e do hook no commit revisado. `shellcheck` e `gitleaks` ausentes do PATH nesta máquina (lacuna; o CI roda o `shellcheck` no hook). Nenhuma ferramenta instalada.
