---
tipo: revisao-seguranca
contrato: 1
pedido: teto-heredoc
branch: melhoria/teto-heredoc
commit: c3192f2fff7438da32036402d88a8add0b5e3021
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: teto-heredoc

Etapa E1.3 do pedido `docs/pedidos/teto-heredoc.md`, item E1. Diff lido: `ce57f2d..c3192f2` (2 arquivos: `tests/test_hooks.py` +23/-2, `changelog.d/teto-heredoc.md` +2). Controles cobrados: C-1 a C-6 de `docs/security/ameacas/teto-heredoc.md`.

## Gatilhos
`R-SEGURANCA`: controles do Forge (o teste que guarda o prazo do hook `conformidade`, cuja perda de prazo libera a chamada). Item entregue: E1 (o teste do orçamento de heredocs deixa de medir a montagem do fixture e acrescenta a cobrança de CPU dos filhos, sem mudar o teto).

M14 (`agents/tech-lead.md:19` da develop): 25 linhas contadas (`tests/test_hooks.py`; o fragmento de `changelog.d/` fica fora), abaixo de 150; um comportamento só; nenhum arquivo de `hooks/` nem de `PROTEGIDOS`. Cumpre.

## Achados
- A1 (recomendado) tests/test_hooks.py:1817 · C-1 lista montar_proc e executar_passos como fora da janela, mas executar_fixture os roda dentro dela (:633, :638). Só endurece (mede a mais, nunca a menos); vale alinhar o texto do modelo ou o comentário de :1814 para não confundir quem ler.
- A2 (recomendado) tests/test_hooks.py:72 · RUSAGE_CHILDREN soma qualquer filho colhido na janela, inclusive Popen órfão de outro teste colhido por subprocess._cleanup; o erro só reprova (C-3), mas a mensagem de CPU pode apontar o hook sem ser ele. Basta registrar no comentário.

## Detalhe dos achados
Conferência dos controles:
- C-1: a janela (`tests/test_hooks.py:1816-1818`) cobre `executar_fixture` inteiro, com o `subprocess.run` do hook (partida do lançador, stdin, `git` esperados). Só `Fixture.montar` (`:1814`) sai. Nada de produção fica fora. A1 é só divergência de texto, e no sentido mais estrito.
- C-2: as duas asserções usam `limite / 2`, com `limite` lido de `hooks/hooks.json` como antes. Sem constante nova, sem `skip`, `retry` nem `expectedFailure`.
- C-3: o teste roda na thread principal, fora do pool (`:604`); `cpu_antes` é lido depois da montagem, cujos `git` já foram colhidos. Ver A2 (informativa).
- C-4: `executar_fixture` continua conferindo código 2 e o stderr `R-MAIN: push direto para main`; o caminho com `montado=` é o mesmo que o pool usa.
- C-5: sem `resource`, `_cpu_dos_filhos` devolve `None` e só a asserção de parede vale, com o mesmo número.
- C-6: diff restrito a `tests/test_hooks.py` e `changelog.d/`; nenhum hook, `hooks.json` nem `tests/config.json` muda.

Afrouxamento: parede só do hook <= parede total de antes, e a CPU só acrescenta reprovação. Um hook que espera ocioso 6 s ainda reprova pela parede (A2 do modelo, a provar no QA E1.4). Não afrouxa (DECISÃO DO DONO de 2026-10-15).

Execução local: `python3 -m unittest tests.test_hooks.Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento` → `Ran 1 test in 4.383s OK` (load 1,62).

A1 e A2: severidade informativa, esforço P, dono `tech-lead` (só texto); não devolvem.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Resíduo do modelo mantido: sob carga extrema a parede do hook ainda pode passar de 5 s; não se corrige afrouxando o número. Ferramentas: leitura estática e o teste local; `gitleaks`, `semgrep` e `zizmor` não estão no PATH (lacuna; o diff não traz segredo nem workflow).
