#!/usr/bin/env python3
"""Forge: conformidade dos agentes por papel (ADR 0009, seções 2, 3, 6 e 7; R-CONFORMIDADE).

PreToolUse em Bash, Write, Edit, MultiEdit e NotebookEdit: o papel vem do `agent_type` (política em
`conformidade.json`) e decide quem pode merge, push, PR, escrita em caminho protegido, instalação de pacote e as
flags proibidas (`--no-verify`, `--force`, `core.hooksPath`). Write/Edit decidem pelo `file_path` normalizado
(garantido); o Bash é lido como texto (barrado em regra: um script ou ofuscação passa, e o sandbox é a garantia).
PostToolUse registra a autoria dos pareceres em `.forge/run/autoria.jsonl`.
Falha fechado nas ações críticas (seção 7); `FORGE_GUARDA_ABERTA=1` no ambiente do processo abre a guarda.
Só age em projeto com `.forge/versao`.
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
    r"\b(git|gh)\b[^\n]*\b(merge|push)\b|\bpr\b.*\bcreate\b|--no-verify|hookspath|--force|"
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
PROFUNDIDADE = 3
CONFIG_PROTEGIDA = re.compile(r"^(user\.|core\.|commit\.gpgsign$|include|alias\.)", re.I)
CONFIG_LEITURA = {"--get", "--get-all", "--get-regexp", "--get-urlmatch", "--list", "-l", "--show-origin", "--show-scope",
                  "--show-names", "--name-only", "--help", "-h"}
CONFIG_ESCRITA = {"--unset", "--unset-all", "--add", "--replace-all", "--rename-section", "--remove-section", "-e",
                  "--edit"}
CONFIG_COM_VALOR = {"-f", "--file", "--blob", "--type", "--default"}


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


def sem_lancadores(palavras):
    """Tira os prefixos que só repassam o comando (`env`, `sudo`, `nice`, `timeout`, `xargs`...) com as opções
    deles, para classificar o comando de verdade; opções do comando seguinte não se perdem."""
    palavras = sem_atribuicoes(palavras)
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
        palavras = sem_atribuicoes(palavras[i:])
    return palavras


class Guarda:
    def __init__(self, hook, politica, papel):
        self.h, self.pol, self.papel = hook, politica, papel
        self._ramo = None
        self._forge = None

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

    def clone_do_forge(self):
        if self._forge is None:
            self._forge = parecer.e_clone_do_forge(self.h.raiz)
        return self._forge

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
        for a in atribuicoes:
            if "core.hookspath" in a.lower():
                self.barrar("R-VERIFY", "core.hooksPath por variável de ambiente", "não troque o caminho dos hooks")
        palavras = sem_lancadores(palavras)
        for p in palavras:
            if "$(" in p or "`" in p:
                self.bash(p, pasta, nivel + 1)
        if not palavras:
            return pasta
        prog = Path(palavras[0].lstrip("`")).name
        args = palavras[1:]
        parte = parecer.analisar(palavras)
        if parte and parte[0] == "cd":
            return pasta / Path(parte[1]).expanduser() if parte[1] else Path.home()
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
            self.git(palavras, parte, pasta, ramos)
        elif prog == "gh":
            self.gh(palavras, parte, pasta)
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

    # git ---------------------------------------------------------------------------------------------
    def ramo_em(self, pasta, ramos):
        raiz = raiz_do_projeto(pasta)
        chave = raiz.resolve() if raiz else None
        return ramos[chave] if chave in ramos else git(pasta, "branch", "--show-current")[1]

    def git(self, palavras, parte, pasta, ramos):
        i, pasta_git = 1, pasta
        while i < len(palavras) and palavras[i].startswith("-"):
            if palavras[i] == "-C" and i + 1 < len(palavras):
                pasta_git = pasta / palavras[i + 1]
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
        refs = refs[1:]  # o primeiro é o remoto
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

    # gh ----------------------------------------------------------------------------------------------
    def gh(self, palavras, parte, pasta):
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


def politica():
    return json.loads((PLUGIN / "hooks" / "conformidade.json").read_text(encoding="utf-8"))


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


def principal(hook):
    ferramenta = hook.campo("tool_name")
    entrada = hook.campo("tool_input")
    if not isinstance(entrada, dict) or (ferramenta != "Bash" and ferramenta not in FERRAMENTAS_DE_ARQUIVO):
        return
    if not hook.projeto(hook.cwd()):
        return
    pol = politica()
    guarda = Guarda(hook, pol, papel_de(pol, hook.campo("agent_type")))
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
