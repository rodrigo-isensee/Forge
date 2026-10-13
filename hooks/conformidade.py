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
import time
from pathlib import Path

import parecer
from _comum import (INTEGRACAO, PLUGIN, bloquear, comandos, executar, git, nome_da_branch, raiz_do_projeto,
                    sem_atribuicoes)

FERRAMENTAS_DE_ARQUIVO = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
CRITICO = re.compile(
    r"\b(git|gh)\b[^\n]*\b(merge|push|edit|close|reopen|ready|review|label)\b|\bpr\b.*\bcreate\b|--no-verify|hookspath|--force|"
    r"\.claude/|\.githooks|\.forge/|docs/reviews|docs/qa|CLAUDE\.md|\.git/(config|hooks)|docs/regras|tests/config\.json|catraca|tests/hooks|conformidade\.json",
    re.I)
# Prefixo -> opções dele que levam valor (as demais são booleanas).
LANCADORES = {"sudo": {"-u", "-g", "-C", "-D", "-p", "-r", "-t", "-U", "-h", "-R", "-T", "--user", "--group"},
              "env": {"-u", "-C", "-S", "--unset", "--chdir", "--split-string"}, "command": set(),
              "nohup": set(), "time": {"-o", "-f", "--output", "--format"}, "exec": {"-a"}, "builtin": set(),
              "nice": {"-n", "--adjustment"}, "setsid": set(), "stdbuf": {"-i", "-o", "-e"},
              "timeout": {"-k", "-s", "--kill-after", "--signal"},
              "xargs": {"-n", "-I", "-L", "-P", "-d", "-E", "-s", "-a", "--max-args", "--max-procs",
                        "--delimiter", "--arg-file", "--max-lines", "--max-chars"}}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
INTERPRETES = re.compile(r"^(python[\d.]*|node(js)?|perl|ruby|php|deno|bun)$")
ESCRITA_NO_TEXTO = re.compile(  # só escrita de arquivo: `.replace(` de texto e `list.append(` não contam
    r"\.write\w*\(|writeFile|appendFile|unlink|\bos\.(remove|rename|replace)|shutil\.|rmtree|truncate|symlink|"
    r"rmSync|rmdir|copyFile|renameSync|cpSync|chmod|WriteStream|\bopen\w*\([^)]*[\"'][wa][bt+]?[\"']|>", re.I)
TODOS_OS_ARGUMENTOS = {"rm", "mv", "tee", "truncate", "shred", "unlink", "rmdir"}
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
                "-A", "--author-email", "--match-head-commit", "-c", "--comment", "--reason"}
CONTRIB_API = re.compile(r"(^|/)pulls/[^/]+|/issues/[^/]+/labels|/issues/[^/]+$|/labels(/|$)")
CONTRIB_GRAPHQL = re.compile(r"closePullRequest|reopenPullRequest|updatePullRequest|addLabelsToLabelable|"
                             r"removeLabelsFromLabelable|createLabel|updateLabel|deleteLabel|updateIssue|closeIssue|"
                             r"markPullRequestReadyForReview|convertPullRequestToDraft", re.I)
PROFUNDIDADE = 3
CONFIG_PROTEGIDA = re.compile(r"^(user\.|core\.|commit\.gpgsign$|include|alias\.)", re.I)
CONFIG_LEITURA = {"--get", "--get-all", "--get-regexp", "--get-urlmatch", "--list", "-l", "--show-origin", "--show-scope",
                  "--show-names", "--name-only", "--help", "-h"}
CONFIG_ESCRITA = {"--unset", "--unset-all", "--add", "--replace-all", "--rename-section", "--remove-section", "-e",
                  "--edit"}
CONFIG_COM_VALOR = {"-f", "--file", "--blob", "--type", "--default"}

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


def separar_lancadores(palavras):
    """Tira os prefixos que só repassam o comando (`env`, `sudo`, `nice`, `timeout`, `xargs`...) com as opções
    deles, para classificar o comando de verdade; opções do comando seguinte não se perdem. Devolve (comando,
    atribuições feitas pelos lançadores): `env GH_REPO=x gh ...` passa a variável ao `gh` como `GH_REPO=x gh ...`."""
    palavras, lancadas = sem_atribuicoes(palavras), []
    while palavras and Path(palavras[0]).name in LANCADORES:
        nome, com_valor = Path(palavras[0]).name, LANCADORES[Path(palavras[0]).name]
        i = 1
        while i < len(palavras) and palavras[i].startswith("-") and palavras[i] != "-":
            opcao = palavras[i]
            i += 1
            if opcao == "--":
                break
            if opcao in com_valor:
                i += 1
        if nome == "timeout" and i < len(palavras):
            i += 1  # a duração
        resto = sem_atribuicoes(palavras[i:])
        lancadas += palavras[i:len(palavras) - len(resto)]
        palavras = resto
    return palavras, lancadas


