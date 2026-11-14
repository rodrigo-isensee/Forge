---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-ci-rapido
commit: 2165f9b1dfdeec8e2f67def0cac35290c25623a0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (CI-RAPIDO, desenho)

Intervalo `origin/develop..2165f9b1` (base 067b2a9f): só `docs/propostas/ci-rapido.md` e o fragmento `changelog.d/v047-ci-rapido.md`. Nenhum workflow, script ou teste muda neste head; o parecer é sobre o **desenho**, antes do código (etapa E1.247). O código que o realizar (o `ci.yml`, `scripts/suite-partes.py` por unidade, a anotação de tempos, `scripts/pesos-do-ci.py`) pede parecer próprio no head dele (`R-SEGURANCA`, gatilho CI).

## Gatilhos
`R-SEGURANCA`: CI e pipeline (permissões dos jobs, matriz, agregador do check exigido, prova da promoção lida por `scripts/arvore-testada.py`, artefatos entre jobs, canal de anotação de check run). Checks exigidos da proteção: `R-CONFORMIDADE` (do dono).

## Conclusão
O desenho preserva a cadeia de prova da promoção. Conferi contra o código de hoje:

- `scripts/arvore-testada.py:66-77` (`prova_valida`) exige execução `push` na `develop`, `path` igual a `.github/workflows/ci.yml`, repositório e `head_repository` iguais, e **um único** job com o nome exato de `JOBS_DE_PROVA` (`:29`), `conclusion == success`, mesmo `head_sha`, `run_id` e `run_attempt`. Um agregador com o nome de hoje, cujo sucesso só é possível com a matriz em `success`, mantém a prova válida sem mudar o script (S1). Nome de perna com "parte K/5" não colide (`len(com_nome) == 1`).
- O sucesso do agregador implica as 5 pernas executadas por duas vias independentes: o `result` agregado da matriz (`success` só com toda perna `success`; pulada, cancelada ou vermelha reprova) e o `--somar-pulados 5`, que reprova parte faltando, repetida ou de outro N (`scripts/suite-partes.py:23`, `:323-333`). A segunda é a que fecha S2: a guarda de completude de cada perna é lógica (a divisão cobre o `discover`), não prova que a perna 5 rodou; matriz `[1, 2, 3, 4]` com `--parte K/5` passaria nas 4 pernas e só o somatório reprova. Por isso o somatório tem de estar no caminho de `needs` do agregador (A1).
- Permissões (S4): o desenho dá `contents: read` às pernas e ao agregador, sem `actions`, `checks` nem token no passo da suíte; o workflow já tem `permissions: contents: read` no topo (`.github/workflows/ci.yml:24-25`). Download de artefato do mesmo run não pede escopo extra.
- Entrada não confiável (S3): só `matrix.parte`, literal do YAML, via `env:`; nada de `head_ref`, título ou branch interpolado. `pull_request_target` não entra (S8), cache novo não entra (S7), nada grava no repositório (S10).
- Checks exigidos: o desenho não renomeia `bateria`, `bateria (python 3.14)` nem `catraca`; as pernas não são exigidas, então 3 para 5 partes não toca na proteção. Não reli o ruleset pela API (a credencial do `gh` está fora do sandbox): fica como lacuna; a afirmação vem do documento e bate com os nomes de `ci.yml:392`, `:665`.
- Anotação de check run (S6): emitida por comando de workflow no passo da suíte, sem `checks: write`. No PR, a perna já roda código do autor do PR, então injetar comando pela anotação não dá a ele nada que ele não tenha; o risco real está no **consumidor** (`pesos-do-ci.py`), tratado em A2. Impacto limitado: peso só muda a partição, nunca a cobertura (guarda por ID, S9), e o resultado vira commit revisado.

Nenhum achado bloqueante: aprovado, com as recomendações abaixo como requisitos para o head do código.

## Achados
- A1 (recomendado) docs/propostas/ci-rapido.md:47 · Agregador da develop roda código da branch (checkout e --somar-pulados), contra o padrão do PR (ci.yml:337-338). Manter job de teto separado e agregador só lendo needs.*.result, com o job de teto em needs; o if dele inclui always() e a restrição de push na develop.
- A2 (recomendado) docs/propostas/ci-rapido.md:77 · pesos-do-ci.py deve aceitar só anotações de runs push na develop do ci.yml, mesmo repo e head_repository, conclusion success (filtro igual ao de arvore-testada.py:68), e unidades que existem no discover, com segundos finitos, não negativos e com teto.
- A3 (recomendado) docs/propostas/ci-rapido.md:128 · Teste de S2 deve ler o YAML e exigir, nas 4 matrizes (PR e develop, 3.12 e 3.14), lista igual a 1..N e o mesmo N em --parte K/N e --somar-pulados N; mais o caso matriz [1,2,3,4] com /5 reprovando no somatório.
- A4 (recomendado) docs/propostas/ci-rapido.md:131 · Download dos pulados sem run-id nem github-token (só artefato do run corrente, como em ci.yml:354-358), e o teste de S5 conferir a ausência dessas entradas.
- A5 (recomendado) docs/propostas/ci-rapido.md:119 · Texto do modelo de projeto: a divisão por fatia das ferramentas da stack não tem guarda de completude; exigir que o agregador confira as N pernas em success e a soma de testes executados igual à de coletados, e o plugin de divisão com versão fixa no lockfile.
- A6 (recomendado) docs/propostas/ci-rapido.md:137 · A alavanca da fila (fundir o teto ao agregador) não vale para os agregadores exigidos do PR: lá o agregador continua sem rodar código da branch; registrar isso no desenho antes de aplicar.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `docs/propostas/ci-rapido.md:47` ("baixa os 5 artefatos, roda `suite-partes.py --somar-pulados 5`") contra o comentário de `.github/workflows/ci.yml:337-338` ("fora do agregador, que não roda código da branch"). Caminho: na develop o código já passou por review, então não há atacante externo realista; o ganho é de robustez: um agregador que só compara `needs.*.result` com `success` não falha aberto por defeito de script, e o check de nome fixo que a promoção lê fica com a mesma forma do `bateria (python 3.14)` (`ci.yml:391-408`). Severidade: baixa. Correção mínima: job `teto de pulados (push na develop, ...)` com `needs` da matriz, e o agregador com `needs: [matriz, teto]`, `if: always() && github.event_name == 'push' && github.ref == 'refs/heads/develop'`, passo único que exige os dois `success`. Se o desenho mantiver o somatório dentro do agregador, a cadeia de S2 continua válida; então é recomendação. Esforço P. Dono: `devops-engineer`.

