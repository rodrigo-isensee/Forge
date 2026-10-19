"""Forge: base comum dos hooks do plugin (ADR 0003).

Silenciosos (sem saída quando tudo está certo), determinísticos (só estado em disco e git local),
só agem em projeto com `.forge/versao` ou com a marca da sessão (`projeto_marcado`) (o `parecer` também no clone do Forge, `raiz_de_estado`) e liberam em erro
interno (registrado em `.forge/run/erros.log`).
Exceção (ADR 0009, seção 7): `parecer` e `conformidade` falham fechado, de forma seletiva: em erro interno
bloqueiam só se a entrada crua tiver um marcador crítico. Só biblioteca padrão; nada vindo da entrada é executado.
"""
import functools
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import re
import shlex
import sys
import time
import unicodedata
from contextlib import contextmanager
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
LIMITE_MENSAGEM = 200
LIMITE_LOG = 256 * 1024
# Usados só se o modelo do projeto (templates/projeto/.forge/config.json) não puder ser lido.
RESERVA = {"teto_agentes": 3, "pesados": []}  # a lista padrão vem da stack (forge-init)
INTEGRACAO = {"main", "master", "develop", "homolog"}
PONTUACAO = "();<>|&\n"
# Um sinal do shell (fora de aspas) se divide em operadores: abertura de substituição de processo (`<(`, `>(`), parênteses,
# redirecionamento (`>`, `>>`, `2>&`, `&>`, `<<`...) e separadores (`;`, `|`, `&&`, quebra de linha).
OPERADOR = re.compile(r"[<>]\(|[()]|&?(?:[<>](?!\())+[&|]?|[;|&\n]+")
# No lugar de uma substituição, o comando de fora recebe uma palavra opaca; o conteúdo dela é conferido como comando
# próprio. `$(…)` contém `$(`: as regras que já desconfiam de `$(` num caminho (`$X/.forge`) seguem valendo.
OPACO = {"$": "$(…)", "<": "<(…)", ">": ">(…)"}


def copia_de_trabalho(inicio):
    """Raiz da cópia de trabalho (a pasta com `.git`, pasta ou arquivo de worktree) que contém `inicio`, ou None.
    Só consulta o disco: nada de git no caminho comum."""
    inicio = Path(inicio)
    return next((d for d in (inicio, *inicio.parents) if (d / ".git").exists()), None)


def raiz_do_projeto(inicio):
    """Raiz da cópia de trabalho que contém `inicio`, se for projeto do Forge: tem `.forge/versao` ou tem a marca da
    sessão (`projeto_marcado`: o arquivo sumiu, a sessão continua sendo de projeto). Senão None."""
    raiz = copia_de_trabalho(inicio)
    if raiz is None:
        return None
    return raiz if (raiz / ".forge" / "versao").is_file() or projeto_marcado(raiz) else None


def e_projeto(raiz):
    """A raiz (ou a cópia de trabalho que a contém) tem `.forge/versao`: é projeto, e nunca o Forge (R-CONTRIB)."""
    raiz = Path(raiz)
    return (raiz / ".forge" / "versao").is_file() or raiz_do_projeto(raiz) is not None