def sem_lancadores(palavras):
    return separar_lancadores(palavras)[0]


def exporta(palavras):
    """`export`, `declare -x` e `typeset -x` passam as variáveis aos comandos seguintes."""
    return palavras[:1] == ["export"] or palavras[:1] in (["declare"], ["typeset"]) and any(
        re.fullmatch(r"-[a-zA-Z]*x[a-zA-Z]*", p) for p in palavras[1:])


class Guarda:
    def __init__(self, hook, politica, papel):
        self.h, self.pol, self.papel = hook, politica, papel
        self._ramo = None
        self._forge = None
        self.externo = None  # nome da sessão de outro projeto (prefixo `melhoria/<nome>-`), quando vem da raiz dela
        self.ambiente = {}   # GH_REPO e GIT_DIR definidos antes, na mesma linha de comando

    # Respostas -------------------------------------------------------------------------------
    def pode(self, acao):
        return self.papel in self.pol["acoes"].get(acao, [])

    def barrar(self, rid, o_que, corrigir):
        bloquear(rid, f"{o_que}. Corrigir: {corrigir}")

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
        if self.externo is not None:
            return False
        if self._forge is None:
            self._forge = parecer.e_clone_do_forge(self.h.raiz)
        return self._forge

    def em_contrib(self, pasta):
        """A pasta está no clone de contribuição (`~/.forge-contrib/`), onde o projeto trabalha o Forge."""
        alvo = Path(os.path.realpath(pasta))
        return Path(os.path.realpath(Path.home() / ".forge-contrib")) in (alvo, *alvo.parents)

    @staticmethod
    def caminho(pasta, texto):
        """Destino de `cd`/`-C`/`--git-dir`: expande `~` e variáveis de ambiente, como o shell faria."""
        return pasta / Path(os.path.expandvars(texto)).expanduser()

    def alvo_do_forge(self, pasta, repo=None):
        """R-CONTRIB: o comando da sessão de OUTRO projeto (raiz que não é o Forge) atinge o repositório do Forge:
        `repo` aponta para ele ou, sem `repo`, a pasta é o clone de contribuição."""
        if self.clone_do_forge():
            return False
        return parecer.aponta_para_o_forge(repo) if repo else self.em_contrib(pasta)

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
            elif e.get("so_forge") and not self.clone_do_forge():
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
                return ("R-CONFORMIDADE", f"{e['motivo']}: {c}", "só o usuário altera; proponha o diff (R-DECISAO)")
            return ("R-CONFORMIDADE", f"{e['motivo']}: {c} (papel: {self.papel})",
                    f"peça a {'/'.join(e['quem'])}")
        return None

    def resolver(self, caminho, pasta):
        p = Path(caminho).expanduser()
        return Path(os.path.realpath(p if p.is_absolute() else pasta / p))

    def checar_escrita(self, caminho, pasta):
        achado = self.caminho_barrado(self.resolver(caminho, pasta))
        if achado:
            self.barrar(*achado)

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
        caminho = entrada.get("file_path") or entrada.get("notebook_path")
        if isinstance(caminho, str) and caminho:
            self.checar_escrita(caminho, self.h.cwd())

    # Bash ----------------------------------------------------------------------------------------
    def bash(self, comando, pasta, nivel=0):
        if nivel > PROFUNDIDADE:
            return
        comando, corpos = tirar_heredocs(comando)
        try:
            partes = list(comandos(comando))
        except ValueError:
            return  # aspas desbalanceadas: o próprio shell vai recusar
        ramos = {}
        if nivel == 0:
            self.ambiente = {}
        for palavras, destinos in partes:
            for d in destinos:
                self.checar_escrita(d, pasta)
            pasta = self.segmento(palavras, pasta, ramos, nivel)
        for dono, corpo in corpos:
            if re.search(r"\b(bash|sh|zsh|dash)\b", dono):
                self.bash(corpo, pasta, nivel + 1)
            elif re.search(r"\b(python[\d.]*|node|nodejs|perl|ruby)\b", dono):
                self.checar_texto(corpo)

    def segmento(self, palavras, pasta, ramos, nivel):
        """Analisa um comando simples; devolve a pasta depois dele (acompanha `cd`)."""
        atribuicoes = palavras[: len(palavras) - len(sem_atribuicoes(palavras))]
        palavras, lancadas = separar_lancadores(palavras)
        atribuicoes += lancadas
        for a in atribuicoes:
            if "core.hookspath" in a.lower():
                self.barrar("R-VERIFY", "core.hooksPath por variável de ambiente", "não troque o caminho dos hooks")
        definidas = [p for p in palavras[1:] if not p.startswith("-")] if exporta(palavras) else \
            [] if palavras else atribuicoes
        for a in definidas:
            nome, _, valor = a.partition("=")
            if nome in ("GH_REPO", "GIT_DIR") and valor:
                self.ambiente[nome] = valor  # vale para os comandos seguintes da linha
        for p in palavras:
            if "$(" in p or "`" in p:
                self.bash(p, pasta, nivel + 1)
        if not palavras:
            return pasta
        prog = Path(palavras[0].lstrip("`")).name
        args = palavras[1:]
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
            for i, a in enumerate(args):
                if re.fullmatch(r"-[a-z]*c[a-z]*", a) and i + 1 < len(args):
                    self.bash(args[i + 1], pasta, nivel + 1)
        elif prog == "eval":
            self.bash(" ".join(args), pasta, nivel + 1)
        elif INTERPRETES.match(prog):
            for a in args:
                self.checar_texto(a)
            if prog.startswith("python") and args[:2] == ["-m", "pip"]:
                self.pacote("pip", args[2:])
        elif prog == "git":
            self.git(palavras, parte, pasta, ramos, self.da_atribuicao(atribuicoes, "GIT_DIR"))
        elif prog == "gh":
            self.gh(palavras, parte, pasta, self.da_atribuicao(atribuicoes, "GH_REPO"))
        elif prog in TODOS_OS_ARGUMENTOS or (prog == "sed" and any(
                re.fullmatch(r"-[a-zA-Z]*i[a-zA-Z.]*|--in-place(=.*)?", a) for a in args)) or (
                prog == "perl" and any(re.fullmatch(r"-[a-zA-Z]*i[a-zA-Z.]*", a) for a in args)):
            for a in args:
                if not a.startswith("-"):
                    self.checar_escrita(a, pasta)
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
        if prog in LEITORES:
            for a in args:
                nome = Path(a).name
                if ARQUIVO_ENV.match(nome) and nome.rsplit(".", 1)[-1] not in ENV_DE_EXEMPLO:
                    self.barrar("R-CONFORMIDADE", f"ler {nome} expõe segredos",
                                "peça ao usuário o valor de que precisa (R-DECISAO)")
        return pasta

    def da_atribuicao(self, atribuicoes, nome):
        """Valor de `NOME=` na própria linha do comando ou definido antes (`export`)."""
        return next((a.split("=", 1)[1] for a in atribuicoes if a.startswith(nome + "=")), self.ambiente.get(nome))

    # git ---------------------------------------------------------------------------------------------
    def ramo_em(self, pasta, ramos):
        raiz = raiz_do_projeto(pasta)
        chave = raiz.resolve() if raiz else None
        return ramos[chave] if chave in ramos else git(pasta, "branch", "--show-current")[1]

    def git(self, palavras, parte, pasta, ramos, git_dir=None):
        i, pasta_git = 1, self.caminho(pasta, git_dir) if git_dir else pasta
        while i < len(palavras) and palavras[i].startswith("-"):
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
                self.barrar("R-VERIFY", "git push --force", "nunca force o push; refaça com um commit novo")
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
                self.barrar("R-MAIN", f"push direto para {d}", "abra um PR; a main é do usuário")
            if d in INTEGRACAO:
                self.barrar("R-CONFORMIDADE", f"push direto para {d}", "abra um PR a partir de uma branch de trabalho")
        if self.alvo_do_forge(pasta) or self.alvo_do_forge(pasta, remoto):  # a pasta ou a URL do remoto
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
                self.barrar("R-CONTRIB", "gh api que edita, fecha, mescla ou rotula PR no Forge: a sessão de outro "
                                         "projeto só abre o PR da própria branch", "avise o usuário e espere o Forge integrar")

    def gh(self, palavras, parte, pasta, repo_env=None):
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
            and isinstance(caminhos, list) and all(entrada_valida(e) for e in caminhos))


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


