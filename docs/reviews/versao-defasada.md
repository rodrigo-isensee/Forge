---
tipo: review
contrato: 1
pedido: versao-defasada
branch: melhoria/versao-defasada
commit: 2b6abddd698eb0385e8d7ac08021ba5e9152f309
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Code review: versão defasada (E2.2)

Rodada 1, sobre `8833e1c..2b6abdd` (2 commits, 10 arquivos, 650+/24-). Revisor diferente do autor da E2.1 (D-ETAPAS-INST). Segurança de `hooks/`, `bin/` e `scripts/` é da E2.3 (`security-engineer`, R-SEGURANCA), não refeita aqui.

Ferramentas rodadas em 2b6abdd: `python3 -m unittest tests.test_doutor tests.test_forge.FerramentaDefasadaNoForge tests.test_forge.FerramentaDefasadaNoProjeto` → `Ran 80 tests ... OK` (rc 0). Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO; o autor declarou 903 OK e validar-plugin OK; o QA os refaz no head). Shellcheck: ausente na máquina (`command -v shellcheck` vazio); pendência já levada pelo Jarvis ao critério do merge (E2.5, bateria do CI).

## Achados
- A1 (bloqueante) hooks/parecer.py:171 · o hook chama fc.cmd_pr direto e a guarda só roda em executar (bin/forge-check:3036): gh pr create/ready/merge passa com cópia atrasada. A VD-3 ajustada pelo aq, escolhida pelo dono, inclui o hook parecer. Chamar guarda_de_versao no verificar, com teste.

## Detalhe dos achados
**A1.** O Histórico registra a VD-3 ajustada do aq com o bloqueio em pr, entrega, delta e brief gerar, e por eles no hook `parecer`; a decisão do dono de 2026-10-19 (garantia A) escolhe essa VD-3 ajustada, e a outra decisão do mesmo dia pede a garantia para todos os projetos. O brief da E2.1 (item 1) omitiu o hook, então a lacuna nasceu no brief, não no autor; mas o resultado fere a decisão: `hooks/_comum.py:495` carrega o `forge-check` como módulo e `hooks/parecer.py:171` usa `cmd_pr` sem passar por `executar`, logo um `gh pr ready` ou `gh pr merge` com a cópia comprovadamente atrasada não é barrado. Sugestão: no `verificar` do `parecer`, chamar a mesma comparação (`guarda_de_versao` ou uma função que devolva o estado) e bloquear com a mesma frase só com prova positiva; erro de comparação não bloqueia. Teste com a cópia falsa atrasada de `tests/apoio_versao_defasada.py`. Precisa de brief de volta (outro papel, D-ETAPAS-INST).

**R1 (recomendado, para o dono decidir, R-DECISAO).** No Forge, a comparação por commit (`bin/forge-check:2879`) faz toda mesclagem na `develop` deixar a cópia vigente atrás da `origin/develop` dos PRs seguintes. Com a guarda já na cópia vigente, o integrador não confere o segundo PR da mesma sessão até a pessoa rodar `jarvis-forge --atualizar-vigente` e reiniciar: a fila noturna para a cada merge. É o comportamento decidido (prova positiva de atraso), não erro de código, mas o custo em tempo não foi posto ao dono. Opção a levar: só contar atraso quando o intervalo entre a cópia e a base muda `bin/`, `hooks/` ou `tests/config.json` (exige o objeto da base; sem ele, segue bloqueando).

**R2 (recomendado).** `README.md:39` ainda diz que, com o tmux aberto, o script avisa numa linha e segue; falta o aviso de defasagem em toda reanexação e o `ATRASADO desde <data>` (definição de pronto: documentação afetada na mesma entrega). Uma frase basta.

## Itens 1 a 4 do brief da E2.1 contra as decisões do dono
1. VD-3: compara por commit no Forge e nos clones (`--base-sha` na entrega, `origin/<base>` nos demais) e pelo cache nos projetos; bloqueia `pr`, `entrega`, `delta` e `brief gerar` com a frase pedida; os outros avisam; erro vira `versão não conferida`. Testes de cópia atrasada (com e sem o objeto), igual, mais nova e erro. Conforme, exceto o hook (A1).
2. VD-1: aviso em toda abertura e reanexação, com a data e o comando; sem rede ou recusa diz `ATRASADO desde <data>`; com a sessão aberta só faz `fetch` na cópia vigente, sem trocar a árvore. Testes com remoto `file://`. Conforme.
3. VD-2 reduzida: falha não marca o dia, cache com `defasado`, `atual` e `ultima`, texto por superfície (`forge atualizar` e `jarvis-forge --atualizar-vigente`). Conforme. ADR 0003 intacta: só `systemMessage` (teste `test_o_aviso_do_hook_nunca_entra_no_contexto_do_modelo`). VD-4 fora.
4. Fragmento `changelog.d/versao-defasada.md` presente. Conforme.

R-CUSTO: só `git` local e arquivos na guarda; a única rede segue a consulta já existente do doutor. R-CONFORMIDADE: nenhum caminho atualiza o plugin; todas as mensagens mandam a pessoa rodar o comando.

## Texto único e invariantes
- A descrição da guarda fica só em `docs/hooks.md` (a ferramenta defasada) e no fragmento; as regras são citadas por ID. Sem duplicação.
- `tests/config.json`: só acrescenta invariantes (`bin/forge-check` ganha 2, `scripts/jarvis-forge` nasce com 2; a linha `Melhoria vista:` volta igual, com vírgula). Nenhum saiu.

## Suposições do autor
- (a) Cópia sem o objeto da base conta como atrasada (`bin/forge-check:2894`): aceita. No Forge e nos clones a cópia vigente e o repositório são o mesmo histórico; um commit da `origin/develop` que a cópia não conhece só existe porque ela não buscou depois dele. A base da entrega vem do brief (commit da develop), não de commit local.
- (b) Prova nos projetos pelo cache `defasado: true`: aceita. Vale só com `atual` igual à versão desta cópia e menor que `ultima`; release não volta, então cache antigo segue verdadeiro, e plugin já atualizado invalida o cache (teste `test_sem_prova_positiva_nao_bloqueia`).
- (c) `forge-check` dentro do próprio repositório não se compara: aceita. É o caso dos testes e do `--dev`; a cópia conferida é a própria ferramenta (teste `test_a_propria_copia_como_repositorio_nao_se_compara`).

## Acréscimos fora do brief
- `sleep 3` (`scripts/jarvis-forge:171`): só com `avisou_defasagem=1` e stderr em terminal; abertura normal e em dia não espera (teste `test_abertura_que_atualiza_nao_avisa_atraso`). Conforme a DECISÃO TÉCNICA do Jarvis no Histórico; não bloqueia.
- Nova tentativa do doutor depois de 10 min (`hooks/doutor.py:26`): a decisão (VD-2 reduzida) já tira a marca do dia na falha, o que sem espera custaria até 3 s em cada `Stop` sem rede; a espera reduz esse tempo, não o aumenta, e não gasta tokens (só `systemMessage`). Não bloqueia.

## Commits
Dois, Conventional Commits em português, um por superfície (`forge-check`; doutor e `jarvis-forge`), com corpo explicando o comportamento. Limpos.

## Parecer
Reprovado por A1. R1 é decisão do dono e não segura o código; R2 entra na mesma volta.
