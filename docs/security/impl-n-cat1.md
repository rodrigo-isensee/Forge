---
tipo: revisao-seguranca
contrato: 1
pedido: impl-n-cat1
branch: melhoria/impl-n-cat1-2
commit: c6413c69240e0bd17768b9db7679619918a727de
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-22
---
# Review de segurança: impl-n-cat1

Escopo: a entrega `a3dbe22..c6413c6` (6 commits: f1ce2af, 82773a2, aecd1c3, 63f99d9 e 52ae7fa, um por item na ordem do desenho, e c6413c6, só com o fragmento) sobre `tests/catraca.py`, `tests/test_catraca.py`, a nota da ADR 0008 e o fragmento `changelog.d/impl-n-cat1-2.md`. Referências: o desenho `docs/propostas/discovery-0.29.0/n-cat1.md` §2 (itens 1, 3, 4, 5 e 6), as medidas M1 a M3 e o modelo de ameaças `docs/security/ameacas/n-cat1.md` (C1 a C6 e os casos de abuso). O item 2 ficou fora (P-CAT1-1 = B): conferi que `rotulo_vale_pelo_conteudo` não mudou no diff. O commit 2cee051 (parecer do review), que chegou depois, não é código e fica fora deste parecer.

O CI roda a catraca da base (ADR 0008), então este PR ainda é julgado pela versão antiga: ela pede o rótulo do dono por `tests/catraca.py`. Os controles novos começam a valer no merge na `develop`.

## Gatilhos
Controles do Forge: `tests/catraca.py` é a própria catraca e está em `PROTEGIDOS` (`R-SEGURANCA`, `R-CONFORMIDADE`). O PR pede o rótulo `afrouxa-regra` do dono, embora nada aqui afrouxe. Não entra credencial nova, chamada de rede nova nem workflow novo.

## Achados

## Detalhe dos achados
Veredito: **aprovado**. Cada controle pedido falha fechado, nenhum caminho novo de liberação foi criado e nada afrouxa. Abaixo, o que foi conferido e as recomendações, que não bloqueiam.

### O que foi conferido (código lido, testes rodados e mutantes)
- **Leituras do git falham fechado (item 1, C2).**
  - `listar` (tests/catraca.py:72) levanta `ErroDeGit` quando o git falha.
  - `existe` (:80) decide a introdução da catraca pelo código de saída do `ls-tree`; `regra_protegidos` (:454) não depende mais da ordem das regras.
  - `violacoes_das_regras` e `violacoes_de_pareceres` (:479 e :978) transformam `ErroDeGit`, `TimeoutExpired` e `OSError` (`FALHAS_DO_GIT`, :128) numa violação `R-CONFORMIDADE` de uma linha.
  - A guarda do rótulo (:1088) procura a marca comum `NAO_LIBERAVEL` (:106). Se a marca aparecer num caminho de arquivo, a violação só fica mais dura, e o R3 de `catraca-endurecer` continua sem afrouxar.
  - No caminho da S-16, `liberado_por_pr_mesclado_ou_none` (:921) passa a pegar também `ErroDeGit`. Ela devolve None, que quer dizer "sem rótulo", e com violação o rc continua 1, como antes.
- **API cortada e paginação sem teto (item 3, C4).** `ERROS_DA_API` (:624) inclui a família de erros HTTP. `api()` (:627) virou `api_com_teto`: acima de 3 páginas devolve None. Os chamadores tratam None como "sem rótulo" e escrevem um aviso.
- **Prazo total de 240 s (item 4, C4).** O prazo usa relógio monotônico, `min(30, restante)` em cada chamada e a exceção `PrazoDaApiEsgotado` (:578), que é `OSError`. Prazo esgotado nunca libera. O valor (:574) bate com a medida M1 e com o teste estrutural do `timeout-minutes`.
- **Parecer que não aprova barra sempre (item 5, C1).** A regra vale para os 4 tipos, com ou sem `SENSIVEIS`, e para o QA também na `develop`. Valor fora do contrato barra. `riscos-aceitos` só passa com o aceite do usuário. A promoção continua fora (:1011). A remoção de duplicata (`ja_ditos`) não abre furo: ela só age quando já existe a violação "sem parecer aprovado", e o rc é 1 mesmo assim.
- **Forma compilada (item 6, C5).** `FORMA_COMPILADA` (:460) é uma lista fixa e vale para o repositório inteiro. `regra_compilados` (:463) gera a mesma violação "mudança em <arquivo>" de um protegido.
- **Testes.** Rodei `tests.test_catraca` numa cópia própria de c6413c6 em `$TMPDIR`: 222 OK, sem rede (`urlopen` e o socket bloqueados, e nenhuma tentativa de conexão no ambiente padrão). Mutantes que morreram, cada um derrubando de 1 a 8 testes:
  - `listar` voltando a `[]`;
  - a guarda voltando a `SEM_LISTA`;
  - tirar `__pycache__/` ou `.so` da lista;
  - voltar a exigir `SENSIVEIS` no item 5;
  - filtrar o QA na `develop`;
  - aceitar qualquer valor de parecer;
  - a exceção do prazo deixar de ser `OSError`;
  - tirar a checagem do prazo;
  - trocar o `min` por 30 fixo;
  - a introdução voltar a `ler(...) is None`;
  - a captura voltar a só `ErroDeDiff`;
  - tirar a família HTTP da captura;
  - tirar o teto de `api()`.

  Sobreviveu só o mutante que tira o `PRAZO.reiniciar()` (:1070). Isso é informativo: cada execução da catraca no CI é um processo novo.

