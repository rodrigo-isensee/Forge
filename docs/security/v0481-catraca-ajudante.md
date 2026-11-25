---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-catraca-ajudante
commit: ab293a4e9da5ca4969ff60e8734b020d7b07bced
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E14.18, #891, catraca conta asserções de ajudantes; classe C)

Lido: `220ba3fa..ab293a4e` inteiro (`tests/catraca.py`, `tests/test_catraca.py`, `tests/mutantes/v0481-catraca-ajudante.json` e `-2.json`, `changelog.d/v0481-catraca-ajudante.md`). Primeira rodada de segurança da branch; sem parecer anterior.

Gatilhos: controle do Forge (a catraca, que decide o bloqueio por teste afrouxado; R-CONFORMIDADE).

## Conferência
- **O PR não se aprova sozinho.** O job usa a catraca da base (`.github/workflows/catraca.yml:39-46`), e ela barra a mudança em `tests/catraca.py` sem o rótulo do dono (visto no run da Catraca em `ab293a4e`). A regra por teste também não lê a própria catraca (`tests/catraca.py:795`).
- **Só aperta ou neutro, por escrito: neutro, com uma ressalva (S5).** O que mudou fica só em `testes_da_arvore`/`_perfil_do_teste` (regra D3 por teste); `_forca_das_arvores` (somas e módulos de controle, MAQ-I7a) não mudou. Na árvore real (S1, 6828 testes do head), nenhuma contagem desce, 1736 sobem, e pulos, vazio e valores esperados da base ficam todos contidos no head. Pulos: a soma é a mesma de antes (classe, decoradores e corpo); os pulos dentro do ajudante continuam fora, como antes. `mesmas_assercoes` aperta: teste de 0 asserções não pareia mais como renomeado (`tests/catraca.py:784`; S7). Ressalva S5: trocar uma asserção direta do teste por uma chamada a ajudante com asserção barrava antes e agora passa calado; o mesmo resultado já se obtinha antes trocando-a por uma asserção direta mais fraca e não vazia (S6, silenciosa nas duas versões). Quem escreve o teste não ganha capacidade nova: neutro, sem achado. Quem quiser o "nada que barra deixa de barrar" literal pode guardar a contagem só direta como piso (perfil com mais um campo); não exijo.
- **`self.fica` por `self.sai` passa a ser vista** (S2): vira "trocou ou tirou valor esperado" (`ajudante fica` some dos esperados), listado para o revisor na primeira entrega e barrando na volta; se o ajudante novo tem menos asserções, "perdeu asserção" barra sempre (`tests/catraca.py:765`).
- **Recursivo e de outro módulo não quebram** (S3, S4): a recursão para em `FUNDO_DOS_AJUDANTES` (`tests/catraca.py:685`, `:725`), e o laço de bases é cortado por `vistas` (`:692`; teste `test_ajudante_com_assercao_conta_e_o_sem_assercao_nao`). A função importada de outro módulo e `mod.f()` não resolvem (contam zero, como antes).
- **Orçamento de tempo** (A1): na árvore real, 0,67 s passam a 1,41 s. Na entrada adversarial (muitos ajudantes que se chamam), o custo cresce perto do quadrado do tamanho do módulo: 213 KB em 3,75 s e 2,6 MB em 100 s, contra 0,00 s antes (S9). O `TETO_DO_MODULO` (2 MiB) só vale para os módulos de controle e foi dimensionado para o custo antigo.
- Testes: `python3 -m unittest tests.test_catraca` → 412 testes, OK. A suíte inteira roda só no CI do PR #891, no mesmo head `ab293a4e`; ao escrever, estava em andamento, com a Catraca vermelha só pelo rótulo do dono e `bateria (pareceres)` vermelha porque os pareceres faltavam. O merge depende dela verde.

Sondas executadas, nenhuma prova bloqueante (catraca da base × a do head, `$TMPDIR/sec891/sonda.py` e `sonda_tempo.py`): S1 árvore real (sobem 1736, descem 0, perdas 0); S2 `self.fica("a")`→`self.sai("a")` (base: nada; head: valor trocado); S3 recursivo tirado (head: perdeu asserção); S4 ajudante importado tirado (nada nas duas); S5 `self.assertTrue(resultado())`→`self.fica(resultado())` (base: perdeu asserção; head: nada); S6 o mesmo por `self.assertTrue(self)` (nada nas duas); S7 renomeado com 0 asserções (barra nas duas); S9 tempo acima.

## Achados
- A1 (recomendado) tests/catraca.py:729 · custo da expansão de ajudantes sem orçamento: módulo de 2,6 MB com ajudantes que se chamam leva 100 s (antes 0 s), perto do quadrado do tamanho. Ponha teto de expansões por módulo que, estourado, conta o módulo como ilegível (falha fechada), com teste de tempo

## Sondas

## Detalhe dos achados
- **A1.** Evidência: `tests/catraca.py:725-730`. Cada chamada a ajudante soma o `Counter` do ajudante (cacheado por `(alvo, fundo)`), e cada nível soma o de baixo, então o trabalho é o número de chamadas × as chaves acumuladas × 8 níveis. Caminho: quem abre PR põe em `tests/` um módulo gerado com centenas de ajudantes que se chamam. Depois do merge, todo PR que tocar esse módulo roda a catraca da develop sobre ele, nos dois lados e em até três passagens (`perdas_dos_testes` em `regra_testes_afrouxados`, na volta e em `valores_para_conferir`), contra os 10 minutos do job (`.github/workflows/catraca.yml:21`). O estouro falha fechado (job vermelho), sem desvio do controle. Severidade baixa (disponibilidade; quem ataca não ganha nada). Correção mínima: contador de trabalho em `_ajudantes` (por exemplo, soma das chaves mescladas ou das chamadas expandidas) com teto fixo; estourado, o módulo é tratado como ilegível, como no `_arvore_do_modulo`: some de `_testes_por_modulo`, e os testes da base dele barram como "apagado". Mais o teste com a entrada da S9 (100 ajudantes × 100 chamadas) que mede o tempo sob o teto. Esforço P. Dono: autor do #891 (tech-lead).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, o módulo de teste tocado e as sondas locais acima (nada externo). Varredor de segredos, SAST e auditor de dependências não se aplicam ao delta, que não traz dependência nem segredo.
