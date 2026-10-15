---
tipo: qa
contrato: 1
pedido: teste-abertura-feita
branch: melhoria/teste-abertura-feita
commit: da445ba433c3d9548d834e72d40ee6073b2c4714
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-15
---
# QA - `ambiente_limpo()` sem variáveis `FORGE_*` (cartão jarvisforge-abrir-falhas)

Links: `docs/reviews/teste-abertura-feita.md`. Sem UX nem API. Obrigação: os testes de `JarvisForgeAbrir` não dependem de `FORGE_ABERTURA_FEITA` herdada da sessão aberta pelo `jarvis-forge`. Offline (`R-CUSTO`). O diff de código é só `tests/test_forge.py` (o commit bf59893 acrescenta o review).

## Resultados
| ID | Obrigação / cenário | Fronteira protegida | Resultado |
|---|---|---|---|
| CT-01 | `JarvisForgeAbrir` com `FORGE_ABERTURA_FEITA=1` herdada | variável herdada presente | Passou: 12 testes, OK |
| CT-02 | Mesma classe com `env -u FORGE_ABERTURA_FEITA` | variável ausente | Passou: 12 testes, OK |
| CT-03 | Suíte completa (`unittest discover -s tests`), `uptime` antes: load 1.17 (`R-TETO`) | n/a | Passou: 561 testes, OK (158 s) |
| CT-04 | `scripts/validar-plugin.sh` | n/a | Passou: `Validation passed` (tentativas a api.anthropic.com negadas pelo sandbox; não afetam) |

## Vermelho antes do verde
Comando: `git checkout develop -- tests/test_forge.py` e `python3 -m unittest tests.test_forge.JarvisForgeAbrir` com `FORGE_ABERTURA_FEITA=1`. Resultado: `FAILED (failures=7)` de 12. Com a correção, 12 passam. Arquivo restaurado com `git checkout HEAD -- tests/test_forge.py`. Mutação: sem ferramenta gratuita na stack; não executada.

## Bugs
Nenhum.

## Veredito
Aprovado em da445ba (código testado; HEAD da branch é bf59893, só doc de review a mais). Zero bugs abertos.
