---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-oraculo-hermetico
commit: 2affeefe68cc7006f370800400b22276ee9f64c7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481, testes herméticos do oráculo (E27.4)

1ª rodada completa sobre `707fea56..2affeefe` (4 arquivos, só `tests/` e `changelog.d/`). Nenhum arquivo de `bin/`, `hooks/`, `scripts/`, `agents/`, `skills/` nem `.github/` muda.

## Gatilhos
Gatilhos: nenhum de produção; o diff toca o oráculo da guarda que adia a atualização com Claude vivo (RD4, RD11), revisto por pedido do dono.

## Achados
- A1 (recomendado) tests/sem_claude_ancestral.py:67 · Com --proc, proc_coerente vira True e os processos vêm da árvore do teste em todo o oráculo, também no CI: nenhum teste prova mais a guarda contra o /proc real. Falta um teste com claude vivo real exigindo duvida ou detecção.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `tests/sem_claude_ancestral.py:66-67` (troca `PROC` e `proc_coerente`) e `tests/test_oraculo_sempre_atual.py:474` (o processo vivo só entra na árvore montada). Antes, no CI, o oráculo rodava a leitura de produção (`bin/forge_sempre_atual.py:148-196`) contra o `/proc` do kernel; a lógica continua coberta pela árvore de mentira em `tests/test_sempre_atual.py:83` (`ProcFalso`, que mata os mutantes M1, M2, S17, S18), mas a integração com o procfs real (o `readlink` de `self`, o `cwd` mágico, o `comm` real, o `st_uid`) não tem mais teste em lugar nenhum. Caminho de ataque: não há atacante; o risco é regressão silenciosa da guarda (a leitura real passa a devolver "sem claude e sem dúvida") e a atualização seguir com sessão viva e trabalho em curso, com o oráculo verde. Severidade: baixa. Correção mínima: em `tests/test_sempre_atual.py`, um teste que lança um processo real de nome `claude` (link para o interpretador, sem `skip`) e chama `processos_de_interesse()` com o `PROC` real, afirmando `achados["duvida"] or <cwd> in achados["claude"]`. Vale nos dois ambientes sem ramo: no sandbox sai `duvida` (sondado aqui: `coerente: False duvida: True`, invariante verdadeira), no CI sai a detecção. Esforço: P. Dono: qa-engineer.

**O que aperta.** (1) O oráculo deixa de depender do `/proc` da máquina: sai o falso vermelho de 39 testes no sandbox, que levava a aceitar D2 vermelho como rotina e escondia vermelho de verdade. (2) Com `--proc`, a árvore só tem os processos do teste: some a contaminação por `claude` e `forge-fechar` de outras partes da suíte, que o filtro `descende_de` só atenuava. (3) `tests/test_forge.py:3587`: o `gh` passa a ser o falso de "sem PR"; antes o teste podia chamar o `gh` real com a credencial de quem roda, e agora não sai para a rede.

**O neutro.** Produção não muda: `bin/forge_sempre_atual.py:982-984` não tem `--proc` e a ferramenta não lê variável nova (SEG-2 do oráculo continua de pé). A costura é só a troca de atributos do módulo dentro do processo do lançador `tests/sem_claude_ancestral.py`, que nenhum script do Forge importa nem executa (grep em `bin/`, `hooks/`, `scripts/`, `.github/`: sem referência); o repasse aos filhos (`Popen` do lançador) só alcança scripts Python da mesma pasta, lançados pelo próprio teste. Nenhuma costura de injeção abre caminho em produção. O processo vivo continua real (pid real na árvore), então RD11 ("não derruba a sessão") segue provado de verdade. O oráculo foi editado pelo dono dele (QA, autor do E27.1), não é oráculo EXT-1 da segurança.

**O que afrouxa.** Só o A1: a prova ponta a ponta contra o `/proc` do kernel, que existia no CI, sai do oráculo. A coerência de namespace (`proc_coerente`) e o adiamento `duvida:proc` continuam provados em `tests/test_sempre_atual.py` sobre árvore de mentira; o afrouxamento é a ausência de qualquer leitura do procfs real.

## Riscos aceitos e ferramentas
Sem risco aceito. Rodado aqui, no sandbox, na cópia em 2affeefe: `tests.test_oraculo_sempre_atual`, `tests.test_sempre_atual` e `ForgeCheck.test_raiz_depois_do_subcomando_e_git_isolado`, 202 testes, OK. A suíte inteira fica para o CI do PR, que ainda não existe; este parecer não afirma CI verde. Sonda do A1 em `~/.forge-contrib/wt/_sec-v0481-hermetico-sonda.py`. Ferramentas de varredura de segredo, SAST e workflow ausentes no PATH (lacuna); o diff não toca segredo, workflow nem dependência.
