---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-catraca-ajudante
commit: ab293a4e9da5ca4969ff60e8734b020d7b07bced
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E14.16, catraca conta asserções de ajudantes, #891)

Diff 220ba3fa..ab293a4e: `tests/catraca.py` (+57 líquidas, dentro do teto H1), 4 testes em `tests/test_catraca.py` (`AssercaoNoAjudante`), specs `tests/mutantes/v0481-catraca-ajudante.json` (CA1-CA8) e `-2.json` (CA9-CA13), fragmento em `changelog.d/`. Primeira rodada; sem parecer anterior na branch.

## Achados
- A1 (bloqueante) tests/mutantes/v0480-d3-teste-enfraquecido-2.json:1 · as specs D3B5 (-2), D3C5 (-3) e D3D2 (-4) têm o `de` de linhas que o diff reescreveu em tests/catraca.py; `ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` falha no CI (suíte 4/5, 3.12 e 3.14) e aqui. Alinhe as três ao texto novo no mesmo commit.
- A2 (recomendado) tests/catraca.py:701 · ajudante levado para outro módulo (refatoração para um util comum) agora barra como "perdeu asserção" sem dizer que a asserção estava no ajudante; falha fechada, mas a mensagem do R-CONFORMIDADE podia citar o ajudante que deixou de ser achado.

## Sondas
- S1 · python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes em ab293a4e · espera: OK · obtido: FAILED, D3B5, D3C5 e D3D2 com o `de` fora da fonte

## Parecer
Reprovado só pelo A1: a lógica está correta e as guardas novas estão provadas, mas a suíte do CI fica vermelha porque três mutantes da v0480 apontam para o texto antigo de `_perfil_do_teste`, do laço de `testes_da_arvore` e de `mesmas_assercoes`. A correção é mecânica (trocar o `de`/`para` das três entradas pelo texto novo e conferir que os testes declarados delas ainda matam), sem mudar código.

O que conferi, pelo que o brief pede:
- **Nada que barra hoje deixa de barrar, salvo o que a troca na própria linha já deixava.** Sonda própria comparando a catraca da base com a da branch sobre os 6828 `def test_*` de `tests/`: 1736 mudam de contagem, nenhum desce, nenhum muda pulos nem "vazio", nenhum perde valor esperado (4,5 s). A única passagem de "perdeu asserção" para silêncio é trocar `self.assertEqual(self.r, esperado)` por `self.h()` cujo corpo faz `self.assertTrue(self.r)`; a base já deixava passar a mesma troca escrita na linha (`self.assertTrue(self.r)` no lugar), então o ajudante não abre caminho novo. Os pulos continuam só do corpo do teste, como antes.
- **`self.fica` -> `self.sai`:** a chave `ajudante fica` some do contador de esperados, vira `VALOR_TROCADO` e aparece em `valores_para_conferir` (teste `test_ajudante_invertido_fica_listado_para_o_revisor`); barra na volta contra o aprovado, como qualquer valor trocado (decisão do dono de 24/11). Ajudante sem asserção trocado pelo com asserção, ou chamada tirada, barra como "perdeu asserção".
- **Recursão e outro módulo:** recursão mútua `a`<->`b` no módulo conta 8 (o fundo), sem laço; base em laço (`class A(B)`/`class B(A)`) para em `vistas`; leque de 40 métodos com 3 chamadas cada, 8 níveis, sai em 0,00 s pelo `functools.cache` por (def, fundo). `from outro import confere`, `outro.confere()`, `self.nao_existe()`, `f()()`, `x[0]()` e `super().h()` contam 0 sem exceção.
- **`mesmas_assercoes`:** com `antes[0] > 0`, apagar um teste sem asserção não pareia mais com qualquer teste novo vazio; renomear um teste que só chama ajudante com asserção pareia, porque o perfil carrega `ajudante <nome>` e as constantes da chamada.
- **Mutantes (V2):** `bin/forge-mutante --processos 1` nas duas specs: CA1-CA13 morreram; `--cobertura --base 220ba3fa`: as 11 linhas de guarda do diff cobertas. `AssercaoNoAjudante` e `TestesAfrouxados` (27 testes) passam no clone.
- **CI do #891 em ab293a4e:** vermelho na suíte 4/5 (A1); `catraca` pede o rótulo `afrouxa-regra` do dono por tocar `tests/catraca.py` (controle; ADR 0008), o que é esperado e fica com o dono depois do último push; `bateria (pareceres)` espera os pareceres.

Leitura (checklist): nomes e docstrings dizem o que fazem; `_assercoes` separa o corpo do perfil sem duplicar; o cache por classe é necessário porque `self.x` resolve diferente em cada uma. A resolução de bases por `_nome(base)` com `classes` indexado por nome em todo o módulo pode confundir duas classes homônimas aninhadas, mas os dois lados da comparação usam a mesma resolução, então não gera perda falsa.
