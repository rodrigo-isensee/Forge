---
tipo: revisao-seguranca
contrato: 1
pedido: versao-034
branch: melhoria/testes-sem-claude-ancestral
commit: 9a08b1c860fc0c24f47467429018020680ba5811
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033 (TESTES-SEM-CLAUDE-ANCESTRAL)

## Gatilhos
Controles do Forge (R-SEGURANCA): a entrega mexe nos testes da guarda `dentro_do_claude()` (`bin/forge_versoes.py:510`), que sustenta R-CONFORMIDADE para `forge atualizar`, `forge voltar-versao` e `forge sugerir`. A guarda de produção e o hook `conformidade` não mudaram (diff só em `tests/` e `changelog.d/`).

## Achados
- A1 (recomendado) tests/sem_claude_ancestral.py:37 · O lançador vai no plugin e, com env -u das duas variáveis, desliga a guarda ao rodar um bin/ por caminho que o hook não reconhece (link simbólico). Não é capacidade nova (ver A2); barrar a palavra sem_claude_ancestral no hook custa pouco e não afeta a suíte.
- A2 (recomendado) bin/forge_versoes.py:515 · Lacuna anterior a esta entrega: env -u das duas variáveis mais setsid -f (o processo é adotado pelo init) já escapava da leitura de ancestrais, e o hook não vê bin/ renomeado ou por link. Registrar como risco conhecido ou endurecer em pedido próprio.

## Detalhe dos achados
**Pergunta 1: o agente escapa da guarda pelo lançador?** Só combinando duas coisas. O lançador troca apenas `_pai_e_nome` (`tests/sem_claude_ancestral.py:36-37`); a checagem das variáveis `CLAUDECODE` e `CLAUDE_CODE_ENTRYPOINT` (`bin/forge_versoes.py:513`) fica intacta. Prova com uma sonda inofensiva (cópia de `forge_versoes.py` e um script que só imprime `dentro_do_claude()`), na sessão real do agente (o pai do shell é o `claude`): direto, `True`; pelo lançador com `--ate $$`, `True`; pelo lançador com `env -u` das duas variáveis e `--ate` igual ao pid do shell, `False`.
O hook `conformidade` barra o lançador quando o nome do binário aparece na linha: `python3 tests/sem_claude_ancestral.py --ate 1 bin/forge-atualizar`, `.../forge-voltar-versao`, `.../forge-sugerir --fila` e `bin/forge atualizar` saem com código 2 (`hooks/conformidade.py:1666-1685`). Passa (código 0) quando o binário vem por link simbólico (`/tmp/a` apontando para `bin/forge-atualizar`), porque o lançador resolve o caminho (`:31`) e acha `forge_versoes.py` ao lado.
**Comparação com antes:** a mesma fuga já existia sem o lançador. `env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT setsid -f sh -c "python3 <sonda>"` imprimiu `False` (o processo vira filho do init e a leitura de ancestrais não encontra o `claude`), e o hook deixa passar `env -u ... setsid -f python3 /tmp/a`. Também já passava `env -u ... python3 /tmp/a` no hook (a guarda recusaria pelo ancestral, mas o setsid resolve isso). As confirmações (`fv.confirmar`) leem a entrada padrão e aceitam um `s` canalizado, nos dois caminhos. Logo, o lançador não abre capacidade nova; só entrega pronta uma das formas. Caminho de ataque: agente desalinhado ou induzido por injeção de prompt, dentro da sessão, que deliberadamente contorna a regra; ganho: atualizar o plugin ou abrir issue no Forge sem a pessoa. Severidade: baixa (exige intenção explícita de contorno, e a fuga equivalente já existia). Correção mínima de A1: no hook, barrar linha com a palavra `sem_claude_ancestral` (a suíte não a escreve na linha de comando; quem a usa é o `unittest`, dentro do processo). Esforço P. Dono: dono do hook `conformidade` (melhoria do Forge). A2: pedido próprio ou registro como risco conhecido, decisão do usuário (R-DECISAO). Esforço M. Dono: idem.
**Pergunta 2: a troca vaza para fora do teste?** Não. A troca é atribuição em memória no processo lançado (`:37`) e a subclasse de `Popen` (`:39-46`) só reescreve filhos `sys.executable <script>` cujo script está no mesmo `bin/`. Nenhuma variável de ambiente é criada, nenhum arquivo é escrito, não há `sitecustomize` nem `.pth` novo (o único `sitecustomize` do repositório é `tests/apoio_pathlib_312/`, anterior e não relacionado). Nenhum script de `bin/` nem de `hooks/` importa o lançador (grep). O `--ate` dos testes é sempre `os.getpid()` do próprio teste.
**Pergunta 3: o teste novo prova que um `claude` abaixo do teste segue visível?** Sim. `tests/test_atualizar.py:695-710` põe um script `/bin/sh` chamado `claude` entre o teste e o lançador, com o ambiente já sem as duas variáveis (então a recusa só pode vir do ancestral), para `forge-atualizar` e `forge-voltar-versao`, e exige código 2, a mensagem de recusa e nenhuma chamada ao `claude` falso. Mutação: trocar a linha 37 por `lambda pid: (0, "")` (ignorar todos os ancestrais) faz o teste falhar; restaurado depois. Se o `sh` fizesse `exec` do filho, o nome `claude` sumiria e o teste falharia, não passaria em falso. Lacuna pequena: o teste não cobre `forge-sugerir`, mas ele usa o mesmo `fv.dentro_do_claude()` (`bin/forge-sugerir:275`) e o mesmo lançador.
**Observação de estabilidade (não é achado):** numa execução isolada com `-v`, o teste novo estourou o timeout de 60 s uma vez, coincidindo com o shell da sessão ser movido para segundo plano; não se repetiu em 8 execuções seguintes (0,6 s cada). Fica para o QA observar.

## Riscos aceitos e ferramentas
Nenhum risco aceito nesta entrega. Testes rodados (só os arquivos tocados, D-5), de dentro do Claude Code: `tests.test_atualizar` (80 testes, OK) e `tests.test_sugerir` com `tests.test_atualizar.Dentro` (42, OK). Sonda local inofensiva e alimentação do hook com linhas de comando (sem rodar `forge atualizar` nem `forge sugerir` de verdade). `gitleaks`, `semgrep` e afins não usados: diff só em testes Python, sem segredo nem dependência nova.
