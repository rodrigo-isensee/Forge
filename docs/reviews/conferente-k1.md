---
tipo: review
contrato: 1
pedido: conferente-k1
branch: melhoria/conferente-k1
commit: 0368e72c056e87f4a6e1e09ef4a3f43dd0fbe77b
parecer: aprovado
revisor: forge:tech-lead (independente)
data: 2026-10-15
---
# Re-review independente (volta 3): conferente confiável, fatia K1

Escopo: `git diff bad3edd...0368e72`, com foco na volta 3 (`git diff ae4c1a1..0368e72`: `ac47f13`, `7f50ea7` e `0368e72`; 4 arquivos, +15/−7). Conferi o diff contra o "Entregar" do brief da volta 3 (`docs/briefs/conferente-k1-tech-lead-5.md`, itens 1–4), contra o pedido `conferente-k1` e contra a linha K1 (§6) da proposta. Não escrevi esta branch. Este parecer substitui o da volta 2 (`ae4c1a1`, sobre `43a7c5a`, reprovado).

## Parecer: **aprovado**
O bloqueante da volta 2 está resolvido. Os quatro trechos que estavam sem proteção agora têm invariante, e cada um falha quando o trecho dele é apagado. Os quatro recomendados também foram resolvidos (achados 3–7 da volta 2). O texto que já estava aprovado não mudou: a volta 3 só acrescenta.

### Evidência (mutação)
Para cada trecho, apaguei-o de uma cópia do arquivo em memória e conferi quais regex de `invariantes` (`tests/config.json`, lidas com `re.S`, como faz `test_trechos_obrigatorios`) deixam de casar. No arquivo real, nenhuma regex falha antes da mutação. Cada trecho aparece uma vez só.

| Trecho apagado | Invariante que falha |
|---|---|
| `conferente.md:50`: `` e `corte: etapa (ok)` `` (exceção do veredito; o bloqueante) | ``menos `não verificável` e `corte: etapa \(ok\)` `` |
| `conferente.md:65`: `precisa ser ancestral das duas` | `precisa ser ancestral das duas` |
| `conferente.md:40`: `; etapa do papel do destino que falta no "Entregar" é corte` | `etapa do papel do destino que falta` |
| `jarvis.md:63`: `` `Arquivo:` (o caminho do brief em `docs/briefs/`), `` | `` `Arquivo:` \(o caminho do brief `` |
| `R-DECISAO.md:15`: ``; na entrega, `pendente:` `` | ``na entrega, `pendente:` `` |
| `jarvis.md:60`: ` \| linhas>=N` | `linhas>=N` (em `agents/jarvis.md`) |
| `conferente.md:41`: ``; sem ele: `forma: sem PQ que o conferente confira` `` | `forma: sem PQ que o conferente confira` |
| `conferente.md:64`: `rode o comando (se for da lista acima) e ` | `` `cmd` → rode o comando `` |

## Achados
| # | Arquivo:linha | Problema | Sugestão | Severidade |
|---|---|---|---|---|
| 1 | PR (K1 PQ-6 da proposta) | A linha K1 pede "um brief real gravado em `docs/briefs/` e conferido, com a saída colada no PR". Os briefs reais existem (`~/.forge-contrib/docs/briefs/conferente-k1-*.md`), mas a saída do conferente ainda não está num PR. | Colar no texto do PR para a `develop` (E3.3) a saída do conferente sobre um desses briefs. | recomendado (vale na abertura do PR, não na branch) |

Nenhum achado bloqueia.

## Conferido e certo
- **`tests/config.json` só acrescenta.** `git diff --numstat ae4c1a1..0368e72 -- tests/config.json` dá `11 3`. As 3 linhas `-` são as últimas entradas de três listas (`linhas>=N` em `conferente.md`, `` `## Etapas` `` em `jarvis.md` e `corte: sem marca` em `R-DECISAO.md`), que voltam iguais com a vírgula. Nenhum item existente foi removido nem afrouxado. São 8 trechos novos: 5 em `agents/conferente.md`, 2 em `agents/jarvis.md` e 1 em `docs/regras/R-DECISAO.md`.
- **Recomendados da volta 2:**
  - `jarvis.md:60` ganhou `| linhas>=N`, e com isso as três fontes do formato (`R-PROVA`, o conferente e o Jarvis) ficaram iguais.
  - `conferente.md:41` ganhou o rótulo `forma: sem PQ que o conferente confira`, que é vocabulário do modo brief.
  - `conferente.md:64` diz "rode o comando (se for da lista acima)". Isso é coerente com o "do autor" para comandos fora da lista (C6).
  - O `pendente:` da entrega está protegido.
- **Fragmento:** foi renomeado para `changelog.d/conferente-k1.md` (similaridade de 87%). `changelog.d/conferente-k1-texto-e-forma.md` não existe mais. A linha da volta 2 foi completada com o que a volta 3 trouxe. O `CHANGELOG.md` e o `plugin.json` não foram tocados.
- **Nada mais mudou:** `git diff --stat ae4c1a1..0368e72` lista só `agents/conferente.md` (2 linhas, os acréscimos dos recomendados 5 e 6), `agents/jarvis.md` (1 linha), o fragmento e `tests/config.json`. As regras C1, C3, C5, C6, C7, C8 e C10 e a correção `5177b43` (`docs/briefs/conferente-k1-causa.md`) estão como na volta 2, em que já estavam aprovadas.
- **Commits:** são três, pequenos e com tipos certos (`docs`, `test`, `chore`), Conventional Commits em português, com trailers.
- **`R-NEUTRO` / `R-CUSTO`:** ok. Não há nome de projeto, stack nem comando pago.

## Ferramentas (citadas, não refeitas)
- **Suíte completa:** não rodei aqui, porque a segurança roda em paralelo na mesma worktree. O autor a rodou (PQ-1 do brief da volta 3). Rodei só as classes de texto no HEAD `0368e72`: `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_forge.RegrasComId tests.test_forge.Agentes` → `Ran 9 tests in 0.030s` / `OK`.
- **`scripts/validar-plugin.sh`:** fica com o QA (`R-QA`).
- **Segurança:** é parecer próprio do `security-engineer` (`docs/security/conferente-k1.md`). Este review não o refaz.
