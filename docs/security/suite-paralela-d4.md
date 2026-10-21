---
tipo: revisao-seguranca
contrato: 1
pedido: suite-paralela-d4
branch: melhoria/suite-paralela-d4
commit: 1bdd3e8522da941d89a8620a980196401e751126
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: suite-paralela-d4

Revisão estática do diff `ad6d96c..1bdd3e8` (13 arquivos), contra o modelo de ameaças `docs/security/ameacas/suite-paralela-d4.md` (T1 a T9, AB-1 a AB-14) e o desenho `docs/propostas/tempo/suite-paralela-d4.md`. Foco: `scripts/suite-paralela.py`, a fila e o PREPUSH-JA-NO-REMOTO em `.githooks/pre-push`, o lançador dos testes de hook em `tests/test_hooks.py` e os dois passos da suíte em `.github/workflows/ci.yml`. Sem execução própria da suíte (R-TETO; o pre-push deste envio a roda).

## Gatilhos
Controles do Forge (R-SEGURANCA): `.githooks/pre-push` (portão local da suíte, trava, fila, prova `.verde`), `.github/workflows/ci.yml` (jobs `rapida` e `bateria`) e `hooks/pesado.py` (lista do que é tarefa pesada).

## Achados

## Detalhe dos achados
Nenhum bloqueante. Conferência por controle do modelo de ameaças:

- **T1 (teste some da divisão): cumprido.** A divisão sai da lista de módulos (`scripts/suite-paralela.py:71`), conferida como partição exata (`:99`), e a guarda de completude compara o multiconjunto dos IDs iniciados em cada processo com a descoberta inteira feita no orquestrador (`:115`, `:364`, `:386`). Módulo em subpasta, módulo que não importa ou falha do preparo de módulo aparecem como ausentes ou como erro: falha fechada. Os pesos (`tests/pesos-d4.json`) só equilibram; peso ausente vale a mediana, arquivo ilegível vira mapa vazio (`:76`). AB-1, AB-2 com teste (`tests/test_suite_paralela.py:187`, `:194`).
- **T2 (falha lida como verde): cumprido.** Código de saída de cada filho, sinal como falha, relatório ausente e zero testes reprovam (`:305`); o veredito final exige erros, falhas e guarda vazios (`:406`); sem atalho de ignorar código de saída no caminho do veredito. No hook, `wait` pelo pid do filho (`.githooks/pre-push:250`). AB-3 a AB-5 com teste.
- **T3 (`.verde` com suíte parcial): cumprido.** A anotação continua depois do veredito e das condições de árvore limpa; interrupção sai pelo `parar`, com código 1 e sem anotar. Teste novo em `tests/test_pre_push_parecer.py` (vermelho não anota, verde anota).
- **T4 (ordem): cumprido.** Divisão por módulo, determinística (LPT com desempate por nome), sem repetição automática.
- **T5 (disco): cumprido.** TMPDIR próprio por processo (modo 700, dentro de pasta criada com permissão restrita, apagada no fim e no sinal); o orquestrador confere a árvore de trabalho e o `.git/config` comum antes e depois e reprova se mudarem (AB-13 com teste). Logs por processo ficam na pasta temporária privada e não imprimem o ambiente.
- **T6 (fila e trava): cumprido.** A senha nasce presa com nome oculto e só então entra na fila; senha cujo flock se obtém é descartada; a exclusão segue no flock do kernel; fila que é link ou de outro dono cai para só a trava (sem rodar sem trava); o prazo de 1200 s continua barrando (`barrar`). Processos com grupo próprio, `nice`, teto de 4 e `FORGE_SUITE_PROCS` fora de 1 a 4 recusado. Parar só a própria execução (`parar`, sem padrão de nome); a suíte chamada à mão passa pela mesma trava e fila (`--suite`) e a variável da trava é conferida (arquivo do usuário, não link, pid anotado, presa).
- **T7 (CI): cumprido.** Um job `bateria` com o mesmo nome e condição; os dois passos chamam o mesmo script, com a guarda de completude contra a descoberta inteira; `permissions:`, ações e segredos sem mudança; `release.yml` intocado, em série, como rede contra defeito de divisão (contraprova em `tests/test_ci_local.py`). Sem runner pago (R-CUSTO). No CI, sem a variável da trava, o script passa pelo hook em `--suite`; se a trava falhar ali, o job fica vermelho (falha fechada, nunca verde).
- **PREPUSH-JA-NO-REMOTO: cumprido pela decisão do dono (B).** Pula só com zero linhas no stdin (`.githooks/pre-push:136`), depois do laço que barra `main`/`homolog`/`develop` e antes da fila; não consulta a rede (AB-9 deixa de existir: não há consulta que possa falhar aberta); mesmo sha em outra ref gera linha e roda a suíte (AB-10); deleção gera linha e roda a suíte (PREPUSH-DELETE-SEM-SUITE fica fora); não anota `.verde`; o modo `--suite` nunca pula. Risco residual registrado no modelo de ameaças: o commit pode ter chegado ao remoto por um clone sem o hook; o CI repete tudo.
- **Lançador de 120 s do `test_hooks`: não esconde falha real do hook.** Só o prazo do git dos testes muda (`tests/test_hooks.py:291`); o mesmo arquivo do hook roda como `__main__`, com o mesmo módulo em cache (`hooks/_comum.py:652`), e o teste novo prova o efeito nos dois sentidos (git lento de 6 s passa com 120 e falha com 5). Hook travado continua detectado (prazo do processo de 120 s).

