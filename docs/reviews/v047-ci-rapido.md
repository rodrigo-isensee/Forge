---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-ci-rapido
commit: 5b632a48bbced4ce0a095539e11895b8d61b47c5
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (CI-RAPIDO, revalidação por delta, E1.298)

Revalidação por delta do parecer anterior (reprovado no head 88fe9ff4, E1.257). Li só `forge-check parecer delta docs/reviews/v047-ci-rapido.md` (rc=0): o intervalo é `88fe9ff4..5b632a48`, no domínio de código e testes. Os arquivos são `docs/economia-de-tokens.md`, `docs/engineering/achados-recorrentes.md`, `scripts/suite-partes.py`, `skills/ci-cd/SKILL.md`, `stacks/node-react/pronto.md`, `stacks/python/pronto.md`, `tests/mutantes/v047-ci-rapido-2.json`, `tests/test_ci_local.py`, `tests/test_forge.py` e `tests/test_suite_partes.py`. Os commits que o remoto ganhou depois (c49a3557, 778d4b18 e o merge acf6a63e) só trazem pareceres de segurança e devops, fora do domínio.

## Achados
- A1 (bloqueante) stacks/node-react/pronto.md:65 · Manda dividir "por unidade de teste, não por arquivo" com `vitest --shard K/N`, mas o Vitest divide por arquivo de teste e não usa pesos (doc do Vitest, Sharding). O texto contradiz a regra da skill ci-cd. Trocar a ferramenta ou dizer que no Vitest a divisão é por arquivo.
- A2 (recomendado) tests/test_suite_partes.py:609 · A docstring ainda diz "as 3 partes de cada versão"; são 5. Mesma classe de AR-9 (limite-antigo-no-texto), de novo neste pedido: na volta, subir AR-9 para vezes: 4, com última nesta linha.
- A3 (recomendado) skills/ci-cd/SKILL.md:57 · "medido: 36 s no PR, 20 s na integração" é o overhead do CI do Forge, numa skill que vale para todo projeto. Dizer que cada projeto mede o seu e, se quiser, citar os 36 s e 20 s como o exemplo do Forge.
- A4 (recomendado) tests/test_suite_partes.py:570 · Vem do A5 anterior, ainda aberto: o agregador da develop é conferido pelo texto do YAML. Levar o caso push na develop ao scripts/ci-local numa etapa própria.

## Sondas

## Parecer
**Reprovado** por A1. O delta corrige o bloqueante anterior e todos os recomendados que ele pedia neste PR. O texto novo do `stacks/node-react/pronto.md`, porém, receita uma ferramenta que não faz o que a frase promete.

**O A1 é requisito e defeito provado (`R-REVIEW`).** O desenho (2.4) e a skill `ci-cd` (linha 57) pedem divisão por unidade de teste, com pesos. O `vitest --shard` reparte arquivos de teste em blocos de tamanho igual, sem pesos. A documentação do Vitest diz que ele divide os arquivos e não os casos. Um projeto Node que siga o texto vai dividir por arquivo achando que divide por unidade, e "pesos regravados a cada release" não tem onde entrar. A correção cabe em uma linha: dizer que no Vitest a divisão é por arquivo (`--shard`), com a guarda de completude e o N único, ou apontar uma ferramenta gratuita que divida por caso com pesos. O `pytest-split` do `stacks/python/pronto.md` divide por teste, com os tempos gravados, e está certo.

O que o delta resolve, conferido no diff:
- **A1 anterior (bloqueante):** `tests/test_forge.py:335` agora pede "5 partes paralelas por versão de Python", e o README (linha 69) traz esse trecho. Rodei `python3 -m unittest discover -s tests -p test_forge.py -k test_readme_diz_baratas` no head e deu OK. O AR-9 subiu para 3, com a nova última linha.
- **A2 anterior:** `docs/economia-de-tokens.md:10` diz 5 partes.
- **A3 anterior:** `esperado_da_parte`, `pesos_por_modulo` e `dividir` saíram do `scripts/suite-partes.py`, junto com os testes deles. Procurei os nomes no repositório e não sobrou chamador; o `dividir` do `scripts/suite-paralela.py` é outra função. O `test_fora_da_divisao_e_modulo_do_id` segue cobrindo `fora_da_divisao` e `modulo_do_id`.
- **A4 anterior:** o M20 está marcado `equivalente` na spec, com justificativa e com `testes`. O `forge-mutante` então o roda e confirma a equivalência se os testes passarem. A justificativa está certa: NaN falha toda comparação, +inf passa de `TETO_S` e -inf fica abaixo de 0.
- **Vermelho com veredito:** em `test_ci_local.py` e `test_suite_partes.py`, `self.job()`, `self.casar()` e os `assertEqual(len(...), 1)` trocam o KeyError, o AttributeError de `None.group` e o ValueError do desempacotamento por asserção. Assim, na base, os 7 testes falham por asserção e não por erro. Nenhum caminho de sucesso mudou.
- **A6 anterior:** o orçamento de tempo e a guarda de completude estão na skill `ci-cd` e nos dois `pronto.md`, com `R-CUSTO` citado. A parte do Node é o A1 acima.

Execuções deste review: só o teste do A1 anterior (OK, acima). A trava `R-TETO` estava ocupada por outra sessão e recusou rodar as classes mudadas de `test_suite_partes` e `test_ci_local`. Não esperei por ela: a mudança nessas classes é só de forma da asserção, e a suíte inteira é do CI do PR (`R-REVIEW`), que ainda não existe, porque o brief é sem PR.

Na volta: corrigir o A1. Os A2 e A3 são baratos e podem ir junto, com o AR-9 em `docs/engineering/achados-recorrentes.md`. Como o brief desta etapa limita os arquivos ao parecer, não o gravei aqui. A revalidação é por delta.
