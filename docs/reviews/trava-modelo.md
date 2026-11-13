---
tipo: review
contrato: 1
pedido: v0457
branch: melhoria/trava-modelo
commit: 5c38e04ea8d010b3250b2c934278a66e94eff43e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: trava-modelo (v0457, E23.29, revisão E23.109)

Classe C, rótulo afrouxa-regra. Instância que não fez a entrega. Head revisado 5c38e04e (base ee608198).

## Achados
- A1 (recomendado) hooks/conformidade.py:1172 · o `except Exception` da isenção engole erro de git ou disco sem rastro; falha fechado e é coberto por teste, mas um log curto na recusa ajudaria o diagnóstico.

## Sondas

## Parecer
Aprovado. O comportamento é um só (isenção do modelo na trava de arquivo): 54 linhas de código em hooks/conformidade.py e 83 em tests/test_hooks.py, dentro da orientação de 150 por PR (M14).

Isenção contra o parecer E23.28 (C1 a C10), lida em `isencao_do_modelo` e `isencao_valida`:
- C1 lista exata pós-realpath: `casa(rel, padrao)` sobre `templates/projeto/.githooks/*` e `.forge/config.json`; `.claude/` e `.forge/versao` do modelo seguem travados (fixtures a09 a11).
- C2 só o clone do Forge, nunca o projeto, e só o clone da sessão ou o de trabalho (`e_clone_do_forge`, `raiz_e_projeto`, `em_contrib`; a03, a21).
- C3 o modelo não vale ali: recusa se o PLUGIN é o clone ou se `core.hooksPath` cai no modelo; erro do git conta como "vale" (a22; testes C3 em `TravaModelo`).
- C4 só Write e Edit; Bash e MultiEdit seguem barrados (a18 a20).
- C5 caminho absoluto, literal (`[\w./@+-]+`) e `normpath` idêntico: sem variável, til nem `..` (a14 a17).
- C6 nenhum link simbólico no caminho dado que aponte para dentro do clone, e nlink 1 do alvo (a01, a02, a04 a08).
- C7 isenção como dado validado (`isencao_valida`) e exceção na conferência não isenta (falha fechado).
- C8 e C9: os 22 casos de abuso a01 a a22 existem como fixtures, mais 5 que liberam; os 22 mutantes declarados (3 specs: 8, 8 e 6) cobrem uma linha de guarda cada.
- C10: fragmento `changelog.d/trava-modelo.md` traz o rótulo afrouxa-regra e o risco residual (troca por link entre a conferência e a escrita) para o aceite do dono no PR. O aceite é do dono; não é achado.

A isenção liberada vale só quando `caminho == self.modelo_isento` (o realpath conferido) e só para as duas regras de `REGRAS_DO_MODELO`; as demais do `conformidade.json` continuam valendo.

## Provas
- `TravaModelo` e `test_fixtures_da_trava_modelo` (7 testes, ambiente limpo, `discover -k`): OK.
- `bin/forge-mutante` nas três specs (`trava-modelo`, `-2`, `-3`) no head 5c38e04e: todos os mutantes morreram, nenhum sobreviveu. M21 morre por erro do teste sob o mutante (esperado: o mutante remove a captura).
- A suíte completa fica no CI do PR; não foi rerrodada aqui.
