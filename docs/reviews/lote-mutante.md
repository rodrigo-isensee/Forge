---
tipo: review
contrato: 1
pedido: lote-mutante
branch: melhoria/lote-mutante
commit: 0fb6a2cc0128c838928220be41bc16a837c3d2a0
parecer: aprovado
revisor: forge:tech-lead (instância de review, não a autora)
data: 2026-10-26
---
# Review: LOTE-MUTANTE (E1.1 do LOTE-MUTANTE-REV), revalidação 2

Base `b6eb84fed86e3b5289f3950b33d43a86f34343c2`, head `0fb6a2cc0128c838928220be41bc16a837c3d2a0`. A volta 1 tem dois commits sobre `7865059`: `221dd68` fix (guardas com teste e mutante declarado) e `0fb6a2c` test (AttributeError da guarda removida vira falha de asserção). Os dois estão em Conventional Commits em português.

## Achados

## Revalidação por delta (7865059..0fb6a2c)
- Li o que `forge-check delta --parecer docs/reviews/lote-mutante.md` listou: `bin/forge-mutante` nas linhas 38, 212 e 216-217; `changelog.d/lote-mutante.md:6`; `skills/qa-testing/SKILL.md:85`; `tests/mutantes/lote-mutante-2.json:1-47`; `tests/mutantes/lote-mutante.json` nas linhas 60-61, 70-71 e 75-84; `tests/test_forge_mutante.py` nas linhas 115-127 e 321-337. Os pareceres de segurança e de QA, que também estão no intervalo, não são meus e não os revisei.
- Ficou como "já lido" (parecer `8c6975c`): o restante de `bin/forge-mutante`, que inclui `validar_specs`, o cabeçalho e `main`, e os testes da entrega original.
- **A1 do review `8c6975c` (SKILL.md:85): fechado.** A frase agora diz que o pedido com mais de 8 mutantes divide em `tests/mutantes/<pedido>-<n>.json`, com o mesmo `pedido` e id único no conjunto, e traz o exemplo de rodada com as duas specs. Isso bate com `validar_specs`.
- **A2 do review `8c6975c` (recusa fora da NFKC): fechado.** A linha 217 exige `unicodedata.normalize("NFKC", p) == p` em cada parte. `tests.c\u0327` e `tests.x.\uff21b` são recusados (teste da linha 115). O mutante M9 tira a guarda e morre.
- **A1 e A2 do QA `cadf28c`:** a guarda `isinstance` da linha 213 tem teste unitário e teste de execução. O teste de execução cobre `testes:[1]`, que sai 2 com "spec inválida" e sem Traceback, e o mutante M10 morre. A guarda `any("executor" ...)` da linha 384 tem teste com as três ordens de conjunto (sem executor; com e sem; sem e com), e M11 (`all(`) e M12 (`if False and`) morrem. **A3 do QA:** `partes[0] == "tests"` ganhou o M8 (`True`), que morre com `outro.x` e `x.tests.y`.
- **M6 e M7 reescritos:** os novos `de` (`p.isidentifier() and unicodedata` e `    return (len(partes) > 1 and partes[0]`) aparecem uma vez cada no `bin/forge-mutante` deste head. Contei as 12 ocorrências de `de`, e todas dão 1. M6 tira só o `isidentifier`, e `tests.ç-x` passa a ser aceito. M7 tira o `len > 1`, e `tests` sozinho passa. Os dois morrem pelo teste da linha 106.
- **Divisão em duas specs:** `lote-mutante.json` tem M1-M8, com 8 mutantes, no teto. `lote-mutante-2.json` tem M9-M12. As duas declaram `pedido: lote-mutante` e não repetem id no conjunto, como pede a regra de `validar_specs` e a frase nova do SKILL.md.
- **Fragmento do changelog:** a linha 6 nova descreve a recusa fora da NFKC, a spec com `testes` que não são texto e os mutantes novos, tudo em `### Corrigido`. Pela DECISÃO TÉCNICA do Jarvis (17:25), ela pertence à mudança, e o `CHANGELOG.md` não foi editado.
- Teste da linha 115: o `try/except AttributeError` converte o erro da guarda removida em `self.fail`, e o comentário explica o motivo (o leitor de veredito conta falha de asserção como "morreu"). É legível e não mascara caso válido, porque o `assertFalse` vem fora do `try`.

## Checklist (leitura)
- Arquitetura e regras: continua só com a biblioteca padrão (`unicodedata`), sem shell e sem ser portão. `R-NEUTRO` e `R-CUSTO` estão preservadas, e não há teste de ausência cujo alvo tenha mudado.
- Teto por PR (M14): sobre a branch inteira, `git diff --numstat --no-renames b6eb84f...HEAD` dá 54+23 em `bin/forge-mutante` e 79+2 em `tests/test_forge_mutante.py`, 158 linhas no total, abaixo de 400. Specs, changelog, pareceres e `.md` ficam fora da conta. O PR não mexe em `hooks/` nem em `PROTEGIDOS`.
- Segurança: não encontrei achado com gatilho. O parecer próprio é o do `security-engineer` (E2.1).

## Ferramenta (citada)
- `python3 -m unittest tests.test_forge_mutante` neste head: `Ran 38 tests`, `OK`.
- `bin/forge-mutante tests/mutantes/lote-mutante.json tests/mutantes/lote-mutante-2.json` neste head: rc=0, `pedido=lote-mutante rev=0fb6a2cc0128` com dois `spec=`, e M1 a M12 todos `morreu`. A rodei só para conferir M6, M7 e a divisão; a evidência formal é a do QA (E3.1).

## Parecer
Aprovado, sem achado. Os dois recomendados do review anterior fecharam, os achados do QA têm teste e mutante que morre, e a divisão em duas specs segue a regra do mesmo pedido.
