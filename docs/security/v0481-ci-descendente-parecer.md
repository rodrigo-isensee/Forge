---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-descendente-parecer
commit: 2364a43b8de4d3fbc87343bd2a7ffa73d9d46c04
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 E8.13 (G3.7, linha do CI aceita o run de descendente só de pareceres; #895, classe C)

## Gatilhos
Gatilhos: controle do Forge (portão `forge-check pr`, PARECER-LE-O-CI), analisador de caminhos do diff

## Achados
- A1 (bloqueante) bin/forge-check:2197 · so_pareceres_ate lê o diff -z sem bruto=True; o strip() do git() tira espaço, tab ou quebra inicial do 1º caminho e ' docs/reviews/x.py', '\ndocs/qa/x.py' e '\tdocs/security/x.py' (fora das três pastas) passam (S1). Concordo com o A1 do review: nomes_z(git(..., bruto=True)[1]) e teste.
- A2 (bloqueante) skills/qa-testing/SKILL.md:46 · o texto novo estoura o orçamento: tests/test_orcamento_instrucao.py:86 falha (qa-engineer 21650 > teto 21480; tech-lead marcadores 57 > 56, por skills/engineering-practices/SKILL.md:54); suíte parte 3/5 vermelha no CI do 2364a43b nas duas versões (S2). Encurte o texto; subir o teto é afrouxar.

## Sondas
- S1 · sonda_via2.py: commit c1 sobre c0 que só cria ' docs/reviews/x.py' (e, em repos à parte, '\ndocs/qa/x.py' e '\tdocs/security/x.py'); so_pareceres_ate(c0, c1) · espera: False · obtido: True nos três
- S2 · python3 -m unittest tests.test_orcamento_instrucao no 2364a43b (no eeb81062: OK) · espera: OK · obtido: FAILED (qa-engineer total_caracteres 21650 passa do teto 21480; tech-lead marcadores 57 passa do teto 56)

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:2197` usa o `git()` em modo texto, que faz `strip()` (`bin/forge-check:603`). Com `-z`, só o primeiro caminho em ordem de bytes perde o branco inicial, e um caminho que começa com espaço, tab ou quebra de linha ordena antes de `d`. Caminho de ataque: quem escreve a linha `via` (um portão) aponta um descendente que, além do parecer, cria ` docs/reviews/x.py` na raiz; a guarda diz "só pareceres" e o contrato G3.7 fura. Severidade baixa: nada executa essa pasta, o código revisado segue igual byte a byte e o merge exige todos os checks do head; ainda assim, é a guarda nova falhando no próprio contrato. Correção mínima: `nomes_z(git(raiz, "diff", "--name-only", "--no-renames", "-z", sha, via, "--", bruto=True)[1])`, rc conferido, e um caso em `LeOCiVia` com os três prefixos brancos (espaço, tab, quebra); os mutantes M4 e M5 se ajustam ao texto novo. Alternativa que fecha a mesma família: reusar o critério de `so_pareceres_a_frente` (`bin/forge-check:7859`): só A e M, modo 100644 ou 100755, sem `com_controle`, sem `/_`, fora de `docs/security/ameacas/` e `docs/security/aceites/`. Esforço P. Dono: autor da E8.10.

**A2.** Evidência: o CI do #895 no `2364a43b` tem `suíte (python 3.12, parte 3/5)` e `suíte (python 3.14, parte 3/5)` em failure com `test_orcamento_instrucao.Orcamento.test_nenhum_agente_passa_do_teto` (job 139109944931), reproduzido à mão (S2); no `eeb81062` o mesmo teste passa. Não é achado de segurança, mas é defeito provado e deixa o CI do sha revisado vermelho: sem CI verde, nenhum portão aprova (PARECER-LE-O-CI). Correção mínima: encurtar as frases novas das duas skills (por exemplo, citar só "G3.7" e a forma `verde via <sha40>`, deixando as pastas no `bin/forge-check`) até `test_orcamento_instrucao` passar, sem mexer no teto. Esforço P. Dono: autor da E8.10.

## Parecer
Reprovado por A1 e A2, ambos de correção pequena. Fora deles, a mudança está correta.

- **O que aperta:** nada no merge. A forma `via` só esvazia a violação `sem_ci` de `suite_do_parecer` (`bin/forge-check:2227`) e exige que o descendente descenda do `commit:` e que o diff fique nas três pastas (mais estrito que o atalho do CI em `.github/workflows/ci.yml:634`, que aceita também `docs/devops/` e `docs/ux/`).
- **O que é neutro:** a forma antiga (`PROVA_DO_CI` segue ancorada em `verde[ \t]*$`, então a linha `via` não passava antes nem passa por ela agora). Seguem iguais `falta_na_prova`, o `ci_verde_no_head` fora do `--previo`, `.github` e todos os checks do head no merge (passos 4 e 6 do `forge-fechar`). A linha `- ci:` continua sendo uma declaração do portão, não lida no gh, nas duas formas.
- **O que afrouxa:** só o caso pedido, o parecer cujo `commit:` teve o run cancelado. Ele passa a valer com o run de um descendente cujo código é idêntico ao revisado. Com A1 corrigido, não há caminho para que esse run seja de código diferente.
- **Sondas sobre `so_pareceres_ate` (sonda_via.py, repos descartáveis):** renomeação de código para a pasta do parecer dá False (`--no-renames` lista a origem). Pasta `docs/qa` trocada por link dá False (sai `docs/qa` sem a barra). `Docs/QA/` em maiúscula dá False. Merge no meio com código dá False (a comparação é de árvore a árvore). Um sha que não descende ou não existe dá False (rc 1 ou 128). Dentro das três pastas, link para `../../bin/forge-check`, gitlink, arquivo apagado, `_modelo.md`, aceite apagado e modo executável dão True. Isso é neutro: nenhum deles muda um byte do código fora de `docs/`, o checkout do CI não inicia submódulo e o merge lê os pareceres no head. O `..` não existe num caminho de árvore do git. Gitlink fora das pastas só some com `diff.ignoreSubmodules=all` na configuração local (protegida pelo sandbox), sem efeito no código testado.
- **O caso que motivou** (marca da 0.47.18) se repetiu aqui: o envio do parecer de review (`b46fbbfa`, só `docs/reviews/`) cancelou as partes 1 e 4 da suíte no `2364a43b`. A forma `via` cobre esse caso (`test_cmd_pr_aceita_o_via_so_de_pareceres`), mas o run do descendente também terá a parte 3/5 vermelha por A2.
- **Testes e mutantes:** `python3 -m unittest tests.test_forge_check_pr.LeOCiVia tests.test_forge_check_pr.LeOCiNoCmdPr tests.test_pre_envio_brief.ChecksForaDaLinhaDoCi` deu 23 OK. `bin/forge-mutante` nas duas specs deu M1 a M9 mortos.
- **CI do #895 no `2364a43b`:** vermelho na suíte parte 3/5 (A2). Partes 1 e 4 canceladas, e `bateria (pareceres)` e `catraca` vermelhos por construção. Sem a linha `- ci:` (o parecer não aprova).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, a biblioteca padrão e `gh` (leitura de checks e do log do job). Não usei gitleaks nem osv-scanner: o diff não traz segredo nem dependência.
