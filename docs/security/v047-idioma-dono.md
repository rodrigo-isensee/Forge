---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-idioma-dono
commit: 8321ae381950e89c93d72fc8f2c906bb42f7c406
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474 (E2.4, lote IDIOMA)

Escopo lido: `git diff 45615e20..8321ae38` (base da develop até o head), 4 arquivos: `changelog.d/v047-idioma-dono.md`, `skills/falar-com-o-dono/SKILL.md`, `skills/falar-com-o-dono/toda-mensagem.md`, `tests/evals/test_erros_por_papel.py`.

## Gatilhos
Gatilhos: texto de skill do Jarvis (classe C); nenhum hook, permissão, workflow, `.githooks`, `bin/`, `docs/regras/` ou `tests/config.json` tocado.

## Resumo
- **Nenhuma regra afrouxou.** O diff em `skills/falar-com-o-dono/` só acrescenta: `toda-mensagem.md:9-17` junta as regras de idioma (SIEG-G4) e de encerrar a rodada (JARVIS-ENCERRA-RODADA); a linha `**Toda mensagem do dono tem resposta e ação:**`, que `tests/test_jarvis_nucleo.py:383` exige, segue intacta em `toda-mensagem.md:7`. Em `SKILL.md:12` muda só o rótulo do ponteiro; nenhuma invariante de `tests/config.json` cita o rótulo antigo.
- **Nenhuma permissão mudou.** `git diff --name-only 45615e20..8321ae38 -- .claude-plugin hooks settings* .githooks bin docs/regras tests/config.json` sai vazio.
- **Regra de espera:** `toda-mensagem.md:15-17` manda a espera ao segundo plano (skill `esperar-estado`), sem afrouxar portão: encerrar a rodada não dispensa parecer nem CI.
- **Evals:** `MensagemEmOutroIdioma` carrega `hooks/meta.py` em processo e chama `medir_mensagem(hook, None)` com `raiz=None`, logo `idioma_do_dono` não lê o `.forge/config.json` real (`hooks/meta.py:208`); a escrita vai só a `mensagens.jsonl` dentro de `TemporaryDirectory` (`hooks/meta.py:232`, `run()` do falso hook). `RodadaQueNaoEncerra` chama `bin/forge-check` em subprocesso com `-I`, ambiente mínimo (`PATH` e `HOME` no diretório temporário), `timeout=60` e transcrito sintético; subcomando só de leitura. Nenhum dado real, rede ou segredo.
- **`expectedFailure`** nos dois testes de backlog é uso legítimo (medida ainda inexistente), não teste desligado: o controle (`test_controle_mensagem_em_portugues_passa`) e o acusador da mensagem final rodam e passam.

## Achados

## Sondas

## Detalhe dos achados
Sem achado bloqueante nem recomendado. Nota informativa: a regra de idioma é só texto; a nota entre chamadas de ferramenta ainda não é medida (o próprio eval a deixa como backlog), o que é lacuna de qualidade, não caminho de ataque.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Testes rodados no head 8321ae38: `python3 -m unittest -v evals.test_erros_por_papel.MensagemEmOutroIdioma evals.test_erros_por_papel.RodadaQueNaoEncerra` (em `tests/`): `Ran 4 tests ... OK (expected failures=2)`.
Lacunas: o CI da branch ainda não existe (sem PR; `gh run list --branch melhoria/v047-idioma-dono` vazio), a suíte inteira fica para o CI do PR, portão do merge; varredura de segredos não rodou (ferramenta ausente do PATH); o diff é de texto e teste, lido linha a linha, sem segredo.
