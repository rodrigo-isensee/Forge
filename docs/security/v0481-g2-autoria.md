---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-autoria
commit: f0c380e28827a0c6168b142dd65d3499faef0dd7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 E21.4 (#914, M9.2 do G2, 1ª rodada completa)

## Gatilhos
Gatilhos: controle do Forge (hook `conformidade`, registro de autoria lido pelo portão `forge-check parecer publicar`)

- ci: f0c380e28827a0c6168b142dd65d3499faef0dd7 verde

## Achados

## Sondas

## Escopo lido
`git diff b4ae1755..f0c380e2` (merge-base com a develop): `hooks/conformidade.py` (16 linhas), `tests/test_conformidade_pareceres.py`, as duas fixtures de `tests/hooks/conformidade/`, `tests/mutantes/v0481-g2-autoria.json`, `bin/forge-testes`, `tests/pesos-d4.json` e o fragmento do changelog. Também li o leitor do registro, `recusa_do_publicar` (`bin/forge-check:3883-3902`), o `pr` (`bin/forge-check:2093-2098`, `autoria_do_parecer` em 2799), a regra de caminho por papel (`hooks/conformidade.json:79-82`) e T9/T10 em `docs/security/ameacas/g2-parecer-status.md`.

## Mitigações do modelo de ameaças
- **M9.2:** feita. `PASTAS_DE_AUTORIA` (`hooks/conformidade.py:4068`) abre a leitura de `.forge/pareceres`, e `PARECER_A_PUBLICAR` (4069, aplicado com `fullmatch` em 4084) registra só a forma `<pedido>/<tipo>.md`. A classe de caracteres é a mesma de `bin/forge-check:3887`, e `[A-Za-z0-9]` no começo barra `..` como pedido. O papel registrado é o de quem gravou (4086). Provas: `test_autoria_registra_forge_pareceres`, `test_caminho_por_papel_em_forge_pareceres` (os nomes da seção 3 do modelo), `test_fora_de_pedido_e_tipo_nao_registra` e as duas fixtures do corpus do hook.
- **M9.1:** a regra continua igual, e agora funciona de ponta a ponta. Os testes `test_ponta_a_ponta_recusa_sem_autoria` (recusa antes de chamar o `gh`) e `test_ponta_a_ponta_recusa_autoria_de_outro_papel` provam isso.

## Detalhe dos achados
Não há achado no diff.

- **O que aperta:** o `.forge/run/autoria.jsonl` passa a amarrar ao papel de quem gravou também o parecer a publicar. O registro não aceita só `.md` em subpasta, em `.txt` ou em `.forge/outros`. O QA que grava `review.md` fica registrado como `qa`, e o publicar o recusa.
- **O que é neutro:** `bin/forge-testes` (o módulo entra em `FORGE_CHECK` e `RODAM_OS_HOOKS`), `tests/pesos-d4.json` e o changelog. A leitura do arquivo é a mesma que já se fazia para `docs/` (o mesmo `.md`, o mesmo `p.is_file()`, o caminho resolvido pelo `guarda.resolver`), então não abre leitura nova de tamanho nem de encoding. Um link simbólico resolve para o alvo, e o `rel` do alvo não casa, ou seja, a falha é fechada. O ramo PreToolUse, a regra de caminho por papel e as mensagens não mudam.
- **O que afrouxa:** nenhuma regra. Deixa de valer só a trava de fato: o publicar recusava sempre, até o parecer do papel certo. A recusa não vinha do desenho (ADR 0019, M9.1). Concordo com o autor que não há `[afrouxa-regra]` de conteúdo. A `catraca` cobra o rótulo do dono por ser mudança em controle, e essa decisão é dele (R-CONFORMIDADE).
- **Risco que o autor apontou (o publicar confere sha256 e papel, não o caminho):** confirmei com sondas, e não bloqueia. As sondas usam o mesmo `gh` falso do teste e ficaram no scratchpad do revisor, fora do repositório. (1) O tech-lead grava `docs/reviews/<pedido>.md`. Uma cópia idêntica fora do projeto, em `<tmp>/fora/.forge/pareceres/<pedido>/review.md`, é escrita sem hook e publicada com caminho absoluto: rc 0. (2) O tech-lead grava `aprovado` e depois `reprovado` no mesmo `.forge/pareceres/<pedido>/review.md`. Recolocar o texto `aprovado` sem hook publica: rc 0, ou seja, o veredito superado volta. O caso (1) já existia antes do PR. O caso (2) ganha um caminho canônico com este PR, mas o defeito está em `bin/forge-check:3900`, fora do diff. O caminho de ataque é um agente da sessão que copia um texto que o tech-lead de fato escreveu e o publica por cima do veredito dele. Pelo modelo, a força é a mesma de hoje: em T9, a autoria é local, e em T10 [B], até o G4, o agente roda qualquer Python com o token e pode chamar a API sem o publicar. Severidade baixa.
- **Cartão (fora do diff, dono: `developer` do `bin/forge-check`, esforço P):** o `recusa_do_publicar` passa a exigir, além do sha256 e do papel, `caminho` igual ao `rel` do arquivo publicado, relativo à raiz (ou seja, `.forge/pareceres/<pedido>/<tipo>.md`). Passa também a exigir que esse registro seja o último de `autoria.jsonl` para esse caminho. Com isso, recusa o arquivo fora da raiz e o veredito superado. As sondas (1) e (2) viram testes de recusa.
- **CI do #914 no `f0c380e2`** (o `headRefOid` foi conferido): passam as dez partes da suíte (3.12 e 3.14), `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, a instalação, o teto de pulados (3.12 e 3.14) e a árvore provada. Três checagens falham, e as três por espera. `bateria (pareceres)` falha porque os pareceres do head ainda não existiam. `bateria` falha só porque `pareceres: failure`, e as outras partes do log estão em `success`. A `catraca` falha por R-CONFORMIDADE ("mudança em hooks/conformidade.py"), à espera do rótulo `afrouxa-regra` do dono depois do último push (log do job 140002887538).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodei `python3 -m unittest tests.test_conformidade_pareceres`: 6 OK. Rodei `bin/forge-mutante tests/mutantes/v0481-g2-autoria.json`: M1 a M5 morrem (`hooks/conformidade.py:4068`, 4084, 4069, 4086, 4079). Usei git e o `gh` só para ler checks e logs. Não usei gitleaks nem osv-scanner, porque o diff não traz segredo nem dependência.
