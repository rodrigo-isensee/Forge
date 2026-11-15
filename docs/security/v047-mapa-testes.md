---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-mapa-testes
commit: 2263bc0d9d032d4d79d42c4e57641b073108f4dc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (mapa de testes, E1.253), revalidação por delta

Revalidação por delta (E1.285) do parecer anterior (aprovado em 477dbefe). O delta é `477dbefe..2263bc0d`, lido por `forge-check parecer delta`. No domínio está só `bin/forge-testes`. Ficam fora `tests/test_testes_tocados.py`, as duas specs de mutantes e o fragmento do changelog. Mudou o seguinte: `quem_importa` vale só para `hooks/` e passa a seguir o fecho de imports (hook, apoio e teste que importa teste), e o apoio da raiz de `tests/` volta à suíte completa (decisão 7 do dono). Parecer aprovado, sem achado novo.

## Gatilhos
`R-SEGURANCA`: a entrega mexe na escolha de testes do envio local, vizinha dos controles do Forge (`R-VERIFY`, M8). Não há analisador de entrada não confiável. A entrada de `quem_importa` é o texto versionado de `hooks/` e `tests/`, escrito por quem já tem escrita na branch.

## Achados

## Sondas

## Detalhe dos achados
**Achados do parecer anterior, fechados pelo delta.**
- A1 (`tests/guarda_git.py` no dirigido): fechado. `IMPORTAVEL` e `APOIO_NA_COMPLETA` saíram, e o apoio fica sem regra. Sondado no head: `planejar` devolve `completo` para os 15 arquivos da raiz de `tests/` que não são `test_*`, entre eles `guarda_git`, `catraca` e `neutralidade`.
- A2 (governança da decisão 7): fechado. O apoio de `tests/` no diff voltou à suíte completa, como diz o registro do dono (`bin/forge-testes:185-188` e a docstring de `quem_importa`). O teste `test_promover_e_apoio_seguem_na_completa` voltou, e `test_apoio_de_tests_importado_segue_na_completa` ficou como teste permanente.

**Dimensões conferidas no delta, sem achado.**
- Hooks, comparação entre a base (477dbefe) e o head para todo `hooks/*.py` (`_comum`, `agentes`, `conformidade`, `doutor`, `meta`, `parecer`, `pesado`, `quadro`, `vigia`). Nenhum plano encolhe e nenhum hook passa de completo a dirigido: os nove ficam dirigidos e o conjunto de módulos só cresce. Hook sem `tests/test_<nome>.py` agora cai na completa (`planejar`, `if casou is None`). Antes ele podia ir ao dirigido só por quem o importava, então a mudança é mais estrita.
- `IMPORTA` e `importados`: a expressão casa em qualquer ponto do texto, e não só no começo da linha. Isso inclui docstring e código mandado a subprocesso, o que só pode acrescentar módulos. Ela também cobre `import a, x as b`, que o padrão antigo perdia. As repetições exigem vírgula entre os itens e não têm retrocesso catastrófico: entradas de 20 mil itens e de 50 mil níveis com ponto levaram 0,09 s.
- Fecho: termina pelo conjunto `vistos` (há teste de ciclo entre hooks) e devolve só módulos de teste (`vistos & set(textos)`). Os nomes de `hooks/*.py` e `tests/*.py` não colidem no head, então o dicionário `lidos` não tem chave sobrescrita.
- `--afetados` (opt-in `FORGE_PREPUSH_SUITE=afetados`, `.githooks/pre-push:584`): o apoio deixa de passar por `quem_importa` e fica com `citam` e `EXERCITAM`, que já são conservadores. Esse modo nunca pede a suíte completa, por desenho, e o CI do PR continua sendo o portão.
- Limitação herdada: um hook carregado por `importlib` com nome montado em tempo de execução escapa do plano local. É a mesma limitação aceita no parecer anterior, e o CI a cobre.

Não há caminho de ataque: o plano dirigido só vale no envio local, que é opt-in. Nenhum workflow o usa como portão, e a suíte inteira no CI do PR segue obrigatória para o merge.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodado no clone, no head 2263bc0d: `python3 -m unittest tests.test_testes_tocados`, 155 testes OK (1 pulado pelo sandbox). Também rodaram os planos de base e de head para cada `hooks/*.py`, o plano de cada arquivo de apoio da raiz de `tests/` e o tempo de `importados` com entrada grande. A suíte inteira roda no CI do PR, que ainda não existe ("sem PR" no brief), e o merge depende dela. As ferramentas da skill (segredos, SAST, auditoria de workflow) não rodaram: o delta não toca segredo, dependência nem workflow.