**A2.** Evidência: `docs/propostas/ci-rapido.md:77` descreve a leitura por `gh api .../check-runs/<job>/annotations` sem dizer de quais runs. Caminho: PR de fork em repositório público roda o workflow e grava anotações nos check runs dele; se o script listar check runs por nome de job sem filtrar o run, um autor externo injeta pesos (unidade inexistente, segundos absurdos, NaN). Ganho do atacante: desequilibrar partes (lentidão, timeouts de 15 min que deixam a develop vermelha), não esconder teste (S9). Severidade: baixa (há o commit revisado no meio). Correção mínima: o filtro de `scripts/arvore-testada.py:68` (evento `push`, `head_branch` `develop`, `path` do `ci.yml`, `repository` e `head_repository` iguais) mais `conclusion == success`; nomes só no alfabeto `[A-Za-z0-9_.]` e presentes no `discover`; segundos finitos em [0, teto do timeout da perna]; JSON fora do formato descarta a anotação inteira. Esforço P. Dono: `devops-engineer` (o script), `qa-engineer` (casos de abuso: anotação de PR, unidade inventada, NaN, negativo).

**A3.** Evidência: S2 em `docs/propostas/ci-rapido.md:128`; a guarda de cada perna confere a partição, não a execução. Caminho: edição descuidada (ou revisão que não vê) reduz a matriz a 4 itens; sem o somatório no caminho, a promoção pularia a suíte com 80% dela provada. Severidade: média se o somatório sair do caminho; baixa com ele. Correção mínima: o teste de `tests/test_ci_local.py` cobre as 4 matrizes e os 3 lugares do N, e o caso negativo do somatório. Esforço P. Dono: `devops-engineer` com o `qa-engineer`.

**A4.** Evidência: S5 em `docs/propostas/ci-rapido.md:131`; o padrão vigente está em `.github/workflows/ci.yml:352-358` (só `pattern`, `merge-multiple`, `path`). Caminho: com `run-id` e token, o agregador poderia ler artefato de outro run (por exemplo, de PR) e somar pulados alheios. Severidade: baixa. Correção mínima: manter a forma atual e fixá-la por teste. Esforço P. Dono: `devops-engineer`.

**A5.** Evidência: `docs/propostas/ci-rapido.md:119` (insumo para o CI dos projetos). Caminho: nos projetos, a fatia K/N da ferramenta da stack não confere a união; uma matriz com N errado ou uma fatia que coleta zero passa verde e o check exigido mente. Severidade: média para os projetos (afeta todos, `R-NEUTRO` respeitado no texto). Correção mínima: no texto de `skills/ci-cd/SKILL.md` e dos `pronto.md`, o agregador reprova perna pulada ou cancelada, reprova soma de executados diferente de coletados (ou fatia com zero testes) e a ferramenta de divisão entra com versão fixa, licença permissiva e sem custo (`R-CUSTO`). Esforço P. Dono: `devops-engineer`.

**A6.** Evidência: `docs/propostas/ci-rapido.md:137`. Caminho: no PR o workflow e os scripts vêm da branch do autor; o agregador puro é a defesa em profundidade de que o check exigido não depende de script alterável na mesma mudança. Severidade: baixa. Correção mínima: uma frase no desenho limitando a fusão à develop. Esforço P. Dono: `devops-engineer`.

Observação para o dono, sem achado: a decisão de 14/11 16:29 pediu os tempos por teste no resumo do job; a medida (`docs/propostas/ci-rapido.md:35`) mostra que o resumo não sai pela API e o desenho troca por anotação, que sai pela API sem o blob e não pede o curinga negado. Do lado de segurança a troca é neutra (sem escopo novo, sem host novo).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do desenho, de `.github/workflows/ci.yml`, `scripts/arvore-testada.py` e `scripts/suite-partes.py`; procura por credencial no diff (nada encontrado). Faltaram no ambiente (lacuna, sem instalar): `gitleaks`, `actionlint`, `zizmor`, `semgrep`, `osv-scanner`; nenhum workflow mudou neste head, e o `actionlint` e o `zizmor` do job de passos do CI valem para o head do código. Ruleset dos checks exigidos não relido pela API (credencial do `gh` fora do sandbox).
