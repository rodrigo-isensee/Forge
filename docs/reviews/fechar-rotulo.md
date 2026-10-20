---
tipo: review
contrato: 1
pedido: fechar-rotulo
branch: melhoria/fechar-rotulo
commit: 8b619b3a431685d0f93e54013d3750e903554b69
parecer: aprovado
revisor: forge:tech-lead (outra instância)
data: 2026-10-20
---
# Review do FECHAR-ROTULO: o passo 5 do `forge-fechar` não para por texto citado e o `--dry-run` avisa o controle

Escopo: `git diff 50997b72e65d11a7cace0bbc5d4aaf5a55b68d60 8b619b3a431685d0f93e54013d3750e903554b69` (bin/forge-fechar, changelog.d/fechar-rotulo.md, docs/fechamento-integrador.md, tests/test_fechar.py), um commit.

## O que conferi
- E1: o passo 5 (`bin/forge-fechar:149`) só para quando o título ou o corpo traz uma linha de item de checklist marcada (`- [x]` ou `* [X]`, com recuo opcional) que cita `afrouxa-regra` e o rótulo não está entre os aplicados. Texto livre, título que cita o nome e item desmarcado não param mais. Um PR com a linha marcada e sem o rótulo continua parando, sem `pr merge`, `pr edit` nem `--add-label` (teste). As duas leituras do `gh` seguem com falha fechada (`die`). A forma da marca segue a DECISÃO TÉCNICA do Histórico do pedido (o modelo de PR não tem o item; incluí-lo é o cartão MODELO-PR-ROTULO). Se o passo mais estreito afrouxa algo, quem julga é a segurança (E1.3). Pelo lado do código: o passo 5 nunca foi o controle do rótulo, que é a Catraca do CI, exigida verde no passo 4, e a documentação diz isso.
- E2: o dry-run importa `tests/catraca.py` por `importlib` (`python3 -I`) e usa `PROTEGIDOS`, `alterados` e `base_efetiva` da própria catraca, sem cópia da lista no script. Só lê o `git` local (`diff` e `merge-base`), sem rede e sem `gh` (o teste confirma que nenhuma chamada sai). Se o Python ou a importação falham, imprime "não consegui conferir" (`bin/forge-fechar:97`). Quando a lista não está vazia, a linha de aviso nomeia os caminhos e cita R-CONFORMIDADE pelo ID. Rodei `bin/forge-fechar fechar-rotulo --ref melhoria/fechar-rotulo --dry-run` na worktree: sete passos, sem aviso, o que está certo, porque o diff não toca nada de `PROTEGIDOS`.
- E3: há testes novos para item marcado sem rótulo (para), item marcado com rótulo (segue), texto que só cita o nome com item desmarcado (não para), `* [X]` com recuo (para), dry-run com `hooks/parecer.py` no diff (avisa e não chama nada) e sem controle (não avisa), além da ausência da lista copiada. `python3 -m unittest tests.test_fechar -q`: 27 testes, OK. O vermelho antes do verde (3 de 27 na develop) vem do relatório do autor; reproduzi-lo é do QA (PQ-1 do pedido).
- Documentação: `docs/fechamento-integrador.md` (passo 5 e `--dry-run`) e o cabeçalho do script mudaram junto. `agents/tech-lead.md` só cita o script de forma genérica e continua certo. Fragmento `changelog.d/fechar-rotulo.md` no formato, sem edição do `CHANGELOG.md`.
- Invariantes: nenhum trecho de `invariantes` (`tests/config.json`) mora nos arquivos do diff, e o diff não toca `tests/config.json`. Nenhum saiu.
- AntiDuplicacao: as regras aparecem pelo ID (R-CONFORMIDADE, R-FLUXO, R-CONTRIB), sem trecho de regra entre aspas.
- Regras da fábrica: R-CUSTO (sem API nem serviço pago; o dry-run segue sem rede), R-NEUTRO (nenhum termo de projeto), R-VERIFY/R-MAIN (nada mudou nas guardas de base e de main). Fora do escopo respeitado: `bin/forge-check` e `.github/` não mudam.
- Ferramentas: o Forge não tem `docs/engineering/praticas.md`. O `shellcheck` não está instalado nesta máquina e quem o roda é a bateria do CI no PR; fica pendente para o CI, sem revisão manual no lugar.
- Segurança: o parecer próprio é da E1.3 (`docs/security/`), que roda em paralelo; aqui não refaço essa análise.

## Achados

## Detalhe dos achados
- R1 (recomendado) bin/forge-fechar:85 · se a `git diff` da catraca falha (por exemplo, `--ref` sem branch local), `alterados` devolve lista vazia e o dry-run fica mudo, sem o "não consegui conferir". Reproduzi com `--ref melhoria/nao-existe-xyz --dry-run`: rc 0, nenhum aviso. Não afrouxa nada, porque na execução real o passo 2 para e a Catraca continua barrando. Mas a promessa "avisa quando não consegue" vale só para a importação. Sugestão: conferir antes `git rev-parse --verify -q refs/heads/$ref` e a base, e cair no mesmo aviso quando faltar uma das duas.
- R2 (recomendado) tests/test_fechar.py:212 · o teste "sem controle" só afirma a ausência de "vai ser pedido", então também passaria se saísse o aviso de "não consegui conferir". Falta ainda um teste do caminho de falha (catraca ilegível ou ref ausente). Sugestão: afirmar a ausência de `aviso:` no stdout e acrescentar um caso que force a falha.
- R3 (recomendado) tests/test_fechar.py:220 · o teste de ausência da lista copiada procura só `.githooks/`. Uma cópia parcial (por exemplo, `hooks/parecer.py` no script) passaria. Sugestão: percorrer `catraca.PROTEGIDOS` e afirmar que nenhum item aparece no script.
- Observação (sem ação): o caminho da catraca vem da pasta do próprio script (`bin/forge-fechar:68`). Quando o script roda pelo PATH, a lista lida é a da cópia instalada (`~/.local/share/forge/vigente/tests/catraca.py`, que existe), não a da branch. Para um aviso isso basta, porque a lista que vale é a da Catraca no CI.
