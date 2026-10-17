#!/usr/bin/env python3
"""Forge: conformidade dos agentes por papel (ADR 0009, seções 2, 3, 6 e 7; R-CONFORMIDADE).

PreToolUse em Bash, Write, Edit, MultiEdit e NotebookEdit: o papel vem do `agent_type` (política em
`conformidade.json`) e decide quem pode merge, push, PR, escrita em caminho protegido, instalação de pacote e as
flags proibidas (`--no-verify`, `--force`, `core.hooksPath`). Write/Edit decidem pelo `file_path` normalizado
(garantido); o Bash é lido como texto (barrado em regra: um script ou ofuscação passa, e o sandbox é a garantia).
PostToolUse registra a autoria dos pareceres em `.forge/run/autoria.jsonl`.
Falha fechado nas ações críticas (seção 7); `FORGE_GUARDA_ABERTA=1` no ambiente do processo abre a guarda.
Só age em projeto com `.forge/versao`; quem é a sessão vem de `CLAUDE_PROJECT_DIR` (`identificar_sessao`, R-CONTRIB).
"""
import hashlib
import json
import os
import re
import tempfile
import shlex
import subprocess
import time
from pathlib import Path

import parecer
from _comum import (INTEGRACAO, OPACO, PLUGIN, bloquear, comandos, construcao_nao_modelada, contrib, diretorio_comum, e_clone_do_forge,
                    em_contrib, executar, fora_da_gramatica_de_leitura, forge_check, git, mensagem, nome_da_branch, raiz_declarada,
                    raiz_do_projeto, sem_atribuicoes, tem_manifesto_do_forge)

FERRAMENTAS_DE_ARQUIVO = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
CRITICO = re.compile(
    r"\b(git|gh)\b[^\n]*\b(merge|push|edit|close|reopen|ready|review|label)\b|\bpr\b.*\bcreate\b|--no-verify|hookspath|--force|"
    r"\.claude/|\.claude-plugin|\.githooks|\.forge/|docs/reviews|docs/qa|docs/devops|docs/security|CLAUDE\.md|\.git/|commondir|docs/regras|tests/config\.json|catraca|tests/hooks|conformidade\.json",
    re.I)
# Prefixo -> opções dele que levam valor (as demais são booleanas).
LANCADORES = {"sudo": {"-u", "-g", "-C", "-D", "-p", "-r", "-t", "-U", "-h", "-R", "-T", "--user", "--group"},
              "env": {"-u", "-C", "-S", "--unset", "--chdir", "--split-string"}, "command": set(),
              "nohup": set(), "time": {"-o", "-f", "--output", "--format"}, "exec": {"-a"}, "builtin": set(),
              "nice": {"-n", "--adjustment"}, "setsid": set(), "stdbuf": {"-i", "-o", "-e"},
              "timeout": {"-k", "-s", "--kill-after", "--signal"},
              "xargs": {"-n", "-I", "-L", "-P", "-d", "-E", "-s", "-a", "--max-args", "--max-procs",
                        "--delimiter", "--arg-file", "--max-lines", "--max-chars"}}
# Variáveis definidas antes na linha que os comandos seguintes herdam; as `GIT_*_PATHSPECS` são as opções `--*-pathspecs`.
PATHSPECS_NO_AMBIENTE = {"GIT_GLOB_PATHSPECS": "--glob-pathspecs", "GIT_NOGLOB_PATHSPECS": "--noglob-pathspecs",
                         "GIT_LITERAL_PATHSPECS": "--literal-pathspecs", "GIT_ICASE_PATHSPECS": "--icase-pathspecs"}
VARIAVEIS_DA_LINHA = {"GH_REPO", "GIT_DIR", *PATHSPECS_NO_AMBIENTE}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
ENV_COM_VALOR_CURTA = set("uCS")  # opções curtas do `env` com valor (no grupo `-iS`: o resto ou a palavra seguinte)
MANIFESTO = ".claude-plugin/"  # no projeto, só a sessão do Forge escreve (R-CONTRIB): a identidade não vem dele
# Nome do interpretador, com versão ou plataforma depois do nome (`perl5.34.0`, `perl5.34-x86_64-linux-gnu`, `ruby3.2`,
# `python3.12`): fonte única para as três conferências (`-e`, edição no lugar, heredoc).
INTERPRETES = re.compile(r"^((python|perl|ruby)([\d][\w.-]*)?|node(js)?|php|deno|bun)$")
PERL_OU_RUBY = re.compile(r"^(perl|ruby)([\d][\w.-]*)?$")
OPCAO_COM_RESTO = set("MmIxCeEfFdDr")  # no grupo de opções curtas do perl/ruby, o resto é o valor delas (`-Mstrict`, `-I lib`)
# Marca da sessão (`.git/forge/projeto-*`): citá-la, ou usar um lançador que o hook não modela, é recusado no projeto.
CITA_A_MARCA = re.compile(r"\.git/forge|forge/projeto-")
LANCADORES_RECUSADOS = {"ionice", "chrt", "taskset", "flock", "unshare", "script"}
AWKS = {"awk", "gawk", "mawk", "nawk"}
# Opções longas do sed e do gawk: o getopt_long do GNU aceita qualquer prefixo não ambíguo (`--expr`, `--i`, `--inc`).
SED_LONGAS = ("binary", "debug", "expression", "file", "follow-symlinks", "help", "in-place", "line-length", "null-data",
              "zero-terminated", "posix", "quiet", "regexp-extended", "sandbox", "separate", "silent", "unbuffered", "version")
GAWK_LONGAS = ("assign", "bignum", "characters-as-bytes", "copyright", "debug", "dump-variables", "exec", "field-separator",
               "file", "gen-pot", "help", "include", "lint", "lint-old", "load", "non-decimal-data", "optimize", "posix",
               "pretty-print", "profile", "re-interval", "sandbox", "source", "traditional", "use-lc-numeric", "version")
# comando `w`/`W arquivo` do sed, com ou sem endereço antes (`$w`, `1,2w`), flag `s/a/b/w arquivo` e delimitador do usuário
# (`s|a|b|w arquivo`, `\%a%w arquivo`): qualquer `w`/`W` seguido de palavra; o custo (lado fechado) só aparece se for caminho protegido
SED_ESCREVE = re.compile(r"[wW]\s*(\S+)")
ESCRITA_NO_TEXTO = re.compile(  # só escrita de arquivo: `.replace(` de texto e `list.append(` não contam
    r"\.write\w*\(|writeFile|appendFile|unlink|\bos\.(remove|rename|replace)|shutil\.|rmtree|truncate|symlink|"
    r"rmSync|rmdir|copyFile|renameSync|cpSync|chmod|WriteStream|\w*open\w*\([^)]*[\"'][wa][bt+]?[\"']|>|"
    r"file_put_contents|\bf(write|puts)\b|File\.(delete|rename)|FileUtils|inplace|system\(", re.I)
