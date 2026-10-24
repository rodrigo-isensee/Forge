---
tipo: review
contrato: 1
pedido: MEDIR-M14B-REV
branch: melhoria/medir-m14b
commit: 19ea7240975b4c68968fa90bc4fbe49001e9d189
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-23
---
# Review: MEDIR-M14B

## Achados

## Parecer
Aprovado. Diff lido por inteiro (8 commits, base `origin/develop` 7423c44): `bin/forge-check`, `tests/test_medidas_m14b.py`, textos do Jarvis e do agile-coach, `changelog.d/medir-m14b.md` e os três arquivos de suporte. Ferramentas: `python3 -m unittest tests.test_medidas_m14b tests.test_testes_tocados` deu 94 testes, OK, em 45 s na worktree do commit revisado. Não há segurança nem devops no diff (só leitura local, sem rede, sem custo: `R-CUSTO` preservado, `R-NEUTRO` sem termo de projeto).

**As cinco medidas da M14b (linha `MELHORIA: M14b` do estudo):**
1. Custo por pedido e casamento do `--pedido`: `cartoes_do_pedido` casa cartão igual, família por prefixo até `-` e coluna Pedido do `KANBAN.md`; `janela_do_pedido` e `transcricao custo --pedido` o usam e imprimem os cartões casados. O texto do Jarvis manda rodar o comando no fim do pedido. Faz o que se pede; testes cobrem família, quadro, prefixo sem hífen e controle no nome.
2. Esperas: `forge-check esperas` mede dono, credencial e bloqueio sem motivo, com continuidade entre colunas do mesmo tipo e espera aberta. Testes incluem o registro real do `movimento`. Faz o que se pede.
3. PRs `fix` que corrigem PR mesclado: `forge-check corrigidos`, `cita` (prova) separado de `arquivo` (indício). Rodei na `origin/develop`: 185 PRs, 31 `fix`, 4 `cita`, 26 `arquivo`, 1 `nenhuma`, em 0,5 s. Faz o que se pede.
4. Defeito escapado: `escape registrar` e `escape resumo`, formato fixo, recusas que citam o campo e não o valor, sem escrever por link simbólico nem sem `KANBAN.md`. Faz o que se pede.
5. Rótulos `afrouxa-regra`: `afrouxamentos` reaproveita a catraca do CI (`real`, `so-protegido`, `sem-violacao`, `sem-commit`, `erro-git`). Faz o que se pede; a parte "sha da `homolog` já diferiu do da `develop`" da linha do estudo não está no escopo do pedido nem no código, ver recomendação 3.

**Testes:** `tests/test_medidas_m14b.py` cobre o comportamento e as bordas de cada comando (entrada ruim, ref inexistente, sem arquivo, sem histórico, quadro ausente), com o último grupo conferindo que os textos dos agentes e a tabela de métricas citam cada medida.

**Arquivos de suporte, todos necessários e corretos:**
- `bin/forge-testes`: o módulo novo executa o `forge-check`, então precisa entrar em `FORGE_CHECK`, que a guarda `MapaDoForgeCheck` compara com os arquivos; sem isso a suíte falha.
- `tests/test_testes_tocados.py`: a contagem 13 para 14 é consequência direta, e o nome do teste acompanha.
- `docs/melhoria-continua.md`: a tabela de métricas é a fonte única de "como coletar"; o teste do último grupo exige as medidas nela e a documentação afetada vai na mesma entrega.

**Recomendações (não bloqueiam, sem cartão exigido):**
1. `corrigidos`: 26 dos 31 `fix` caem em `evidencia=arquivo`, indício ruidoso; ao ler a linha de base, use só `cita` como prova, como a tabela já diz.
2. `escape resumo`: a taxa conta pedidos "Pronto" pelo nome do cartão do histórico, não pelo pedido; aproximação aceitável, mas anote isso ao publicar o número.
3. Se o dono ainda quiser a comparação dos shas `homolog` e `develop` da linha do estudo, é medida à parte; hoje nenhuma ferramenta a faz.