Recomendações (não bloqueiam; severidade baixa ou informativa; dono `tech-lead`, cartões):

- **R1 (baixa, P).** `.githooks/pre-push:250` roda a suíte com o descritor da trava fechado e o orquestrador não vigia o próprio pai (só os filhos vigiam o orquestrador, `scripts/suite-paralela.py:183`). Hook morto por SIGKILL solta a trava com a suíte ainda rodando, e outra pode começar em cima (carga dobrada, falso vermelho; não é fuga). Classe já existente antes da D4 (T6, residual). Correção mínima: o orquestrador também encerra os grupos quando o pai muda.
- **R2 (baixa, P).** O comentário de `tests/test_hooks.py:290` diz que o prazo de produção do git é conferido à parte, mas `test_timeout_de_rede_dos_hooks_abaixo_do_hooks_json` lê só `hooks/*.py`, não `GIT_TIMEOUT_S` de `bin/forge-check:102`. Nada impede subir esse prazo acima do timeout do `hooks.json` (o Claude Code mataria o hook: falha aberta). Não é regressão; somar a asserção ao cartão FC-GIT-TIMEOUT-ENV.
- **R3 (informativa, P).** `scripts/suite-paralela.py:222`: se o `git status` falhar antes e depois com o mesmo código, a conferência de árvore passa calada. Correção mínima: código diferente de 0 vira erro da guarda.
- **R4 (informativa).** `scripts/suite-paralela.py:276`: sinal entre o nascimento do filho e a entrada em `filhos`, ou pai morto antes de o filho ler o próprio pai, deixa um processo órfão até o fim dos módulos. Janela de milissegundos, sem efeito no veredito (o orquestrador já reprovou).
- **R5 (informativa).** `.githooks/pre-push:106`: a contagem de refs depende de cada linha do stdin terminar em quebra de linha (o git sempre a escreve). Só uma chamada à mão do hook, sem efeito no remoto, cairia no caminho de zero refs.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Ferramentas: leitura do diff e busca por padrões de credencial no diff (nada encontrado). Faltaram no PATH: `gitleaks`, `actionlint`, `zizmor`, `shellcheck` e Semgrep CE (não instalados, R-CUSTO; lacuna registrada). `shellcheck`, `actionlint` e `zizmor` rodam no job `bateria` do CI sobre este mesmo código.
