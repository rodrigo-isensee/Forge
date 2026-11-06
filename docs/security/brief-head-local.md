---
tipo: revisao-seguranca
contrato: 1
pedido: versao-034
branch: melhoria/brief-head-local
commit: f7e34819f8402d6e6e1c6b049c21e4d7903d42d3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-05
---
# Review de segurança: versao-034, E2 BRIEF-HEAD-LOCAL

Delta revisado: `360186e..10c3703` (`bin/forge-check`, `agents/conferente.md`, `docs/regras/R-BRIEF.md`, `tests/test_etapa_do_brief.py`, `tests/test_forge.py`, `changelog.d/brief-head-local.md`). Revisão estática e defensiva contra a seção E2 de `docs/security/ameacas/versao-034.md` (controles C-1 a C-9, proibições T-1 a T-5, casos de abuso 1 a 14). A implementação segue a leitura estreita do cartão; a leitura larga (A7) não entrou.

## Gatilhos
Controles do Forge: a mudança altera a pré-condição `commit:` da R-BRIEF e a linha `review`, `seguranca` da tabela do conferente. Pede o rótulo `afrouxa-regra` e o aceite do dono na E1.8 (R-CONFORMIDADE, R-DECISAO); o changelog já o cita.

## Achados
- A1 (recomendado) bin/forge-check:4917 · PASTAS_DE_PARECER redefine a constante de :961 (usada por delta --parecer em :1641 e :1765). Hoje só muda a ordem da mensagem (dentro_da_raiz tira a barra), mas a sombra acopla as duas listas sem querer; dar outro nome ou reusar a de :961.
- A2 (recomendado) tests/test_etapa_do_brief.py:592 · falta o teste do abuso 14 (C-7): parecer só local dá "sem parecer da branch" em forge-check pr --ref origin/<b> até o envio. cmd_pr não mudou e lê da ref (bin/forge-check:909): regressão sem teste, não defeito.
- A3 (recomendado) bin/forge-check:4936 · a troca só do bit de execução (100644 para 100755) de um parecer passa como M. Sem caminho de ataque (o .md não é executado); recusar para alinhar com a dimensão da matriz, ou registrá-la como aceita.

## Vereditos por controle
- C-1 cumprido: a exceção só roda com `conferido` e `remota` verdadeiros (`bin/forge-check:4960`); `remoto_da_branch` devolve `conferido` False no ref de rastreio (:4912-4914); R ausente como objeto local faz `merge-base --is-ancestor` falhar (:4926). Teste: `test_so_o_ref_de_rastreio_sem_remoto_conferido_nao_concede_a_excecao` (`tests/test_etapa_do_brief.py:583`).
- C-2 cumprido: `e_ancestral(raiz, remota, head)` antes de tudo (:4926); remoto vazio no `ls-remote` dá `remota` None e não entra na exceção (:4960). Teste: `test_head_que_nao_descende_do_remoto_ou_com_remoto_ausente_reprova` (:568).
- C-3 cumprido: diferença de árvore `remota..head` por `git diff --raw -z --no-renames --no-ext-diff --no-textconv` (:4928), lida em pares NUL, falha do git e saída ímpar reprovam (:4929-4933), `com_controle` reprova (:4937). Sem log por commit. Teste: subteste `controle` de `test_head_a_frente_so_vale_para_arquivo_novo_ou_alterado_comum` (:539).
- C-4 cumprido: lista branca própria (:4917-4918), sem `LIVRES`; recusa `/_`, `ameacas/`, `aceites/` e todo o resto (:4936-4938), com prefixo exato com barra (`docs/securityx/` cai). Testes: :529 (bin, tests, aceites, ameacas, KANBAN, kanban, ux, modelo, securityx) e `test_a_lista_de_pareceres_do_forge_check_e_a_do_pre_push` (:592).
- C-5 cumprido: só A e M com modo de arquivo comum, antes e depois (:4936); D, T, symlink (120000) e gitlink (160000) reprovam. Teste: subtestes `apagar` e `symlink` (:539). Ver A3.
- C-6 cumprido: `ETAPAS_COM_PARECER_A_FRENTE` = review, seguranca, qa (:4919, :4960); `codigo` sai antes (:4951). Teste: `test_head_a_frente_nas_etapas_de_branch_inteira_continua_reprovando` (:559) para pr, merge-integracao e pedido-de-merge-ao-dono.
- C-7 cumprido no código: `commit_vale` e `cmd_pr` fora do diff; o `pr` lê os pareceres da ref (:909). O teste pedido falta (A2).
- C-8 cumprido: linha `aviso: commit:` com head, remoto, contagem e "envie antes do PR" (:4963-4964), com rc 0. Teste: :518 (4 pastas por 3 etapas). Na reprovação, o arquivo fora sai por `nome_seguro` (:4967).
- C-9 cumprido: a tabela do conferente muda junto (`agents/conferente.md:99`) e manda copiar a linha `commit:` ou `aviso: commit:` do `forge-check brief`, sem leitura própria: uma fonte só, sem a divergência que um segundo comando traria. Teste: `tests/test_forge.py:5540`.
- T-1 cumprido: nenhuma comparação com `Head-sha`; a exceção exige C-2 e C-4 (:4926-4938).
- T-2 cumprido: `LIVRES` e `PASTAS_LIVRES` não aparecem no novo código.
- T-3 cumprido: sem `conferido`, nenhuma exceção (:4960).
- T-4 cumprido: o diff de `bin/forge-check` toca só :4916-4967; `commit_vale`, `cmd_pr` e a linha `pr` do conferente não mudam.
- T-5 cumprido: nenhuma mensagem nem doc sugere `--force`, `--amend` ou `--no-verify`; a mensagem pede `git fetch origin` ou `git push origin <branch>`.

