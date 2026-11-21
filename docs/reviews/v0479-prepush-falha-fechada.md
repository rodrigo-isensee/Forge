---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-prepush-falha-fechada
commit: 653b44116a942dc9c8d7bfd8d7895472ce12930a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 E82.2 (PREPUSH-MODELO-FALHA-ABERTA)

Escopo: proposta `docs/propostas/prepush-modelo-falha-aberta.md` (diff de 12 linhas para o `templates/projeto/.githooks/pre-push`, arquivo travado que o dono aplica), `tests/test_prepush_falha_fechada.py`, `tests/mutantes/v0479-prepush-falha-fechada.json`, mapa do `bin/forge-testes`, `tests/pesos-d4.json`, `CITACOES_CONHECIDAS` de `tests/test_reval_delta.py` e o fragmento do changelog. Base 2097f9bf, head 99a4fc30.

## Achados
- A1 (recomendado) docs/propostas/prepush-modelo-falha-aberta.md:84 · sem python3, o case barra qualquer config que cite "registros", também com a chave vazia, que o contrato do hook trata como nada a conferir; só aperta, mas convém dizer isso na seção 2 ou no critério de reversão.
- A2 (recomendado) tests/test_prepush_falha_fechada.py:50 · com o patch já aplicado no modelo, o teste usa o hook como está e os mutantes, que mutam a proposta, passam a sobreviver; quando o dono aplicar, mover a spec para o modelo ou apagar a proposta junto.

## Sondas

## Parecer
Aprovado. Faz o que o cartão pede, só aperta (`R-CONFORMIDADE`: nada de variável que pule) e respeita a trava do modelo, entregando proposta em vez de escrever no arquivo travado.

Leitura do diff:
- `lider_vivo`: o `for` sobre `$(jobs -rp)` depende só do IFS padrão; o hook não muda o IFS fora do `read` da linha 74, então a troca é equivalente com o `tr` presente e corrige o caso sem ele.
- `dirname`: o status da atribuição é o da substituição, logo ausente (127), com erro ou com saída vazia barra; a guarda roda antes do `[ -x ]`, cobrindo também o `pre-push.local` gerado. Os `tr -d ' '` das linhas 155 e 158 sem o `tr` só degradam o alvo do sinal ao próprio `$etapa`, como a proposta registra.
- `comando_de_registros`: `$(<arquivo)` é do bash, sem utilitário novo; mensagem diz o que falta.
- Mapa do `forge-testes`, peso D4 e as duas citações conhecidas são coerentes com o teste novo (o teste lê a proposta; o mapa só cita o caminho). Tamanho (H1): 12 linhas de código no diff do hook, dentro do teto.

Verificações rodadas neste review (sem a suíte, que é do CI, `R-REVIEW`):
- `git apply --check docs/propostas/prepush-modelo-falha-aberta.md` sobre o head: aplica.
- `python3 -m unittest -v tests.test_prepush_falha_fechada`: 8 testes, OK em 4 s.
- `bin/forge-mutante --processos 1 tests/mutantes/v0479-prepush-falha-fechada.json`: M1 a M8 morreram (linhas 51, 62, 62, 63, 83, 84, 84, 85); cada mutação troca uma linha `+` inteira sem mudar a contagem do hunk, então o patch mutado aplica e a morte vem do comportamento, não do `git apply`.
- `bin/forge-mutante --cobertura --base 2097f9bf`: só `tests/pesos-d4.json` não coberto (dado de peso, sem guarda).
- `shellcheck` não está instalado nesta máquina; o hook com o patch não está na árvore, então o CI também não o passa pelo shellcheck até o dono aplicar.

Testes leem comportamento (rc, mensagem e o arquivo `rodou`), com o ambiente limpo por `sem_git_herdado` e PATH só na pasta de links; nenhum lê o texto da fonte do hook.

## Revalidação (E82.6, head 653b4411)
Delta lido: `forge-check parecer delta` sobre 99a4fc30..653b4411, no domínio só `tests/test_prepush_falha_fechada.py`. A classe `RegistrosSemPython` perdeu o `skipUnless(python3)`; o caso de controle passa o `python3` como falso que faz `exec` do `sys.executable`, então roda sem python3 no PATH da máquina e continua só com a pasta de links no PATH. Os casos "sem python3" já tiravam o link e não mudaram. Rodados: o módulo, 8 testes OK em 2,8 s com ambiente limpo; `bin/forge-mutante --processos 1` na spec, M1 a M8 morreram. Os achados A1 e A2 seguem recomendados, sem mudança. Aprovado no head.