TODOS_OS_ARGUMENTOS = {"rm", "mv", "tee", "truncate", "shred", "unlink", "rmdir", "touch"}
SO_DESTINO = {"cp", "ln", "install", "rsync"}
LEITORES = {"cat", "head", "tail", "less", "more", "bat", "nl", "tac", "source", ".", "grep", "egrep", "rg", "xxd",
            "od", "strings", "base64"}
ARQUIVO_ENV = re.compile(r"^\.env(\.[\w.-]+)?$")
ENV_DE_EXEMPLO = {"example", "sample", "template", "dist"}
HEREDOC = re.compile(r"(?<!<)<<-?\s*(['\"]?)([A-Za-z_][\w-]*)\1")
PUSH_COM_VALOR = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}
API_ADMIN = re.compile(r"/(git/refs|contents/|rulesets|branches/[^/]+/protection|collaborators|actions/(secrets|variables)"
                       r"|hooks|keys|transfer)")
GRAPHQL_PERIGOSO = re.compile(r"mergePullRequest|enablePullRequestAutoMerge|updateRef|createRef|deleteRef|"
                              r"createCommitOnBranch", re.I)
# R-CONTRIB: o que a sessão de outro projeto não faz no Forge (PR alheio, rótulos), pela API REST e pelo GraphQL.
CONTRIB_PR_ALHEIO = {"merge", "edit", "close", "ready", "reopen", "review"}
CONTRIB_ISSUE_ALHEIA = {"edit", "close", "reopen", "delete", "transfer", "lock", "unlock"}  # o PR também é uma issue
# Opções de `gh pr|issue` que levam valor: o texto delas (corpo, título, rótulo) não é o alvo do comando.
GH_COM_VALOR = {"-R", "--repo", "-b", "--body", "-F", "--body-file", "-t", "--title", "-l", "--add-label",
                "--remove-label", "-a", "--add-assignee", "--remove-assignee", "-m", "--milestone", "-B", "--base",
                "-p", "--add-project", "--remove-project", "-r", "--add-reviewer", "--remove-reviewer", "--subject",
                "-A", "--author-email", "--match-head-commit", "-c", "--comment", "--reason", "--label", "--assignee"}
CONTRIB_API = re.compile(r"(^|/)pulls/[^/]+|/issues/[^/]+/labels|/issues/[^/]+$|/issues/?(\?.*)?$|/labels(/|$)")
CONTRIB_GRAPHQL = re.compile(r"closePullRequest|reopenPullRequest|updatePullRequest|addLabelsToLabelable|"
                             r"removeLabelsFromLabelable|createIssue|createLabel|updateLabel|deleteLabel|updateIssue|closeIssue|"
                             r"markPullRequestReadyForReview|convertPullRequestToDraft", re.I)
PROFUNDIDADE = 3
CONFIG_PROTEGIDA = re.compile(r"^(user\.|core\.|commit\.gpgsign$|include|alias\.)", re.I)
CONFIG_LEITURA = {"--get", "--get-all", "--get-regexp", "--get-urlmatch", "--list", "-l", "--show-origin", "--show-scope",
                  "--show-names", "--name-only", "--help", "-h"}
CONFIG_ESCRITA = {"--unset", "--unset-all", "--add", "--replace-all", "--rename-section", "--remove-section", "-e",
                  "--edit"}
CONFIG_COM_VALOR = {"-f", "--file", "--blob", "--type", "--default"}

# Travas para atos perigosos (arquitetura do primeiro uso, 2.2 e 2.5). Valem para todo papel e todo perfil; no perfil
# `iniciante` a recusa e a confirmação trazem a consequência em linguagem simples. Mensagem de uma linha (200 caracteres).
REPO_APAGAR = re.compile(r"^/?repos/[^/]+/[^/]+/?$")
GRAPHQL_APAGAR = re.compile(r"mutation[^}]*deleteRepository", re.I)
VISIBILIDADE_PUBLICA = re.compile(r"\bprivate[\"']?\s*[=:]\s*[\"']?false\b|\bvisibility[\"']?\s*[=:]\s*[\"']?public\b", re.I)
CAMINHOS_NO_GIT = {"rm", "mv", "checkout", "restore"}  # subcomandos que mexem em arquivos do projeto
PASTAS_PROTEGIDAS = {".forge", ".githooks", ".claude"}
MAGIA_DE_PATHSPEC = re.compile(r"^:(\(.*?\)|[/!^]*)")  # `:(top)`, `:(literal)`, `:/`, `:!`...
GLOB_DE_PATHSPEC = re.compile(r"[*?\[\\]")
CHECKOUT_COM_VALOR = {"-b", "-B", "--orphan"}

VARIAVEL = re.compile(r"\$\{?(\w+)\}?|\$\(|`")
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
CORPO_DE_LACO = {"do", "then", "else", "elif", "if", "while", "until", "!", "{"}
REMOCAO = {"rm", "mv", "rmdir", "unlink", "shred"}

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


def casa(rel, caminho):
    """`rel` é o `caminho` (arquivo) ou está dentro dele (diretório, que termina em `/`)."""
    return rel.startswith(caminho) or rel + "/" == caminho if caminho.endswith("/") else rel == caminho


def em_qualquer_lugar(posix, caminho):
    return ("/" + caminho) in posix + "/" if caminho.endswith("/") else posix.endswith("/" + caminho)


def tirar_heredocs(comando):
    """Separa o corpo dos heredocs (que não são comandos) da linha: devolve (comando, [(linha do dono, corpo)])."""
    linhas, saida, corpos, i = comando.split("\n"), [], [], 0
    while i < len(linhas):
        linha = linhas[i]
        saida.append(linha)
        i += 1
        for m in HEREDOC.finditer(linha):
            corpo = []
            while i < len(linhas) and linhas[i].strip() != m.group(2):
                corpo.append(linhas[i])
                i += 1
            i += 1  # o marcador de fim
            corpos.append((linha, "\n".join(corpo)))
    return "\n".join(saida), corpos


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