def autoria(hook, guarda, alvos):
    """PostToolUse: grava quem escreveu cada parecer (caminho, hash do texto sem espaços nas pontas, agente, papel,
    hora) em autoria.jsonl; o `forge-check pr` confere (ADR 0009, 6.4)."""
    raiz = Path(os.path.realpath(hook.raiz))
    for alvo in alvos:
        p = guarda.resolver(alvo, hook.cwd())
        if raiz not in p.parents or p.suffix != ".md" or not p.is_file():
            continue
        rel = p.relative_to(raiz).as_posix()
        if rel.startswith(("docs/reviews/", "docs/qa/")):
            registro = {"caminho": rel, "sha256": hashlib.sha256(p.read_text(encoding="utf-8").strip().encode()).hexdigest(),
                        "agente": hook.entrada.get("agent_type") or "", "papel": guarda.papel,
                        "quando": time.strftime("%Y-%m-%dT%H:%M:%S")}
            with hook.trava(), open(hook.run() / "autoria.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def alvos_de_escrita(comando):
    """Alvos de `>`, `>>` e `tee` na linha (para a autoria dos pareceres escritos pelo Bash)."""
    comando, _ = tirar_heredocs(comando)
    alvos = []
    try:
        for palavras, destinos in comandos(comando):
            alvos += destinos
            palavras = sem_lancadores(palavras)
            if palavras[:1] == ["tee"]:
                alvos += [a for a in palavras[1:] if not a.startswith("-")]
    except ValueError:
        pass
    return alvos


def raiz_declarada():
    """`CLAUDE_PROJECT_DIR`: a raiz da sessão, que o Claude Code define no processo do hook (também para os
    subagentes). O Bash roda em outro processo: `export` ou `VAR=...` na linha de comando não a mudam."""
    raiz = os.environ.get("CLAUDE_PROJECT_DIR")
    return Path(raiz) if raiz and Path(raiz).is_absolute() else None


def identificar_sessao(hook):
    """R-CONTRIB: quem é a sessão vem da raiz dela, não da pasta corrente (que passa de uma chamada para a outra).
    - Raiz no Forge (clone do próprio Forge): regras da sessão do Forge; o hook só age dentro de um projeto, pela
      pasta corrente, como sempre.
    - Raiz num projeto do Forge: as regras dele e as de contribuição valem em qualquer pasta (o próprio projeto, o
      clone, `wt/*`, `~`, outra pasta), no Bash, no Write e no Edit; a raiz fica em `hook.raiz`, ou a do projeto
      onde a pasta está, se houver.
    - Sem raiz (ou raiz fora do Forge): pela pasta corrente; em `~/.forge-contrib` falha fechado, como sessão de
      outro projeto de nome igual ao do clone (`wt/*` e a própria pasta: nome vazio).
    Devolve False se o hook não age; None se age pela raiz do repositório; o nome da sessão de outro projeto."""
    cwd, raiz = hook.cwd(), raiz_declarada()
    if raiz and parecer.e_clone_do_forge(raiz):
        return None if hook.projeto(cwd) else False
    if raiz and raiz_do_projeto(raiz):
        if not hook.projeto(raiz):  # o projeto desligou o hook: só a pasta corrente, se for outro projeto
            return None if hook.projeto(cwd) else False
        nome = hook.raiz.name
        if not hook.projeto(cwd):
            hook.projeto(raiz)
        return nome
    if hook.projeto(cwd):
        return None
    contrib, pasta = Path(os.path.realpath(Path.home() / ".forge-contrib")), Path(os.path.realpath(cwd))
    if contrib != pasta and contrib not in pasta.parents:
        return False
    partes = pasta.relative_to(contrib).parts
    clone = partes[:2] if partes and (partes[0] == "wt" or partes[0].endswith("-wt")) else partes[:1]
    hook.raiz = contrib.joinpath(*clone)
    return partes[0].removesuffix("-wt") if partes and partes[0] != "wt" else ""


def principal(hook):
    ferramenta = hook.campo("tool_name")
    entrada = hook.campo("tool_input")
    if not isinstance(entrada, dict) or (ferramenta != "Bash" and ferramenta not in FERRAMENTAS_DE_ARQUIVO):
        return
    externo = identificar_sessao(hook)
    if externo is False:
        return
    pol = politica()
    guarda = Guarda(hook, pol, papel_de(pol, hook.campo("agent_type")))
    guarda.externo = externo
    if hook.campo("hook_event_name") == "PostToolUse":
        if ferramenta == "Bash":
            alvos = alvos_de_escrita(entrada["command"]) if isinstance(entrada.get("command"), str) else []
        else:
            alvos = [entrada.get("file_path") or entrada.get("notebook_path") or ""]
        autoria(hook, guarda, [a for a in alvos if a])
    elif ferramenta == "Bash":
        if isinstance(entrada.get("command"), str):
            guarda.bash(entrada["command"], hook.cwd())
    else:
        guarda.arquivo(entrada)


if __name__ == "__main__":
    executar("conformidade", principal, CRITICO)
