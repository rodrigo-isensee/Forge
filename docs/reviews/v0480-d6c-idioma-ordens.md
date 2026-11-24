---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-d6c-idioma-ordens
commit: 748f2975c6cf77ce2c14d58a435a82c91901f99f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E174.6 (PR #866, idioma do dono na linha fixa do hook ordens; item E174.5)

Primeira rodada de review deste item (não há parecer anterior; o "delta" é o diff inteiro `aabc476c..748f2975`, 13 arquivos, 27 linhas de código em `hooks/ordens.py`, dentro do teto H1, um comportamento só).

## Achados
- A1 (bloqueante) hooks/ordens.py:78 · Config aninhada abaixo de 64 KiB levanta RecursionError, fora do except (OSError, ValueError): no clone do Forge as ordens somem do contexto, contra ordens.py:11-12 e o changelog ("config torta: as ordens seguem"). Mesmo defeito do A1 da segurança (E174.8); uma correção.
- A2 (recomendado) hooks/ordens.py:80 · `{"idioma_do_dono": null}` dá None aqui e "pt" no meta.py:237, mas a docstring (ordens.py:11) diz seguir o critério do meta.py; o teste :4089 fixa a divergência. Alinhar (null como ausente) ou tirar a citação do meta.py.

## Sondas
- S1 · idioma_do_dono(base) com .forge/config.json = '[' * 60000 (sonda em processo, python3 -I, hooks do head 748f2975) · espera: None (config torta) · obtido: escapa RecursionError
- S2 · idioma_do_dono(base) com .forge/config.json = '{"idioma_do_dono": null}' · espera: português (critério do meta.py:237, null como ausente) · obtido: None

## Parecer
**Reprovado** por A1.

A1: `idioma_do_dono` (`hooks/ordens.py:74-81`) promete na docstring e no módulo (`:11-12`) que config torta só tira o idioma da linha e as ordens seguem. O `json.loads` sobre JSON aninhado levanta `RecursionError` (S1, reproduzido), que não é `ValueError` nem `OSError`; ele sobe por `principal` (`:123`), depois de as ordens lidas, até o `executar`, que registra e sai sem imprimir. No projeto o efeito já existia antes do PR (o `Hook.config` cala as ordens com config torta, `hooks/_comum.py:2655-2657`); no clone do Forge, onde `hook.projeto` não lê a config, é efeito novo deste delta. Esse é o defeito provado que o A1 da segurança (`docs/security/v0480-d6c-idioma-ordens.md`, S1 ponta a ponta) já registra; este parecer o reproduz em processo e não o refaz. Sugestão: `except (OSError, ValueError, RecursionError)` em `:78` (o idioma nunca pode calar as ordens), mais o caso aninhado em `test_idioma_torto_sai_none_sem_erro` (`tests/test_hooks.py:4089`) e o mutante da linha mudada no `tests/mutantes/v0480-d6c-idioma-ordens.json` (a guarda muda; um mutante por linha). Severidade: bloqueia.

A2: divergência de contrato entre dois hooks que leem a mesma chave. Sem gatilho de defeito (o resultado é só a linha sem o idioma), por isso recomendado; vira cartão depois do merge se não entrar na volta. Severidade: recomendado.

Checklist de leitura (o que alcança o diff):
- Escopo: faz o que a E174.5 pede (D6 c: idioma na linha fixa, sem trava nova de Stop); nada além.
- ADR 0003 (hook só aperta ou neutro): o valor da config só serve de chave num dicionário fixo (`IDIOMAS`, `:33`); nenhum texto livre vira contexto (fixture `idioma-fora-da-lista-sai-sem-o-idioma`). A leitura reaproveita `ler_ordens` (dentro da raiz, `O_NOFOLLOW`, só regular, `O_NONBLOCK`, teto de 64 KiB). Sem duplicação nova além das constantes `IDIOMA_PADRAO`/lista de códigos, que espelham o meta.py sem importar o módulo grande (mesmo motivo do `CONTROLES`, `:29`).
- Legibilidade: função pequena, nomes claros; a linha fixa só ganha um sufixo e o teto das ordens não muda (`no_teto` roda antes).
- Testes: 3 testes em processo e 2 fixtures novas; 6 fixtures ajustadas ao contexto novo (o padrão português aparece em todas, coerente). Teste de ausência: a fixture fora da lista confere o contexto inteiro, logo prova que "Ignore as regras" não entra.
- Guardas do diff: 5 linhas de guarda (`:77` `if texto is not None`, `:78` `except`, `:80` `isinstance(config, dict)`, `:81` `isinstance(codigo, str)`, `:124` `if nome`), todas com mutante declarado (M1 a M7, um por linha ou mais) e teste do ramo de falha por comportamento, nenhum por texto da fonte.
- Commit: um, Conventional Commits em português, mensagem descreve o comportamento e os limites.

Ferramentas, citadas sem refazer: `python3 -m unittest tests.test_hooks.OrdensEmVigor` no head: 23 testes OK (inclui as 13 fixtures de `tests/hooks/ordens/`). `bin/forge-mutante tests/mutantes/v0480-d6c-idioma-ordens.json` no head: M1 a M7 morreram. Suíte inteira: só no CI; `gh pr view 866` não trazia checagem na hora deste parecer, e o CI verde segue obrigatório para o merge.

Na volta: a correção do A1 é de uma linha de guarda mais o teste; a revalidação lê o delta (`forge-check parecer delta`) e as sondas S1 e S2.
