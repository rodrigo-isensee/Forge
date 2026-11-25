#!/usr/bin/env python3
"""Forge: conformidade dos agentes por papel (ADR 0009, seções 2, 3, 6 e 7; R-CONFORMIDADE).

PreToolUse em Bash, Write, Edit, MultiEdit e NotebookEdit: o papel vem do `agent_type` (política em
`conformidade.json`) e decide quem pode merge, push, PR, escrita em caminho protegido, instalação de pacote e as
flags proibidas (`--no-verify`, `--force`, `core.hooksPath`). Write/Edit decidem pelo `file_path` normalizado
(garantido); o Bash é lido como texto (barrado em regra: um script ou ofuscação passa, e o sandbox é a garantia).
PostToolUse registra a autoria dos pareceres em `.forge/run/autoria.jsonl`.
Falha fechado nas ações críticas (seção 7); `FORGE_GUARDA_ABERTA=1` no ambiente do processo abre a guarda.
Só age em projeto com `.forge/versao`; quem é a sessão vem de `CLAUDE_PROJECT_DIR` (`identificar_sessao`, R-CONTRIB). Na
sessão do Forge, fora de projeto, valem as travas (R-MAIN, R-VERIFY, push para a integração, tag v*) para todo papel.
"""
import collections
import contextlib
import functools
import glob
import hashlib
import json
import os
import re
import signal
import stat
import tempfile
import shlex
import subprocess
import sys
import time
import types
import unicodedata
import urllib.parse
from functools import lru_cache
from pathlib import Path

import parecer
from _comum import (CONTORNO_DA_GRAMATICA, CONTORNO_DO_LANCADOR, CONTORNO_DO_TETO, CORPO_DE_LACO, INTEGRACAO,
                    GIT_GRAVA_ARQUIVO, LancadorDemais, OPACO, TextoAbertoComLeituras, TextoDivididoAberto,
                    LIMITE_MENSAGEM, PLUGIN, PrazoVencido, PROFUNDIDADE, bloquear, comentarios,
                    construcao_nao_modelada, contorno_da_reavaliacao, juntar_continuacoes, formas_que_o_shell_le, conteudos_de_crase, contrib, corpo_so_lido, diretorio_comum,
                    e_clone_do_forge, em_contrib, excede_o_teto, executar, expandir_home, fora_da_gramatica_com_heredoc,
                    expandir_heredoc, fora_da_gramatica_de_leitura, FORMA_DO_HEREDOC, heredocs, motivo_da_reavaliacao,
                    forge_check, git, leituras, mensagem, nome_da_branch, nome_do_caminho, raiz_declarada, raiz_do_projeto, reavaliacao,
                    ANTES_DO_PROGRAMA, palavras_do_texto, sem_atribuicoes, separar_lancadores, SHELLS, subcomando_do_git, TETO_FORA_DA_TABELA, tem_manifesto_do_forge, tirar_heredocs,
                    PrazoVencido)
# Orçamento de `Guarda.bash` por linha; acima de qualquer um, a linha é recusada (fecha na dúvida, como PROFUNDIDADE). O
# custo de uma conferência cresce com o tamanho do texto, então o número delas não basta (A1 do review): conta também os
# caracteres somados e o tempo, com folga para o timeout do hooks.json (10 s), que o Claude Code trata como liberado.
TETO_DE_CONFERENCIAS = 400
TETO_DO_TRECHO = 50  # HOOK-MSG-SEGMENTO: caracteres do comando citado na recusa (C-A6-3)
TOKEN_DO_GITHUB = re.compile(r"(gh[pousr]_|github_pat_)[A-Za-z0-9_]+")  # mascarado no trecho citado
INVISIVEIS = frozenset(("Cc", "Cf", "Zl", "Zp"))  # controle C0/C1 e formato (bidirecionais): fora do trecho (C-A6-1)
TETO_DE_CARACTERES = 150_000  # a conferência de 290 mil caracteres levava 4,2 s (recomendação do review, volta 3)
PRAZO_DA_LINHA_S = 3.0
TETO_DO_CAMINHO = 4096  # VV-3 C-8: bytes do caminho vindo de texto (brief), na escrita pública
NAO_CONFERIDA, NAO_VERIFICAVEL = "não conferida", "não verificável"  # VV-3: quarto campo da recusa da escrita pública

FERRAMENTAS_DE_ARQUIVO = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
# M1 (review de segurança da 0.43.1): as linhas que o `forge-check` grava no `## Histórico` do pedido e que os portões leem como
# prova (`brief selar`, `entrega --pedido`). Write/Edit/MultiEdit que acrescente uma delas no pedido é recusado, de qualquer papel.
# No Bash (M1, [B]): a linha que cita a forma do selo ou da conferência e escreve (redireção, heredoc, tee, sed, interpretador,
# cópia) é recusada, onde quer que grave: o hook não segue `cd` nem variável até o pedido (falha fechada, ADR 0009).
CITA_PORTAO = re.compile(r"brief selado\s+\S*docs/briefs/\S+\s+[0-9a-f]{64}|entrega conferida\s+[0-9a-f]{40}")
ESCRITA_NA_LINHA = re.compile(r">|<<|\b(?:tee|sed|dd|cp|mv|install|python\w*|perl\w*|ruby\w*|node|awk|gawk|nawk|printf)\b")
LINHA_DE_PORTAO = re.compile(r"(?m)^-\s+\d{4}-\d{2}-\d{2} \d{2}:\d{2}: (?:brief selado docs/briefs/\S+ [0-9a-f]{64}|entrega conferida [0-9a-f]{40})")
# TEMPO-FIXTURE-INSTAVEL (E164.1): o par "git/gh ... ação" parte do início da linha (`(?<![^\n])`) e o grupo atômico fixa
# o 1.º programa dela, o que deixa mais linha para a ação: a decisão é a mesma, e a busca fica linear (sem isso, cada
# `gh` repetido varria a linha até o fim; 8 KB de `gh repo ` custavam 0,14 s por busca).
CRITICO = re.compile(
    r"(?<![^\n])(?>[^\n]*?\b(git|gh)\b)[^\n]*\b(merge|push|edit|close|reopen|ready|review|label)\b|"
    r"\bpr\b.*\bcreate\b|--no-verify|hookspath|--force|"
    r"\.claude/|\.claude-plugin|\.githooks|\.forge/|docs/reviews|docs/qa|docs/devops|docs/security|CLAUDE\.md|\.git/|commondir|docs/regras|tests/config\.json|catraca|tests/hooks|conformidade\.json",
    re.I)
# Variáveis definidas antes na linha que os comandos seguintes herdam; as `GIT_*_PATHSPECS` são as opções `--*-pathspecs`.
PATHSPECS_NO_AMBIENTE = {"GIT_GLOB_PATHSPECS": "--glob-pathspecs", "GIT_NOGLOB_PATHSPECS": "--noglob-pathspecs",
                         "GIT_LITERAL_PATHSPECS": "--literal-pathspecs", "GIT_ICASE_PATHSPECS": "--icase-pathspecs"}
VARIAVEIS_DA_LINHA = {"GH_REPO", "GIT_DIR", "GH_CONFIG_DIR", "XDG_CONFIG_HOME", *PATHSPECS_NO_AMBIENTE}
MANIFESTO = ".claude-plugin/"  # no projeto, só a sessão do Forge escreve (R-CONTRIB): a identidade não vem dele
# Nome do interpretador, com versão ou plataforma depois do nome (`perl5.34.0`, `perl5.34-x86_64-linux-gnu`, `ruby3.2`,
# `python3.12`): fonte única para as três conferências (`-e`, edição no lugar, heredoc).
INTERPRETES = re.compile(r"^((python|perl|ruby)([\d][\w.-]*)?|node(js)?|php|deno|bun)$")
PERL_OU_RUBY = re.compile(r"^(perl|ruby)([\d][\w.-]*)?$")
OPCAO_COM_RESTO = set("MmIxCeEfFdDr")  # no grupo de opções curtas do perl/ruby, o resto é o valor delas (`-Mstrict`, `-I lib`)
# Marca da sessão (`.git/forge/projeto-*`): citá-la, ou usar um lançador que o hook não modela, é recusado no projeto. O mesmo
# para a função que grava o resultado do `forge-check pr` em `.git/forge/pr/` (S2 da segurança, E2.142): o caminho sai dela.
CITA_A_MARCA = re.compile(r"\.git/forge|forge/projeto-|gravar_resultado_do_pr")
LANCADORES_RECUSADOS = {"ionice", "chrt", "taskset", "flock", "unshare", "script"}
AWKS = {"awk", "gawk", "mawk", "nawk"}


@functools.lru_cache(maxsize=64)
def interpretado(texto):
    """Algum programa do texto (as palavras, sem aspas nem `\\`) é interpretador."""
    return any(interprete(t) for t in re.split(r"[\s;&|()`<>]+", re.sub(r"[\"'\\]", "", texto)))


def interpreta_o_corpo(dono):
    """Algum programa do dono é interpretador: o todo é a soma das partes (o `\\n` entre elas separa palavras)."""
    return any(map(interpretado, getattr(dono, "partes", None) or (dono,)))


def interprete(programa):
    """Python, Perl, Node, awk...: o corpo de heredoc que eles leem é programa, conferido pelo `checar_texto`."""
    programa = nome_do_caminho(programa)
    return bool(INTERPRETES.match(programa)) or programa in AWKS


def args_do_forge_check(prog, args):
    """A4: os argumentos do `forge-check`, se o comando simples o roda (direto, por caminho, por interpretador ou com o nome
    do programa opaco: `$(command -v forge-check)`, que só conta com a forma do `anotar` ou do `--gravar`); senão None."""
    if prog == "forge-check":
        return args
    if INTERPRETES.match(prog):
        # a opção do interpretador pode levar valor (`-X utf8`, `-W ignore`): procura a palavra, não a 1.ª sem `-`
        achados = [i for i, a in enumerate(args) if nome_do_caminho(a) == "forge-check"]
        return args[achados[0] + 1:] if achados else None
    opaco = re.search(r"[`$]", prog) and ("anotar" in args and any(abreviacao_de(a, ("--tipo",)) for a in args)
                                           or any(abreviacao_de(a, ("--gravar",)) for a in args))
    return args if opaco else None


# Opções longas do sed e do gawk: o getopt_long do GNU aceita qualquer prefixo não ambíguo (`--expr`, `--i`, `--inc`).
SED_LONGAS = ("binary", "debug", "expression", "file", "follow-symlinks", "help", "in-place", "line-length", "null-data",
              "zero-terminated", "posix", "quiet", "regexp-extended", "sandbox", "separate", "silent", "unbuffered", "version")
GAWK_LONGAS = ("assign", "bignum", "characters-as-bytes", "copyright", "debug", "dump-variables", "exec", "field-separator",
               "file", "gen-pot", "help", "include", "lint", "lint-old", "load", "non-decimal-data", "optimize", "posix",
               "pretty-print", "profile", "re-interval", "sandbox", "source", "traditional", "use-lc-numeric", "version")
# comando `w`/`W arquivo` do sed, com ou sem endereço antes (`$w`, `1,2w`), flag `s/a/b/w arquivo` e delimitador do usuário
# (`s|a|b|w arquivo`, `\%a%w arquivo`): qualquer `w`/`W` seguido de palavra; o custo (lado fechado) só aparece se for caminho protegido
SED_ESCREVE = re.compile(r"(?=[wW]\s*(\S+))")  # lookahead: acha também o `w` dentro do nome/arquivo de outro `w` (`s/aw/b/w x`, `;w x`)
ESCRITA_NO_TEXTO = re.compile(  # só escrita de arquivo: `.replace(` de texto e `list.append(` não contam
    r"\.write\w*\(|writeFile|appendFile|unlink|\bos\.(remove|rename|replace)|shutil\.|rmtree|truncate|symlink|"
    r"rmSync|rmdir|copyFile|renameSync|cpSync|chmod|WriteStream|\w*open\w*\([^)]*[\"'][wa][bt+]?[\"']|>|"
    r"file_put_contents|\bf(write|puts)\b|File\.(delete|rename)|FileUtils|inplace|system\(", re.I)
TODOS_OS_ARGUMENTOS = {"rm", "mv", "tee", "truncate", "shred", "unlink", "rmdir", "touch"}
SO_DESTINO = {"cp", "ln", "install", "rsync"}
LEITORES = {"cat", "head", "tail", "less", "more", "bat", "nl", "tac", "source", ".", "grep", "egrep", "rg", "xxd",
            "od", "strings", "base64"}
# F6: leitor sem execução (sem `source`/`.`, pagers e `xxd`, que executam ou gravam por argumento) e as opções que não executam
# programa nem gravam (curtas pela letra; longas pelo nome exato, sem abreviação: `--pre`, `--filter`, `--pager`, `--config`,
# `--output`, `--ext-diff` ficam de fora, e na dúvida recusa)
LEITORES_SEM_EXEC = {"cat", "head", "tail", "nl", "tac", "grep", "egrep", "rg", "od", "strings", "base64"}
GIT_LEITURA = {"log", "show", "diff"}
CURTAS_SEM_EXEC = set("AbBcCdeEfFGHhiIjklLmnNoqrRsStTuvwxX0123456789")
LONGAS_SEM_EXEC = {"recursive", "dereference-recursive", "line-number", "ignore-case", "count", "files-with-matches",
                   "files-without-match", "fixed-strings", "no-filename", "with-filename", "include", "exclude",
                   "exclude-dir", "max-count", "context", "after-context", "before-context", "extended-regexp",
                   "word-regexp", "line-regexp", "invert-match", "only-matching", "quiet", "silent", "no-messages",
                   "regexp", "bytes", "lines", "decode", "stat", "oneline", "name-only", "name-status", "no-color",
                   "no-merges", "graph", "all", "abbrev-commit", "shortstat", "numstat", "cached", "staged", "patch",
                   "summary", "follow", "merges", "reverse", "first-parent", "decorate", "pretty", "format", "author",
                   "since", "until", "no-ext-diff", "no-textconv"}
ARQUIVO_ENV = re.compile(r"^\.env(\.[\w.-]+)?$")
ENV_DE_EXEMPLO = {"example", "sample", "template", "dist"}
PUSH_COM_VALOR = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}
# v0474 (segurança A2): no repositório do Forge a tag `v*` é a versão que todas as máquinas instalam e só nasce do release.yml
# sobre a main. `git tag` só lista ou confere (lista positiva); envio de tag, de qualquer forma, é recusado.
TAG_SO_LEITURA_CURTAS = set("lvn0123456789i")
TAG_SO_LEITURA_LONGAS = {"--list", "--verify", "--contains", "--no-contains", "--points-at", "--merged", "--no-merged", "--sort",
                         "--format", "--column", "--no-column", "--ignore-case", "--omit-empty", "--color"}
TAG_NO_ENVIO = re.compile(r"(\+?(refs/)?tags/|\+?v[\d*?\[])")
TAG_NA_CONFIG = re.compile(r"followtags|refs/tags", re.I)
CRIAR_PR_POR_API = re.compile(r"(^|/)repos/[^/]+/[^/]+/pulls/?$", re.I)  # FILA-22: POST aqui abre PR
CRIAR_PR_NO_GRAPHQL = re.compile(r"createPullRequest", re.I)
API_ADMIN = re.compile(r"/(git/refs|contents/|rulesets|branches/[^/]+/protection|collaborators|actions/(secrets|variables)"
                       r"|hooks|keys|transfer)")
GRAPHQL_PERIGOSO = re.compile(r"mergePullRequest|enablePullRequestAutoMerge|updateRef|createRef|deleteRef|"
                              r"createCommitOnBranch", re.I)
# R-CONTRIB (diretriz 36): a sessão de outro projeto não mexe no Forge (nem o próprio PR), pela API REST e pelo GraphQL.
# Na sessão de projeto, o `gh` no Forge só lê: todo subcomando fora desta lista mexe e é recusado (falha fechado).
GH_SO_LE = {"view", "list", "status", "diff", "checks", "download", "watch", "browse"}
# Opções de `gh pr|issue` que levam valor: o texto delas (corpo, título, rótulo) não é o alvo do comando.
GH_COM_VALOR = {"-R", "--repo", "-b", "--body", "-F", "--body-file", "-t", "--title", "-l", "--add-label",
                "--remove-label", "-a", "--add-assignee", "--remove-assignee", "-m", "--milestone", "-B", "--base",
                "-p", "--add-project", "--remove-project", "-r", "--add-reviewer", "--remove-reviewer", "--subject",
                "-A", "--author-email", "--match-head-commit", "-c", "--comment", "--reason", "--label", "--assignee"}
GH_DO_REPO = {"pr", "issue", "label", "release", "workflow", "run", "repo", "secret", "variable", "cache", "ruleset"}
CONTRIB_GRAPHQL = re.compile(r"createPullRequest|closePullRequest|reopenPullRequest|updatePullRequest|addLabelsToLabelable|"
                             r"removeLabelsFromLabelable|createIssue|createLabel|updateLabel|deleteLabel|updateIssue|closeIssue|"
                             r"markPullRequestReadyForReview|convertPullRequestToDraft|addComment|updateIssueComment|addPullRequestReview|"
                             r"submitPullRequestReview|createRelease|updateRelease", re.I)
SO_SUGERE = 'guarde a melhoria com `forge sugerir --guardar "<texto>"` e avise o usuário: quem implementa é o Forge'
NO_FORGE = "a sessão de projeto não cria branch, não commita, não envia nem abre PR no Forge"
# Opções que criam branch: a curta (também agrupada) e a longa por extenso ou abreviada, com ou sem `=valor`
BRANCH_NOVA = {"switch": (re.compile(r"-[a-zA-Z]*[cCt][a-zA-Z]*"), ("--create", "--force-create", "--orphan", "--track")),
               "checkout": (re.compile(r"-[a-zA-Z]*[bBt][a-zA-Z]*"), ("--orphan", "--track"))}
BRANCH_LISTA = {"-l", "--list", "--show-current", "--contains", "--no-contains", "--merged", "--no-merged", "--points-at"}
BRANCH_COM_VALOR = {"--sort", "--format"}  # valem no modo de lista, mas não o ligam: com nome, o git cria a branch
# Gravam commit ou ref no repositório da pasta (R-CONTRIB: no clone do Forge, vindo de sessão de projeto)
GRAVA_NO_REPO = {"commit", "merge", "cherry-pick", "revert", "am", "rebase", "pull", "commit-tree", "update-ref", "subtree",
                 "reset", "stash", "notes", "symbolic-ref"}  # na dúvida grava: `stash list` e `notes show` também são recusados
# A chave que troca para onde o envio vai: a URL do remoto, a reescrita de URL ou o remoto do envio sem remoto na linha,
# que aceita URL (`git -c <chave>=` e `git config <chave>`; segurança A7)
CHAVE_DO_DESTINO = (r"(remote\..+\.(url|pushurl)|url\..+\.(insteadof|pushinsteadof)|branch\..+\.(remote|pushremote)"
                    r"|remote\.pushdefault)")
CONFIG_DO_DESTINO = re.compile(CHAVE_DO_DESTINO + "=.*", re.I | re.S)
SUBTREE_COM_VALOR = {"-P", "--prefix", "-m", "--message", "-b", "--branch", "--onto", "--annotate"}
ROTULO_PROTEGIDO = "afrouxa-regra"  # R-CONTRIB: só a conta do dono do Forge o aplica
ROTULO_COM_VALOR = ("--add-label", "--label", "-l", "--remove-label")  # a opção que acaba a linha leva o valor do xargs
# Mutações do GraphQL que aplicam, criam ou renomeiam rótulo: o ID não traz o nome, então toda ocorrência conta
GRAPHQL_DE_ROTULO = re.compile(r"addLabelsToLabelable|labelIds|createLabel|updateLabel", re.I)
CITA_ROTULO = re.compile(rf"{ROTULO_PROTEGIDO}|{GRAPHQL_DE_ROTULO.pattern}", re.I)  # falha fechado pelo texto
TIMEOUT_DA_CONTA = 5  # s; abaixo do timeout do hook em hooks.json (10 s), senão o Claude Code o mata e o comando segue
# FURO-HOOK-A, A3: a configuração que troca a estratégia ou o resultado do merge (R-REVIEW): a chave vale em `git config` e em `-c`
CONFIG_DO_MERGE = re.compile(r"^(branch\..+\.mergeoptions|pull\.(twohead|octopus)|merge\..+\.driver)(=|$)", re.I)
CONFIG_PROTEGIDA = re.compile(r"^(user\.|core\.|commit\.gpgsign$|include|alias\.|help\.autocorrect)|" + CONFIG_DO_MERGE.pattern[1:], re.I)
MERGE_OPCOES_QUE_MUDAM_O_RESULTADO = ("--strategy", "--strategy-option", "--squash", "--no-commit")  # e `-s`, `-X`
CONFIG_LEITURA = {"--get", "--get-all", "--get-regexp", "--get-urlmatch", "--list", "-l", "--show-origin", "--show-scope",
                  "--show-names", "--name-only", "--help", "-h"}
CONFIG_ESCRITA = {"--unset", "--unset-all", "--add", "--replace-all", "--rename-section", "--remove-section", "-e",
                  "--edit"}
CONFIG_ESCOPO = {"--local", "--global", "--system", "--worktree"}  # escolhem o arquivo, não são valor
CONFIG_COM_VALOR = {"-f", "--file", "--blob", "--type", "--default", "--comment", "--value"}
# IMPL-FURO-HOOK-N, N2 (L20b): objeto de troca (`refs/replace/*`) e enxerto fazem o `git show <ref>:<parecer>` do
# forge-check ler outro conteúdo, sem diff nem cópia suja. As variáveis mudam onde o git os procura.
AMBIENTE_DE_TROCA = re.compile(r"^(GIT_REPLACE_REF_BASE|GIT_GRAFT_FILE|GIT_ALTERNATE_OBJECT_DIRECTORIES"
                               r"|GIT_OBJECT_DIRECTORY)$")
CITA_TROCA = re.compile(r"refs/replace|replace-?refs|grafts", re.I)
# Review da 0.43.5: configuração dada na linha que o hook não avalia (alias troca o subcomando; GIT_CONFIG_* e
# --config-env escondem o -c) recusa para todo papel; o refspec de remote.*.fetch|push no -c vale como o da linha.
# IMPL-FURO-HOOK-N, N1 (C-N1-2, 0.45.1): o git roda o alias da configuração (repositório, ~/.gitconfig) no lugar do
# subcomando que não é dele, e o hook lia o nome do alias. Os comandos internos do git (`git --list-cmds=builtins`) não
# se trocam por alias (o git ignora o alias que esconde um deles); o resto é lido na configuração e a expansão passa
# pelas mesmas regras. `!` (shell) e o alias que mescla recusam: o `parecer` só lê o merge escrito por extenso.
# AR-TRAVA-UMA-SINTAXE (0.45.1): o git aceita a opção longa abreviada sem ambiguidade (`--no-verif`, `--forc`, `--mirr`,
# `--conti`), e a trava que compara o nome inteiro deixava a abreviação passar. A opção que uma trava confere é lida por
# extenso antes das regras; a abreviação de mais de uma (ambígua, que o git recusa) vira a primeira, e recusa também. A
# ordem importa: a inteira vem antes das que ela abrevia (`--force` antes de `--force-with-lease`).
# As opções do merge que mudam o resultado (`--strat`, `--squa`) já se leem abreviadas em opcao_de_merge_que_muda_o_resultado.
LONGAS_VIGIADAS = ("--no-verify", "--force", "--force-with-lease", "--force-if-includes", "--mirror", "--continue",
                   "--delete", "--hard", "--amend", "--all")
COMANDOS_DO_GIT = frozenset("""add am annotate apply archive bisect blame branch bugreport bundle cat-file check-attr
check-ignore check-mailmap check-ref-format checkout checkout-index cherry cherry-pick clean clone column commit commit-graph
commit-tree config count-objects credential describe diagnose diff diff-files diff-index diff-tree difftool fast-export
fast-import fetch fetch-pack fmt-merge-msg for-each-ref for-each-repo format-patch fsck gc grep hash-object help hook
index-pack init interpret-trailers log ls-files ls-remote ls-tree mailinfo mailsplit maintenance merge merge-base
merge-file merge-index merge-tree mktag mktree multi-pack-index mv name-rev notes pack-objects pack-refs patch-id prune
pull push range-diff read-tree rebase receive-pack reflog remote repack replace rerere reset restore rev-list rev-parse
revert rm send-pack shortlog show show-branch show-index show-ref sparse-checkout stash status stripspace submodule
switch symbolic-ref tag unpack-objects update-index update-ref upload-pack var verify-commit verify-pack verify-tag
version whatchanged worktree write-tree""".split())
ALIAS_QUE_MESCLA = {"merge", "pull"}
PROFUNDIDADE_DO_ALIAS = 8
CONFIG_NO_AMBIENTE = re.compile(r"^GIT_CONFIG_(COUNT|KEY_\d+|VALUE_\d+|PARAMETERS)$")
REFSPEC_NA_CONFIG = re.compile(r"remote\..+\.(fetch|push)", re.I)
# IMPL-FURO-HOOK-N, N5 (L22, C-22-1): na branch de integração a única entrada é o `git merge` com parecer; o que grava
# commit, move a branch ou conclui um merge fora dele recusa para todo papel (o conflito se resolve na branch de trabalho).
RESET_MODOS = {"--soft", "--mixed", "--hard", "--keep", "--merge"}
NA_INTEGRACAO_RECUSADOS = {"commit", "cherry-pick", "revert", "am", "commit-tree", "fast-import"}
SAIDAS_DA_OPERACAO = {"--abort", "--quit", "--skip"}  # desfazem a operação em curso: livres
NOTAS_DE_LEITURA = {None, "list", "show", "get-ref"}
RESET_COM_VALOR = {"--pathspec-from-file"}
FETCH_COM_VALOR = {"--depth", "--deepen", "--shallow-since", "--shallow-exclude", "--negotiation-tip", "-j", "--jobs",
                   "--upload-pack", "--refmap", "-o", "--server-option", "--filter", "--recurse-submodules-default",
                   "--submodule-prefix"}
CONTORNO_DA_INTEGRACAO = ("faça o commit na branch de trabalho e mescle com `git merge` (parecer); para atualizar a "
                          "integração, `git merge --ff-only origin/<branch>`")
# 0.45.3: parecer gravado pelo Bash (`>`, `>>`, `tee`, `cp`, `sed -i`...) não tem a autoria que o `forge-check pr` exige, e a
# volta caía no PR; agora recusa na hora da escrita, para todo papel, com a forma certa. O `git` (checkout de parecer trazido) e
# a remoção não são escrita de parecer.
PASTAS_DE_PARECER = ("reviews", "qa", "security", "devops", "ux")
COMO_GRAVAR_PARECER = ("regrave com a ferramenta Write (o esqueleto sai de `forge-check parecer novo`); "
                       "parecer gravado pelo Bash fica sem autoria")
# 0.45.3 (N1 resto): o alias do gh gravado antes da trava (`aliases:` do config.yml) troca o comando que o hook lê. O gh só
# expande o nome que não é comando dele; a expansão (com `$1`... e o resto da linha no fim, como o gh faz) passa pelas mesmas
# regras. O hook lê o config.yml de GH_CONFIG_DIR (ou XDG_CONFIG_HOME/gh, ou ~/.config/gh) e também ~/.claude/gh; o bloco que
# ele não lê (valor em bloco, mapa em linha) recusa o nome que não é comando do gh (na dúvida, recusa).
COMANDOS_DO_GH = frozenset("""accessibility actions agent-task alias api attestation auth browse cache codespace completion config
copilot discussion environment exit-codes extension formatting gist gpg-key help issue label licenses mintty org pr preview
project reference release repo ruleset run search secret skill ssh-key status telemetry variable version workflow""".split())
CHAVE_DE_ALIAS = re.compile(r"^(\s+)([^\s:#'\"][^:#]*?|'[^']*'|\"[^\"]*\"):(?:\s+(.*?))?\s*$")


class AliasIlegivel(ValueError):
    """O bloco `aliases:` do config.yml do gh tem forma que o hook não lê."""


def valor_do_yaml(bruto):
    """O texto de um valor escalar simples do YAML (sem aspas, entre aspas simples ou duplas); o resto é ilegível."""
    if bruto.startswith("'"):
        if not bruto.endswith("'") or len(bruto) < 2:
            raise AliasIlegivel(bruto)
        return bruto[1:-1].replace("''", "'")
    if bruto.startswith('"'):
        try:
            return json.loads(bruto)  # começa com `"`: só sai texto ou erro
        except ValueError:
            raise AliasIlegivel(bruto) from None
    if not bruto or bruto[0] in "|>{[&*!%@`":
        raise AliasIlegivel(bruto)
    return re.sub(r"\s+#.*$", "", bruto)


def aliases_do_gh(texto):
    """{nome: expansão} do bloco `aliases:` de topo do config.yml do gh; AliasIlegivel se ele tem forma que o hook não lê."""
    aliases, dentro = {}, False
    for linha in texto.splitlines():
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        if not linha[0].isspace():
            topo = linha.split("#", 1)[0].rstrip()
            dentro = topo == "aliases:"
            if not dentro and topo.startswith("aliases:") and topo.split(":", 1)[1].strip() not in ("{}", ""):
                raise AliasIlegivel(topo)
            continue
        if not dentro:
            continue
        achado = CHAVE_DE_ALIAS.match(linha)
        if not achado or achado.group(3) is None:
            raise AliasIlegivel(linha)
        aliases[valor_do_yaml(achado.group(2).strip())] = valor_do_yaml(achado.group(3))
    return aliases


def expandir_alias_do_gh(expansao, resto):
    """As palavras que o gh roda: `$N` trocado pelo N-ésimo argumento (e o resto sem `$` vai no fim), como o gh."""
    if "$" in expansao:
        for i, a in enumerate(resto, 1):
            expansao = expansao.replace(f"${i}", a)
        resto = []
    if re.search(r"\$\d", expansao):
        return None  # o gh recusa: argumento que falta
    try:
        return shlex.split(expansao) + list(resto)
    except ValueError:
        return None


# 0.45.3 (decisão do dono): `git push --all` e `--mirror` (também abreviados) recusam para todo papel.
UMA_BRANCH_POR_VEZ = "envie uma branch por vez (R-FLUXO)"
REFS_DE_TROCA = {"fetch", "pull", "push", "send-pack", "update-ref", "symbolic-ref"}  # gravam refs pelo argumento

# Travas para atos perigosos (arquitetura do primeiro uso, 2.2 e 2.5). Valem para todo papel e todo perfil; no perfil
# `iniciante` a recusa e a confirmação trazem a consequência em linguagem simples. Mensagem de uma linha (200 caracteres).
REPO_APAGAR = re.compile(r"^/?repos/[^/]+/[^/]+/?$")
GRAPHQL_APAGAR = re.compile(r"mutation[^}]*deleteRepository", re.I)
VISIBILIDADE_PUBLICA = re.compile(r"\bprivate[\"']?\s*[=:]\s*[\"']?false\b|\bvisibility[\"']?\s*[=:]\s*[\"']?public\b", re.I)
# CONFORMIDADE-REPO-CREATE-PUBLICO (v0478 E141.2; A1 e A2 de docs/security/v0480-repo-publico-diag.md): criar repositório
# só com a visibilidade privada explícita (o padrão da API é público; sem TTY o gh exige uma), pelo `gh repo create` e
# pela API. Valor que o hook não lê (`$`, crase, arquivo ausente) no endpoint do repositório falha fechado. E141.7: a
# decisão é pelo nome do campo (`-f`/`-F` separado, colado ou com `=`; chave do topo do `--input`), não pelo texto todo.
REPO_CRIAR = {"create", "new"}  # `gh repo new` é alias de `gh repo create`
CAMPO_COLADO = re.compile(r"(?:-[fF]=?|--(?:raw-)?field=)(.+)", re.S)  # `-Fk=v`, `-F=k=v`, `--field=k=v`
CAMPOS_DA_API = {"-f", "-F", "--field", "--raw-field"}
PRIVADO_REST = {"private": {"true"}, "visibility": {"private", "internal"}}  # o valor privado de cada nome
CORPO_ILEGIVEL = [("", None)]  # o `--input` que o hook não lê (sentinela: comparado por identidade)
API_SEGMENTO_ESTRANHO = re.compile(r"(^|/)\.{0,2}(/|$)")  # `user//repos`, `user/./repos`: o servidor pode normalizar
CHAVES = parecer.CHAVES  # E168.9 (A5): a palavra que pode ter expansão de chaves (`expansao_por_palavra`); fonte única
GRAPHQL_ILEGIVEL = ("R-CONFORMIDADE", "gh api graphql com consulta que o hook não lê (variável, expansão do shell, "
                    "arquivo ou entrada padrão)", "escreva a consulta literal entre aspas simples "
                    "(gh api graphql -f query='...') e cada valor em -F \"nome=$valor\", com aspas")


def expansao_por_palavra(linha):
    """GRAPHQL-CONSULTA-EM-VARIAVEL (E168.1): {palavra sem aspas, como o `shlex` a devolve: a maior expansão vista nela}.
    0: `$` e crase literais (aspas simples, barra; entre aspas duplas, `\\$` fica como o `shlex` o lê); 1: expansão
    entre aspas duplas (o valor fica numa palavra só); 2: fora de aspas (o bash divide o valor em palavras). A palavra
    que esta leitura não reproduz fica fora, e quem consulta a toma por 2."""
    saida, texto, nivel, aspas, letras = {}, [], 0, None, iter(linha)
    chave, anterior = False, ""  # E168.9 (A5): `{` fora de aspas na palavra; a letra anterior fora de aspas

    def juntar():  # a palavra vazia (`""`) entra e não pesa: só a palavra com `$` ou crase é consultada
        palavra = "".join(texto)
        saida[palavra] = max(saida.get(palavra, 0), nivel)

    for c in letras:
        fora = aspas is None
        if aspas == "'":
            if c == "'":
                aspas = None
            else:
                texto.append(c)
        elif c == "\\":  # o escapado é literal; entre aspas duplas o `shlex` só tira a barra antes de `"` e `\\`
            seguinte = next(letras, "")
            texto.append(("\\" if aspas and seguinte not in '"\\' else "") + seguinte)
        elif c in "$`" or fora and (CURINGA.match(c) or chave and (c == "," or c == "." == anterior)):
            # E168.5 (A3): o curinga fora de aspas o bash troca por nomes; E168.9 (A5): a chave com `,` ou `..` fora de
            # aspas (`{'…mergePull','-Hx:'}'Request…'`), por várias palavras remontadas
            nivel = max(nivel, 1 if aspas else 2)
            texto.append(c)
        elif c == aspas:
            aspas = None
        elif aspas or not (c in "'\";&|" or c.isspace()):
            texto.append(c)
        elif c in "'\"":
            aspas = c
        else:
            juntar()
            texto, nivel, chave = [], 0, False
        chave, anterior = (chave or c == "{", c) if fora else (chave, "")
    juntar()
    return saida


CRIAR_COM_VALOR = {"-d", "--description", "-h", "--homepage", "-t", "--team", "-g", "--gitignore", "-l", "--license", "-p",
                   "--template", "-r", "--remote", "-s", "--source"}  # as opções de `gh repo create` que levam valor
API_CRIA_REPO = re.compile(r"user/repos|orgs/[^/]+/repos|repos/[^/]+/[^/]+/generate", re.I)  # endpoint normalizado
API_DO_REPO = re.compile(r"repos/[^/]+/[^/]+", re.I)
GRAPHQL_DO_REPO = re.compile(r"\b(createRepository|cloneTemplateRepository|updateRepository)\b")
GRAPHQL_CRIA_REPO = re.compile(r"\b(createRepository|cloneTemplateRepository)\b")
# E141.11 (A1 do review, A7 da segurança): strings e comentários pela especificação; no bloco `"""` só `\"""` escapa, e
# o comentário fecha no LF ou no CR. CR, BOM e outro controle na consulta falham fechado, sem modelar mais léxico.
GRAPHQL_SEM_TEXTO = re.compile(r'"""(?:\\"""|\\(?!""")|[^"\\]|"(?!""))*"""|"(?:\\.|[^"\\\n])*(?P<fecha>"?)|#[^\r\n]*')
GRAPHQL_CONTROLE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f\ufeff]")  # todo controle, fora o TAB e o LF; e o BOM
GRAPHQL_VISIBILIDADE = re.compile(r"\bvisibility\s*:\s*(\$?\w*)")  # com a vírgula já trocada por espaço
# REPO-PUBLICO-REDESENHO (v0478 E148.1; A1 do review e A9 da segurança de v0480-repo-publico-fix): as formas do gh que
# decidem a visibilidade marcam só o prazo vencido e o erro interno (`MarcadorDaPolitica.marca`), não o `CRITICO` das
# recusas de construção: a leitura do gh com `$`, crase ou `\` + quebra segue livre. Cada termo é uma busca própria na
# linha (a continuação já vem juntada numa das formas), então o custo é linear no texto.
GH_DA_VISIBILIDADE = [[re.compile(p, re.I) for p in termos] for termos in (
    (r"\bgh\b", r"\brepo\b", r"\b(?:create|new)\b"),  # gh repo create, gh repo new
    (r"\bgh\b", r"\bapi\b", r"graphql|\brepos\b"))]  # user/repos, orgs/<o>/repos, .../generate, repos/<o>/<r>, graphql


def visibilidade_do_gh(texto):
    """Alguma linha do texto tem todos os termos de uma das formas de `GH_DA_VISIBILIDADE`?"""
    return any(all(t.search(linha) for t in termos) for linha in texto.split("\n") for termos in GH_DA_VISIBILIDADE)


CAMINHOS_NO_GIT = {"rm", "mv", "checkout", "restore"}  # subcomandos que mexem em arquivos do projeto
# CONFORMIDADE-ESCRITA-NO-INDICE (v0478 E63.1; S1-S4 de docs/security/v0479-pv-a1-adr.md): gravam no índice o caminho
# nomeado, com conteúdo que nunca esteve na árvore (`-c filter.*.clean`, `--chmod`, `--cacheinfo`).
INDICE_NO_GIT = {"add", "stage", "update-index", "reset"}  # E63.5: `stage` é o `add` (A2); o `reset` com caminho (A7)
INDICE_PELA_ENTRADA = ("--pathspec-from-file", "--stdin", "--index-info")  # a lista de caminhos que o hook não lê
PASTAS_PROTEGIDAS = {".forge", ".githooks", ".claude"}
# S8: a prova da suíte (`.verde`, `.dirigida`, o `.novo` do `mv`) só o pre-push grava, fora deste hook; todo papel e pasta. Limites
# aceitos (o hook protege contra engano; o CI é o portão): nome inteiro numa variável, script em arquivo, `curl -o`, `tar -x`.
# N4/P3 (versao-045 E5a): também o carimbo K6 de scripts/suite-paralela.py e o temporário do `os.replace` (`.<pid>`).
MARCA_DA_SUITE = re.compile(r"forge-suite-[^/]*\.(verde|dirigida)(\.novo)?|forge-suite-verde(\.\d{1,10})?")
PROVA_DA_SUITE = ("R-VERIFY", "a prova da suíte só é gravada pelo pre-push e pela suíte (scripts/suite-paralela.py)",
                  "rode o push ou .githooks/pre-push --suite")
# PROFUNDIDADE-BASH-C (v0457 E17.1): acima do teto de aninhamento o hook não lê a linha; recusa em toda sessão e pasta,
# também fora de projeto (a `GuardaDaProva` a deixa passar), e não só quando ela aponta para o Forge.
PROFUNDIDADE_EXCEDIDA = ("R-CONFORMIDADE", f"comando aninhado (bash -c, eval, $(, crase, heredoc) em mais de {PROFUNDIDADE} "
                         "níveis: o hook não o lê", f"rode o comando direto, com no máximo {PROFUNDIDADE} níveis aninhados")
# CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE (v0478 E51.1): na sessão do Forge com a pasta corrente fora de projeto (o
# clone, `wt/*`), as travas valem para todo papel na `GuardaDaProva`: R-MAIN, R-VERIFY, o push direto para a integração
# e a tag v* (`trava_da_sessao_do_forge`). O resto da linha segue livre (ADR 0009, seção 6).
# E51.6: a marca vai no `barrar` (`trava=`), não no texto da recusa. `TRAVA`: vale sempre (o push direto para a integração,
# a tag v*; R-MAIN e R-VERIFY valem pelo ID). `TRAVA_OPACA`: o alvo opaco com ação crítica (variável, reavaliação, heredoc
# fora da gramática), que pode esconder uma trava (`F=--force; git push $F`, `B=develop; git push origin $B`); vale quando
# um comando da linha pode ser uma trava (`toca_uma_trava`); a que só cita um caminho crítico segue livre. `TRAVA_NO_TETO`:
# a linha acima do teto, que o hook não lê, pelo texto (`GIT_NO_TEXTO`).
TAG_E_VERSAO = "a tag v* é a versão que todos os projetos instalam"
PUSH_DIRETO = "push direto para"
TRAVA, TRAVA_OPACA, TRAVA_NO_TETO = "trava", "trava-opaca", "trava-no-teto"
# Lista positiva do que não chega a uma trava (AR-15): o subcomando do git e as duas primeiras palavras do gh que só leem
# ou mexem na árvore; o resto (alias, `send-pack`, `am`, `fetch` para uma branch, `release create`) é trava.
GIT_FORA_DAS_TRAVAS = {"add", "blame", "cat-file", "describe", "diff", "grep", "log", "ls-files", "ls-remote", "ls-tree",
                       "restore", "rev-list", "rev-parse", "shortlog", "show", "stash", "status", "worktree"}
GH_FORA_DAS_TRAVAS = {"pr view", "pr list", "pr checks", "pr diff", "pr status", "pr edit", "run view", "run list",
                      "issue view", "issue list", "repo view", "release view", "release list"}
OPACA_NA_PALAVRA = re.compile(r"[$`]")  # a palavra que o bash expande: o hook não sabe o valor
GIT_NO_TEXTO = re.compile(r"(?<![\w./-])(?:git|gh)(?=\s)")  # o git ou o gh como palavra, não `.git/` nem `x-git`
COLCHETE_DE_DIGITO = re.compile(r"\[[0-9-]+\]")  # o bash e o glob do Python o leem igual: sem caixa, negação nem classe
CURINGA = re.compile(r"[*?\[]")  # o bash expande no alvo antes de gravar (A1 e A2 da segurança g1 da 0.45)
MAGIA_DE_PATHSPEC = re.compile(r"^:(\(.*?\)|[/!^]*)")  # `:(top)`, `:(literal)`, `:/`, `:!`...
GLOB_DE_PATHSPEC = re.compile(r"[*?\[\\]")
CHECKOUT_COM_VALOR = {"-b", "-B", "--orphan"}

VARIAVEL = re.compile(r"\$\{?(\w+)\}?|\$\(|`")
# E20.6 (A2 da segurança, v046): nomes do diretório do git. Depois de `$(…)` ou de variável, o resto que começa por um
# deles pode estar no `.git` (`$(git rev-parse --git-common-dir)/forge/x`, `d=<raiz>/.git; cp x $d/config`).
NOMES_DO_GIT = frozenset({"forge", "config", "hooks", "HEAD", "index", "refs", "objects", "logs", "info", "worktrees",
                          "commondir", "gitdir", "packed-refs", "modules"})
SO_VARIAVEL = re.compile(r"\$\{[^}]*\}|\$\w+|\$[@*]|`")  # `${d%/}` (A2 da E20.8): a variável vai até o `}` que a fecha
# CONFORMIDADE-SET-POSICIONAL (A18): `$@` e `$*` (o que `set --` grava) são opacos como `$1`; `$$`, `$!`, `$#`, `$?` e
# `$-` seguem literais: dígitos e letras de opção nunca completam o nome `.git`
# Volta 1 da E20.6 (A1 e A3 da segurança E20.8, v046): `git rev-parse --git-dir` (e `--git-common-dir`, `--absolute-git-dir`,
# `--git-path <x>`) em `$(…)` ou crase tem valor conhecido, o `.git` da raiz: a linha troca a substituição por esta
# variável, que `expandir` resolve (também na variável atribuída a ela), e as regras `.git/…` decidem como no literal.
DIR_DO_GIT = "FORGE_DIR_DO_GIT"
# Volta 2 (review E20.12 A3, segurança E20.13 A1): o corpo da substituição é lido por palavras (shlex), não pela grafia:
# qualquer forma de chamar o git (`git -C <pasta>`, `-c a=b`, `\git`, `/usr/bin/git`), opções antes da do diretório
# (`-q`, `--path-format=x`), argumento entre aspas e redirecionamento dentro (`2>/dev/null`). Falha fechada: `-C` de outro
# repositório também vale como o `.git` da raiz, e o argumento do `--git-path` que não é caminho simples, como o próprio `.git`.
REV_PARSE_DO_GIT = re.compile(r"\$\((?P<sub>[^()`]*)\)|`(?P<crase>[^`]*)`")
OPCOES_DO_DIR_DO_GIT = frozenset({"--git-dir", "--git-common-dir", "--absolute-git-dir"})
CAMINHO_SIMPLES = re.compile(r"[\w./-]+")
VARIAVEL_INTEIRA = re.compile(r"\$\{(\w+)\}|\$(\w+)")  # sem operador: `${d%/}` não é o valor de `d`
SUBSTITUICAO = re.compile(r"[$<>]\(")
SIMPLES = {
    "apagar": "Apagar o projeto no GitHub perde todo o trabalho, sem volta. Se quiser mesmo, faça pelo site do GitHub.",
    "publico": "Deixar o projeto público faz qualquer pessoa na internet ver todo o código e o histórico. "
               "Se quiser mesmo, mude pelo site do GitHub.",
    "forca": "Enviar à força sobrescreve o que já está no GitHub e pode perder versões. Salve uma versão nova em vez disso.",
    "main": "A linha principal (main) é sua: só você junta nela, pelo pedido de revisão no GitHub. Peça ao Jarvis para abri-lo.",
    "historico": "Isso reescreve o histórico e as outras cópias deixam de bater. Para voltar atrás, use o 'forge desfazer'.",
    "integracao": "Isso apagaria uma linha de trabalho central do projeto, que ninguém mais conseguiria usar. Peça ao Jarvis.",
    "perfil": "O seu perfil de uso só muda por você, não por mim. Se quiser mudar, peça ao Jarvis como fazer.",
    "atualizar": "Atualizar ou voltar a versão do Forge é com você, no terminal: rode 'forge atualizar' (ou 'forge voltar-versao'). "
                 "Posso explicar o que muda.",
    "sugerir": "Enviar a sugestão ao Forge não é comigo: quem envia a sugestão é você, no seu terminal: `forge sugerir --fila`. "
                "Eu só guardo o texto, com `forge sugerir --guardar`.",
    "instalacao": "Isso mexe na instalação do Forge, que fica protegida para o projeto não quebrar. "
                  "Posso registrar o pedido como sugestão ao Forge.",
}
# F5: quem atualiza o Forge (ou volta de versão) é a pessoa, no terminal; o agente só oferece e explica.
# F6: o mesmo vale para enviar sugestão ao Forge (`forge sugerir`, `forge-sugerir`): só `--guardar` é do agente. A variável de
# ambiente que o script confere some com `env -i`; por isso a defesa principal é este hook.
GUARDAR_EXATO = re.compile(r"(?:forge sugerir|forge-sugerir|bin/forge-sugerir) --guardar (\"[^\"$`\\!]*\"|'[^']*')", re.S)


def sem_caixa(padrao):
    """O `nocaseglob` do bash no glob do Python: cada letra do padrão (o colchete que sobra só tem dígito) vira `[xX]`."""
    return re.sub(r"[^\W\d_]", lambda m: f"[{m[0].lower()}{m[0].upper()}]", padrao)


def valor_do_rev_parse(corpo):
    """O caminho dentro do `.git` que o corpo de `$(…)` ou da crase devolve ("" é o próprio `.git`), ou None se o corpo não
    é `rev-parse` com uma das opções do diretório do git. Aspas sem par: as palavras sem as aspas."""
    try:
        palavras = shlex.split(corpo)
    except ValueError:
        palavras = re.findall(r"[^\s'\"]+", corpo)
    depois = palavras[palavras.index("rev-parse") + 1:] if "rev-parse" in palavras else []
    for i, palavra in enumerate(depois):
        if palavra in OPCOES_DO_DIR_DO_GIT:
            return ""
        if palavra == "--git-path":  # `--git-path=x` o git não lê como opção
            caminho = next(iter(depois[i + 1:]), "")
            return caminho if CAMINHO_SIMPLES.fullmatch(caminho) else ""
    return None


def trocar_rev_parse(m):
    """`$(…)` ou crase de `rev-parse` do diretório do git vira `${DIR_DO_GIT}/<caminho>`; as outras voltam iguais."""
    valor = valor_do_rev_parse(m["sub"] or m["crase"] or "")
    return m[0] if valor is None else "${%s}/%s" % (DIR_DO_GIT, valor)


# A10 (E1.139, v047): só o corpo que é um comando simples dá à origem de link a liberação do #512. Com `;`, `&&`, `|`, `&`
# ou parênteses (`$(git rev-parse --git-dir >/dev/null; echo .git/hooks)`), o valor que o hook lê não é o do bash.
SEPARADOR_DE_COMANDO = re.compile(r"[;|()`]|&&|(?<![>&])&(?![>&])")


def rev_parse_de_varios_comandos(texto):
    """True se algum corpo de `rev-parse` do diretório do git no texto tem mais de um comando."""
    return any(valor_do_rev_parse(c) is not None and SEPARADOR_DE_COMANDO.search(c)
               for m in REV_PARSE_DO_GIT.finditer(texto) for c in [m["sub"] or m["crase"] or ""])


# A9 (E1.139, v047): destino opaco sem resto (`cp config "$(echo .git)"`), pelo plano de segurança da E1.133. U1: o texto
# que produz o valor cita o diretório do git; U2: o hook não lê esse texto; U3: origem com nome do git (C18 da v2) e
# corpo fora da lista positiva. Listas fechadas e positivas (AR-3).
CITA_DIR_DO_GIT = re.compile(r"(?<![\w.])\.git(?![\w.-])|--(?:git-dir|git-common-dir|absolute-git-dir|git-path)(?![\w-])"
                             rf"|GIT_DIR|{DIR_DO_GIT}")
CORPO_ILEGIVEL = re.compile(r"(?<![\w-])(?:eval|bash|sh|zsh|dash|ksh)(?![\w-])|\$'|\\")
PALAVRA_COM_CURINGA = re.compile(r"[^\s/\"'`()=;|&{}:]*[*?\[][^\s/\"'`()=;|&{}:]*")
COLCHETE = re.compile(r"\[!?\]?[^\]]*\]")  # o colchete do bash casa um caractere: vira `?` (sobra, nunca falta)
NOMES_DA_C18 = frozenset("""config config.worktree HEAD ORIG_HEAD FETCH_HEAD MERGE_HEAD index packed-refs commondir gitdir
    hooks forge refs objects info logs modules worktrees shallow applypatch-msg pre-applypatch post-applypatch pre-commit
    pre-merge-commit prepare-commit-msg commit-msg post-commit pre-rebase post-checkout post-merge pre-push pre-receive
    update proc-receive post-receive post-update reference-transaction push-to-checkout pre-auto-gc post-rewrite
    sendemail-validate fsmonitor-watchman p4-changelist p4-prepare-changelist p4-post-changelist p4-pre-submit
    post-index-change""".split())
CORPO_POSITIVO = re.compile(r"mktemp(?:\s+(?:-[duqt]+|-p\s+[\w./-]+|--tmpdir(?:=[\w./-]+)?|[\w.-]*XXX[\w.-]*))*"
                            r"|date(?:\s+[-+%\w:.,]+)*|pwd(?:\s+-[LP])?|git\s+rev-parse\s+--show-toplevel"
                            r"|git\s+rev-parse\s+(?:--short(?:=\d+)?|--abbrev-ref)(?:\s+[\w./@^~-]+)?|true|false|:")
UNIDADE_OPACA = re.compile(r"\$\((?P<sub>.*)\)|`(?P<crase>[^`]*)`|\$\{?(?P<nome>\w+)\}?", re.S)
TETO_DE_OPACOS = 64  # C21 da v2: acima disso, na mesma linha, o hook não lê


def corpos_de_substituicao(texto):
    """O corpo de cada `$(…)` de fora (com o de dentro) e de cada crase, por profundidade de parênteses e sem olhar
    aspas: sobra texto, nunca falta (a sobra só recusa mais)."""
    corpos, i = [m[1] for m in re.finditer(r"`([^`]*)`", texto)], texto.find("$(")
    while i >= 0:
        fundo, j = 1, i + 2
        while j < len(texto) and fundo:
            fundo += {"(": 1, ")": -1}.get(texto[j], 0)
            j += 1
        corpos.append(texto[i + 2:j - (not fundo)])
        i = texto.find("$(", j)
    return corpos


def valor_atribuido(texto, inicio):
    """O valor da atribuição que começa em `inicio`, até o espaço ou separador fora de aspas e de parênteses."""
    fundo, aspa, j = 0, None, inicio
    while j < len(texto) and (aspa or fundo or not (texto[j].isspace() or texto[j] in ";&|)")):
        c = texto[j]
        if aspa:
            aspa = None if c == aspa else aspa
        elif c in "\"'":
            aspa = c
        else:
            fundo += {"(": 1, ")": -1}.get(c, 0)
        j += 1
    return texto[inicio:j]


def glob_casa(padrao, nome):
    """O curinga do bash com `nocaseglob`, cada colchete lido como `?` (sobre-aproxima)."""
    regex = "".join(".*" if c == "*" else "." if c == "?" else re.escape(c) for c in COLCHETE.sub("?", padrao))
    return re.fullmatch(regex, nome, re.I) is not None


def cita_o_dir_do_git(texto):
    """U1: `.git` como palavra ou componente, opção do diretório do git, `GIT_DIR` ou curinga que casa `.git`."""
    return bool(CITA_DIR_DO_GIT.search(texto)) or any(glob_casa(p, ".git") for p in PALAVRA_COM_CURINGA.findall(texto))


REF_DE_VARIAVEL = re.compile(r"\$(?:\{[^}]*\}|\w+)")


def palavra_juntada(texto):
    """D2b (E1.175, v047): o texto como o bash junta a palavra: sem aspas (`.g'i't`, `.g""it`) e com cada variável colada
    a outro texto lida como `*` (`${a}it`, `.gi${z}t`, `$a$b`), que `cita_o_dir_do_git` casa pelo curinga. A variável
    sozinha no componente segue como está: o valor dela vem do `nome=` da linha (`textos_do_valor`)."""
    sem_aspas = re.sub(r"[\"']", "", texto)
    return re.sub(r"[^\s/;|&()`]+", lambda m: m[0] if REF_DE_VARIAVEL.fullmatch(m[0]) else REF_DE_VARIAVEL.sub("*", m[0]),
                  sem_aspas)


def nome_da_c18(nome):
    """U3: o nome está nas listas fechadas da C18 (git e githooks(5)), também por curinga."""
    return nome in NOMES_DA_C18 or bool(CURINGA.search(nome)) and any(glob_casa(nome, n) for n in NOMES_DA_C18)


# Volta da E1.232 (A1 e A2 da segurança E1.206, A1 do review E1.205): U4, lista positiva. O destino opaco sem resto ou
# com resto colado (`"$(echo .g)it/config"`) libera só o valor que o hook calcula: corpo da lista positiva
# (`na_lista_positiva`), ou `echo` e `printf %s` de palavras literais, direto, por função ou por variável da linha.
# `printf` com formato, `tr`, `sed`, `rev`, `base64`, `cat` e todo o resto recusam (AR-3).
SEM_VALOR = "\0"  # a saída de um corpo da lista positiva ou a variável do ambiente: o hook não a sabe
LITERAL = re.compile(r"[\w.,:@%+=/*?\[\]~ -]*")
VARIAVEL_DO_VALOR = re.compile(r"\$(?:\{(?P<chave>[A-Za-z_]\w*)(?:(?P<op>:?[-=])(?P<padrao>[^}]*))?\}"
                               r"|(?P<nome>[A-Za-z_]\w*))")
# Shell Variables do manual do bash que o próprio bash grava durante a execução (A4 da segurança E1.280)
VARIAVEIS_DO_BASH = frozenset("_ REPLY MAPFILE BASH_REMATCH OPTARG OPTIND PWD OLDPWD DIRSTACK COPROC BASH_ARGV BASH_ARGV0 "
                              "BASH_ARGC BASH_COMMAND BASH_SOURCE BASH_LINENO FUNCNAME PIPESTATUS READLINE_LINE "
                              "READLINE_POINT READLINE_MARK COMP_WORDS COMP_CWORD COMP_LINE COMP_POINT COMPREPLY "
                              "BASH_EXECUTION_STRING EPOCHREALTIME EPOCHSECONDS RANDOM SRANDOM LINENO SECONDS".split())
TETO_DE_VALORES = 64  # combinações de valores de uma palavra; acima, o hook não calcula
# Redesenho da E1.322 (A1 a A3 do review E1.319, A7 a A9 da segurança E1.320, A2 do QA E1.321): a lista positiva, o
# `echo`/`printf %s` calculado e a troca de `$(pwd)` por `$PWD` valem só quando todos os comandos da linha, lidos como o
# bash os lê depois de tirar aspas e barras (`shlex`), estão numa lista fechada de comandos que não trocam a resolução
# nem a saída de outro comando. O que o hook não reconhece recusa (falha fechada; sobra recusa, nunca falta).
COMANDOS_INOFENSIVOS = frozenset("echo printf cat tee cp mv ln install dd mkdir touch rm rmdir ls find git date mktemp "
                                 "pwd true false : test [ head tail wc sort uniq grep cut basename dirname realpath "
                                 "readlink stat diff".split())
PALAVRAS_DA_GRAMATICA = frozenset("{ ! if then elif else do while until time".split())  # a posição de comando segue
FIM_DA_GRAMATICA = frozenset("} fi done".split())
ATRIBUICAO = re.compile(r"(?P<nome>[A-Za-z_]\w*)(?:\[(?P<indice>[^]]*)\])?\+?=")
INDICE_LITERAL = re.compile(r"[0-9]+")  # o índice de vetor é aritmética: só o número não atribui
NOME_INOFENSIVO = re.compile(r"[a-z_][a-z0-9_]*")  # o bash não lê nome minúsculo (PATH, TMPDIR, GIT_*, BASH_* são maiúsculos)
PADRAO_QUE_ATRIBUI = re.compile(r"\$\{#?(?P<nome>\w+)(?:\[[^]]*\])?:?=")
# `${!x:=v}` atribui ao nome guardado em `x` e `${x@P}` expande o valor como prompt (com `${T:=v}` dentro)
EXPANSAO_QUE_ESCONDE = re.compile(r"\$\{(?:!|[^}]*@[A-Za-z])")
# Volta da E1.326 (A4 do review E1.323, A10 da segurança E1.324): o bash avalia aritmética em qualquer palavra, também
# argumento, e ela atribui (`PATH=5`, `BASH_CMDS[date]=7`); o índice de nome avalia o valor da variável como expressão
# (`i=PATH=5; : ${a[i]}`). Recusa no texto: `$[`, `((` (também `$((`), vetor composto `=(`, `${…[…]}` com índice que não
# é número, `@` nem `*`, `${…:…}` de deslocamento que não é só número e o descritor nomeado `{nome}>f`, que grava o
# número no nome. `test`/`[` (`-v` avalia o índice) e o índice da atribuição são lidos na palavra, em `linha_conhecida`.
CONTEXTO_ARITMETICO = re.compile(r"\$\[|\(\(|=\(|\$\{[^}\[]*\[(?![0-9]+\]|[@*]\])|\$\{[^}:]*:(?![-=+?]|[0-9\s:-]*\})"
                                 r"|(?<!\$)\{[^{}\s]*\}[<>]")
LE_INDICE = frozenset("test [".split())  # `test -v 'x[i]'` avalia o índice; o nome pode vir de `$`, crase ou curinga
REDIRECAO = re.compile(r"&?[<>]+[&|]?")
# Embutidos e palavras reservadas do bash 5 (`compgen -b`, `compgen -k`): função com esse nome fora da lista não vale,
# porque o hook acha a definição pelas palavras sem aspas (`"function" source` não define nada e o `source` seguinte é o
# embutido); com nome de programa, o engano só libera um programa, que não troca a resolução do shell.
EMBUTIDOS_DO_BASH = frozenset(""". : [ alias bg bind break builtin caller cd command compgen complete compopt continue
    declare dirs disown echo enable eval exec exit export false fc fg getopts hash help history jobs kill let local logout
    mapfile popd printf pushd pwd read readarray readonly return set shift shopt source suspend test times trap true type
    typeset ulimit umask unalias unset wait if then else elif fi case esac for select while until do done in function
    time { } ! [[ ]] coproc""".split())
NOME_DE_FUNCAO = re.compile(r"[A-Za-z_][\w-]*")


def linha_juntada(linha):
    """A3 do QA E1.325: a linha com cada `\\` + quebra tirado como o bash tira (`juntar_continuacoes`: a barra escapada
    antes não conta, e `\\\\` + quebra fica, barra e separador, como o `shlex` o lê), ou None se o hook não sabe onde o
    bash junta: com aspa simples ou `#` na linha (na aspa e no comentário a barra do fim não continua a linha)."""
    if "\\\n" not in linha:
        return linha
    return None if "'" in linha or "#" in linha else juntar_continuacoes(linha)


def expansao_conhecida(linha):
    """As buscas de texto de `linha_conhecida`: sem contexto aritmético, sem `${NOME:=v}` de nome que o bash lê e sem
    expansão que esconde o nome. Vale também para o corpo de heredoc sem aspas no delimitador (A12 da segurança
    E1.328, A5 do review E1.327), que o bash expande no próprio processo."""
    if linha is None or CONTEXTO_ARITMETICO.search(linha):
        return False
    texto = linha.replace("\n", ";")
    if any(not NOME_INOFENSIVO.fullmatch(m["nome"]) for m in PADRAO_QUE_ATRIBUI.finditer(texto)):
        return False
    if EXPANSAO_QUE_ESCONDE.search(texto):
        return False
    return True


def corpos_conhecidos(comando):
    """A12 da segurança E1.328: todo corpo de heredoc que o bash expande (delimitador sem aspas nem `\\`), como ele o
    entrega, passa nas buscas de `expansao_conhecida`; o corpo de `<<'E'` é literal e não conta. A13 (E1.332): o corpo
    não atribui, nem a nome minúsculo (`${d:=v}`), porque `valores_da_variavel` não o lê."""
    corpos = [expandir_heredoc(comando[h.corpo[0]:h.corpo[1]]) for h in heredocs(comando)[0] if not h.literal]
    return all(expansao_conhecida(corpo) and not PADRAO_QUE_ATRIBUI.search(corpo) for corpo in corpos)


@lru_cache(maxsize=256)
def linha_conhecida(linha, funcoes=frozenset()):
    """Todos os comandos da linha, e os de cada `$(…)` e crase dela, estão em `COMANDOS_INOFENSIVOS` ou são funções
    definidas na linha (o corpo delas é lido como o resto); a atribuição e o `${x:=v}` só com nome minúsculo;
    `printf -v` recusa."""
    linha = linha_juntada(linha)
    if not expansao_conhecida(linha):
        return False
    texto = linha.replace("\n", ";")
    lexico = shlex.shlex(texto, posix=True, punctuation_chars=True)
    lexico.whitespace_split, lexico.commenters = True, ""
    try:
        palavras = list(lexico)
    except ValueError:  # aspa sem par
        return False
    for i in range(len(palavras) - 1, 0, -1):  # `f ( )` define a função como `f()`
        if palavras[i - 1:i + 1] == ["(", ")"]:
            palavras[i - 1:i + 1] = ["()"]
    definidas = {p for i, p in enumerate(palavras[1:]) if palavras[i] == "function"} | {
        p for i, p in enumerate(palavras[:-1]) if palavras[i + 1] == "()"}
    funcoes = funcoes | {f for f in definidas if NOME_DE_FUNCAO.fullmatch(f) and (
        f not in EMBUTIDOS_DO_BASH or f in COMANDOS_INOFENSIVOS)}
    inicio, alvo, funcao, comando = True, False, False, None
    for p in palavras:
        if alvo or funcao:
            alvo, funcao = False, False
        elif p and all(c in lexico.punctuation_chars for c in p):
            alvo = bool(REDIRECAO.fullmatch(p))
            if not alvo:
                inicio, comando = p != ")", None
        elif not inicio:
            if comando == "printf" and p.startswith("-v"):
                return False
            if comando in LE_INDICE and any(c in p for c in "[$`*?"):
                return False
        elif p in PALAVRAS_DA_GRAMATICA:
            continue
        elif p in FIM_DA_GRAMATICA:
            inicio, comando = False, None
        elif p == "function":
            funcao = True  # o nome que vem depois dele não fecha a posição de comando: o corpo `{ …; }` é lido
        elif m := ATRIBUICAO.match(p):
            if not NOME_INOFENSIVO.fullmatch(m["nome"]):
                return False
            if m["indice"] is not None and not INDICE_LITERAL.fullmatch(m["indice"]):
                return False
        elif p in COMANDOS_INOFENSIVOS or p in funcoes:
            inicio, comando = False, p
        else:
            return False
    return all(linha_conhecida(corpo, funcoes) for corpo in corpos_de_substituicao(texto))


def na_lista_positiva(corpo, linha):
    """O corpo está em `CORPO_POSITIVO`, não cita o `.git` (A3 da segurança E1.206: `mktemp -p .git`), a linha não
    redefine o comando como função (A1 do review E1.279: `date(){ printf .gi%s t/config; }`) e todos os comandos dela
    estão na lista fechada (`linha_conhecida`, E1.322), no U4 e no U3."""
    if not linha_conhecida(linha, frozenset()):  # defesa do U3; no U4, `valores_do_corpo` recusa antes
        return False
    if corpo_da_funcao(corpo.split()[0] if corpo.split() else corpo, linha)[0]:
        return False
    return bool(CORPO_POSITIVO.fullmatch(corpo)) and not cita_o_dir_do_git(corpo)


def juntar(partes):
    """Cada combinação das alternativas das partes, na ordem; None acima de `TETO_DE_VALORES`."""
    valores = [""]
    for alternativas in partes:
        valores = [v + a for v in valores for a in alternativas]
        if len(valores) > TETO_DE_VALORES:
            return None
    return valores


PALAVRA_DO_CORPO = re.compile(r"""(?:[^\s'"]+|'[^']*'|"[^"]*"|['"])+""")  # a aspa sem par fica na palavra (U4 recusa)


def dividir_corpo(corpo):
    """As palavras do corpo, cortadas no espaço fora de aspas e com as aspas."""
    return PALAVRA_DO_CORPO.findall(corpo)


def corpo_da_funcao(nome, linha):
    """(definida, corpo): se a linha define a função `nome` e o corpo da definição única (`f(){ …; }`, `f() ( … )`,
    `function f { …; }`), sem o `;` do fim; corpo None se o hook não o lê."""
    nome = re.escape(nome)
    if not re.search(rf"(?<![\w$.-]){nome}\s*\(\s*\)|(?<![\w$.-])function\s+{nome}(?![\w.-])", linha):
        return False, None
    definicoes = list(re.finditer(rf"(?:(?<![\w$.-])function\s+{nome}(?:\s*\(\s*\))?|(?<![\w$.-]){nome}\s*\(\s*\))\s*"
                                  r"(?:\{(?P<chaves>[^{}]*)\}|\((?P<parenteses>[^()]*)\))", linha))
    if len(definicoes) != 1:
        return True, None
    corpo = definicoes[0]["chaves"] if definicoes[0]["chaves"] is not None else definicoes[0]["parenteses"]
    return True, re.sub(r"\s*;\s*$", "", corpo.strip())


def valores_do_corpo(corpo, linha, fundo):
    """U4: os valores da saída do corpo de `$(…)` ou da crase, ou None fora da lista positiva."""
    corpo = corpo.strip()
    if not linha_conhecida(linha):  # A2 do review E1.319, A7 da segurança E1.320: também o `echo` e o `printf %s`
        return None
    if na_lista_positiva(corpo, linha):
        return [SEM_VALOR]
    palavras = dividir_corpo(corpo)
    if not palavras or fundo > 4:
        return None
    definida, definicao = corpo_da_funcao(palavras[0], linha)
    if definida:  # a função da linha vale pelo corpo dela, também a que se chama `echo`
        return valores_do_corpo(definicao, linha, fundo + 1) if definicao is not None and len(palavras) == 1 else None
    if palavras[0] == "echo" and not any(p.startswith("-") for p in palavras[1:]):
        args, separador = palavras[1:], " "
    elif palavras[0] == "printf" and palavras[1:2] in (["%s"], ["'%s'"], ['"%s"']):
        args, separador = palavras[2:], ""
    else:
        return None
    valores = [valores_da_palavra(arg, linha, fundo + 1, sem_substituicao=True) for arg in args]
    if None in valores:
        return None
    return juntar([parte for v in valores for parte in ([separador], v)][1:])


def atribui_por_expansao(nome, linha):
    """`${nome:=v}` ou `${nome=v}` (também com índice) atribui na própria linha."""
    return re.search(rf"\$\{{#?{nome}(\[[^]]*\])?:?=", linha) is not None


def nasce_fora_do_ambiente(nome, linha):
    """U4: o nome não vale como do ambiente: o bash o grava, é do git ou nasce na linha de outro jeito que `nome=v`
    (`for`, `read`, `${nome:=v}`). Vale para o nome inteiro e para cada prefixo de `$dt` (A16 da segurança E1.340)."""
    if nome in VARIAVEIS_DO_BASH:  # A4 da segurança E1.280: o bash a grava (`read`, `mapfile`, `=~`), não é do ambiente
        return True
    if nome.startswith("GIT_") or re.search(rf"(?<![\w${{]){nome}(?![\w=])", linha):
        return True
    return atribui_por_expansao(nome, linha)  # A14 (E1.332): `${d:=v}` atribui na linha


DECLARADORES = frozenset("declare typeset local export readonly".split())
OPCAO_SEM_REFERENCIA = re.compile(r"[-+][A-Za-mo-z]+")  # sem `n`: `-n` faz de `d=_` uma referência a `$_`


def atribui_como_argumento(nome, linha):
    """CONFORMIDADE-DECLARE-N (A19): `nome=` vem como argumento de um comando, não como atribuição do shell. Só o
    declarador literal com opções literais sem `n` (`declare -r d=x`, `local d=x`) dá o valor escrito; `declare -n d=_`,
    `$c -n d=_`, `declare $o d=_` e a linha que o hook não lê, não (falha fechada)."""
    lidas = leituras(linha)
    if lidas.ilegivel:  # a linha que o hook não lê: nenhuma atribuição vale
        return True
    atribuicao = re.compile(rf"{re.escape(nome)}(\[[^]]*\])?\+?=")
    for partes in lidas.partes:
        for palavras, *_ in partes:
            while palavras and palavras[0] in PALAVRAS_DA_GRAMATICA | CORPO_DE_LACO:
                palavras = palavras[1:]
            for i, p in enumerate(palavras):
                if not atribuicao.match(p) or all(ATRIBUICAO.match(w) for w in palavras[:i]):
                    continue
                if palavras[0] not in DECLARADORES or not all(
                        OPCAO_SEM_REFERENCIA.fullmatch(w) or ATRIBUICAO.match(w) for w in palavras[1:i]):
                    return True
    return False


def valores_da_variavel(m, linha, fundo):
    """U4: os valores de `$x`, `${x}` e `${x:-v}`: o da única atribuição na linha ou, sem ela, o do ambiente
    (`SEM_VALOR`), mais o padrão literal; None se a variável nasce de outro jeito (`for`, `read`, `+=`)."""
    nome = m["chave"] or m["nome"]
    if nasce_fora_do_ambiente(nome, linha):
        return None
    atribuicoes = [valor_atribuido(linha, a.end()) for a in re.finditer(rf"(?<![\w$]){nome}=", linha)]
    if len(atribuicoes) > 1 or atribuicoes and atribui_como_argumento(nome, linha):  # A19: `declare -n d=_`
        return None
    if not atribuicoes and any(nasce_fora_do_ambiente(nome[:k], linha) or re.search(rf"(?<![\w$]){nome[:k]}=", linha)
                               for k in range(1, len(nome))):  # A15 (E1.336), A16 (E1.340): `"$d"t` e `"$_"t`
        return None  # `d=.gi; cp x "$d"t` chega sem aspas como `$dt`: o prefixo nascido na linha não é do ambiente
    valores = valores_da_palavra(atribuicoes[0], linha, fundo + 1) if atribuicoes else [SEM_VALOR]
    if m["op"] and valores is not None:
        padrao = valores_da_palavra(m["padrao"], linha, fundo + 1, sem_substituicao=True)
        valores = None if padrao is None else valores + padrao
    return valores


def fim_do_parentese(texto, inicio):
    """A posição do `)` que fecha o `$(` aberto antes de `inicio`, ou o fim do texto (sobra corpo, nunca falta)."""
    fundo = 1
    for j in range(inicio, len(texto)):
        fundo += {"(": 1, ")": -1}.get(texto[j], 0)
        if not fundo:
            return j
    return len(texto)


def valores_da_palavra(palavra, linha, fundo=0, sem_substituicao=False):
    """U4: os valores que o bash pode dar à palavra, com `SEM_VALOR` no lugar do que o hook não sabe, ou None quando
    ele não os calcula. `$(…)` sem aspas vale por cada corpo da linha; crase partida, só como único corpo e palavra."""
    if fundo > 4 or SEM_VALOR in palavra:
        return None
    if palavra.count("`") % 2:
        corpos = corpos_de_substituicao(linha)
        inteira = len(corpos) == 1 and re.search(rf"(?:^|[\s;&|(]|\sof=)`{re.escape(corpos[0])}`(?:$|[\s;&|)])", linha)
        return None if sem_substituicao or not inteira else valores_do_corpo(corpos[0], linha, fundo + 1)
    partes, i, aspas = [], 0, False
    while i < len(palavra):
        c, valores = palavra[i], None
        if c == '"':
            aspas, i = not aspas, i + 1
            continue
        if c == "'" and not aspas:
            j = palavra.find("'", i + 1)
            valores, i = ([palavra[i + 1:j]] if j > i and LITERAL.fullmatch(palavra[i + 1:j]) else None), j + 1
        elif palavra.startswith(OPACO["$"], i) and not sem_substituicao:
            corpos = [valores_do_corpo(corpo, linha, fundo + 1) for corpo in corpos_de_substituicao(linha)]
            valores = None if not corpos or None in corpos else [v for vs in corpos for v in vs]
            i += len(OPACO["$"])
        elif (palavra.startswith("$(", i) or c == "`") and not sem_substituicao:
            fim = palavra.find("`", i + 1) if c == "`" else fim_do_parentese(palavra, i + 2)
            valores, i = valores_do_corpo(palavra[i + (1 if c == "`" else 2):fim], linha, fundo + 1), fim + 1
        elif c == "$" and (m := VARIAVEL_DO_VALOR.match(palavra, i)):
            valores, i = valores_da_variavel(m, linha, fundo + 1), m.end()
        elif LITERAL.fullmatch(c):
            valores, i = [c], i + 1
        if valores is None:
            return None
        partes.append(valores)
    return juntar(partes)


def valor_no_git(valores):
    """U4: algum valor cai no `.git` pelo U1. O que o hook não sabe vale como curinga (`*`), salvo sozinho num
    componente (`"$(mktemp -d)"`, `"$TMPDIR"/`): a saída da lista positiva sozinha nunca é o `.git`."""
    return any(cita_o_dir_do_git("/".join("_" if c == SEM_VALOR else c.replace(SEM_VALOR, "*") for c in v.split("/")))
               for v in valores)


def opcoes_sem_exec(args):
    """Todas as opções são de leitura pura: curta só com letras de `CURTAS_SEM_EXEC`, longa só pelo nome exato em
    `LONGAS_SEM_EXEC`; `+comando` (less) e qualquer outra forma recusam. Depois de `--` tudo é argumento."""
    for a in args:
        if a == "--":
            return True
        if a.startswith("--"):
            if a[2:].split("=", 1)[0] not in LONGAS_SEM_EXEC:
                return False
        elif a.startswith("-") and len(a) > 1:
            if not set(a[1:]) <= CURTAS_SEM_EXEC:
                return False
        elif a.startswith("+"):
            return False
    return True


def forma_aceita(achado):
    """ADR 0011, item 2 (E3.50): a forma que o hook aceita no lugar da construção recusada, dita na mensagem da recusa."""
    if achado.startswith("$"):
        return (f"valor literal no lugar de {achado} (caminho, branch, log); "
                "texto com $ só entre aspas simples: '${{ x }}'")
    if achado == "heredoc":
        return FORMA_DO_HEREDOC
    return "branch literal, um comando por linha, sem # entre linhas, $, crase, chaves nem case"


def so_leitura(linha):
    """F6: a linha só lê (todo segmento da leitura fiel de `leituras()`, ADR 0013, é leitor sem execução ou
    `git log|show|diff`), sem `$`, crase, `#` (sem comentário, a leitura é uma só e não há o que provar), várias linhas, substituição, redirecionamento de saída nem opção que execute programa: `forge` e `sugerir` ali são dado.
    `eval`, `xargs`, shell aninhado, variável antes do programa e programa com caminho não são leitor: recusam. Na dúvida, False."""
    if re.search(r"[$`\n#]", linha):
        return False
    lidas = leituras(linha)
    if lidas.ilegivel or len(lidas.partes) != 1 or not lidas.partes[0]:
        return False
    for palavras, destinos, sub in lidas.partes[0]:
        if destinos or sub or not palavras:
            return False
        prog, args = palavras[0], palavras[1:]
        if prog == "git":
            if not args or args[0] not in GIT_LEITURA:
                return False
            args = args[1:]
        elif prog not in LEITORES_SEM_EXEC:
            return False
        if not opcoes_sem_exec(args) or any(re.match(r"[*?\[]", a) or "{" in a for a in args):
            return False  # R2 (conformidade-leitura): `*`, `?` e `[` no início e `{` expandem para `--pre=...`
    return True


def guardar_exato(linha):
    """A linha inteira é `forge sugerir --guardar <um texto entre aspas>` (ou `forge-sugerir`, `bin/forge-sugerir`): sem
    encadeamento, variável, substituição, redirecionamento nem nada antes ou depois."""
    linha = linha.strip()
    if not GUARDAR_EXATO.fullmatch(linha):
        return False
    try:
        palavras = shlex.split(linha)
    except ValueError:
        return False
    return palavras[:-1] in (["forge", "sugerir", "--guardar"], ["forge-sugerir", "--guardar"], ["bin/forge-sugerir", "--guardar"])


BINARIOS_DE_ATUALIZACAO = {"forge-atualizar", "forge-voltar-versao", "forge-sugerir"}
SUBCOMANDOS_DE_ATUALIZACAO = {"atualizar", "voltar-versao", "sugerir"}
ENVOLVEDORES = {"env", "script", "nohup", "sudo", "command", "exec", "time", "timeout", "setsid", "stdbuf", "unbuffer", "xargs",
                "nice", "ionice", "busybox", "expect", "socat"}
SUGESTAO = "se deveria valer, registre como sugestão ao Forge"
PERGUNTAS = {
    "descartar": "Isso descarta as mudanças ainda não salvas e não dá para recuperá-las. Prefira 'forge desfazer'. Confirma?",
    "limpar": "Isso apaga os arquivos novos ainda não salvos, sem volta. Confirma?",
    "arquivar": "Isso deixa o projeto somente leitura no GitHub: ninguém salva nada até desarquivar. Confirma?",
    "rebase": "Isso reescreve versões que já estão no GitHub; outras cópias deixam de bater. Confirma?",
    "mover": "Isso move uma branch já publicada no GitHub para outro ponto; outras cópias deixam de bater. Confirma?",
}
DISPENSA_NA_COPIA = {"descartar", "limpar"}  # só atos sobre os arquivos da cópia; `rebase` e `arquivar` perguntam sempre
UM_ATO_SIMPLES = re.compile(r"\s*git\s+(reset|clean|checkout|restore)(\s+[^\s;&|`$()<>\\\n]+)*\s*")
ATO_FORA_DA_COPIA = re.compile(r"(^|\s)(-C|--work-tree|--git-dir|--work-tree=\S*|--git-dir=\S*)(\s|$)|GIT_DIR|GIT_WORK_TREE|\b(cd|pushd)\b")
REBASE_COM_VALOR = {"--onto", "-s", "--strategy", "-X", "--strategy-option", "-x", "--exec", "-C"}
REMOCAO = {"rm", "mv", "rmdir", "unlink", "shred"}
# A2 da segurança (v0478; C9 de docs/security/v047-v2-ameacas.md): comandos que escrevem ou removem por opção. O modo, o dono
# e os atributos mudam o acesso ao alvo e, com `-R`, ao que há dentro: escrita nos operandos e remoção do ancestral.
MUDA_ATRIBUTO = {"chmod", "chown", "chgrp", "setfacl", "chattr"}
FIND_EXECUTA = {"-exec", "-execdir", "-ok", "-okdir"}  # roda o comando até `;` ou `+`, com `{}` trocado pelo achado
FIND_GRAVA = {"-fprint", "-fprint0", "-fprintf", "-fls"}  # grava no arquivo seguinte
TAR_GRAVA = {"create", "append", "update", "concatenate", "catenate", "delete"}  # modos que gravam no arquivo de `-f`
TAR_COM_VALOR = "bCfFgHIKLNTVX"  # letras curtas do GNU tar com valor, colado (`-C.git`) ou na palavra seguinte
TAR_EXECUTA = {"to-command", "use-compress-program", "info-script", "new-volume-script", "rsh-command", "rmt-command",
               "checkpoint-action"}  # rodam o valor (o `checkpoint-action`, o que vem depois de `exec=`)
LONGAS_EXATAS = {"checkpoint"}  # nome exato de opção que é prefixo de outra (`--checkpoint-action`): não a abrevia
Alvos = collections.namedtuple("Alvos", "pastas arquivos removidos executados")  # o que um `EXTRATORES` faz por opção

# Papel só de leitura: o `git ls-remote` aceita só estas opções (`--upload-pack`, `-u` e `--exec` rodam um programa num
# shell); nos demais subcomandos da lista, a opção que executa programa ou grava arquivo recusa, mesmo abreviada.
LS_REMOTE_LEITURA = {"--heads", "--tags", "--branches", "-h", "-t", "-b", "--refs", "-q", "--quiet", "--exit-code",
                     "--symref", "--get-url"}
GIT_EXECUTA = ("--upload-pack", "--receive-pack", "--exec", "--config-env", "--ext-diff", "--textconv", "--filters",
               "--show-signature")  # `--show-signature` roda o `gpg.program`
# Opções de verdade que são prefixo de uma de `GIT_EXECUTA` (o git escolhe a exata); no `cat-file`, que não as tem, o
# mesmo texto é abreviação de `--textconv`/`--filters`.
GIT_EXATAS = {"--text", "--filter"}
# `%G?`, `%GS`, `%+GK`... no `--format`/`--pretty` do git rodam o `gpg.program` para verificar a assinatura.
FORMATO_ASSINATURA = re.compile(r"%[-+ ]?G")
# Opção do `forge-check` que grava (hoje nenhuma existe; o Pacote A prevê `--gerar-entrada` no `entrega`): o papel só de leitura
# nunca a herda da liberação do subcomando (VV-2, B2); a opção que gravar nasce aqui, ou em subcomando fora da lista.
FORGE_CHECK_GRAVA = ("--gerar-entrada", "--gravar", "--escrever", "--salvar")
# Nomes que ainda não existem casam só por inteiro: `--destino` do `forge-check brief` é prefixo de `--destino-arquivo`.
FORGE_CHECK_GRAVA_EXATA = ("--destino-arquivo",)
# FURO-HOOK-A, A4: o subcomando do `forge-check` que grava fora do papel só de leitura -> a pasta de destino (a política de caminhos
# decide quem grava lá); o `transcricao anonimizar` grava no 2.º argumento. Os que gravam em caminho livre ficam na 2.ª lista.
FORGE_CHECK_ESCRITAS = {"anotar": "docs/pedidos", "brief": "docs/briefs", "medida": "docs/kanban", "pedido": "docs/pedidos",
                        "pausa": ".forge", "rodar": ".forge", "meta": ".forge"}  # 0.44.2: `rodar` (S5) e `meta` (S4) gravam em .forge/run  # X1: `pausa` sem `--retomar` grava .forge/pausa.json  # S2: `pedido fala --gravar`
FORGE_CHECK_EM_CAMINHO_LIVRE = {"movimento", "registrar"}
# 0.43.1 (P1, P2): a forma nova grava no `## Histórico` do pedido: `brief selar` (o selo) e `entrega --pedido` (a `entrega conferida`),
# esta salvo com `--sem-gravar`. A forma antiga do `entrega` (pedido posicional) só lê.
# `test` no papel só de leitura: só estas, com um caminho (`agents/conferente.md`); o `-v` reavalia o índice como código.
TESTE_LEITURA = {"-e", "-f", "-d", "-s"}
DICA_LEITURA = ("use só os comandos de `so_leitura` em hooks/conformidade.json, um por vez ou encadeados com &&, ; e |; "
                "o que exige escrita é de outro agente")

ACOES = {"merge_integracao", "pr_criar", "pr_merge_integracao", "instalar_pacote", "instalar_congelado"}


def papel_de(politica, agent_type):
    """Papel do `agent_type`: sem ele, a sessão principal; tipo desconhecido é `dev` (ADR 0009, seção 2)."""
    if not agent_type:
        return politica["sem_agent_type"]
    for papel, tipos in politica["papeis"].items():
        if agent_type in tipos:
            return papel
    return politica["papel_padrao"]


@functools.lru_cache(maxsize=1024)
def _pasta_real(pasta):
    return os.path.realpath(pasta)


def realpath_pela_pasta(caminho):
    """`os.path.realpath(caminho)`, com o `realpath` da pasta guardado (a linha com milhares de arquivos na mesma pasta não
    resolve a pasta de novo a cada um). O último nome que é link, `.`, `..` ou vazio vai ao `realpath` inteiro."""
    pasta, nome = os.path.split(caminho)
    if not pasta or nome in ("", ".", "..") or os.path.islink(caminho):
        return os.path.realpath(caminho)
    return os.path.join(_pasta_real(pasta), nome)


def relativo_ao_pai(posix, base):
    """O `relative_to(base).as_posix()` do caminho absoluto e resolvido `posix` quando `base` (resolvida) é ele ou um pai dele
    (`.` quando é ele); senão None. Pelo texto, sem montar os `parents` (custo: uma chamada por arquivo gravado da linha)."""
    b = base.as_posix()
    if posix == b:
        return "."
    prefixo = b if b.endswith("/") else b + "/"
    return posix[len(prefixo):] if posix.startswith(prefixo) else None


def casa(rel, caminho):
    """`rel` é o `caminho` (arquivo) ou está dentro dele (diretório, que termina em `/`). Um `*` no `caminho` vale por
    uma pasta qualquer (`~/.forge-contrib/*/docs/pedidos/`: a cópia de trabalho do Forge, qualquer que seja o nome)."""
    if "*" in caminho:
        padrao = "[^/]+".join(re.escape(p) for p in caminho.split("*"))
        return re.match(padrao + ("" if caminho.endswith("/") else "$"), rel + ("/" if caminho.endswith("/") else "")) is not None
    return rel.startswith(caminho) or rel + "/" == caminho if caminho.endswith("/") else rel == caminho


def em_qualquer_lugar(posix, caminho):
    return ("/" + caminho) in posix + "/" if caminho.endswith("/") else posix.endswith("/" + caminho)


def endpoint_normalizado(endpoint):
    """O endpoint do `gh api` como o GitHub o lê: sem `?…` nem `#…`, sem esquema e host (`https://api.github.com/`), sem a
    barra inicial e sem o prefixo do GitHub Enterprise (`api/v3/`, `api/`). `/graphql` e a URL completa viram `graphql`."""
    e = re.split(r"[?#]", endpoint.strip(), maxsplit=1)[0]
    e = re.sub(r"^[a-z][a-z0-9+.-]*://[^/]*", "", e, flags=re.I).lstrip("/")
    return re.sub(r"^api/(v3/)?", "", e, flags=re.I).rstrip("/")


def e_graphql(endpoint):
    """O endpoint normalizado é o do GraphQL (`graphql`, `/graphql`, `https://<host>/graphql`, `.../api/graphql`)."""
    return endpoint_normalizado(endpoint).lower() == "graphql"


def edita_no_lugar(args):
    """`perl`/`ruby` com `-i`: sozinho, agrupado (`-pi`, `-0777pi`) ou com sufixo qualquer (`-i~`, `-i_bak`, `-i,o`,
    `-pi~`: o que vem depois do `i` é o sufixo). Opção que leva o resto do grupo como valor (`-Mstrict`, `-Ilib`,
    `-e...`) encerra a busca; o valor de `-e`/`-E` e o que vem depois de `--` não são opções."""
    for k, a in enumerate(args):
        if a == "--":
            return False
        if k and args[k - 1] in ("-e", "-E") or not re.match(r"-[^-]", a):
            continue
        for letra in a[1:]:
            if letra == "i":
                return True
            if letra in OPCAO_COM_RESTO:
                break
    return False


def longa_do_gnu(opcao, longas):
    """A opção longa inteira que `--<prefixo>[=valor]` abrevia (`--expr` -> `expression`), à maneira do `getopt_long`:
    o nome exato ou o prefixo que só um nome de `longas` tem; ambíguo ou desconhecido devolve vazio."""
    if not opcao.startswith("--") or len(opcao) < 3:
        return ""
    nome = opcao[2:].split("=", 1)[0]
    achadas = [o for o in longas if o.startswith(nome)]
    return nome if nome in longas else achadas[0] if len(achadas) == 1 else ""


def awk_no_lugar(args):
    """`awk`/`gawk`/`nawk` que carrega a extensão `inplace` por qualquer caminho (`-i inplace`, `-iinplace`, `-E inplace.awk`,
    `-l inplace`, `--include`/`--inc`/`--load`/`--lo` abreviados, `-f inplace.awk`, `@include`/`@load`): do lado fechado,
    qualquer argumento que cite `inplace` liga a conferência, e os arquivos-alvo contam como escrita."""
    return any("inplace" in a.lower() for a in args)


def script_do_sed(arg):
    """O texto de script de um argumento do `sed`: o argumento solto, `--expression=<texto>` (ou abreviada, `--expr=`) ou
    `-e<texto>` colado (também no grupo, `-ne<texto>`); opção sem script (`-n`, `-i.bak`) devolve vazio."""
    if longa_do_gnu(arg, SED_LONGAS) == "expression" and "=" in arg:
        return arg.split("=", 1)[1]
    colado = re.match(r"-[a-zA-Z]*e(.+)", arg) if not arg.startswith("--") else None
    return colado.group(1) if colado else "" if arg.startswith("-") else arg


def longa_do_tar(nome, opcoes):
    """O nome da opção longa (do `tar`, do `cpio`) é uma das `opcoes` ou abreviação dela (o getopt do GNU aceita o prefixo;
    o ambíguo o programa recusa, então contar a mais só recusa a mais); o nome exato de outra opção (`--checkpoint`) não."""
    return nome in opcoes or len(nome) >= 2 and nome not in LONGAS_EXATAS and any(o.startswith(nome) for o in opcoes)


def ler_opcoes(args, curtas_com_valor, longas_com_valor, velho=False):
    """As opções de um extrator à maneira do getopt (volta 2, review A1): (letras, [(opção, valor)], operandos). A letra de
    `curtas_com_valor` toma o resto do grupo (`-C.git/forge`, `-cf.git/a`) ou a palavra seguinte; com `velho` (o `tar`), o
    grupo sem `-` na primeira palavra (`xfC a.tar d`) toma as palavras seguintes na ordem. A longa de `longas_com_valor` sem
    `=` toma a palavra seguinte; as outras ficam com valor None. Depois de `--`, só operandos."""
    letras, valores, operandos, i, fim = set(), [], [], 0, False
    while i < len(args):
        a, i = args[i], i + 1
        if a == "--" and not fim:
            fim = True
        elif fim or a == "-" or not a.startswith("-") and not (velho and i == 1 and re.fullmatch(r"[A-Za-z]+", a)):
            operandos.append(a)
        elif a.startswith("--"):
            nome, igual, valor = a[2:].partition("=")
            if not igual and longa_do_tar(nome, longas_com_valor) and i < len(args):
                valor, i, igual = args[i], i + 1, "="
            valores.append((nome, valor if igual else None))
        else:
            velho, grupo = not a.startswith("-"), a.lstrip("-")
            for k, letra in enumerate(grupo):
                letras.add(letra)
                if letra in curtas_com_valor:
                    valor = "" if velho else grupo[k + 1:]
                    if not valor and i < len(args):
                        valor, i = args[i], i + 1
                    valores.append((letra, valor))
                    if not velho:
                        break
    return letras, valores, operandos


def valores_de(valores, curtas, longas):
    """Os valores da opção curta de `curtas` ou da longa de `longas` (também abreviada)."""
    return [v for n, v in valores if v is not None and (n in curtas if len(n) == 1 else longa_do_tar(n, longas))]


def longas_de(valores):
    return [n for n, _ in valores if len(n) > 1]


# Volta 3 (E1.13): por programa, as opções que escolhem a pasta de destino ou o arquivo gravado, tiradas da ajuda do
# próprio programa (`tar --help` do GNU tar 1.35, `bsdtar --help` 3.7, `cpio --help` 2.15, `unzip -h` 6.0, `7z --help`
# 23.01); `le` é o que a ajuda dá como arquivo só lido, para o teste conferir a do tar contra o `tar --help` da máquina.
# `pasta`: onde extrai; `subpasta`: dentro de cada `pasta` (`--one-top-level=`); `reescreve`: expressão sed que manda o
# nome a outra pasta; `arquivo`: gravado nos modos que gravam; `grava`: gravado sempre; `remove`: apaga os operandos.
Destinos = collections.namedtuple("Destinos", "pasta subpasta reescreve arquivo grava remove le")
DESTINOS = {
    "tar": Destinos(("C", "directory"), ("one-top-level",), ("transform", "xform"), ("f", "file"),
                    ("g", "listed-incremental", "index-file", "volno-file"), ("remove-files",),
                    ("T", "files-from", "X", "exclude-from", "N", "newer", "after-date", "add-file", "exclude-ignore",
                     "exclude-ignore-recursive", "exclude-tag", "exclude-tag-all", "exclude-tag-under", "group-map",
                     "owner-map", "mtime")),
    "bsdtar": Destinos(("C", "cd", "directory"), (), ("s",), ("f", "file"), (), (),
                       ("T", "files-from", "X", "exclude-from", "newer-than", "newer-mtime-than", "older-than",
                        "older-mtime-than")),
    "cpio": Destinos(("D", "directory"), (), (), ("F", "file"), ("O",), (), ("E", "pattern-file", "I")),
    "unzip": Destinos(("d",), (), (), (), (), (), ()),
    "7z": Destinos(("o",), (), (), (), ("w", "u"), ("sdel",), ("i", "x", "ai", "ax")),  # chaves sem caixa, valor colado
}


def com_valor(destinos):
    """As letras e as longas do catálogo que tomam valor (a `subpasta` do tar é opcional, só com `=`; `remove` não tem)."""
    return separar([n for campo in destinos._fields if campo not in ("subpasta", "remove") for n in getattr(destinos, campo)])


def separar(nomes):
    """As letras (juntas, como no getopt) e as longas de `nomes`, misturadas no catálogo."""
    return "".join(n for n in nomes if len(n) == 1), tuple(n for n in nomes if len(n) > 1)


def valores_do(valores, nomes):
    """Os valores das opções de `nomes` (letras e longas misturadas, como no catálogo)."""
    return valores_de(valores, *separar(nomes))


def pastas_da_troca(expressao):
    """A pasta para onde a expressão sed do `--transform` (`s,^,pasta/,`; várias com `;`) ou do `-s` do bsdtar
    (`/^/pasta//`) manda o nome: o começo literal da troca, antes de `&` ou `\\` (troca sem pasta dá a própria pasta)."""
    pastas = []
    for e in expressao.split(";"):
        e = re.sub(r"^s(?=\W)", "", e)  # o `s` do GNU; o bsdtar começa no delimitador
        partes = re.split(r"(?<!\\)" + re.escape(e[:1]), e[1:])
        pastas.append(re.split(r"[&\\]", "".join(partes[1:2]))[0])
    return pastas


def alvos_do_tar(args, destinos=DESTINOS["tar"]):
    """A2 da segurança (v0478), pelo catálogo `DESTINOS`: o que o `tar` (e `bsdtar`, `gtar`, o do `busybox` e do
    `toybox`) faz por opção. Extração (`-x`, `--extract`, `--get`): as pastas de `pasta`, ou a corrente, e dentro de
    cada uma a `subpasta` e a pasta da `reescreve`. Criação, acréscimo e atualização (`-c`, `-r`, `-u`, `-A`,
    `--create`, `--delete`...): o `arquivo`; `grava`, sempre. `TAR_EXECUTA` (`-I`, `-F`, `--to-command`,
    `--checkpoint-action=exec=`...) roda o valor; `remove` apaga os operandos, também a partir de cada pasta. Na dúvida
    sobre o modo, não grava (o resto da linha segue as outras regras)."""
    curtas, longas = com_valor(destinos)
    letras, valores, operandos = ler_opcoes(args, TAR_COM_VALOR + curtas, (*longas, *TAR_EXECUTA), velho=True)
    nomes = longas_de(valores)
    extrai = "x" in letras or any(longa_do_tar(n, ("extract", "get")) for n in nomes)
    grava = bool(letras & set("cruA")) or any(longa_do_tar(n, TAR_GRAVA) for n in nomes)
    pastas = valores_do(valores, destinos.pasta)
    dentro = valores_do(valores, destinos.subpasta)
    dentro += [t for e in valores_do(valores, destinos.reescreve) for t in pastas_da_troca(e)]
    arquivos = [a for a in valores_do(valores, destinos.arquivo) if a != "-"] if grava else []
    arquivos += valores_do(valores, destinos.grava)
    executados = valores_de(valores, "IF", TAR_EXECUTA - {"checkpoint-action"})
    executados += [v[5:] for v in valores_de(valores, "", ("checkpoint-action",)) if v.startswith("exec=")]
    remove = any(longa_do_tar(n, destinos.remove) for n in nomes)
    removidos = [f"{d}/{o}" for o in operandos for d in (".", *pastas)] if remove else []
    extracao = [p for d in (pastas or ["."]) for p in (d, *(os.path.join(d, s) for s in dentro))]
    return Alvos(extracao if extrai else [], arquivos, removidos, executados)


def alvos_do_cpio(args, destinos=DESTINOS["cpio"]):
    """A2 da volta 2: `cpio -i`/`--extract` extrai na `pasta` (`-D`), ou na corrente; `-p`/`--pass-through`, também
    nos operandos (o destino); `-o`/`--create` grava o `arquivo` (`-F`), e `grava` (`-O`) grava sempre;
    `--rsh-command` roda o valor."""
    curtas, longas = com_valor(destinos)
    letras, valores, operandos = ler_opcoes(args, "CHMR" + curtas, (*longas, "rsh-command", "format", "message",
                                                                     "owner", "io-size"))
    nomes = longas_de(valores)
    extrai = bool(letras & set("ip")) or any(longa_do_tar(n, ("extract", "pass-through")) for n in nomes)
    cria = "o" in letras or any(longa_do_tar(n, ("create",)) for n in nomes)
    pastas = (valores_do(valores, destinos.pasta) or ["."]) + operandos if extrai else []
    arquivos = valores_do(valores, destinos.grava) + (valores_do(valores, destinos.arquivo) if cria else [])
    return Alvos(pastas, arquivos, [], valores_de(valores, "", ("rsh-command",)))


def alvos_do_unzip(args, destinos=DESTINOS["unzip"]):
    """A2 da volta 2: o `unzip` extrai na `pasta` (`-d`, colada ou na palavra seguinte), ou na corrente."""
    return Alvos(valores_do(ler_opcoes(args, com_valor(destinos)[0], ())[1], destinos.pasta) or ["."], [], [], [])


def alvos_do_7z(args, destinos=DESTINOS["7z"]):
    """A4 da volta 2 e A5 da segurança: o 7-Zip lê as chaves sem caixa (`-o`, `-O`, `-SDEL`) e com o valor colado.
    `x`/`e` extraem na `pasta` (`-o<pasta>`), ou na corrente; `a`, `u`, `d` e `rn` gravam o arquivo (o primeiro operando
    depois do comando); `grava`: a pasta de trabalho de `-w<pasta>` e o arquivo novo de `-u...!<arquivo>`; `remove`
    (`-sdel`) apaga os outros operandos. O `--` não é lido: o nome que começa com `-` depois dele conta como chave
    (recusa a mais, nunca a menos); `-w` vazio (pasta temporária) e `-u` sem `!` contam como a pasta corrente."""
    chaves, operandos = [], []
    for a in args:
        (chaves if a.startswith("-") else operandos).append(a)
    comando, arquivo = (operandos[0].lower() if operandos else ""), operandos[1:2]

    def valores(nomes):
        return [(n, c[len(n) + 1:]) for c in chaves for n in nomes if c[1:].lower().startswith(n)]

    pastas = ([v for _, v in valores(destinos.pasta)] or ["."]) if comando in ("x", "e") else []
    gravados = [v.partition("!")[2] if n == "u" else v for n, v in valores(destinos.grava)]
    removidos = operandos[2:] if any(c[1:].lower() in destinos.remove for c in chaves) else []
    return Alvos(pastas, (arquivo if comando in ("a", "u", "d", "rn") else []) + gravados, removidos, [])


# A2 e A4 da segurança, volta 2 (v0478): catálogo único dos programas que extraem, gravam ou rodam comando por opção;
# o `busybox` e o `toybox` repassam ao applet (`leitura_do_segmento`), e o `tar` deles cai aqui pelo nome.
EXTRATORES = {"tar": alvos_do_tar, "gtar": alvos_do_tar, "bsdtar": functools.partial(alvos_do_tar, destinos=DESTINOS["bsdtar"]),
              "cpio": alvos_do_cpio, "unzip": alvos_do_unzip, **dict.fromkeys(("7z", "7za", "7zr", "7zz"), alvos_do_7z)}


def sed_no_lugar(args):
    """`sed` com edição no lugar: `-i` sozinho, agrupado ou com sufixo (`-ni`, `-i.bak`) ou `--in-place[=sufixo]` em
    qualquer abreviação (`--i`, `--in-pl=~`)."""
    return any(re.fullmatch(r"-[a-zA-Z]*i.*", a) or longa_do_gnu(a, SED_LONGAS) == "in-place" for a in args)


def sem_lancadores(palavras):
    """O comando atrás dos lançadores, em cada leitura possível (`separar_lancadores`)."""
    return [comando for comando, _ in separar_lancadores(palavras)]


def atras_do_xargs(escritas, palavras):
    """A5: o `xargs` está entre os lançadores antes do comando `palavras`: os argumentos dele vêm da entrada padrão."""
    return "xargs" in {Path(p).name for p in escritas[: max(0, len(escritas) - len(palavras))]}


def exporta(palavras):
    """`export`, `declare -x` e `typeset -x` passam as variáveis aos comandos seguintes."""
    return palavras[:1] == ["export"] or palavras[:1] in (["declare"], ["typeset"]) and any(
        re.fullmatch(r"-[a-zA-Z]*x[a-zA-Z]*", p) for p in palavras[1:])


VALOR_DE_CONTAINS = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._/@^~-]*$")


def forma_de_leitura_git(chave, args):
    """E8 (C-1, C-2): lista branca exata de `git branch` (sem argumento, `--list`, `-r`, `--contains <commit>` ou
    `--contains=<commit>`, e o padrão sem `-` só junto de `--list`) e de `git worktree` (só `list`, sem argumento)."""
    if chave == "git worktree":
        return args == ["list"]
    padroes, lista, i = [], False, 0
    while i < len(args):
        a = args[i]
        if a in ("--list", "-r"):
            lista = lista or a == "--list"
        elif a == "--contains":
            i += 1
            if i >= len(args) or not VALOR_DE_CONTAINS.match(args[i]):
                return False
        elif a.startswith("--contains="):
            if not VALOR_DE_CONTAINS.match(a[len("--contains="):]):
                return False
        elif a.startswith("-"):
            return False
        else:
            padroes.append(a)
        i += 1
    return lista or not padroes


def livres_do_forge_check(args):
    """As palavras livres (subcomando e posicionais) do `forge-check`, sem `--raiz` e `--raiz-pedidos` e o valor delas."""
    livres, pular = [], False
    for a in args:
        if pular:
            pular = False
        elif abreviacao_de(a, ("--raiz", "--raiz-pedidos")):
            pular = "=" not in a  # o valor vem na palavra seguinte
        elif not a.startswith("-"):
            livres.append(a)
    return livres


def entrega_pela_forma_nova(livres, args):
    """`entrega --pedido`: o argparse aceita abreviação, então `--p`/`--ped` contam como `--pedido` (na dúvida, é a forma nova)."""
    return next(iter(livres), "") == "entrega" and any(a.startswith("--p") and "--pedido".startswith(a.split("=", 1)[0]) for a in args)


def so_leitura_no_entrega(args):
    """D4 (0.44.0): `--so-leitura` (ou a abreviação longa, `--so`), sem `=valor`: o `entrega --pedido` não grava nem roda os PQ cmd."""
    return any(abreviacao_de(a, ("--so-leitura",)) and "=" not in a for a in args)


def grava_no_pedido(livres, args):
    """A forma nova que grava no pedido: `brief selar` e `entrega --pedido` sem `--sem-gravar` nem `--so-leitura`. Só a abreviação
    longa (`--sem`, `--so`) conta como uma delas."""
    sub = next(iter(livres), "")
    if sub == "brief":
        return "selar" in livres[1:]
    if not entrega_pela_forma_nova(livres, args):
        return False
    return not (any(abreviacao_de(a, ("--sem-gravar",)) and "=" not in a for a in args) or so_leitura_no_entrega(args))


def prefixo_de(opcao, longa):
    """A opção é a `longa` ou uma abreviação dela que o argparse aceita (`--p` de `--para`)."""
    return len(opcao) >= 3 and longa.startswith(opcao)


def so_le(args, leitura):
    """S2/S8 (review da 0.44.1): o modo de leitura (`--ler`, `--confirmar`, com ou sem `=valor`) está na linha; sem ele, grava."""
    return any(prefixo_de(a.split("=", 1)[0], leitura) for a in args)


def opcao_curta_presente(args, letra, com_valor=""):
    """A opção curta `-<letra>` está na linha, sozinha ou agrupada (`-ze`, `-zze`), como o parse-options do git a lê: no
    grupo, a letra de `com_valor` leva o resto como valor (`-fe` é `--file e`) ou, sem resto, a palavra seguinte; `--`
    encerra as opções (segurança A8)."""
    proxima_e_valor = False
    for a in args:
        if proxima_e_valor:
            proxima_e_valor = False
        elif a == "--":  # o fim das opções: o que vem depois é palavra
            return False
        elif re.fullmatch(r"-[^-].*", a, re.S):
            for n, c in enumerate(a[1:], 2):
                if c == letra:
                    return True
                if c in com_valor:
                    proxima_e_valor = n == len(a)
                    break
    return False


def abreviacao_de(opcao, longas):
    """A opção longa (sem o `=valor`) é uma das `longas` ou a abreviação dela que o git aceita (`--upload-p`)."""
    nome = opcao.split("=", 1)[0]
    return nome.startswith("--") and len(nome) > 3 and any(o.startswith(nome) for o in longas)


def por_extenso(palavra):
    """A opção longa de `LONGAS_VIGIADAS` que `palavra` abrevia (com o `=valor`, se houver), ou a própria palavra."""
    nome, igual, valor = palavra.partition("=")
    if len(nome) < 4:  # `-`, `--` e as curtas
        return palavra
    inteira = next((o for o in LONGAS_VIGIADAS if o.startswith(nome)), None)
    return palavra if inteira is None else inteira + igual + valor


def opcao_de_merge_que_muda_o_resultado(args):
    """A3: a primeira opção do `git merge`/`pull` que troca a estratégia (`-s`, `-X`, também coladas e agrupadas, e as
    longas, abreviadas como o git aceita), faz `--squash` ou deixa o commit para depois (`--no-commit`); None se não há."""
    for a in args:
        if a.startswith("--"):
            if abreviacao_de(a, MERGE_OPCOES_QUE_MUDAM_O_RESULTADO):
                return a
        elif a.startswith("-"):
            for letra in a[1:]:
                if letra in "sX":
                    return a
                if letra in "mFS":  # o resto do grupo é o valor
                    break
    return None


def linhas_de_portao(texto):
    """O multiconjunto das linhas de `LINHA_DE_PORTAO` do texto (cada linha com a data, o arquivo e o hash dela)."""
    return collections.Counter(LINHA_DE_PORTAO.findall(texto)) if isinstance(texto, str) else collections.Counter()


def acrescenta_linha_de_portao(caminho, entrada, pasta):
    """M1: True se o Write/Edit/MultiEdit em `docs/pedidos/*.md` deixa alguma linha de `LINHA_DE_PORTAO` que não havia (o
    multiconjunto: trocar o arquivo, o hash ou o tipo da linha também conta; no Write, contra o arquivo de hoje; no Edit e no
    MultiEdit, `new_string` contra `old_string`). Arquivo ilegível vale vazio (falha fechada)."""
    alvo = os.path.normpath(os.path.join(str(pasta), os.path.expanduser(caminho)))
    if not re.search(r"(^|/)docs/pedidos/[^/]+\.md$", alvo):
        return False
    if "content" in entrada:
        try:
            antes = Path(alvo).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            antes = ""
        return bool(linhas_de_portao(entrada.get("content")) - linhas_de_portao(antes))
    edicoes = entrada.get("edits") if isinstance(entrada.get("edits"), list) else [entrada]
    edicoes = [edicao for edicao in edicoes if isinstance(edicao, dict)]
    novas, antigas = collections.Counter(), collections.Counter()
    for edicao in edicoes:
        novas += linhas_de_portao(edicao.get("new_string"))
        antigas += linhas_de_portao(edicao.get("old_string"))
    return bool(novas - antigas)


def emenda(args):
    """`git commit --amend`, também abreviado (`--am`, `--amen`: o git aceita o prefixo único da opção longa); depois do `--` é caminho."""
    args = args[:args.index("--")] if "--" in args else args
    return any(len(a) >= 4 and "--amend".startswith(a) for a in args)


def caminho_com_curinga_no_texto(caminho, texto):
    """A9 da E63.3: o caminho da política com `*` (`~/.forge-contrib/*/docs/pedidos/`) como o texto o cita, com o `~/`
    também pelo home real, ou None; o `*` casa um trecho sem barra, espaço nem aspas."""
    home = str(Path.home())
    for forma in ((caminho, caminho.replace("~", home, 1)) if caminho.startswith("~/") else (caminho,)):
        achado = re.search(re.escape(forma).replace(r"\*", r"[^/\s'\"]+"), texto)
        if achado:
            return achado.group(0)
    return None


def registrar_recusa(hook, chave, rid, grupo, alvo):
    """G4 F1: a recusa (`barrado`) ou o aviso (`teria_barrado`) numa linha do `comandos.jsonl`, com `fonte`, `grupo` e
    `alvo` (None é a recusa só pelo texto da linha: a recusa falsa a medir). Só na pasta `run` que já existe (não cria
    estado fora do projeto), achada só pelo disco (sem `git`: nada lento no caminho da recusa), sem seguir link nem
    esperar FIFO (`O_NONBLOCK`, e só grava em arquivo regular, como `anexar_ao_log`); a falha de gravação não muda a
    decisão."""
    try:
        run = hook._run
        if run is None:
            comum = diretorio_comum(hook.raiz)
            run = (comum.parent if comum is not None and comum.name == ".git" else hook.raiz) / ".forge" / "run"
            if not run.is_dir():
                run = comum / "forge" / "run"
        linha = {"hora": time.strftime("%Y-%m-%dT%H:%M:%S"), "sessao": hook.campo("session_id"),
                 "agente": hook.campo("agent_type"), "fonte": "conformidade", chave: rid, "grupo": grupo,
                 "alvo": None if alvo is None else str(alvo)[:300]}
        fd = os.open(run / "comandos.jsonl",
                     os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o666)
        try:
            if stat.S_ISREG(os.fstat(fd).st_mode):
                os.write(fd, (json.dumps(linha, ensure_ascii=False) + "\n").encode("utf-8"))
        finally:
            os.close(fd)
    except Exception:  # noqa: BLE001 - o registro é medida: sem pasta `run`, link ou erro, a decisão segue a mesma
        return


def perfil_iniciante(raiz):
    """`Hook.iniciante` no caminho da recusa (A2 da segurança no #885): a cópia principal sai só do disco
    (`diretorio_comum`, sem `git`) e o `.forge/perfil` abre sem esperar FIFO nem seguir link (`O_NONBLOCK`,
    `O_NOFOLLOW`); só arquivo regular vale, até 64 bytes. Ausente, especial ou ilegível: a próxima cópia, e no fim
    experiente. Só escolhe o texto: a recusa já está decidida."""
    comum = diretorio_comum(raiz)
    principal = comum.parent if comum is not None and comum.name == ".git" else Path(raiz)
    for base in dict.fromkeys((Path(raiz), principal)):
        try:
            fd = os.open(base / ".forge" / "perfil", os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
        except OSError:
            continue
        try:
            if stat.S_ISREG(os.fstat(fd).st_mode):
                return os.read(fd, 64).decode("utf-8").strip().lower() == "iniciante"
        except (OSError, ValueError):
            pass
        finally:
            os.close(fd)
    return False


class Guarda:
    def __init__(self, hook, politica, papel):
        self.h, self.pol, self.papel = hook, politica, papel
        self._ramo = None
        self._forge = None
        self.externo = None  # nome da sessão de outro projeto (prefixo `melhoria/<nome>-`), quando vem da raiz dela
        self.sessao_forge = False  # a raiz da sessão (`CLAUDE_PROJECT_DIR`) é um clone do Forge
        self.ambiente = {}   # GH_REPO e GIT_DIR definidos antes, na mesma linha de comando
        self.conferidas, self.conferencias = {}, 0  # orçamento da linha (`bash`)
        self.em_curso = set()  # textos em conferência num nível de dentro (PROFUNDIDADE-BASH-C)
        self.releituras = 0    # palavras com crase relidas na pilha: somam ao `nivel`, não à profundidade do shell
        self._repos = {}     # (raiz git, remoto) -> é o Forge
        self._regras = None  # `regras_do_forge`, lido uma vez por decisão (a raiz e o `externo` não mudam nela)
        self._raiz_home = None  # (realpath da raiz, realpath do home), uma vez por decisão
        self.linha = ""      # a linha de comando inteira, como veio (nível 0)
        self.texto_da_linha = None  # A9: o texto do nível em conferência, sem heredocs e com o rev-parse lido (só Bash)
        self.corpo_desconhecido = False  # A12 (E1.328): heredoc sem aspas do nível ou de fora com corpo que atribui
        self.opacos = 0  # A9: destinos opacos sem resto da linha (`TETO_DE_OPACOS`)
        self.rev_parse_misto = False  # A10: a linha tem rev-parse do .git em corpo de mais de um comando
        self.perguntas = []  # confirmações pendentes da linha (perfil iniciante)
        self.lancador_recusado = None  # lançador da linha que o hook não modela (`LANCADORES_RECUSADOS`), recusado no fim
        self.reavaliacao = None  # a primeira reavaliação pelo shell da linha, em qualquer nível (`reavaliacao`, opção B)
        self.trecho = None  # as palavras do comando simples em conferência (`segmento`), que a recusa cita
        self.parecer_pelo_bash = None  # 0.45.3: um parecer que a linha grava; só o Bash o recusa, no fim
        self.sem_leitura = False  # E16.1: a linha que o hook não lê (teto, ilegível); a `GuardaDaProva` volta ao texto
        leitura = politica.get("so_leitura")
        self.leitura = leitura if leitura and papel in leitura["papeis"] else None  # papel só de leitura (conferente)
        # 0.45.3: o aq tem a lista própria de comandos e grava pelas ferramentas de arquivo, só em `escrita_permitida`
        self.comandos_de_leitura = (leitura.get("comandos_por_papel", {}).get(papel, leitura["comandos"])
                                    if self.leitura else ())
        self.arquivo_pela_lista = bool(self.leitura) and papel in leitura.get("arquivos_por_escrita_permitida", [])

    # Respostas -------------------------------------------------------------------------------
    def pode(self, acao):
        return self.papel in self.pol["acoes"].get(acao, [])

    def barrar(self, rid, o_que, corrigir, simples=None, trava=None, alvo=None, grupo=None):
        """Recusa (saída 2). No perfil iniciante, `simples` (SIMPLES) troca o texto técnico pela consequência. `trava`
        (`TRAVA`, `TRAVA_OPACA`) só pesa na `GuardaDaProva` (`trava_da_sessao_do_forge`). G4 F1: o `grupo` (o ID da regra,
        se não vier) dá o modo em `modo_por_grupo`; só `avisar` deixa passar, com a forma certa no stderr. Nos dois modos,
        o `comandos.jsonl` ganha o grupo e o `alvo` (caminho, ref protegida ou destino opaco; None: só o texto da linha)."""
        grupo = grupo or rid
        modos = self.pol.get("modo_por_grupo")
        avisar = isinstance(modos, dict) and modos.get(grupo) == "avisar"
        if avisar:
            registrar_recusa(self.h, "teria_barrado", rid, grupo, alvo)
            print(mensagem(rid, f"aviso: teria barrado: {o_que}. Corrigir: {corrigir}"), file=sys.stderr)
            return
        texto = None
        try:  # a recusa já está decidida: o prazo vencido na escolha do texto cai no texto técnico, nunca no `prazo_vencido`
            if simples and perfil_iniciante(self.h.raiz):
                texto = SIMPLES[simples]
        except PrazoVencido:
            pass
        texto = texto or com_trecho(rid, o_que, corrigir, self.trecho)
        try:  # a recusa já está decidida: o registro grava depois dela, e o prazo vencido nele não a troca
            registrar_recusa(self.h, "barrado", rid, grupo, alvo)
        except PrazoVencido:
            pass
        bloquear(rid, texto)

    def perguntar(self, texto):
        """Só no perfil iniciante: o ato é legítimo mas arriscado; a pessoa confirma na janela de permissão, com a
        consequência (`permissionDecision: ask`). Vale só se nada na linha for recusado (a recusa vem antes)."""
        if self.h.iniciante() and not (texto in DISPENSA_NA_COPIA and self.worktree_temporaria()):
            self.perguntas.append(PERGUNTAS[texto])

    def worktree_temporaria(self):
        """Worktree vinculada em pasta temporária, com HEAD solto (cópia de review): descartar ou limpar arquivos ali não
        toca o trabalho da pessoa. Com branch, o `reset --hard` move a branch dela (os refs são comuns às cópias).
        Só vale para a linha que é UM ato simples (`git reset|clean|checkout|restore ...`): sem encadeamento, `$`, crase,
        `cd`, `-C`, `--work-tree`, `--git-dir`, `GIT_DIR`, `GIT_WORK_TREE`; na dúvida, pergunta."""
        if not UM_ATO_SIMPLES.fullmatch(self.linha) or ATO_FORA_DA_COPIA.search(self.linha):
            return False
        raiz = Path(os.path.realpath(self.h.raiz))
        if git(raiz, "symbolic-ref", "-q", "HEAD")[0] != 1:
            return False
        cod, comum = git(raiz, "rev-parse", "--git-common-dir")
        cod2, gitdir = git(raiz, "rev-parse", "--git-dir")
        if cod or cod2 or Path(os.path.realpath(raiz / comum)) == Path(os.path.realpath(raiz / gitdir)):
            return False
        temporarias = {os.path.realpath(tempfile.gettempdir()), os.path.realpath("/tmp")}
        return any(t in map(str, raiz.parents) for t in temporarias)

    def so_de(self, acao):
        quem = "/".join(self.pol["acoes"].get(acao, [])) or "só o usuário"
        return f"é de {quem}"

    # Caminhos --------------------------------------------------------------------------------
    def ramo_atual(self):
        if self._ramo is None:
            self._ramo = git(self.h.raiz, "branch", "--show-current")[1]
        return self._ramo

    def clone_do_forge(self):
        """A raiz em que o hook age é o Forge (dá poder: R-CONTRIB não se aplica). Projeto nunca é o Forge."""
        if self.externo is not None:
            return False
        if self._forge is None:
            self._forge = e_clone_do_forge(self.h.raiz)
        return self._forge

    def regras_do_forge(self):
        """Os caminhos `so_forge` valem: a raiz tem o manifesto do Forge. Só protege mais, então basta o arquivo."""
        if self._regras is None:
            self._regras = self.externo is None and tem_manifesto_do_forge(self.h.raiz)
        return self._regras

    @staticmethod
    def raiz_git(pasta):
        """Raiz da cópia de trabalho que contém a pasta (só disco), ou None."""
        alvo = Path(os.path.realpath(pasta))
        return next((d for d in (alvo, *alvo.parents) if (d / ".git").exists()), None)

    def repositorio_do_forge(self, pasta, remoto=None):
        """O repositório da pasta é o Forge, em qualquer pasta: o clone de contribuição, um clone do Forge (manifesto e
        sem `.forge/versao`) ou um repositório com remoto que aponta para o Forge (`git remote get-url`, que aplica o
        `insteadOf`; `remoto`: só ele, senão qualquer um, como o `gh` faz ao escolher o repositório)."""
        if em_contrib(pasta):
            return True
        raiz = self.raiz_git(pasta)
        if raiz is None:
            return False
        chave = (raiz, remoto)
        if chave not in self._repos:
            self._repos[chave] = e_clone_do_forge(raiz) or any(
                parecer.aponta_para_o_forge(url) or self.caminho_do_forge(raiz, url)
                for url in self.urls_dos_remotos(raiz, remoto))
        return self._repos[chave]

    @staticmethod
    def urls_dos_remotos(raiz, remoto=None):
        cod, saida = git(raiz, "remote")
        nomes = saida.split() if not cod else []
        if remoto is not None:
            nomes = [remoto] if remoto in nomes else []
        urls = []
        for nome in nomes:
            for push in ([], ["--push"]):
                cod, saida = git(raiz, "remote", "get-url", "--all", *push, nome)
                urls += saida.splitlines() if not cod else []
        return urls

    def caminho_do_forge(self, base, url):
        """Segurança A9: o destino é caminho local (ou `file://`) em `~/.forge-contrib` ou num clone do Forge."""
        local = url[7:] if url.startswith("file://") else None if re.match(r"[\w+.-]+://|[^/]*:", url) else url
        if not local:
            return False
        alvo = self.caminho(Path(base), local)
        return em_contrib(alvo) or e_clone_do_forge(self.raiz_git(alvo))

    def destino_na_config(self, pasta):
        """Segurança A7: sem remoto na linha, `branch.<b>.pushRemote`, `remote.pushDefault` e `branch.<b>.remote`
        gravados escolhem o destino e aceitam URL. Devolve a chave que aponta ao Forge ou, se a leitura falha, o texto
        da dúvida (falha fechado; o prazo vencido do git já bloqueia o envio, ADR 0009); senão None. O remoto nomeado já
        passa pela URL dele (`repositorio_do_forge`)."""
        if (raiz := self.raiz_git(pasta)) is None:
            return None
        cod, saida = git(raiz, "config", "--get-regexp", r"^(branch\..*\.(remote|pushremote)|remote\.pushdefault)$")
        if cod not in (0, 1):
            return "a configuração do envio, ilegível"
        for linha in saida.splitlines():
            chave, _, valor = linha.partition(" ")
            if parecer.aponta_para_o_forge(valor) or self.caminho_do_forge(raiz, valor):
                return chave
        return None

    @staticmethod
    def caminho(pasta, texto):
        """Destino de `cd`/`-C`/`--git-dir`: expande `~` e variáveis de ambiente, como o shell faria."""
        return pasta / expandir_home(os.path.expandvars(texto))

    def alvo_do_forge(self, pasta, repo=None, remoto=None):
        """R-CONTRIB: o comando da sessão de OUTRO projeto (raiz que não é o Forge) atinge o repositório do Forge:
        `repo` aponta para ele ou, sem `repo`, o repositório da pasta é o Forge (`repositorio_do_forge`)."""
        if self.clone_do_forge():
            return False
        return parecer.aponta_para_o_forge(repo) if repo else self.repositorio_do_forge(pasta, remoto)

    def caminho_barrado(self, caminho):
        """(rid, o quê, como corrigir) se o `caminho` (já resolvido) é protegido para o papel; senão None."""
        if MARCA_DA_SUITE.fullmatch(caminho.name):  # S8 (C-1, C-2): antes de política, papel e sessão; nome resolvido
            return PROVA_DA_SUITE
        if self._raiz_home is None:
            self._raiz_home = Path(os.path.realpath(self.h.raiz)), Path(os.path.realpath(Path.home()))
        raiz, home = self._raiz_home
        posix = caminho.as_posix()
        formas = []
        if (rel := relativo_ao_pai(posix, raiz)) is not None:
            formas.append(("proj", rel))
        if (rel := relativo_ao_pai(posix, home)) is not None:
            formas.append(("home", "~/" + rel))
        # B1 da 0.43.1: ~/.forge-contrib como link para fora do home. A forma pelo link só BARRA (regras `caminhos`);
        # nunca entra na lista de escrita, que continua recusando o que fica fora do home.
        pelo_link = [("home", f"~/{nome}/" + rel if rel != "." else f"~/{nome}") for nome, alvo_link in self.links_do_home(home)
                     if (rel := relativo_ao_pai(posix, alvo_link)) is not None]
        no_claude_do_home = relativo_ao_pai(posix, home / ".claude") is not None
        do_home = [r for t, r in [*formas, *pelo_link] if t == "home"]  # fora do laço das regras (custo por arquivo)
        do_proj = [r for t, r in formas if t == "proj"]
        for e in self.pol["caminhos"]:
            c = e["caminho"]
            if c.startswith("~/"):
                achou = any(casa(r, c) for r in do_home)
            elif e.get("so_forge") and not self.regras_do_forge():
                continue
            else:
                achou = any(casa(r, c) for r in do_proj) or (
                    not e["quem"] and not no_claude_do_home and em_qualquer_lugar(posix, c)) or (
                    c in PELA_COPIA_PRINCIPAL and em_qualquer_lugar(posix, c)  # sem a pasta no texto, sem ler o disco
                    and any(casa(r, c) for r in self.relativos_a_copia_principal(posix)))
            if not achou:
                continue
            if self.papel in e["quem"]:
                if e.get("branch") and not self.ramo_atual().startswith(e["branch"]):
                    return ("R-CONFORMIDADE", f"{e['motivo']} (branch atual: {self.ramo_atual() or 'solta'})",
                            f"crie uma branch {e['branch']}*")
                continue
            if not e["quem"]:
                return ("R-CONFORMIDADE", f"{e['motivo']}: {c}",
                        f"só o usuário altera; proponha o diff (R-DECISAO); {SUGESTAO}", "instalacao")
            return ("R-CONFORMIDADE", f"{e['motivo']}: {c} (papel: {self.papel})",
                    f"peça a {'/'.join(e['quem'])}")
        if posix.endswith("/.forge/perfil") and self.h.iniciante():
            return ("R-CONFORMIDADE", "o perfil iniciante (.forge/perfil) não é mudado por agente",
                    f"só o usuário muda o perfil, à mão; {SUGESTAO}", "perfil")
        fora_da_lista = self.fora_da_lista_de_escrita(caminho, formas)
        if fora_da_lista:
            return fora_da_lista
        no_manifesto = any(t == "proj" and casa(r, MANIFESTO) for t, r in formas)
        if no_manifesto and not self.sessao_forge and self.raiz_e_projeto():
            return ("R-CONTRIB", f"manifesto de plugin no projeto ({MANIFESTO}): só a sessão do Forge escreve",
                    "proponha a mudança ao usuário (R-DECISAO)")
        return None

    def relativos_a_copia_principal(self, posix):
        """[caminho relativo à cópia principal] do `posix` resolvido, ou []: a cópia principal é a pasta comum `.git`
        da raiz lida do disco (`diretorio_comum`, o cálculo do `fontes` do hook ordens); nu ou `.git` que não se resolve,
        nenhuma (A2 da segurança E123.8: o dev na worktree grava a cópia principal pelo caminho absoluto ou por `../`)."""
        comum = diretorio_comum(self.h.raiz)
        if comum is None or comum.name != ".git":
            return []
        rel = relativo_ao_pai(posix, comum.parent)
        return [] if rel is None else [rel]

    def links_do_home(self, home):
        """(nome, realpath do alvo) de cada pasta do home citada nas regras `~/X/...` que é link para fora do home."""
        if getattr(self, "_links_do_home", None) is None:
            nomes = {e["caminho"][2:].split("/", 1)[0] for e in self.pol["caminhos"] if e["caminho"].startswith("~/")}
            links = []
            for nome in sorted(n for n in nomes if n and "*" not in n):
                alvo = Path(os.path.realpath(home / nome))
                if (home / nome).is_symlink() and home not in {alvo, *alvo.parents}:
                    links.append((nome, alvo))
            self._links_do_home = links
        return self._links_do_home

    def fora_da_lista_de_escrita(self, caminho, formas):
        """Papel com `escrita_permitida` (ADR 0009, seção 6): escreve só nos caminhos da lista, pelo caminho normalizado.
        Entrada `~/...` vale a partir do home; as demais, a partir da raiz do projeto ou da raiz de uma cópia do Forge
        que contém o arquivo (worktree em `~/.forge-contrib/`; qualquer outro repositório não vale). Fora disso,
        recusa: a lista só nega mais, nunca libera o que `caminhos` barra."""
        lista = self.pol.get("escrita_permitida", {}).get(self.papel)
        if lista is None:
            return None
        topo = self.raiz_git(caminho.parent)
        if topo and topo in {caminho, *caminho.parents} and e_clone_do_forge(topo) and (
                em_contrib(topo) or topo == Path(os.path.realpath(self.h.raiz or raiz_declarada()))):
            formas = [*formas, ("proj", caminho.relative_to(topo).as_posix())]
        if any(casa(r, c) for c in lista for t, r in formas if t == ("home" if c.startswith("~/") else "proj")):
            return None
        return ("R-CONFORMIDADE", f"o papel {self.papel} escreve só em {', '.join(lista)}: {caminho.as_posix()}",
                "grave o estudo ou parecer nesses caminhos; o resto é de outro papel (R-DECISAO)")

    def raiz_e_projeto(self):
        return (Path(self.h.raiz) / ".forge" / "versao").is_file()

    def resolver(self, caminho, pasta):
        p = Path(expandir_home(caminho))
        return Path(realpath_pela_pasta(str(p if p.is_absolute() else pasta / p)))

    def checar_escrita(self, caminho, pasta, parecer_conta=True):
        """Na dúvida, recusa: o que vem depois de uma substituição (`$(git rev-parse --show-toplevel)/docs/reviews/x`) é
        conferido também a partir da raiz do projeto. Pelo Bash, o parecer recusa depois da regra do caminho (0.45.3);
        `parecer_conta=False` no `git` e na remoção."""
        if MARCA_DA_SUITE.fullmatch(Path(caminho).name):  # S8 (C-2): o nome literal, antes da expansão
            self.barrar(*PROVA_DA_SUITE)
        alvos = self.alvos_da_escrita(caminho, pasta)
        self.curinga_na_prova(Path(caminho).name, self.pastas_do_curinga(caminho, pasta))
        for alvo in alvos:
            achado = self.caminho_barrado(alvo)
            if achado and alvo == self.resto_no_git(caminho, pasta) != alvos[0]:  # QA A1: o falso positivo se explica
                achado = (achado[0], f"valor de $(…), crase ou variável que o hook não sabe, lido como .git (use o caminho "
                                     f"literal se não for): {achado[1]}", *achado[2:])
            if achado:
                self.barrar(*achado, alvo=alvo)
        self.destino_opaco(caminho, pasta)  # A9: depois das regras do caminho, que falam primeiro
        for alvo in alvos:  # o Bash recusa no fim da linha (`parecer_pelo_bash`), depois das regras específicas dela
            if parecer_conta and e_parecer(alvo):
                self.parecer_pelo_bash = alvo

    def fim_do_opaco(self, caminho, pasta):
        """A9: (expandido, fim da última parte opaca) se o valor do caminho, no Bash, depende de `$(…)`, crase ou variável
        que o hook não resolve (U0: `expandir`); senão None. Write e Edit não entram: lá o caminho é literal."""
        if self.texto_da_linha is None:
            return None
        expandido = self.expandir(caminho, pasta)
        fins = [m.end() for m in SO_VARIAVEL.finditer(expandido)]
        if "$(" in expandido:
            fins.append(expandido.rfind(")") + 1)
        return (expandido, max(fins)) if fins else None

    def opaco_sem_resto(self, caminho, pasta):
        """A9: o caminho é opaco e nada vem depois da última parte opaca além de `/`."""
        opaco = self.fim_do_opaco(caminho, pasta)
        return bool(opaco) and not opaco[0][opaco[1]:].strip("/")

    def textos_do_valor(self, palavra):
        """(precisos, largos): o texto que produz o valor da palavra. Precisos: a palavra, os corpos de substituição da
        linha quando ela os perdeu (`$(…)` sem aspas, crase partida) e o valor de cada `nome=` da linha que ela usa.
        Largos: mais a linha inteira se a variável nasce de outro jeito (`for d in`, `read d`) ou se o texto chama uma
        função definida na linha (U0 e U1)."""
        linha, palavra = juntar_continuacoes(self.texto_da_linha), juntar_continuacoes(palavra)  # A4 do QA E1.329
        precisos, nomes, largo = [palavra], set(), False
        if OPACO["$"] in palavra or palavra.count("`") % 2:
            precisos += [f"$({c})" for c in corpos_de_substituicao(linha)]  # inteiras: o aninhado segue à vista
        for texto in precisos:  # cresce enquanto o valor de uma variável usa outra
            for nome in set(re.findall(r"\$\{?(\w+)", texto)) - nomes:
                nomes.add(nome)
                precisos += [valor_atribuido(linha, m.end()) for m in re.finditer(rf"(?<![\w$]){nome}\+?=", linha)]
                largo |= bool(re.search(rf"(?<![\w${{]){nome}(?![\w+=])", linha))
        funcoes = (re.findall(r"(?<![\w$-])([\w.-]+)\s*\(\s*\)", linha)
                   + re.findall(r"(?<![\w$.-])function\s+([\w.-]+)", linha))  # D2b: `function f {` sem `()`
        largo |= any(re.search(rf"(?<![\w.-]){re.escape(f)}(?![\w.-])", t) for f in funcoes for t in precisos)
        return precisos, precisos + [linha] if largo else precisos

    def destino_opaco(self, caminho, pasta):
        """A9 (E1.139, v047): o destino opaco sem resto recusa quando o texto que produz o valor cita o diretório do git
        (U1) ou quando o hook não o lê (U2: aninhado, `eval`, `sh -c`, `$'…'`, barra invertida). Acima de
        `TETO_DE_OPACOS` por linha, recusa como ilegível (C21)."""
        if not self.opaco_sem_resto(caminho, pasta):
            self.resto_colado(caminho, pasta)
            return
        self.opacos += 1
        if self.opacos > TETO_DE_OPACOS:
            self.barrar("R-CONFORMIDADE", f"mais de {TETO_DE_OPACOS} destinos de $(…), crase ou variável na linha: o hook "
                                          "não os lê", "separe em comandos menores, com o caminho literal")
        precisos, largos = self.textos_do_valor(caminho)
        if any(cita_o_dir_do_git(t) or cita_o_dir_do_git(palavra_juntada(t)) for t in largos):
            motivo = "o texto que produz o valor cita o diretório do git (.git)"
        elif any(CORPO_ILEGIVEL.search(t) for t in precisos) or any(
                "$(" in c or "`" in c for t in precisos for c in corpos_de_substituicao(t)):
            motivo = "o hook não lê o texto que produz o valor (aninhado, eval, sh -c, $'…' ou barra invertida)"
        else:
            return self.valor_calculado(self.expandir(caminho, pasta))
        self.barrar("R-CONFORMIDADE", f"destino de $(…), crase ou variável sem nada depois: {motivo}",
                    "escreva o caminho literal do destino", alvo=caminho)

    def resto_colado(self, caminho, pasta):
        """A2 (volta da E1.232): o resto colado sem barra (`"$(echo .g)it/config"`, `"${X:-.g}it"`) vale pelo U4; o U1
        da linha não (`"$(echo .git)x"` é `.gitx`), e o resto com barra é do `resto_no_git`."""
        expandido, fim = self.fim_do_opaco(caminho, pasta) or ("", 0)
        if expandido[fim:fim + 1] not in ("", "/"):
            self.valor_calculado(expandido)

    def valor_calculado(self, palavra):
        """U4 (volta da E1.232): libera só o valor que o hook calcula (`valores_da_palavra`) e que não cai no `.git`."""
        # A3 do QA E1.325: o `replace` juntava `\\` + quebra; A12 (E1.328): corpo de heredoc que atribui
        linha = None if self.corpo_desconhecido else linha_juntada(self.texto_da_linha)
        valores = None if linha is None else valores_da_palavra(palavra, linha)
        if valores is not None and not valor_no_git(valores):
            return
        motivo = ("o valor que o hook calcula cai no diretório do git (.git)" if valores else "o hook só libera o "
                  "valor que calcula (mktemp, date, pwd, true, git rev-parse --show-toplevel, --short ou "
                  "--abbrev-ref, echo ou printf %s de palavras literais)")
        self.barrar("R-CONFORMIDADE", f"destino de $(…), crase ou variável: {motivo}",
                    "escreva o caminho literal do destino")

    def origem_do_git_no_opaco(self, args, pasta):
        """A9, U3: `cp`, `mv`, `install` e `ln` com destino opaco sem resto e origem com nome do git ou de hook (C18)
        recusam, salvo quando o corpo é um da lista positiva (`CORPO_POSITIVO`: `mktemp`, `date`, `pwd`,
        `git rev-parse --show-toplevel`)."""
        alvo = next((args[i + 1] for i, a in enumerate(args[:-1]) if a in ("-t", "--target-directory")), None)
        alvo = alvo or next((a.split("=", 1)[1] for a in args if a.startswith("--target-directory=")), None)
        alvo = alvo or next((a for a in reversed(args) if not a.startswith("-") or "`" in a), None)
        if not alvo or not self.opaco_sem_resto(alvo, pasta) or self.corpo_positivo(alvo):
            return
        nomes = [Path(a.rstrip("/")).name for a in args if not a.startswith("-") and a != alvo]
        achado = next((n for n in nomes if nome_da_c18(n)), None)
        if achado:
            self.barrar("R-CONFORMIDADE", f"origem `{achado}` (nome do git ou de hook) para destino de $(…), crase ou "
                                          "variável que o hook não lê", "escreva o caminho literal do destino")

    def corpo_positivo(self, palavra):
        """U3: a palavra é uma substituição só (direta ou pela única atribuição da variável na linha) cujo corpo está na
        lista positiva; a substituição sem aspas vale se todos os corpos da linha estiverem."""
        linha, m = self.texto_da_linha, UNIDADE_OPACA.fullmatch(palavra.rstrip("/"))
        if m and m["nome"]:
            valores = [valor_atribuido(linha, a.end()) for a in re.finditer(rf"(?<![\w$]){m['nome']}=", linha)]
            outro = re.search(rf"(?<![\w${{]){m['nome']}(?![\w=])", linha)
            m = UNIDADE_OPACA.fullmatch(valores[0].strip("\"'")) if len(valores) == 1 and not outro else None
        if not m or m["nome"]:
            return False
        corpo = m["sub"] if m["sub"] is not None else m["crase"]
        corpos = corpos_de_substituicao(linha) if corpo == "…" else [corpo]
        return bool(corpos) and all(na_lista_positiva(c.strip(), linha) for c in corpos)

    def alvos_da_escrita(self, caminho, pasta):
        """O caminho resolvido, o resto que cai no `.git` (`resto_no_git`) e, depois de uma substituição (`$(…)/x`), o resto
        resolvido a partir da raiz do projeto."""
        alvos = [self.resolver(self.expandir(caminho, pasta), pasta)]
        no_git = self.resto_no_git(caminho, pasta)
        alvos = [*alvos, no_git] if no_git else alvos
        resto = caminho.rsplit(OPACO["$"], 1)[1].lstrip("/") if OPACO["$"] in caminho else ""
        return [*alvos, self.resolver(resto, Path(self.h.raiz))] if resto else alvos

    def resto_no_git(self, caminho, pasta):
        """E20.6 (A2 da segurança, v046): o hook não sabe o valor de `$(…)`, da crase nem de variável. Se o resto depois do
        último deles começa por um nome do diretório do git (`NOMES_DO_GIT` ou o que existe no diretório comum), devolve o mesmo
        resto dentro do `.git` da raiz, que as regras `.git/…` barram; senão None (`$(pwd)/docs/x` segue livre)."""
        expandido = self.expandir(caminho, pasta)
        fins = [m.end() for m in SO_VARIAVEL.finditer(expandido)]
        if SUBSTITUICAO.search(expandido):  # `$(…)` (opaca ou, entre aspas, com o texto dentro): até o último `)`
            fins.append(expandido.rfind(")") + 1)
        if not fins:
            return None
        partes = Path(expandido[max(fins, default=0):].lstrip("/")).parts
        if not partes or partes[0] not in self.nomes_do_git(pasta):
            return None
        return Path(os.path.realpath(self.h.raiz)) / ".git" / Path(*partes)

    def nomes_do_git(self, pasta):
        """`NOMES_DO_GIT` mais o que existe no diretório comum do git da pasta (lido do disco)."""
        topo = self.raiz_git(pasta)
        comum = topo and diretorio_comum(topo)
        return NOMES_DO_GIT | set(os.listdir(comum)) if comum else NOMES_DO_GIT

    def pastas_do_curinga(self, caminho, pasta, opaco=False):
        """S8 (E5a/C-2, A1 da segurança g1-r2): onde o bash expande o curinga do nome, igual na escrita, na origem de
        link e no fallback: as pastas dos alvos e, com `$(…)` ou variável (`opaco`), o diretório comum do git."""
        topo = self.raiz_git(pasta) if opaco or VARIAVEL.search(caminho) else None
        return [a.parent for a in self.alvos_da_escrita(caminho, pasta)] + [topo and diretorio_comum(topo)]

    def curinga_na_prova(self, nome, pastas):
        """S8 (E5a/C-2, A1 e A2 da segurança g1): com `*`, `?` ou `[` no nome, o hook expande o nome nas pastas onde o
        alvo cai, como o bash fará, e barra se algum nome expandido casar a prova da suíte."""
        if CURINGA.search(nome) and any(MARCA_DA_SUITE.fullmatch(Path(n).name)
                                        for p in filter(None, pastas) for n in glob.glob(f"{glob.escape(str(p))}/{nome}")):
            self.barrar(*PROVA_DA_SUITE)

    def expandir(self, caminho, pasta):
        """`$PWD`, `$CLAUDE_PROJECT_DIR`, `$HOME` e `DIR_DO_GIT` (com ou sem chaves; as aspas o shlex já tirou; também a
        variável da linha atribuída ao `DIR_DO_GIT`) viram o caminho real."""
        if "$" not in caminho:  # sem `$`, nada a expandir (a crase que `VARIAVEL` casa volta igual): custo por arquivo
            return caminho
        caminho = VARIAVEL_INTEIRA.sub(lambda m: v if DIR_DO_GIT in (v := self.ambiente.get(m[1] or m[2], "")) else m[0],
                                       caminho)
        valores = {"PWD": str(pasta), "CLAUDE_PROJECT_DIR": str(self.h.raiz), "HOME": str(Path.home()),
                   DIR_DO_GIT: str(Path(os.path.realpath(self.h.raiz)) / ".git")}
        return VARIAVEL.sub(lambda m: valores.get(m.group(1), m.group(0)), caminho)

    def link_em_protegido(self, args, pasta):
        """N3 (IMPL-FURO-HOOK-N, 0.45.1): `ln` e `cp -l|-s|--link|--symbolic-link` com origem ou destino num caminho
        protegido recusam para todo papel, mesmo o dono do caminho: o link físico dá ao arquivo protegido um nome livre, e o
        link criado dentro da pasta protegida (o brief) aponta para um arquivo que qualquer papel edita depois. O destino
        que é pasta (também o de `-t` e `--target-directory=`) recebe o nome da origem, e ele também é conferido."""
        caminhos = [a.split("=", 1)[1] if a.startswith("--target-directory=") else a for a in args
                    if not a.startswith("-") or a.startswith("--target-directory=")]
        alvos = [self.resolver(self.expandir(a, pasta), pasta) for a in caminhos]
        alvos += [d / Path(a).name for d in alvos if d.is_dir() for a in caminhos]
        generico = next((f"{e['motivo']}: {e['caminho']}" for e in self.pol["caminhos"] if e["caminho"] == ".git/"), None)
        papel, self.papel = self.papel, "-"  # nenhum papel: vale o caminho protegido para qualquer um
        try:
            livres = self.origens_do_rev_parse(args, caminhos, pasta, generico)  # os derivados acima nunca entram
            achado = next((x for i, x in enumerate(map(self.caminho_barrado, alvos))
                           if x and not (i in livres and x[1] == generico)), None)
        finally:
            self.papel = papel
        if not achado and any(self.fim_do_opaco(a, pasta) and any(map(cita_o_dir_do_git, self.textos_do_valor(a)[1]))
                              for a in caminhos):  # A10: opaco (com ou sem resto) que cita o diretório do git
            achado = ("R-CONFORMIDADE", "valor de $(…), crase ou variável que o hook não lê e que cita o diretório do git")
        if achado:
            motivo = achado[1].replace(" (papel: -)", "")
            self.barrar("R-CONFORMIDADE", f"link com caminho protegido ({motivo}): o link dá outro nome ao arquivo",
                        "copie o conteúdo sem link (cp sem -l nem -s) ou peça ao dono do caminho (R-DECISAO)")

    def origens_do_rev_parse(self, args, caminhos, pasta, generico):
        """Volta 3 (A1 da E20.29, v046): os índices em `caminhos` das origens de link que vêm de `git rev-parse` (direto ou
        pela variável da linha). Ler do `.git` para fora era livre na develop (a substituição era opaca) e segue livre só da
        regra genérica `.git/`; as específicas (`.git/config`, `.git/hooks/`, `.git/forge/`) e o destino seguem barrando.
        Falha fechada: com opção que não seja `-` e letras sem valor (`-S`, `-t`, as longas e `--` mudam qual palavra é o
        destino), nenhuma; a última palavra (o destino, também a de `ln <origem>` sozinha) nunca entra; nem a origem cujo
        curinga ou chaves alcança uma regra específica (`origem_so_generica`)."""
        if self.rev_parse_misto or any(a.startswith("-") and not re.fullmatch(r"-[^-St=]+", a) for a in args):
            return set()  # A10: com rev-parse de mais de um comando na linha, nenhuma
        valores = (VARIAVEL_INTEIRA.sub(lambda m: self.ambiente.get(m[1] or m[2], m[0]), a) for a in caminhos[:-1])
        return {i for i, v in enumerate(valores) if DIR_DO_GIT in v and self.origem_so_generica(v, pasta, generico)}

    def origem_so_generica(self, valor, pasta, generico):
        """Volta 4 (A11 da segurança E20.31, A4 do QA E20.32, v046): o resto depois do `DIR_DO_GIT` com chaves
        (`conf{i,}g`) não se libera (o hook não expande chaves: falha fechada); com curinga (`c?nfig`, `hook[s]/pre-push`),
        só se nenhum nome que o glob de cada prefixo do resto expande no `.git` da raiz e no diretório comum (o de
        `pastas_do_curinga`) cair em regra que não seja a genérica `.git/`. Volta 5 (A11 da segurança E20.37, A1 do review
        E20.36): o glob do Python não lê o colchete do bash (`[^x]`, `[[:alpha:]]`, `[[=c=]]`, `[[.c.]]`), então resto com
        `[` também não se libera, salvo o colchete só de dígitos (`[0-9]`, que os dois leem igual); com `?` e `*`, cada letra
        casa as duas caixas (`shopt -s nocaseglob` com `CONFI?`)."""
        resto = valor.rsplit(DIR_DO_GIT, 1)[1].lstrip("}").strip("/")
        if "{" in resto:
            return False
        if "[" in COLCHETE_DE_DIGITO.sub("", resto):
            return False
        if not CURINGA.search(resto):
            return True
        git = Path(os.path.realpath(self.h.raiz)) / ".git"
        topo = self.raiz_git(pasta)
        partes = sem_caixa(resto).split("/")
        for base in {str(b) for b in filter(None, (git, topo and diretorio_comum(topo)))}:
            for k in range(1, len(partes) + 1):
                for n in glob.glob(f"{glob.escape(base)}/{'/'.join(partes[:k])}"):
                    x = self.caminho_barrado(Path(os.path.normpath(git / os.path.relpath(n, base))))
                    if x and x[1] != generico:
                        return False
        return True

    def find(self, args, pasta, nivel, atribuicoes):
        """A2 da segurança (v0478): o `find` escreve por opção. `-delete` apaga os pontos de partida e o que há dentro (escrita
        e remoção do ancestral, como o `rm -r`; a raiz fica de fora, como no `rm`); `-exec`, `-execdir`, `-ok` e `-okdir`
        rodam o comando com `{}` trocado por cada ponto de partida; `-fprint*` e `-fls` gravam no arquivo seguinte."""
        i = 0
        while i < len(args) and re.fullmatch(r"-[HLP]|-D|-O\d*", args[i]):
            i += 2 if args[i] == "-D" else 1
        partidas = []
        while i < len(args) and not re.match(r"[-(!)]", args[i]):
            partidas.append(args[i])
            i += 1
        partidas, expressao = partidas or ["."], args[i:]
        for j, a in enumerate(expressao):
            if a == "-delete":
                for p in partidas:
                    self.checar_escrita(p, pasta, parecer_conta=False)
                    self.checar_remocao(p, pasta)
            elif a in FIND_GRAVA and j + 1 < len(expressao):
                self.checar_escrita(expressao[j + 1], pasta)
            elif a in FIND_EXECUTA:
                fim = next((k for k in range(j + 1, len(expressao)) if expressao[k] in (";", "+")), len(expressao))
                for p in partidas:
                    self.aninhado(shlex.join(c.replace("{}", p) for c in expressao[j + 1:fim]), pasta, nivel, atribuicoes)

    def checar_remocao(self, caminho, pasta, ato="apagar"):
        """`rm -rf .forge`, `rm -r .githooks`: apagar a pasta que contém um caminho protegido sem dono (a instalação) é
        o mesmo que apagar o arquivo. A raiz do projeto e as pastas acima dela ficam de fora (`rm` de worktree).
        `$PWD` e `$CLAUDE_PROJECT_DIR` são expandidos; outra variável antes de uma pasta protegida (`$X/.forge`) não
        dá para resolver, então recusa (variável sozinha, `rm -rf $X`, é limite aceito: o sandbox é a garantia)."""
        caminho = self.expandir(caminho, pasta)
        if VARIAVEL.search(caminho):
            if PASTAS_PROTEGIDAS & set(Path(caminho).parts):
                self.barrar("R-CONFORMIDADE", f"apagar {caminho} com variável no caminho pode apagar a instalação do Forge",
                            f"use o caminho sem variável, ou deixe ao usuário (R-DECISAO); {SUGESTAO}", "instalacao")
            return
        home = Path(os.path.realpath(Path.home()))
        alvo = self.resolver(caminho, pasta)
        # O critério é o caminho protegido, não a raiz do cwd: vale a raiz da sessão e a do repositório que contém o alvo.
        raizes = {Path(os.path.realpath(self.h.raiz)), *filter(None, [self.raiz_git(alvo)])}
        for e in self.pol["caminhos"]:
            c = e["caminho"]
            if e["quem"]:
                continue
            fora = [a.parent for n, a in self.links_do_home(home) if c.startswith(f"~/{n}/") or c == f"~/{n}"]
            for dentro in ([home, *fora] if c.startswith("~/") else raizes):
                protegido = home / c[2:] if c.startswith("~/") else dentro / c
                if alvo != dentro and dentro in alvo.parents and alvo in Path(os.path.realpath(protegido)).parents:
                    self.barrar("R-CONFORMIDADE", f"{ato} {alvo.name}/ {'apaga' if ato == 'apagar' else 'alcança'} {c}: "
                                f"{e['motivo']}",
                                f"só o usuário altera; proponha o diff (R-DECISAO); {SUGESTAO}", "instalacao", alvo=alvo)

    def checar_texto(self, texto):
        """Escrita em caminho protegido com o caminho em literal dentro de `python -c`, `node -e`, script."""
        if not ESCRITA_NO_TEXTO.search(texto):
            return
        if any(MARCA_DA_SUITE.fullmatch(Path(t).name) for t in re.split(r"[\s'\"(),;=]+", texto)):  # S8
            self.barrar(*PROVA_DA_SUITE)
        raiz = Path(os.path.realpath(self.h.raiz))
        for e in self.pol["caminhos"]:
            c = e["caminho"]
            if "*" in c:  # A9 da E63.3: o `*` da política casa um trecho sem barra no texto
                if c.rsplit("*", 1)[1] not in texto:  # o fim depois do `*` antes da busca: custo do corpus
                    continue
                c = caminho_com_curinga_no_texto(c, texto) or c  # sem o trecho, o `*` literal não casa abaixo
            literais = (c.replace("~", str(Path.home()), 1), c) if c.startswith("~/") else (c,)
            if any(lit in texto for lit in literais):
                achado = self.caminho_barrado(self.resolver(c.replace("~", str(Path.home()), 1) if c.startswith("~/")
                                                            else c, raiz))
                if achado:
                    self.barrar(*achado)

    # Write, Edit, MultiEdit, NotebookEdit -------------------------------------------------------
    def arquivo(self, entrada):
        if self.leitura and not self.arquivo_pela_lista:
            self.barrar("R-CONFORMIDADE", f"escrita de arquivo pelo papel só de leitura ({self.papel})", DICA_LEITURA)
        caminho = entrada.get("file_path") or entrada.get("notebook_path")
        if isinstance(caminho, str) and caminho:
            self.checar_escrita(caminho, self.h.cwd())
            if acrescenta_linha_de_portao(caminho, entrada, self.h.cwd()):
                self.barrar("R-CONFORMIDADE", "linha `brief selado` ou `entrega conferida` escrita à mão no pedido",
                            "quem grava é a ferramenta: `forge-check brief selar` e `forge-check entrega --pedido`")

    # Bash ----------------------------------------------------------------------------------------
    def bash(self, comando, pasta, nivel=0, so_substituicoes=False, corpo_de_heredoc=False):
        """Confere a linha. `so_substituicoes`: a linha é uma palavra entre aspas (`"$(git log)"`), e só o conteúdo das
        substituições dela é comando. `corpo_de_heredoc`: a linha é o corpo de um heredoc que vai a um programa fora da
        lista dos que só o leem (a recusa por ilegível diz como passar o texto por arquivo). Orçamento por linha (a
        linha adversária de crases e `cd` aninhados refaria a mesma conferência milhares de vezes e estouraria o
        timeout do hook, que o Claude Code trata como liberado): o mesmo (corpo, pasta, nível, ambiente) não é
        conferido duas vezes, e a linha é recusada acima de
        `TETO_DE_CONFERENCIAS` conferências, de `TETO_DE_CARACTERES` caracteres conferidos ao todo ou de
        `PRAZO_DA_LINHA_S` segundos."""
        if nivel == 0 and CITA_PORTAO.search(comando) and ESCRITA_NA_LINHA.search(comando):
            self.barrar("R-CONFORMIDADE", "linha `brief selado` ou `entrega conferida` escrita pelo Bash",
                        "quem grava é a ferramenta: `forge-check brief selar` e `forge-check entrega --pedido`")
        if nivel == 0:
            self.conferidas, self.conferencias, self.caracteres, self.em_curso, self.releituras = {}, 0, 0, set(), 0
            self.reavaliacao = None
            self.prazo = time.monotonic() + PRAZO_DA_LINHA_S
            self.opacos, self.rev_parse_misto = 0, rev_parse_de_varios_comandos(comando)
        chave = (comando, pasta, nivel, self.releituras, so_substituicoes, corpo_de_heredoc,
                 tuple(sorted(self.ambiente.items())))
        if chave in self.conferidas:
            self.ambiente = dict(self.conferidas[chave])  # o resultado é o mesmo que a primeira conferência deixou
            return
        # PROFUNDIDADE-BASH-C: a palavra com crase relida dá o mesmo texto (`x=`…``), um nível abaixo; o texto já em
        # conferência num nível de dentro decide igual (só o nível 0 tem regras próprias): sem isso, o teto o recusaria.
        releitura = chave[:2] + chave[4:]
        if nivel > 1 and releitura in self.em_curso:
            return
        self.conferencias += 1
        self.caracteres += len(comando)
        if (self.conferencias > TETO_DE_CONFERENCIAS or self.caracteres > TETO_DE_CARACTERES
                or time.monotonic() > self.prazo):
            self.barrar("R-CONFORMIDADE", "linha longa demais ou com crases e substituições demais para o hook "
                                              "conferir dentro do prazo",
                        "separe em comandos menores, sem crase nem $( aninhados, e grave texto longo num arquivo")
        if nivel:
            self.em_curso.add(releitura)
        texto_de_fora, corpo_de_fora = self.texto_da_linha, self.corpo_desconhecido
        try:
            self.conferir_linha(comando, pasta, nivel, so_substituicoes, corpo_de_heredoc)
            for forma in formas_que_o_shell_le(comando, corpo_de_heredoc):  # HOOK-CONTINUACAO-LINHA: a que o bash roda
                self.conferir_linha(forma, pasta, nivel, so_substituicoes, corpo_de_heredoc)
        finally:
            self.em_curso.discard(releitura)
            self.texto_da_linha, self.corpo_desconhecido = texto_de_fora, corpo_de_fora
        self.conferidas[chave] = dict(self.ambiente or {})

    def recusar_o_teto(self, comando, original, nivel):
        """Bloco T da revalidação 10: com o marcador crítico no nível 0, a chamada acima do teto de caracteres (sem os
        corpos de heredoc) ou de palavras (`excede_o_teto`) é recusada antes de qualquer leitura cara."""
        if nivel == 0 and not self.leitura and self.critico(original):
            excesso = excede_o_teto(comando)
            if excesso:
                self.sem_leitura = True
                self.barrar("R-CONFORMIDADE", f"chamada com ação crítica e {excesso}: o hook não a decide dentro do "
                                              "prazo", CONTORNO_DO_TETO, trava=TRAVA_NO_TETO)

    def conferir_linha(self, comando, pasta, nivel, so_substituicoes, corpo_de_heredoc=False):
        if nivel - self.releituras > PROFUNDIDADE:
            self.barrar(*PROFUNDIDADE_EXCEDIDA)
        if self.leitura and nivel:  # depois da gramática, só `$(`/crase entre aspas simples: o bash só roda por reavaliação
            self.barrar("R-CONFORMIDADE", f"substituição dentro de aspas pelo papel só de leitura ({self.papel})",
                        "escreva o nome literal em vez de $( ou crase, mesmo entre aspas (para procurar um trecho, "
                        "grep -F 'trecho' <arquivo>, sem esses sinais)")
        if self.leitura and nivel == 0:
            self.gramatica_de_leitura(comando)
        provisorios = comando.count("<<")  # S-A2: o prazo que vence antes da tirada dos heredocs já os acha pendentes
        self.h.corpos_pendentes += provisorios
        # ADR 0011, item 2: linha com marcador crítico e construção não modelada recusa; a recusa vem depois das
        # checagens da linha, para que a regra mais específica (R-MAIN, R-VERIFY...) fale primeiro.
        achado = None if self.leitura or not self.critico(comando) else construcao_nao_modelada(comando)
        original = comando
        if nivel == 0 and self.h.raiz and self.raiz_e_projeto() and CITA_A_MARCA.search(comando):
            self.barrar("R-CONFORMIDADE", "a linha cita a marca da sessão (.git/forge) ou a função que grava nela: só o usuário mexe nela",
                        f"não cite .git/forge nem gravar_resultado_do_pr (o resultado sai do forge-check pr); {SUGESTAO}")
        try:
            comando, corpos, gravado = tirar_heredocs(comando, com_gravado=True)
        except ValueError:  # HEREDOC-FURO-HOOK: `<<` em dúvida com linha depois, ou corpo que o bash expande com `$(`
            lidas, corpos, gravado = None, [], None
            self.recusar_o_teto(comando, original, nivel)
        else:
            if corpos and not corpos_conhecidos(original):  # A12 (E1.328): o bash expande o corpo e atribui
                self.corpo_desconhecido = True
            if not corpo_da_funcao("pwd", comando)[0] and linha_conhecida(comando):  # A1 (E1.279) e E1.322
                comando = re.sub(r"\$\(\s*pwd(\s+-[LP])?\s*\)", "$PWD", comando)  # `$(pwd)/x` é um caminho conhecido
            comando = REV_PARSE_DO_GIT.sub(trocar_rev_parse, comando)
            self.texto_da_linha = comando
            self.recusar_o_teto(comando, original, nivel)
            lidas = leituras(comando)
            # opção B da revalidação 9: sobre a palavra que o bash recebe, em qualquer posição; recusa no fim do nível 0.
            # A palavra `"$(…)"` não: o texto dela é o do `shlex`, e o nível de fora já leu as substituições como escritas
            if not so_substituicoes:
                self.reavaliacao = self.reavaliacao or reavaliacao(comando)
        self.h.corpos_pendentes += len(corpos) - provisorios  # C-4: descontado depois do corpo conferido, no laço
        if lidas is None or lidas.ilegivel:
            self.sem_leitura = True
            if nivel:
                self.ilegivel(comando, pasta)
            self.nao_modelada(achado)
            # A linha que a leitura do hook não fecha (`(true)#'`, apóstrofo no comentário de `((…))`, barra no fim) o
            # bash pode rodar, e o `return` pularia todas as checagens dela: fora do papel só de leitura, recusa sempre,
            # com ou sem marcador crítico. O papel só de leitura fica como estava (a gramática dele, no nível 0, já
            # recusa aspas sem par e `#`).
            if not self.leitura and isinstance(corpo_de_heredoc, str):  # M2: só o programa do texto o roda
                self.barrar("R-CONFORMIDADE", f"o texto roda `{corpo_de_heredoc}`, fora da lista dos que não rodam o "
                                              "arquivo gravado, e o corpo do heredoc tem aspa sem par",
                            "grave numa chamada do Bash e rode o programa noutra")
            if not self.leitura and corpo_de_heredoc:  # A1 do review, volta 3: <<'FIM' já está na linha
                self.barrar("R-CONFORMIDADE", "corpo de heredoc com aspa sem par, dado a programa que pode rodá-lo",
                            "grave o texto num arquivo (cat > arq <<'FIM', sozinho) e passe-o ao programa noutra "
                            "chamada do Bash")
            if not self.leitura:
                self.barrar("R-CONFORMIDADE", "aspas sem par na leitura do hook, # que ele não prova ser comentário ou "
                                              "<< que ele não prova ser heredoc: o hook não modela a linha",
                            f"feche as aspas, tire aspas e # do comentário, {FORMA_DO_HEREDOC}, ou separe os comandos")
            return
        if nivel == 0:
            self.ambiente = {}
            self.linha = original
            self.sugerir_na_linha(original)
        # ADR 0013, I2: a leitura fiel e, se a linha tem `#` e a da develop deu outra, também ela, cada uma com estado
        # novo (ambiente, `cd`, branch); a pasta dos corpos de heredoc e o ambiente que segue são os da fiel.
        ambiente = dict(self.ambiente)
        pasta_fiel, ambiente_fiel, vistas = None, None, set()
        for partes in lidas.partes:
            self.ambiente = dict(ambiente)
            depois, pastas = self.conferir_partes(partes, pasta, nivel, so_substituicoes)
            vistas |= pastas
            if pasta_fiel is None:
                pasta_fiel, ambiente_fiel = depois, self.ambiente
        self.ambiente = ambiente_fiel
        pasta = pasta_fiel
        # CRASE-SESSAO-PROJETO: a crase é um `$(…)`, e o corpo dela passa pelas mesmas regras, também entre aspas duplas e
        # numa atribuição. Roda num subshell, numa das pastas por onde a linha passa: o corpo é conferido em cada uma.
        for corpo in conteudos_de_crase(comando, so_os_fechados=True):
            for p in sorted(vistas, key=str):
                self.bash(corpo, p, nivel + 1)
        interpretados = {}  # os heredocs de um mesmo dono (o mesmo texto, `DonosDosHeredocs`) o leem uma vez só
        for dono, corpo in corpos:  # o corpo é comando, a menos que todo dono da linha só o leia (ou o interprete)
            if not corpo_so_lido(dono, interprete):
                self.bash(corpo, pasta, nivel + 1, corpo_de_heredoc=getattr(dono, "rodado", None) or True)
            if dono not in interpretados:  # o `\n` entre as partes separa: o todo lido como a soma das partes
                interpretados[dono] = interpreta_o_corpo(dono)
            if interpretados[dono]:
                self.checar_texto(corpo)
            self.h.corpos_pendentes -= 1
        self.nao_modelada(achado)
        if nivel == 0 and not self.leitura and envio_com_substituicao(comando):  # CONFORMIDADE-SUBSTITUICAO-NO-PROJETO
            self.barrar("R-CONFORMIDADE", "envio do git com o programa, o subcomando, a flag ou o destino vindos de "
                                          "substituição ($(…), crase, <(…)) ou da entrada (xargs, pipe para o shell): o hook não "
                                          "sabe o valor", "escreva o envio literal: git push origin <branch>", trava=TRAVA)  # A6 da E63.3
        if gravado and not self.leitura and CRITICO.search(original):  # M3, depois das regras da linha e do corpo
            self.barrar("R-CONFORMIDADE", f"heredoc gravado e programa não modelado na mesma chamada (`{gravado}`)",
                        "grave o arquivo pelo Write ou numa chamada do Bash e rode o programa noutra")
        if self.lancador_recusado:  # depois das regras específicas da linha (R-MAIN, R-VERIFY, atualizar...)
            self.barrar("R-CONFORMIDADE", f"lançador `{self.lancador_recusado}` repassa o comando sem que o hook o veja, "
                                          "numa sessão de projeto", f"rode o comando direto, sem o lançador; {SUGESTAO}")
        # ADR 0011, item 2 (opção B da revalidação 8), depois das regras específicas, também as do texto reavaliado (o
        # `aninhado` já o conferiu): com o marcador crítico no nível 0, a reavaliação pelo shell em qualquer nível recusa
        if nivel == 0 and not self.leitura and self.reavaliacao and CRITICO.search(original):
            self.barrar("R-CONFORMIDADE", f"`{self.reavaliacao}` na chamada com ação crítica: "
                                          f"{motivo_da_reavaliacao(self.reavaliacao)}",
                        contorno_da_reavaliacao(self.reavaliacao), trava=TRAVA_OPACA)
        # ADR 0011, item 2 (opções D e A), por último: sobre o texto do nível 0, com o `<<` que o bash pode formar nele
        # ou num nível de cima (`tem_heredoc_no_texto`)
        if nivel == 0 and not self.leitura and CRITICO.search(original):
            sinal = fora_da_gramatica_com_heredoc(original)
            if sinal is not None:
                self.barrar("R-CONFORMIDADE", f"`{sinal}` na chamada com heredoc e ação crítica: o hook não modela",
                            CONTORNO_DA_GRAMATICA, trava=TRAVA_OPACA)

    def conferir_partes(self, partes, pasta, nivel, so_substituicoes):
        """As checagens de cada comando simples de uma leitura da linha (`leituras`); devolve a pasta depois dela e as
        pastas por onde a leitura passou (a de cada comando, também dentro das substituições)."""
        ramos = {}
        contextos = {(): (pasta, ramos)}  # cada substituição roda num subshell: `cd` e branch lá dentro ficam lá
        vistas = {pasta}

        def contexto(sub):
            if sub not in contextos:
                pasta_de_fora, ramos_de_fora = contexto(sub[:-1])
                contextos[sub] = (pasta_de_fora, dict(ramos_de_fora))
            return contextos[sub]

        for palavras, destinos, sub in partes:
            if so_substituicoes and not sub:
                continue
            pasta_sub, ramos_sub = contexto(sub)
            for d in destinos:
                if self.leitura and d not in self.leitura["saidas"]:
                    self.barrar("R-CONFORMIDADE", f"redirecionamento para {d} pelo papel só de leitura ({self.papel})",
                                DICA_LEITURA)
                self.checar_escrita(d, pasta_sub)
            contextos[sub] = (self.segmento(palavras, pasta_sub, ramos_sub, nivel), ramos_sub)
            vistas.add(contextos[sub][0])
        return contextos[()][0], vistas

    critico = CRITICO.search  # o marcador da ação crítica; a `GuardaDaProva` soma o controle (custo: uma chamada só)

    def nao_modelada(self, achado):
        """ADR 0011, item 2: recusa a linha crítica com construção que o analisador não modela (`construcao_nao_modelada`)."""
        if achado is not None:
            self.barrar("R-CONFORMIDADE", f"`{achado}` com ação crítica: o hook não modela", forma_aceita(achado),
                        trava=TRAVA_OPACA)

    def gramatica_de_leitura(self, linha):
        """ADR 0011, item 1: antes de qualquer outra checagem, a linha do papel só de leitura precisa caber na gramática
        positiva (`fora_da_gramatica_de_leitura`). O que ela não modela (`$`, crase, `\\`, `#`, chaves, globs,
        redirecionamento, substituição, várias linhas) recusa, e a mensagem diz a forma explícita."""
        sinal = fora_da_gramatica_de_leitura(linha)
        contorno = "um comando por chamada; sinais só entre aspas simples"
        if sinal == "$":  # E3.50: a variável sai pelo valor literal, que a gramática aceita (cabe no LIMITE_MENSAGEM)
            contorno = "caminho literal no lugar da variável (não F=x; cat $F)"
        contorno += "; no lugar de echo $?: && echo contém || echo não contém"
        if sinal is not None:
            self.barrar("R-CONFORMIDADE", f"`{sinal}` fora da gramática do papel só de leitura ({self.papel})", contorno)

    def sugerir_na_linha(self, linha):
        """F6, lista branca estrita: a única linha com `sugerir` que passa é `forge sugerir --guardar "<texto>"` inteira, ou a
        linha só de leitura (`so_leitura`: `grep -n 'forge sugerir' README.md`). Qualquer outra que contenha a palavra, mesmo ofuscada (`sug""erir`, `$S`, `forge $S`), é recusada: na dúvida, recusa."""
        if guardar_exato(linha) or so_leitura(linha):
            return
        limpa = re.sub(r"[\"'\\`]", "", linha)
        if "sugerir" in limpa or re.search(r"(?:^|[\s;&|(])(?:\S*/)?forge[\"']?\s+[\"']?\S*[$`*?\[{~]", linha):
            self.barrar("R-CONFORMIDADE", "`forge sugerir` fora da forma `forge sugerir --guardar \"<texto>\"` sozinha na linha",
                        "quem envia a sugestão é você, no seu terminal: `forge sugerir --fila`; o agente só guarda, "
                        "com a linha inteira `forge sugerir --guardar \"<texto>\"`", "sugerir")

    def ilegivel(self, comando, pasta):
        """R-CONTRIB: comando aninhado (`bash -c`, `eval`, `env -S`) que o hook não consegue analisar, numa sessão de
        projeto, apontando para o Forge (o texto, o GH_REPO/GIT_DIR da linha ou a pasta): falha fechado."""
        if self.sessao_forge or self.clone_do_forge():
            return
        if (parecer.aponta_para_o_forge(comando) or any(parecer.aponta_para_o_forge(v) for v in self.ambiente.values())
                or self.alvo_do_forge(pasta)):
            self.barrar("R-CONTRIB", "comando aninhado (bash -c, eval, env -S) que o hook não consegue analisar, "
                                     "apontando para o Forge", "rode o comando direto, sem shell aninhado")

    def aninhado(self, comando, pasta, nivel, atribuicoes):
        """`bash -c`, `sh -c`, `eval`: o comando interno passa pelas mesmas regras, com as variáveis da linha externa
        (`GH_REPO=x bash -c '...'`, `env GH_REPO=x sh -c '...'`)."""
        antes = {}
        for a in atribuicoes:
            nome, _, valor = a.partition("=")
            if nome in VARIAVEIS_DA_LINHA and valor:
                antes.setdefault(nome, self.ambiente.get(nome))
                self.ambiente[nome] = valor
        try:
            self.bash(comando, pasta, nivel + 1)
            if "\\`" in comando:  # entre aspas duplas o shell de fora troca `\`` por crase: o de dentro a executa (R-CONTRIB)
                self.bash(comando.replace("\\`", "`"), pasta, nivel + 1)
        finally:
            for nome, valor in antes.items():
                if valor is None:
                    self.ambiente.pop(nome, None)
                else:
                    self.ambiente[nome] = valor

    def segmento(self, palavras, pasta, ramos, nivel):
        """HOOK-MSG-SEGMENTO: a recusa dentro do comando simples o cita (`com_trecho`); fora dele, volta o de antes."""
        anterior, self.trecho = self.trecho, palavras
        try:
            return self.segmento_lido(palavras, pasta, ramos, nivel)
        finally:
            self.trecho = anterior

    def segmento_lido(self, palavras, pasta, ramos, nivel):
        """Analisa um comando simples; devolve a pasta depois dele (acompanha `cd`). Atrás de lançador com palavra de `-`
        fora da tabela (`separar_lancadores`), roda as regras sobre cada leitura possível e recusa se qualquer uma recusa
        (RET-LEITURA-HOOK-G, opção A da proposta caminho-rev13). A pasta e as variáveis que seguem na linha são as da
        primeira leitura (sem valor, ADR 0013, item 5); as outras partem do estado de antes e o descartam depois. Com
        mais de uma leitura, o texto dividido que não fecha aspas recusa (RET-LEITURA-HOOK-H, opção B da proposta
        caminho-rev14); com uma só, vai a `ilegivel`."""
        while palavras and palavras[0] in CORPO_DE_LACO:  # `do rm ...`, `then ...`: o comando vem depois da palavra
            palavras = palavras[1:]
        try:
            leituras_do_lancador = separar_lancadores(palavras)
        except TextoAbertoComLeituras as achado:  # mais de uma leitura, e uma não se lê: o hook não as lê todas
            self.barrar("R-CONFORMIDADE", f"`{achado}` na chamada: opção de lançador que o hook não modela, com texto "
                                          "dividido que não fecha aspas", CONTORNO_DO_LANCADOR)
        except LancadorDemais as achado:  # mais palavras fora da tabela que o teto: o hook não lê as leituras todas
            self.barrar("R-CONFORMIDADE", f"`{achado}` na chamada: opção de lançador que o hook não modela, em mais de "
                                          f"{TETO_FORA_DA_TABELA} palavras fora da tabela no mesmo comando",
                        CONTORNO_DO_LANCADOR)
        except TextoDivididoAberto:  # texto dividido do `env` com aspas abertas, numa leitura só
            self.ilegivel(" ".join(palavras), pasta)
            return pasta
        ambiente, recusado = dict(self.ambiente), self.lancador_recusado
        depois = self.leitura_do_segmento(palavras, *leituras_do_lancador[0], pasta, ramos, nivel)
        for comando, lancadas in leituras_do_lancador[1:]:
            ambiente_fiel, recusado_fiel = self.ambiente, self.lancador_recusado
            self.ambiente, self.lancador_recusado = dict(ambiente), recusado
            try:
                self.leitura_do_segmento(palavras, comando, lancadas, pasta, dict(ramos), nivel)
            finally:  # o ambiente da leitura a mais se descarta; a recusa do lançador (no fim da linha) só soma
                # volta 3 (A3 da E20.29): menos a variável do `.git` (`L -w X d=$(git rev-parse --git-dir)`), que segue
                # na linha como no corpo sozinho: falha fechada, a leitura que a define ganha da que não define
                no_git = {k: v for k, v in self.ambiente.items() if DIR_DO_GIT in v}
                self.ambiente, self.lancador_recusado = ambiente_fiel, recusado_fiel or self.lancador_recusado
                self.ambiente.update(no_git)
        return depois

    def leitura_do_segmento(self, escritas, palavras, lancadas, pasta, ramos, nivel):
        """As checagens de uma leitura (`palavras`, com `lancadas` pelos lançadores) do comando simples `escritas`, como
        veio escrito; devolve a pasta depois dele."""
        originais = sem_atribuicoes(escritas)
        atribuicoes = escritas[: len(escritas) - len(originais)]
        atribuicoes += lancadas
        if self.leitura:
            if originais[:1] != palavras[:1]:
                self.barrar("R-CONFORMIDADE", f"lançador `{Path(originais[0]).name}` repassa argumentos que o hook não vê "
                                              f"(papel só de leitura: {self.papel})", DICA_LEITURA)
            self.checar_so_leitura(palavras, atribuicoes)
        for a in atribuicoes + (palavras[1:] if exporta(palavras) else []):
            if "core.hookspath" in a.lower():
                self.barrar("R-VERIFY", "core.hooksPath por variável de ambiente", "não troque o caminho dos hooks")
            if AMBIENTE_DE_TROCA.match(a.partition("=")[0]):  # N2: atribuição, `env` ou `export`
                self.barrar("R-REVIEW", f"{a.partition('=')[0]} muda os objetos que o git lê",
                            "não troque objetos do repositório; o parecer vale pelo que está commitado")
        for a in atribuicoes + (palavras[1:] if exporta(palavras) else []):  # depois do core.hooksPath
            if CONFIG_NO_AMBIENTE.match(a.partition("=")[0]):  # alias e -c escondidos do hook
                self.barrar("R-REVIEW", f"{a.partition('=')[0]} dá ao git configuração que o hook não lê",
                            "rode o git sem configuração pela variável de ambiente")
        definidas = [p for p in palavras[1:] if not p.startswith("-")] if exporta(palavras) else \
            [] if palavras else atribuicoes
        for a in definidas:
            nome, _, valor = a.partition("=")
            if nome in VARIAVEIS_DA_LINHA and valor or DIR_DO_GIT in valor:  # `d=$(git rev-parse --git-dir)` também
                self.ambiente[nome] = valor  # vale para os comandos seguintes da linha
        for p in atribuicoes + palavras:  # substituição entre aspas: a palavra chega inteira (N1: também a atribuição)
            if "`" in p:  # a palavra relida não é um nível do shell: o corpo da crase já conta o dele (PROFUNDIDADE-BASH-C)
                self.releituras += 1
                try:
                    self.bash(p, pasta, nivel + 1)
                finally:
                    self.releituras -= 1
            elif "$(" in p.replace(OPACO["$"], ""):
                self.bash(p, pasta, nivel + 1, so_substituicoes=True)
        if not palavras:
            return pasta
        prog = Path(palavras[0].lstrip("`")).name
        args = palavras[1:]
        por_applet = prog in ("busybox", "toybox") and bool(args) and not args[0].startswith("-")
        if por_applet:  # A4 da volta 2, A5: o applet é o programa
            self.atualizacao(palavras)  # A6: antes da troca, a varredura que o `busybox` tinha em ENVOLVEDORES
            palavras, prog, args = args, Path(args[0]).name, args[1:]
        if self.raiz_e_projeto() and LANCADORES_RECUSADOS & {prog, nome_do_caminho(originais[0])}:
            self.lancador_recusado = (LANCADORES_RECUSADOS & {prog, nome_do_caminho(originais[0])}).pop()  # recusa no fim da linha
        parte = parecer.analisar(palavras)
        if parecer.expande(palavras[0]) and parecer.gh_de_merge_ou_api(args):
            self.barrar("R-MAIN", "programa por expansão com pr merge ou api: o hook não sabe se é o gh",
                        "chame `gh` pelo nome, sem expansão")  # GH-MERGE-ADMIN, C-1 e C-3: falha fechado
        if prog == "pushd":  # como o `cd`: o destino é o primeiro argumento que não é opção
            alvo = next((a for a in args if not a.startswith("-")), None)
            return self.caminho(pasta, alvo) if alvo else pasta
        if parte and parte[0] == "cd":
            return self.caminho(pasta, parte[1]) if parte[1] else Path.home()
        if parte and parte[0] == "branch" and not por_applet:  # A8: nem busybox nem toybox têm applet git
            raiz = raiz_do_projeto(pasta / parte[1] if parte[1] else pasta)
            if raiz:
                ramos[raiz.resolve()] = parte[2]
        if prog in SHELLS:
            self.atualizacao(palavras, so_binarios=True)
        elif prog in ENVOLVEDORES or INTERPRETES.match(prog) or prog == "forge" or prog in BINARIOS_DE_ATUALIZACAO:
            self.atualizacao(palavras)
        no_lugar = bool(PERL_OU_RUBY.match(prog)) and edita_no_lugar(args)
        argumentos_do_forge_check = args_do_forge_check(prog, args)
        if argumentos_do_forge_check is not None:
            self.forge_check_grava(argumentos_do_forge_check, pasta)
        if prog in SHELLS:
            for i, a in enumerate(args):
                if re.fullmatch(r"-[a-z]*c[a-z]*", a) and i + 1 < len(args):
                    self.aninhado(args[i + 1], pasta, nivel, atribuicoes)
        elif prog == "eval":
            self.aninhado(" ".join(args), pasta, nivel, atribuicoes)
        elif INTERPRETES.match(prog):
            for a in args:
                self.checar_texto(a)
            if no_lugar:  # edição no lugar (`-i`, `-pi`, `-0777pi`, `-i.bak`): os arquivos-alvo também são escrita
                for i, a in enumerate(args):
                    if not a.startswith("-") and not (i and args[i - 1] in ("-e", "-E")):
                        self.checar_escrita(a, pasta)
            if prog.startswith("python") and args[:2] == ["-m", "pip"]:
                self.pacote("pip", args[2:])
        elif prog in AWKS:  # programa no texto (`print > arq`, `system("rm ...")`) e, com `-i inplace`, os arquivos-alvo
            for a in args:
                if re.search(r"[\s{(;]", a):
                    self.checar_texto(a)
            if awk_no_lugar(args):
                for a in args:
                    if not a.startswith("-") and a != "inplace" and not re.search(r"[\s{(;=]", a):
                        self.checar_escrita(a, pasta)
        elif prog == "git":
            self.git(palavras, parte, pasta, ramos, self.da_atribuicao(atribuicoes, "GIT_DIR"), atribuicoes)
        elif prog == "gh":
            self.gh(palavras, parte, pasta, self.da_atribuicao(atribuicoes, "GH_REPO"), atras_do_xargs(originais, palavras),
                    self.da_atribuicao(atribuicoes, "GH_CONFIG_DIR"))
        elif prog == "claude":
            self.claude(args)
        elif prog in TODOS_OS_ARGUMENTOS or (prog == "sed" and sed_no_lugar(args)):
            for a in args:
                if not a.startswith("-"):
                    self.checar_escrita(a, pasta, parecer_conta=prog == "mv" or prog not in REMOCAO)
                    if prog in REMOCAO:
                        self.checar_remocao(a, pasta)
        elif prog in SO_DESTINO:
            if prog == "ln" or any(re.fullmatch(r"-[^-]*[ls]\w*|--(link|symbolic-link)", a) for a in args):  # S8 (C-3)
                for a in args:  # o link aponta a prova: a origem também conta, pelo nome literal e pelo resolvido
                    nomes = Path(a).name, self.resolver(self.expandir(a, pasta), pasta).name
                    self.curinga_na_prova(nomes[0], self.pastas_do_curinga(a, pasta))
                    if any(map(MARCA_DA_SUITE.fullmatch, nomes)):
                        self.barrar(*PROVA_DA_SUITE)
            alvo = next((args[i + 1] for i, a in enumerate(args[:-1]) if a in ("-t", "--target-directory")), None)
            alvo = alvo or next((a.split("=", 1)[1] for a in args if a.startswith("--target-directory=")), None)  # A5
            alvo = alvo or next((a for a in reversed(args) if not a.startswith("-") or "`" in a), None)  # A3: `x --y`/config
            if alvo:
                self.checar_escrita(alvo, pasta)
            # N3: depois da escrita no destino, para a regra do papel falar primeiro
            if prog == "ln" or prog == "cp" and any(re.fullmatch(r"-[^-]*[ls]\w*|--(link|symbolic-link)", a) for a in args):
                self.link_em_protegido(args, pasta)
        elif prog == "dd":
            for a in args:
                if a.startswith("of="):
                    self.checar_escrita(a[3:], pasta)
        elif prog == "find":
            self.find(args, pasta, nivel, atribuicoes)
        elif prog in EXTRATORES:
            alvos = EXTRATORES[prog](args)
            for a in alvos.arquivos:
                self.checar_escrita(a, pasta)
            for a in alvos.removidos:
                self.checar_escrita(a, pasta, parecer_conta=False)
                self.checar_remocao(a, pasta)
            for d in alvos.pastas:
                self.checar_escrita(d, pasta, parecer_conta=False)
                self.checar_remocao(d, pasta, "extrair em")
            for c in alvos.executados:
                self.aninhado(c, pasta, nivel, atribuicoes)
        elif prog in MUDA_ATRIBUTO:
            for a in args:
                if not a.startswith("-"):
                    self.checar_escrita(a, pasta, parecer_conta=False)
                    self.checar_remocao(a, pasta, f"{prog} em")
        elif prog in self.pol["pacotes"]:
            self.pacote(prog, args)
        if prog in ("cp", "mv", "install", "ln"):  # A9, U3: depois das regras do destino e do link
            self.origem_do_git_no_opaco(args, pasta)
        if prog == "sed":  # `w arquivo` no script escreve, com ou sem `-i`
            for a in args:
                for destino in SED_ESCREVE.findall(script_do_sed(a)):
                    self.checar_escrita(destino, pasta)
        if prog in LEITORES:
            for a in args:
                nome = nome_do_caminho(a)
                if ARQUIVO_ENV.match(nome) and nome.rsplit(".", 1)[-1] not in ENV_DE_EXEMPLO:
                    self.barrar("R-CONFORMIDADE", f"ler {nome} expõe segredos",
                                "peça ao usuário o valor de que precisa (R-DECISAO)")
        return pasta

    def forge_check_grava_no_pedido(self, args):
        """True se a linha do `forge-check` grava no pedido pela forma nova (`grava_no_pedido`)."""
        return grava_no_pedido(livres_do_forge_check(args), args)

    def forge_check_grava(self, args, pasta):
        """A4: o que o `forge-check` grava passa pela política de caminhos do papel, como o Write no mesmo destino (o `anotar`
        em `docs/pedidos/`, o `brief --gravar` em `docs/briefs/`, a saída do `transcricao anonimizar`), a partir da pasta da
        sessão e de `~/.forge-contrib`, as duas raízes que o `forge-check` aceita. `--raiz` e `--raiz-pedidos`, antes ou depois
        do subcomando, só saem do caminho para achar o subcomando: a política não depende do nome do pedido nem da raiz."""
        livres = livres_do_forge_check(args)
        sub = next(iter(livres), "")
        if grava_no_pedido(livres, args):  # o selo e a `entrega conferida` são do jarvis (docs/pedidos/)
            destinos = [f"{r}/docs/pedidos/pedido.md" for r in (".", "~/.forge-contrib")]
        elif sub == "pausa":  # X1 (review da 0.44.1): a pausa é da sessão principal; `--retomar` só lê (e apaga a pausa vencida)
            destinos = [] if so_le(args, "--retomar") else ["./.forge/pausa.json"]
        elif sub in FORGE_CHECK_ESCRITAS and (sub != "brief" or any(abreviacao_de(a, ("--gravar",)) for a in args)) \
                and not (sub == "pedido" and so_le(args, "--ler")):
            destinos = [f"{r}/{FORGE_CHECK_ESCRITAS[sub]}/pedido.md" for r in (".", "~/.forge-contrib")]
        elif sub == "recado" and not so_le(args, "--confirmar"):
            # S8 (review da 0.44.1): a caixa de recados é da sessão principal; a raiz de destino (`--para`) é livre, então a política de
            # `.forge/recados/` da sessão decide, com qualquer raiz; sem `--confirmar`, grava (na dúvida, recusa)
            destinos = ["./.forge/recados/recado.md"]
        else:
            destinos = livres[3:4] if sub == "transcricao" and livres[1:2] == ["anonimizar"] else []
        for destino in destinos:
            self.checar_escrita(destino, pasta)

    def checar_so_leitura(self, palavras, atribuicoes):
        """Papel só de leitura (`so_leitura`): lista branca de comandos, depois da gramática (`gramatica_de_leitura`, que já
        recusa expansão, substituição e redirecionamento). Variável na linha (`GIT_EXTERNAL_DIFF=x`), programa com caminho
        (`./grep`), opção global do git que não seja `-C`/`--no-pager` (`-c core.pager=...`), `--output`, `test` fora de
        `TESTE_LEITURA` e valor de opção do `forge-check` que começa com `-` recusam; o resto fora da lista também: na
        dúvida, recusa."""
        if atribuicoes:
            self.barrar("R-CONFORMIDADE", f"variável na linha ({atribuicoes[0]}) pelo papel só de leitura ({self.papel})",
                        DICA_LEITURA)
        if not palavras:
            return
        prog, args = palavras[0], palavras[1:]
        if prog == "git":
            while args[:1] == ["--no-pager"] or (args[:1] == ["-C"] and len(args) > 1):
                args = args[1:] if args[0] == "--no-pager" else args[2:]
        chave = " ".join([prog, *args[:2 if prog == "gh" else 1]]) if prog in ("git", "gh", "forge-check") else prog
        if any(abreviacao_de(a, ("--output",)) for a in args):
            self.barrar("R-CONFORMIDADE", f"`{chave} --output` grava arquivo (papel só de leitura: {self.papel})",
                        DICA_LEITURA)
        if prog == "test" and (len(args) != 2 or args[0] not in TESTE_LEITURA):
            self.barrar("R-CONFORMIDADE", f"`test` fora da forma `test -e|-f|-d|-s <caminho>` (papel só de leitura: "
                                          f"{self.papel})", "um teste por chamada, com um caminho")
        if prog == "forge-check" and any(
                abreviacao_de(a, FORGE_CHECK_GRAVA) or a.split("=", 1)[0] in FORGE_CHECK_GRAVA_EXATA for a in args):
            self.barrar("R-CONFORMIDADE", f"`{chave}` com opção que grava arquivo (papel só de leitura: {self.papel})",
                        DICA_LEITURA)
        if prog == "forge-check" and self.forge_check_grava_no_pedido(args):
            self.barrar("R-CONFORMIDADE", f"`{chave}` grava no Histórico do pedido (papel só de leitura: {self.papel})",
                        "use a forma antiga (`forge-check entrega <pedido> --branch ... --base ... --base-sha ...`) ou "
                        "`entrega --pedido ... --so-leitura`; o selo e a `entrega conferida` são do jarvis")
        if prog == "forge-check" and entrega_pela_forma_nova(livres_do_forge_check(args), args) and not so_leitura_no_entrega(args):
            self.barrar("R-CONFORMIDADE", f"`{chave} --pedido` sem `--so-leitura` roda os PQ cmd, código da branch (papel só de leitura: "
                                          f"{self.papel})", "use `forge-check entrega --pedido <p> --branch <b> --etapa <etapa> --so-leitura`; "
                                                            "os PQ cmd ficam com o autor, o CI e o QA (D4)")
        if prog == "forge-check" and any(re.match(r"--[\w-]+=-", a) for a in args):
            self.barrar("R-CONFORMIDADE", f"`{chave}` com valor de opção que começa com `-` (papel só de leitura: "
                                          f"{self.papel})", DICA_LEITURA)
        if prog == "gh" and any(a in ("--web", "-w") for a in args):
            self.barrar("R-CONFORMIDADE", f"`{chave} --web` abre o navegador (papel só de leitura: {self.papel})", DICA_LEITURA)
        if prog == "git":
            self.git_so_leitura(chave, args[1:])
        if prog == "forge-check" and livres_do_forge_check(args)[:2] == ["transcricao", "anonimizar"]:
            self.barrar("R-CONFORMIDADE", f"`forge-check transcricao anonimizar` grava arquivo (papel só de leitura: "
                                          f"{self.papel})", DICA_LEITURA)
        if "/" in prog or chave not in self.comandos_de_leitura:
            self.barrar("R-CONFORMIDADE", f"`{chave}` fora da lista do papel só de leitura ({self.papel})", DICA_LEITURA)

    def git_so_leitura(self, chave, args):
        """Opções do git no papel só de leitura: lista branca no `ls-remote` (sem transporte `<x>::`, que roda o
        `git-remote-<x>`); nos outros subcomandos, recusa as de `GIT_EXECUTA`, inclusive abreviadas (`--textconv` e
        `--filters` rodam o driver configurado no repositório), e o formato `%G` (`FORMATO_ASSINATURA`). `git branch` e
        `git worktree` só passam pela gramática exata de `forma_de_leitura_git` (E8, C-1 e C-2)."""
        if chave in ("git branch", "git worktree"):
            if not forma_de_leitura_git(chave, args):
                self.barrar("R-CONFORMIDADE", f"`{(chave + ' ' + ' '.join(args)).strip()}` fora das formas de leitura "
                                              f"(papel só de leitura: {self.papel})", DICA_LEITURA)
            return
        for a in args:
            if chave == "git ls-remote":
                if a.startswith("-") and a not in LS_REMOTE_LEITURA and not a.startswith("--sort="):
                    self.barrar("R-CONFORMIDADE", f"`git ls-remote` com a opção `{a}`, fora das de leitura "
                                                  f"(papel só de leitura: {self.papel})", DICA_LEITURA)
                if not a.startswith("-") and "::" in a:
                    self.barrar("R-CONFORMIDADE", f"`git ls-remote` com transporte `{a.split('::', 1)[0]}::`, que executa "
                                                  f"programa (papel só de leitura: {self.papel})", DICA_LEITURA)
            elif a.startswith("--show-signature"):
                self.barrar("R-CONFORMIDADE", f"`{chave}` com `{a}`, opção que executa programa (o gpg) "
                                              f"(papel só de leitura: {self.papel})",
                            "tire a opção e peça o dado por --format, por exemplo --format='%h %s' (sem %G)")
            elif abreviacao_de(a, GIT_EXECUTA) and (a.split("=", 1)[0] not in GIT_EXATAS or chave == "git cat-file"):
                self.barrar("R-CONFORMIDADE", f"`{chave}` com `{a}`, opção que executa programa "
                                              f"(papel só de leitura: {self.papel})", DICA_LEITURA)
            elif FORMATO_ASSINATURA.search(a):
                self.barrar("R-CONFORMIDADE", f"`{chave}` com formato de assinatura (`%G`), que roda o gpg "
                                              f"(papel só de leitura: {self.papel})",
                            "use um formato sem %G, por exemplo --format='%h %s' (hash e assunto)")

    def da_atribuicao(self, atribuicoes, nome):
        """Valor de `NOME=` na própria linha do comando ou definido antes (`export`)."""
        return next((a.split("=", 1)[1] for a in atribuicoes if a.startswith(nome + "=")), self.ambiente.get(nome))

    # git ---------------------------------------------------------------------------------------------
    def ramo_em(self, pasta, ramos):
        raiz = raiz_do_projeto(pasta)
        chave = raiz.resolve() if raiz else None
        return ramos[chave] if chave in ramos else git(pasta, "branch", "--show-current")[1]

    def pathspecs_da_linha(self, atribuicoes):
        """As opções `--*-pathspecs` que as variáveis `GIT_*_PATHSPECS` da linha (atribuição, `env`, `export`) ligam. Só
        um falso explícito (`0`, `false`, `no`, `off`, vazio) as desliga; na dúvida, vale como ligada (mais recusa)."""
        valores = {nome: self.da_atribuicao(atribuicoes, nome) for nome in PATHSPECS_NO_AMBIENTE}
        return [opcao for nome, opcao in PATHSPECS_NO_AMBIENTE.items()
                if valores[nome] is not None and valores[nome].strip().lower() not in ("", "0", "false", "no", "off")]

    def git(self, palavras, parte, pasta, ramos, git_dir=None, atribuicoes=(), alias=0):
        i, pasta_git, opcoes = 1, self.caminho(pasta, git_dir) if git_dir else pasta, self.pathspecs_da_linha(atribuicoes)
        cwd = pasta  # cada `-C` é relativo ao anterior, como o git faz (`-C ~ -C .forge-contrib/proj`)
        troca = []  # `-c` que troca o destino do envio (GIT_CONFIG_* já é recusado para todos)
        while i < len(palavras) and palavras[i].startswith("-"):
            if palavras[i].endswith("-pathspecs"):  # `--literal-pathspecs`...: valem também para o `ls-files` do hook
                opcoes.append(palavras[i])
            if palavras[i] == "-C" and i + 1 < len(palavras):
                cwd = pasta_git = self.caminho(cwd, palavras[i + 1])
            elif palavras[i] == "--git-dir" and i + 1 < len(palavras):
                pasta_git = self.caminho(cwd, palavras[i + 1])
            elif palavras[i].startswith("--git-dir="):
                pasta_git = self.caminho(cwd, palavras[i].split("=", 1)[1])
            if palavras[i] == "-c" and i + 1 < len(palavras) and CONFIG_DO_MERGE.match(palavras[i + 1]):
                self.barrar("R-REVIEW", f"git -c {palavras[i + 1]} muda como o merge mescla o que o review leu",
                            "mescle sem estratégia, --squash nem --no-commit")
            if palavras[i] == "-c" and i + 1 < len(palavras):
                self.config_da_linha(palavras[i + 1])
                troca += [palavras[i + 1]] if CONFIG_DO_DESTINO.fullmatch(palavras[i + 1]) else []
            if palavras[i].startswith("--config-env"):
                self.barrar("R-REVIEW", "git --config-env dá ao git configuração que o hook não lê",
                            "rode o git sem configuração pela variável de ambiente")
            i += 2 if palavras[i] in parecer.GIT_COM_VALOR else 1
        sub, args = (palavras[i], palavras[i + 1:]) if i < len(palavras) else (None, [])
        expansao = self.alias_do_git(sub, pasta_git)
        if expansao is not None:  # N1 (C-N1-2): o git roda a expansão, e é ela que as regras leem
            novas = self.expansao_do_alias(sub, expansao, alias) + args
            novas = palavras[:i] + novas
            self.git(novas, parecer.analisar(novas), pasta, ramos, git_dir, atribuicoes, alias + 1)
            return
        args = [por_extenso(a) for a in args]  # AR-TRAVA-UMA-SINTAXE: `--no-verif` é `--no-verify` para o git
        ativacao = sub == "config" and args == ["core.hooksPath", ".githooks"]  # R-CONTRIB: ativar o hook do repositório
        if any("core.hookspath" in p.lower() for p in (palavras[:i] if ativacao else palavras)):
            self.barrar("R-VERIFY", "core.hooksPath", "não desative nem troque o caminho dos hooks")
        if "--no-verify" in args or (sub == "commit" and any(re.fullmatch(r"-[a-zA-Z]*n[a-zA-Z]*", a)
                                                             for a in args)):
            self.barrar("R-VERIFY", f"git {sub} --no-verify", "corrija a causa do hook que falhou")
        if sub == "config" and not ativacao:
            self.git_config(args)
        self.git_troca(sub, args, palavras[1:i])
        self.git_trava(sub, args, pasta_git, ramos)  # antes da N5: apagar ou reescrever a integração tem recusa própria
        self.git_integracao(sub, args, pasta_git, ramos)
        if sub in CAMINHOS_NO_GIT:
            self.git_caminhos(sub, args, [pasta, pasta_git], opcoes)
        if sub in INDICE_NO_GIT:
            self.git_indice(sub, args, [pasta, pasta_git], opcoes)
        self.git_no_forge(sub, args, pasta_git)
        if sub == "tag":
            self.git_tag(args, pasta_git)
        if sub in ("push", "send-pack"):  # o send-pack grava refs no destino como o push
            self.git_tags_no_envio(args, palavras[1:i], pasta_git, sub)
            self.git_push(args, pasta_git, ramos, sub, troca)
        elif sub == "subtree" and args[:1] == ["push"]:  # `git subtree push -P <pasta> <repositório> <ref>`
            self.git_push(parecer.posicionais(args[1:], SUBTREE_COM_VALOR), pasta_git, ramos, "subtree push", troca)
        elif parte and parte[0] == "merge" and parte[2]:
            atual = self.ramo_em(pasta_git, ramos)
            if atual in INTEGRACAO and not all(b == atual for b, _ in parte[2]):
                if atual in ("main", "master"):
                    self.barrar("R-MAIN", f"merge na {atual} é do usuário", "abra o PR e peça ao usuário que o mescle",
                                alvo=atual)
                achada = opcao_de_merge_que_muda_o_resultado(args)
                if achada:  # A3: todo papel; a estratégia, o squash e o no-commit descartam ou mudam o que o review leu
                    self.barrar("R-REVIEW", f"git {sub} {achada} na {atual} muda o que o review leu",
                                "mescle sem estratégia, --squash nem --no-commit; resolva o conflito na branch de trabalho")
                if not self.pode("merge_integracao"):
                    self.barrar("R-CONFORMIDADE", f"merge em {atual} {self.so_de('merge_integracao')} "
                                                  f"(papel: {self.papel})", "peça ao tech-lead")

    def alias_do_git(self, sub, pasta):
        """A expansão do alias `sub` na configuração que o git lê em `pasta`, ou None se `sub` é comando do git ou não é
        alias (o nome que não é chave válida também sai 1). O git que não responde recusa (na dúvida, o hook não lê)."""
        if sub is None or sub in COMANDOS_DO_GIT:
            return None
        try:
            cod, saida = forge_check().git(pasta, "config", "--get", f"alias.{sub}")
        except (OSError, subprocess.SubprocessError):
            cod, saida = None, ""
        if cod == 1:
            return None
        if cod != 0:
            self.barrar("R-REVIEW", f"git {sub}: o hook não conseguiu ler se é alias da configuração",
                        "rode o subcomando do git por extenso", trava=TRAVA_OPACA)
        return saida

    def expansao_do_alias(self, sub, expansao, alias):
        """As palavras da expansão do alias `sub`; recusa o alias de shell, o que mescla, o encadeado demais e o ilegível."""
        if expansao.startswith("!"):
            self.barrar("R-REVIEW", f"git {sub}: alias de shell (`!`) da configuração roda o que o hook não lê",
                        "rode o comando direto, sem alias", trava=TRAVA_OPACA)
        if alias >= PROFUNDIDADE_DO_ALIAS:
            self.barrar("R-REVIEW", f"git {sub}: alias encadeado demais",
                        "rode o subcomando do git por extenso", trava=TRAVA_OPACA)
        try:
            palavras = shlex.split(expansao)
        except ValueError:
            palavras = None
        if not palavras:
            self.barrar("R-REVIEW", f"git {sub}: alias da configuração que o hook não lê",
                        "rode o subcomando do git por extenso", trava=TRAVA_OPACA)
            return []  # a GuardaDaProva não para no barrar: sem palavras não há o que ler (segurança A6)
        if palavras[0] in ALIAS_QUE_MESCLA:
            self.barrar("R-REVIEW", f"git {sub}: alias da configuração que mescla (`{palavras[0]}`); o parecer só lê o merge "
                                    "por extenso", f"rode git {palavras[0]} direto, sem alias")
        return palavras

    def git_caminhos(self, sub, args, pastas, opcoes=()):
        """`git rm|mv|checkout|restore` mexem nos arquivos como `rm`/`mv`: os caminhos passam pela mesma conferência de
        escrita e de remoção (`.forge/versao` apagado por `git rm` desligaria os hooks). Quem resolve o pathspec é o
        próprio git (`git ls-files`: `*` atravessa `/` e casa ponto inicial, `.` e `-r .` valem pelos arquivos, e a
        magia `:(top)`, `:(literal)`, `:(glob)`, `:(icase)`, `:/` vale como o git a entende), então o hook não refaz a
        semântica dele. `--pathspec-from-file` é recusado: o hook não lê o arquivo nem a entrada padrão. `checkout` e
        `restore` sem origem só devolvem o que o índice já tem: `git checkout -- .` segue livre, e só o caminho
        protegido nomeado barra; com origem (`-s`, `git checkout <ref> -- ...`) o pathspec vale pelo que ele alcança."""
        if any(a.startswith("--pathspec-fr") and "--pathspec-from-file".startswith(a.split("=", 1)[0]) for a in args):
            self.barrar("R-CONFORMIDADE", f"git {sub} --pathspec-from-file: o hook não lê a lista de caminhos",
                        "passe os caminhos na linha de comando; o que for protegido é do usuário (R-DECISAO)")
        caminhos, com_origem = self.pathspecs_do_git(sub, args, pastas[0])
        for pasta in dict.fromkeys(pastas):
            for c in caminhos:
                self.checar_escrita(c, pasta, parecer_conta=False)
                self.checar_remocao(c, pasta)
                if com_origem or sub in ("rm", "mv") or not self.varredura(c):
                    for alvo in filter(self.pode_ser_protegido, self.tracked_do_pathspec(c, pasta, opcoes)):
                        self.checar_escrita(alvo, pasta, parecer_conta=False)
                        self.checar_remocao(alvo, pasta)

    def git_indice(self, sub, args, pastas, opcoes=()):
        """CONFORMIDADE-ESCRITA-NO-INDICE: `git add` (toda opção) e `git update-index` (também `--cacheinfo`, nas duas
        formas) que nomeiam um caminho `quem: []` da política recusam, como a escrita na árvore. Toda palavra que não é
        opção conta como caminho (o modo e o sha do `--cacheinfo` não casam regra), e o pathspec que não é varredura (pasta,
        curinga ou magia) vale também pelo que alcança no índice e fora dele (`git ls-files -c -o`). A lista pela entrada (`--stdin`,
        `--index-info`, `--pathspec-from-file`) recusa: o hook não a lê. Limite: o comando sem o caminho (`git add -A`,
        `git add .`, `git commit -a`) segue fora."""
        if any(abreviacao_de(a, INDICE_PELA_ENTRADA) for a in args):
            self.barrar("R-CONFORMIDADE", f"git {sub} com a lista de caminhos pela entrada: o hook não a lê",
                        "passe os caminhos na linha de comando; o que for protegido é do usuário (R-DECISAO)")
        palavras, termos = [a for a in args if not a.startswith("-")], MARCADOR.termos()
        caminhos = palavras + [a.split(",", 2)[2] for a in palavras if a.count(",") >= 2]
        for pasta in dict.fromkeys(pastas):
            for c in caminhos:
                alvos = self.alvos_da_escrita(c, pasta)
                if not self.varredura(c) and (GLOB_DE_PATHSPEC.search(c) or c.startswith(":") or alvos[0].is_dir()):
                    alvos += filter(self.pode_ser_protegido, self.tracked_do_pathspec(c, pasta, opcoes, ("-c", "-o")))
                for alvo in alvos:
                    achado = self.caminho_barrado(Path(alvo)) if termos is False or termos.search(str(alvo)) else None
                    if achado and achado[3:4] == ("instalacao",):
                        self.barrar(achado[0], f"git {sub} grava no índice {achado[1]}", achado[2])

    def pode_ser_protegido(self, caminho):
        """Filtro barato para `git rm -r <pasta grande>`: só confere um por um o arquivo cujo caminho cita algum caminho
        da política (mais o perfil e o manifesto), ou todos se o papel só escreve numa lista (`escrita_permitida`).
        Só deixa de fora o que `caminho_barrado` não barraria."""
        if self.pol.get("escrita_permitida", {}).get(self.papel) is not None:
            return True
        if not hasattr(self, "_citacoes"):
            self._citacoes = tuple({e["caminho"].removeprefix("~/").rstrip("/").rsplit("*", 1)[-1] for e in self.pol["caminhos"]}
                                   | {".forge/perfil", MANIFESTO})
        return any(t in caminho for t in self._citacoes)

    @staticmethod
    def varredura(pathspec):
        """O pathspec seleciona tudo (`.`, `*`, `:/`, `:(top)`): `git checkout -- .` não troca arquivo que já está igual."""
        return MAGIA_DE_PATHSPEC.sub("", pathspec, 1) in ("", ".", "./", "*")

    def pathspecs_do_git(self, sub, args, pasta):
        """(pathspecs do comando, tem origem): o que é caminho em `git rm|mv|checkout|restore`. `checkout` sem `--` toma
        como caminho a palavra que existe, tem curinga ou magia (`git checkout <branch>` não é caminho); a primeira
        palavra que não for caminho é a origem (`git checkout <ref> <caminho>`)."""
        antes, depois = (args[:args.index("--")], args[args.index("--") + 1:]) if "--" in args else (args, [])
        positivas, i = [], 0
        while i < len(antes):
            if antes[i].startswith("-"):
                valor = ("-s", "--source") if sub == "restore" else CHECKOUT_COM_VALOR if sub == "checkout" else ()
                i += 2 if antes[i] in valor else 1
            else:
                positivas.append(antes[i])
                i += 1
        com_origem = sub == "restore" and any(a in ("-s", "--source") or a.startswith("--source=") for a in args)
        if sub == "checkout":
            if depois:  # `git checkout <ref> -- <caminhos>`: o que vem antes do `--` é a origem
                com_origem = bool(positivas)
                positivas = []
            else:
                caminhos = [a for a in positivas if GLOB_DE_PATHSPEC.search(a) or a.startswith(":")
                            or os.path.lexists(self.resolver(a, pasta))]
                com_origem = len(caminhos) < len(positivas) and bool(caminhos)
                positivas = caminhos
        return positivas + depois, com_origem

    def tracked_do_pathspec(self, pathspec, pasta, opcoes, quais=()):
        """Os arquivos do índice que o git alcança com o pathspec (`git ls-files`, só leitura; `quais` (`-c`, `-o`) soma
        os de fora do índice). Se o git não responde (fora de repositório, limite de tempo), vale o pathspec literal:
        o `git rm` também não teria o que fazer."""
        if not Path(pasta).is_dir():
            return []
        try:
            cod, saida = forge_check().git(pasta, *opcoes, "ls-files", "-z", *quais, "--", pathspec, bruto=True)
        except (OSError, subprocess.SubprocessError):
            cod, saida = 1, b""
        if cod:
            if GLOB_DE_PATHSPEC.search(pathspec) or pathspec.startswith(":"):
                self.barrar("R-CONFORMIDADE", f"o git não resolveu o pathspec {pathspec!r}",
                            "use o caminho do arquivo, sem magia nem curinga (na dúvida, recusa)")
            return []
        return [str(Path(pasta) / n) for n in forge_check().nomes_z(saida)]

    def git_troca(self, sub, args, globais):
        """N2 (L20b, C-20b-1): `git replace` (toda forma), `update-ref` de `refs/replace/*` ou pela entrada padrão (o hook
        não a lê), `fast-import` (grava refs pela entrada padrão), refspec de `fetch`/`push` e `-c` com `refs/replace` ou
        `core.useReplaceRefs`: o objeto trocado vale para todas as worktrees e o forge-check o leria no lugar do parecer."""
        motivo = None
        if sub == "replace":
            motivo = "git replace"
        elif sub == "fast-import" or sub == "update-ref" and "--stdin" in args:
            motivo = f"git {sub} pela entrada padrão (o hook não a lê)"
        elif any(map(CITA_TROCA.search, globais)) or sub in REFS_DE_TROCA and any(map(CITA_TROCA.search, args)):
            motivo = f"git {sub} com refs/replace, grafts ou core.useReplaceRefs"
        if motivo:
            self.barrar("R-REVIEW", f"{motivo}: objeto de troca faz o forge-check ler outro parecer",
                        "não troque objetos do repositório; o parecer vale pelo que está commitado")

    def config_da_linha(self, valor):
        """`git -c <chave>=<valor>`: alias troca o subcomando que o hook leu; refspec de `remote.*.fetch|push` que
        escreve na integração vale como o da linha."""
        chave, _, refspec = valor.partition("=")
        if chave.lower().startswith(("alias.", "help.autocorrect")):  # A13 da segurança E63.7: `stge` vira `stage`
            self.barrar("R-REVIEW", f"git -c {chave}: o alias da linha troca o subcomando que o hook leu (e o "
                                    "help.autocorrect, a correção do nome)",
                        "rode o subcomando do git direto, sem alias", trava=TRAVA_OPACA)
        if REFSPEC_NA_CONFIG.fullmatch(chave) and ":" in refspec and self.ref_local_da_integracao(refspec.split(":", 1)[1]):
            self.integracao_movida(f"git -c {chave}")

    def git_integracao(self, sub, args, pasta, ramos):
        """N5 (L22): o que muda a branch de integração depois do merge revisado. Em qualquer branch, `update-ref` e
        refspec de `fetch` que escrevem na integração; nela, commit (e `--amend`), `cherry-pick`, `revert`, `am`,
        `commit-tree`, `fast-import`, `reset <rev>` (todo modo), `merge --continue`, `pull --rebase` e `notes` que grava."""
        pos = parecer.posicionais(args, {"-m"}) if sub in ("update-ref", "symbolic-ref") else \
            [a for a in args if not a.startswith("-")]
        if sub == "update-ref" and pos and self.ref_local_da_integracao(pos[0]):
            self.integracao_movida(f"git update-ref {nome_da_branch(pos[0])}")
        if sub == "symbolic-ref" and len(pos) > 1 and (self.ref_local_da_integracao(pos[0]) or (
                pos[0] == "HEAD" and self.ref_local_da_integracao(pos[1]))):
            self.integracao_movida(f"git symbolic-ref {pos[0]} {pos[1]}")
        if sub in ("fetch", "pull"):
            destinos = [r.split(":", 1)[1] for r in parecer.posicionais(args, FETCH_COM_VALOR)[1:] if ":" in r]
            if any(map(self.ref_local_da_integracao, destinos)):
                self.integracao_movida(f"git {sub} <ref>:<integração>")
        relevante = sub in NA_INTEGRACAO_RECUSADOS | {"reset", "merge", "pull", "notes", "update-ref"}
        if not relevante or SAIDAS_DA_OPERACAO & set(args):
            return
        atual = self.ramo_em(pasta, ramos)
        if atual not in INTEGRACAO:
            return
        if sub in NA_INTEGRACAO_RECUSADOS:
            self.integracao_movida(f"git {sub} na {atual}")
        elif sub == "update-ref" and pos and pos[0] == "HEAD":
            self.integracao_movida(f"git update-ref HEAD na {atual}")
        elif sub == "merge" and "--continue" in args:
            self.integracao_movida(f"git merge --continue na {atual}")
        elif sub == "pull" and any(a == "-r" or a.startswith("--rebase") and a != "--rebase=false" for a in args):
            self.integracao_movida(f"git pull --rebase na {atual}")
        elif sub == "notes" and (pos[:1] or [None])[0] not in NOTAS_DE_LEITURA:
            self.integracao_movida(f"git notes {pos[0]} na {atual}")
        elif sub == "reset" and self.reset_com_revisao(args, pasta):
            self.integracao_movida(f"git reset <rev> na {atual}")

    @staticmethod
    def ref_local_da_integracao(ref):
        """`develop`, `refs/heads/develop`, `heads/develop`, `+develop`: a branch local de integração (a de rastreio do
        remoto não conta); o destino com curinga conta quando o prefixo dele alcança uma delas (`refs/heads/*`)."""
        ref = ref.lstrip("+")
        ref = "refs/" + ref if ref.startswith("heads/") else ref
        if ref.startswith("refs/remotes/"):
            return False
        if "*" in ref:
            prefixo = ref.split("*", 1)[0]
            return any(f"refs/heads/{b}".startswith(prefixo) or b.startswith(prefixo) for b in INTEGRACAO)
        return nome_da_branch(ref) in INTEGRACAO

    def reset_com_revisao(self, args, pasta):
        """`git reset` que move a branch: com modo (`--soft`, `--hard`...) e uma revisão que não é `HEAD`, ou sem modo com
        revisão antes do `--` que não é caminho existente. `git reset`, `git reset HEAD <arq>` e `git reset -- <arq>`
        só tiram do índice."""
        antes = args[:args.index("--")] if "--" in args else args
        revs = [a for a in parecer.posicionais(antes, RESET_COM_VALOR) if a != "HEAD"]
        if RESET_MODOS & set(args):
            return bool(revs)
        if args[len(antes) + 1:]:  # `git reset <rev> -- <caminho>`: só o índice
            return False
        return bool(revs) and not any(os.path.lexists(self.resolver(a, pasta)) for a in revs[:2])

    def integracao_movida(self, o_que):
        self.barrar("R-REVIEW", f"{o_que}: muda a integração depois do merge revisado", CONTORNO_DA_INTEGRACAO)

    def reescreve_historico(self, o_que):
        self.barrar("R-VERIFY", f"reescrever histórico ({o_que}) da main, develop ou homolog",
                    "faça um commit novo (git revert) em vez de reescrever", "historico")

    def git_trava(self, sub, args, pasta, ramos):
        """Atos perigosos do git (2.5): reescrever ou apagar a história das branches de integração é recusado para todos;
        descartar mudanças e reescrever branch já publicada só pedem confirmação no perfil iniciante."""
        positivos = [a for a in args if not a.startswith("-")]
        if sub in ("filter-branch", "filter-repo"):
            self.reescreve_historico(f"git {sub}")
        elif sub == "rebase":
            pos = parecer.posicionais(args, REBASE_COM_VALOR)
            atual = self.ramo_em(pasta, ramos)
            alvo = nome_da_branch(pos[1]) if len(pos) > 1 else atual
            if any(a in ("--abort", "--quit") for a in args):
                return
            if atual in INTEGRACAO or alvo in INTEGRACAO:
                self.reescreve_historico("git rebase")
            if alvo and git(pasta, "branch", "-r", "--list", f"*/{alvo}")[1].strip():
                self.perguntar("rebase")
        elif sub == "branch" and any(a == "--delete" or re.fullmatch(r"-[a-zA-Z]*[dD][a-zA-Z]*", a) for a in args):
            if any(nome_da_branch(b) in INTEGRACAO for b in positivos):
                self.barrar("R-VERIFY", "apagar a branch main, develop ou homolog",
                            "peça ao usuário (R-DECISAO)", "integracao")
        elif sub == "update-ref" and {"-d", "--delete"} & set(args):
            if any(nome_da_branch(b) in INTEGRACAO for b in positivos):
                self.barrar("R-VERIFY", "apagar a branch main, develop ou homolog (git update-ref -d)",
                            "peça ao usuário (R-DECISAO)", "integracao")
        elif (alvo := self.branch_movida(sub, args, positivos)) is not None:
            if nome_da_branch(alvo) in INTEGRACAO:
                self.reescreve_historico(f"git {sub} move a {nome_da_branch(alvo)}")
            if git(pasta, "branch", "-r", "--list", f"*/{nome_da_branch(alvo)}")[1].strip():
                self.perguntar("mover")
        elif sub == "commit" and emenda(args) and self.ja_enviado(pasta):
            self.barrar("R-VERIFY", "git commit --amend de commit já enviado (AGENTE-NAO-EMENDA-ENVIADO)",
                        "o commit enviado não se emenda: faça um commit novo", "historico")
        elif sub == "reset" and "--hard" in args:
            self.perguntar("descartar")
        elif sub == "clean" and (any(a == "--force" or re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", a) for a in args)
                                 and not any(a == "--dry-run" or re.fullmatch(r"-[a-zA-Z]*n[a-zA-Z]*", a) for a in args)):
            self.perguntar("limpar")
        elif sub == "checkout" and "." in args and "-b" not in args:
            self.perguntar("descartar")
        elif sub == "restore" and "." in args and (
                not {"--staged", "-S"} & set(args) or {"--worktree", "-W"} & set(args)):
            self.perguntar("descartar")

    @staticmethod
    def ja_enviado(pasta):
        """O HEAD está em alguma branch remota (`git branch -r --contains HEAD`); git que falha conta como enviado (falha fechada)."""
        cod, saida = git(pasta, "branch", "-r", "--contains", "HEAD")
        return bool(cod) or bool(saida.strip())

    @staticmethod
    def branch_movida(sub, args, positivos):
        """Branch que `checkout -B`, `switch -C`, `worktree add -B`, `branch -f` e `branch -M|-C` (ou `-m|-c` com força)
        recriam apontando para outro commit; senão None. No `-M|-C`, só a de integração:
        a de destino ou, no `-M`, a de origem."""
        forca = any(a == "--force" or re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", a) for a in args)
        curtas = "".join(a[1:] for a in args if re.fullmatch(r"-[a-zA-Z]+", a))
        move = "M" in curtas or forca and ("m" in curtas or "--move" in args)
        if sub == "branch" and (move or "C" in curtas or forca and ("c" in curtas or "--copy" in args)):
            candidatas = positivos[-1:] + (positivos[:1] if move and len(positivos) > 1 else [])
            return next((b for b in candidatas if nome_da_branch(b) in INTEGRACAO), None)
        if sub == "branch" and forca:
            return positivos[0] if positivos else None
        if sub == "worktree" and args[:1] == ["add"] and "-B" in args:
            return args[args.index("-B") + 1] if args.index("-B") + 1 < len(args) else None
        letra = {"checkout": "B", "switch": "C"}.get(sub)
        for i, a in enumerate(args):
            if letra and (re.fullmatch(rf"-[a-zA-Z]*{letra}", a) or (sub == "switch" and a == "--force-create")):
                return args[i + 1] if i + 1 < len(args) else None
        return None

    def git_config(self, args):
        """`git config` que grava identidade, `core.*`, assinatura, `include*`, alias ou `help.autocorrect` (A13): fora
        do papel de todos. Numa worktree, sem `--worktree` ele grava no `.git/config` comum a todas as cópias
        (R-CONFORMIDADE); o `help.autocorrect` e as chaves do merge, também com `--worktree`."""
        if any(a in CONFIG_LEITURA or a.startswith(("--get", "--show-")) for a in args):
            return
        chaves, pulo, subcomando = [], False, False
        for a in args:
            if pulo:
                pulo = False
            elif not chaves and not subcomando and a in ("set", "unset"):  # git 2.46: `git config set <chave> <valor>` grava
                subcomando = True  # as opções dele (`--all`, `--append`, `--comment`) vêm antes da chave e não contam
            elif a in CONFIG_COM_VALOR:
                pulo = True
            elif a == "--":  # depois do `--` tudo é chave ou valor, mesmo com `-` na frente (`mergeoptions -- --squash`)
                chaves += args[args.index("--") + 1:]
                break
            elif not a.startswith("-") or (chaves and a not in CONFIG_ESCOPO):  # depois da chave, toda palavra é valor
                chaves.append(a)
        grava = subcomando or len(chaves) > 1 or any(a in CONFIG_ESCRITA for a in args)  # só a chave é leitura
        if grava and any(CITA_TROCA.search(c) for c in chaves):  # N2: refspec de troca ou core.useReplaceRefs, todo escopo
            self.barrar("R-REVIEW", "git config com refs/replace ou core.useReplaceRefs: objeto de troca faz o forge-check "
                                    "ler outro parecer", "não troque objetos do repositório")
        if not (grava and chaves[:1] and CONFIG_PROTEGIDA.match(chaves[0])):
            return
        do_merge = bool(CONFIG_DO_MERGE.match(chaves[0])) or chaves[0].lower().startswith("help.autocorrect")  # A13
        if "--worktree" in args and not do_merge:  # as chaves do merge valem em toda worktree
            return
        dica = "deixe ao usuário (R-DECISAO)" if do_merge else "use --worktree ou deixe ao usuário (R-DECISAO)"
        self.barrar("R-CONFORMIDADE", f"git config grava {chaves[0]} na configuração compartilhada do repositório", dica)

    def git_tag(self, args, pasta):
        """No Forge, `git tag` só lista ou confere: sem argumento, ou só com opções de leitura (`-l`, `-v`, `-n`, `--contains`...).
        Criar, apagar ou mover tag é do release.yml (v0474, segurança A2)."""
        if not self.repositorio_do_forge(pasta):
            return
        curtas = {c for a in args if re.fullmatch(r"-[a-zA-Z0-9]+", a) for c in a[1:]}
        longas = {a.split("=", 1)[0] for a in args if a.startswith("--")}
        leitura = curtas & set("lvn") or longas & {"--list", "--verify", "--contains", "--no-contains", "--points-at",
                                                    "--merged", "--no-merged"}
        so_opcoes_de_leitura = curtas <= TAG_SO_LEITURA_CURTAS and longas <= TAG_SO_LEITURA_LONGAS
        if args and not (leitura and so_opcoes_de_leitura):
            self.barrar("R-FLUXO", f"git tag no repositório do Forge: {TAG_E_VERSAO}",
                        "só o release.yml cria a tag, sobre a main; para ler, use git tag -l", trava=TRAVA)

    def git_tags_no_envio(self, args, globais, pasta, sub="push"):
        """No Forge, nenhum envio leva tag: `--tags`, `--follow-tags`, `tag <nome>`, refspec com `refs/tags/` ou `v<número>`
        e `-c` com `push.followTags` ou refspec de tags (v0474, segurança A2). Na dúvida (remoto de nome `v1`), recusa."""
        posicionais = parecer.posicionais(args, PUSH_COM_VALOR)
        remoto = posicionais[0] if posicionais else None
        if not (self.repositorio_do_forge(pasta) or (remoto and parecer.aponta_para_o_forge(remoto))):
            return
        refs = posicionais  # o remoto entra também: com `--repo <remoto>`, o primeiro posicional já é refspec
        envia_tag = ({"--tags", "--follow-tags"} & {a.split("=", 1)[0] for a in args} or "tag" in refs
                     or any(TAG_NO_ENVIO.match(parte) for r in refs for parte in r.split(":"))
                     or any(TAG_NA_CONFIG.search(g) for g in globais))
        if envia_tag:
            self.barrar("R-FLUXO", f"git {sub} de tag para o Forge: {TAG_E_VERSAO}",
                        "envie só a branch; a tag nasce do release.yml, sobre a main", trava=TRAVA)

    def git_push(self, args, pasta, ramos, sub="push", troca=()):
        refs, repo = [], None
        pulo = None
        for a in args:
            if pulo:
                repo = a if pulo == "--repo" else repo
                pulo = None
            elif a in PUSH_COM_VALOR:
                pulo = a
            elif "=" in a and abreviacao_de(a, ("--repo",)):  # `--repo=<url>` e `--rep=<url>`: o repositório do envio
                repo = a.split("=", 1)[1]
            elif a.startswith("--force") or re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", a) or a.startswith("+"):
                self.barrar("R-VERIFY", "git push --force", "nunca force o push; refaça com um commit novo", "forca")
            elif a == "--mirror":  # 0.45.3 (decisão do dono): todas as refs de uma vez, e sobrescreve como o force
                self.barrar("R-VERIFY", "git push --mirror", "sobrescreve o remoto como um force push; "
                            f"{UMA_BRANCH_POR_VEZ}, com um commit novo", "forca")
            elif a == "--all":  # 0.45.3 (decisão do dono): o envio agrupado roda a suíte inteira e cai junto
                self.barrar("R-FLUXO", f"git {sub} --all envia todas as branches de uma vez", UMA_BRANCH_POR_VEZ)
            elif not a.startswith("-"):
                refs.append(a)
        remoto, refs = (refs[0] if refs else repo), refs[1:]
        if not refs and "--tags" in args:
            return
        atual = None
        destinos = []
        for r in refs or [None]:
            destino = r.split(":")[-1] if r else None
            if destino in (None, "", "HEAD"):
                atual = atual or self.ramo_em(pasta, ramos)
                destino = atual
            if "*" in destino and self.ref_local_da_integracao(destino):  # `refs/heads/*`: o curinga alcança a integração
                destino = "develop"
            destinos.append(nome_da_branch(re.sub(r"^heads/", "refs/heads/", destino)))
        for d in destinos:
            if d in ("main", "master"):
                self.barrar("R-MAIN", f"{PUSH_DIRETO} {d}", "abra um PR; a main é do usuário", "main", alvo=d)
            if d in INTEGRACAO:
                self.barrar("R-CONFORMIDADE", f"{PUSH_DIRETO} {d}", "abra um PR a partir de uma branch de trabalho",
                            "main", trava=TRAVA, alvo=d)
        # o remoto nomeado (a URL dele, resolvida no repositório da pasta), a URL dada ou, sem remoto, a pasta
        if self.alvo_do_forge(pasta, remoto=remoto) or (remoto and self.alvo_do_forge(pasta, remoto)) or (
                remoto and self.caminho_do_forge(pasta, remoto)):
            self.barrar("R-CONTRIB", f"push para {', '.join(map(str, destinos))}: {NO_FORGE}", SO_SUGERE)
        if remoto is None and (chave := self.destino_na_config(pasta)):
            self.barrar("R-CONTRIB", f"git {sub} sem remoto: `{chave}` escolhe o destino e o hook não confirma que não "
                                     f"é o Forge: {NO_FORGE}", SO_SUGERE)
        duvida = next((c for c in troca if c.lower().startswith("url.") or "$" in c
                       or parecer.aponta_para_o_forge(c.split("=", 1)[1])
                       or self.caminho_do_forge(pasta, c.split("=", 1)[1])), None)
        if duvida:  # na dúvida sobre o alvo, a sessão de projeto falha fechado (a do Forge não passa pela Guarda)
            self.barrar("R-CONTRIB", f"git {sub} com `{duvida.split('=', 1)[0]}` na linha troca o destino e o hook não "
                                     f"confirma que não é o Forge: {NO_FORGE}", SO_SUGERE)

    def git_no_forge(self, sub, args, pasta):
        """R-CONTRIB (diretriz 36): a sessão de outro projeto não cria branch nem grava commit ou ref no repositório do
        Forge (`GRAVA_NO_REPO`, `worktree add`, `branch <nome>`, `switch -c`, `checkout -b`, `--track`, `fetch` com
        destino), nem aponta um remoto para o Forge (`remote add|set-url`), o passo antes do envio."""
        cria = (sub in GRAVA_NO_REPO or sub == "worktree" and args[:1] == ["add"]
                or sub == "branch" and self.branch_grava(args)
                or sub in BRANCH_NOVA and any(self.cria_branch(BRANCH_NOVA[sub], a) for a in args)
                or sub == "fetch" and any(r.partition(":")[2] for r in parecer.posicionais(args, FETCH_COM_VALOR)[1:]))
        if cria and self.alvo_do_forge(pasta):
            self.barrar("R-CONTRIB", f"git {sub}{' add' if sub == 'worktree' else ''}: {NO_FORGE}", SO_SUGERE)
        if sub == "remote" and args[:1] in (["add"], ["set-url"]) and not self.clone_do_forge() and any(
                map(parecer.aponta_para_o_forge, args[1:])):
            self.barrar("R-CONTRIB", f"git remote {args[0]} com o Forge: {NO_FORGE}", SO_SUGERE)
        if sub == "config" and self.config_troca_destino(args, pasta):  # a sessão do Forge não chega à Guarda (E3.106)
            self.barrar("R-CONTRIB", f"git config que aponta o envio para o Forge (ou que o hook não confirma): {NO_FORGE}",
                        SO_SUGERE)

    def config_troca_destino(self, args, pasta):
        """`git config` que grava a URL de um remoto com o Forge ou com `$`, ou qualquer reescrita de URL (`insteadOf`,
        `pushInsteadOf`, cujo alvo o hook não confirma): o envio da mesma linha iria ao Forge sem o hook ver. O editor
        (`-e`, também agrupada, `--edit`, `edit`) grava o que o hook não vê: falha fechado (segurança A8). O valor que é
        caminho em `~/.forge-contrib` ou num clone do Forge também troca o destino (segurança A9)."""
        if args[:1] == ["edit"] or opcao_curta_presente(args, "e", "ft") or any(
                abreviacao_de(a, ("--edit",)) for a in args):
            return True
        if any(a.startswith(("--get", "--show-")) or a in CONFIG_LEITURA for a in args):
            return False
        palavras = [a for a in args if not a.startswith("-")]
        i = next((n for n, a in enumerate(palavras) if re.fullmatch(CHAVE_DO_DESTINO, a, re.I | re.S)), None)
        if i is None or i + 1 >= len(palavras):
            return False
        valor = " ".join(palavras[i + 1:])
        return (palavras[i].lower().startswith("url.") or "$" in valor or parecer.aponta_para_o_forge(valor)
                or self.caminho_do_forge(pasta, palavras[i + 1]))

    @staticmethod
    def cria_branch(opcoes, a):
        """A opção de `switch`/`checkout` cria branch: a curta, agrupada ou com o nome colado (`-qc`, `-cnova`), ou a
        longa por extenso ou abreviada como o git aceita, com ou sem `=valor` (`--cr`, `--create=nova`)."""
        curta, longas = opcoes
        nome = a.split("=", 1)[0]
        return bool(curta.match(a)) or len(nome) > 2 and nome.startswith("--") and any(o.startswith(nome) for o in longas)

    @staticmethod
    def branch_grava(args):
        """`git branch` que cria, apaga ou move: um nome posicional fora do modo de lista (na dúvida, grava). `--sort` e
        `--format` levam valor e não ligam a lista (`git branch --sort=refname nova` cria `nova`)."""
        if any(a.split("=", 1)[0] in BRANCH_LISTA for a in args):
            return False
        return bool(parecer.posicionais(args, BRANCH_COM_VALOR))

    # gh ----------------------------------------------------------------------------------------------
    @staticmethod
    def textos_da_api(args, pasta):
        """(textos, ilegivel) do `gh api`: o texto vem inline ou de arquivo (`-F query=@arq`, `--input arq`); o que não
        dá para ler (`--input -`, arquivo ausente) marca `ilegivel`."""
        textos, args = [], parecer.desagrupa_i(args)
        for i, a in enumerate(args):
            valor = args[i + 1] if a == "--input" and i + 1 < len(args) else a.split("=", 1)[-1]
            if a == "--input" or a.startswith("--input=") or re.search(r"=@", a) or (
                    a in ("-F", "--field") and i + 1 < len(args) and "=@" in args[i + 1]):
                arq = valor if a.startswith("--input") else (args[i + 1] if a in ("-F", "--field") else a).split("=@", 1)[-1]
                caminho = expandir_home(str(pasta / os.path.expandvars(arq)))
                try:  # E168.5 (A2): `/dev/stdin`, `/proc/self/fd/0` e FIFO não são o arquivo que o gh lê: ilegível
                    if any(p(caminho).startswith(("/dev/", "/proc/")) for p in (os.path.abspath, os.path.realpath)):
                        return textos, True
                    with open(os.open(caminho, os.O_RDONLY | os.O_NONBLOCK), "rb") as f:
                        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
                            return textos, True
                        textos.append(f.read().decode("utf-8"))
                except (OSError, ValueError):
                    return textos, True
            else:
                textos.append(a)
        return textos, False

    def graphql_perigoso(self, args, pasta):
        """Mutação do GraphQL que fecha, edita ou rotula PR: o ID é global (sem slug), então vale para toda sessão
        de projeto. O que não dá para ler (`--input -`, arquivo ausente) falha fechado."""
        textos, ilegivel = self.textos_da_api(args, pasta)
        return ilegivel or any("mutation" in t and CONTRIB_GRAPHQL.search(t) for t in textos)

    # R-CONTRIB: o rótulo afrouxa-regra é só do dono do Forge ------------------------------------------
    @staticmethod
    @lru_cache(maxsize=1)
    def conta_do_gh():
        """Login da conta autenticada no `gh` (`gh api user`), uma consulta por chamada do hook; vazio se não der para
        ler (falha fechado). O limite de tempo fica abaixo do timeout do hook (`TIMEOUT_DA_CONTA`)."""
        try:  # grupo próprio: no limite de tempo, o `kill` alcança também os filhos que seguram a saída aberta
            p = subprocess.Popen(["gh", "api", "user", "--jq", ".login"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL, text=True, start_new_session=True)
        except (OSError, subprocess.SubprocessError):
            return ""
        try:
            saida, _ = p.communicate(timeout=TIMEOUT_DA_CONTA)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(OSError):
                os.killpg(p.pid, signal.SIGKILL)
            p.kill()
            p.wait()
            return ""
        return saida.strip().lower() if p.returncode == 0 else ""

    @staticmethod
    def rotulos_pedidos(args):
        """Rótulos que `gh pr|issue edit|create` aplica (`--add-label`, `--label`, `-l`; vírgulas separam)."""
        saida = []
        for i, a in enumerate(args):
            if a in ("--add-label", "--label", "-l") and i + 1 < len(args):
                saida.append(args[i + 1])
            elif a.startswith(("--add-label=", "--label=")):
                saida.append(a.split("=", 1)[1])
            elif a.startswith("-l") and not a.startswith("--") and len(a) > 2:
                saida.append(a[2:].removeprefix("="))
        return [r.strip().lower() for v in saida for r in v.split(",")]

    @staticmethod
    def rotulos_removidos(args):
        """Rótulos que `gh pr|issue edit` tira (`--remove-label`; vírgulas separam): tirar o rótulo exige o dono como o
        `DELETE` em `issues/<n>/labels/<nome>`."""
        saida = []
        for i, a in enumerate(args):
            if a == "--remove-label" and i + 1 < len(args):
                saida.append(args[i + 1])
            elif a.startswith("--remove-label="):
                saida.append(a.split("=", 1)[1])
        return [r.strip().lower() for v in saida for r in v.split(",")]

    def aplica_afrouxa_regra(self, palavras, pasta, por_xargs=False):
        """True se o comando `gh` aplica (ou pode aplicar) ou tira o rótulo `afrouxa-regra` (`--remove-label` como o `DELETE`), `gh label clone`, ou cria ou renomeia um rótulo com
        esse nome: `gh pr|issue edit|create` com o rótulo, `gh label create|edit` que o cita, `gh api` em
        `issues/<n>[/labels]` ou `labels[/<nome>]` com o nome no texto e a mutação GraphQL de rótulo (o ID do rótulo
        não traz o nome: toda `addLabelsToLabelable`/`labelIds`/`createLabel`/`updateLabel` conta). O endpoint é
        comparado normalizado (`endpoint_normalizado`). Corpo ilegível conta."""
        pos = parecer.posicionais(palavras[1:], GH_COM_VALOR)
        grupo, sub = (pos + [None, None])[:2]
        if grupo in ("pr", "issue") and sub in ("edit", "create"):
            pedidos = self.rotulos_pedidos(palavras[1:]) + self.rotulos_removidos(palavras[1:])
            # A5: o valor que o hook não vê (variável, substituição, opção sem valor, entrada do xargs) pode ser o rótulo
            return (ROTULO_PROTEGIDO in pedidos or any(re.search(r"[`$]", r) for r in pedidos)
                    or palavras[-1] in ROTULO_COM_VALOR or por_xargs)
        if grupo == "alias" and sub in ("set", "import"):  # o alias do gh que cita o rótulo aplica sem que o hook o veja
            return any(CITA_ROTULO.search(a) for a in palavras[3:])
        if grupo == "label" and sub == "clone":  # cria ou sobrescreve rótulos de outro repositório, sem citar o nome
            return True
        if grupo == "label" and sub in ("create", "edit"):
            return any(ROTULO_PROTEGIDO in a.lower() for a in palavras[2:])
        if grupo != "api" or not parecer.metodo_mutante(palavras[2:]):
            return False
        args = palavras[2:]
        endpoint = endpoint_normalizado(parecer.endpoint_da_api(args))
        textos, ilegivel = self.textos_da_api(args, pasta)
        textos = [re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m[1], 16)), t) for t in textos]  # A5: escape JSON
        ilegivel = ilegivel or any(r"\u" in t for t in textos)  # o que não decodifica conta como ilegível
        junto = urllib.parse.unquote(" ".join(textos)).lower()
        if endpoint.lower() == "graphql":
            return ilegivel or any("mutation" in t and GRAPHQL_DE_ROTULO.search(t) for t in textos)
        if re.search(r"(^|/)(issues/[^/]+(/labels)?|labels(/[^/]+)?)$", endpoint, re.I):
            return ilegivel or ROTULO_PROTEGIDO in junto
        return False

    def rotulo_na_sessao_do_forge(self, comando, pasta, nivel=0):
        """R-CONTRIB: na sessão do Forge (pasta fora de projeto, onde o hook não aplica as demais regras), só confere o
        rótulo `afrouxa-regra`: percorre os comandos da linha, por baixo de lançadores, `bash -c`, `eval`, `$(...)` e
        crase. Linha que não dá para analisar e cita o rótulo (ou a mutação de rótulo do GraphQL) exige a conta do dono;
        outro erro sobe a `principal`, que barra se a linha cita o rótulo."""
        if nivel > PROFUNDIDADE:
            return
        for forma in formas_que_o_shell_le(comando):  # HOOK-CONTINUACAO-LINHA: a juntada e a do `$'…'` também
            self.rotulo_na_sessao_do_forge(forma, pasta, nivel)
        try:
            sem_heredoc, corpos = tirar_heredocs(comando)
            for interno in conteudos_de_crase(sem_heredoc):  # a crase é um `$(...)`: o mesmo caminho
                self.rotulo_na_sessao_do_forge(interno, pasta, nivel + 1)
            lidas = leituras(sem_heredoc)
            if lidas.ilegivel:
                if CITA_ROTULO.search(comando):
                    self.exigir_dono()
                return
            for palavras, _, _ in (parte for partes in lidas.partes for parte in partes):  # ADR 0013: as duas leituras
                while palavras and palavras[0] in CORPO_DE_LACO:
                    palavras = palavras[1:]
                escritas = palavras
                for palavras in sem_lancadores(escritas):  # a recusa é a união das leituras possíveis do lançador
                    for p in palavras:
                        if "$(" in p.replace(OPACO["$"], ""):
                            self.rotulo_na_sessao_do_forge(p, pasta, nivel + 1)
                    prog = Path(palavras[0].lstrip("`")).name if palavras else ""
                    if prog == "gh":
                        if parecer.gh_incerto(palavras):  # E168.9: o subcomando incerto pode aplicar o rótulo
                            self.exigir_dono()
                        self.gh_rotulo(parecer.ordem_do_gh(palavras), pasta, atras_do_xargs(escritas, palavras))
                        self.gh_pr_na_sessao_do_forge(palavras, pasta)
                    elif prog == "alias" and CITA_ROTULO.search(" ".join(palavras)):  # A5: o alias do shell guarda o rótulo
                        self.exigir_dono()
                    elif prog in SHELLS:
                        for i, a in enumerate(palavras[1:]):
                            if re.fullmatch(r"-[a-z]*c[a-z]*", a) and i + 2 < len(palavras):
                                self.rotulo_no_argumento(palavras[i + 2], pasta, nivel + 1)
                    elif prog == "eval":
                        self.rotulo_no_argumento(" ".join(palavras[1:]), pasta, nivel + 1)
            for dono, corpo in corpos:
                if not corpo_so_lido(dono):
                    for forma in [corpo, *formas_que_o_shell_le(corpo, True)]:  # A1: o corpo expandido também
                        self.rotulo_na_sessao_do_forge(forma, pasta, nivel + 1)
        except ValueError:
            if CITA_ROTULO.search(comando):
                self.exigir_dono()

    def rotulo_no_argumento(self, texto, pasta, nivel):
        """Argumento de `bash -c`/`eval`: o `shlex` mantém `\\`` entre aspas duplas, e o shell de fora o troca por crase antes
        de passar ao de dentro; confere o texto como veio e com `\\`` já virado crase (o que o shell de dentro executa)."""
        self.rotulo_na_sessao_do_forge(texto, pasta, nivel)
        if "\\`" in texto:
            self.rotulo_na_sessao_do_forge(texto.replace("\\`", "`"), pasta, nivel)

    def gh_api_cria_pr(self, parte, pasta):
        """FILA-22 (review da 0.43.2): o PR aberto pelo `gh api` (POST em `repos/<o>/<r>/pulls` ou `createPullRequest` no GraphQL,
        inline ou em arquivo; ilegível falha fechado) segue a política `pr_criar`, como o `gh pr create`."""
        if not parte or parte[0] != "api" or self.pode("pr_criar") or not parecer.metodo_mutante(parte[1]):
            return
        endpoint = parecer.endpoint_da_api(parte[1])
        abre_pr = bool(CRIAR_PR_POR_API.search(endpoint))
        if not abre_pr and parecer.ENDPOINT_GRAPHQL.search(endpoint):
            textos, ilegivel = self.textos_da_api(parte[1], pasta)
            abre_pr = ilegivel or any(CRIAR_PR_NO_GRAPHQL.search(t) for t in textos)
        if abre_pr:
            self.barrar("R-CONFORMIDADE", f"gh api que abre PR {self.so_de('pr_criar')} (papel: {self.papel})", "peça ao tech-lead")

    def gh_pr_na_sessao_do_forge(self, palavras, pasta="."):
        """FILA-22 (0.43.2, N4; diretiva do dono "Jarvis só interface"): na sessão do Forge, `gh pr create` e `gh pr merge` seguem a
        política dos projetos (`pr_criar`, `pr_merge_integracao`): o jarvis e os papéis fora da lista não abrem nem mesclam PR.
        O tech-lead abre o PR e o `bin/forge-fechar` mescla."""
        parte = parecer.analisar(palavras)
        if parte and parte[0] == "pr" and not self.pode("pr_criar"):
            self.barrar("R-CONFORMIDADE", f"gh pr create {self.so_de('pr_criar')} (papel: {self.papel})", "peça ao tech-lead")
        self.gh_api_cria_pr(parte, pasta)
        if parte and parte[0] == "prmerge" and not self.pode("pr_merge_integracao"):
            self.barrar("R-CONFORMIDADE", f"gh pr merge {self.so_de('pr_merge_integracao')} (papel: {self.papel})",
                        "peça ao tech-lead (bin/forge-fechar)")

    def gh_rotulo(self, palavras, pasta, por_xargs=False):
        """R-CONTRIB: na sessão do Forge, só a conta do dono do Forge aplica o rótulo `afrouxa-regra`; qualquer outra conta,
        ou erro ao ler a conta ou o dono, barra. Os outros rótulos e comandos não mudam."""
        if not self.aplica_afrouxa_regra(palavras, pasta, por_xargs):
            return
        self.exigir_dono()

    def exigir_dono(self):
        """Barra se a conta do `gh` não é a dona do Forge (dono lido do `repository` do `plugin.json`) ou se não deu para ler."""
        try:
            dono = parecer.slug_do_forge().split("/")[0].lower()
        except (OSError, ValueError):
            dono = ""
        conta = self.conta_do_gh()
        if not dono or not conta or conta != dono:
            self.barrar("R-CONTRIB", f"só o dono do Forge aplica ou delega o rótulo afrouxa-regra (conta do gh: {conta or 'ilegível'})",
                        "avise o dono: só ele aplica, na conta dele")

    def gh_contrib(self, palavras, pasta, repo_env):
        """R-CONTRIB (diretriz 36): na sessão de outro projeto, o `gh` no Forge só lê (`GH_SO_LE`): abrir, comentar,
        editar, fechar, rotular, criar release ou rodar workflow é recusado. O alvo vem de `-R`, de `GH_REPO`, de URL
        entre os argumentos ou da pasta; no `gh api`, do endpoint (`gh_api_no_forge`). A sessão do Forge não passa por
        aqui (fora de projeto, só o rótulo é conferido)."""
        pos = parecer.posicionais(palavras[1:], GH_COM_VALOR)
        grupo, sub = (pos + [None, None])[:2]
        if grupo == "api":
            self.gh_api_no_forge(palavras[2:], pasta, repo_env)
            return
        if grupo not in GH_DO_REPO or sub is None or sub in GH_SO_LE:
            return
        repo = parecer.opcao(palavras[1:], "--repo", "-R") or repo_env
        if not (self.alvo_do_forge(pasta, repo) or any(parecer.aponta_para_o_forge(a) for a in pos[2:])):
            return
        if grupo == "issue" and sub == "create":
            # Issue nova no Forge é da pessoa: `forge sugerir`, no terminal dela, fora do Claude (onde o hook não roda).
            self.barrar("R-CONTRIB", "gh issue create no Forge: só a pessoa envia sugestão, no terminal dela, fora do "
                                     "Claude, com `forge sugerir`", "guarde o texto com `forge sugerir --guardar \"<texto>\"` "
                                     "e avise a pessoa")
        self.barrar("R-CONTRIB", f"gh {grupo} {sub}: {NO_FORGE}", SO_SUGERE)

    def gh_api_no_forge(self, args, pasta, repo_env):
        """`gh api` que muda algo no Forge, pelo slug do endpoint (também a URL completa e o `api/v3/`). O ID numérico
        (`repositories/<n>`), o endpoint com variável e a mutação do GraphQL (ID global) não dizem o repositório: na
        sessão de projeto, falham fechado."""
        if not parecer.metodo_mutante(args):
            return
        endpoint = parecer.endpoint_da_api(args)
        if e_graphql(endpoint):
            alvo = self.graphql_perigoso(args, pasta)
        else:
            caminho = endpoint_normalizado(endpoint)
            dono = re.match(r"repos/([^/]+/[^/]+)", caminho, re.I)
            if dono and "{" not in dono.group(1):
                alvo = "$" in dono.group(1) or self.alvo_do_forge(pasta, dono.group(1))
            elif dono or "{owner}" in caminho:  # `{owner}/{repo}`: o gh usa o GH_REPO ou o repositório da pasta
                alvo = self.alvo_do_forge(pasta, repo_env)
            else:
                alvo = not caminho or "$" in caminho or caminho.lower().startswith("repositories/")
        if alvo:
            self.barrar("R-CONTRIB", f"gh api que muda algo no Forge (ou cujo repositório o hook não confirma): {NO_FORGE}",
                        SO_SUGERE)

    def gh_trava(self, palavras, pasta):
        """Atos perigosos do `gh` (2.5): apagar o repositório e torná-lo público são recusados para todos (a pessoa faz
        pelo site do GitHub); arquivar só pede confirmação no perfil iniciante. Cobre `gh repo` e `gh api`."""
        pos = parecer.posicionais(palavras[1:], GH_COM_VALOR | {"--visibility"})
        grupo, sub = (pos + [None, None])[:2]
        apagar = ("R-CONFORMIDADE", "apagar o repositório", "só o usuário, pelo site do GitHub (R-DECISAO)", "apagar")
        publico = ("R-CONFORMIDADE", "tornar o repositório público", "só o usuário, pelo site do GitHub (R-DECISAO)",
                   "publico")
        if grupo == "repo" and sub == "delete":
            self.barrar(*apagar)
        elif grupo == "repo" and sub == "archive":
            self.perguntar("arquivar")
        elif grupo == "repo" and sub == "edit":
            if (parecer.opcao(palavras[1:], "--visibility", "--visibility") or "").lower() == "public":
                self.barrar(*publico)
        elif grupo == "repo" and sub in REPO_CRIAR:
            if parecer.bandeira(palavras[1:], CRIAR_COM_VALOR, {"--public"}):
                self.barrar(*publico)
            if not parecer.bandeira(palavras[1:], CRIAR_COM_VALOR, {"--private", "--internal"}):
                self.barrar(*publico)
        elif grupo == "api" and parecer.metodo_mutante(palavras[2:]):
            args = palavras[2:]
            if (parecer.opcao(args, "--method", "-X") or "").upper() == "DELETE" and REPO_APAGAR.match(
                    parecer.endpoint_da_api(args)) or GRAPHQL_APAGAR.search(" ".join(args)):
                self.barrar(*apagar)
            if VISIBILIDADE_PUBLICA.search(" ".join(args)) or self.input_publica(args, pasta):
                self.barrar(*publico)
            if self.api_publica(args, pasta):
                self.barrar(*publico)

    def consulta_ilegivel(self, args):
        """GRAPHQL-CONSULTA-EM-VARIAVEL (E168.1, decisão do dono de 24/11, opção a; C1 de v0480-repo-publico-v2): o `gh api`
        do GraphQL (ou de endpoint com expansão) com palavra que o hook não lê, em todo papel: a expansão fora de aspas
        (o bash a divide em palavras) e, entre aspas duplas, fora do valor de uma opção ou de um campo de nome literal que
        não é `query`. O arquivo e a entrada padrão que o hook não lê já recusam antes (GH-MERGE-ADMIN, R-CONTRIB)."""
        args = parecer.desagrupa_i(args)
        endpoint = parecer.endpoint_da_api(args)
        if not (e_graphql(endpoint) or parecer.expande(endpoint)):
            return False
        vistas, j = expansao_por_palavra(self.texto_da_linha), 0
        while j < len(args):
            a, j = args[j], j + 1
            opcao = a if a in parecer.API_COM_VALOR else None
            if opcao:
                a, j = (args[j] if j < len(args) else ""), j + 1
            nivel = vistas.get(a, 2) if parecer.expande(a) or CURINGA.search(a) or CHAVES.search(a) else 0
            if nivel == 2:
                return True
            if nivel == 0 or opcao and opcao not in CAMPOS_DA_API:
                continue  # literal, ou o valor entre aspas de -H, --jq, -X: uma palavra só, fora da consulta
            colado = CAMPO_COLADO.fullmatch(a)
            chave, igual, _ = (a if opcao else colado[1] if colado else "").partition("=")
            if not igual or parecer.expande(chave) or chave.lower() == "query":
                return True
        return False

    def api_publica(self, args, pasta):
        """CONFORMIDADE-REPO-CREATE-PUBLICO (A2): `gh api` mutante que cria ou edita repositório sem a visibilidade privada
        explícita, decidido pelo nome do campo (E141.7). REST: criar (`user/repos`, `orgs/<o>/repos`,
        `repos/<o>/<r>/generate`) pede o campo `private=true` ou `visibility=private|internal` (com `--input`, no corpo);
        criar e editar recusam o campo de visibilidade com outro valor e falham fechado no que o hook não lê e no
        endpoint com segmento vazio ou de ponto. GraphQL: `graphql_publica`."""
        args = parecer.desagrupa_i(args)
        endpoint = endpoint_normalizado(parecer.endpoint_da_api(args))
        campos, corpo = self.campos_da_api(args, pasta)
        if e_graphql(endpoint):
            texto = " ".join(args + self.textos_da_api(args, pasta)[0])
            return bool(GRAPHQL_DO_REPO.search(texto)) and self.graphql_publica(campos, corpo, GRAPHQL_CRIA_REPO.search(texto))
        if API_SEGMENTO_ESTRANHO.search(endpoint):
            return True
        cria = bool(API_CRIA_REPO.fullmatch(endpoint))
        if not cria and not API_DO_REPO.fullmatch(endpoint):
            return False
        if not parecer.textos_do_gh_api(args, pasta)[1]:
            return True
        if not all(self.privado_rest(campos + (corpo or []))):
            return True
        return cria and not any(self.privado_rest(campos if corpo is None else corpo))

    @staticmethod
    def campos_da_api(args, pasta):
        """(campos, corpo) que o `gh api` envia: os pares (chave, valor) de `-f`/`-F`/`--field`/`--raw-field`, separados,
        colados (`-Fprivate=false`) ou com `=`, com o `@arq` lido (None se o hook não lê); e os do topo do JSON do
        `--input` (None sem ele; [] se não é objeto). O valor de outra opção (`-H -Fx=y`) não é campo."""
        campos, corpo, j = [], None, 0
        while j < len(args):
            a, j = args[j], j + 1
            colado = CAMPO_COLADO.fullmatch(a)
            if a in parecer.API_COM_VALOR:  # o valor vem separado: campo, corpo ou valor de outra opção
                valor, j = (args[j] if j < len(args) else ""), j + 1
                if a == "--input":
                    corpo = Guarda.corpo_da_api(valor, pasta)
                elif a in CAMPOS_DA_API:
                    campos.append(Guarda.campo_da_api(valor, pasta))
            elif a.startswith("--input="):
                corpo = Guarda.corpo_da_api(a.split("=", 1)[1], pasta)
            elif colado:
                campos.append(Guarda.campo_da_api(colado[1], pasta))
        return campos, corpo

    @staticmethod
    def campo_da_api(texto, pasta):
        chave, _, valor = texto.partition("=")
        if valor.startswith("@"):  # o gh lê o arquivo; a leitura é a de `textos_do_gh_api` (GH-API-LEITURA-UNICA)
            lidos, legivel = parecer.textos_do_gh_api([texto], pasta)
            valor = lidos[0] if legivel else None
        return chave, valor

    @staticmethod
    def corpo_da_api(arq, pasta):
        lidos, legivel = parecer.textos_do_gh_api(["--input", arq], pasta)
        if not legivel:
            return CORPO_ILEGIVEL
        dados = json.loads(lidos[0], object_pairs_hook=tuple)  # objeto vira tupla de pares, com a chave repetida
        return list(dados) if isinstance(dados, tuple) else []

    @staticmethod
    def privado_rest(pares):
        """Para cada campo de visibilidade (`private`, `visibility`, também `private[x]` e com outra caixa), True só se
        é o nome exato com o valor privado."""
        saida = []
        for chave, valor in pares:
            nome = chave.split("[", 1)[0].lower()
            if nome in PRIVADO_REST:
                valor = "true" if valor is True else valor
                saida.append(chave == nome and isinstance(valor, str) and valor.strip().lower() in PRIVADO_REST[nome])
        return saida

    @staticmethod
    def graphql_publica(campos, corpo, cria):
        """GraphQL: o `visibility` do input, literal na query (sem strings nem comentários, a vírgula como espaço) ou no
        campo `<var>[visibility]` ou a chave `visibility` nas `variables` do `--input`, fora de PRIVATE e INTERNAL recusa,
        e criar sem ele também. Falha fechado no valor ilegível, na expansão do shell num campo (vira outros argumentos),
        em mais de um `query` e na string sem fechamento (A8)."""
        if corpo is CORPO_ILEGIVEL or any(v is None for _, v in campos):
            return True
        if any(parecer.expande(f"{k}={v}") for k, v in campos if k != "query"):
            return True
        pares = campos + (corpo or [])
        if any(GRAPHQL_CONTROLE.search(v) for k, v in pares if k == "query" and isinstance(v, str)):
            return True
        textos = [v for k, v in pares if isinstance(v, str) and k == "query"]
        if len(textos) > 1:  # A8: o gh manda só o último `query`, e o hook não sabe qual vai ao servidor
            return True
        if any(m["fecha"] == "" for v in textos for m in GRAPHQL_SEM_TEXTO.finditer(v)):  # A8: string sem fechamento
            return True
        consulta = " ".join(GRAPHQL_SEM_TEXTO.sub(" ", v) for k, v in pares if k == "query" and isinstance(v, str))
        valores = GRAPHQL_VISIBILIDADE.findall(consulta.replace(",", " "))
        da_var = [(k.split("[")[0], v) for k, v in campos if "[visibility]" in k.lower()]
        usados = [v for n, v in da_var if re.search(rf"\${re.escape(n)}\b", consulta)]  # A2: só a variável da consulta
        valores += [x for k, v in corpo or [] if k == "variables" for x in Guarda.visibilidades_json(v)]
        publica = any(v not in ("PRIVATE", "INTERNAL") for v in valores + [v for _, v in da_var])
        return publica or bool(cria) and not valores + usados

    @staticmethod
    def visibilidades_json(valor):
        """Os valores de toda chave `visibility` do objeto JSON lido em tuplas de pares, em qualquer nível."""
        if not isinstance(valor, tuple):
            return []
        return [x for k, v in valor for x in ([v] if k == "visibility" else []) + Guarda.visibilidades_json(v)]

    @staticmethod
    def input_publica(args, pasta):
        """`gh api --input arq` com `private:false`/`visibility:public` no corpo. No endpoint do repositório, PATCH ou PUT
        com corpo que não dá para ler (`--input -`, arquivo ausente) falha fechado."""
        for i, a in enumerate(args):
            if a != "--input" and not a.startswith("--input="):
                continue
            arq = a.split("=", 1)[1] if "=" in a else (args[i + 1] if i + 1 < len(args) else "")
            try:
                if VISIBILIDADE_PUBLICA.search(Path(expandir_home(str(pasta / os.path.expandvars(arq)))).read_text(encoding="utf-8")):
                    return True
            except (OSError, ValueError):
                metodo = (parecer.opcao(args, "--method", "-X") or "").upper()
                if metodo in ("PATCH", "PUT") and REPO_APAGAR.match(parecer.endpoint_da_api(args)):
                    return True
        return False

    def atualizacao(self, palavras, so_binarios=False):
        """`forge atualizar`, `forge voltar-versao` e os binários `forge-atualizar` e `forge-voltar-versao`, direto ou por baixo de
        `env`, `script` (terminal falso), interpretador ou aspas: o agente não roda (R-CONFORMIDADE); a pessoa roda no terminal."""
        todas = [w.strip("'\"`;()") for p in palavras for w in p.split()]
        direto = nome_do_caminho(palavras[0]) in ("forge", *BINARIOS_DE_ATUALIZACAO)  # só o comando em si, não o texto que ele recebe
        for i, palavra in enumerate(todas[:1] if direto else todas):
            nome = nome_do_caminho(palavra)
            sub = next((x for x in todas[i + 1:] if not x.startswith("-")), "")
            e_sugerir = nome == "forge-sugerir" or (nome == "forge" and sub == "sugerir")
            if e_sugerir:
                if guardar_exato(self.linha):  # guardar na fila é do agente; enviar é da pessoa
                    continue
                if nome == "forge" and so_binarios:
                    continue
                self.barrar("R-CONFORMIDADE", f"`{nome}{' sugerir' if nome == 'forge' else ''}` envia ao Forge o que o agente escreveu",
                            "quem envia a sugestão é você, no seu terminal: `forge sugerir --fila`", "sugerir")
                continue
            if nome in BINARIOS_DE_ATUALIZACAO or (nome == "forge" and not so_binarios and sub in SUBCOMANDOS_DE_ATUALIZACAO):
                self.barrar("R-CONFORMIDADE", f"`{nome}{' ' + sub if nome == 'forge' else ''}` troca o plugin e mexe no projeto",
                            "quem roda é a pessoa, no terminal (rode no terminal: forge atualizar); o agente só oferece e explica",
                            "atualizar")

    def claude(self, args):
        """Instalação intocável (2.2): dentro da sessão, `claude plugin` e `claude config` não mudam o Forge nem a
        configuração; ler, validar, listar e `plugin update` (o caminho oficial de atualização) continuam livres. A pessoa faz no terminal dela."""
        pos = [a for a in args if not a.startswith("-")]
        sub = pos[1] if pos[:1] in (["plugin"], ["plugins"]) and len(pos) > 1 else None
        muda = (pos[:1] in (["plugin"], ["plugins"]) and (sub in ("install", "uninstall", "remove", "disable") or (
                sub == "marketplace" and pos[2:3] in (["add"], ["remove"])))) or (
            pos[:1] == ["config"] and pos[1:2] in (["set"], ["add"], ["remove"]))
        if muda:
            self.barrar("R-CONFORMIDADE", f"claude {' '.join(pos[:3])} altera a instalação do Forge",
                        f"só o usuário, no terminal dele; {SUGESTAO}", "instalacao")

    CORRIGIR_DO_MERGE = "o dono mescla pela interface do GitHub, fora dos hooks do agente (R-DECISAO)"

    def gh_alias(self, palavras):
        """N1 (C-N1-4): `gh alias set|import|delete` grava a configuração do usuário e troca o comando que os hooks leem."""
        pos = parecer.posicionais(palavras[1:], GH_COM_VALOR)
        if pos[:2] in (["alias", "set"], ["alias", "import"], ["alias", "delete"]):
            self.barrar("R-REVIEW", f"gh alias {pos[1]}: o alias do gh troca o comando que os hooks leem",
                        "rode o comando do gh por extenso; o alias é configuração do usuário (R-DECISAO)")

    def gh_admin(self, palavras, parte):
        """GH-MERGE-ADMIN (R-MAIN): `gh pr merge` com `--admin` (qualquer valor) pula a proteção do GitHub: recusa em
        qualquer papel, base e pasta, antes de toda saída antecipada de `gh`."""
        if parte and parte[0] == "prmerge" and parecer.usa_admin(palavras[1:]):
            self.barrar("R-MAIN", "gh pr merge com --admin desvia a proteção da branch", self.CORRIGIR_DO_MERGE)

    def gh_api_de_merge(self, args, pasta):
        """GH-MERGE-ADMIN (R-MAIN): o `gh api` mutante de merge (REST ou GraphQL, inline ou em arquivo) também desvia a
        proteção. O GraphQL que não dá para ler (`--input -`, arquivo ausente) falha fechado."""
        endpoint = parecer.endpoint_da_api(args)
        merge = bool(parecer.MERGE_POR_API.search(endpoint))
        if not merge and parecer.ENDPOINT_GRAPHQL.search(endpoint):
            textos, ilegivel = self.textos_da_api(args, pasta)
            merge = ilegivel or any(parecer.MERGE_NO_GRAPHQL.search(t) for t in textos)
        if merge:
            self.barrar("R-MAIN", "gh api que mescla PR (merge REST ou GraphQL) pode desviar a proteção da branch",
                        self.CORRIGIR_DO_MERGE)

    def configs_do_gh(self, config_env=None):
        """Os config.yml que o gh pode ler: o de GH_CONFIG_DIR (linha, `export` ou ambiente), senão o de XDG_CONFIG_HOME/gh,
        senão o de ~/.config/gh; e sempre o de ~/.claude/gh (onde a estação guarda a configuração)."""
        pasta = config_env or self.ambiente.get("GH_CONFIG_DIR") or os.environ.get("GH_CONFIG_DIR")
        xdg = self.ambiente.get("XDG_CONFIG_HOME") or os.environ.get("XDG_CONFIG_HOME")
        if not pasta:
            pasta = os.path.join(xdg, "gh") if xdg else os.path.join(Path.home(), ".config", "gh")
        return list(dict.fromkeys(Path(os.path.expanduser(p)) / "config.yml"
                                  for p in (pasta, os.path.join(Path.home(), ".claude", "gh"))))

    def gh_pelo_alias(self, palavras, pasta, repo_env, por_xargs, config_env):
        """N1 resto (0.45.3): `gh <nome>` com `nome` no `aliases:` do gh roda a expansão; ela passa pelas mesmas regras.
        Devolve True se o nome não é comando do gh (o que roda é só a expansão)."""
        nome = palavras[1] if len(palavras) > 1 else ""
        if not nome or nome.startswith("-"):
            return False
        expansoes = []
        for arquivo in self.configs_do_gh(config_env):
            try:
                texto = arquivo.read_text(encoding="utf-8")
            except FileNotFoundError:
                continue
            except (OSError, ValueError):
                texto = None
            try:
                if texto is None:
                    raise AliasIlegivel(str(arquivo))
                aliases = aliases_do_gh(texto)
            except AliasIlegivel:
                if nome in COMANDOS_DO_GH:
                    continue
                self.barrar("R-REVIEW", f"gh {nome}: o hook não lê os aliases do gh em {arquivo}",
                            "rode o comando do gh por extenso")
            if nome in aliases:
                expansoes.append(aliases[nome])
        for expansao in expansoes:
            if expansao.startswith("!"):
                self.barrar("R-REVIEW", f"gh {nome}: alias de shell (`!`) do gh roda o que o hook não lê",
                            "rode o comando direto, sem alias")
            novas = expandir_alias_do_gh(expansao, palavras[2:])
            if not novas:
                self.barrar("R-REVIEW", f"gh {nome}: alias do gh que o hook não lê", "rode o comando do gh por extenso")
            novas = [palavras[0], *novas]  # o mesmo programa; não roda nada (é a leitura da expansão)
            self.gh(novas, parecer.analisar(novas), pasta, repo_env, por_xargs, config_env, alias=False)
        return bool(expansoes) and nome not in COMANDOS_DO_GH

    def gh(self, palavras, parte, pasta, repo_env=None, por_xargs=False, config_env=None, alias=True):
        if parecer.gh_incerto(palavras):  # E168.9: na dúvida sobre o subcomando, recusa, sem escolher leitura
            self.barrar("R-CONFORMIDADE", *parecer.GH_INCERTO)
        palavras = parecer.ordem_do_gh(palavras)  # E168.5: toda trava do gh lê o subcomando logo depois do `gh`
        if alias and self.gh_pelo_alias(palavras, pasta, repo_env, por_xargs, config_env):
            return
        self.gh_trava(palavras, pasta)
        self.gh_contrib(palavras, pasta, repo_env)
        if self.sessao_forge:
            self.gh_rotulo(palavras, pasta, por_xargs)
        self.gh_admin(palavras, parte)  # antes de toda saída antecipada: não depende de branch, base nem raiz
        self.gh_alias(palavras)
        if not parte:
            return
        if parte[0] == "pr" and not self.pode("pr_criar"):
            self.barrar("R-CONFORMIDADE", f"gh pr create {self.so_de('pr_criar')} (papel: {self.papel})",
                        "peça ao tech-lead")
        elif parte[0] == "prmerge":
            raiz = self.h.raiz
            branch = parecer.branch_do_pr(raiz, parte[2])
            if not branch:
                return  # o parecer pede o nome da branch
            base = parecer.base_do_pr(raiz, branch)
            if base in ("main", "master"):
                self.barrar("R-MAIN", f"gh pr merge de `{branch}` (base {base}) é do usuário",
                            "deixe o PR aberto e peça ao usuário", alvo=base)
            if not self.pode("pr_merge_integracao"):
                self.barrar("R-CONFORMIDADE", f"gh pr merge {self.so_de('pr_merge_integracao')} "
                                              f"(papel: {self.papel})", "peça ao tech-lead")
        elif parte[0] == "api":
            self.gh_api_cria_pr(parte, pasta)
            args = parte[1]
            if parecer.metodo_mutante(args) and (
                    API_ADMIN.search(parecer.endpoint_da_api(args))
                    or any("mutation" in a and GRAPHQL_PERIGOSO.search(a) for a in args)):
                self.barrar("R-CONFORMIDADE", "gh api que altera refs, regras, acessos ou faz merge",
                            "use gh pr/git pelo papel certo ou leve ao usuário (R-DECISAO)")
            if parecer.metodo_mutante(args):
                self.gh_api_de_merge(args, pasta)
            # por último: a regra do gh fala antes. E168.9 (A5): no GraphQL, também sem campo à vista (a chave fora de
            # aspas esconde o `-f` que o bash remonta)
            if (parecer.metodo_mutante(args) or e_graphql(parecer.endpoint_da_api(args))) and self.consulta_ilegivel(args):
                self.barrar(*GRAPHQL_ILEGIVEL, trava=TRAVA)  # também na sessão do Forge: a consulta pode ser um merge

    # Pacotes ----------------------------------------------------------------------------------------
    @staticmethod
    def so_arquivo(cfg, args, sub):
        """`pip install -r arquivo` sem pacote avulso instala só o que o repositório já lista."""
        opcoes = cfg.get("so_arquivo")
        if not opcoes or not any(a in opcoes for a in args):
            return False
        avulsos, pulo = [], False
        for a in args[args.index(sub) + 1:]:
            if pulo:
                pulo = False
            elif a in opcoes:
                pulo = True
            elif not a.startswith("-"):
                avulsos.append(a)
        return not avulsos

    def pacote(self, prog, args):
        cfg = self.pol["pacotes"][prog]
        sub = next((a for a in args if not a.startswith("-")), None)
        if sub not in cfg["adicionam"]:
            return
        flags = self.pol["flags_congeladas"] + cfg.get("flags_congeladas", [])
        congelado = sub in cfg["congelados"] or any(a in flags for a in args) or self.so_arquivo(cfg, args, sub)
        acao = "instalar_congelado" if congelado else "instalar_pacote"
        if not self.pode(acao):
            dica = "use a instalação com lockfile congelado do gerenciador (--frozen, --locked ou o comando equivalente)" \
                if self.pode("instalar_congelado") else "peça ao dev"
            self.barrar("R-CONFORMIDADE", f"{prog} {sub} {self.so_de(acao)} (papel: {self.papel})", dica)


def mascarado(palavra):
    """HOOK-MSG-SEGMENTO, A1 da segurança: a palavra citada sem o valor da atribuição (`GH_TOKEN=***`) e sem o corpo
    de token do GitHub (`ghp_***`, `github_pat_***`)."""
    nome, igual, _ = palavra.partition("=")
    if igual and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nome):
        palavra = f"{nome}=***"
    return TOKEN_DO_GITHUB.sub(r"\1***", palavra)


def com_trecho(rid, o_que, corrigir, palavras):
    """HOOK-MSG-SEGMENTO: o texto da recusa com o comando simples que a disparou, `(em `…`)` antes do `Corrigir:`.
    O trecho sai sem controle nem formato (C-A6-1), com crase trocada por `'` (C-A6-2) e até `TETO_DO_TRECHO`
    caracteres; só entra se a linha inteira couber em `LIMITE_MENSAGEM`, para o motivo e o `Corrigir:` nunca se
    cortarem por ele (C-A6-3). O valor de `NOME=valor` e o que tem cara de token do GitHub saem mascarados."""
    texto = f"{o_que}. Corrigir: {corrigir}"
    trecho = "".join("'" if c == "`" else c for c in " ".join(" ".join(map(mascarado, palavras or ())).split())
                     if unicodedata.category(c) not in INVISIVEIS)
    if not trecho:
        return texto
    trecho = trecho if len(trecho) <= TETO_DO_TRECHO else trecho[:TETO_DO_TRECHO - 1] + "…"
    citado = f"{o_que} (em `{trecho}`). Corrigir: {corrigir}"
    return citado if len(" ".join(f"{rid}: {citado}".split())) <= LIMITE_MENSAGEM else texto


def entrada_valida(e):
    """Forma de uma entrada de `caminhos`: sem ela o hook cairia em KeyError/TypeError e liberaria (saída 0). Sem função
    por campo: roda para cada entrada em toda chamada do hook (custo do corpus, CORPUS-CUSTO-CONTADOR)."""
    if not isinstance(e, dict):
        return False
    caminho, motivo, quem = e.get("caminho"), e.get("motivo"), e.get("quem")
    return (isinstance(caminho, str) and caminho != ""
            and isinstance(motivo, str) and motivo != ""
            and isinstance(quem, list) and all(isinstance(q, str) for q in quem)
            and isinstance(e.get("so_forge", False), bool)
            and ("branch" not in e or isinstance(e["branch"], str) and e["branch"] != ""))


def lista_de_textos(v):
    return isinstance(v, list) and all(isinstance(t, str) for t in v)


def pacote_valido(cfg):
    """Um gerenciador de `pacotes`: `adicionam` e `congelados` obrigatórios; as flags opcionais, se existirem, são listas."""
    return (isinstance(cfg, dict) and lista_de_textos(cfg.get("adicionam")) and lista_de_textos(cfg.get("congelados"))
            and all(lista_de_textos(cfg[k]) for k in ("flags_congeladas", "so_arquivo") if k in cfg))


def leitura_valida(v):
    """`so_leitura` é opcional; presente, precisa das três listas (sem elas o papel só de leitura cairia em KeyError)."""
    return v is None or (isinstance(v, dict) and all(lista_de_textos(v.get(k)) for k in ("papeis", "comandos", "saidas"))
                         and isinstance(v.get("comandos_por_papel", {}), dict)
                         and all(lista_de_textos(c) and c for c in v.get("comandos_por_papel", {}).values())
                         and lista_de_textos(v.get("arquivos_por_escrita_permitida", [])))


def escrita_valida(v):
    """`escrita_permitida` é opcional; presente, mapeia papel a uma lista não vazia de caminhos (lista vazia barraria tudo)."""
    return v is None or (isinstance(v, dict) and all(lista_de_textos(c) and c for c in v.values()))


def politica_valida(pol):
    """Forma de toda a política: o hook lê estas chaves sem checar, então qualquer desvio liberaria por erro interno."""
    def texto(v):
        return isinstance(v, str) and bool(v)
    if not isinstance(pol, dict):
        return False
    papeis, acoes, pacotes, caminhos = (pol.get(k) for k in ("papeis", "acoes", "pacotes", "caminhos"))
    return (isinstance(papeis, dict) and all(lista_de_textos(t) for t in papeis.values())
            and texto(pol.get("sem_agent_type")) and texto(pol.get("papel_padrao"))
            and isinstance(acoes, dict) and ACOES <= acoes.keys() and all(lista_de_textos(q) for q in acoes.values())
            and isinstance(pacotes, dict) and all(pacote_valido(c) for c in pacotes.values())
            and lista_de_textos(pol.get("flags_congeladas"))
            and isinstance(caminhos, list) and all(entrada_valida(e) for e in caminhos)
            and leitura_valida(pol.get("so_leitura")) and escrita_valida(pol.get("escrita_permitida")))


def politica():
    """Lê a política; qualquer parte malformada (ou JSON ilegível) bloqueia (falha fechado), em vez de liberar por erro interno."""
    try:
        pol = json.loads((PLUGIN / "hooks" / "conformidade.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pol = None
    if not politica_valida(pol):
        bloquear("R-CONFORMIDADE", "política de conformidade inválida: chave ausente ou com tipo errado "
                                   "(hooks/conformidade.json). Corrigir: leve ao usuário (R-DECISAO)")
    return pol


def escrita_barrada(agent_type, caminho, raiz, ramo):
    """A resposta do hook para a escrita de `caminho` pelo `agent_type`, na `raiz` do pedido e no `ramo` dado (VV-3):
    a tupla de recusa de `Guarda.caminho_barrado` ou None. Não decide escrita; quem decide é o hook: o None não libera
    nada. Só lê: não chama `politica()` nem `bloquear`, não grava, não lê stdin nem o ambiente (`CLAUDE_PROJECT_DIR`,
    `FORGE_GUARDA_ABERTA`); a raiz e o ramo vêm de quem chama, e o `git branch` não roda. Raiz vazia, política
    inválida e qualquer exceção interna saem como recusa (C-4: falha fechado, nunca None); as duas últimas levam
    `NAO_CONFERIDA` no quarto campo. O caminho é texto (de brief, C-5): caractere invisível recusa; acima de
    `TETO_DO_CAMINHO` bytes sai com `NAO_VERIFICAVEL` no quarto campo; só o `~/` do começo se expande (o home do
    `caminho_barrado`; variável nunca), e o relativo vale a partir da raiz, nunca da pasta corrente."""
    if not raiz:
        return ("R-CONFORMIDADE", "raiz vazia: a raiz do pedido é obrigatória", "leve ao usuário (R-DECISAO)")
    try:
        pol = json.loads((PLUGIN / "hooks" / "conformidade.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pol = None
    if not politica_valida(pol):
        return ("R-CONFORMIDADE", "política de conformidade inválida (hooks/conformidade.json)", "leve ao usuário (R-DECISAO)",
                NAO_CONFERIDA)
    try:
        if any(unicodedata.category(c) in INVISIVEIS for c in caminho):
            return ("R-CONFORMIDADE", "caractere invisível no caminho", "escreva o caminho sem controle nem formato")
        if len(caminho.encode("utf-8", "surrogatepass")) > TETO_DO_CAMINHO:
            return ("R-CONFORMIDADE", f"caminho acima de {TETO_DO_CAMINHO} bytes", "encurte o caminho", NAO_VERIFICAVEL)
        raiz = Path(os.path.realpath(raiz))
        caminho = raiz / (str(Path.home()) + caminho[1:] if caminho.startswith("~/") else caminho)
        guarda = Guarda(types.SimpleNamespace(raiz=raiz, iniciante=lambda: False), pol, papel_de(pol, agent_type))
        guarda._ramo, guarda.sessao_forge = ramo, e_clone_do_forge(raiz)
        return guarda.caminho_barrado(Path(os.path.realpath(caminho)))
    except Exception as erro:  # noqa: BLE001 - C-4: qualquer erro interno recusa, nunca escapa nem libera
        return ("R-CONFORMIDADE", f"erro interno ({type(erro).__name__})", "leve ao usuário (R-DECISAO)", NAO_CONFERIDA)


def raiz_do_parecer(hook, p):
    """Raiz da cópia de trabalho que contém `p`, ou None: a mais próxima (só pelo disco, `Guarda.raiz_git`), se for a
    da sessão ou uma worktree do mesmo repositório (mesmo diretório comum, `.git` conferido nos dois sentidos).
    Uma worktree dentro da raiz da sessão (`.claude/worktrees/<n>`) conta como ela mesma, não como a sessão."""
    raiz = Path(os.path.realpath(hook.raiz))
    topo = Guarda.raiz_git(p.parent)
    if topo is None or topo == raiz or topo in raiz.parents:
        return raiz if raiz in p.parents else None
    comum = diretorio_comum(topo)
    return topo if comum and comum == diretorio_comum(raiz) else None


def e_parecer(p):
    """O `.md` dentro de `docs/<pasta de parecer>/` (`PASTAS_DE_PARECER`), em qualquer raiz ou worktree."""
    return p.suffix == ".md" and any(par == ("docs", pasta) for par in zip(p.parts, p.parts[1:]) for pasta in PASTAS_DE_PARECER)


def autoria(hook, guarda, alvos):
    """PostToolUse: grava quem escreveu cada parecer (caminho, hash do texto sem espaços nas pontas, agente, papel,
    hora) em autoria.jsonl; o `forge-check pr` confere (ADR 0009, 6.4). Vale também para parecer gravado em outra
    worktree do repositório: o caminho é relativo a ela e o registro vai para o `.forge/run/` comum."""
    for alvo in alvos:
        p = guarda.resolver(alvo, hook.cwd())
        if p.suffix != ".md" or not any(par == ("docs", pasta) for par in zip(p.parts, p.parts[1:])
                                        for pasta in ("reviews", "qa", "devops", "security")) or not p.is_file():
            continue  # só caminho de parecer dispara leitura
        sha = hashlib.sha256(p.read_text(encoding="utf-8").strip().encode()).hexdigest()  # antes de qualquer outra leitura
        raiz = raiz_do_parecer(hook, p)
        rel = p.relative_to(raiz).as_posix() if raiz else ""
        if rel.startswith(("docs/reviews/", "docs/qa/", "docs/devops/", "docs/security/")):
            registro = {"caminho": rel, "sha256": sha,
                        "agente": hook.entrada.get("agent_type") or "", "papel": guarda.papel,
                        "quando": time.strftime("%Y-%m-%dT%H:%M:%S")}
            with hook.trava(), open(hook.run() / "autoria.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def alvos_de_escrita(comando):
    """Alvos de `>`, `>>` e `tee` na linha (para a autoria dos pareceres escritos pelo Bash): a união das leituras
    (`leituras`, ADR 0013); a que não fecha não dá alvo. Atrás de lançador com mais de uma leitura e texto dividido que
    não fecha aspas, cada palavra depois de um `tee` da parte é alvo: ler a mais não esconde alvo."""
    try:
        comando, _ = tirar_heredocs(comando)
    except ValueError:
        pass  # lê os corpos como comando: é só autoria, e ler a mais não esconde alvo
    alvos = []
    for partes in leituras(comando).partes:
        for palavras, destinos, _ in partes:
            alvos += destinos
            try:
                lidas = sem_lancadores(palavras)  # a união das leituras possíveis do lançador
            except TextoAbertoComLeituras:
                tees = [k for k, p in enumerate(palavras) if nome_do_caminho(p) == "tee"]
                alvos += [a for a in palavras[tees[0] + 1:] if not a.startswith("-")] if tees else []
                continue
            except ValueError:  # texto dividido do `env` com aspas abertas, ou acima do teto de palavras fora da tabela
                continue
            for lida in lidas:
                if lida[:1] == ["tee"]:
                    alvos += [a for a in lida[1:] if not a.startswith("-")]
    return list(dict.fromkeys(alvos))


def identificar_sessao(hook):
    """R-CONTRIB: quem é a sessão vem da raiz dela, não da pasta corrente (que passa de uma chamada para a outra).
    - Raiz num projeto do Forge (tem `.forge/versao`; vem antes do Forge, então o manifesto `.claude-plugin/` do
      Forge escrito no projeto não muda nada): as regras dele e as de contribuição valem em qualquer pasta (o
      próprio projeto, o clone, `wt/*`, `~`, outra pasta), no Bash, no Write e no Edit; a raiz fica em
      `hook.raiz`, ou a do projeto onde a pasta está, se houver.
    - Raiz no Forge (clone do próprio Forge, sem `.forge/versao`): regras da sessão do Forge; o hook age por inteiro
      dentro de um projeto, pela pasta corrente; fora dele (o clone, `wt/*`) valem as travas para todo papel
      (`GuardaDaProva` com `travas`, CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE).
    - Sem raiz (ou raiz fora do Forge): pela pasta corrente; em `~/.forge-contrib` falha fechado, como sessão de
      outro projeto de nome igual ao do clone (`wt/*` e a própria pasta: nome vazio).
    Devolve False se o hook não age; None se age pela raiz do repositório; o nome da sessão de outro projeto."""
    cwd, raiz = hook.cwd(), raiz_declarada()
    if raiz and raiz_do_projeto(raiz):
        if not hook.projeto(raiz):  # o projeto desligou o hook: só a pasta corrente, se for outro projeto
            return None if hook.projeto(cwd) else False
        nome = hook.raiz.name
        if not hook.projeto(cwd):
            hook.projeto(raiz)
        return nome
    if raiz and e_clone_do_forge(raiz):
        return None if hook.projeto(cwd) else False
    if hook.projeto(cwd):
        return None
    if not em_contrib(cwd):
        return False
    base = contrib()
    partes = Path(os.path.realpath(cwd)).relative_to(base).parts
    clone = partes[:2] if partes and (partes[0] == "wt" or partes[0].endswith("-wt")) else partes[:1]
    hook.raiz = base.joinpath(*clone)
    return partes[0].removesuffix("-wt") if partes and partes[0] != "wt" else ""


def pedir_confirmacao(perguntas):
    """Saída 0 com `permissionDecision: ask`: o Claude Code mostra o motivo e a pessoa decide na janela de permissão."""
    motivo = mensagem("R-CONFORMIDADE", " | ".join(dict.fromkeys(perguntas)))
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                             "permissionDecisionReason": motivo}}, ensure_ascii=False))


class ForaDaProva(Exception):
    """A `GuardaDaProva` achou outra recusa, que fora de projeto não vale (ADR 0009, seção 6)."""


# AGENTES-JSON-SEM-GUARDA (v0478; C9 e C10 de docs/security/v047-v2-ameacas.md): no clone do Forge, as recusas destas
# entradas da política valem também na `GuardaDaProva`, para todo papel (o jarvis incluído); o resto do clone segue livre.
# CONFIG-TETO-SEM-GUARDA (v0478, parte do hook): o `.forge/config.json` da raiz da sessão, onde o hook `agentes` lê o teto.
CONFIG_DA_RAIZ = ".forge/config.json"
ESTADO_DOS_HOOKS = (".git/forge/", CONFIG_DA_RAIZ)
# `.git/forge` só como nome inteiro: `.git/forge-suite-verde` é a prova da suíte, com a recusa própria (R-VERIFY).
ESTADO_NO_TEXTO = re.compile(r"\.git/forge(?![\w.-])|forge/run|agentes\.json|\.forge/config\.json")  # C10: linha que o hook não lê e cita o estado
# PARECER-PELO-PAPEL (v0478 E50.7, A3 de docs/security/v0479-entrega-parecer-mesclado.md): no clone do Forge, as recusas
# das pastas de parecer valem também na `GuardaDaProva`, para todo papel, e também pela forma relativa ao topo da cópia
# do Forge que contém o alvo (o clone ou `wt/*` com a raiz da sessão em outra cópia). O papel dono segue livre na pasta.
CAMINHOS_DE_PARECER = ("docs/reviews/", "docs/qa/", "docs/devops/", "docs/security/aceites/", "docs/security/")
# A5 e A6 da segurança: a pasta de parecer citada no texto da linha (a variável no alvo, `d=docs/qa; echo x > $d/n.md`);
# `docs/security` cobre `docs/security/aceites`; a caixa não conta (`d=DOCS/QA; echo x > ${d,,}/n.md`).
PARECER_NO_TEXTO = re.compile(r"(?<![\w.-])docs/(?:reviews|qa|devops|security)(?![\w.-])", re.I)  # `${d,,}` baixa a caixa
# CONTROLE-PEDIDOS-E-BRIEFS-SO-JARVIS (v0478 E63.1): na sessão do Forge, o pedido e o brief da pasta de controle são só do
# jarvis, como as pastas de parecer: as linhas `entrega conferida`, `parecer conferido` e `DECISÃO DO DONO` vivem neles.
# A2 da segurança E123.8: entradas com dono que casam também relativas à cópia principal (o hook ordens a lê de lá).
PELA_COPIA_PRINCIPAL = (".forge/ordens/",)  # A4 da segurança E123.12: a pasta, que o curinga no nome não escapa
CAMINHOS_DO_CONTROLE = ("~/.forge-contrib/docs/pedidos/", "~/.forge-contrib/*/docs/pedidos/",
                        "~/.forge-contrib/docs/briefs/", "~/.forge-contrib/*/docs/briefs/",
                        "~/.forge-contrib/docs/ordens/")  # A1 da segurança E123.8: a pasta das ordens, como pasta
# A1 da E63.3: a pasta mãe numa variável (`d=~/.forge-contrib; echo x > $d/docs/pedidos/v1.md`) separa os dois nomes;
# basta a linha citar os dois, em qualquer ordem e posição. Com a pasta corrente no controle, basta `pedidos` ou `briefs`.
CONTROLE_NO_TEXTO = re.compile(r"forge-contrib[\s\S]*(?:pedidos|briefs|ordens)|(?:pedidos|briefs|ordens)"
                               r"[\s\S]*forge-contrib", re.I)
CRITICO_COM_CONTROLE = re.compile(f"{CRITICO.pattern}|{CONTROLE_NO_TEXTO.pattern}", re.I)
PEDIDO_OU_BRIEF = r"pedidos|briefs|ordens"  # compilado só na pasta do controle (`GuardaDaProva`): custo do corpus
# A1 do review E63.6: a cópia de `wt/` pelo caminho literal (`cd ~/.forge-contrib/wt/x &&`, `f=~/.forge-contrib/wt/r.txt`)
# não é a pasta mãe. Lista positiva em `sem_copia_de_wt`; textos, e não compilados no carregamento (custo do corpus).
COPIA_DE_WT = (r"(?<![^\s;&|<>=])(~|\$HOME|/[^\s;&|<>'\"()=]*|)/\.forge-contrib/wt/(\w[\w.-]*(?:/\w[\w.-]*)*)/?"
               r"(?=[\s;&|<>)'\"]|$)")  # só o caminho absoluto: `~`, `$HOME` ou `/`
SUBIDA_NO_TEXTO = (r"\.\.|`|\\|[{}]|(?:^|[\s/=])\.[*?[]|~[-+\d]|\bcd\s+-|pushd|popd|OLDPWD|CDPATH|dirname|realpath|"
                   r"readlink")
# A16 e A17 da segurança E63.11: o que troca, na própria linha, o caminho que o hook resolveu antes de ela rodar: o nome
# `HOME` fora do `$HOME` e do `${HOME}` (`HOME=`, `export`, `read`, `printf -v`, `env HOME=`, `unset`), o arquivo que o
# shell lê e pode trocá-lo (`source`, o ponto, `BASH_ENV`, `ENV`) e a entrada criada ou movida (`ln`, `link`, `mv`,
# `install`, `rename`, `cp -s|-l`): o `~`, o `$HOME` e o caminho real do hook deixam de ser os do bash.
CAMINHO_TROCADO_NA_LINHA = (r"(?<![\w$])(?<!\$\{)(?:HOME|BASH_ENV|ENV)(?!\w)|(?<![\w.-])(?:source|ln|link|mv|install|rename)"
                            r"(?![\w.-])|(?:^|[;&|(])\s*\.\s|\bcp\b[^;&|\n]*\s-(?:[a-zA-Z]*[sl][a-zA-Z]*|-(?:symbolic-)?link)"
                            r"(?![\w-])")


def sem_copia_de_wt(texto):
    """A1 do review E63.6: o texto com cada caminho literal e absoluto de uma cópia de `wt/` (pelo caminho real, dentro
    de `~/.forge-contrib/wt/`) trocado por um NUL (o bash não o recebe na linha), para que só a pasta mãe conte em
    `CONTROLE_NO_TEXTO`. Volta o texto intacto se algo nele pode subir ou montar o caminho (`..`, também partido por
    aspas, `$(`, crase, chave, escape, curinga no ponto, `~-`, `cd -`, `dirname`...), se troca o caminho que o bash usa
    (`CAMINHO_TROCADO_NA_LINHA`: `HOME=`, `ln`, A16 e A17 da segurança E63.11) ou se um `$` do texto de antes da troca
    não é TMPDIR, HOME ou um nome que a linha só atribui a uma cópia (`f=<cópia>`)."""
    plano = texto.replace("'", "").replace('"', "")
    if "forge-contrib/wt/" not in texto or re.search(SUBIDA_NO_TEXTO, plano):
        return texto
    if re.search(CAMINHO_TROCADO_NA_LINHA, plano):  # A16 e A17: o caminho que o bash usa não é o que o hook resolve
        return texto
    wt, casa = (contrib() / "wt").as_posix() + "/", str(Path.home())

    def copia(m):
        base = casa if m.group(1) in ("~", "$HOME") else m.group(1)
        return "\0" if os.path.realpath(f"{base}/.forge-contrib/wt/{m.group(2)}").startswith(wt) else m.group(0)
    novo = re.sub(COPIA_DE_WT, copia, texto)
    for ref in re.finditer(r"\$([A-Za-z_]\w*)?", texto):  # A16: antes da troca, o `$` dentro da cópia também conta
        nome = ref.group(1)
        if not nome:
            return texto  # `$(`, `$'`, `$1`, `$?`: fora da lista
        usos = [u.start() for u in re.finditer(rf"(?<![\w$]){nome}\b", novo)]  # o nome fora do `$nome`
        if (not usos) != (nome in ("TMPDIR", "HOME")) or any(not novo.startswith(f"{nome}=\0", u) for u in usos):
            return texto
    return novo


class GuardaDaProva(Guarda):
    """S8 (C-1) com a pasta corrente fora de projeto: a Guarda lê a escrita, mas só a recusa da prova da suíte vale, e a
    da linha que o hook não lê por passar de `PROFUNDIDADE` (PROFUNDIDADE-BASH-C).
    E16.1 (HOOK-RVERIFY-FALSO-POSITIVO): a outra recusa não para a leitura, que segue até o fim da linha; a prova é
    recusada pelo destino da escrita, resolvido pela Guarda, e não pelo texto. Só a linha que o hook não lê (teto,
    ilegível: `sem_leitura`) volta ao texto em `prova_fora_de_projeto`, falhando fechado.
    AGENTES-JSON-SEM-GUARDA: com a sessão no clone do Forge (`no_clone`), vale também a recusa que cita o motivo de uma
    entrada de `ESTADO_DOS_HOOKS` (escrita, remoção do ancestral, link).
    CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE: com `travas` (raiz da sessão no clone do Forge), valem também as travas
    (`trava_da_sessao_do_forge`)."""
    def __init__(self, hook, pol, papel, no_clone=False, travas=False):
        super().__init__(hook, pol, papel)
        # CONTROLE-PEDIDOS-E-BRIEFS-SO-JARVIS: a linha que cita o pedido ou o brief da pasta de controle é crítica para o
        # papel que não é o jarvis, e a construção que o hook não modela nela recusa (`controle`: o texto que conta).
        self.controle, self.critico = ((None, CRITICO.search) if papel == "jarvis"
                                       else (CONTROLE_NO_TEXTO, CRITICO_COM_CONTROLE.search))
        if self.controle and self.na_pasta_do_controle():
            self.controle = re.compile(PEDIDO_OU_BRIEF, re.I)
            self.critico = re.compile(f"{CRITICO.pattern}|{PEDIDO_OU_BRIEF}", re.I).search
        self.no_clone, self.travas = no_clone, travas
        self.motivos_do_estado = tuple(e["motivo"] for e in pol["caminhos"] if e["caminho"] in ESTADO_DOS_HOOKS)
        self.motivo_do_config = next((e["motivo"] for e in pol["caminhos"] if e["caminho"] == CONFIG_DA_RAIZ), None)

    def bash(self, comando, pasta, nivel=0, so_substituicoes=False, corpo_de_heredoc=False):
        """A16 e A17 da segurança E63.11: para o papel que não é o jarvis, a linha que troca o caminho que o hook resolve
        (`CAMINHO_TROCADO_NA_LINHA`: `HOME=`, `ln`, `mv`...) é construção que ele não modela; recusa se cita o pedido ou o
        brief da pasta de controle (`recusa_do_estado`), também pela cópia de `wt/` (`HOME=~/.forge-contrib/wt/g; …`). O
        nome partido por continuação (`HO\\` + quebra) já recusa como construção que o hook não modela."""
        if not nivel and self.controle is not None:
            trocado = re.search(CAMINHO_TROCADO_NA_LINHA, comando.replace("'", "").replace('"', ""))
            if trocado:
                self.barrar("R-CONFORMIDADE", f"`{trocado.group().strip()}` na linha: o hook não modela o caminho que ela "
                            "troca (o HOME, o link, o arquivo lido pelo shell)",
                            "peça ao jarvis; texto que cita o pedido ou o brief vai num arquivo (git commit -F)")
        super().bash(comando, pasta, nivel, so_substituicoes, corpo_de_heredoc)

    def caminho_barrado(self, caminho):
        """CONFIG-TETO-SEM-GUARDA: a recusa de `.forge/config.json` só vale para o da raiz da sessão; o modelo
        (`templates/projeto/.forge/config.json`) e o de outra pasta seguem livres."""
        achado = super().caminho_barrado(caminho)
        if achado and self.motivo_do_config and self.motivo_do_config in achado[1] and (
                caminho != Path(os.path.realpath(self.h.raiz)) / CONFIG_DA_RAIZ):
            return None
        return achado or self.parecer_no_topo(caminho)

    def parecer_no_topo(self, caminho):
        """PARECER-PELO-PAPEL: a recusa da pasta de parecer pela forma relativa ao topo da cópia do Forge que contém o alvo
        (a forma da raiz da sessão já vem da `Guarda`); fora de uma cópia do Forge, None. Só vale no clone
        (`recusa_do_estado`)."""
        topo = self.raiz_git(caminho.parent)
        rel = (relativo_ao_pai(caminho.as_posix(), topo) if e_clone_do_forge(topo) else None) or ""
        for e in self.pol["caminhos"]:
            if e["caminho"] in CAMINHOS_DE_PARECER and casa(rel, e["caminho"]):
                return None if self.papel in e["quem"] else (
                    "R-CONFORMIDADE", f"{e['motivo']}: {e['caminho']} (papel: {self.papel})",
                    f"peça a {'/'.join(e['quem'])}")
        return None

    def barrar(self, rid, o_que, corrigir, simples=None, trava=None, alvo=None, grupo=None):
        if (rid, o_que, corrigir) == PROVA_DA_SUITE:
            super().barrar(rid, o_que, corrigir, alvo=alvo, grupo=grupo)
        if (rid, o_que, corrigir) == PROFUNDIDADE_EXCEDIDA:
            super().barrar(rid, o_que, corrigir, alvo=alvo, grupo=grupo)
        if self.recusa_do_estado(o_que):
            super().barrar(rid, o_que, corrigir, alvo=alvo, grupo=grupo)
        if self.travas and trava_da_sessao_do_forge(rid, trava, self.h.campo("tool_input").get("command")):
            super().barrar(rid, o_que, corrigir, simples, alvo=alvo, grupo=grupo)
        if self.sem_leitura:
            raise ForaDaProva(rid)

    def recusa_do_estado(self, o_que):
        """No clone: a recusa cita o motivo de uma entrada do estado, ou é a da construção que o hook não modela (`$d`,
        J13) numa linha que cita o estado (`ESTADO_NO_TEXTO`)."""
        if not self.no_clone:
            return False
        if any(f"{e['motivo']}: {e['caminho']}" in o_que
               for e in self.pol["caminhos"] if e["caminho"] in CAMINHOS_DE_PARECER):
            return True  # PARECER-PELO-PAPEL
        if ".forge-contrib/" in o_que and any(f"{e['motivo']}: {e['caminho']}" in o_que
                                              for e in self.pol["caminhos"] if e["caminho"] in CAMINHOS_DO_CONTROLE):
            return True  # CONTROLE-PEDIDOS-E-BRIEFS-SO-JARVIS
        if any(m in o_que for m in self.motivos_do_estado):
            return True
        linha = self.h.campo("tool_input").get("command")
        if "o hook não modela" in o_que and isinstance(linha, str) and self.controle_no_texto(linha):
            return True  # CONTROLE-PEDIDOS-E-BRIEFS-SO-JARVIS
        return "o hook não modela" in o_que and isinstance(linha, str) and (
            bool(ESTADO_NO_TEXTO.search(linha)) or self.parecer_no_texto(linha))

    def controle_no_texto(self, linha):
        """CONTROLE-PEDIDOS-E-BRIEFS-SO-JARVIS: a linha que o hook não lê cita o pedido ou o brief da pasta de controle, e
        o papel não é o jarvis (o dono grava pelo caminho literal ou pelo `forge-check`). A cópia de `wt/` pelo caminho
        literal não conta como a pasta mãe (A1 do review E63.6, `sem_copia_de_wt`)."""
        if self.controle is None:
            return False
        texto = juntar_continuacoes(linha) if "\\\n" in linha else linha
        return bool(self.controle.search(sem_copia_de_wt(texto) if self.controle is CONTROLE_NO_TEXTO else texto))

    def na_pasta_do_controle(self):
        """A1 da E63.3: a pasta corrente fica em `~/.forge-contrib` (pelo caminho real) fora de uma cópia de `wt/`, e
        `docs/pedidos` relativo alcança o controle (`d=docs/pedidos; echo x >> $d/v1.md`)."""
        rel = relativo_ao_pai(os.path.realpath(self.h.cwd()), contrib())
        return rel is not None and not rel.startswith("wt/")

    @staticmethod
    def parecer_no_texto(linha):
        """A5 e A6 da segurança: a linha (com as continuações juntadas) cita uma das cinco pastas de parecer, dono incluído,
        como no projeto: a variável que guarda a pasta do dono alcança a vizinha (`d=docs/reviews; echo x > $d/../qa/n.md`);
        o dono grava a própria pasta pelo caminho literal."""
        return bool(PARECER_NO_TEXTO.search(juntar_continuacoes(linha)))

    def perguntar(self, texto):
        """Fora de projeto não há confirmação a pedir."""


def trava_da_sessao_do_forge(rid, trava, linha):
    """A recusa é uma trava que vale na sessão do Forge para todo papel: R-MAIN, R-VERIFY, a marcada `TRAVA` (o push
    direto para a develop ou homolog, a tag v*), a `TRAVA_OPACA` numa linha com um comando que pode ser uma trava
    (`toca_uma_trava`) e a `TRAVA_NO_TETO` com o git ou o gh no texto (CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE, E51.6)."""
    if trava == TRAVA_NO_TETO:
        return isinstance(linha, str) and bool(GIT_NO_TEXTO.search(linha))
    if trava == TRAVA_OPACA:
        return isinstance(linha, str) and toca_uma_trava(linha)
    return rid in ("R-MAIN", "R-VERIFY") or trava == TRAVA


# E51.18 (A1 da segurança E51.16): o `source` e o ponto executam o here-string (`source /dev/stdin <<< '…'`).
FONTES = frozenset({"source", "."})
PREFIXOS_DA_FONTE = frozenset({"builtin", "command"})  # E51.22: `builtin source`, `command -p .`


def na_posicao_de_programa(palavras, j):
    """E51.22 (A2 da segurança E51.20): a palavra `j` é o programa do comando simples: a primeira, ou depois só de
    `builtin`/`command` e das opções deles (`command -p .`). O `.` argumento (`find .`) não é."""
    return all(p in PREFIXOS_DA_FONTE or (k and p.startswith("-")) for k, p in enumerate(palavras[:j]))


def toca_uma_trava(linha, nivel=0):
    """E51.6: algum comando simples da linha pode ser uma trava com o alvo opaco: o programa opaco (`$G push`), o git
    com subcomando fora de `GIT_FORA_DAS_TRAVAS` (opaco, alias, com `-c`), o gh com as duas primeiras palavras fora de
    `GH_FORA_DAS_TRAVAS`, e o texto que o `eval` ou o `sh -c` reavalia (um nível; o `eval` com texto a reavaliar, o
    shell (com texto ou lendo a entrada, `echo … | bash`) e o `source` ou o ponto como programa dentro dele são trava,
    fecha na dúvida: A1 da segurança E51.12, E51.16 e A2 E51.20). O git ou o gh valem em qualquer posição do comando
    (`env git push $F`). A palavra vem do leitor (`palavras_do_texto`, sem aspas nem escapes); a que o bash expande,
    pelo texto cru, vira `$`: a substituição (`$(echo git) push`, `git $(echo push)`) também é opaca. O corpo de heredoc
    é comando só quando o dono o roda (`bash <<'X'`; `corpo_so_lido`, como na conferência da linha), e o here-string de
    um shell, do `source` ou do ponto (`bash <<< '…'`, `source /dev/stdin <<< '…'`) é texto reavaliado como o do
    `sh -c` (`texto_reavaliado`); o heredoc em dúvida deixa a linha inteira como comando."""
    try:
        linha, corpos = tirar_heredocs(linha)
    except ValueError:
        corpos = []
    for dono, corpo in corpos:
        if not corpo_so_lido(dono, interprete) and toca_uma_trava(corpo, nivel):
            return True
    for comando in palavras_do_texto(linha).simples:
        k = 0
        while k < len(comando.palavras) and (comando.palavras[k].cru in ANTES_DO_PROGRAMA
                                             or ATRIBUICAO.match(comando.palavras[k].cru)):
            k += 1
        originais = comando.palavras[k:]
        palavras = ["$" if OPACA_NA_PALAVRA.search(p.cru) else p.valor for p in originais]
        aqui = [r.alvo for r in comando.redirecoes if r.operador == "<<<" and r.alvo is not None]
        if palavras and OPACA_NA_PALAVRA.search(palavras[0]):
            return True
        for j, palavra in enumerate(palavras):
            nome, resto = nome_do_caminho(palavra), palavras[j + 1:]
            if nome == "git" and resto and subcomando_do_git(resto) not in GIT_FORA_DAS_TRAVAS:
                return True
            if nome == "gh" and " ".join(resto[:2]) not in GH_FORA_DAS_TRAVAS:
                return True
            if nivel and nome in SHELLS:  # E51.18: o shell aninhado relê o argumento, o here-string ou a entrada (pipe)
                return True
            if nivel and nome == "eval" and originais[j + 1:]:  # o eval não lê a entrada
                return True
            if nivel and palavra in FONTES and (aqui or na_posicao_de_programa(palavras, j)):  # lê o pipe também
                return True
            relidos = map(texto_reavaliado, originais[j + 1:])
            if (nome == "eval" or nome in SHELLS) and not nivel and any(toca_uma_trava(t, 1) for t in relidos):
                return True
            le_o_here_string = nome in SHELLS or palavra in FONTES
            if le_o_here_string and not nivel and any(toca_uma_trava(texto_reavaliado(a), 1) for a in aqui):
                return True
    return False


# CONFORMIDADE-SUBSTITUICAO-NO-PROJETO (v0478 E63.1): o envio do git com parte vinda de substituição de comando ou da
# entrada, lido pelo texto cru como na `toca_uma_trava` (E51.6). Vale no projeto e, pela `TRAVA_OPACA`, na sessão do Forge.
ENVIO_DO_GIT = frozenset({"push", "send-pack"})
SUBSTITUICAO_NA_PALAVRA = re.compile(r"\$\(|`|<\(")
CITA_O_ENVIO = re.compile(r"(?<![\w./-])(?:push|send-pack)(?![\w.-])")


def envio_com_substituicao(linha):
    """Algum comando simples da linha (já sem os corpos de heredoc: a mesma que `leituras` lê, e a leitura dela vem do
    cache de `palavras_do_texto`) é um envio do git, ou pode ser, com parte que o hook não sabe: o programa por substituição seguido de `push` ou de outra substituição (`$(echo git) push`), o subcomando por
    substituição (`git $(echo push)`), uma flag ou o destino do envio por substituição (`git push $(echo --force)`), o
    envio atrás do `xargs` (os argumentos vêm do pipe), ou o shell que lê a entrada numa linha que cita o git e o envio
    (`echo 'git push …' | bash`)."""
    marcador = "$(" in linha or "`" in linha or "<(" in linha
    envio = "push" in linha or "send-pack" in linha or "\\" in linha  # o escape pode esconder o nome (`pu\sh`)
    xargs = "xargs" in linha and "git" in linha  # A5 da E63.3: o subcomando pode vir todo do pipe
    if not (marcador and (envio or "git" in linha) or xargs or envio and ("sh" in linha.replace("push", "") or "stdin" in linha or "/fd/" in linha)):
        return False  # custo do corpus (o `in` não é chamada): nenhum caso abaixo casa sem esses textos
    cita_o_envio = bool(GIT_NO_TEXTO.search(linha) and CITA_O_ENVIO.search(linha))
    for comando in palavras_do_texto(linha).simples:
        originais = [p for p in comando.palavras if p.cru not in ANTES_DO_PROGRAMA and not ATRIBUICAO.match(p.cru)]
        valores, nomes = [p.valor for p in originais], [nome_do_caminho(p.valor) for p in originais]
        opacas = [bool(SUBSTITUICAO_NA_PALAVRA.search(p.cru)) for p in originais]
        for j in range(len(valores)):
            no_programa = j == 0 or nomes[j - 1] in ENVOLVEDORES
            if opacas[j] and no_programa and (ENVIO_DO_GIT & set(valores[j + 1:]) or opacas[j + 1:j + 2] == [True]):
                return True
            if nomes[j] != "git":
                continue
            k = j + 1 + len(valores[j + 1:]) - len(resto_do_subcomando(valores[j + 1:]))
            if k < len(valores) and opacas[k]:
                return True
            envio = k < len(valores) and valores[k] in ENVIO_DO_GIT or k >= len(valores) and ENVIO_DO_GIT & set(valores)
            if envio and (any(opacas[j + 1:]) or "xargs" in nomes[:j]):
                return True
            if k >= len(valores) and "xargs" in nomes[:j]:  # A5 da E63.3: `echo push … | xargs git`
                return True
        programa = nomes and (nomes[0] in SHELLS or nomes[0] in ENVOLVEDORES or valores[0] in FONTES
                              or valores[0] == "builtin")
        if cita_o_envio and programa and shell_que_le_a_entrada(nomes, valores, opacas, comando.redirecoes, linha):
            return True
    return False


# Conjuntos literais, sem chamada no carregamento do módulo (custo do corpus: cada chamada conta em toda execução).
ENTRADA_DO_SHELL = {"-", "-s", "/dev/stdin", "/dev/fd/0", "/proc/self/fd/0"}
SHELL_OPCAO_COM_VALOR = {"-o", "+o", "-O", "+O", "--rcfile", "--init-file"}
NAO_E_ARQUIVO = {"dev", "proc", "fd", "..", "stdin"}  # segmento do alvo que pode nomear a própria entrada (A12)


def literal_atribuido(nome, linha):
    """O valor literal (sem `/` nem `.`) que a linha dá a `nome` em toda ocorrência dele fora do `$nome` (`B=x`); None se
    a linha não o atribui, o atribui a outro texto ou o usa de outro jeito (`read B`)."""
    usos = re.findall(rf"(?<![\w$]){nome}\b(=[\w+-]*(?=[\s;&|)]|$))?", linha)
    return usos[0][1:] if usos and len(set(usos)) == 1 and usos[0] else None


def entrada_de_arquivo(redirecoes, linha=""):
    """A12 da segurança E63.7, por lista positiva: a última redireção da entrada padrão (sem número ou `0`, de qualquer
    operador) é `<` com alvo sem crase, `<(`, curinga nem chave, e com `$` só num nome que a linha atribui a um valor
    literal (`B=x; bash < "a $B"`, E51.10), que não pode nomear a própria entrada: nenhum segmento `dev`, `proc`, `fd`,
    `..` ou `stdin` e o último não só de dígitos (`< /dev/stdin`, `0< /dev/fd/0`, `< /proc/self/fd/0`,
    `cd /dev && bash < stdin`; a `bash 3< x 0< /dev/stdin` vale pela última)."""
    ultima = None
    for r in redirecoes:
        if r.prefixo.strip("0") == "" and (r.prefixo or r.operador[0] == "<"):
            ultima = r
    alvo = ultima.alvo if ultima and ultima.operador == "<" else None  # `<<<`, `<&`, `<>` e `0>&` não são arquivo
    if alvo is None or re.search(r"[`*?[{]|<\(", alvo.cru):
        return False
    nome = re.sub(r"\$([A-Za-z_]\w*)", lambda m: literal_atribuido(m.group(1), linha) or "/dev/", alvo.valor)
    partes = nome.split("/")  # o último vazio (`0/`) não abre: o bash falha com ENOTDIR
    return "$" not in nome and not NAO_E_ARQUIVO.intersection(partes) and not partes[-1].isdigit()


def shell_que_le_a_entrada(nomes, valores, opacas, redirecoes=(), linha=""):
    """A4 da E63.3: o comando simples roda um shell que lê a entrada (o pipe) ou um texto opaco: o shell como programa
    ou atrás de um envolvedor (`env bash`, `sudo bash`, `timeout 5 bash`), e o `source` ou o ponto como programa, sem
    script, com `-s`, `-` ou `/dev/stdin`, ou com o script vindo de substituição (`. <(…)`, `bash <(…)`). A entrada
    tirada de um arquivo (`bash < x.sh`) não é o pipe: o shell lê o arquivo, como o `bash x.sh` (E51.10); a de `<(…)`
    (`bash < <(…)`) é texto opaco."""
    if redirecoes and entrada_de_arquivo(redirecoes, linha):
        return False
    for j, nome in enumerate(nomes):
        shell = nome in SHELLS and (j == 0 or nomes[0] in ENVOLVEDORES)
        if not (shell or valores[j] in FONTES and na_posicao_de_programa(valores, j)):
            continue
        i = j + 1
        while i < len(valores) and valores[i][:1] in ("-", "+") and valores[i] not in ENTRADA_DO_SHELL:
            i += 2 if valores[i] in SHELL_OPCAO_COM_VALOR else 1
        if i >= len(valores) and shell or i < len(valores) and (valores[i] in ENTRADA_DO_SHELL or opacas[i]):
            return True
    return False


# A opção global do git com o valor na palavra seguinte (`git --git-dir .git push`): o valor não é o subcomando.
GIT_GLOBAIS_COM_VALOR = {"-C", "--git-dir", "--work-tree", "--namespace", "--attr-source", "--config-env"}  # literal: custo


def resto_do_subcomando(argumentos):
    """Os argumentos do git a partir do subcomando, como `subcomando_do_git` os pula (o `-c` para: o resto todo)."""
    resto = list(argumentos)
    while resto and resto[0].startswith("-") and resto[0] != "-c":
        resto = resto[2:] if resto[0] in GIT_GLOBAIS_COM_VALOR else resto[1:]  # E63.5 (A3): `--git-dir .git push`
    return resto if not resto or resto[0] != "-c" else []


def texto_reavaliado(palavra):
    """O texto que o `eval` ou o shell relê numa palavra: o valor dela (aspas e escapes tirados, a crase escapada vira
    crase e a variável fica no texto, opaca na releitura), ou `$` (opaco) se o bash de fora substitui um comando nela
    (`"$(echo git) push"`: o leitor a troca por `_` e devolve o corpo como outro comando simples)."""
    return "$" if len(palavras_do_texto(palavra.cru).simples) > 1 else palavra.valor


def prova_fora_de_projeto(hook, pol, papel, ferramenta, entrada, raiz, travas=False):
    """S8 (C-1, A2 da segurança g3): a prova da suíte é por uid, então vale também fora de projeto, em toda sessão e
    para todo papel. A outra recusa não vale e a leitura segue (`GuardaDaProva`); linha que o hook não lê ou erro
    interno: falha fechado só se o alvo cita o nome da prova ou, no clone do Forge, o estado dos hooks (C10).
    `travas`: na sessão do Forge valem também as travas (`trava_da_sessao_do_forge`)."""
    if hook.campo("hook_event_name") == "PostToolUse":
        return
    hook.raiz = raiz or Path(hook.cwd())
    guarda = GuardaDaProva(hook, pol, papel, bool(raiz and e_clone_do_forge(raiz)), travas)
    try:
        decidir(hook, guarda, ferramenta, entrada)
    except Exception as erro:  # noqa: BLE001 - ForaDaProva ou erro interno; a decisão vem do texto do alvo
        alvo = entrada.get("command") or entrada.get("file_path") or entrada.get("notebook_path")
        palavras = re.split(r"[\s'\"(),;=<>|&]+", alvo) if isinstance(alvo, str) else []
        if any(MARCA_DA_SUITE.fullmatch(Path(t).name) for t in palavras):
            Guarda.barrar(guarda, *PROVA_DA_SUITE)
        if guarda.no_clone and isinstance(alvo, str) and ESTADO_NO_TEXTO.search(juntar_continuacoes(alvo)):
            hook.registrar_erro(erro)
            Guarda.barrar(guarda, "R-CONFORMIDADE", "linha que o hook não lê ou erro interno, e ela cita o estado dos "
                          "hooks (.git/forge/, forge/run, agentes.json, .forge/config.json)", f"só o usuário altera; {SUGESTAO}")
        if guarda.no_clone and isinstance(alvo, str) and guarda.parecer_no_texto(alvo):  # A5 e A6 da segurança
            erro_interno = not isinstance(erro, ForaDaProva)  # a linha sem leitura é a recusa; só o erro interno vai ao registro
            if erro_interno:
                hook.registrar_erro(erro)
            Guarda.barrar(guarda, "R-CONFORMIDADE", "linha que o hook não lê ou erro interno, e ela cita uma pasta de parecer "
                          f"(papel: {papel})", "o dono grava a própria pasta pelo caminho literal; os outros papéis pedem ao dono")
        if guarda.no_clone and isinstance(alvo, str) and guarda.controle_no_texto(alvo):
            interno = not isinstance(erro, ForaDaProva)  # a linha sem leitura é a recusa; só o erro interno vai ao registro
            if interno:
                hook.registrar_erro(erro)
            Guarda.barrar(guarda, "R-CONFORMIDADE", "linha que o hook não lê ou erro interno, e ela cita o pedido ou o "
                          f"brief da pasta de controle (papel: {papel})", "peça ao jarvis")
        pasta = Path(hook.cwd())
        opaco = bool(palavras and VARIAVEL.search(alvo))  # S3: `$(…)` ou variável no alvo
        for t in filter(CURINGA.search, palavras):  # A1 da segurança g1: o curinga que o bash expande no alvo
            guarda.curinga_na_prova(Path(t).name, guarda.pastas_do_curinga(t, pasta, opaco))
        if not isinstance(erro, ForaDaProva):
            hook.registrar_erro(erro)


# HOOK-ERRO-LIBERA (C2, C3): a linha que escreve, para o marcador da falha fechada. Lê a mais de propósito: só pesa em erro
# interno ou prazo vencido, e aí a dúvida recusa. Os verbos do git que gravam arquivo vêm das listas da guarda normal (A1).
ESCRITORES = (TODOS_OS_ARGUMENTOS | SO_DESTINO | REMOCAO | CAMINHOS_NO_GIT | GIT_GRAVA_ARQUIVO
              | {"ln", "chmod", "truncate", "touch", "unlink", "shred", "rmdir", "find", "tar"} | MUDA_ATRIBUTO)
ESCREVE_NA_LINHA = re.compile(ESCRITA_NA_LINHA.pattern + r"|\b(?:" + "|".join(sorted(map(re.escape, ESCRITORES))) + r")\b")
ALVO_OPACO = re.compile(r"[$`]|<\(")  # C3: substituição, crase, variável ou `<(`: o hook não sabe o destino
# A2: a troca da pasta de base (`cd`, `pushd`, `popd`, `-C`, `--chdir`, `--git-dir`, `--work-tree`, `GIT_DIR`,
# `GIT_WORK_TREE`) tira do texto o caminho que a política conhece: na linha que escreve, conta como alvo opaco. A aspa
# antes do `cd` pega o invólucro (`sh -c 'cd docs && cp …'`, AR-8).
BASE_TROCADA = re.compile(r"(?:^|[\s;&|(){}'\"])(?:cd|pushd|popd)(?=[\s;&|)]|$)|(?<!\S)(?:-C|--chdir|--git-dir|--work-tree)"
                          r"|\bGIT_(?:DIR|WORK_TREE)\b")


def termos_da_politica(pol):
    """C2: a regex dos caminhos de `pol["caminhos"]`, um termo por entrada, sem a barra final; `~/` também como `$HOME/`,
    `${HOME}/` e o home real; `*` como um trecho sem barra nem espaço. Política sem `caminhos` ou com entrada ilegível:
    None (marca tudo)."""
    caminhos = pol.get("caminhos") if isinstance(pol, dict) else None
    if not isinstance(caminhos, list) or not caminhos:
        return None
    home = os.path.expanduser("~")
    homes = dict.fromkeys(("~", "$HOME", "${HOME}", home, os.path.realpath(home)))  # sem home, o termo a mais só marca a mais
    padroes = []
    for entrada in caminhos:
        caminho = entrada.get("caminho") if isinstance(entrada, dict) else None
        if not isinstance(caminho, str) or not caminho.rstrip("/"):
            return None
        caminho = caminho.rstrip("/")
        variantes = [h + caminho[1:] for h in homes] if caminho.startswith("~/") else [caminho]
        padroes += [re.escape(v).replace(r"\*", r"[^/\s]*") for v in variantes]
    return re.compile("|".join(dict.fromkeys(padroes)), re.I)


class MarcadorDaPolitica:
    """HOOK-ERRO-LIBERA: o marcador que o `executar` usa no erro interno e no prazo vencido (`_comum.marcado`). Marca o
    `CRITICO` ou a linha que escreve (`ESCREVE_NA_LINHA`) e cita um caminho da política (C2), tem alvo opaco (C3) ou
    troca a pasta de base (A2); no Write, Edit, MultiEdit e NotebookEdit, o caminho resolvido dentro da raiz da sessão
    ou casando a política (C4). A política ilegível marca tudo. Os termos se montam na 1.ª busca, do JSON real: entrada nova já nasce coberta."""

    def __init__(self, critico, arquivo):
        self.critico, self.arquivo, self._termos = critico, arquivo, None

    def termos(self):
        if self._termos is None:
            try:
                self._termos = termos_da_politica(json.loads(self.arquivo.read_text(encoding="utf-8"))) or False
            except (OSError, ValueError):
                self._termos = False
        return self._termos

    def marca(self, hook, formas):
        termos = self.termos()
        if termos is False or any(self.critico.search(t) for t in formas):
            return True
        if hook.entrada.get("tool_name") in FERRAMENTAS_DE_ARQUIVO:
            return self.arquivo_marcado(hook, formas[0], termos)
        if any(map(visibilidade_do_gh, formas)):  # E148.1: só no marcador, fora do `CRITICO`
            return True
        return any(ESCREVE_NA_LINHA.search(t) and (termos.search(t) or ALVO_OPACO.search(t) or BASE_TROCADA.search(t))
                   for t in formas)

    @staticmethod
    def arquivo_marcado(hook, caminho, termos):
        """C4: o caminho resolvido (link, `..`, `~`) dentro da raiz da sessão (ou da pasta corrente, sem raiz) ou casando a
        política. Caminho vazio marca."""
        if not caminho:
            return True
        pasta = os.path.realpath(hook.cwd())
        alvo = os.path.realpath(os.path.join(pasta, expandir_home(caminho)))
        raiz = os.path.realpath(raiz_declarada() or pasta)
        return alvo == raiz or alvo.startswith(raiz.rstrip(os.sep) + os.sep) or bool(termos.search(alvo))


MARCADOR = MarcadorDaPolitica(CRITICO, PLUGIN / "hooks" / "conformidade.json")


def principal(hook):
    ferramenta = hook.campo("tool_name")
    entrada = hook.campo("tool_input")
    if not isinstance(entrada, dict) or (ferramenta != "Bash" and ferramenta not in FERRAMENTAS_DE_ARQUIVO):
        return
    externo = identificar_sessao(hook)
    pol = politica()  # fora da falha fechada: o papel só se conhece depois dela (uma política malformada já falha fechado)
    papel = papel_de(pol, hook.campo("agent_type"))
    com_lista = papel in pol.get("escrita_permitida", {})
    if externo is False:
        raiz = raiz_declarada()
        # Sessão do Forge com a pasta corrente fora de projeto: só o papel com lista de permissão é avaliado (ADR 0009, 6)
        na_sessao_do_forge = bool(raiz and e_clone_do_forge(raiz) and hook.campo("hook_event_name") != "PostToolUse")
        if na_sessao_do_forge and ferramenta == "Bash" and not com_lista and isinstance(entrada.get("command"), str):
            guarda = Guarda(hook, pol, papel)  # R-CONTRIB: só o rótulo afrouxa-regra é conferido aqui
            guarda.sessao_forge = True
            try:
                guarda.rotulo_na_sessao_do_forge(entrada["command"], hook.cwd())
            except Exception as erro:  # noqa: BLE001 - linha que cita o rótulo falha fechado (R-CONTRIB)
                if not (CITA_ROTULO.search(entrada["command"])  # HOOK-CONTINUACAO-LINHA: também a forma juntada
                        or CITA_ROTULO.search(juntar_continuacoes(entrada["command"]))):
                    raise
                hook.registrar_erro(erro)
                bloquear("R-CONTRIB", "erro interno ao conferir o rótulo afrouxa-regra; o hook não pôde decidir. "
                                      "Corrigir: veja .forge/run/erros.log e leve ao dono do Forge (R-DECISAO)")
        if not (com_lista and na_sessao_do_forge):
            prova_fora_de_projeto(hook, pol, papel, ferramenta, entrada, raiz, na_sessao_do_forge)
            return
        externo, hook.raiz = None, raiz
    try:
        guarda = Guarda(hook, pol, papel)
        guarda.externo = externo
        guarda.sessao_forge = e_clone_do_forge(raiz_declarada())
        decidir(hook, guarda, ferramenta, entrada)
    except Exception as erro:  # noqa: BLE001 - papel com lista de permissão falha fechado (ADR 0009, seção 7)
        if not com_lista or hook.campo("hook_event_name") == "PostToolUse":
            raise
        hook.registrar_erro(erro)
        bloquear("R-CONFORMIDADE", f"erro interno do hook conformidade para o papel {papel}, que só escreve na "
                                   "lista de permissão; ele não pôde decidir. Corrigir: veja .forge/run/erros.log e "
                                   "leve ao usuário (R-DECISAO)")


def decidir(hook, guarda, ferramenta, entrada):
    if hook.campo("hook_event_name") == "PostToolUse":
        if ferramenta == "Bash":
            alvos = alvos_de_escrita(entrada["command"]) if isinstance(entrada.get("command"), str) else []
        else:
            alvos = [entrada.get("file_path") or entrada.get("notebook_path") or ""]
        autoria(hook, guarda, [a for a in alvos if a])
    elif ferramenta == "Bash":
        if isinstance(entrada.get("command"), str):
            guarda.bash(entrada["command"], hook.cwd())
            alvo = guarda.parecer_pelo_bash
            if alvo:  # 0.45.3: depois de todas as regras da linha, para a mais específica falar primeiro
                guarda.barrar("R-REVIEW", f"parecer {alvo.name} gravado pelo Bash ({alvo.parent.name}/)", COMO_GRAVAR_PARECER)
            if guarda.perguntas:
                pedir_confirmacao(guarda.perguntas)
    else:
        guarda.arquivo(entrada)


if __name__ == "__main__":
    executar("conformidade", principal, MARCADOR, regra_do_prazo="R-CONFORMIDADE")
