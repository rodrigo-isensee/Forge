---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-specs-conferidas
commit: 48e5741594135d899e5a4d668eaf6a947aa5e09e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047-specs-conferidas

Item E2.215 da v047 (classe AR-12), revisado em E2.281 por instância que não fez a entrega. Base-sha e13aed85 (= merge-base com a develop). Parecer completo (não havia parecer anterior).

## Achados
- A1 (recomendado) tests/fixtures/mutantes-pendentes.txt:37 · A develop andou (c6a5932c): no merge simulado (merge-tree), a catraca sai com 12 pendentes que já conferem (a mutantes-velhos entrou) e 3 specs novas fora da fonte (pr-verde-lote-check M8, v0442-mensagem M4, v047-hook-erro-libera-4 M28). Ao trazer a base, alinhe-as e encolha a lista.
- A2 (recomendado) bin/forge-mutante:52 · A ajuda e a catraca citam o `--todas`, mas a skill qa-testing ('Mutantes declarados') não cita o `--conferir` (nem `--base` nem `--todas`); uma linha lá evita o autor descobrir a catraca só no CI.

## Sondas

## Parecer
Aprovado. O diff faz o que o E2.215 pede: `--conferir --todas` confere o `de` de todas as specs do rev (sem `linha_base`, que segue com o `--base`), e a catraca `ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` (tests/test_forge_mutante.py:1272) só deixa a lista de pendentes encolher, com piso de 400 specs (checklist 11).

Conferido nesta leitura:
- Código (bin/forge-mutante): `texto_no_commit` com `lru_cache` é seguro (chave sha + arquivo, conteúdo imutável); `specs_do_rev` recusa rev que não é commit e rev sem spec (rc 2); `--todas` despachado antes do `--conferir --base`, recusado sem `--conferir` e com `--base`, SPEC ou `--cobertura`. Tamanho (M14): 131 linhas de código e teste (59 em bin/forge-mutante, 72 em tests/test_forge_mutante.py), dentro de 150; specs, fixture e changelog fora da conta.
- Testes: subprocesso com `-I` e ambiente limpo (`sem_manutencao`, `GIT_CONFIG_*` em /dev/null), sem herdar o do CI (AR-4, AR-5). `python3 -m unittest tests.test_forge_mutante.ConferirTodas`: 4 testes OK em 28 s.
- Mutantes: `bin/forge-mutante tests/mutantes/v047-specs-conferidas.json --rev HEAD` em 0064a82ee021: T1 a T7 morreram, um por guarda nova (693, 696, 708, 720, 724, 969, 970).
- Specs alinhadas: `--conferir --todas` no head dá 0 trechos ausentes fora das 15 linhas da melhoria/v047-mutantes-velhos e 29 de trecho repetido; na develop (Base) os mesmos 29 repetidos já existiam (comparação linha a linha vazia), então a branch não criou repetição.
- Retirados: para cada mutante que sai (lote-l10, lote-fechar2-2 e os demais listados nos commits ce87ef7a, 2124eec7, efc38e0d e 30740464), o `de` aparece 0 vezes no arquivo da spec no head; o motivo de cada retirada está no corpo do commit. Nenhum retira cobertura de guarda que ainda existe.
- Sobreviventes declarados pelo autor (pr-verde-lote-check-3 M17, t6t3-mensagem M10 e M16, fix-037-uniao-seg M5, v0433-integracao-10 I155, vel-p1p10 M7, lote-m8-hook M9) são lacuna de teste do QA (E2.283), não deste review.
- Commits: um por arquivo de fonte, Conventional Commits em português, corpo com alinhados, retirados e motivo.
- Suíte: roda no CI do PR (R-REVIEW); este review rodou só a classe nova e os mutantes. Não há `docs/engineering/praticas.md` no Forge; sem regra "ferramenta" a citar.
- Achados recorrentes (PA-7): AR-4, AR-5 e AR-12 conferidos; nada se repete, sem linha nova.

## Revalidação (E2.361, head 48e57415)
Delta lido: `forge-check parecer delta docs/reviews/v047-specs-conferidas.md`, intervalo 0064a82e..48e57415, sem o que veio da base (develop); no domínio só tests/fixtures/mutantes-pendentes.txt e as specs pr-verde-lote-check.json, v0442-mensagem.json e v047-hook-erro-libera-4.json. Não reli o que não está no delta.
- A1 resolvido: o `de` de pr-verde-lote-check M8 (bin/forge-check:1785), v0442-mensagem M4 (hooks/meta.py:193) e v047-hook-erro-libera-4 M28 (tests/catraca.py:315) aparece 1 vez na fonte; `bin/forge-mutante` só com esses três no head 48e57415: M8, M4 e M28 morreram.
- Fixture: saiu o bloco das 15 linhas da mutantes-velhos (entrou na develop, #578); ficam hooks-corpus-rapido M2 e M5, cujo `de` some do bin/forge-testes no head (0 ocorrências), na ordem alfabética da lista. A lista só encolheu fora delas (15 → 2).
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas`: 4 testes OK em 6,9 s no head.
- A2 segue recomendado, sem mudança no delta. Achados recorrentes (PA-7): AR-12 é a classe que a catraca deste item passa a pegar; sem achado novo, sem linha nova.
- Suíte: roda no CI do PR (R-REVIEW), não rerrodada aqui.

Integração (R-FLUXO), nota da rodada anterior: A1 não bloqueia o código revisado, mas o CI do PR roda sobre o merge com a develop e hoje reprovaria; quem trouxer a base atualiza a fixture e as 3 specs, e o delta volta aos pareceres pelo `forge-check pr`.