def sed_no_lugar(args):
    """`sed` com edição no lugar: `-i` sozinho, agrupado ou com sufixo (`-ni`, `-i.bak`) ou `--in-place[=sufixo]` em
    qualquer abreviação (`--i`, `--in-pl=~`)."""
    return any(re.fullmatch(r"-[a-zA-Z]*i.*", a) or longa_do_gnu(a, SED_LONGAS) == "in-place" for a in args)


def separar_lancadores(palavras):
    """Tira os prefixos que só repassam o comando (`env`, `sudo`, `nice`, `timeout`, `xargs`...) com as opções
    deles, para classificar o comando de verdade; opções do comando seguinte não se perdem. Devolve (comando,
    atribuições feitas pelos lançadores): `env GH_REPO=x gh ...` passa a variável ao `gh` como `GH_REPO=x gh ...`."""
    palavras, lancadas = sem_atribuicoes(palavras), []
    while palavras and Path(palavras[0]).name in LANCADORES:
        nome, com_valor = Path(palavras[0]).name, LANCADORES[Path(palavras[0]).name]
        i, dividido = 1, []
        while i < len(palavras) and palavras[i].startswith("-") and palavras[i] != "-":
            opcao = palavras[i]
            i += 1
            if opcao == "--":
                break
            split = valor_do_split_string(opcao, palavras[i] if i < len(palavras) else "") if nome == "env" else None
            if split is not None:  # `env -S '<comando>'`: o valor é o comando, dividido em palavras
                texto, consome = split
                i += consome
                dividido += shlex.split(texto)  # aspas abertas: ValueError, e o comando não é analisável
            elif opcao in com_valor or (nome == "env" and re.fullmatch(r"-[a-zA-Z]*[uC]", opcao)):
                i += 1
        if nome == "timeout" and i < len(palavras):
            i += 1  # a duração
        cauda = dividido + palavras[i:]
        resto = sem_atribuicoes(cauda)
        lancadas += cauda[:len(cauda) - len(resto)]
        palavras = resto
    return palavras, lancadas


def valor_do_split_string(opcao, seguinte):
    """(texto, 1 se consumiu a palavra seguinte) do `env -S`/`--split-string`, o comando que o `env` divide e roda;
    None se a opção não é essa. No grupo curto (`-iS`), a primeira letra que leva valor decide (`-uS` é `-u S`)."""
    if opcao == "--split-string":
        return seguinte, 1
    if opcao.startswith("--split-string="):
        return opcao.split("=", 1)[1], 0
    if opcao.startswith("--"):
        return None
    for k, letra in enumerate(opcao[1:], 1):
        if letra in ENV_COM_VALOR_CURTA:
            if letra != "S":
                return None
            return (opcao[k + 1:], 0) if opcao[k + 1:] else (seguinte, 1)
    return None


def sem_lancadores(palavras):
    return separar_lancadores(palavras)[0]


def exporta(palavras):
    """`export`, `declare -x` e `typeset -x` passam as variáveis aos comandos seguintes."""
    return palavras[:1] == ["export"] or palavras[:1] in (["declare"], ["typeset"]) and any(
        re.fullmatch(r"-[a-zA-Z]*x[a-zA-Z]*", p) for p in palavras[1:])


def abreviacao_de(opcao, longas):
    """A opção longa (sem o `=valor`) é uma das `longas` ou a abreviação dela que o git aceita (`--upload-p`)."""
    nome = opcao.split("=", 1)[0]
    return nome.startswith("--") and len(nome) > 3 and any(o.startswith(nome) for o in longas)


