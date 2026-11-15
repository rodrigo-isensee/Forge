---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-ci-rapido
commit: 88fe9ff40c95a8cae5565c6ea7105117f0a8f4dc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (CI-RAPIDO, implementação)

Intervalo revisado: `067b2a9f..88fe9ff4` (a base do brief; o `origin/develop` andou para `c5c3a449` e o diff contra ele mostra arquivos da develop que não são desta entrega). O código é o commit `88fe9ff4` (E1.248): `.github/workflows/ci.yml`, `scripts/suite-partes.py`, `scripts/pesos-do-ci.py` (novo), os testes deles, os mutantes e o texto do modelo de projeto `templates/projeto/docs/engineering/protecao-de-branch.md`. Este parecer substitui o do desenho (`2165f9b1`, E1.247), cujos A1 a A6 eram requisitos para este head.

## Gatilhos
`R-SEGURANCA`: CI e pipeline (permissões, matriz, agregador de nome fixo lido como prova da promoção por `scripts/arvore-testada.py`, artefatos entre jobs, emissão de comando de workflow em anotação, script que lê a API com token). Checks exigidos da proteção: `R-CONFORMIDADE`.

## Conclusão
Aprovado, sem achado. Os seis requisitos do desenho estão no código e testados:

- **A1 (agregador sem código da branch).** `rapida` e `rapida-quatorze` (`.github/workflows/ci.yml:121-137`, `:227-243`) não fazem checkout: só comparam `needs.<matriz>.result` e `needs.<teto>.result` com `success`, com `if: always() && push && refs/heads/develop`. O teto roda em job próprio (`:95-119`, `:201-225`) nos `needs` do agregador. Perna vermelha, pulada ou cancelada reprova; teto pulado (porque a matriz falhou) também. Os nomes dos agregadores são os de `JOBS_DE_PROVA` (`scripts/arvore-testada.py:29`), que não mudou; as pernas ("suíte (push na develop, ...)") não colidem com a exigência de um único job com o nome. Teste: `tests/test_ci_local.py` (needs exatos dos dois agregadores e nenhum `scripts/` no passo deles).
- **A2 (consumidor dos tempos).** `scripts/pesos-do-ci.py:49-54` aceita só execução `push` na `develop` do `ci.yml`, `repository` e `head_repository` iguais ao `--repo`, `completed` e `success`; `:57-63` só job de perna da develop em `success` e do mesmo `run_id` (`:126`); `:66-88` descarta a anotação inteira com JSON ilegível, versão, parte ou versão do interpretador diferentes do job, unidade fora do alfabeto `[A-Za-z0-9_.]` ou fora do plano atual, segundos não finitos, negativos ou acima de 900; `:136-142` descarta execução com conjunto parcial de pernas. O script não escreve no repositório (saída em stdout ou `--saida`), não imprime o detalhe do erro de rede (`:185-187`) e manda o token só no cabeçalho.
- **A3 (o mesmo N nos três lugares).** `tests/test_suite_partes.py:603` lê o YAML e exige, nas 4 matrizes, lista 1..N e o mesmo N em `--parte K/N` e `--somar-pulados N`; `:460` prova que matriz de 4 pernas com `--somar-pulados 5` reprova.
- **A4 (download só do run corrente).** `ci.yml:112-118` e `:218-224` usam só `pattern`, `merge-multiple` e `path`; `tests/test_suite_partes.py:589-601` proíbe `run-id`, `github-token`, `GH_TOKEN`, `actions: read` e `checks:`.
- **A5 e A6 (texto do modelo de projeto).** `templates/projeto/docs/engineering/protecao-de-branch.md:13-18`: agregador exigido só lê os necessários, reprova perna pulada ou cancelada, guarda de completude (executados igual a coletados, nenhuma fatia com zero, o mesmo N conferido por teste), plugin de divisão com versão fixa, licença permissiva e sem custo (`R-CUSTO`), e a fusão do teto ao agregador limitada à integração, nunca ao agregador exigido do PR. Texto neutro (`R-NEUTRO`): cita ferramentas só como exemplo.

