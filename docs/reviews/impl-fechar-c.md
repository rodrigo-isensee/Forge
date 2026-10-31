---
tipo: review
contrato: 1
pedido: impl-fechar-c
branch: melhoria/impl-fechar-c-c1
commit: ee73f7da97bc7b9448af69a262c187fd8ae590e0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-fechar-c (branch c1)

Etapa E1.2, revisor de outra instância (D-ETAPAS-INST = A). Diff lido: `234dbe0..ee73f7d` (4 commits: correção do C1, teste vermelho do C1-2, correção do C1-2, fragmento).

## Item entregue
E1 do pedido, FECHAR-R1-WORKTREE com o C1-2 do modelo de ameaças: pendência por commit sem merge imprime leitura (`git log --oneline <base>..<ref>`, argumentos com `printf '%q'`) e não o comando que apaga, em `limpar_entrega` (worktree, branch local, aviso de quem está na worktree sem outra para sair, remota pelo sha lido do servidor) e no bloco do `--sem-limpar` (local e remota relidas ali). Bate com o desenho (`fechar-c.md` §2 E1, (b) 1 a 3). Com sha mesclado o comando continua (teste AB-C1-6).

## M14 (R-REVIEW, agents/tech-lead.md:19)
- Um comportamento só: a troca do comando que apaga pela leitura, quando há commit sem merge. O C1-2 é o mesmo comportamento no segundo caminho que imprime a pendência; separá-lo deixaria o `docs/fechamento-integrador.md` contraditório entre dois PRs (o motivo da volta da rodada 3 da conferência).
- Teto: 192 linhas contadas (`bin/forge-fechar` 48+7, `tests/test_fechar_r1_worktree.py` 137+0; fora o `.md` e o fragmento). Passa de 150. O PR não mexe em `hooks/` nem em caminho de `PROTEGIDOS` (`tests/catraca.py:43-45`; `bin/forge-fechar` não está na lista), então a exceção cabe. **Exceção aceita neste review**, com a condição do A1: o corpo do PR leva a linha `teto: excedido, 192 linhas, um comportamento em dois caminhos (limpar_entrega e --sem-limpar), 137 delas de teste` (pelo `--muda` do `forge-fechar`). Sem a linha no corpo, vale o bloqueante da M14.

## Checklist
1. Faz o pedido, nem mais nem menos: sim. 2. Regras: nada apaga a mais nem confere a menos (R-VERIFY, aperta); R-CUSTO e R-NEUTRO sem efeito. 3. Legível: a função `leitura_sem_merge` evita repetir o texto em três lugares; `leitura_dada` impede a linha duplicada entre worktree e branch. 4. Erros: leitura da remota que falha no `--sem-limpar` imprime só aviso, sem comando (falha fechada). 5. Segurança: nada novo além do que o modelo de ameaças cobre (C1-2); a E1.3 julga. 7. Testes: 7 casos (worktree com commit novo, worktree principal, remota sem merge, as duas variantes do `--sem-limpar`, ref com caractere do shell, regressão do sha mesclado). 9. Commits: Conventional Commits, o vermelho do C1-2 separado. 12. O `gh` falso é o da suíte; o `ls-remote` é o real contra o origin temporário (nome exato pelo `remoto_exato`).

Ferramentas: módulos `tests/test_fechar*.py` rodados na worktree, sem bytecode: `Ran 209 tests in 109.582s` / `OK (skipped=1)`. `bin/forge-testes --listar` dá suíte completa (`bin/forge-fechar sem mapa`), então os módulos novos são alcançados. Shellcheck: não instalado aqui; fica com o CI (o `forge-fechar` está na lista dele), pendência registrada, não revisão manual.

## Achados
- A1 (recomendado) tests/test_fechar_r1_worktree.py:1 · PR acima do teto da M14 (192 linhas); exceção aceita neste review só com a linha teto: excedido, 192 linhas, <motivo> no corpo do PR, pelo --muda do forge-fechar na E1.5; sem ela, o achado vira bloqueante pela M14.

## Parecer
Aprovado. Correção mínima, falha fechada, coberta por teste vermelho antes do verde; a exceção ao teto vale com a linha no corpo do PR (A1).
