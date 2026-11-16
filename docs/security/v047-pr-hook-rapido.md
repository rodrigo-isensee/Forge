---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-pr-hook-rapido
commit: 6f3f4e7042bf32734c23ae04f1141a7a6e117162
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047 (E2.154, revalidação da PR-HOOK-RAPIDO, E2.117)

Revalidação por delta. Li a saída de `forge-check parecer delta docs/security/v047-pr-hook-rapido.md` (intervalo `8eebc2a5..6f3f4e70`, que contém a volta `5f3f9d69..6f3f4e70`). Arquivos no domínio: `hooks/parecer.py`, `hooks/conformidade.py`, `hooks/_comum.py`, `bin/forge-check`, `docs/hooks.md` e as duas fixtures novas de `tests/hooks/`. Também li o changelog, o teste e os mutantes do item. O parecer anterior (E2.142, head `8eebc2a5`) reprovou pelo A1.

## Gatilhos
Controle do Forge (hook `parecer`, `R-REVIEW`; hook `conformidade`, `R-CONFORMIDADE`). A decisão do `gh pr ready` e do `gh pr merge` usa estado local fora da árvore versionada (`<diretório comum do git>/forge/pr/<head>/`).

## Achados
- A4 (recomendado) hooks/conformidade.py:76 · A regra nova casa só o nome literal: getattr(f,'gravar_resultado'+'_do_pr') passa (S4, rc 0). Sem impacto depois do A1. Registre em docs/hooks.md, entre os limites da BP-5, que o nome montado em tempo de execução escapa.

## Sondas
- S1 · fixture de projeto com o review em `parecer: reprovado`, hook parecer com `gh pr merge feature/x --squash`, sem resultado gravado · espera: rc 2 · obtido: rc 2 (R-REVIEW, o último parecer não é aprovado)
- S2 · mesma raiz, hook conformidade, papel tech-lead: `python3 -c "import importlib.machinery as m, pathlib; f=m.SourceFileLoader('f','<clone>/bin/forge-check').load_module(); f.gravar_resultado_do_pr(pathlib.Path('.'),'p1','feature/x','develop',[])"` · espera: rc 2 · obtido: rc 2 (R-CONFORMIDADE)
- S4 · a mesma linha com `getattr(f,'gravar_resultado'+'_do_pr')(...)` · espera: rc 0 (limite da lista negativa, A4) · obtido: rc 0
- S3 · a linha da S4 executada na raiz (o JSON aprovado gravado em `.git/forge/pr/<head>/`), depois o hook parecer com `gh pr merge feature/x --squash` · espera: rc 2 · obtido: rc 2 (R-REVIEW)

## Detalhe dos achados
**Resolvidos da volta 1 (do parecer do head 8eebc2a5):**
- A1 (era bloqueante) hooks/parecer.py:567 · Fora do clone do Forge, o aprovado gravado não libera mais o gh pr merge e a conferência de hoje decide. S3 refeita: aprovado forjado sobre review reprovado dá rc 2 (R-REVIEW). O mutante PHR9 guarda a linha.
- A2 (era recomendado) hooks/_comum.py:2757 · O comentário agora descreve o limite que vale: o aprovado libera só no clone do Forge e o reprovado recusa em todo lugar.
- A3 (era recomendado) changelog.d/v047-pr-hook-rapido.md:2 · O afrouxamento está declarado (diretriz 3, só no clone do Forge), com a medida e a volta atrás; nos projetos, sem afrouxamento.

**A1, resolvido.** Em `hooks/parecer.py:567`, `if estado == "aprovado" and (gravado == EXIGE or e_clone_do_forge(raiz)): return`. Nos projetos, o `ATALHO` (ready e merge) só recusa pelo reprovado. O aprovado cai na conferência de hoje (`cmd_pr`), como antes da E2.117. O `e_clone_do_forge` (`hooks/_comum.py:76-79`) exige a ausência de `.forge/versao`. No projeto, esse arquivo é só do usuário: a conformidade o protege e o sandbox (BP-5) também. Por isso o agente não troca o projeto por "clone do Forge" para ganhar o atalho. O `EXIGE` (o `gh pr create`) segue liberando pelo aprovado gravado também nos projetos: é o risco que a PR-HOOK-PRAZO aceitou (`docs/security/v046-pr-hook-prazo.md`), compensado pelo merge, e o merge do projeto volta a conferir sem o arquivo. No clone do Forge, o ruleset (`bateria (pareceres)` e `catraca`) segue sendo o portão no servidor. Lá, o atalho só acelera (informativo, como no parecer anterior). Testes: `AtalhoNoProjeto.test_aprovado_forjado_nao_libera_o_merge_s3` e `test_aprovado_gravado_refaz_a_conferencia`; o mutante PHR9 está em `tests/mutantes/v047-pr-hook-rapido-2.json`.

**A4 · baixa · esforço P · dono: tech-lead.** A recusa de `gravar_resultado_do_pr` em `CITA_A_MARCA` é uma lista negativa (AR-3): o nome montado pelo programa não é visto. Depois do A1, um aprovado forjado no projeto só serve ao `gh pr create`, que já tinha esse risco aceito na v046, e o merge confere. Então a regra é defesa em profundidade, não portão, e o S4 não devolve. A correção mínima é de texto: em `docs/hooks.md`, na lista de limites da BP-5 ("programa que monta o caminho da marca em tempo de execução"), incluir "ou o nome da função que grava nela". O changelog, que diz que "a conformidade recusa a linha que cita gravar_resultado_do_pr", fica coerente com esse limite. Falso positivo da regra nova: só nos projetos e só em linha que cita o nome (por exemplo, um `grep` no plugin). É raro e tem saída.

**`textos_da_arvore` (bin/forge-check:355-366): sem achado.** O `cat-file` que sai com erro (`cod`) e o corpo menor que o tamanho do cabeçalho agora devolvem `{}`: nada é lido, e o `cmd_pr` reprova (falha fechada). Os testes `test_lote_com_falha_do_git_nao_le_nada` e o subcaso "corpo truncado" guardam isso, com os mutantes PHR10 e PHR11.

Conferido contra `docs/engineering/achados-recorrentes.md` (PA-7):
- AR-3: a lista negativa é o A4, aceita como defesa em profundidade.
- AR-7: a escrita e a leitura usam o mesmo `--git-common-dir`.
- AR-9: o limite antigo no texto foi corrigido pelo A2.
- AR-1 e AR-12: os mutantes PHR9 a PHR12 estão declarados com o `de` igual à linha do head. Não rodei o `forge-mutante`, que fica com o QA e o CI.

## Riscos aceitos e ferramentas
Nenhum risco aceito neste parecer. O risco do `gh pr create` com o arquivo forjável é o da v046, já aceito lá.

Testes rodados no head 6f3f4e70: `python3 -m unittest tests.test_pr_hook_rapido` (15 testes, OK, 41,8 s). As sondas S1, S2, S4 e S3 rodaram com o harness de `tests/test_hooks.py` e `tests/test_pr_hook_rapido.py` (`AtalhoNoProjeto.montar`, `rodar`) em raízes temporárias, contra os hooks e o `bin/forge-check` do head. O resto da suíte fica com o CI do PR, que não conferi: o `gh` não lê a configuração dentro do sandbox.

Ferramentas da skill fora do PATH (lacuna): gitleaks, semgrep, zizmor, actionlint, osv-scanner. Nenhuma delas é necessária a este diff.
