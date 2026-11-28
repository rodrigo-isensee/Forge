"""Forge: ponto único do git de controle (GIT-CONTROLE-CONFIG-DA-COPIA, anexo E3.1, 3.1). Só biblioteca padrão.

Hooks e ferramentas que eles carregam rodam git fora do sandbox, numa cópia cujo `.git/config`, `.git/hooks` e
`.git/info/attributes` o agente grava. Aqui o git roda sem nada disso executar:
1. ambiente sem `GIT_*` nem `XDG_CONFIG_HOME` e sem pergunta (a config global e a de sistema são do dono);
2. `NEUTRO` na linha de comando, antes do subcomando: vence a config local e as `GIT_CONFIG_*` (a chave por protocolo da
   cópia vence `protocol.allow`, por isso cada protocolo vai por nome);
3. lista positiva de subcomandos: leitura (`LEITURA`, com a opção que a faz leitura se o subcomando também grava),
   flags postas aqui (`FLAGS`) e, para o que toca índice ou árvore (`INDICE`), a config local só com chaves de
   `PERMITIDAS` (o `info/attributes` só executa com um driver dela). Fora da lista: `Recusado`;
4. `merge_tree` e `rede` num repositório neutro em `PASTA_NEUTRA`, que o sandbox não grava.
Resíduo (anexo, seção 4): a janela entre a leitura da config e o git; submódulo com config própria.
"""
import contextlib
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

PRAZO_S = 10
PASTA_NEUTRA = Path.home() / ".forge" / "maquina" / "neutro"
PROTOCOLOS = ("ext", "file", "ssh", "git", "http", "https")
NEUTRO = ("--no-optional-locks", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false",
          "-c", "protocol.allow=never", *(item for p in PROTOCOLOS for item in ("-c", f"protocol.{p}.allow=never")),
          "-c", "diff.external=", "-c", "core.sshCommand=", "-c", "core.gitProxy=", "-c", "core.askPass=",
          "-c", "log.showSignature=false", "-c", "gpg.program=/bin/false", "-c", "gpg.ssh.program=/bin/false",
          "-c", "gpg.x509.program=/bin/false", "-c", "core.attributesFile=/dev/null")
SEM_CREDENCIAL = ("-c", "credential.helper=")
LEITURA = {"rev-parse": None, "rev-list": None, "merge-base": None, "cat-file": None, "for-each-ref": None,
           "ls-tree": None, "symbolic-ref": None, "check-ref-format": None, "show-ref": None, "name-rev": None,
           "grep": None, "config": {"--get", "--get-all", "--get-regexp", "--list", "-l"},
           "remote": {"-v", "get-url"}, "branch": {"--show-current", "-r", "--list", "--contains"},
           "worktree": {"list"}}
SEM_DIFF_EXTERNO = ("--no-ext-diff", "--no-textconv")
FLAGS = {"diff": SEM_DIFF_EXTERNO, "diff-tree": SEM_DIFF_EXTERNO, "show": SEM_DIFF_EXTERNO,
         "log": (*SEM_DIFF_EXTERNO, "--no-show-signature"), "hash-object": ("--no-filters",)}
INDICE = frozenset({"status", "ls-files", "add", "commit", "rm", "mv", "restore", "checkout", "switch", "reset",
                    "diff"})  # o diff da árvore roda o filtro do info/attributes mesmo com --no-textconv (sonda GC1)
REATIVA = frozenset({"--ext-diff", "--textconv", "--show-signature", "--filters", "--path", "--open-files-in-pager"})
PERMITIDAS = re.compile(r"core\.(?:repositoryformatversion|filemode|bare|logallrefupdates|ignorecase|precomposeunicode"
                        r"|symlinks|hookspath)|extensions\.objectformat|remote\.origin\.(?:url|fetch)"
                        r"|remote\.[^.]+\.tagopt|branch\..+\.(?:remote|merge)|user\.(?:name|email)")


class Recusado(Exception):
    """Chamada fora da lista positiva, ou cópia com config que apontaria programa: falha fechada (R-SEGURANCA)."""


def ambiente():
    fora = ("XDG_CONFIG_HOME",)
    return {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k not in fora},
            "GIT_TERMINAL_PROMPT": "0"}


def _rodar(prefixo, args, bruto=False, entrada=None, prazo=PRAZO_S):
    r = subprocess.run(["git", *prefixo, *args], capture_output=True, text=not bruto, env=ambiente(),
                       timeout=prazo, input=entrada, stdin=None if entrada is not None else subprocess.DEVNULL)
    return r.returncode, (r.stdout if bruto else r.stdout.strip())


