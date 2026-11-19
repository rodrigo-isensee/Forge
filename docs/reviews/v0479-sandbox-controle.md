---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-sandbox-controle
commit: 64fca89083f7549aa5ea97ed4e716bec049f1306
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 (E29.12, revalidação do A7 de SANDBOX-TRAVA-CONTROLE, head 64fca890)

Revalidação (H3, R-REVIEW): li só `forge-check parecer delta docs/reviews/v0479-sandbox-controle.md`, intervalo `1aaea973..64fca890`, 8 arquivos no domínio. Suíte inteira não rodada (fica no CI do PR). Rodei o teste do item, `python3 -m unittest tests.test_sandbox_controle`: `Ran 14 tests ... OK (skipped=2)`, os dois do bubblewrap pulados aqui. Rodei `bin/forge-mutante --processos 1 tests/mutantes/v0479-sandbox-controle.json` no rev 64fca89083f7: os 13 mutantes declarados morreram (M1, M2, M4 a M14; o M3 saiu junto com a guarda que ele cobria).

Delta lido:
- A7 resolvido: `hooks/agentes.py` volta a ser igual ao da base em `ler_estado`. `git diff 73842444..64fca890 -- hooks/agentes.py` mostra só a troca do `ler_trava` em `pesado_livre`. A fixture original `tests/hooks/agentes/estado-ilegivel-vazio-bloqueia.json` voltou, e `git diff 73842444..64fca890 -- tests/hooks/agentes/` sai vazio. A docstring de HOOK-ESTADO-ILEGIVEL-LIBERA, `docs/hooks.md` e o fragmento do changelog dizem que o `agentes.json` de 0 byte segue ilegível. O teste de `ControleVazio` agora afirma `EstadoIlegivel` no 0 byte. A regra com ID fica como estava, sem afrouxamento.
- `hooks/_comum.py:2561` (`gravar_json`, A5 da segurança): tira a sobra do temporário e abre com `O_CREAT|O_EXCL|O_NOFOLLOW`. Um link plantado não é seguido, e a corrida depois da checagem cai em `FileExistsError` sem escrever no alvo. M12 a M14 cobrem as três guardas pelo comportamento. O mérito de segurança é do parecer da segurança.
- O teste do limite de renomear a pasta mãe documenta o limite que está registrado em `docs/hooks.md`. Ele não o fecha.

## Parecer
Aprovado. O A7 foi desfeito como pedido: o 0 byte do registro de agentes segue recusando com R-TETO, e a fixture original está de volta. O resto do delta não traz achado novo.
