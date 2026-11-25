---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-descendente-parecer
commit: 2364a43b8de4d3fbc87343bd2a7ffa73d9d46c04
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 E8.11 (G3.7, linha do CI aceita o run de descendente só de pareceres; #895)

## Achados
- A1 (bloqueante) bin/forge-check:2197 · so_pareceres_ate lê o `diff -z` sem `bruto=True`; o strip() do git() corta o espaço ou tab inicial do 1º caminho e ` docs/reviews/x.py` (pasta fora das três) passa como parecer (S1). Use `nomes_z(git(..., bruto=True)[1])`, como nas linhas 836 e 922, com teste.

## Sondas
- S1 · sonda_tl_espaco.py: commit sobre c0 que só cria ` docs/reviews/x.py` (pasta com espaço na raiz); so_pareceres_ate(c0, c1) · espera: False · obtido: True (git() devolve 'docs/reviews/x.py\x00')

## Parecer
Reprovado por um bloqueante (A1), de correção pequena. O resto do pedido confere.

- **O que muda:** `PROVA_DO_CI_VIA`, `so_pareceres_ate` e `leu_o_ci_via` (31 linhas em `bin/forge-check`, dentro do H1). Em `suite_do_parecer`, a linha via só esvazia `sem_ci`. A prova da suíte e o CI do head (`ci_verde_no_head`) seguem iguais, e a forma antiga, `.github` e os checks do head no merge não mudam. Nada que barra hoje deixa de barrar, salvo a via válida.
- **Sondas sobre `so_pareceres_ate`, feitas por mim:** renomeação de código para `docs/reviews/` dá False (`--no-renames`). Código apagado dá False. `Docs/reviews/` em maiúscula dá False. `docs/reviews` trocado por link para `bin` dá False (o caminho sai sem a barra final). Merge no meio que traz código dá False, porque a árvore é comparada de ponta a ponta. Um link dentro de `docs/reviews/` dá True, e está certo: não muda o código testado. Caminho com `..` não existe numa árvore do git. A única fuga é o espaço ou tab inicial do A1.
- **A1 em detalhe:** o `git()` faz `strip()` no texto. Com `-z`, só o primeiro caminho, em ordem de bytes, perde o espaço ou tab inicial, e um caminho com espaço ou tab inicial ordena antes das letras. O `bin/forge-check` já lê toda saída `-z` com `bruto=True` e `nomes_z` (linhas 412, 704, 836, 873 e 922); o código novo saiu desse padrão. O efeito prático é pequeno, porque o arquivo cai numa pasta que nada executa, mas a guarda fura o próprio contrato ("só toca docs/reviews/, docs/qa/ e docs/security/"). Correção: `nomes_z(git(raiz, "diff", ..., bruto=True)[1])` e um caso de teste com ` docs/reviews/x.py` no `LeOCiVia`. Na volta, a linha muda e o M4 e o M5 se ajustam ao texto novo.
- **O caso que motivou** (a marca da 0.47.18, com o run do sha revisado cancelado pelo envio de outro parecer) fica coberto: o descendente que só soma pareceres descende do `commit:` e o diff dele só toca as três pastas (`test_cmd_pr_aceita_o_via_so_de_pareceres`).
- **Mutantes:** `bin/forge-mutante --processos 1` nas duas specs deu M1 a M9 mortos. `--cobertura --base eeb81062` deu todas as guardas cobertas.
- **Testes:** `python3 -m unittest tests.test_forge_check_pr.LeOCiVia tests.test_pre_envio_brief` passou, 37 testes OK.
- **CI do #895 no 2364a43b:** a suíte estava pendente na leitura, e `bateria (pareceres)` e `catraca` estão vermelhos por construção. Sem aprovação, a linha `- ci:` não se aplica a este parecer.
- **Commit e fragmento:** a mensagem segue Conventional Commits em português, e o fragmento `changelog.d` está presente. As skills `engineering-practices` e `qa-testing`, o brief e o esqueleto citam a forma nova, com teste.
