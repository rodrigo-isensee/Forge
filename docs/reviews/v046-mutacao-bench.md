---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/v046-mutacao-bench
commit: 60bba369d14f778d47f085e4f68c59707c44388f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E7.2, melhoria/v046-mutacao-bench)

Diff revisado: `8b5a44d5..60bba369` (classe C pela catraca: `bin/forge-changelog`). Instância que não fez a entrega.

## Achados
- A1 (bloqueante) bin/forge-mutante:805 · --base escolhe o mutante só pelo `arquivo`; teste de `testes` enfraquecido (ou spec mudada) entre base e rev deixa o mutante `fora do diff` e a rodada sai 0 com ele vivo (S1, S2). Mesmo defeito do A1 da segurança. Incluir o mutante quando a spec ou o módulo de um `testes` mudou, com teste.
- A2 (recomendado) bin/forge-mutante:19 · a docstring promete que na revalidação "só o que mudou desde ele roda de novo"; depois do A1, dizer que conta arquivo, testes e spec, e que a primeira rodada do QA é a spec inteira.
- A3 (recomendado) skills/qa-testing/SKILL.md:95 · a skill do QA, agents/qa-engineer.md:20 e agents/tech-lead.md:25 não citam `SPEC --base`; agents/tech-lead.md:41 cita o placar e não o bench da versão. Uma frase em cada, junto do A2 da segurança.

## Sondas
- S1 · repo com lib.py (if x > 5) e M1 x>=5 testado por tests/test_lib.py; commit que só apaga o assert f(5)==0; forge-mutante p.json --base <base> · espera: M1 roda e sobrevive, rc 1 (como sem --base) · obtido: fora do diff: M1 · lib.py, rc 2 (nada executado)
- S2 · igual a S1 com M2 em outro.py e o mesmo commit tocando outro.py; forge-mutante p.json --base <base> · espera: rc 1 (M1 sobrevive; sem --base dá M1 sobreviveu, rc 1) · obtido: fora do diff: M1 · lib.py; M2 morreu; rc 0

## Parecer
Reprovado por A1. O recorte da `--base` olha só o `arquivo` mutado, mas o veredito de um mutante depende também dos `testes` que o matam e da própria entrada na spec; com o teste enfraquecido entre a base e o rev, a mutação dirigida dá verde (rc 0) com um mutante que sobrevive sem a `--base` (S2). Isso esvazia a revalidação que a docstring prescreve. Correção: o mutante entra no diff quando muda o `arquivo`, o arquivo do módulo de algum `testes` (`tests.<módulo>...` → `tests/<módulo>.py`) ou o arquivo da spec; teste de comportamento do ramo novo e mutante declarado na guarda.

Conferido e sem achado:
- Arquivo renomeado: o `diff --no-renames` lista o caminho velho e o novo; spec com o caminho novo roda (sonda local, `M2 · morreu · novo.py:2`), spec com o velho cai como inválida, como sem a `--base`.
- Base ilegível, sem ancestral comum e nenhum mutante no diff saem 2 sem traceback (testes `MutacaoDirigida`); `--cobertura --base` sem SPEC segue igual; `--cobertura` com SPEC continua erro de uso.
- M-5 e bench: só aviso no `forge-changelog release`, depois da gravação, sem mudar a saída; fora do clone do Forge não imprime nada. Nada em `.github/` nem em `.githooks/` (o teste `test_nem_o_ci_nem_o_envio_rodam_o_placar` guarda isso com mínimo de 3 fontes). Decisão do dono de 12/11 11:06 atendida no M-5 e no bench; o tempo do CI do PR foi medido pelo autor (histórico 11:28: 0,5% pelos testes novos).
- Guardas do diff: 10 linhas de guarda, 10 mutantes declarados (`--cobertura --base 8b5a44d5 --rev 60bba369`: as 9 condições `coberta`, rc 0; o `except RuntimeError` tem o M7). Tamanho: 135 linhas de código e teste, dentro de 150.
- Testes dos arquivos tocados: `bin/forge-testes tests/test_forge_mutante.py tests/test_changelog.py`, 178 testes, OK. A suíte inteira fica no CI.
- Commits: três, Conventional Commits em português, um comportamento por commit.

O A3 da segurança (tag crua no comando impresso, `shlex.quote`) é dela; não o refaço.
