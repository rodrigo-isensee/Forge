---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b1-registros
commit: f7baaa533910b7af1777ad406f7bc940f8df669c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-pv-b1-registros (PR-VERDE B1, revalidação v0478 E57.26)

Volta por delta (`R-REVIEW`, H3): a rodada anterior (head `1aed3a74`, E57.13) fica no git. Delta lido: `forge-check parecer delta` de `1aed3a74..f7baaa53`; no domínio só `bin/forge-testes` (`RAMO_BUSCAVEL`, validação e `--end-of-options` em `buscar_base`, comentário do cabeçalho); fora do domínio, sem releitura: `tests/test_testes_tocados.py`, `tests/mutantes/v0478-pv-b1-registros-2.json`, `changelog.d/v0479-pv-b1-registros.md`. O aviso do delta sobre o merge `94c76b7` refere-se ao merge dos pareceres da própria branch (review, QA, segurança), já lidos.

## Gatilhos
Gatilhos: ferramenta de envio do Forge (`bin/forge-testes`, pesada em `hooks/pesado.py:46`), `git fetch` com ambiente da sessão.

## Estado dos achados anteriores
- A1 (recomendado, E57.13): corrigido em `bin/forge-testes:117` e `:920-922`. O ramo precisa casar `[A-Za-z0-9._/-]+` inteiro, não pode começar com `-` nem conter `..`; a busca usa `git fetch -q --end-of-options origin <ramo>`. Recusado, o aviso sai e não há busca; o `merge-base` seguinte sai 2 com base que não resolve. Teste: `Registros.test_ramo_que_seria_opcao_ou_refspec_e_recusado_sem_buscar` (as entradas de S1 e S2, mais `-x` e `a..b`). A classe `Registros` roda aqui: 11 testes, OK, árvore limpa.

Sondas refeitas no head `f7baaa53` (git 2.43, repositório de brinquedo com origin local, `buscar_base` carregada do arquivo).

## Sondas
- S1 · `buscar_base('origin/--upload-pack=touch $d/PWNED;git-upload-pack')` · espera: recusa sem buscar · obtido: aviso "ramo inválido", PWNED não criado
- S2 · `buscar_base('origin/+develop:refs/heads/sobrescrita')` · espera: recusa · obtido: aviso "ramo inválido", ramo `sobrescrita` não criado
- S3 · `buscar_base` com `origin/develop:x`, `origin/-c`, `origin/a..b` e `origin/develop` · espera: os três primeiros recusados, o legítimo buscado · obtido: três avisos "ramo inválido"; `origin/develop` devolve None, sem regressão

## Riscos aceitos e ferramentas
Sem risco aceito, sem achado novo. Suíte: não rodada aqui (brief: sem suíte local); o parecer conta com o CI verde no head, como o `forge-check` exige. Ferramentas ausentes no PATH: varredor de segredos, SAST e linter de workflow (lacuna registrada, `R-CUSTO`); o delta não traz segredo nem workflow.