class Guarda:
    def __init__(self, hook, politica, papel):
        self.h, self.pol, self.papel = hook, politica, papel
        self._ramo = None
        self._forge = None
        self.externo = None  # nome da sessão de outro projeto (prefixo `melhoria/<nome>-`), quando vem da raiz dela
        self.sessao_forge = False  # a raiz da sessão (`CLAUDE_PROJECT_DIR`) é um clone do Forge
        self.ambiente = {}   # GH_REPO e GIT_DIR definidos antes, na mesma linha de comando
        self._repos = {}     # (raiz git, remoto) -> é o Forge
        self.linha = ""      # a linha de comando inteira, como veio (nível 0)
        self.perguntas = []  # confirmações pendentes da linha (perfil iniciante)
        self.lancador_recusado = None  # lançador da linha que o hook não modela (`LANCADORES_RECUSADOS`), recusado no fim
        leitura = politica.get("so_leitura")
        self.leitura = leitura if leitura and papel in leitura["papeis"] else None  # papel só de leitura (conferente)

    # Respostas -------------------------------------------------------------------------------
    def pode(self, acao):
        return self.papel in self.pol["acoes"].get(acao, [])

    def barrar(self, rid, o_que, corrigir, simples=None):
        """Recusa (saída 2). No perfil iniciante, `simples` (SIMPLES) troca o texto técnico pela consequência."""
        if simples and self.h.iniciante():
            bloquear(rid, SIMPLES[simples])
        bloquear(rid, f"{o_que}. Corrigir: {corrigir}")

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

    @property
    def projeto(self):
        """Nome do projeto da sessão: o prefixo próprio das branches de contribuição é `melhoria/<nome>-`."""
        return self.h.raiz.name if self.externo is None else self.externo

    def clone_do_forge(self):
        """A raiz em que o hook age é o Forge (dá poder: R-CONTRIB não se aplica). Projeto nunca é o Forge."""
        if self.externo is not None:
            return False
        if self._forge is None:
            self._forge = e_clone_do_forge(self.h.raiz)
        return self._forge

    def regras_do_forge(self):
        """Os caminhos `so_forge` valem: a raiz tem o manifesto do Forge. Só protege mais, então basta o arquivo."""
        return self.externo is None and tem_manifesto_do_forge(self.h.raiz)

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
                parecer.aponta_para_o_forge(url) for url in self.urls_dos_remotos(raiz, remoto))
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

    @staticmethod
    def caminho(pasta, texto):
        """Destino de `cd`/`-C`/`--git-dir`: expande `~` e variáveis de ambiente, como o shell faria."""
        return pasta / Path(os.path.expandvars(texto)).expanduser()

    def alvo_do_forge(self, pasta, repo=None, remoto=None):
        """R-CONTRIB: o comando da sessão de OUTRO projeto (raiz que não é o Forge) atinge o repositório do Forge:
        `repo` aponta para ele ou, sem `repo`, o repositório da pasta é o Forge (`repositorio_do_forge`)."""
        if self.clone_do_forge():
            return False
        return parecer.aponta_para_o_forge(repo) if repo else self.repositorio_do_forge(pasta, remoto)

    def caminho_barrado(self, caminho):
        """(rid, o quê, como corrigir) se o `caminho` (já resolvido) é protegido para o papel; senão None."""
        raiz, home = Path(os.path.realpath(self.h.raiz)), Path(os.path.realpath(Path.home()))
        pais = {caminho, *caminho.parents}
        posix = caminho.as_posix()
        formas = []
        if raiz in pais:
            formas.append(("proj", caminho.relative_to(raiz).as_posix()))
        if home in pais:
            formas.append(("home", "~/" + caminho.relative_to(home).as_posix()))
        no_claude_do_home = (home / ".claude") in pais
        for e in self.pol["caminhos"]:
            c = e["caminho"]
            if c.startswith("~/"):
                achou = any(t == "home" and casa(r, c) for t, r in formas)
            elif e.get("so_forge") and not self.regras_do_forge():
                continue
            else:
                achou = any(t == "proj" and casa(r, c) for t, r in formas) or (
                    not e["quem"] and not no_claude_do_home and em_qualquer_lugar(posix, c))
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
        p = Path(caminho).expanduser()
        return Path(os.path.realpath(p if p.is_absolute() else pasta / p))

    def checar_escrita(self, caminho, pasta):
        """Na dúvida, recusa: o que vem depois de uma substituição (`$(git rev-parse --show-toplevel)/docs/reviews/x`) é
        conferido também a partir da raiz do projeto."""
        alvos = [self.resolver(self.expandir(caminho, pasta), pasta)]
        resto = caminho.rsplit(OPACO["$"], 1)[1].lstrip("/") if OPACO["$"] in caminho else ""
        if resto:
            alvos.append(self.resolver(resto, Path(self.h.raiz)))
        for alvo in alvos:
            achado = self.caminho_barrado(alvo)
            if achado:
                self.barrar(*achado)

    def expandir(self, caminho, pasta):
        """`$PWD`, `$CLAUDE_PROJECT_DIR` e `$HOME` (com ou sem chaves; as aspas o shlex já tirou) viram o caminho real."""
        valores = {"PWD": str(pasta), "CLAUDE_PROJECT_DIR": str(self.h.raiz), "HOME": str(Path.home())}
        return VARIAVEL.sub(lambda m: valores.get(m.group(1), m.group(0)), caminho)

    def checar_remocao(self, caminho, pasta):
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
            for dentro in ([home] if c.startswith("~/") else raizes):
                protegido = home / c[2:] if c.startswith("~/") else dentro / c
                if alvo != dentro and dentro in alvo.parents and alvo in Path(os.path.realpath(protegido)).parents:
                    self.barrar("R-CONFORMIDADE", f"apagar {alvo.name}/ apaga {c}: {e['motivo']}",
                                f"só o usuário altera; proponha o diff (R-DECISAO); {SUGESTAO}", "instalacao")

    def checar_texto(self, texto):
        """Escrita em caminho protegido com o caminho em literal dentro de `python -c`, `node -e`, script."""
        if not ESCRITA_NO_TEXTO.search(texto):
            return
        raiz = Path(os.path.realpath(self.h.raiz))
        for e in self.pol["caminhos"]:
            c = e["caminho"]
            literais = (c.replace("~", str(Path.home()), 1), c) if c.startswith("~/") else (c,)
            if any(lit in texto for lit in literais):
                achado = self.caminho_barrado(self.resolver(c.replace("~", str(Path.home()), 1) if c.startswith("~/")
                                                            else c, raiz))
                if achado:
                    self.barrar(*achado)

    # Write, Edit, MultiEdit, NotebookEdit -------------------------------------------------------
    def arquivo(self, entrada):
        if self.leitura:
            self.barrar("R-CONFORMIDADE", f"escrita de arquivo pelo papel só de leitura ({self.papel})", DICA_LEITURA)
        caminho = entrada.get("file_path") or entrada.get("notebook_path")
        if isinstance(caminho, str) and caminho:
            self.checar_escrita(caminho, self.h.cwd())

    # Bash ----------------------------------------------------------------------------------------
    def bash(self, comando, pasta, nivel=0, so_substituicoes=False):
        """Confere a linha. `so_substituicoes`: a linha é uma palavra entre aspas (`"$(git log)"`), e só o conteúdo das
        substituições dela é comando."""
        if nivel > PROFUNDIDADE:
            self.ilegivel(comando, pasta)
            return
        if self.leitura and nivel:  # depois da gramática, só `$(`/crase entre aspas simples: o bash só roda por reavaliação
            self.barrar("R-CONFORMIDADE", f"substituição dentro de aspas pelo papel só de leitura ({self.papel})",
                        "escreva o nome literal em vez de $( ou crase, mesmo entre aspas (para procurar um trecho, "
                        "grep -F 'trecho' <arquivo>, sem esses sinais)")
        if self.leitura and nivel == 0:
            self.gramatica_de_leitura(comando)
        # ADR 0011, item 2: linha com marcador crítico e construção não modelada recusa; a recusa vem depois das
        # checagens da linha, para que a regra mais específica (R-MAIN, R-VERIFY...) fale primeiro.
        achado = None if self.leitura or not CRITICO.search(comando) else construcao_nao_modelada(comando)
        original = comando
        if nivel == 0 and self.h.raiz and self.raiz_e_projeto() and CITA_A_MARCA.search(comando):
            self.barrar("R-CONFORMIDADE", "a linha cita a marca da sessão (.git/forge): só o usuário mexe nela",
                        f"não cite .git/forge; {SUGESTAO}")
        comando, corpos = tirar_heredocs(comando)
        comando = re.sub(r"\$\(\s*pwd(\s+-[LP])?\s*\)", "$PWD", comando)  # `$(pwd)/x` é um caminho conhecido
        try:
            partes = list(comandos(comando))
        except ValueError:
            self.nao_modelada(achado)
            if nivel:
                self.ilegivel(comando, pasta)
            return  # aspas desbalanceadas: o próprio shell vai recusar
        ramos = {}
        if nivel == 0:
            self.ambiente = {}
            self.linha = original
            self.sugerir_na_linha(original)
        contextos = {(): (pasta, ramos)}  # cada substituição roda num subshell: `cd` e branch lá dentro ficam lá

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
        pasta = contextos[()][0]
        for dono, corpo in corpos:
            if re.search(r"\b(bash|sh|zsh|dash)\b", dono):
                self.bash(corpo, pasta, nivel + 1)
            elif any(INTERPRETES.match(Path(t).name) or Path(t).name in AWKS for t in re.split(r"[\s;&|()`<>\"'\\]+", dono)):
                self.checar_texto(corpo)
        self.nao_modelada(achado)
        if self.lancador_recusado:  # depois das regras específicas da linha (R-MAIN, R-VERIFY, atualizar...)
            self.barrar("R-CONFORMIDADE", f"lançador `{self.lancador_recusado}` repassa o comando sem que o hook o veja, "
                                          "numa sessão de projeto", f"rode o comando direto, sem o lançador; {SUGESTAO}")

    def nao_modelada(self, achado):
        """ADR 0011, item 2: recusa a linha crítica com construção que o analisador não modela (`construcao_nao_modelada`)."""
        if achado is not None:
            self.barrar("R-CONFORMIDADE", f"`{achado}` com ação crítica: o hook não modela",
                        "branch literal, um comando por linha, sem # entre linhas, "
                        "$, crase, chaves nem case; heredoc só <<'FIM'")

    def gramatica_de_leitura(self, linha):
        """ADR 0011, item 1: antes de qualquer outra checagem, a linha do papel só de leitura precisa caber na gramática
        positiva (`fora_da_gramatica_de_leitura`). O que ela não modela (`$`, crase, `\\`, `#`, chaves, globs,
        redirecionamento, substituição, várias linhas) recusa, e a mensagem diz a forma explícita."""
        sinal = fora_da_gramatica_de_leitura(linha)
        if sinal is not None:
            self.barrar("R-CONFORMIDADE", f"`{sinal}` fora da gramática do papel só de leitura ({self.papel})",
                        "um comando por chamada; sinais só entre aspas simples; "
                        "no lugar de echo $?: && echo contém || echo não contém")

    def sugerir_na_linha(self, linha):
        """F6, lista branca estrita: a única linha com `sugerir` que passa é `forge sugerir --guardar "<texto>"` inteira. Qualquer
        outra que contenha a palavra, mesmo ofuscada (`sug""erir`, `$S`, `forge $S`), é recusada: na dúvida, recusa."""
        if guardar_exato(linha):
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
        finally:
            for nome, valor in antes.items():
                if valor is None:
                    self.ambiente.pop(nome, None)
                else:
                    self.ambiente[nome] = valor

    def segmento(self, palavras, pasta, ramos, nivel):
        """Analisa um comando simples; devolve a pasta depois dele (acompanha `cd`)."""
        while palavras and palavras[0] in CORPO_DE_LACO:  # `do rm ...`, `then ...`: o comando vem depois da palavra
            palavras = palavras[1:]
        atribuicoes = palavras[: len(palavras) - len(sem_atribuicoes(palavras))]
        originais = sem_atribuicoes(palavras)
        try:
            palavras, lancadas = separar_lancadores(palavras)
        except ValueError:  # `env -S` com aspas abertas
            self.ilegivel(" ".join(palavras), pasta)
            return pasta
        atribuicoes += lancadas
        if self.leitura:
            if originais[:1] != palavras[:1]:
                self.barrar("R-CONFORMIDADE", f"lançador `{Path(originais[0]).name}` repassa argumentos que o hook não vê "
                                              f"(papel só de leitura: {self.papel})", DICA_LEITURA)
            self.checar_so_leitura(palavras, atribuicoes)
        for a in atribuicoes:
            if "core.hookspath" in a.lower():
                self.barrar("R-VERIFY", "core.hooksPath por variável de ambiente", "não troque o caminho dos hooks")
        definidas = [p for p in palavras[1:] if not p.startswith("-")] if exporta(palavras) else \
            [] if palavras else atribuicoes
        for a in definidas:
            nome, _, valor = a.partition("=")
            if nome in VARIAVEIS_DA_LINHA and valor:
                self.ambiente[nome] = valor  # vale para os comandos seguintes da linha
        for p in palavras:  # substituição entre aspas: a palavra chega inteira e o conteúdo dela é conferido aqui
            if "`" in p:
                self.bash(p, pasta, nivel + 1)
            elif "$(" in p.replace(OPACO["$"], ""):
                self.bash(p, pasta, nivel + 1, so_substituicoes=True)
        if not palavras:
            return pasta
        prog = Path(palavras[0].lstrip("`")).name
        args = palavras[1:]
        if self.raiz_e_projeto() and LANCADORES_RECUSADOS & {prog, Path(originais[0]).name}:
            self.lancador_recusado = (LANCADORES_RECUSADOS & {prog, Path(originais[0]).name}).pop()  # recusa no fim da linha
        parte = parecer.analisar(palavras)
        if prog == "pushd":  # como o `cd`: o destino é o primeiro argumento que não é opção
            alvo = next((a for a in args if not a.startswith("-")), None)
            return self.caminho(pasta, alvo) if alvo else pasta
        if parte and parte[0] == "cd":
            return self.caminho(pasta, parte[1]) if parte[1] else Path.home()
        if parte and parte[0] == "branch":
            raiz = raiz_do_projeto(pasta / parte[1] if parte[1] else pasta)
            if raiz:
                ramos[raiz.resolve()] = parte[2]
        if prog in SHELLS:
            self.atualizacao(palavras, so_binarios=True)
        elif prog in ENVOLVEDORES or INTERPRETES.match(prog) or prog == "forge" or prog in BINARIOS_DE_ATUALIZACAO:
            self.atualizacao(palavras)
        no_lugar = bool(PERL_OU_RUBY.match(prog)) and edita_no_lugar(args)
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
            self.gh(palavras, parte, pasta, self.da_atribuicao(atribuicoes, "GH_REPO"))
        elif prog == "claude":
            self.claude(args)
        elif prog in TODOS_OS_ARGUMENTOS or (prog == "sed" and sed_no_lugar(args)):
            for a in args:
                if not a.startswith("-"):
                    self.checar_escrita(a, pasta)
                    if prog in REMOCAO:
                        self.checar_remocao(a, pasta)
        elif prog in SO_DESTINO:
            alvo = next((args[i + 1] for i, a in enumerate(args[:-1]) if a in ("-t", "--target-directory")), None)
            alvo = alvo or next((a for a in reversed(args) if not a.startswith("-")), None)
            if alvo:
                self.checar_escrita(alvo, pasta)
        elif prog == "dd":
            for a in args:
                if a.startswith("of="):
                    self.checar_escrita(a[3:], pasta)
        elif prog in self.pol["pacotes"]:
            self.pacote(prog, args)
        if prog == "sed":  # `w arquivo` no script escreve, com ou sem `-i`
            for a in args:
                for destino in SED_ESCREVE.findall(script_do_sed(a)):
                    self.checar_escrita(destino, pasta)
        if prog in LEITORES:
            for a in args:
                nome = Path(a).name
                if ARQUIVO_ENV.match(nome) and nome.rsplit(".", 1)[-1] not in ENV_DE_EXEMPLO:
                    self.barrar("R-CONFORMIDADE", f"ler {nome} expõe segredos",
                                "peça ao usuário o valor de que precisa (R-DECISAO)")
        return pasta

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
        if prog == "forge-check" and any(re.match(r"--[\w-]+=-", a) for a in args):
            self.barrar("R-CONFORMIDADE", f"`{chave}` com valor de opção que começa com `-` (papel só de leitura: "
                                          f"{self.papel})", DICA_LEITURA)
        if prog == "gh" and any(a in ("--web", "-w") for a in args):
            self.barrar("R-CONFORMIDADE", f"`{chave} --web` abre o navegador (papel só de leitura: {self.papel})", DICA_LEITURA)
        if prog == "git":
            self.git_so_leitura(chave, args[1:])
        if "/" in prog or chave not in self.leitura["comandos"]:
            self.barrar("R-CONFORMIDADE", f"`{chave}` fora da lista do papel só de leitura ({self.papel})", DICA_LEITURA)

    def git_so_leitura(self, chave, args):
        """Opções do git no papel só de leitura: lista branca no `ls-remote` (sem transporte `<x>::`, que roda o
        `git-remote-<x>`); nos outros subcomandos, recusa as de `GIT_EXECUTA`, inclusive abreviadas (`--textconv` e
        `--filters` rodam o driver configurado no repositório), e o formato `%G` (`FORMATO_ASSINATURA`)."""
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

    def git(self, palavras, parte, pasta, ramos, git_dir=None, atribuicoes=()):
        i, pasta_git, opcoes = 1, self.caminho(pasta, git_dir) if git_dir else pasta, self.pathspecs_da_linha(atribuicoes)
        while i < len(palavras) and palavras[i].startswith("-"):
            if palavras[i].endswith("-pathspecs"):  # `--literal-pathspecs`...: valem também para o `ls-files` do hook
                opcoes.append(palavras[i])
            if palavras[i] in ("-C", "--git-dir") and i + 1 < len(palavras):
                pasta_git = self.caminho(pasta, palavras[i + 1])
            elif palavras[i].startswith("--git-dir="):
                pasta_git = self.caminho(pasta, palavras[i].split("=", 1)[1])
            i += 2 if palavras[i] in parecer.GIT_COM_VALOR else 1
        sub, args = (palavras[i], palavras[i + 1:]) if i < len(palavras) else (None, [])
        ativacao = sub == "config" and args == ["core.hooksPath", ".githooks"]  # R-CONTRIB: ativar o hook do repositório
        if any("core.hookspath" in p.lower() for p in (palavras[:i] if ativacao else palavras)):
            self.barrar("R-VERIFY", "core.hooksPath", "não desative nem troque o caminho dos hooks")
        if "--no-verify" in args or (sub == "commit" and any(re.fullmatch(r"-[a-zA-Z]*n[a-zA-Z]*", a)
                                                             for a in args)):
            self.barrar("R-VERIFY", f"git {sub} --no-verify", "corrija a causa do hook que falhou")
        if sub == "config" and not ativacao:
            self.git_config(args)
        self.git_trava(sub, args, pasta_git, ramos)
        if sub in CAMINHOS_NO_GIT:
            self.git_caminhos(sub, args, [pasta, pasta_git], opcoes)
        if sub == "push":
            self.git_push(args, pasta_git, ramos)
        elif parte and parte[0] == "merge" and parte[2]:
            atual = self.ramo_em(pasta_git, ramos)
            if atual in INTEGRACAO and not all(b == atual for b, _ in parte[2]):
                if atual in ("main", "master"):
                    self.barrar("R-MAIN", f"merge na {atual} é do usuário", "abra o PR e peça ao usuário que o mescle")
                if not self.pode("merge_integracao"):
                    self.barrar("R-CONFORMIDADE", f"merge em {atual} {self.so_de('merge_integracao')} "
                                                  f"(papel: {self.papel})", "peça ao tech-lead")

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
                self.checar_escrita(c, pasta)
                self.checar_remocao(c, pasta)
                if com_origem or sub in ("rm", "mv") or not self.varredura(c):
                    for alvo in filter(self.pode_ser_protegido, self.tracked_do_pathspec(c, pasta, opcoes)):
                        self.checar_escrita(alvo, pasta)
                        self.checar_remocao(alvo, pasta)

    def pode_ser_protegido(self, caminho):
        """Filtro barato para `git rm -r <pasta grande>`: só confere um por um o arquivo cujo caminho cita algum caminho
        da política (mais o perfil e o manifesto), ou todos se o papel só escreve numa lista (`escrita_permitida`).
        Só deixa de fora o que `caminho_barrado` não barraria."""
        if self.pol.get("escrita_permitida", {}).get(self.papel) is not None:
            return True
        if not hasattr(self, "_citacoes"):
            self._citacoes = tuple({e["caminho"].removeprefix("~/").rstrip("/") for e in self.pol["caminhos"]}
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

    def tracked_do_pathspec(self, pathspec, pasta, opcoes):
        """Os arquivos do índice que o git alcança com o pathspec (`git ls-files`, só leitura). Se o git não responde
        (fora de repositório, limite de tempo), vale o pathspec literal: o `git rm` também não teria o que fazer."""
        if not Path(pasta).is_dir():
            return []
        try:
            cod, saida = forge_check().git(pasta, *opcoes, "ls-files", "-z", "--", pathspec, bruto=True)
        except (OSError, subprocess.SubprocessError):
            cod, saida = 1, b""
        if cod:
            if GLOB_DE_PATHSPEC.search(pathspec) or pathspec.startswith(":"):
                self.barrar("R-CONFORMIDADE", f"o git não resolveu o pathspec {pathspec!r}",
                            "use o caminho do arquivo, sem magia nem curinga (na dúvida, recusa)")
            return []
        return [str(Path(pasta) / n) for n in forge_check().nomes_z(saida)]

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
    def branch_movida(sub, args, positivos):
        """Branch que `checkout -B`, `switch -C` ou `branch -f` recriam apontando para outro commit; senão None."""
        if sub == "branch" and any(a == "--force" or re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", a) for a in args):
            return positivos[0] if positivos else None
        letra = {"checkout": "B", "switch": "C"}.get(sub)
        for i, a in enumerate(args):
            if letra and (re.fullmatch(rf"-[a-zA-Z]*{letra}", a) or (sub == "switch" and a == "--force-create")):
                return args[i + 1] if i + 1 < len(args) else None
        return None

    def git_config(self, args):
        """`git config` que grava identidade, `core.*`, assinatura, `include*` ou alias: fora do papel de todos. Numa
        worktree, sem `--worktree` ele grava no `.git/config` comum a todas as cópias (R-CONFORMIDADE)."""
        if "--worktree" in args or any(a in CONFIG_LEITURA or a.startswith(("--get", "--show-")) for a in args):
            return
        chaves, pulo = [], False
        for a in args:
            if pulo:
                pulo = False
            elif a in CONFIG_COM_VALOR:
                pulo = True
            elif not a.startswith("-"):
                chaves.append(a)
        grava = len(chaves) > 1 or any(a in CONFIG_ESCRITA for a in args)  # só a chave é leitura
        if grava and chaves[:1] and CONFIG_PROTEGIDA.match(chaves[0]):
            self.barrar("R-CONFORMIDADE", f"git config grava {chaves[0]} na configuração compartilhada do repositório",
                        "use --worktree ou deixe ao usuário (R-DECISAO)")

    def git_push(self, args, pasta, ramos):
        refs = []
        pulo = False
        for a in args:
            if pulo:
                pulo = False
            elif a in PUSH_COM_VALOR:
                pulo = True
            elif a.startswith("--force") or re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", a) or a.startswith("+"):
                self.barrar("R-VERIFY", "git push --force", "nunca force o push; refaça com um commit novo", "forca")
            elif a == "--mirror":
                self.barrar("R-VERIFY", "git push --mirror", "sobrescreve o remoto como um force push; "
                            "envie só a branch, com um commit novo", "forca")
            elif not a.startswith("-"):
                refs.append(a)
        remoto, refs = (refs[0] if refs else None), refs[1:]
        if not refs and "--tags" in args:
            return
        atual = None
        destinos = []
        for r in refs or [None]:
            destino = r.split(":")[-1] if r else None
            if destino in (None, "", "HEAD"):
                atual = atual or self.ramo_em(pasta, ramos)
                destino = atual
            destinos.append(nome_da_branch(destino))
        for d in destinos:
            if d in ("main", "master"):
                self.barrar("R-MAIN", f"push direto para {d}", "abra um PR; a main é do usuário", "main")
            if d in INTEGRACAO:
                self.barrar("R-CONFORMIDADE", f"push direto para {d}", "abra um PR a partir de uma branch de trabalho",
                            "main")
        # o remoto nomeado (a URL dele, resolvida no repositório da pasta), a URL dada ou, sem remoto, a pasta
        if self.alvo_do_forge(pasta, remoto=remoto) or (remoto and self.alvo_do_forge(pasta, remoto)):
            propria = f"melhoria/{self.projeto}-"
            for d in destinos:
                if not d.startswith(propria):
                    self.barrar("R-CONTRIB", f"push para {d}: a sessão de outro projeto só envia a própria "
                                             f"branch `{propria}<tema>`", "abra o PR da sua branch e espere o Forge integrar")

    # gh ----------------------------------------------------------------------------------------------
    def graphql_perigoso(self, args, pasta):
        """Mutação do GraphQL que fecha, edita ou rotula PR: o ID é global (sem slug), então vale para toda sessão
        de projeto. O texto vem inline ou de arquivo (`-F query=@arq`, `--input arq`); o que não dá para ler
        (`--input -`, arquivo ausente) falha fechado."""
        textos = []
        for i, a in enumerate(args):
            valor = args[i + 1] if a == "--input" and i + 1 < len(args) else a.split("=", 1)[-1]
            if a == "--input" or a.startswith("--input=") or re.search(r"=@", a) or (
                    a in ("-F", "--field") and i + 1 < len(args) and "=@" in args[i + 1]):
                arq = valor if a.startswith("--input") else (args[i + 1] if a in ("-F", "--field") else a).split("=@", 1)[-1]
                try:
                    textos.append((pasta / os.path.expandvars(arq)).expanduser().read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    return True
            else:
                textos.append(a)
        return any("mutation" in t and CONTRIB_GRAPHQL.search(t) for t in textos)

    def gh_contrib(self, palavras, pasta, repo_env):
        """R-CONTRIB: a sessão de outro projeto abre o PR e para; não mescla, edita, fecha, revisa nem rotula no
        Forge. O alvo vem de `-R`, de `GH_REPO`, de URL entre os argumentos ou da pasta (clone de contribuição)."""
        pos = parecer.posicionais(palavras[1:], GH_COM_VALOR)
        grupo, sub = (pos + [None, None])[:2]
        repo = parecer.opcao(palavras[1:], "--repo", "-R") or repo_env
        proibido = (grupo == "pr" and sub in CONTRIB_PR_ALHEIO or grupo == "issue" and sub in CONTRIB_ISSUE_ALHEIA
                    or grupo == "label")
        if proibido:
            alvo = self.alvo_do_forge(pasta, repo) or any(parecer.aponta_para_o_forge(a) for a in pos[2:])
            if alvo and not self.clone_do_forge():
                self.barrar("R-CONTRIB", f"gh {grupo}{' ' + sub if grupo != 'label' else ''} no Forge: a sessão de outro "
                                         "projeto só abre o PR da própria branch", "avise o usuário e espere o Forge integrar")
        elif grupo == "issue" and sub == "create":
            # Issue nova no Forge é da pessoa: `forge sugerir`, no terminal dela, fora do Claude (onde o hook não roda).
            alvo = self.alvo_do_forge(pasta, repo) or any(parecer.aponta_para_o_forge(a) for a in pos[2:])
            if alvo and not self.clone_do_forge():
                self.barrar("R-CONTRIB", "gh issue create no Forge: só a pessoa envia sugestão, no terminal dela, fora do "
                                         "Claude, com `forge sugerir`", "guarde o texto com `forge sugerir --guardar \"<texto>\"` "
                                         "e avise a pessoa")
        elif grupo == "api":
            args = palavras[2:]
            endpoint = parecer.endpoint_da_api(args)
            dono = re.match(r"^/?repos/([^/]+/[^/]+)", endpoint)
            if not parecer.metodo_mutante(args):
                return
            if endpoint == "graphql":
                alvo, perigoso = True, self.graphql_perigoso(args, pasta)
            else:
                slug = dono.group(1) if dono and "{" not in dono.group(1) else repo_env  # {owner}/{repo} = GH_REPO
                alvo, perigoso = self.alvo_do_forge(pasta, slug), bool(CONTRIB_API.search(endpoint))
            if alvo and perigoso and not self.clone_do_forge():
                self.barrar("R-CONTRIB", "gh api que cria issue ou edita, fecha, mescla ou rotula PR no Forge: a sessão de outro "
                                         "projeto só abre o PR da própria branch", "avise o usuário e espere o Forge integrar")

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
        elif grupo == "api" and parecer.metodo_mutante(palavras[2:]):
            args = palavras[2:]
            if (parecer.opcao(args, "--method", "-X") or "").upper() == "DELETE" and REPO_APAGAR.match(
                    parecer.endpoint_da_api(args)) or GRAPHQL_APAGAR.search(" ".join(args)):
                self.barrar(*apagar)
            if VISIBILIDADE_PUBLICA.search(" ".join(args)) or self.input_publica(args, pasta):
                self.barrar(*publico)

    @staticmethod
    def input_publica(args, pasta):
        """`gh api --input arq` com `private:false`/`visibility:public` no corpo. No endpoint do repositório, PATCH ou PUT
        com corpo que não dá para ler (`--input -`, arquivo ausente) falha fechado."""
        for i, a in enumerate(args):
            if a != "--input" and not a.startswith("--input="):
                continue
            arq = a.split("=", 1)[1] if "=" in a else (args[i + 1] if i + 1 < len(args) else "")
            try:
                if VISIBILIDADE_PUBLICA.search((pasta / os.path.expandvars(arq)).expanduser().read_text(encoding="utf-8")):
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
        direto = Path(palavras[0]).name in ("forge", *BINARIOS_DE_ATUALIZACAO)  # só o comando em si, não o texto que ele recebe
        for i, palavra in enumerate(todas[:1] if direto else todas):
            nome = Path(palavra).name
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

    def gh(self, palavras, parte, pasta, repo_env=None):
        self.gh_trava(palavras, pasta)
        self.gh_contrib(palavras, pasta, repo_env)
        if not parte:
            return
        if parte[0] == "pr" and not self.pode("pr_criar"):
            self.barrar("R-CONFORMIDADE", f"gh pr create {self.so_de('pr_criar')} (papel: {self.papel})",
                        "peça ao tech-lead ou ao jarvis")
        elif parte[0] == "prmerge":
            raiz = self.h.raiz
            branch = parecer.branch_do_pr(raiz, parte[2])
            if not branch:
                return  # o parecer pede o nome da branch
            base = parecer.base_do_pr(raiz, branch)
            if base in ("main", "master"):
                self.barrar("R-MAIN", f"gh pr merge de `{branch}` (base {base}) é do usuário",
                            "deixe o PR aberto e peça ao usuário")
            if not self.pode("pr_merge_integracao"):
                self.barrar("R-CONFORMIDADE", f"gh pr merge {self.so_de('pr_merge_integracao')} "
                                              f"(papel: {self.papel})", "peça ao tech-lead")
        elif parte[0] == "api":
            args = parte[1]
            if parecer.metodo_mutante(args) and (
                    API_ADMIN.search(parecer.endpoint_da_api(args))
                    or any("mutation" in a and GRAPHQL_PERIGOSO.search(a) for a in args)):
                self.barrar("R-CONFORMIDADE", "gh api que altera refs, regras, acessos ou faz merge",
                            "use gh pr/git pelo papel certo ou leve ao usuário (R-DECISAO)")

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


def entrada_valida(e):
    """Forma de uma entrada de `caminhos`: sem ela o hook cairia em KeyError/TypeError e liberaria (saída 0)."""
    def texto(v):
        return isinstance(v, str) and bool(v)
    return (isinstance(e, dict) and texto(e.get("caminho")) and texto(e.get("motivo"))
            and isinstance(e.get("quem"), list) and all(isinstance(q, str) for q in e["quem"])
            and isinstance(e.get("so_forge", False), bool) and ("branch" not in e or texto(e["branch"])))


def lista_de_textos(v):
    return isinstance(v, list) and all(isinstance(t, str) for t in v)


def pacote_valido(cfg):
    """Um gerenciador de `pacotes`: `adicionam` e `congelados` obrigatórios; as flags opcionais, se existirem, são listas."""
    return (isinstance(cfg, dict) and lista_de_textos(cfg.get("adicionam")) and lista_de_textos(cfg.get("congelados"))
            and all(lista_de_textos(cfg[k]) for k in ("flags_congeladas", "so_arquivo") if k in cfg))


def leitura_valida(v):
    """`so_leitura` é opcional; presente, precisa das três listas (sem elas o papel só de leitura cairia em KeyError)."""
    return v is None or (isinstance(v, dict) and all(lista_de_textos(v.get(k)) for k in ("papeis", "comandos", "saidas")))


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
    """Alvos de `>`, `>>` e `tee` na linha (para a autoria dos pareceres escritos pelo Bash)."""
    comando, _ = tirar_heredocs(comando)
    alvos = []
    try:
        for palavras, destinos, _ in comandos(comando):
            alvos += destinos
            palavras = sem_lancadores(palavras)
            if palavras[:1] == ["tee"]:
                alvos += [a for a in palavras[1:] if not a.startswith("-")]
    except ValueError:
        pass
    return alvos


def identificar_sessao(hook):
    """R-CONTRIB: quem é a sessão vem da raiz dela, não da pasta corrente (que passa de uma chamada para a outra).
    - Raiz num projeto do Forge (tem `.forge/versao`; vem antes do Forge, então o manifesto `.claude-plugin/` do
      Forge escrito no projeto não muda nada): as regras dele e as de contribuição valem em qualquer pasta (o
      próprio projeto, o clone, `wt/*`, `~`, outra pasta), no Bash, no Write e no Edit; a raiz fica em
      `hook.raiz`, ou a do projeto onde a pasta está, se houver.
    - Raiz no Forge (clone do próprio Forge, sem `.forge/versao`): regras da sessão do Forge; o hook só age dentro
      de um projeto, pela pasta corrente, como sempre.
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
        if not (com_lista and raiz and e_clone_do_forge(raiz) and hook.campo("hook_event_name") != "PostToolUse"):
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
            if guarda.perguntas:
                pedir_confirmacao(guarda.perguntas)
    else:
        guarda.arquivo(entrada)


if __name__ == "__main__":
    executar("conformidade", principal, CRITICO)
