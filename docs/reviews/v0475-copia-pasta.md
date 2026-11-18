---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-copia-pasta
commit: efe73e1755211bf8d2db0dbbf1fb4e1fc2f808af
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.55, item E3.44, `bin/forge-copia`)

## Achados
- A1 (bloqueante) tests/test_forge_copia.py:20 · self.env não passa por ambiente_git.sem_manutencao; test_ambiente_git falha em test_forge_copia.py:28, :44 e :56, a suíte do CI fica vermelha. Montar o env com sem_manutencao (S-9).
- A2 (recomendado) docs/propostas/copia-pasta-settings.patch:9 · pendente: a parte "pelo modelo de projeto" da decisão do dono (item 2) só existe como patch; o modelo não muda neste commit. Dizer no PR que o dono aplica o patch (settings protegido) e ligar ao parecer da segurança A1/A2.
- A3 (recomendado) skills/contribuir-com-o-forge/SKILL.md:22 · diz que a cópia nasce só pelo forge-copia, mas a linha 23 ainda manda git clone solto; e bin/forge-copia não existe na sessão de projeto (no PATH é forge-copia). Alinhar as duas linhas.
- A4 (recomendado) skills/trabalho-em-paralelo/SKILL.md:11 · manda só o modo worktree; a ordem do dono de 2026-11-17 07:51 põe o time em clones em ~/.forge-contrib/wt/ enquanto .git/worktrees estiver protegido. Citar o modo clone como padrão e o worktree como alternativa.
- A5 (recomendado) bin/forge-copia:1 · 187 linhas de código e teste (71 + 116), acima da orientação de 150 (M14); o corpo do PR leva teto: excedido, 187 linhas, com o motivo.

## Sondas
- S1 · env -i PATH HOME python3 -m unittest tests.test_ambiente_git (head efe73e17) · espera: OK · obtido: FAILED (failures=1), test_forge_copia.py:28/:44/:56 `self.env` não é montado com sem_manutencao

## Parecer
Reprovado por A1: defeito provado por ferramenta. O guarda estático `tests/test_ambiente_git.py` (origem S-9, `maintenance.lock`) exige que toda chamada a `git` em teste receba o ambiente de `sem_manutencao`; o teste novo monta `{**os.environ, ...}` e o guarda acusa as três chamadas. Correção mínima: `self.env = sem_manutencao({**os.environ, "HOME": ..., ...})` (com o `sys.path` de `tests/`, como os outros módulos), sem mudar a lógica. Na volta, rodar `tests.test_ambiente_git` e `tests.test_forge_copia`.

O resto está correto e simples. `bin/forge-copia` recusa `..` antes de resolver, resolve links com `realpath` (inclusive no último componente), usa `commonpath` (o prefixo parecido não passa), recusa a própria pasta, o destino ocupado, o nome que parece opção e a branch inválida, e passa o destino depois de `--`. Os códigos de saída 0, 1 e 2 batem com o docstring. A biblioteca padrão basta e não há dependência nova. As sondas de segurança não se repetem aqui (parecer `docs/security/v0475-copia-pasta.md`, E3.56).

Mutantes: `bin/forge-mutante --processos 1 tests/mutantes/v0475-copia-pasta.json` no head efe73e17 matou os 10, M1 a M10, um por guarda (`:28`, `:31`, `:32`, `:34`, `:36`, `:54`, `:56`, `:62`, `:63`, `:65`). `--cobertura --base 2fa505d7` deixa sem mutante só `:61` (o ramo do modo, coberto pelos testes de clone e de worktree) e `:70` (o `__main__`). Os testes chamam Python com `-I`. A limpeza do ambiente herdado é justamente o A1.

Sonda de ambiente (A4, não bloqueia): nesta sessão, `forge-copia worktree` dentro de `~/.forge-contrib` criou a worktree (rc=0). Hoje o modo worktree funciona nessa pasta, mas a ordem do dono continua valendo para o texto da skill.

Suíte: sem PR nem CI na branch. A suíte inteira fica para o CI do PR. Aqui só rodaram o teste novo e o guarda que ele toca.