## Casos de abuso
- 1 código no intervalo: reprova, `bin/forge-check` e `tests/t.py` (:529).
- 2 aceite forjado: reprova (:529).
- 3 KANBAN, kanban e ux: reprova (:529).
- 4 modelo `_modelo.md`: reprova (:529).
- 5 amend: mesma topologia de divergência do caso 6, pelo mesmo `e_ancestral` (:4926); coberto por :568.
- 6 remoto andou: reprova (:568).
- 7 sem rede, só ref de rastreio: reprova (:583).
- 8 branch nunca enviada: reprova (:568, segunda metade).
- 9 nome com quebra de linha: reprova (:539).
- 10 symlink: reprova (:539).
- 11 apagar parecer alheio: reprova (:539).
- 12 etapa pr: reprova (:559).
- 13 legítimos: passam com `aviso:` (:518); head igual ao remoto segue nos testes antigos da classe.
- 14 `cmd_pr --ref origin/<b>` sem envio: comportamento garantido por construção (:909), sem teste próprio (A2).

## Detalhe dos achados
- A1: evidência `bin/forge-check:961` e `:4917`; caminho de ataque: nenhum hoje (mesmo conjunto, `dentro_da_raiz` normaliza a barra em :1603); risco é de manutenção, uma pasta nova em `PASTA_E_REGRA` sumiria do `delta --parecer` (falha fechada, não aberta). Severidade informativa. Correção: renomear a nova constante (por exemplo `PASTAS_DO_SO_PARECER`) e ajustar o teste :592. Esforço P. Dono: forge:tech-lead.
- A2: evidência `bin/forge-check:909`; severidade baixa (A6 do modelo). Correção: um teste em `tests/test_etapa_do_brief.py` que, depois do caso 13, roda `forge-check pr <p> --ref origin/melhoria/x` e espera "sem parecer da branch". Esforço P. Dono: forge:qa-engineer.
- A3: evidência `bin/forge-check:4936`; severidade informativa. Correção: exigir `antigo == novo` no M, ou registrar a dimensão como aceita no modelo de ameaças. Esforço P. Dono: forge:tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito por este parecer; o afrouxamento do texto da R-BRIEF depende do rótulo e do aceite do dono na E1.8. Ferramentas: leitura do diff e `bin/forge-testes bin/forge-check` (resultado no relatório ao Jarvis). Lacunas no PATH: `gitleaks` e `semgrep` ausentes (o delta não traz segredo nem dependência; as varreduras seguem no CI).

## Confirmação
Delta revisado: `338eacf..f7e3481` (`bin/forge-check`, `tests/test_etapa_do_brief.py`; três commits: 138b6fc, 9717fa3, f7e3481). Revisão estática e defensiva; `python3 -m unittest tests.test_etapa_do_brief`: 74 testes, OK.
- A1 fechado: a constante nova chama-se `PASTAS_DO_SO_PARECER` (`bin/forge-check:4917`, uso em :4937) e a `PASTAS_DE_PARECER` de :961 voltou a ser única; o teste :626 usa o nome novo.
- A2 fechado: `test_parecer_so_local_a_frente_do_remoto_continua_sem_parecer_no_pr_pela_ref_do_remoto` (`tests/test_etapa_do_brief.py:599`) prova o abuso 14: válido na ref local, "review: sem parecer" em `--ref origin/<b>`, rc 1. O A1 do review ganhou também o teste de amend (:583), que afirma a reprovação pela ancestralidade (C-2, abuso 5).
- Os 9 controles (C-1 a C-9) seguem valendo: o delta de código é só a troca do nome da constante, sem mudar lógica, lista branca, `commit_vale` nem `cmd_pr`. Nenhum falha aberto.
- A3 segue recomendado e fora desta volta (cartão BRIEF-HEAD-LOCAL-AJUSTES); não devolve. Sem risco aceito novo; o rótulo `afrouxa-regra` segue na E1.8.
Veredito: aprovado.