def _pasta_git(raiz):
    rc, saida = _rodar(("-C", str(raiz), *NEUTRO, *SEM_CREDENCIAL), ("rev-parse", "--git-common-dir"))
    if rc:
        raise Recusado(f"{raiz}: não é repositório git")
    return Path(raiz) / saida


def config_permitida(raiz):
    """A config local (lida sem includes: ler não executa nada) só com chaves de PERMITIDAS."""
    rc, saida = _rodar(NEUTRO, ("config", "--file", str(_pasta_git(raiz) / "config"), "--no-includes", "--list", "-z"),
                       bruto=True)
    chaves = [item.decode("utf-8", "replace").partition("\n")[0] for item in saida.split(b"\0") if item]
    return rc == 0 and all(PERMITIDAS.fullmatch(chave) for chave in chaves)


def montar(raiz, args):
    """O comando depois de `git`, ou `Recusado`. O 1.º argumento é o subcomando: quem chama não põe opção global."""
    sub, resto = (args[0], list(args[1:])) if args else ("", [])
    if any(arg.split("=", 1)[0] in REATIVA or arg.startswith("-O") for arg in resto):
        raise Recusado(f"git {sub}: opção que reabre programa externo")
    if sub in LEITURA:
        if LEITURA[sub] is not None and not LEITURA[sub].intersection(resto):
            raise Recusado(f"git {sub}: só a leitura ({', '.join(sorted(LEITURA[sub]))})")
    elif sub not in FLAGS and sub not in INDICE:
        raise Recusado(f"git {sub or '(vazio)'}: fora da lista positiva do git de controle")
    if sub in INDICE and not config_permitida(raiz):
        raise Recusado(f"git {sub}: a config local de {raiz} tem chave fora da lista positiva")
    return ["-C", str(raiz), *NEUTRO, *SEM_CREDENCIAL, sub, *FLAGS.get(sub, ()), *resto]


def git(raiz, *args, bruto=False, entrada=None, prazo=PRAZO_S):
    """(código, stdout) do git de controle em `raiz`; com `bruto`, bytes sem strip. TimeoutExpired sobe."""
    return _rodar((), montar(raiz, args), bruto=bruto, entrada=entrada, prazo=prazo)


@contextlib.contextmanager
def neutro(objetos_de=None):
    """Repositório nu e vazio em PASTA_NEUTRA (sem config, hooks nem attributes de cópia); com `objetos_de`, lê os
    objetos dessa cópia por alternates. Apagado na saída."""
    PASTA_NEUTRA.mkdir(parents=True, exist_ok=True, mode=0o700)
    pasta = tempfile.mkdtemp(prefix="git-", dir=PASTA_NEUTRA)
    try:
        rc, _ = _rodar((*NEUTRO, *SEM_CREDENCIAL), ("init", "-q", "--bare", "--template=", pasta))
        if rc:
            raise Recusado("git init do repositório neutro falhou")
        if objetos_de is not None:
            alternates = Path(pasta) / "objects" / "info" / "alternates"
            alternates.parent.mkdir(parents=True, exist_ok=True)
            alternates.write_text(f"{(_pasta_git(objetos_de) / 'objects').resolve()}\n", encoding="utf-8")
        yield pasta
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


def merge_tree(raiz, *args, prazo=PRAZO_S):
    """`git merge-tree <args>` no neutro: as revisões resolvidas na cópia (leitura), o merge sem a config, o
    info/attributes e os hooks dela; os objetos escritos ficam no neutro."""
    resolvidos = []
    for arg in args:
        if not arg.startswith("-"):
            rc, arg = git(raiz, "rev-parse", "--verify", "--quiet", f"{arg}^{{commit}}")
            if rc:
                return 128, ""  # como o git: erro, não o rc 1 do conflito
        resolvidos.append(arg)
    with neutro(objetos_de=raiz) as pasta:
        return _rodar((f"--git-dir={pasta}", *NEUTRO, *SEM_CREDENCIAL), ("merge-tree", *resolvidos), prazo=prazo)


def rede(url, sub, *opcoes, refs=(), prazo=PRAZO_S):
    """`ls-remote` ou `fetch` só por https, num neutro descartável: a URL vem de fonte protegida (nunca da cópia), e
    nenhum `insteadOf`, `uploadpack` nem `credential.helper` da cópia é lido. A credencial global (do dono) vale."""
    if sub not in ("ls-remote", "fetch"):
        raise Recusado(f"git {sub}: a rede só faz ls-remote e fetch")
    if not url.startswith("https://"):
        raise Recusado(f"{url}: a rede do git de controle só vai por https")
    with neutro() as pasta:
        return _rodar((f"--git-dir={pasta}", *NEUTRO, "-c", "protocol.https.allow=always"),
                      (sub, *opcoes, "--", url, *refs), prazo=prazo)
