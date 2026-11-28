---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-brief-vagas
commit: 126b903b79e75737551b263384acf23783e91f62
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047, desenho BRIEF-NAO-SEGURA-VAGAS (E2.339)

Parecer completo (não havia parecer anterior) do diff `1b88640e..8a8d8473`: um arquivo, `docs/arquitetura/brief-nao-segura-vagas.md` (179 linhas, classe T, só desenho). Revisor: instância que não fez o commit (E2.320). Sem `docs/engineering/praticas.md` no Forge: checklist da skill `engineering-practices` por leitura. Suíte não rerrodada (só texto `.md`; o CI do PR a roda).

## Achados
- A1 (bloqueante) docs/arquitetura/brief-nao-segura-vagas.md:173 · os oráculos do Critério de parada (linhas 173 a 179) usam `python3 -I -m unittest tests.<m>`; o -I tira a raiz do sys.path e tests/ não é pacote: ImportError antes de qualquer teste (S1). Usar `python3 -m unittest tests.<m>` na raiz.
- A2 (recomendado) docs/arquitetura/brief-nao-segura-vagas.md:30 · linhas de bin/forge-check citadas nas seções 1 e 2 defasadas na Base 1b88640e (montar_brief :8366 é 8460, cmd_brief_selar :8750 é 8844, ETAPAS_DE_PARECER :2231/:8312 é 2277/8406); citar pela função.
- A3 (recomendado) docs/arquitetura/brief-nao-segura-vagas.md:138 · "decisão E8 pendente" sem referente: o v047 não tem E8 no Escopo e o desenho não define o termo; nomear a condição que o teste de recusa monta.
- A4 (recomendado) docs/arquitetura/brief-nao-segura-vagas.md:88 · o passo 7 apaga os briefs da execução que reprova, mas as etapas do passo 6 ficam no pedido; dizer isso no texto e na saída da recusa (o reaproveitamento pela chave da 5.2 cobre a execução seguinte).

## Sondas
- S1 · python3 -I -m unittest tests.test_etapa_do_brief (raiz do clone, head 8a8d8473) · espera: os testes do módulo rodam · obtido: ImportError: Failed to import test module: tests

## Parecer
Reprovado por A1 (`R-REVIEW`, defeito provado). O `## Critério de parada` é o contrato que os pareceres das partes P0 a PC vão rodar para decidir o que bloqueia (PAR-P2); com o `-I`, todo oráculo sai com ImportError mesmo com os testes verdes, e cada portão leria falha onde não há. A forma `discover -s tests -t .` também não serve com `-I` (tests/ não é importável). Correção: tirar o `-I` das sete linhas de oráculo; o AR-5 vale para o interpretador dentro dos testes (seção 7, que está certa), não para o comando do oráculo.

O resto está conforme: O2 bem justificada contra O1 e O3, com "por que o existente não basta" (seção 2) e critério de reversão (seção 10, `R-DECISAO`); referências conferidas na Base (todas as funções citadas existem; três cópias de `ETAPAS_DE_PARECER` sem `devops`; `forge-check brief` na lista só de leitura em `hooks/conformidade.json:111`); Δ1 fecha a reprodução por construção; mutantes um por guarda (AR-1, AR-12); `R-NEUTRO` e `R-CUSTO` respeitados; D1 levado ao dono sem afrouxar `R-BRIEF`. A2 a A4 não devolvem.

Revalidação na volta: `forge-check parecer delta docs/reviews/v047-brief-vagas.md`; basta o delta nas linhas 173 a 179.

## Revalidação (E2.343, head 0e45c3a8)
Delta lido: `forge-check parecer delta docs/reviews/v047-brief-vagas.md`, intervalo `8a8d8473..0e45c3a8`, no domínio só `docs/arquitetura/brief-nao-segura-vagas.md` (commit 0e45c3a8, E2.342).
- A1 resolvido: as sete linhas do `## Critério de parada` usam `python3 -m unittest tests.<m>`, sem `-I`; nenhum `python3 -I` restante fora da seção 7 (linha 134, interpretador dos testes, AR-5, correto). Sonda S1 refeita sem `-I`: `python3 -m unittest tests.test_etapa_do_brief` na raiz do clone, `Ran 89 tests`, `OK`.
- A2 resolvido: as seções 1, 2, 4, 5.3 e 5.5 citam as funções pelo nome, sem número de linha do `bin/forge-check`; resta só `hooks/conformidade.json:111`, conferido na revisão anterior.
- A3 resolvido: o passo 7 (linha 88) define a "decisão E8 pendente" da seção 7 (linha 138) como a checagem `pendencias_da_conferencia` do `cmd_brief_selar` (existe em `bin/forge-check`).
- A4 resolvido: o passo 7 diz que as etapas do passo 6 ficam no pedido e são reaproveitadas pela chave da seção 5.2.

Achados novos no delta: nenhum. Sem classe repetida para `docs/engineering/achados-recorrentes.md`. Parecer: aprovado no head 0e45c3a8 (`R-REVIEW`).

## Revalidação (E2.392, head 126b903b)
Delta lido: `forge-check parecer delta docs/reviews/v047-brief-vagas.md`, intervalo `0e45c3a8..126b903b`, no domínio só `changelog.d/v047-brief-vagas.md` (novo, commit 126b903b, E2.387).
- Fragmento conforme ADR 0006: nome igual à branch sem prefixo, seção `### Adicionado`, uma entrada com o pedido e o arquivo do desenho, sem editar o `CHANGELOG.md`; `R-NEUTRO` respeitado. `python3 -m unittest tests.test_changelog` na raiz do clone: `Ran 74 tests`, `OK`.

Achados novos no delta: nenhum. Sem classe repetida para `docs/engineering/achados-recorrentes.md`. Parecer: aprovado no head 126b903b (`R-REVIEW`).