def tem_manifesto_do_forge(raiz):
    """A raiz tem `.claude-plugin/plugin.json` de nome `forge`. Sozinho não prova nada (o projeto pode escrever o
    arquivo): serve para PROTEGER mais (caminhos `so_forge`, alvo do Forge), nunca para dar poder."""
    try:
        dados = json.loads((Path(raiz) / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        return isinstance(dados, dict) and dados.get("name") == "forge"
    except (OSError, ValueError):
        return False


def e_clone_do_forge(raiz):
    """A raiz é um clone do próprio Forge: tem o manifesto do Forge e não é projeto (sem `.forge/versao`). O projeto
    vem antes do Forge, então escrever o manifesto num projeto não o torna o Forge (R-CONTRIB)."""
    return raiz is not None and not e_projeto(raiz) and tem_manifesto_do_forge(raiz)


def raiz_de_estado(inicio):
    """Raiz em que os hooks agem e guardam o estado (`.forge/run/` da cópia principal, `Hook.run`): a do projeto que
    contém `inicio` ou, fora de projeto, a do clone do Forge que o contém. Vale para a cópia principal do dono
    (`~/Forge`) e para as worktrees de `~/.forge-contrib/wt/`. O manifesto do Forge pode ser escrito em qualquer pasta,
    então quem usa esta raiz só pode ganhar guarda com ela, nunca perder (`tem_manifesto_do_forge`)."""
    raiz = raiz_do_projeto(inicio)
    if raiz is not None:
        return raiz
    copia = copia_de_trabalho(inicio)
    return copia if e_clone_do_forge(copia) else None


def raiz_declarada():
    """`CLAUDE_PROJECT_DIR`: a raiz da sessão, que o Claude Code define no processo do hook (também para os
    subagentes). O Bash roda em outro processo: `export` ou `VAR=...` na linha de comando não a mudam."""
    raiz = os.environ.get("CLAUDE_PROJECT_DIR")
    return Path(raiz) if raiz and Path(raiz).is_absolute() else None


def diretorio_comum(topo):
    """Diretório comum de git de uma cópia de trabalho, lido só do disco (sem git e sem seguir o que o git resolveria).
    Cópia principal: o próprio `.git`, que nunca tem `commondir` (se tem, alguém o escreveu para desviar a busca). Worktree
    vinculada: o `.git` é um arquivo `gitdir: <comum>/worktrees/<n>`; o `gitdir` de volta dessa pasta tem de apontar
    para ele (comparado com o caminho real do topo: a worktree aberta por link simbólico vale) e o `commondir` dela, para
    o `<comum>`; um `.git` forjado ou desviado não vale. Senão, None."""
    marca = Path(topo) / ".git"
    if marca.is_symlink():
        return None
    if marca.is_dir():
        return None if os.path.lexists(marca / "commondir") else Path(os.path.realpath(marca))
    try:
        apontado = marca.read_text(encoding="utf-8").strip()
        pasta = Path(os.path.realpath(Path(topo) / apontado[len("gitdir:"):].strip()))
        volta = (pasta / "gitdir").read_text(encoding="utf-8").strip()
        desvio = (pasta / "commondir").read_text(encoding="utf-8").strip()
    except (OSError, ValueError):
        return None
    if not apontado.startswith("gitdir:") or pasta.parent.name != "worktrees":
        return None
    comum = Path(os.path.realpath(pasta.parent.parent))
    esperado = os.path.join(os.path.realpath(os.path.dirname(volta)), os.path.basename(volta))
    real = str(Path(os.path.realpath(topo)) / ".git")
    return comum if esperado == real and Path(os.path.realpath(pasta / desvio)) == comum else None


def marca_de_projeto(raiz):
    """`<diretório comum>/forge/projeto-<hash da raiz>`: o SessionStart grava aqui que a raiz da sessão é projeto. Uma
    marca por raiz (a chave é o caminho real da cópia de trabalho): a worktree irmã, com ou sem Forge, não apaga nem
    herda a marca de outra. Fica dentro do `.git/` (protegido em `hooks/conformidade.json`) e não na árvore de
    trabalho, onde o próprio git a apagaria. O diretório comum é o lido do disco (`diretorio_comum`), não o que o
    `git rev-parse` aponta: um `commondir` escrito dentro do `.git/` não desvia a busca."""
    pasta = diretorio_comum(raiz)
    if pasta is None:
        return None
    chave = hashlib.sha256(os.path.realpath(raiz).encode("utf-8")).hexdigest()[:16]
    return pasta / "forge" / f"projeto-{chave}"


def marcar_projeto(raiz):
    """SessionStart: raiz com `.forge/versao` grava a marca. Nada a apaga: só o usuário, à mão, ao tirar o Forge do
    projeto (o `startup` também chega por chamada à mão do hook, e `resume`/`compact`/`clear` acontecem no meio de uma
    sessão em que um agente pode ter apagado o arquivo)."""
    marca = marca_de_projeto(raiz)
    if marca is not None and (Path(raiz) / ".forge" / "versao").is_file():
        marca.parent.mkdir(parents=True, exist_ok=True)
        marca.write_text(time.strftime("%Y-%m-%dT%H:%M:%S") + "\n", encoding="utf-8")


def projeto_marcado(raiz):
    """A raiz foi marcada como projeto (`marcar_projeto`). Falha fechado quanto ao git: se existe `.git` (pasta ou
    arquivo de worktree) e ele não se resolve (inclui `commondir` num clone principal ou desviado numa worktree), a
    marca não pode ser consultada e a raiz da sessão vale como marcada."""
    marca = marca_de_projeto(raiz)
    if marca is not None:
        return marca.is_file()
    declarada = raiz_declarada()
    return (Path(raiz) / ".git").exists() and declarada is not None and (
        os.path.realpath(declarada) == os.path.realpath(raiz))


def versao_sumiu(raiz=None):
    """A sessão (`CLAUDE_PROJECT_DIR`) foi marcada como projeto e o `.forge/versao` não existe mais: alguém o apagou
    (`git rm`, `git sparse-checkout`, troca de branch...). Sem ele os hooks se desligariam (ADR 0003, item 3): a
    sessão segue sendo de projeto (`raiz_do_projeto`) e as ações críticas falham fechado. A raiz da sessão que deixou
    de existir (movida ou removida: `mv`, `git worktree move`) também falha fechado: a marca é por caminho."""
    raiz = raiz or raiz_declarada()
    return raiz is not None and (not Path(raiz).exists() or (
        not (raiz / ".forge" / "versao").is_file() and projeto_marcado(raiz)))


def motivo_da_falha(raiz=None):
    """Por que `versao_sumiu` vale, para a mensagem dizer a causa: `raiz` (a pasta da sessão sumiu), `git` (o `.git` não
    se resolve: a marca não se consulta e o `.forge/versao` não está lá) ou `versao` (o arquivo sumiu, com marca)."""
    raiz = raiz or raiz_declarada()
    if raiz is None or not Path(raiz).exists():
        return "raiz"
    return "git" if marca_de_projeto(raiz) is None else "versao"


TEXTO_DA_FALHA = {
    "versao": ("o .forge/versao da sessão sumiu (os hooks do Forge se desligam sem ele). Corrigir: não apague nem mova "
               ".forge/; peça ao usuário que o restaure (o agente não pode: .forge/versao é arquivo em vigor) (R-DECISAO)"),
    "raiz": ("a pasta da sessão (CLAUDE_PROJECT_DIR) sumiu ou foi movida (a marca do projeto é por caminho). Corrigir: "
             "não mova nem apague a raiz da sessão; peça ao usuário que a restaure e abra uma sessão nova (R-DECISAO)"),
    "git": ("o .git da raiz da sessão não se resolve (arquivo de worktree inválido, `commondir` inesperado, ligação "
            "desfeita) e não há .forge/versao: os hooks não conseguem conferir a marca do projeto. Corrigir: não mexa no "
            ".git; peça ao usuário que o repare (R-DECISAO)"),
}


def contrib():
    """`~/.forge-contrib`, onde o projeto trabalha o Forge (clone e worktrees)."""
    return Path(os.path.realpath(Path.home() / ".forge-contrib"))


def em_contrib(pasta):
    alvo = Path(os.path.realpath(pasta))
    return contrib() in (alvo, *alvo.parents)


def sessao_vigiada(hook, clone_do_forge=False):
    """Os hooks que falham fechado agem nesta sessão? A mesma decisão de `identificar_sessao` (conformidade), pela
    raiz da sessão e não pela pasta corrente: raiz em projeto, em qualquer pasta; raiz no Forge, só dentro de um
    projeto; sem raiz, num projeto ou em `~/.forge-contrib`. Se nem isso der para decidir, vigia (falha fechado).
    `clone_do_forge` (hook que age no clone, como o `parecer`): vigia também com a raiz da sessão ou a pasta corrente
    num clone do Forge."""
    try:
        cwd, raiz = hook.cwd(), raiz_declarada()
        if clone_do_forge and (e_clone_do_forge(raiz) or raiz_de_estado(cwd) is not None):
            return True
        if raiz is not None and e_projeto(raiz):
            return True
        if raiz_do_projeto(cwd) is not None:
            return True
        return not e_clone_do_forge(raiz) and em_contrib(cwd)
    except Exception:  # noqa: BLE001 - na dúvida, a ação crítica fica barrada (ADR 0009, seção 7)
        return True


def git(raiz, *args):
    """O git do forge-check (sem GIT_* herdadas, com limite de tempo): uma função só para hooks e validador."""
    return forge_check().git(raiz, *args)


def fichas(comando):
    """As palavras e os sinais da linha, sem executar nada: (texto, é sinal fora de aspas, colada na seguinte).
    Aspas desbalanceadas levantam ValueError (o próprio shell vai recusar o comando)."""
    lex = shlex.shlex(comando, posix=True, punctuation_chars=PONTUACAO)
    lex.whitespace, lex.whitespace_split = " \t\r", True
    # O `shlex` devolve o caractere que encerrou a palavra (sem espaço no meio) em `_pushback_chars`: é por ele que se
    # sabe o que está colado (`$(`, `)/x`), e pela posição na linha, se o sinal estava entre aspas (`")"`).
    def posicao():
        return lex.instream.tell() - len(lex._pushback_chars)

    inicio = posicao()
    while (tok := lex.get_token()) is not None:
        fim = posicao()
        bruto = comando[inicio:fim].rstrip(" \t\r")
        sinal = bool(tok) and set(tok) <= set(PONTUACAO) and bruto.endswith(tok) and (
            len(bruto) == len(tok) or bruto[-len(tok) - 1] in " \t\r\n")
        yield tok, sinal, bool(lex._pushback_chars)
        inicio = fim


def comandos(comando):
    """Divide a linha do shell em comandos simples: (palavras, destinos, substituição) por comando. `destinos` são os
    alvos dos redirecionamentos de saída (`>`, `>>`, `&>`, `>|`, `2>`); `>&1` e `>&-` não são arquivos.

    `$(...)`, `<(...)` e `>(...)` não separam comandos: uma pilha de aninhamento guarda o comando de fora, que recebe a
    palavra opaca (`OPACO`, colada ao que estiver colado: `$(…)/x`) e segue juntando palavras depois do `)`. O conteúdo
    sai antes, como comando próprio, com `substituição` = a tupla que a identifica (`()` é a linha; `(1,)`, a primeira
    substituição; `(1, 2)`, uma dentro dela): roda num subshell, então `cd` lá dentro não vale para a linha. O `(` de
    subshell e o `)` que o fecha continuam separando. Aspas desbalanceadas levantam ValueError."""
    pilha, contador = [], [0]  # pilha: ("(", None) para subshell; (tipo, estado de fora) para substituição
    estado = {"palavras": [], "destinos": [], "modo": None, "palavra": None, "colar": False, "sub": ()}

    def entregar():
        palavra, estado["palavra"], estado["colar"] = estado["palavra"], None, False
        if palavra is None:
            return
        if estado["modo"]:
            if estado["modo"] == "saida" and not re.fullmatch(r"\d+|-", palavra):
                estado["destinos"].append(palavra)
            estado["modo"] = None
        else:
            estado["palavras"].append(palavra)

    def separar():
        entregar()
        feito = (estado["palavras"], estado["destinos"], estado["sub"])
        estado.update(palavras=[], destinos=[], modo=None)
        return feito

    def abrir(tipo, prefixo):
        contador[0] += 1
        pilha.append((tipo, dict(estado, palavra=prefixo)))
        estado.update(palavras=[], destinos=[], modo=None, palavra=None, colar=False, sub=estado["sub"] + (contador[0],))

    def fechar():
        feito = separar()
        tipo, fora = pilha.pop()
        estado.clear()
        estado.update(fora, palavra=(fora["palavra"] or "") + OPACO[tipo])
        return feito

    for tok, sinal, colada in fichas(comando):
        if not sinal:
            if estado["palavra"] is not None and estado["colar"]:
                estado["palavra"] += tok
            else:
                entregar()
                estado["palavra"] = tok
            estado["colar"] = colada
            continue
        ops = OPERADOR.findall(tok)
        for i, op in enumerate(ops):
            colado = estado["colar"] and i == 0 and estado["palavra"] is not None
            if op == "(" and colado and estado["palavra"].endswith("$"):
                abrir("$", estado["palavra"][:-1])
            elif op in ("<(", ">("):
                prefixo = estado["palavra"] if colado else None
                if not colado:
                    entregar()
                abrir(op[0], prefixo)
            elif op == "(":
                yield separar()
                pilha.append(("(", None))
            elif op == ")" and pilha and pilha[-1][0] != "(":
                yield fechar()
                estado["colar"] = colada and i == len(ops) - 1
                continue
            elif op == ")":
                yield separar()
                if pilha:
                    pilha.pop()
            elif set(op) & set("<>"):
                entregar()
                estado["modo"] = "saida" if ">" in op else "entrada"
            else:
                yield separar()
            estado["colar"] = False
    while pilha:  # substituição sem o `)`: o shell recusa, mas o de dentro é conferido do mesmo jeito
        if pilha[-1][0] == "(":
            pilha.pop()
        else:
            yield fechar()
    yield separar()


# ADR 0011, item 1: fora de aspas, o papel só de leitura usa só este alfabeto (letras e dígitos, inclusive acentuados),
# o espaço e o tab literais e os operadores `&&`, `||`, `;` e `|`. Entre aspas duplas, tudo menos `DUPLAS_RECUSA`.
ALFABETO_LEITURA = frozenset(" \t_./:=@,+%-~^")
DUPLAS_RECUSA = frozenset("$`\\!")


def controle(c):
    """Caractere de controle ou invisível (quebra de linha, `\\r`, largura zero...); o tab não conta."""
    return c != "\t" and unicodedata.category(c)[0] == "C"


def nome_do_sinal(c):
    return "quebra de linha" if c == "\n" else f"U+{ord(c):04X}" if controle(c) else c


def fora_da_gramatica_de_leitura(linha):
    """ADR 0011, item 1: o primeiro sinal da linha fora da gramática do papel só de leitura, ou None. As aspas são lidas
    em sequência, num estado só: o que está entre aspas simples vale como está (menos controle); entre duplas, o bash
    ainda interpreta `$`, crase, `\\` e `!`. Aspas sem fechar recusam."""
    i, n = 0, len(linha)
    while i < n:
        c = linha[i]
        if c in "'\"":
            fim = linha.find(c, i + 1)
            if fim < 0:
                return f"{c} sem fechar"
            proibidos = DUPLAS_RECUSA if c == '"' else ()
            ruim = next((x for x in linha[i + 1:fim] if x in proibidos or controle(x)), None)
            if ruim is not None:
                return nome_do_sinal(ruim)
            i = fim + 1
        elif linha.startswith(("&&", "||"), i):
            i += 2
        elif c in ";|" or c in ALFABETO_LEITURA or c.isalnum():
            i += 1
        else:
            return nome_do_sinal(c)
    return None


# ADR 0011, item 2: `case` como palavra de comando, no que sobra fora de aspas.
CASE = re.compile(r"(?:^|[\s;&|()])case(?=\s|$)")
INICIO_DE_PALAVRA = " \t\n;&|()"
# O único heredoc que o analisador modela: delimitador entre aspas (corpo literal, sem expansão), sem `-`, terminado na
# palavra. É a forma que `tirar_heredocs` (conformidade) separa igual ao bash; qualquer outro `<<` é não modelado.
HEREDOC_MODELADO = re.compile(r"<<[ \t]*(['\"])([A-Za-z_][A-Za-z0-9_]*)\1(?=[\s;&|)]|$)")


def corpos_de_heredoc(linha, inicio, delimitadores):
    """Pula os corpos dos heredocs pendentes a partir de `inicio` (o começo da linha seguinte ao operador). Devolve o
    índice depois do último delimitador, ou None se um corpo não termina numa linha igual ao delimitador ou tem uma
    linha que só é igual com espaços em volta (o `tirar_heredocs` a tomaria por fim, o bash não)."""
    j = inicio
    for delimitador in delimitadores:
        while True:
            if j > len(linha):
                return None
            k = linha.find("\n", j)
            atual = linha[j:] if k < 0 else linha[j:k]
            j = len(linha) + 1 if k < 0 else k + 1
            if atual == delimitador:
                break
            if atual.strip() == delimitador:
                return None
    return min(j, len(linha))


def construcao_nao_modelada(linha):
    """ADR 0011, item 2: a primeira construção da lista fechada que o analisador não modela, ou None. Fora de aspas
    simples: `#` com outra linha depois (em qualquer posição da palavra), crase, `$` que não abra `$(` (`$'`, `$"`,
    `${`, `$X`, `$@`, `$1`...), `\\` seguido de quebra de linha; fora de aspas, chaves e `case`; e todo `<<` que não
    seja heredoc de `HEREDOC_MODELADO` (inclusive `<<` entre aspas ou escapado numa linha com várias linhas). As aspas
    são lidas em sequência, e `$(` abre um contexto novo de aspas, como no bash; `\\` escapa o caractere seguinte fora
    de aspas e, entre duplas, `$`, crase, `"` e `\\`."""
    pilha = [["fora", 0]]  # contexto: fora | subst (com a profundidade de parênteses) | simples | duplas
    esqueleto, pendentes, modelados, i, n = [], [], set(), 0, len(linha)
    while i < n:
        c, seguinte = linha[i], linha[i + 1:i + 2]
        contexto = pilha[-1]
        if contexto[0] == "simples":
            if c == "'":
                pilha.pop()
            elif c == "\n" and pendentes:
                return "heredoc"
            i += 1
            continue
        if c == "\\":
            if seguinte == "\n":
                return "\\ + quebra de linha"
            if contexto[0] != "duplas" or seguinte in ('$', '`', '"', '\\'):
                i += 1  # o caractere seguinte é literal
        elif c == "`":
            return "crase"
        elif c == "$":
            if seguinte != "(":
                nome = re.match(r"\w+", linha[i + 1:])  # o nome inteiro da variável, não só a primeira letra
                return "$" + (nome.group() if nome else seguinte) if seguinte and not seguinte.isspace() else "$"
            pilha.append(["subst", 0])
            i += 1
        elif contexto[0] == "duplas":
            if c == '"':
                pilha.pop()
            elif c == "\n" and pendentes:
                return "heredoc"
        elif c == "'":
            pilha.append(["simples", 0])
            esqueleto.append("_")
        elif c == '"':
            pilha.append(["duplas", 0])
            esqueleto.append("_")
        elif c == "#":
            if re.search(r"\n[ \t]*\S", linha[i:]):
                return "# + outra linha"
            if i == 0 or linha[i - 1] in INICIO_DE_PALAVRA:
                break  # comentário até o fim da linha
            esqueleto.append(c)
        elif c in "{}":
            return "chaves"
        elif linha.startswith("<<", i):
            m = HEREDOC_MODELADO.match(linha, i)
            if m is None:
                return "heredoc"
            pendentes.append(m.group(2))
            modelados.add(i)
            esqueleto.append(" ")
            i = m.end()
            continue
        elif c == "\n" and pendentes:
            fim = corpos_de_heredoc(linha, i + 1, pendentes)
            if fim is None:
                return "heredoc"
            modelados.update(range(i + 1, fim))
            pendentes, i = [], fim
            esqueleto.append("\n")
            continue
        else:
            if contexto[0] == "subst" and c == "(":
                contexto[1] += 1
            elif contexto[0] == "subst" and c == ")":
                if contexto[1]:
                    contexto[1] -= 1
                else:
                    pilha.pop()
            esqueleto.append(c)
        i += 1
    if pendentes:
        return "heredoc"
    # O `tirar_heredocs` acha `<<` em qualquer lugar da linha física (entre aspas, depois de `\\`): com várias linhas,
    # todo `<<` fora dos heredocs modelados e dos corpos deles é não modelado.
    if "\n" in linha and any(m.start() not in modelados for m in re.finditer("<<", linha)):
        return "heredoc"
    return "case" if CASE.search("".join(esqueleto)) else None


def segmentos(comando):
    """Os comandos simples da linha (listas de palavras), sem os alvos de redirecionamento: os de `comandos`, inclusive
    o conteúdo de cada substituição. Aspas desbalanceadas levantam ValueError."""
    for palavras, _, _ in comandos(comando):
        yield palavras


def sem_atribuicoes(palavras):
    """Tira as atribuições de variáveis do início de um comando simples (`A=1 B=2 git ...`)."""
    i = 0
    while i < len(palavras) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", palavras[i]):
        i += 1
    return palavras[i:]


@functools.lru_cache(maxsize=1)
def forge_check():
    """Carrega bin/forge-check como módulo, para reaproveitar a validação (ADR 0004) sem duplicá-la."""
    caminho = str(PLUGIN / "bin" / "forge-check")
    carregador = importlib.machinery.SourceFileLoader("forge_check", caminho)
    spec = importlib.util.spec_from_loader("forge_check", carregador)
    modulo = importlib.util.module_from_spec(spec)
    carregador.exec_module(modulo)
    return modulo


@functools.lru_cache(maxsize=1)
def forge_doutor():
    """Carrega bin/forge-doutor como módulo: o hook `doutor` roda as mesmas conferências do comando, sem duplicá-las."""
    carregador = importlib.machinery.SourceFileLoader("forge_doutor", str(PLUGIN / "bin" / "forge-doutor"))
    spec = importlib.util.spec_from_loader("forge_doutor", carregador)
    modulo = importlib.util.module_from_spec(spec)
    carregador.exec_module(modulo)
    return modulo


def ler_json(caminho, padrao):
    if not caminho.exists():
        return padrao
    return json.loads(caminho.read_text(encoding="utf-8"))


def gravar_json(caminho, dados):
    tmp = caminho.with_name(caminho.name + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, caminho)


def mensagem(rid, texto):
    """Uma linha com o ID da regra, até LIMITE_MENSAGEM caracteres."""
    linha = " ".join(f"{rid}: {texto}".split())
    return linha if len(linha) <= LIMITE_MENSAGEM else linha[: LIMITE_MENSAGEM - 1] + "…"


def bloquear(rid, texto):
    """Saída 2: o Claude Code bloqueia a ferramenta (PreToolUse) ou mostra o motivo (PostToolUse)."""
    print(mensagem(rid, texto), file=sys.stderr)
    sys.exit(2)


def separar_regra(violacao, padrao):
    """'arquivo: campo: problema (R-X)' -> ('R-X', 'arquivo: campo: problema')."""
    m = re.search(r"\s*\((R-[A-Z][A-Z0-9-]*|ADR-\d+)\)$", violacao)
    return (m.group(1), violacao[: m.start()]) if m else (padrao, violacao)


def nome_da_branch(ref):
    """'origin/feature/x' ou 'refs/heads/feature/x' -> 'feature/x'."""
    for prefixo in ("refs/heads/", "refs/remotes/", "origin/", "upstream/"):
        if ref.startswith(prefixo):
            ref = ref[len(prefixo):]
            if prefixo == "refs/remotes/" and "/" in ref:
                ref = ref.split("/", 1)[1]
    return ref


class Aviso(Exception):
    """Linha informativa no erros.log (uso de escape do dono), não falha."""


class Hook:
    def __init__(self, nome):
        self.nome = nome
        self.entrada = {}
        self.raiz = None
        self._config = None
        self._run = None

    # Entrada -------------------------------------------------------------------------------
    def campo(self, *chaves):
        valor = self.entrada
        for c in chaves:
            valor = valor.get(c) if isinstance(valor, dict) else None
        return valor

    def cwd(self):
        cwd = self.entrada.get("cwd")
        return Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd()

    # Projeto e configuração ------------------------------------------------------------------
    def projeto(self, inicio, clone_do_forge=False):
        """Raiz do projeto do Forge que contém `inicio`, ou None (projeto alheio ou hook desligado na config).
        `clone_do_forge`: fora de projeto, também a raiz do clone do Forge (`raiz_de_estado`). Lá a guarda não se
        desliga: `.forge/` do clone fica fora do git e nenhum hook a protege."""
        self.raiz, self._config, self._run = raiz_do_projeto(inicio), None, None
        if self.raiz is None and clone_do_forge:
            self.raiz = raiz_de_estado(inicio)
            return self.raiz
        if self.raiz is None or self.nome in self.config()["hooks_desligados"]:
            return None
        return self.raiz

    def config(self):
        """Limites do projeto (`.forge/config.json`); o que faltar vem do modelo do Forge."""
        if self._config is not None:
            return self._config
        try:
            base = json.loads((PLUGIN / "templates/projeto/.forge/config.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            base = RESERVA
        projeto = ler_json(self.raiz / ".forge" / "config.json", {})
        if not isinstance(projeto, dict):
            raise ValueError(".forge/config.json não é um objeto JSON")

        def valor(chave, valido, padrao):
            for fonte in (projeto, base):
                if chave in fonte and valido(fonte[chave]):
                    return fonte[chave]
            return padrao

        def inteiro(v):
            return isinstance(v, int) and not isinstance(v, bool) and v >= 1

        def numero(v):
            return isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0

        def lista(v):
            return isinstance(v, list) and all(isinstance(x, str) and x.strip() for x in v)

        self._config = {
            "teto_agentes": valor("teto_agentes", inteiro, None),  # None: teto adaptativo (R-TETO)
            "teto_maximo": valor("teto_maximo", inteiro, None),
            "pesados": valor("pesados", lista, RESERVA["pesados"]),
            "expiracao_horas": valor("expiracao_horas", numero, 2),
            "hooks_desligados": valor("hooks_desligados", lista, []),
        }
        return self._config

    def expira_s(self):
        return self.config()["expiracao_horas"] * 3600

    # Estado em .forge/run/ da cópia principal ------------------------------------------------
    def run(self):
        """`.forge/run/` da cópia de trabalho principal (as worktrees somam no mesmo estado)."""
        if self._run is None:
            run = self.copia_principal() / ".forge" / "run"
            run.mkdir(parents=True, exist_ok=True)
            ignorar = run / ".gitignore"
            if not ignorar.exists():
                ignorar.write_text("*\n", encoding="utf-8")
            self._run = run
        return self._run

    def copia_principal(self):
        """Raiz da cópia de trabalho principal: as worktrees dividem o estado e o perfil dela."""
        cod, comum = git(self.raiz, "rev-parse", "--git-common-dir")
        if not cod and comum:
            comum = (self.raiz / comum).resolve()
            if comum.name == ".git":
                return comum.parent
        return self.raiz

    def iniciante(self):
        """`.forge/perfil` diz `iniciante` (da cópia de trabalho ou da principal). Ausente, ilegível ou outro valor:
        experiente, e o hook segue o fluxo de sempre. Só consulta o disco."""
        for base in dict.fromkeys((self.raiz, self.copia_principal())):
            try:
                return (base / ".forge" / "perfil").read_text(encoding="utf-8").strip().lower() == "iniciante"
            except (OSError, ValueError):
                continue
        return False

    @contextmanager
    def trava(self):
        """Exclusão mútua entre hooks simultâneos (sessões e worktrees) ao ler e gravar o estado."""
        with open(self.run() / ".trava", "a", encoding="utf-8") as f:
            try:
                import fcntl
                fcntl.flock(f, fcntl.LOCK_EX)
            except ImportError:  # sem fcntl (Windows nativo): segue sem trava
                pass
            yield

    def registrar_erro(self, erro):
        """Falha interna não bloqueia (ADR 0003, item 4): registra numa linha e libera."""
        try:
            raiz = self.raiz or raiz_do_projeto(self.cwd())
            if raiz is None:
                return
            self.raiz = raiz
            try:
                pasta = self._run or self.run()
            except Exception:  # noqa: BLE001 - sem git: grava ao lado do projeto
                pasta = raiz / ".forge" / "run"
                pasta.mkdir(parents=True, exist_ok=True)
            log = pasta / "erros.log"
            if log.exists() and log.stat().st_size > LIMITE_LOG:
                os.replace(log, pasta / "erros.log.1")
            linha = " ".join(f"{type(erro).__name__}: {erro}".split())[:300]
            with open(log, "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {self.nome} {linha}\n")
        except Exception:  # noqa: BLE001 - registrar o erro nunca pode bloquear a ferramenta
            pass

    def registrar_escape(self, texto):
        """Uso de um escape do dono (ex.: FORGE_CARGA_LIVRE=1) deixa uma linha no erros.log; nunca bloqueia."""
        self.registrar_erro(Aviso(texto))


def texto_da_acao(hook, bruto):
    """O que a ação tem de crítico: o comando do Bash e o caminho do arquivo, nunca o conteúdo gravado (`content`,
    `new_string`...). Se o JSON não abriu, só resta a entrada crua."""
    entrada = hook.campo("tool_input")
    if not hook.entrada:
        return bruto
    if not isinstance(entrada, dict):
        return ""
    return "\n".join(v for k in ("command", "file_path", "notebook_path") if isinstance(v := entrada.get(k), str))


def falhar_fechado(hook, critico, bruto, clone_do_forge=False):
    """ADR 0009, seção 7: em erro interno, bloqueia só se o comando ou o caminho da ação tem marcador crítico e a
    sessão é vigiada (`sessao_vigiada`: pela raiz da sessão, não pela pasta corrente), e nunca depois da
    ferramenta, quando já não há o que impedir."""
    if (critico is None or hook.entrada.get("hook_event_name") == "PostToolUse"
            or not critico.search(texto_da_acao(hook, bruto)) or not sessao_vigiada(hook, clone_do_forge)):
        return
    bloquear("R-CONFORMIDADE", f"erro interno do hook {hook.nome} diante de uma ação crítica; ele não pôde "
                               "decidir. Corrigir: veja .forge/run/erros.log e leve ao usuário (R-DECISAO)")


def desligado_na_config(hook):
    """O `.forge/config.json` da raiz da sessão (arquivo em vigor, ainda lá) desliga este hook (`hooks_desligados`)."""
    config = ler_json(raiz_declarada() / ".forge" / "config.json", {})
    lista = config.get("hooks_desligados") if isinstance(config, dict) else None
    return isinstance(lista, list) and hook.nome in lista


def barrar_sem_versao(hook, critico, bruto):
    """Ação crítica numa sessão que era de projeto e perdeu o `.forge/versao`: bloqueia (R-CONFORMIDADE), em vez de
    deixar os hooks se desligarem junto com o arquivo. Nunca depois da ferramenta; respeita `hooks_desligados`."""
    if (hook.entrada.get("hook_event_name") != "PostToolUse" and critico.search(texto_da_acao(hook, bruto))
            and versao_sumiu() and not desligado_na_config(hook)):
        bloquear("R-CONFORMIDADE", TEXTO_DA_FALHA[motivo_da_falha()])


def executar(nome, funcao, critico=None, clone_do_forge=False):
    """Lê o JSON do stdin, chama `funcao(hook)` e sai com 0; `bloquear` sai com 2. `critico` (regex) liga a falha
    fechada seletiva (`clone_do_forge`: também no clone do Forge); `FORGE_GUARDA_ABERTA=1` no ambiente do processo
    (só o dono) abre a guarda desses hooks."""
    hook = Hook(nome)
    bruto = sys.stdin.read()
    if critico is not None and os.environ.get("FORGE_GUARDA_ABERTA") == "1":
        sys.exit(0)
    try:
        entrada = json.loads(bruto or "{}")
        if isinstance(entrada, dict):
            hook.entrada = entrada
            if critico is not None:
                barrar_sem_versao(hook, critico, bruto)
            funcao(hook)
    except Exception as erro:  # noqa: BLE001 - ADR 0003: erro interno libera e fica no erros.log
        hook.registrar_erro(erro)
        falhar_fechado(hook, critico, bruto, clone_do_forge)
    sys.exit(0)