Demais pontos conferidos:
- **Permissões:** todo job novo tem `permissions: contents: read` (o topo já é `contents: read`, `ci.yml:27-28`) e todo checkout tem `persist-credentials: false`; nenhum job novo recebe `actions`, `checks` nem token; nenhuma ação nova (as mesmas, fixadas por SHA); nada de `pull_request_target` nem cache novo.
- **Entrada interpolada:** só `matrix.parte` (literal do YAML) e `needs.*.result`, sempre via `env:`; nada de `head_ref`, título ou nome de branch em `run:`.
- **Emissor da anotação (injeção de comando de workflow):** `scripts/suite-partes.py:207-232` só emite unidade no alfabeto `[A-Za-z0-9_.]` (`:51`), segundos finitos e não negativos (bool fora), parte e versão por expressão fixa, e ainda escapa `%`, CR e LF do dado; mensagem e título não carregam `::` nem `,` vindos de fora. No PR a perna roda código do autor, que já poderia emitir qualquer comando; a anotação não lhe dá nada novo, e o consumidor só lê runs de push na develop (A2).
- **Completude da divisão por unidade (S9):** `completude_da_divisao` (`scripts/suite-partes.py:181-204`, chamada em `:394`) reprova unidade do discover fora do plano, unidade do plano sem teste e partes que não cobrem o multiconjunto de IDs do discover uma vez cada; o peso muda só a partição, nunca a cobertura, e os pesos ainda não recalibrados (por desenho) não abrem brecha.
- **Disponibilidade:** o `timeout-minutes` da perna caiu de 30 para 15 (medida de 2:30 a 5:00); estourar deixa a develop vermelha (falha fechada), sem pular prova.
- **Segredos no diff:** o único padrão de token é o valor fictício de teste em `tests/test_pesos_do_ci.py` (prova de que o token não vaza); nenhuma credencial real.

Observação, sem achado (proporcionalidade): `scripts/pesos-do-ci.py:147-151` envia `GH_TOKEN` ao host de `GITHUB_API_URL` sem exigir `https`. Quem controla o ambiente do dev já tem o token; não há caminho de ataque realista. Se o script um dia rodar num job do CI, vale restringir o esquema.

## Achados

## Sondas

## Detalhe dos achados
Sem achado. Sondas executadas (nenhuma prova bloqueante, por isso fora do bloco `## Sondas`), por `python3 -I` contra as funções do head:
- emissor com nome `a::x`, nome com quebra de linha e `::error::`, NaN, `True` e negativo: sai uma única linha `::notice` só com a unidade válida;
- emissor com parte ou versão fora do formato (quebra de linha, vírgula): nenhuma linha;
- consumidor com parte diferente do job, unidade fora do plano, `NaN` literal no JSON e 901 s: anotação descartada (None); a válida passa;
- execução de `pull_request`, de `head_repository` de fork e com `id` booleano: rejeitadas;
- job com o nome da perna do PR e com parte 6/5: rejeitados;
- erro de rede com o token na mensagem: rc 1, token ausente do stderr.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: a inteira roda no CI do PR; aqui rodei os testes novos e alterados que tocam a segurança (`tests.test_pesos_do_ci` e `tests.test_suite_partes`: 60 testes, OK) e as sondas acima. Ferramentas: leitura estática do diff, de `scripts/arvore-testada.py` e do `ci.yml` inteiro nos jobs novos; procura por padrão de credencial no diff. Faltaram no ambiente (lacuna, sem instalar): `gitleaks`, `actionlint`, `zizmor`, `semgrep`, `osv-scanner`; o `actionlint` e o `zizmor` do job de passos do CI valem para este head. Ruleset dos checks exigidos não relido pela API (credencial do `gh` fora do sandbox); a entrega não renomeia `bateria`, `bateria (python 3.14)` nem `catraca`.