### Recomendações (não bloqueiam)
- **R1 (baixa; testes sem rede, `R-CUSTO`).**
  - **Evidência:** tests/test_catraca.py:2281 (`test_o_rotulo_do_dono_libera_como_a_qualquer_protegido`) e o `roda` de tests/test_catraca.py:517, usado pelo `test_estouro_de_prazo_do_git_vira_uma_linha_e_rc_1`, chamam a API real quando o ambiente tem as variáveis `GITHUB_TOKEN`, `GITHUB_REPOSITORY`, `PR_NUMBER` e `HEAD_SHA`. Com as quatro definidas, medi 5 chamadas a `urlopen`, uma requisição de fato à API (HTTPError) e uma falha do segundo teste. O mesmo padrão já existia em tests/test_catraca.py:1329 e :1953.
  - **Caminho de ataque:** não há. O CI e o pre-push não definem essas variáveis (no ambiente local só há `GH_TOKEN`) e a API não cobra, então não há custo. É higiene de teste.
  - **Correção mínima:** limpar as quatro variáveis no `setUp` da `Base`, como faz o teste de tests/test_catraca.py:627.
  - **Esforço e dono:** P, tech-lead.
- **R2 (informativa; prazo do `git fetch`).**
  - **Evidência:** `buscar_cabeca_do_pr` (tests/catraca.py:819) continua com 60 s por `fetch`, fora do prazo total. São até 20 candidatos (:687), mais que os 10 min do job.
  - **Efeito:** o job morre vermelho, ou seja, fecha, mas sem mensagem. O C4 do modelo pedia o `fetch` dentro do prazo, e o desenho limitou o item à API.
  - **Correção mínima:** usar `min(60, restante)` no `fetch` e reaproveitar o mesmo relógio.
  - **Esforço e dono:** P, tech-lead, num lote futuro.
- **R3 (informativa; estouro do git fora das regras).** Um `TimeoutExpired` em `base_efetiva`, `so_troca_sha_de_acoes` ou `rotulo_vale_pelo_conteudo` fora das regras ainda sai por rastro de pilha com rc 1, porque `main` (:1049) pega só `ErroDeGit`. Fecha, mas sem a linha no formato da ADR 0008. Fica para o mesmo lote da R2.
- **R4 (informativa; "o último ganha").** A escolha do último parecer usa a chave `(data, caminho)` (tests/catraca.py:999), como o `cmd_pr` e como o desenho decidiu. Um segundo arquivo forjado com data maior ainda mascara o reprovado (A2 do modelo). O C1 pedia o contrário, mas o ganho real seria pequeno: quem forja pode regravar o próprio arquivo, e isso não se distingue da revalidação legítima. O resíduo é a falta de conferência de autoria no CI, que vai para o N-FC-CONF ou o N-PAR.
- **R5 (média; cartão novo, fora deste lote; K10).**
  - **Evidência:** um pacote de diretório tem precedência sobre o módulo de mesmo nome. Medi numa cópia em `$TMPDIR`: com `_comum.py` e `_comum/__init__.py` lado a lado, o import carrega o pacote.
  - **Furo:** `hooks/_comum/__init__.py` não casa o prefixo `hooks/_comum.py` de `PROTEGIDOS` (tests/catraca.py:43) e passa só com o review, sem o rótulo do dono. Vale também para `hooks/conformidade/`, `hooks/parecer/` e `tests/neutralidade/`.
  - **Caminho de ataque:** o mesmo do A8 do modelo. Um PR mesclado com o pacote desliga o `conformidade` em toda sessão.
  - **Origem:** o furo não foi introduzido por esta entrega.
  - **Correção mínima:** proteger o diretório de mesmo nome de cada módulo protegido, ou seja, os prefixos `<módulo>/` ao lado de `<módulo>.py`.
  - **Esforço e dono:** P, tech-lead, com a segurança, junto com a K10/D2a. O cartão chega ao quadro pelo Jarvis.
- **R6 (baixa; cartão N-PAR).** Num PR que não toca `SENSIVEIS`, apagar o parecer reprovado deixa o PR sem parecer nenhum, e lá o parecer não é exigido. É evasão deliberada, equivalente a forjar, e o desenho manteve a exigência como estava. A correção seria barrar a remoção de arquivo em `docs/reviews`, `docs/qa`, `docs/security` e `docs/devops` no diff.
- **R7 (baixa; promoção).** A promoção continua sem ler pareceres (:1011), o que deixa o A3 do modelo. O padrão da P1 do modelo de ameaças era A (ler na promoção), e o desenho, citando a ADR 0008, deixou de fora. O Jarvis registra qual dos dois vale, com o dono se for o caso. Isso não afrouxa em relação a hoje.
- **Integrador (C6 do modelo).** Depois do merge, toda branch em voo com parecer reprovado já commitado, à espera de revalidação, fica vermelha no job `pareceres`. É intencional. O integrador avisa quem estiver com essas branches.
- **Alinhamento do modelo de ameaças.** O C4 do modelo de ameaças fala em 6 min, e o certo é 240 s (medida M1). O ajuste é meu e vai no próximo toque no arquivo do modelo, que está fora desta branch.

## Riscos aceitos e ferramentas
- Nenhum risco aceito.
- Ferramentas: só leitura do código, `git` e a suíte em cópia própria em `$TMPDIR`, com o socket bloqueado e a troca de código para os mutantes. Faltam no PATH: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint` e `trivy`. A entrega não toca workflow nem dependências, e as varreduras rodam no CI.
