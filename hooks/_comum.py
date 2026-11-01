"""Forge: base comum dos hooks do plugin (ADR 0003).

Silenciosos (sem saída quando tudo está certo), determinísticos (só estado em disco e git local),
só agem em projeto com `.forge/versao` ou com a marca da sessão (`projeto_marcado`) (o `parecer` também no clone do Forge, `raiz_de_estado`) e liberam em erro
interno (registrado em `.forge/run/erros.log`).
Exceção (ADR 0009, seção 7): `parecer` e `conformidade` falham fechado, de forma seletiva: em erro interno
bloqueiam só se a entrada crua tiver um marcador crítico. Só biblioteca padrão; nada vindo da entrada é executado.
"""
import bisect
import collections
import functools
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import re
import shlex
import signal
import sys
import threading
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
PROFUNDIDADE = 3  # teto de aninhamento das leituras (`bash -c`, `$(`, crase, corpo de heredoc de shell)
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


# ADR 0013: o `#` só abre comentário onde se prova que o bash também o abre. A varredura de `comentarios` anda da
# esquerda para a direita só enquanto a linha está na gramática G, o estado normal em que o bash lê palavras de um
# comando simples ou de uma lista; o primeiro sinal fora de G encerra a varredura, e dali em diante nenhum `#` abre
# comentário (a linha é lida por inteiro). Ficam fora de G, entre outros: crase, `(` e `)`, `$` que não seja de nome ou
# de parâmetro especial (`${`, `$[`, `$'`, `$"`), `=~`, `<<`, `\` no fim ou antes da quebra de linha, aspas sem fechar
# e caracteres de controle. Um contexto do bash que ninguém listou também começa fora de G: a omissão desliga o
# comentário, não o liga.
LITERAIS_DE_G = frozenset("_./:=@,+%-~^*?[]{}!#")
SEPARADORES_DE_G = frozenset(" \t\n;&|")  # depois deles (lidos pela varredura, sem `\`), começa palavra
PARAMETRO = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|[0-9?#@*!$-]")  # depois de `$`: nome ou parâmetro especial


def fim_das_duplas(linha, i):
    """O índice do `"` que fecha as aspas duplas abertas antes de `i`, se o conteúdo estiver em G (caracteres comuns,
    `\\` seguido de um caractere que não é quebra de linha, `$` de nome ou parâmetro especial); senão, None."""
    while i < len(linha):
        c = linha[i]
        if c == '"':
            return i
        if c == "\\":
            if linha[i + 1:i + 2] in ("", "\n"):
                return None
            i += 2
        elif c == "$":
            m = PARAMETRO.match(linha, i + 1)
            if m is None:
                return None
            i = m.end()
        elif c == "`" or (controle(c) and c not in "\n\t"):
            return None
        else:
            i += 1
    return None


def varrer_comentarios(linha):
    """A varredura da gramática G (ADR 0013): (posições dos `#` que abrem comentário, onde a varredura parou). Pára em
    `len(linha)` se a linha inteira está em G. O comentário provado é pulado até a quebra de linha."""
    provados, i, n = set(), 0, len(linha)
    inicio, depois_de_redirecionar = True, False
    while i < n:
        c = linha[i]
        if c == "#" and inicio:
            provados.add(i)
            fim = linha.find("\n", i)
            i = n if fim < 0 else fim
            continue
        if c == "#" and depois_de_redirecionar:  # `>#x`: o bash começa palavra nova depois do operador
            break
        if c in SEPARADORES_DE_G:
            inicio, depois_de_redirecionar = True, False
            i += 1
            continue
        if c == "'":
            fim = linha.find("'", i + 1)
            if fim < 0:
                break
            i = fim + 1
        elif c == '"':
            fim = fim_das_duplas(linha, i + 1)
            if fim is None:
                break
            i = fim + 1
        elif c == "\\":
            if linha[i + 1:i + 2] in ("", "\n"):
                break
            i += 2
        elif c == "$":
            m = PARAMETRO.match(linha, i + 1)
            if m is None:
                break
            i = m.end()
        elif linha.startswith(("=~", "<<"), i):
            break
        elif c in "<>":
            i += 1
            inicio, depois_de_redirecionar = False, True
            continue
        elif c.isalnum() or c in LITERAIS_DE_G:
            i += 1
        else:
            break
        inicio, depois_de_redirecionar = False, False
    return frozenset(provados), i


def comentarios(linha):
    """Posições dos `#` que abrem comentário pela gramática G (o prefixo provado). Fora delas, o `#` é palavra."""
    return varrer_comentarios(linha)[0]


# Antes de um `#`, o que pode fazer dele início de palavra para o bash (fora de G, o hook não sabe se é comentário). A
# crase entra porque o corpo dela é lido à parte: o `#` logo depois da crase que abre começa palavra.
ANTES_DE_CANDIDATO = frozenset(" \t\n;&|<>()`")


def comentario_ambiguo(linha):
    """Depois do ponto em que a varredura de G parou, um `#` que o bash pode ler como comentário e que, lido como
    palavra (como o hook o lê), levaria uma aspa ou uma barra para fora do comentário e esconderia o que o bash roda. A
    linha não se lê com segurança quando o resto da linha física depois do `#`:
    - tem aspa, crase ou `\\` no fim, e há outra linha depois (o comentário acaba na quebra de linha); ou
    - tem crase e aspa, na última linha física: dentro de crase o comentário acaba na crase que fecha, não na quebra de
      linha, e a aspa dele casaria com outra mais adiante (`` x=`#'`; gh repo delete d/p --yes # ' ``)."""
    _, parada = varrer_comentarios(linha)
    for m in re.finditer("#", linha[parada:]):
        i = parada + m.start()
        if i and linha[i - 1] not in ANTES_DE_CANDIDATO:
            continue
        fim = linha.find("\n", i)
        ultima = fim < 0 or not linha[fim:].strip()
        resto = linha[i:len(linha) if fim < 0 else fim].rstrip(" \t\r")
        aspa = any(c in resto for c in "'\"")
        if ultima:
            if "`" in resto and aspa:
                return True
            continue
        if aspa or "`" in resto or resto.endswith("\\"):
            return True
    return False


def conteudos_de_crase(comando, so_os_fechados=False):
    """Os comandos dentro de crase (`` `…` ``), que o shell executa como `$(...)`: fora de aspas simples, inclusive entre
    aspas duplas; a barra invertida escapa; comentário (o `#` que a gramática G prova, `comentarios`, ADR 0013) não
    conta. Crase sem par levanta ValueError (a linha não se analisa); com `so_os_fechados`, ficam só os corpos que
    fecham (o que vem depois da crase sem par o bash não roda: é erro de sintaxe)."""
    saida, inicio, simples, duplas, i = [], None, False, False, 0
    provados = comentarios(comando)
    while i < len(comando):
        c = comando[i]
        if c == "\\" and not simples and i + 1 < len(comando):
            i += 2
            continue
        if i in provados:
            fim = comando.find("\n", i)  # comentário (`# don't`): vai até o fim da linha e não abre aspa
            i = len(comando) if fim < 0 else fim
            continue
        if inicio is not None:
            if c == "`":
                saida.append(comando[inicio:i].replace("\\`", "`"))
                inicio = None
        elif simples:
            simples = c != "'"
        elif c == "'" and not duplas:
            simples = True
        elif c == '"':
            duplas = not duplas
        elif c == "`":
            inicio = i + 1
        i += 1
    if inicio is not None and not so_os_fechados:
        raise ValueError("crase sem par")
    return saida


def fichas(comando, legado=False):
    """As palavras e os sinais da linha, sem executar nada: (texto, é sinal fora de aspas, colada na seguinte).
    Aspas desbalanceadas levantam ValueError.

    O `shlex` toma por comentário um `#` em qualquer ponto da palavra (`a#; git push` esconderia o push) e engole a
    quebra de linha que o encerra: aqui ele não conhece comentário, e o `#` só abre um onde a gramática G prova que o
    bash o abre (`comentarios`, ADR 0013); o comentário vai até a quebra de linha, que continua separando comandos.
    `legado`: a leitura da develop (o `#` do `shlex`), o piso de `leituras`."""
    lex = shlex.shlex(comando, posix=True, punctuation_chars=PONTUACAO)
    lex.whitespace, lex.whitespace_split = " \t\r", True
    if not legado:
        lex.commenters = ""
    provados = frozenset() if legado else comentarios(comando)
    # O `shlex` devolve o caractere que encerrou a palavra (sem espaço no meio) em `_pushback_chars`: é por ele que se
    # sabe o que está colado (`$(`, `)/x`), e pela posição na linha, se o sinal estava entre aspas (`")"`).
    def posicao():
        return lex.instream.tell() - len(lex._pushback_chars)

    def pular_comentario():
        """Entre duas fichas: se a próxima começa num `#` provado, pula até a quebra de linha (ou o fim)."""
        atual = posicao()
        proximo = len(comando) - len(comando[atual:].lstrip(" \t\r"))
        if proximo not in provados:
            return atual
        fim = comando.find("\n", proximo)
        fim = len(comando) if fim < 0 else fim
        lex._pushback_chars.clear()
        lex.instream.seek(fim)
        return fim

    inicio = pular_comentario()
    while (tok := lex.get_token()) is not None:
        fim = posicao()
        bruto = comando[inicio:fim].rstrip(" \t\r")
        sinal = bool(tok) and set(tok) <= set(PONTUACAO) and bruto.endswith(tok) and (
            len(bruto) == len(tok) or bruto[-len(tok) - 1] in " \t\r\n")
        yield tok, sinal, bool(lex._pushback_chars)
        inicio = pular_comentario()


def comandos(comando, legado=False, com_sinal=False):
    """Divide a linha do shell em comandos simples: (palavras, destinos, substituição) por comando. `destinos` são os
    alvos dos redirecionamentos de saída (`>`, `>>`, `&>`, `>|`, `2>`); `>&1` e `>&-` não são arquivos.

    `$(...)`, `<(...)` e `>(...)` não separam comandos: uma pilha de aninhamento guarda o comando de fora, que recebe a
    palavra opaca (`OPACO`, colada ao que estiver colado: `$(…)/x`) e segue juntando palavras depois do `)`. O conteúdo
    sai antes, como comando próprio, com `substituição` = a tupla que a identifica (`()` é a linha; `(1,)`, a primeira
    substituição; `(1, 2)`, uma dentro dela): roda num subshell, então `cd` lá dentro não vale para a linha. O `(` de
    subshell e o `)` que o fecha continuam separando. Aspas desbalanceadas levantam ValueError. `com_sinal`: cada
    comando traz, em quarto, o sinal que o encerrou (`|`, `&&`, `;`, `|\n`..., `(` e `)` do subshell, `$)` do fim de uma
    substituição, `""` no fim da linha)."""
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

    def separar(sinal=""):
        entregar()
        feito = (estado["palavras"], estado["destinos"], estado["sub"]) + ((sinal,) if com_sinal else ())
        estado.update(palavras=[], destinos=[], modo=None)
        return feito

    def abrir(tipo, prefixo):
        contador[0] += 1
        pilha.append((tipo, dict(estado, palavra=prefixo)))
        estado.update(palavras=[], destinos=[], modo=None, palavra=None, colar=False, sub=estado["sub"] + (contador[0],))

    def fechar():
        feito = separar("$)")
        tipo, fora = pilha.pop()
        estado.clear()
        estado.update(fora, palavra=(fora["palavra"] or "") + OPACO[tipo])
        return feito

    for tok, sinal, colada in fichas(comando, legado):
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
                yield separar(op)
                pilha.append(("(", None))
            elif op == ")" and pilha and pilha[-1][0] != "(":
                yield fechar()
                estado["colar"] = colada and i == len(ops) - 1
                continue
            elif op == ")":
                yield separar(op)
                if pilha:
                    pilha.pop()
            elif set(op) & set("<>"):
                entregar()
                estado["modo"] = "saida" if ">" in op else "entrada"
            else:
                yield separar(op)
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
# O único heredoc que o analisador modela: delimitador entre aspas (corpo literal, sem expansão), sem `-`, terminado na
# palavra. É a forma que `tirar_heredocs` separa igual ao bash; qualquer outro `<<` é não modelado.
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


Heredoc = collections.namedtuple("Heredoc", "operador fim_do_operador delimitador literal corpo fim")
SEM_PALAVRA = frozenset(" \t\n;&|()<>")  # o que encerra a palavra do delimitador fora de aspas


def palavra_do_delimitador(comando, j):
    """A palavra do delimitador que começa em `j`: (delimitador sem aspas nem `\\`, se tinha aspa ou `\\`, fim)."""
    partes, literal, n = [], False, len(comando)
    while j < n and comando[j] not in SEM_PALAVRA:
        c = comando[j]
        if c == "'":
            fim = comando.find("'", j + 1)
            fim = n if fim < 0 else fim
            partes.append(comando[j + 1:fim])
            literal, j = True, fim + 1
        elif c == '"':
            k = j + 1
            while k < n and comando[k] != '"':
                k += 2 if comando[k] == "\\" else 1
            partes.append(re.sub(r"\\(.)", r"\1", comando[j + 1:k], flags=re.S))
            literal, j = True, k + 1
        elif c == "\\":
            partes.append(comando[j + 1:j + 2])
            literal, j = True, j + 2
        else:
            partes.append(c)
            j += 1
    return "".join(partes), literal, min(j, n)


def heredocs(comando):
    """HEREDOC-FURO-HOOK: os heredocs cujo operador a varredura prova, e a posição do primeiro `<<` em dúvida (ou None).
    Um `<<` é operador provado fora de aspas, de escape e de comentário provado (`comentarios`), no nível da linha, num
    subshell ou dentro de `$(` (também `"$(cat <<'EOF'…"`), e não é `<<<`. Entre aspas simples, duplas ou `$'…'`,
    escapado ou em comentário provado, é literal. É dúvida dentro de crase, de `${…}`, de `((…))`, `$((…))` ou `$[…]`,
    depois de um `#` que pode ser comentário e que G não prova (até o fim da linha física), numa linha com `case` e
    `$(` (o `)` do padrão fecharia o `$(`) e com um heredoc pendente numa quebra de linha que não está no nível da
    linha. O estado das aspas atravessa as linhas físicas, e os corpos provados são pulados. O corpo acaba na primeira
    linha igual ao delimitador, como no bash (com `<<-`, sem as tabs do começo; espaço em volta não vale), ou no fim do
    texto. Dentro de `$(`, a linha do corpo que começa pelo delimitador sem ser igual a ele é dúvida: o bash 5.3 fecha
    ali o heredoc em `EOF)`, `EOF )` ou `EOF x)` e roda o resto da linha."""
    provados = comentarios(comando)
    com_case = bool(CASE.search(comando)) and "$(" in comando
    pilha = [["fora", 0]]  # fora | subst | simples | ansi | duplas | crase | chave | aritm | colchete (com a profundidade)
    achados, pendentes, duvida, i, n = [], [], None, 0, len(comando)

    def duvidar(posicao):
        nonlocal duvida
        duvida = posicao if duvida is None else duvida

    while i < n:
        c, contexto = comando[i], pilha[-1]
        tipo = contexto[0]
        if tipo == "simples":
            if c == "'":
                pilha.pop()
            elif c == "\n" and pendentes:
                duvidar(i)
            i += 1
            continue
        if tipo == "crase":
            if c == "\\":
                i += 2
                continue
            if c == "`":
                pilha.pop()
            elif comando.startswith("<<", i) or (c == "\n" and pendentes):
                duvidar(i)
            i += 1
            continue
        if c == "\\":
            i += 2  # o caractere seguinte é literal (`\\<<X`; `\\` + quebra de linha continua a linha)
            continue
        if tipo == "ansi":
            if c == "'":
                pilha.pop()
            i += 1
            continue
        if tipo == "duplas":
            if c == '"':
                pilha.pop()
                i += 1
                continue
            if c == "\n" and pendentes:
                duvidar(i)
            if c not in "$`":
                i += 1
                continue
        # fora, subst, chave, aritm, colchete e os `$`/crase entre aspas duplas
        nivel_da_linha = tipo in ("fora", "subst")
        if c == "`":
            pilha.append(["crase", 0])
            i += 1
        elif comando.startswith("$((", i):
            pilha.append(["aritm", 2])
            i += 3
        elif comando.startswith("$(", i):
            pilha.append(["subst", 0])
            i += 2
        elif comando.startswith("${", i):
            pilha.append(["chave", 1])
            i += 2
        elif comando.startswith("$[", i):
            pilha.append(["colchete", 1])
            i += 2
        elif tipo == "duplas":
            i += 1  # `$` comum entre aspas duplas
        elif comando.startswith("$'", i):
            pilha.append(["ansi", 0])
            i += 2
        elif c == "'":
            pilha.append(["simples", 0])
            i += 1
        elif c == '"':
            pilha.append(["duplas", 0])
            i += 1
        elif c == "#" and nivel_da_linha and (i in provados or i == 0 or comando[i - 1] in ANTES_DE_CANDIDATO):
            fim = comando.find("\n", i)
            fim = n if fim < 0 else fim
            resto = comando[i:fim]
            if i not in provados and ("<<" in resto or any(x in resto for x in "'\"`\\") or "$(" in resto):
                duvidar(i)  # pode ser comentário ou palavra: nenhuma das duas leituras se prova
            i = fim
        elif comando.startswith("<<<", i):
            i += 3
        elif comando.startswith("<<", i):
            if not nivel_da_linha or com_case:
                duvidar(i)
                i += 2
                continue
            j = i + 2 + (comando[i + 2:i + 3] == "-")
            while j < n and comando[j] in " \t":
                j += 1
            delimitador, literal, fim = palavra_do_delimitador(comando, j)
            if not delimitador:
                duvidar(i)
                i = max(fim, i + 2)
                continue
            pendentes.append((i, fim, delimitador, literal, comando[i + 2:i + 3] == "-"))
            i = fim
        elif c == "\n" and pendentes:
            if not nivel_da_linha:
                duvidar(i)
                i += 1
                continue
            j = i + 1
            for operador, fim_do_operador, delimitador, literal, tabs in pendentes:
                corpo = j
                while j < n:
                    k = comando.find("\n", j)
                    k = n if k < 0 else k
                    linha = comando[j:k].lstrip("\t") if tabs else comando[j:k]
                    fisica = j  # o começo da linha física corrente
                    while not literal and k < n and barra_impar_no_fim(comando[fisica:k]):
                        # sem aspas no delimitador, o bash junta `\` + quebra com a linha seguinte (sem tirar as tabs
                        # dela) antes de comparar: `a\`⏎`X` é `aX` e não fecha; `\`⏎`X` é `X` e fecha (A2)
                        proxima = comando.find("\n", k + 1)
                        proxima = n if proxima < 0 else proxima
                        linha, fisica, k = linha[:-1] + comando[k + 1:proxima], k + 1, proxima
                    if linha == delimitador:  # como o bash: igual, e com `<<-` só as tabs do começo saem (R2)
                        achados.append(Heredoc(operador, fim_do_operador, delimitador, literal, (corpo, j), min(k + 1, n)))
                        j = k + 1
                        break
                    if tipo == "subst" and linha.startswith(delimitador):
                        duvidar(j)  # dentro de `$(`, o bash 5.3 fecha em `EOF)`, `EOF )`, `EOF x)` (opção A, item 3)
                    j = k + 1
                else:
                    achados.append(Heredoc(operador, fim_do_operador, delimitador, literal, (corpo, n), n))  # até o fim
                    j = n
            pendentes, i = [], min(j, n)
        else:
            if tipo in ("subst", "aritm") and c == "(":
                contexto[1] += 1
            elif tipo == "subst" and c == ")":
                if contexto[1]:
                    contexto[1] -= 1
                else:
                    pilha.pop()
            elif tipo == "aritm" and c == ")":
                contexto[1] -= 1
                if not contexto[1]:
                    pilha.pop()
            elif tipo == "chave" and c in "{}":
                contexto[1] += 1 if c == "{" else -1
                if not contexto[1]:
                    pilha.pop()
            elif tipo == "colchete" and c in "[]":
                contexto[1] += 1 if c == "[" else -1
                if not contexto[1]:
                    pilha.pop()
            elif tipo == "fora" and comando.startswith("((", i):
                pilha.append(["aritm", 2])
                i += 2
                continue
            i += 1
    return achados, duvida


def barra_impar_no_fim(linha):
    """A linha acaba numa quantidade ímpar de `\\`: a última escapa a quebra de linha (continuação)."""
    return (len(linha) - len(linha.rstrip("\\"))) % 2 == 1


def expandido(corpo):
    """O corpo de um heredoc sem aspas no delimitador como o bash o expande, só no que importa para achar `$(` e crase:
    `\\` + quebra de linha some (junta as linhas: `$\\⏎(` vira `$(`) e `\\` escapa `$`, crase e `\\` (o par vira um
    caractere neutro: `\\$(` é literal, mas `\\\\$(` é uma barra e um `$(` vivo)."""
    saida, i, n = [], 0, len(corpo)
    while i < n:
        c = corpo[i]
        if c == "\\" and corpo[i + 1:i + 2] == "\n":
            i += 2
        elif c == "\\" and corpo[i + 1:i + 2] in ("$", "`", "\\"):
            saida.append("_")
            i += 2
        else:
            saida.append(c)
            i += 1
    return "".join(saida)


def tirar_heredocs(comando, com_gravado=False):
    """Separa o corpo dos heredocs provados (`heredocs`), que não são comandos, da linha: devolve (comando sem os corpos,
    [(dono, corpo)]), com o dono do operador lido na linha sem os corpos (`DonosDosHeredocs`); com `com_gravado`, também
    `gravado_e_rodado` (M3: o programa fora da lista num texto que grava arquivo, ou None). O
    operador e o delimitador saem junto, como um espaço: a palavra que o hook relê depois (`"$(cat <<'X'⏎X⏎L⏎Y)"`) não
    tira de novo, como corpo, a linha que o bash roda. ValueError (quem chama trata como linha ilegível): um `<<` em
    dúvida com uma linha não vazia depois dele (lido como comando, o corpo que não se tira esconderia o resto com uma
    aspa; tirado, esconderia a linha que o bash roda), ou um corpo que o bash expande (delimitador sem aspa nem `\\`)
    com `$(` ou crase (H9)."""
    achados, duvida = heredocs(comando)
    if duvida is not None:
        fim = comando.find("\n", duvida)
        if fim >= 0 and comando[fim:].strip():
            raise ValueError("heredoc em dúvida")
    cortes, corpos = [], []
    for h in achados:
        corpo = comando[h.corpo[0]:h.corpo[1]].rstrip("\n")
        if not h.literal and re.search(r"\$\(|`", expandido(corpo)):
            raise ValueError("corpo de heredoc com substituição")
        corpos.append((h.operador, corpo))
        cortes += [(h.operador, h.fim_do_operador, " "), (h.corpo[0], h.fim, "")]
    saida, marcada, inicio, no_resto, tamanho = [], [], 0, {}, 0
    for ini, fim, troca in sorted(cortes):
        saida.append(comando[inicio:ini])
        marcada.append(comando[inicio:ini])
        tamanho += ini - inicio
        no_resto[ini] = tamanho  # onde o operador fica na linha sem os corpos (a soma, sem reler a saída)
        saida.append(troca)
        tamanho += len(troca)
        marcada.append(f" {marca(ini)} " if troca else "")
        inicio = fim
    saida.append(comando[inicio:])
    marcada.append(comando[inicio:])
    resto, marcada = "".join(saida), "".join(marcada)
    lidas = leituras(marcada, com_sinal=True, sem_marcas=resto) if corpos else None
    donos = DonosDosHeredocs(resto, lidas) if corpos else None  # o que serve a todos, lido uma vez por texto
    lidos = [(donos.dono(no_resto[operador], marca(operador)), corpo) for operador, corpo in corpos]
    return (resto, lidos, donos and donos.gravado_e_rodado) if com_gravado else (resto, lidos)


# Fim de linha física que o bash junta com a linha seguinte num comando só: barra ímpar (continuação), ou um operador
# que pede o comando seguinte (`|`, `|&`, `||`, `&&`) ou um `(` aberto (`eval "$(`⏎`cat <<'EOF'`).
CONTINUA_NA_PROXIMA = re.compile(r"(\|&?|&&|\()[ \t]*$")


def continua_na_proxima(linha):
    return barra_impar_no_fim(linha) or bool(CONTINUA_NA_PROXIMA.search(linha))


# No lugar de cada operador, com o número dele e `__`, na linha sem os corpos (`DonosDosHeredocs`): uma palavra comum,
# que a gramática G lê como as outras (um caractere de controle mudaria a prova do `#` seguinte). A mesma palavra
# escrita na linha só junta mais texto ao dono. Curta (heredoc-rapido, passo 2): a linha marcada é lida inteira, e
# cada caractere da marca pesa nessa leitura (3000 heredocs: 112 para 76 mil caracteres). Fonte única dos usos: `marca`
# escreve, `MARCAS` procura.
MARCA = "__fh"
MARCAS = re.compile(MARCA + r"\d+__")


def marca(operador):
    """A marca do heredoc cujo operador está na posição `operador` do texto."""
    return f"{MARCA}{operador}__"


# Palavras de comando composto: a leitura por pipeline não as modela (o `;` de `{ read; bash; }` não separa quem lê o
# corpo), e uma delas em qualquer palavra da linha, entre aspas ou não, faz o dono ser o comando lógico inteiro.
COMPOSTOS = frozenset({"{", "}", "if", "then", "elif", "else", "fi", "case", "esac", "for", "select", "while", "until",
                       "do", "done", "function", "coproc", "[[", "]]"})
# Os outros comandos do comando lógico (`&&`, `||`, `;`, outra linha) que não rodam o corpo do heredoc, nem o arquivo
# que ele grava (A1 de segurança, volta 4). A lista é positiva, como a dos leitores: qualquer outro programa (`./x.sh`,
# `make`, `bash x.sh`, `$x`, `git -c alias.x='!sh x.sh' x`) pode rodar o que o heredoc gravou, e faz do corpo comando.
# M5 da volta única: `echo` e `true`, builtins sem efeito além da saída; a função ou o alias com esse nome definidos no
# texto aparecem como outro programa (`echo() { ./x.sh; }` põe `./x.sh`, `alias echo=./x.sh` põe `alias`), e a
# redireção de saída deles conta em `grava_arquivo`. O `git log` não entra (`gpg.program`, pager).
OUTROS_SEM_O_CORPO = frozenset({"cd", "mkdir", "echo", "true"})
# A1 de segurança, volta 5: as opções que cada subcomando aceita como outro comando, numa lista fechada de opções que
# não rodam programa. Opção fora dela, inclusive a abreviada (`--rec` é `--receive-pack` para o git), tira o comando da
# lista: `git push --receive-pack='sh x.sh'` e `--exec=` rodam um programa da própria linha.
GIT_OUTRO_SEM_O_CORPO = {
    "add": frozenset({"-A", "--all", "-u", "--update", "-n", "--dry-run", "-v", "--verbose", "-f", "--force", "--"}),
    "push": frozenset({"-u", "--set-upstream", "--tags", "--follow-tags", "-n", "--dry-run", "-q", "--quiet", "-v",
                       "--verbose", "--porcelain"}),
    "status": frozenset({"-s", "--short", "-b", "--branch", "-sb", "--porcelain", "--porcelain=v1", "--porcelain=v2",
                         "--"}),
}
# A1 de segurança, volta 5: um comando do texto que muda o ambiente dos seguintes (`export GIT_SSH=sh`, `set -a`,
# `source`, `.`, `eval`, `env`) tira da lista positiva os outros comandos de todo comando lógico do texto.
MUDAM_O_AMBIENTE = frozenset({"export", "declare", "typeset", "readonly", "local", "set", "env", "source", ".", "eval"})


class Dono(str):
    """O texto que `corpo_so_lido` confere para um heredoc (`DonosDosHeredocs.montar`). `rodado`: o primeiro programa de
    `fora_do_texto` quando só ele faz do corpo comando (o dono sozinho só leria), para a mensagem nomeá-lo (M2)."""
    rodado = None


SUBSTITUICOES = ("$(", "`", "<(", ">(")


def citar(palavra):
    """A palavra de uma leitura (`leituras`, já sem as aspas), escrita de novo para o leitor (`palavras_do_texto`):
    entre aspas se preciso; sem elas a de `ANTES_DO_PROGRAMA`, que só vale sem aspas, e a que tem substituição, cujo
    conteúdo é texto do shell e tem programas (`BODY=$(cat …)`)."""
    if palavra in ANTES_DO_PROGRAMA or any(s in palavra for s in SUBSTITUICOES):
        return palavra
    return shlex.quote(palavra)


class DonosDosHeredocs:
    """Os donos dos heredocs de um texto (a linha sem os corpos, `resto`, e as leituras `com_sinal` dela, `lidas`), com
    o que serve a todos lido uma vez por texto (A1 do review, volta 5): os limites dos comandos lógicos
    (`limites_logicos`), o índice de cada leitura (`indice_das_partes`), se o texto grava arquivo (`grava_arquivo`) e
    os programas do texto inteiro fora da lista positiva dos outros comandos (`fora_do_texto`, M2 da volta única): o
    arquivo que o heredoc grava continua no disco depois do comando lógico dele, e o programa de qualquer ponto do
    texto, antes ou depois, em qualquer nível de substituição, pode rodá-lo. Heredocs com o mesmo dono recebem o mesmo
    texto, o mesmo objeto, e quem chama confere cada dono uma vez (`corpo_so_lido` guarda o resultado)."""

    def __init__(self, resto, lidas):
        self.resto, self.lidas = resto, lidas
        programas = programas_e_atribuicoes(resto)
        self.muda_o_ambiente = any(p in MUDAM_O_AMBIENTE for p, _, _ in programas)
        self.grava = grava_arquivo(resto)
        # cada programa com o comando simples dele (a atribuição antes conta, M4), ou todos se o texto muda o
        # ambiente; com o texto gravando, todo `git` (o `git` sem subcomando, que nenhum leitor aceita, fecha `git commit`)
        self.fora_do_texto = [(p, " ".join(map(citar, [*atribuicoes, p, *argumentos])))
                              for p, argumentos, atribuicoes in programas
                              if self.muda_o_ambiente or (self.grava and p == "git")
                              or not outro_sem_o_corpo(p, argumentos, atribuicoes)]
        if self.grava and any(p == "git" for p, _ in self.fora_do_texto):
            self.fora_do_texto.append(("git", "git"))
        if palavras_do_texto(resto).duvida:  # aspas ou substituição sem fechar no fim: o leitor não prova o resto
            self.fora_do_texto.append(("?", citar("?")))
        # M3: o texto grava arquivo e roda programa fora da lista; com o marcador crítico, construção não modelada
        self.gravado_e_rodado = self.fora_do_texto[0][0] if self.grava and self.fora_do_texto else None
        self.indices = [] if lidas.ilegivel else [indice_das_partes(partes) for partes in lidas.partes]
        self.vistos, self.citados, self.iguais, self.montados, self.gasto, self.largo = {}, {}, {}, {}, 0, None

    def segmento(self, k, sub, ini, fim):
        """As linhas citadas do segmento (nível, ini, fim) da leitura k, lidas uma vez (T3: a chave é o segmento, não o
        lugar); linhas e segmentos iguais viram o mesmo objeto, e `montar` os compara pelo `id`."""
        chave = (k, sub, ini, fim)
        if chave not in self.citados:
            partes, indice = self.lidas.partes[k], self.indices[k]
            linhas = tuple(self.iguais.setdefault(l, l) for l in citadas(partes[j][0] for j in indice.mesmo[sub][ini:fim + 1]))
            self.citados[chave] = self.iguais.setdefault(linhas, linhas)
        return self.citados[chave]

    def dono(self, posicao, marca):
        """O texto que `corpo_so_lido` confere para o heredoc do operador `marca` (A1 de segurança e A1 do review, volta
        3): o pipeline que recebe o corpo e, quando ele está numa substituição (`eval $(cat <<'EOF'`), os comandos de
        fora dela, lidos por `leituras` na linha sem os corpos; o `&&`, o `||`, o `;` e a quebra de linha (sem `|`
        antes) separam outro comando, que não lê o corpo (`git add x && git commit -m "$(cat <<'EOF'`). Mais os
        programas do texto inteiro fora da lista positiva dos outros comandos (`fora_do_texto`: `outro_sem_o_corpo`,
        ou todos se o texto tem um comando que muda o ambiente, `MUDAM_O_AMBIENTE`, e todo `git` se o texto grava
        arquivo, `grava_arquivo`: o git roda ganchos, filtros e configuração). O comando lógico inteiro
        (`comando_logico`), se a linha não se lê, tem subshell ou comando composto, ou a marca não aparece."""
        lugar = lugar_logico(self.resto, posicao)
        trechos = [] if self.lidas.ilegivel else [segmentos_do_operador(partes, marca, indice)
                                                    for partes, indice in zip(self.lidas.partes, self.indices)]
        chave = (lugar,) if self.lidas.ilegivel or None in trechos else (lugar, *map(tuple, trechos))
        if chave not in self.vistos:
            self.vistos[chave] = self.montar(lugar, trechos if len(chave) > 1 else None)
        return self.vistos[chave]

    def montar(self, lugar, trechos):
        if trechos is None:
            inicios, fins = limites_logicos(self.resto)
            return self.vestir(self.resto[inicios[lugar]:fins[lugar]] if lugar < len(fins) else "")
        if self.largo is not None:
            return self.largo
        pedacos = [self.segmento(k, *seg) for k, dela in enumerate(trechos) for seg in dela]
        chave = tuple(map(id, pedacos))  # o texto só depende dos segmentos, não do lugar
        if chave not in self.montados:
            sozinho = "\n".join(l for seg in pedacos for l in seg)
            self.gasto += len(sozinho)
            if self.gasto > TETO_DE_CARACTERES_DA_CHAMADA:  # C-4: alarga para as leituras inteiras e o resto, um objeto
                if len(self.resto) > TETO_DE_CARACTERES_DA_CHAMADA:
                    raise ValueError("donos dos heredocs acima do teto")
                todas = [l for partes in self.lidas.partes for l in citadas(p[0] for p in partes)]
                self.largo = self.vestir("\n".join([*todas, self.resto]))
                return self.largo
            self.montados[chave] = self.vestir(sozinho)
        return self.montados[chave]

    def vestir(self, sozinho):
        # os programas do texto vêm antes: uma aspa sem par no dono não os esconde
        texto = Dono("\n".join([*(comando for _, comando in self.fora_do_texto), sozinho]))
        if self.fora_do_texto and corpo_so_lido(sozinho):
            texto.rodado = self.fora_do_texto[0][0]
        return texto


def citadas(grupos):
    """Cada grupo de palavras de uma leitura, escrito de novo numa linha (`citar`), sem as marcas dos operadores."""
    linhas = []
    for palavras in grupos:  # a palavra `$(…)` não é programa: vale `_`, como no leitor
        for opaco in OPACO.values():
            palavras = [p.replace(opaco, "_") for p in palavras]
        linhas.append(MARCAS.sub(" ", " ".join(map(citar, palavras))))
    return linhas


# LOTE-LEITURA-HOOK, volta única (M1 e M2): o leitor sequencial do texto sem os corpos de heredoc. Uma passada, um
# estado para as aspas em cada nível de substituição (ADR 0011, item 1), como o bash lê: as palavras e as redireções de
# cada comando simples, de todos os níveis. A base de `grava_arquivo` e de `programas_e_atribuicoes`; nenhuma outra
# função do lote tira aspas para decidir gravação ou programa.
Palavra = collections.namedtuple("Palavra", "valor cru")  # o valor (sem aspas nem escapes) e o texto como escrito
Redirecao = collections.namedtuple("Redirecao", "prefixo operador alvo")  # alvo: Palavra, ou None (sem alvo)
ComandoSimples = collections.namedtuple("ComandoSimples", "palavras redirecoes")
# `aspa_escapada`: algum `$'…'` do texto (ou `\$'…'`, que o shell de dentro lê como `$'…'`) tem `\'` dentro. O bash
# o lê até o `'` que fecha; o `shlex` (`fichas`) toma a `\'` por fecho de aspas simples e junta o `;` seguinte à
# palavra (HOOK-ANSI-C): quem lê com `fichas` falha fechado.
LeituraDoTexto = collections.namedtuple("LeituraDoTexto", "simples duvida aspa_escapada", defaults=(False,))
OPERADORES_DE_REDIRECAO = ("<<<", "<<-", "<<", "<>", "<&", ">&", ">>", ">|", "<", ">")
PREFIXO_DE_REDIRECAO = re.compile(r"\d+|\{[A-Za-z_][A-Za-z0-9_]*\}")
SEPARADORES_DO_LEITOR = frozenset(";&|\n()")
ESCAPES_DAS_DUPLAS = frozenset('$`"\\\n')


class _Nivel:
    """Um nível do leitor: o texto de fora ou uma substituição (`$(…)`, crase, `<(…)`, `>(…)`), com o comando simples
    corrente, a palavra corrente e o estado das aspas dele."""

    def __init__(self, tipo):
        self.tipo, self.profundidade, self.aspas = tipo, 0, None  # aspas: None | simples | duplas | ansi
        self.palavras, self.redirecoes, self.pendente = [], [], None
        self.valor, self.inicio = None, 0


def _ansi_com_aspa_escapada(texto, inicio):
    """Se o `$'…'` cujo conteúdo começa em `inicio`, lido como o bash lê (`\\` escapa o seguinte), tem `\\'` antes do `'`
    que fecha. Vale para `\\$'…'`: o hook lê aspas simples, e o shell de dentro de `bash -c "…"` ou `eval "…"` recebe
    `$'…'` (o de fora troca `\\$` por `$`), então a leitura fiel não sabe onde a palavra termina (HOOK-ANSI-C)."""
    i, n = inicio, len(texto)
    while i < n and texto[i] != "'":
        if texto[i] == "\\":
            if texto[i + 1:i + 2] == "'":
                return True
            i += 2
        else:
            i += 1
    return False


@functools.lru_cache(maxsize=256)
def palavras_do_texto(texto):
    """Os comandos simples de `texto` (a linha sem os corpos de heredoc), de todos os níveis de substituição, com as
    palavras e as redireções de cada um, e se a leitura ficou em dúvida (aspas ou substituição sem fechar no fim, ou
    crase fechada dentro de aspas).
    Fora de aspas e numa substituição, `\\` torna o seguinte literal; entre aspas simples, tudo é literal; em `$'…'`,
    `\\` escapa o seguinte; entre aspas duplas (e `$"…"`), `\\` só escapa `$`, crase, `"` e `\\`, e `$(` e crase abrem
    substituição. `#` só abre comentário onde `comentarios` o prova. `${…}` e `$((…))` são texto do nível. Separadores
    (`;`, `&`, `|`, quebra de linha, `(`, `)`) e redireções só valem fora de aspas. A redireção leva o prefixo (`2`,
    `&`, `{fd}`) e o alvo, que é a palavra seguinte (colada ou não): `2>&1 x` tem o alvo `1` e deixa `x` como palavra."""
    provados = comentarios(texto)
    lidos, pilha, i, n, duvida = [], [_Nivel("fora")], 0, len(texto), False
    aspa_escapada = False

    def fechar_palavra(nivel, fim):
        if nivel.valor is None:
            return
        palavra = Palavra("".join(nivel.valor), texto[nivel.inicio:fim])
        nivel.valor = None
        if nivel.pendente is not None:
            nivel.redirecoes.append(nivel.pendente._replace(alvo=palavra))
            nivel.pendente = None
        else:
            nivel.palavras.append(palavra)

    def fechar_comando(nivel, fim):
        fechar_palavra(nivel, fim)
        if nivel.pendente is not None:
            nivel.redirecoes.append(nivel.pendente)
            nivel.pendente = None
        if nivel.palavras or nivel.redirecoes:
            lidos.append(ComandoSimples(tuple(nivel.palavras), tuple(nivel.redirecoes)))
        nivel.palavras, nivel.redirecoes = [], []

    def acrescentar(nivel, texto_lido, posicao):
        if nivel.valor is None:
            nivel.valor, nivel.inicio = [], posicao
        nivel.valor.append(texto_lido)

    def abrir(nivel, tipo, posicao, tamanho):
        acrescentar(nivel, "_", posicao)  # a palavra de fora vale `_` no lugar da substituição
        pilha.append(_Nivel(tipo))
        return posicao + tamanho

    while i < n:
        nivel, c = pilha[-1], texto[i]
        if nivel.tipo == "crase" and c == "`":  # o primeiro acento sem `\` fecha a crase; entre aspas, fica em dúvida
            duvida = duvida or nivel.aspas is not None
            fechar_comando(nivel, i)
            pilha.pop()
            i += 1
            continue
        if nivel.aspas == "simples":
            if c == "'":
                nivel.aspas = None
            else:
                nivel.valor.append(c)
            i += 1
            continue
        if nivel.aspas == "ansi":
            if c == "\\":
                aspa_escapada = aspa_escapada or texto[i + 1:i + 2] == "'"
                nivel.valor.append(texto[i:i + 2])
                i += 2
            else:
                if c == "'":
                    nivel.aspas = None
                else:
                    nivel.valor.append(c)
                i += 1
            continue
        if nivel.aspas == "duplas":
            if c == "\\":
                seguinte = texto[i + 1:i + 2]
                if seguinte in ESCAPES_DAS_DUPLAS and seguinte:
                    if seguinte != "\n":
                        nivel.valor.append(seguinte)
                    i += 2
                else:
                    nivel.valor.append(c)
                    i += 1
            elif c == '"':
                nivel.aspas = None
                i += 1
            elif texto.startswith("$(", i) and not texto.startswith("$((", i):
                i = abrir(nivel, "subst", i, 2)
            elif c == "`":
                i = abrir(nivel, "crase", i, 1)
            else:
                nivel.valor.append(c)
                i += 1
            continue
        # fora de aspas, no texto de fora ou numa substituição
        if c == "\\":
            if texto.startswith("$'", i + 1):  # HOOK-ANSI-C: o shell de dentro (`bash -c "…"`, `eval "…"`) lê `$'…'`
                aspa_escapada = aspa_escapada or _ansi_com_aspa_escapada(texto, i + 3)
            if texto[i + 1:i + 2] != "\n":  # `\` + quebra de linha continua a linha
                acrescentar(nivel, texto[i + 1:i + 2], i)
            i += 2
        elif c == "'":
            acrescentar(nivel, "", i)
            nivel.aspas = "simples"
            i += 1
        elif c == '"':
            acrescentar(nivel, "", i)
            nivel.aspas = "duplas"
            i += 1
        elif texto.startswith("$'", i):
            acrescentar(nivel, "", i)
            nivel.aspas = "ansi"
            i += 2
        elif texto.startswith('$"', i):
            acrescentar(nivel, "", i)
            nivel.aspas = "duplas"
            i += 2
        elif texto.startswith("$(", i) and not texto.startswith("$((", i):
            i = abrir(nivel, "subst", i, 2)
        elif c == "`":
            i = abrir(nivel, "crase", i, 1)
        elif texto.startswith(("<(", ">("), i) and nivel.valor is None:
            i = abrir(nivel, "subst", i, 2)
        elif c == "#" and i in provados:
            fim = texto.find("\n", i)
            i = n if fim < 0 else fim
        elif c in "<>" or texto.startswith(("&>",), i):
            prefixo = ""
            if c == "&":
                fechar_palavra(nivel, i)
                prefixo, i = "&", i + 1
            elif nivel.valor is not None and PREFIXO_DE_REDIRECAO.fullmatch(texto[nivel.inicio:i]):
                prefixo, nivel.valor = texto[nivel.inicio:i], None
            else:
                fechar_palavra(nivel, i)
            if nivel.pendente is not None:  # operador logo depois de outro, sem alvo
                nivel.redirecoes.append(nivel.pendente)
            operador = next(o for o in OPERADORES_DE_REDIRECAO if texto.startswith(o, i))
            nivel.pendente = Redirecao(prefixo, operador, None)
            i += len(operador)
        elif c in " \t":
            fechar_palavra(nivel, i)
            i += 1
        elif c in SEPARADORES_DO_LEITOR:
            if nivel.tipo == "subst" and c == ")" and not nivel.profundidade:
                fechar_comando(nivel, i)
                pilha.pop()
            else:
                if nivel.tipo == "subst" and c in "()":
                    nivel.profundidade += 1 if c == "(" else -1
                fechar_comando(nivel, i)
            i += 1
        else:
            acrescentar(nivel, c, i)
            i += 1
    for nivel in reversed(pilha):
        fechar_comando(nivel, n)
    duvida = duvida or len(pilha) > 1 or pilha[0].aspas is not None
    return LeituraDoTexto(tuple(lidos), duvida, aspa_escapada)


DESCRITOR = re.compile(r"\d+-?|-")  # o alvo de `>&` e `<&` que copia ou fecha um descritor
SEM_GRAVAR = frozenset({'/dev/null', '"/dev/null"'})


def redirecao_grava(redirecao):
    """M1, classificação positiva: a redireção não grava só se é de entrada (`<`, `<<`, `<<-`, `<<<`, `[n]<&m`,
    `[n]<&-`), cópia ou fechamento de descritor (`[n]>&m`, `[n]>&-`, `[n]>&m-`, com `m` só dígitos) ou saída para
    exatamente `/dev/null`. Qualquer outra grava: `>&arquivo`, `&>`, `<>`, `{fd}>`, `> >(…)`, alvo com `$` ou montado."""
    prefixo, operador, alvo = redirecao
    cru = alvo.cru if alvo is not None else None
    if prefixo.startswith("{"):
        return True
    if operador in ("<<", "<<-", "<<<", "<"):
        return False
    if operador in ("<&", ">&") and prefixo != "&":
        return cru is None or not DESCRITOR.fullmatch(cru)
    if operador in (">", ">>", ">|"):
        return cru not in SEM_GRAVAR
    return True


# A2 do review, volta 5: o `git` roda ganchos (`core.hooksPath`), filtros e `fsmonitor` lidos de arquivos; se o texto
# grava arquivo, o heredoc pode ter escrito um deles, e nenhum `git` do texto fica na lista positiva.
GRAVAM_ARQUIVO = frozenset({"tee", "uniq"})
GIT_GRAVA_ARQUIVO = frozenset({"apply", "am"})


def grava_arquivo(texto):
    """O texto pode gravar arquivo (A2 do review, volta 5; M1 da volta única): leitura em dúvida
    (`palavras_do_texto`), redireção fora da lista fechada das que não gravam (`redirecao_grava`), em qualquer posição
    e nível, `tee`, `uniq`, opção `-o`/`--output`, ou `git apply`/`git am`."""
    leitura = palavras_do_texto(texto)
    if leitura.duvida or any(redirecao_grava(r) for comando in leitura.simples for r in comando.redirecoes):
        return True
    for programa, argumentos in programas_da_linha(texto):
        if programa in GRAVAM_ARQUIVO or any(a.startswith(("-o", "--output", "--out")) for a in argumentos):
            return True
        if programa == "git" and subcomando_do_git(argumentos) in GIT_GRAVA_ARQUIVO:
            return True
    return False


def pipeline_do_operador(partes, marca, indice=None):
    """As palavras dos comandos do pipeline que contém `marca` (numa leitura `com_sinal` de `leituras`) e, a cada
    substituição em volta dele, as do pipeline do comando de fora que a contém; ou None: subshell, comando composto
    (`COMPOSTOS`), a marca não aparece ou o comando de fora não aparece."""
    indice = indice or indice_das_partes(partes)
    trechos = segmentos_do_operador(partes, marca, indice)
    if trechos is None:
        return None
    return [partes[j][0] for sub, ini, fim in trechos for j in indice.mesmo[sub][ini:fim + 1]]


def segmentos_do_operador(partes, marca, indice):
    """Os pipelines de `pipeline_do_operador`, como (nível de substituição, primeiro e último lugar na lista do nível,
    `indice.mesmo`), ou None. Só buscas no `indice` (`indice_das_partes`), lido uma vez por leitura para todos os
    heredocs dela (A1 do review, volta 5)."""
    if indice.opaco:
        return None
    achados = []
    for i in indice.onde.get(marca, ()):
        sub = partes[i][2]
        while True:
            achados.append((sub, *indice.pipeline[i]))
            if not sub:
                break
            sub = sub[:-1]  # o comando de fora vem depois dos de dentro da substituição (`comandos`)
            fora = indice.mesmo.get(sub, ())
            k = bisect.bisect_right(fora, i)
            if k == len(fora):
                return None
            i = fora[k]
    return achados or None


IndiceDasPartes = collections.namedtuple("IndiceDasPartes", "opaco onde mesmo pipeline")


def indice_das_partes(partes):
    """O que `pipeline_do_operador` busca numa leitura, numa passada só: `opaco` (subshell ou comando composto),
    `onde` (as partes que citam cada marca de operador), `mesmo` (por nível de substituição, as partes com palavras ou
    destinos, em ordem) e `pipeline` (de cada uma dessas partes, o primeiro e o último lugar, na lista do nível, do
    pipeline dela: as partes ligadas por `|` ou `|&`)."""
    opaco = any(sinal in ("(", ")") or COMPOSTOS.intersection(palavras) for palavras, _, _, sinal in partes)
    onde, mesmo, pipeline, abertos = {}, {}, {}, {}
    for i, (palavras, destinos, sub, _) in enumerate(partes):
        for marca in dict.fromkeys(m for p in palavras for m in MARCAS.findall(p)):
            onde.setdefault(marca, []).append(i)
        if not (palavras or destinos):
            continue
        nivel = mesmo.setdefault(sub, [])
        if not nivel or partes[nivel[-1]][3].strip("\n") not in ("|", "|&"):
            abertos[sub] = len(nivel)  # começa um pipeline novo neste nível
        nivel.append(i)
        pipeline[i] = abertos[sub]
    for nivel in mesmo.values():  # o fim de cada pipeline: o último lugar com o mesmo começo
        fim = {}
        for lugar, j in enumerate(nivel):
            fim[pipeline[j]] = lugar
        for j in nivel:
            pipeline[j] = (pipeline[j], fim[pipeline[j]])
    return IndiceDasPartes(opaco, onde, mesmo, pipeline)


def comando_logico(texto, posicao):
    """O comando lógico de `posicao` em `texto` (a linha sem os corpos de heredoc): as linhas físicas que o bash junta
    num comando só, lidas do começo do texto. Uma linha se junta à seguinte se acaba em continuação
    (`continua_na_proxima`: `bash \\`⏎`<<'EOF'`, `cat <<'EOF' |`⏎corpo⏎`EOF`⏎`bash`) ou se deixa um `(`, uma aspa ou
    uma crase sem par (`x=$(cat <<'EOF'`⏎corpo⏎`EOF`⏎`); eval "$x"`, A2 de segurança, volta 4). É o dono do heredoc
    quando a leitura por pipeline não serve: quem lê o corpo pode estar noutra linha física (A1 de segurança, volta 3).
    Os limites saem de `limites_logicos`, lidos uma vez por texto; aqui, só a busca (A1 do review, volta 5)."""
    inicios, fins = limites_logicos(texto)
    k = lugar_logico(texto, posicao)
    return texto[inicios[k]:fins[k]] if k < len(fins) else ""


def lugar_logico(texto, posicao):
    """O lugar, na lista de `limites_logicos`, do comando lógico de `posicao` em `texto` (busca binária)."""
    return bisect.bisect_left(limites_logicos(texto)[1], posicao)


@functools.lru_cache(maxsize=4)
def limites_logicos(texto):
    """(inícios, fins) dos comandos lógicos de `texto`, em ordem, numa passada só (`comando_logico`): o mesmo texto
    com milhares de heredocs não é relido do começo a cada operador."""
    inicios, fins, ini, pilha = [], [], 0, []
    for fim in [m.start() for m in re.finditer("\n", texto)] + [len(texto)]:
        linha = texto[texto.rfind("\n", 0, fim) + 1:fim]
        pilha = abertos_na_linha(linha, pilha)
        if fim < len(texto) and (pilha or continua_na_proxima(linha)):
            continue
        inicios.append(ini)
        fins.append(fim)
        ini, pilha = fim + 1, []
    return tuple(inicios), tuple(fins)


def abertos_na_linha(linha, pilha):
    """A pilha de contextos sem par (`(`, `"`, `'`, crase) depois de `linha`, partindo de `pilha` (a das linhas
    anteriores do mesmo comando lógico). Lê como o bash: aspas simples não têm escape; `\\` escapa o caractere
    seguinte; `$(` abre contexto também entre aspas duplas; `#` no começo de palavra, fora de aspas, comenta o resto da
    linha. Na dúvida a pilha fica maior, e o comando lógico, que só torna o hook mais desconfiado, também."""
    pilha, i = list(pilha), 0
    while i < len(linha):
        c, topo = linha[i], pilha[-1] if pilha else None
        if topo == "'":
            if c == "'":
                pilha.pop()
        elif c == "\\":
            i += 1
        elif topo == '"':
            if c == '"':
                pilha.pop()
            elif c == "`":
                pilha.append(c)
            elif linha.startswith("$(", i):
                pilha.append("(")
                i += 1
        elif c == "#" and (i == 0 or linha[i - 1] in " \t;&|()<>"):
            break
        elif c in "'\"(":
            pilha.append(c)
        elif c == "`":
            if topo == "`":
                pilha.pop()
            else:
                pilha.append(c)
        elif c == ")" and topo == "(":
            pilha.pop()
        i += 1
    return pilha


# LOTE-LEITURA-HOOK (A1 de segurança): os programas que leem o corpo de um heredoc como texto e não o executam. A lista
# é positiva: qualquer outro dono (shell, `source`, `.`, `eval`, `xargs`, um laço, um lançador, um caminho) roda ou pode
# rodar o corpo, que então é conferido como comando. `git` e `gh` só com um subcomando embutido (alias não os sobrepõe)
# e, no `git`, sem `-c` (que pode definir um alias `!sh`). Sem `sort`: `--compress-program=sh` roda os dados (A3 de
# segurança, volta 4).
LEITORES_DO_CORPO = frozenset({"cat", "tee", "grep", "egrep", "fgrep", "head", "tail", "wc", "uniq", "cut", "tr",
                               "base64", "diff", "cmp", "nl", "tac", "jq", "md5sum", "sha1sum", "sha256sum", "read"})
GIT_LE_O_CORPO = frozenset({"commit", "tag", "notes", "apply", "am", "hash-object", "interpret-trailers", "stripspace",
                            "check-ignore", "check-attr", "cat-file"})
GH_LE_O_CORPO = frozenset({"pr", "issue", "release", "api", "gist", "label", "secret", "variable"})
ANTES_DO_PROGRAMA = frozenset({"!", "{", "time", "then", "do", "else", "elif", "if", "while", "until"})
ATRIBUICAO = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\+?=")


def programas_da_linha(linha):
    """O programa de cada comando simples do texto (`programas_e_atribuicoes`), com os argumentos:
    [(programa, [argumentos])]."""
    return [(programa, argumentos) for programa, argumentos, _ in programas_e_atribuicoes(linha)]


def programas_e_atribuicoes(linha):
    """M2 da volta única, enumerador positivo: em cada comando simples do leitor (`palavras_do_texto`), de qualquer
    nível de substituição, o programa é a primeira palavra que não se prova atribuição (`NOME=` ou `NOME+=` sem aspas
    no nome) nem palavra de `ANTES_DO_PROGRAMA` sem aspas; a redireção completa (operador e alvo) já sai do leitor e
    não consome a palavra seguinte (`2>&1 ./x.sh`). Com os argumentos e as atribuições daquele comando simples, não as
    do comando de fora de uma substituição (`BODY="$(cat <<'EOF'…)"`: o `cat` não tem atribuição):
    [(programa, [argumentos], [atribuicoes])]."""
    achados = []
    for comando in palavras_do_texto(linha).simples:
        atribuicoes = []
        for k, palavra in enumerate(comando.palavras):
            if palavra.cru in ANTES_DO_PROGRAMA:
                continue
            if ATRIBUICAO.match(palavra.cru):
                atribuicoes.append(palavra.valor)
                continue
            achados.append((palavra.valor, [p.valor for p in comando.palavras[k + 1:]], atribuicoes))
            break
    return achados


def subcomando_do_git(argumentos):
    """O subcomando embutido do `git` com estes argumentos, ou None (sem subcomando, ou com `-c`, que pode definir um
    alias `!sh`)."""
    resto = list(argumentos)
    while resto and resto[0].startswith("-") and resto[0] != "-c":
        resto = resto[2:] if resto[0] == "-C" else resto[1:]
    return resto[0] if resto and resto[0] != "-c" else None


def outro_sem_o_corpo(programa, argumentos, atribuicoes=()):
    """O comando simples `programa argumentos`, noutro ponto do comando lógico do heredoc, não roda o corpo nem o
    arquivo que ele grava: um leitor (`le_o_corpo`), `OUTROS_SEM_O_CORPO` ou um `git` de `GIT_OUTRO_SEM_O_CORPO` só com as
    opções da lista dele. Nunca com atribuição antes (`GIT_SSH=sh git push`, `HOME=. git status`)."""
    if atribuicoes:
        return False
    if programa in OUTROS_SEM_O_CORPO or (programa == "git" and git_outro_sem_o_corpo(argumentos)):
        return True
    return le_o_corpo(programa, argumentos)


def git_outro_sem_o_corpo(argumentos):
    """`git argumentos` é um subcomando de `GIT_OUTRO_SEM_O_CORPO` só com as opções da lista dele e, antes do
    subcomando, só `-C <pasta>` e `--no-pager` (`--config-env`, `--exec-path` e `-c` ficam fora)."""
    resto = list(argumentos)
    while resto and resto[0] in ("-C", "--no-pager"):
        resto = resto[2:] if resto[0] == "-C" else resto[1:]
    if not resto or resto[0] not in GIT_OUTRO_SEM_O_CORPO:
        return False
    return all(not a.startswith("-") or a in GIT_OUTRO_SEM_O_CORPO[resto[0]] for a in resto[1:])


def nenhum(programa):
    return False


def le_o_corpo(programa, argumentos, tambem=nenhum):
    """`programa argumentos` lê o corpo como texto: `LEITORES_DO_CORPO`, `git`/`gh` com subcomando que lê, ou o que
    `tambem` aceitar."""
    if programa in LEITORES_DO_CORPO or tambem(programa):
        return True
    if programa == "git":
        return subcomando_do_git(argumentos) in GIT_LE_O_CORPO
    return programa == "gh" and bool(argumentos) and argumentos[0] in GH_LE_O_CORPO


@functools.lru_cache(maxsize=1024)
def corpo_so_lido(dono, tambem=nenhum):
    """O corpo de heredoc do comando `dono` (`DonosDosHeredocs`) só é lido como texto: o dono tem programa provado
    (M2: sem programa, como em `(2>&1 bash)` lido sem o `bash`, não só lê) e todo comando dele é um leitor
    (`le_o_corpo`), sem atribuição antes no mesmo comando simples (M4: `PATH=/tmp/x cat`, `GIT_CONFIG_COUNT=1 … git
    commit` mudam o programa ou o que ele roda). Senão, o corpo é conferido como comando. O resultado fica guardado: os
    heredocs de um mesmo dono (o mesmo texto) são conferidos uma vez só."""
    programas = programas_e_atribuicoes(dono)
    return bool(programas) and all(not atribuicoes and le_o_corpo(programa, argumentos, tambem)
                                   for programa, argumentos, atribuicoes in programas)


def construcao_nao_modelada(linha):
    """ADR 0011, item 2: a primeira construção da lista fechada que o analisador não modela, ou None. Fora de aspas
    simples: `#` com outra linha depois (em qualquer posição da palavra), crase, `$` que não abra `$(` (`$'`, `$"`,
    `${`, `$X`, `$@`, `$1`, `$?`...; só o `$?` entre aspas duplas passa, emenda H1-1; isso vale no domínio desta
    função, que só roda com marcador crítico: sem ele o hook lê o `$?` como na base), `\\` seguido de quebra de linha;
    fora de aspas, chaves e `case`; e todo `<<` que não seja heredoc de `HEREDOC_MODELADO` (inclusive `<<` entre aspas
    ou escapado numa linha com várias linhas). As aspas
    são lidas em sequência, e `$(` abre um contexto novo de aspas, como no bash; `\\` escapa o caractere seguinte fora
    de aspas e, entre duplas, `$`, crase, `"` e `\\`."""
    pilha = [["fora", 0]]  # contexto: fora | subst (com a profundidade de parênteses) | simples | duplas
    esqueleto, pendentes, modelados, i, n = [], [], set(), 0, len(linha)
    provados = comentarios(linha)  # o mesmo conjunto que o leitor usa, sobre a mesma linha
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
        elif c == "$" and seguinte == "?" and contexto[0] == "duplas":
            pass  # `"$?"`: um decimal de 0 a 255 numa palavra que o bash não divide (ADR 0011, emenda H1-1)
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
            if i in provados:
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
    # O `tirar_heredocs` só separa o corpo de um `<<` que `heredocs` prova ser operador, e a linha com `<<` em dúvida é
    # ilegível; esta regra continua mais estrita (só com `CRITICO`): com várias linhas, todo `<<` fora dos heredocs
    # modelados e dos corpos deles é não modelado, também entre aspas ou depois de `\\`.
    if "\n" in linha and any(m.start() not in modelados for m in re.finditer("<<", linha)):
        return "heredoc"
    return "case" if CASE.search("".join(esqueleto)) else None


# ADR 0011, item 2, opção D (RET-LEITURA-HOOK-D): a chamada com heredoc e ação crítica só passa numa gramática positiva.
# Sem os corpos, cada forma canônica vira uma palavra literal (K1 a K3); o resto usa o alfabeto do item 1, os separadores
# `&&`, `;` e a quebra de linha, e cada comando simples começa por um programa da lista, sem atribuição antes.
PROGRAMAS_DA_GRAMATICA = frozenset({"git", "gh", "cd", "mkdir", "echo", "true"})
GIT_FORA_DA_GRAMATICA = re.compile(r"-c$|--config-env|--exec-path")  # o `git` sem configuração nem programa trocado
VALOR_DE_TEXTO = frozenset({"-m", "--message", "-b", "--body", "-t", "--title", "--subject", "--notes"})
OPERADOR_K = "\x01"  # o operador e o delimitador de um heredoc modelado, na linha sem os corpos
PALAVRA_K3 = "\x02"  # a palavra `"$(cat <<'X'⏎…⏎X⏎)"`, já sem o corpo
K1 = re.compile(r"[ \t]*cat[ \t]+>>?[ \t]*[\w./:@,+%~^-]+[ \t]+\x01[ \t\n]*")  # a chamada inteira (fullmatch)
K3 = re.compile(r'"\$\(cat[ \t]+\x01[ \t]*\n\)"')
CONTORNO_DA_GRAMATICA = ("na chamada com heredoc e ação crítica, só cat > arq <<'FIM' sozinho na chamada, "
                         "git commit -F - <<'FIM' e -m, --body ou --title \"$(cat <<'FIM'…FIM)\", com comandos git, gh, "
                         "cd, mkdir, echo e true literais, separados por &&, ; ou quebra de linha (sem atribuição, $, "
                         "redireção nem pipe); o resto vai noutra chamada do Bash (docs/hooks.md)")


def sem_os_corpos(texto, achados):
    """O texto sem os corpos dos heredocs provados, com o operador e o delimitador de cada um trocados por `OPERADOR_K`."""
    cortes = sorted([(h.operador, h.fim_do_operador, f" {OPERADOR_K} ") for h in achados]
                    + [(h.corpo[0], h.fim, "") for h in achados])
    saida, inicio = [], 0
    for ini, fim, troca in cortes:
        saida += [texto[inicio:ini], troca]
        inicio = fim
    saida.append(texto[inicio:])
    return "".join(saida)


def legivel(palavra):
    """A palavra com as formas K de volta no texto, para a mensagem."""
    return palavra.replace(OPERADOR_K, "<<'FIM'").replace(PALAVRA_K3, '"$(cat <<…)"')


def simples_da_gramatica(resto):
    """Os comandos simples do resto (listas de palavras cruas), ou o primeiro sinal fora da gramática (str). Aspas
    como no item 1: entre simples, tudo menos controle; entre duplas, também sem `$`, crase, `\\` e `!`, menos o `$?`
    (o código de saída, ADR 0011, emenda H1-1); fora de aspas, o `$?` é recusado. Isso vale no domínio desta função,
    que só roda com marcador crítico; sem ele o hook lê o `$?` como na base."""
    simples, palavras, palavra, i, n = [], [], "", 0, len(resto)

    def fechar():
        nonlocal palavra
        if palavra:
            palavras.append(palavra)
        palavra = ""

    while i < n:
        c = resto[i]
        if c in "'\"":
            fim = resto.find(c, i + 1)
            if fim < 0:
                return f"{c} sem fechar"
            proibidos = DUPLAS_RECUSA if c == '"' else ()
            ruim = next((x for x in resto[i + 1:fim].replace("$?", "") if x in proibidos or controle(x)), None)
            if ruim is not None:
                return nome_do_sinal(ruim)
            palavra, i = palavra + resto[i:fim + 1], fim + 1
            continue
        if resto.startswith("&&", i) or c in ";\n":
            fechar()
            if palavras:
                simples.append(palavras)
            palavras = []
            i += 2 if c == "&" else 1
            continue
        if c in " \t":
            fechar()
        elif c in (OPERADOR_K, PALAVRA_K3) or c.isalnum() or c in ALFABETO_LEITURA:
            palavra += c
        else:
            return nome_do_sinal(c)
        i += 1
    fechar()
    if palavras:
        simples.append(palavras)
    return simples


def sem_aspas(palavra):
    """A palavra como o bash a entrega ao programa (opção A, item 1): na gramática, o que está entre aspas já é literal
    (`simples_da_gramatica`), então tirar as aspas é exato. `'-c'`, `"-c"` e `-'c'` são `-c`."""
    partes, i, n = [], 0, len(palavra)
    while i < n:
        c = palavra[i]
        if c in "'\"":
            fim = palavra.index(c, i + 1)
            partes.append(palavra[i + 1:fim])
            i = fim + 1
        else:
            partes.append(c)
            i += 1
    return "".join(partes)


def comando_fora_da_gramatica(palavras):
    """O primeiro sinal do comando simples fora da gramática, ou None: o programa da lista, o heredoc só na forma K2
    (`git commit … -F - <<'X'`) e a palavra K3 só como valor de `-m`, `--body`, `--title`… Cada palavra é comparada sem
    as aspas (`sem_aspas`), como o programa a recebe."""
    palavras = [sem_aspas(p) for p in palavras]
    programa = palavras[0]
    if ATRIBUICAO.match(programa):
        return f"{legivel(programa)} (atribuição antes do programa)"
    if programa not in PROGRAMAS_DA_GRAMATICA:
        return f"{legivel(programa)} (fora da lista de programas)"
    for k, palavra in enumerate(palavras[1:], 1):
        if programa == "git" and GIT_FORA_DA_GRAMATICA.match(palavra):
            return f"git {legivel(palavra)}"
        if OPERADOR_K in palavra and not (palavra == OPERADOR_K and programa == "git" and palavras[1] == "commit"
                                          and palavras[k - 2:k] == ["-F", "-"]):
            return "<<'FIM' fora de git commit -F -"
        if PALAVRA_K3 in palavra and not (palavra == PALAVRA_K3 and palavras[k - 1] in VALOR_DE_TEXTO):
            return '"$(cat <<…)" fora de -m, --body ou --title'
    return None


# O que a gramática aceitou (o T9 roda o texto no bash e compara): os comandos simples, com as palavras sem aspas e as
# formas K (`OPERADOR_K`, `PALAVRA_K3`) no lugar, os corpos na ordem delas no texto e se a chamada é a K1 sozinha.
Gramatica = collections.namedtuple("Gramatica", "comandos corpos k1")


# O `<<` que o bash pode formar num nível de cima (opção A da revalidação 8): ele lê o operador antes de tirar aspas e
# expandir, então no nível N só há `<<` se o nível N-1 deixou dois `<` juntos. Entre eles, o N-1 pode apagar aspas,
# `\`, `\` + quebra de linha e `$(…)` que dá vazio (`eval '<''<EOF'`, `bash -c "<""<EOF"`, `\<\<`, `"<$(:)<"`).
HEREDOC_QUE_O_BASH_FORMA = re.compile(r"<(?:['\"\\]|\\\n|\$\([^()]*\))*<")


def tem_heredoc_no_texto(texto):
    """Opção A (revalidações 7 e 8): o gatilho é textual, haja heredoc provado ou não: dois `<` com, entre eles, só o
    que um nível pode apagar (`HEREDOC_QUE_O_BASH_FORMA`), o que inclui o `<<` literal e o `<\\`⏎`<` (o bash junta a
    quebra antes de ler os operadores). O `<<` calculado (`$(printf '\\x3c\\x3c')` dentro de `eval`) nenhum gatilho de
    texto vê: a reavaliação com marcador crítico recusa (opção B)."""
    return HEREDOC_QUE_O_BASH_FORMA.search(texto) is not None


def gramatica_com_heredoc(texto):
    """ADR 0011, item 2 (opções D e A): None se o texto não tem `<<` (`tem_heredoc_no_texto`); senão o primeiro sinal
    fora da gramática positiva (str) ou o que ela aceitou (`Gramatica`). O `<<` em dúvida, o heredoc fora de
    `HEREDOC_MODELADO` e a linha de corpo que começa pelo delimitador sem ser igual a ele (o bash 5.3 fecha em `EOF)`
    dentro de `$(`; opção A, item 3) recusam. Sem heredoc provado, o resto é o próprio texto (`bash -c '…<<…'`, `eval`,
    `grep '<<'`). Tirados os corpos, K1 (`cat > arq <<'X'`, ou `>>`) passa sozinha na chamada, K3 vira uma palavra
    literal e o resto passa por `simples_da_gramatica` e `comando_fora_da_gramatica`."""
    if not tem_heredoc_no_texto(texto):
        return None
    achados, duvida = heredocs(texto)
    if duvida is not None:
        return "<< que o hook não prova ser heredoc"
    if OPERADOR_K in texto or PALAVRA_K3 in texto:
        return nome_do_sinal(OPERADOR_K if OPERADOR_K in texto else PALAVRA_K3)
    for h in achados:
        m = HEREDOC_MODELADO.match(texto, h.operador)
        if m is None or m.end() != h.fim_do_operador:
            return "heredoc fora da forma <<'FIM'"
    corpos = [texto[h.corpo[0]:h.corpo[1]] for h in achados]
    for h, corpo in zip(achados, corpos):
        if any(linha != h.delimitador and linha.startswith(h.delimitador) for linha in corpo.split("\n")):
            return f"linha que começa por {h.delimitador} no corpo"
    resto = sem_os_corpos(texto, achados)
    if len(achados) == 1 and K1.fullmatch(resto):
        return Gramatica([], corpos, True)
    lidos = simples_da_gramatica(K3.sub(PALAVRA_K3, resto))
    if isinstance(lidos, str):
        return lidos
    sinal = next((sinal for sinal in map(comando_fora_da_gramatica, lidos) if sinal), None)
    return sinal or Gramatica([[sem_aspas(p) for p in palavras] for palavras in lidos], corpos, False)


def fora_da_gramatica_com_heredoc(texto):
    """ADR 0011, item 2: o primeiro sinal da chamada com `<<` fora da gramática positiva, ou None (também quando o texto
    não tem `<<`). Quem chama a aplica só no texto inteiro da chamada (o nível 0) e com o marcador crítico; o `<<` de um
    nível de cima é o que o bash pode formar com o texto do nível 0 (`tem_heredoc_no_texto`). Nenhuma expansão sobra fora das formas K, as palavras são comparadas sem aspas e os corpos são cortados
    como o bash os corta, então a decisão não depende de como o leitor lê aspas, substituições e níveis."""
    lida = gramatica_com_heredoc(texto)
    return lida if isinstance(lida, str) else None


# Orçamento da chamada com marcador crítico (bloco T da revalidação 10): o texto sem os corpos de heredoc passa de 150 mil
# caracteres, ou o leitor acha mais de 5 mil palavras (de todos os níveis). Uma chamada real não chega perto; o teto de
# palavras faz a decisão independer da carga da máquina. O corpo de heredoc sai da conta, e o texto entre aspas é uma
# palavra só.
TETO_DE_CARACTERES_DA_CHAMADA = 150_000
TETO_DE_PALAVRAS = 5_000
CONTORNO_DO_TETO = "divida a chamada em comandos menores e grave o texto longo num arquivo"


def excede_o_teto(texto):
    """`texto`: a chamada sem os corpos de heredoc. O motivo (str) se ela passa do teto de caracteres ou de palavras, ou
    None. Quem chama a confere só com o marcador crítico, no nível 0, antes de qualquer leitura cara."""
    if len(texto) > TETO_DE_CARACTERES_DA_CHAMADA:
        return f"{len(texto)} caracteres (o teto é {TETO_DE_CARACTERES_DA_CHAMADA})"
    palavras = sum(len(simples.palavras) for simples in palavras_do_texto(texto).simples)
    if palavras > TETO_DE_PALAVRAS:
        return f"{palavras} palavras (o teto é {TETO_DE_PALAVRAS})"
    return None


Leituras = collections.namedtuple("Leituras", "partes ilegivel")


def leituras(comando, com_sinal=False, sem_marcas=None):
    """ADR 0013: a única porta dos hooks para ler a linha. `partes`: a leitura fiel (`comandos`) e, se a linha tem `#`
    e a leitura antiga (a da develop, `legado`) fecha e dá outro resultado, também ela (I2: o que a develop recusava
    continua recusado). `ilegivel`: a leitura fiel não fecha (aspas sem par, também no corpo de uma crase que fecha) ou
    um comentário que o hook não prova levaria aspa ou `\\` para outra linha (`comentario_ambiguo`); quem chama
    decide, fechado onde é controle. `com_sinal`: o de `comandos` (o sinal que encerra cada comando). `sem_marcas`: o
    `comando` sem as marcas de `tirar_heredocs` (palavras `[A-Za-z0-9_]` depois de um espaço, sem aspa, `\\` nem `$`,
    não mudam a `aspa_escapada`), cuja `palavras_do_texto` o chamador lê de qualquer jeito: lida no lugar da marcada."""
    def corpos_se_leem(texto, nivel):
        """CRASE-ASPA-HOOK: o bash fecha a crase antes da aspa (`` x=`'`; L; y=`'` ``), o `shlex` não; a aspa sem par
        de um corpo casaria com a de outro e o comando do meio viraria texto. Cada corpo (e os de dentro, até
        `PROFUNDIDADE`) se lê sozinho, ou a linha é ilegível. A crase sem par não basta para isso: o `segmento` do
        `conformidade` relê pedaços de palavra (`` `date ``), e o resto depois dela o bash não roda."""
        if nivel > PROFUNDIDADE:
            return False
        for corpo in conteudos_de_crase(texto, so_os_fechados=True):
            list(comandos(corpo))  # aspa sem par no corpo: ValueError
            if not corpos_se_leem(corpo, nivel + 1):
                return False
        return True

    try:
        fiel = (None if comentario_ambiguo(comando) or not corpos_se_leem(comando, 1)
                # HOOK-ANSI-C: o `shlex` não fecha `$'…\'…'` como o bash
                or palavras_do_texto(comando if sem_marcas is None else sem_marcas).aspa_escapada
                else list(comandos(comando, com_sinal=com_sinal)))
    except ValueError:
        fiel = None
    partes = [] if fiel is None else [fiel]
    if "#" in comando:
        try:
            antiga = list(comandos(comando, legado=True, com_sinal=com_sinal))
        except ValueError:
            antiga = None
        if antiga is not None and antiga != fiel:
            partes.append(antiga)
    return Leituras(tuple(partes), fiel is None)


def depois_das_atribuicoes(palavras, i=0):
    """O índice da primeira palavra de `palavras`, a partir de `i`, que não é atribuição de variável (`A=1 B=2 git ...`)."""
    while i < len(palavras) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", palavras[i]):
        i += 1
    return i


def sem_atribuicoes(palavras):
    """Tira as atribuições de variáveis do início de um comando simples (`A=1 B=2 git ...`)."""
    return palavras[depois_das_atribuicoes(palavras):]


# Lançador -> as opções dele que o hook modela (RET-LEITURA-HOOK-F, opção A da proposta caminho-rev12): a fonte única e
# positiva que `separar_lancadores` e a recusa (`opcao_fora_da_tabela`) leem. Cada opção vale por extenso e uma por
# palavra: "booleanas" não levam valor; "com_valor" leva a palavra seguinte (a longa também `--opcao=valor`); "coladas"
# leva o valor colado (`stdbuf -oL`). O `--` fecha as opções de todos. Com o marcador crítico, a palavra com `-` fora da
# tabela, antes do comando, recusa nos dois hooks, sem que o hook tente lê-la (ADR 0011: o que o analisador não modela é
# recusado): o `env -S` em qualquer grafia, o `-a`, o `-f`, o grupo curto (`-iu X`), a abreviação longa (`--un`), o
# `sudo -s` e a opção de um `env` que o hook não conhece. Sem o marcador, a recusa não vale: `separar_lancadores` devolve
# as leituras possíveis da palavra fora da tabela, e as regras da linha recusam se qualquer uma recusa. O hook não imita
# nenhum `env` (GNU, uutils, BSD).
LANCADORES = {
    "env": {"booleanas": frozenset({"-i", "-", "--ignore-environment", "-0", "--null", "-v", "--debug"}),
            "com_valor": frozenset({"-u", "--unset", "-C", "--chdir"})},
    "sudo": {"booleanas": frozenset({"-E", "-H", "-n", "-P", "-k", "-b"}),
             "com_valor": frozenset({"-u", "-g", "-C", "-D", "-p", "-r", "-t", "-U", "-h", "-R", "-T", "--user",
                                     "--group"})},
    "command": {"booleanas": frozenset({"-p", "-v", "-V"})},  # `-v`/`-V` só mostram: ler o comando é o lado seguro
    "nohup": {},
    "time": {"booleanas": frozenset({"-p"}), "com_valor": frozenset({"-o", "-f", "--output", "--format"})},
    "exec": {"booleanas": frozenset({"-c", "-l"}), "com_valor": frozenset({"-a"})},
    "builtin": {},
    "nice": {"booleanas": frozenset(f"-{n}" for n in range(20)), "com_valor": frozenset({"-n", "--adjustment"})},
    "setsid": {},
    "stdbuf": {"com_valor": frozenset({"-i", "-o", "-e", "--input", "--output", "--error"}),
               "coladas": frozenset({"-i", "-o", "-e"})},
    "timeout": {"booleanas": frozenset({"--preserve-status", "--foreground", "-v", "--verbose"}),
                "com_valor": frozenset({"-k", "-s", "--kill-after", "--signal"})},
    "xargs": {"booleanas": frozenset({"-0", "-r", "-t", "-x", "--null", "--no-run-if-empty"}),
              "com_valor": frozenset({"-n", "-I", "-L", "-P", "-d", "-E", "-s", "-a", "--max-args", "--max-procs",
                                      "--delimiter", "--arg-file", "--max-lines", "--max-chars"}),
              "coladas": frozenset({"-n", "-I", "-L", "-P", "-d", "-E", "-s", "-a"})},
}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
ATRIBUICAO = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")  # `NOME=valor`, que o lançador aceita misturado às opções


def opcao_modelada(nome, palavra):
    """Quantas palavras seguintes a opção `palavra` do lançador `nome` consome pela tabela `LANCADORES` (0 ou 1), ou
    None se a tabela não a modela."""
    tabela = LANCADORES[nome]
    if palavra == "--" or palavra in tabela.get("booleanas", ()):
        return 0
    if palavra in tabela.get("com_valor", ()):
        return 1
    longa, igual, _ = palavra.partition("=")
    if igual and longa.startswith("--") and longa in tabela.get("com_valor", ()):
        return 0
    if len(palavra) > 2 and palavra[:2] in tabela.get("coladas", ()):
        return 0
    return None  # fora da tabela


def opcao_fora_da_tabela(palavras, i, nome, memoria=None):
    """A primeira palavra com `-`, a partir de `palavras[i]` (depois do lançador `nome`) e antes do comando, que a
    tabela `LANCADORES` não modela, ou None. Anda pelas opções da tabela misturadas com `NOME=valor` (como o uutils
    aceita) até a primeira palavra que não é nenhuma das duas, ou até o `--`. `memoria`: {(nome, índice): resultado},
    para que a passada de `reavaliacao_das_palavras` sobre lançadores seguidos (`sudo -u sudo -u …`) siga linear."""
    caminho, fora = [], None
    while i < len(palavras):
        if memoria is not None and (nome, i) in memoria:
            fora = memoria[(nome, i)]
            break
        caminho.append(i)
        palavra = palavras[i]
        if ATRIBUICAO.match(palavra):
            i += 1
            continue
        if not palavra.startswith("-"):
            break
        consome = opcao_modelada(nome, palavra)
        if consome is None:
            fora = palavra
            break
        if palavra == "--":
            break
        i += 1 + consome
    if memoria is not None:
        for j in caminho:
            memoria[(nome, j)] = fora
    return fora


class LancadorDemais(ValueError):
    """O comando simples tem mais de `TETO_FORA_DA_TABELA` palavras com `-` fora da tabela `LANCADORES` antes do comando:
    o hook não lê as leituras todas e o comando não é analisável (RET-LEITURA-HOOK-G, opção A da proposta caminho-rev13)."""


class TextoAbertoComLeituras(LancadorDemais):
    """O texto dividido do `env` não fecha aspas e o comando tem mais de uma leitura (uma palavra fora da tabela
    `LANCADORES` já vista antes dele): o hook não lê todas e o comando não é analisável; recusa como o teto, qualquer que
    seja o resto (RET-LEITURA-HOOK-H, opção B da proposta caminho-rev14)."""


class TextoDivididoAberto(ValueError):
    """O texto dividido do `env` não fecha aspas, numa leitura só (nenhuma palavra fora da tabela antes dele): o `env`
    não o roda, e o comando vai à regra do comando aninhado que o hook não analisa (`ilegivel`), como na `develop`."""


# O teto K de palavras fora da tabela por leitura (contando os lançadores encadeados): cada uma abre até 3 leituras, e o
# `segmento` roda as regras da linha sobre cada uma. K = 3 dá no máximo 27 leituras. Medido em RET-LEITURA-HOOK-G
# (`test_tempo_do_teto_das_leituras_do_lancador`): com K palavras e 50 lançadores, a `Guarda` decide em cerca de 2 a 5 ms
# (o limite do teste é 0,5 s; o vigia de produção, 3 s), e com K + 1 o comando não é analisável e recusa. K fica em 3
# porque cobre o uso real (as opções da tabela não contam) e o contorno é escrever as opções da lista.
TETO_FORA_DA_TABELA = 3


def separar_lancadores(palavras):
    """Tira os prefixos que só repassam o comando (`env`, `sudo`, `nice`, `timeout`, `xargs`...) com as opções
    deles, pela tabela `LANCADORES` (a mesma da recusa), para classificar o comando de verdade; opções do comando
    seguinte não se perdem. Devolve a lista das leituras possíveis, cada uma (comando, atribuições feitas pelos
    lançadores): `env GH_REPO=x gh ...` passa a variável ao `gh` como `GH_REPO=x gh ...`, e o `NOME=valor` misturado às
    opções também. A primeira é a leitura sem valor, que dá a pasta e as variáveis que seguem na linha (ADR 0013, item
    5); as outras só somam recusa. As palavras da tabela têm uma leitura só; o `env -S` por extenso
    (`texto_dividido_do_env`, certo) é dividido, para que a regra específica fale antes da recusa. Para cada palavra
    com `-` fora da tabela, antes do comando, o hook não escolhe qual leitura o lançador instalado faz (nenhuma
    tabela de opções do `env` volta) e lê as possíveis: sem valor (a palavra seguinte segue como opção ou comando); com
    valor (a palavra seguinte é o valor); e, no `env`, com o texto dividido, se a palavra tem o `S` (grupo curto
    `-iS'…'` ou abreviação de `--split-string`): o resto dela, ou a palavra seguinte, é o comando. Texto dividido que
    não fecha aspas: `TextoAbertoComLeituras` (recusa) se uma palavra fora da tabela veio antes, e `TextoDivididoAberto`
    (`ilegivel`) se não; `LancadorDemais`: mais de `TETO_FORA_DA_TABELA` palavras fora da tabela. Anda por índices: só o texto dividido (que põe palavras novas na frente) copia a cauda."""
    saidas = []
    _ler_lancadores(palavras, depois_das_atribuicoes(palavras), [], 0, saidas)
    return saidas


def _ler_lancadores(base, inicio, lancadas, gasto, saidas, meio=None):
    """Anda pela cadeia de lançadores de `base` a partir de `inicio` (ou de `meio`: (lançador, índice, texto dividido) no
    meio das opções de um), junta a leitura que fecha em `saidas` e, depois dela, as que cada palavra fora da tabela
    adiou (com valor, texto dividido): a leitura sem valor sai primeiro. `gasto`: as palavras fora da tabela vistas."""
    adiadas = []
    while meio or (inicio < len(base) and Path(base[inicio]).name in LANCADORES):
        if meio:
            nome, i, dividido = meio
            meio = None
        else:
            nome = Path(base[inicio]).name
            i, dividido = inicio + 1, []
        while i < len(base):
            opcao = base[i]
            if ATRIBUICAO.match(opcao):
                lancadas.append(opcao)
                i += 1
                continue
            if not opcao.startswith("-"):
                break
            i += 1
            if opcao == "--":
                break
            seguinte = base[i] if i < len(base) else ""
            texto = texto_dividido_do_env(opcao, seguinte) if nome == "env" else None
            if texto is not None and texto[2]:  # `-S`, `-Svalor`, `--split-string[=valor]`: o `env` sempre divide
                i += texto[1]
                dividido += _dividir(texto[0], gasto, f"{nome} {opcao}")
                continue
            consome = opcao_modelada(nome, opcao)
            if consome is None:  # fora da tabela: as leituras possíveis, e a sem valor segue aqui
                if gasto >= TETO_FORA_DA_TABELA:
                    raise LancadorDemais(f"{nome} {opcao}")
                gasto += 1
                adiadas.append((base, inicio, list(lancadas), gasto, (nome, i + 1, list(dividido))))  # com valor
                if texto is not None:  # no `env`, o texto dividido que a palavra tem depois do `S`
                    adiadas.append((base, inicio, list(lancadas), gasto,
                                    (nome, i + texto[1], dividido + _dividir(texto[0], gasto, f"{nome} {opcao}"))))
                consome = 0
            i += consome
        if nome == "timeout" and i < len(base):
            i += 1  # a duração
        if dividido:
            base, i = dividido + list(base[i:]), 0
        fim = depois_das_atribuicoes(base, i)
        lancadas += base[i:fim]
        inicio = fim
    leitura = (base[inicio:], lancadas)
    if leitura not in saidas:
        saidas.append(leitura)
    for resto in adiadas:
        _ler_lancadores(*resto[:4], saidas, meio=resto[4])


def _dividir(texto, gasto, achado):
    """O texto dividido do `env` (`shlex.split`). Se ele não fecha aspas: com `gasto` (palavras fora da tabela já vistas)
    acima de 0, há mais de uma leitura e alguma não se lê, e o comando recusa (`TextoAbertoComLeituras`); com 0, a
    leitura é uma só e o `env` não a roda (`TextoDivididoAberto`)."""
    try:
        return shlex.split(texto)
    except ValueError:
        if gasto:
            raise TextoAbertoComLeituras(achado) from None
        raise TextoDivididoAberto(achado) from None


# A palavra de laço ou de condição antes do comando (`do rm …`, `then …`): o comando vem depois dela.
CORPO_DE_LACO = {"do", "then", "else", "elif", "if", "while", "until", "!", "{"}
OPCAO_DE_REAVALIACAO = re.compile(r"-[A-Za-z]*c[A-Za-z]*")  # `-c`, `-ec`, `-lc`: o shell roda o texto do argumento
CONTORNO_DA_REAVALIACAO = ("rode o comando direto, sem eval nem shell com -c, ou a reavaliação e a ação crítica em "
                           "chamadas diferentes do Bash")


SHELLS_DA_REAVALIACAO = SHELLS | {"rbash"}


ACHADO_DO_ENV_S = "env -S"
CONTORNO_DO_ENV_S = "use o env sem -S (`env VAR=x comando`) ou rode o comando direto"
CONTORNO_DO_LANCADOR = ("use o lançador só com as opções da lista, uma por palavra (`env -i -u X comando`, `env VAR=x "
                        "comando`), rode o comando direto ou faça a busca noutra chamada")


class OpcaoDeLancador(str):
    """O achado da opção de lançador que a tabela `LANCADORES` não modela (`env -a`, `sudo -s`): o texto é
    `<lançador> <opção>`."""


def achado_do_lancador(nome, opcao):
    """O nome que `reavaliacao_das_palavras` dá à opção `opcao`, fora da tabela, do lançador `nome`: a opção de dividir
    texto do `env` (o teste do `S` de `texto_dividido_do_env`, o mesmo de `separar_lancadores`: `-S` em qualquer grafia
    ou grupo, `--split-string` e toda abreviação) é `env -S`; o resto, `OpcaoDeLancador`."""
    if nome == "env" and texto_dividido_do_env(opcao, "") is not None:
        return ACHADO_DO_ENV_S
    return OpcaoDeLancador(f"{nome} {opcao}")


def reavaliacao_das_palavras(palavras):
    """ADR 0011, item 2 (opção B da revalidação 9): o comando simples, com as palavras já reduzidas como o bash
    (`reduzida`; None: a palavra não se reduz; `INDECIDIVEL`: tem `$'…'` ou `$"…"`, que o hook não lê), reavalia um texto
    pelo shell? Em qualquer posição: alguma palavra é `eval`, ou um shell de `SHELLS_DA_REAVALIACAO` (pelo nome do
    arquivo) seguido, mais adiante no mesmo comando, de uma opção curta com `c`, ou é `INDECIDIVEL`. Não há lista de
    prefixos: `coproc`, `time`, `find -exec`, `flock f`, `sudo` e o prefixo
    que vier caem pela mesma regra. Um lançador de `LANCADORES`, em qualquer posição, com uma palavra com `-` fora da
    tabela dele antes do comando (`opcao_fora_da_tabela`) também é texto que o hook não lê, e recusa sem lê-lo: `env -S`
    para a opção de dividir texto, `OpcaoDeLancador` para o resto (`env -a`, `sudo -s`). Devolve o nome (`eval`,
    `bash -c`, `env -S`, `env -a`) ou None.
    Linear (bloco T da revalidação 10): uma passada da direita para a esquerda, que guarda se há opção com `c` depois
    de cada palavra; o lançador só lê as opções dele, com memória por (lançador, índice). A passada vai até a esquerda e
    o último achado é o da palavra mais à esquerda."""
    n = len(palavras)
    textos = ["" if p is None or p is INDECIDIVEL else p for p in palavras]  # o `env` lê vazia a palavra que não se lê
    opcao_a_partir = [False] * (n + 1)  # [j]: há opção com `c` em palavras[j:]
    achada, memoria = None, {}
    for k in range(n - 1, -1, -1):
        palavra = palavras[k]
        opcao_a_partir[k] = opcao_a_partir[k + 1] or OPCAO_DE_REAVALIACAO.fullmatch(textos[k]) is not None
        if palavra is None:
            continue
        if palavra is INDECIDIVEL:
            achada = ACHADO_DO_INDECIDIVEL
            continue
        nome = Path(palavra).name
        if palavra == "eval":
            achada = "eval"
        elif nome in SHELLS_DA_REAVALIACAO and opcao_a_partir[k + 1]:
            achada = f"{nome} -c"
        elif nome in LANCADORES:
            fora = opcao_fora_da_tabela(textos, k + 1, nome, memoria)
            if fora is not None:
                achada = achado_do_lancador(nome, fora)
    return achada


def reavaliacao(texto):
    """A primeira reavaliação pelo shell (`reavaliacao_das_palavras`) em algum comando simples do texto, de qualquer
    nível de substituição (`palavras_do_texto`: `$(…)`, crase, `<(…)`), sobre a palavra que o bash recebe (`reduzida`
    do texto como escrito, e não a palavra do `shlex`, que lê `$'eval'` como `$eval`), ou None. `texto`: a linha sem os
    corpos de heredoc. Com o marcador crítico no nível 0, os dois hooks recusam a chamada, haja `<<` ou não: o texto
    reavaliado nunca chega ao leitor, então não importa como o `<<` nasce lá dentro."""
    for simples in palavras_do_texto(texto).simples:
        achada = reavaliacao_das_palavras([reduzida(p.cru) for p in simples.palavras])
        if achada:
            return achada
    return None


# A redução da palavra como o bash (proposta caminho-rev9, seção 1; manual do bash, "Quoting" e "Quote Removal"): a
# palavra que tem só caracteres comuns e os mecanismos de aspas do POSIX tem um valor só, e o hook o calcula sem rodar
# nada: `\` fora de aspas, `'…'` e `"…"` (com `\` antes de `$`, crase, `"`, `\` e quebra de linha). Não há tabela de
# escapes: a palavra com `$'…'` ou `$"…"` fora de aspas é `INDECIDIVEL` (opção C da revalidação 10, RET-LEITURA-HOOK-E), e
# o hook não depende do que a versão do bash faz com cada escape; com o marcador, os dois hooks a recusam. O resto é
# expansão (`$x`, `${…}`, `$(…)`, crase, glob, `{a,b}`, `~`): a palavra não se reduz (None; cartão N-HOOK1, R5).
INDECIDIVEL = object()
ACHADO_DO_INDECIDIVEL = "$'…' ou $\"…\""  # o nome que `reavaliacao_das_palavras` dá à palavra INDECIDIVEL
CONTORNO_DO_INDECIDIVEL = "escreva a palavra entre aspas simples ou duplas, sem $'…' nem $\"…\""
EXPANDE_FORA_DE_ASPAS = frozenset("`*?[{~")  # além do `$`, que `reduzida` olha à parte


def contorno_da_reavaliacao(achada):
    """O contorno que a recusa diz para o que `reavaliacao` achou."""
    if isinstance(achada, OpcaoDeLancador):
        return CONTORNO_DO_LANCADOR
    return {ACHADO_DO_INDECIDIVEL: CONTORNO_DO_INDECIDIVEL, ACHADO_DO_ENV_S: CONTORNO_DO_ENV_S}.get(
        achada, CONTORNO_DA_REAVALIACAO)


def motivo_da_reavaliacao(achada):
    """O porquê que a recusa diz para o que `reavaliacao` achou."""
    if isinstance(achada, OpcaoDeLancador):
        return "opção de lançador que o hook não modela"
    return "o hook não modela o texto que o shell reavalia"


def _resto_com_ansi(cru, i):
    """Depois de uma construção que aninha (`$(`, `${`, crase), o hook não segue mais as aspas da palavra: `$'` ou `$"`
    em qualquer ponto do resto vale como INDECIDIVEL (no máximo recusa um que estava entre aspas); sem eles, a palavra
    não se reduz (None)."""
    return INDECIDIVEL if "$'" in cru[i:] or '$"' in cru[i:] else None


def reduzida(cru):
    """A palavra como o bash a entrega ao programa (a remoção de aspas, sem expansão): o str; None se ela não se reduz
    a literal (expansão, aspas sem par); `INDECIDIVEL` se tem `$'` ou `$"` fora de aspas. Dentro de aspas simples, o `$`
    é literal; dentro de aspas duplas, o `$'` e o `$"` também (o `$` sozinho é expansão)."""
    saida, i, expande = [], 0, False
    while i < len(cru):
        c = cru[i]
        if c == "\\":
            if cru[i + 1:i + 2] != "\n":
                saida.append(cru[i + 1:i + 2] or "\\")
            i += 2
        elif c == "'":
            fim = cru.find("'", i + 1)
            if fim < 0:
                return None
            saida.append(cru[i + 1:fim])
            i = fim + 1
        elif cru.startswith(("$'", '$"'), i):
            return INDECIDIVEL
        elif c == "`" or cru.startswith(("$(", "${"), i):
            return _resto_com_ansi(cru, i)
        elif c == '"':
            i += 1
            while True:
                if i >= len(cru):
                    return None  # aspas sem par
                d = cru[i]
                if d == '"':
                    i += 1
                    break
                if d == "`" or cru.startswith(("$(", "${"), i):
                    return _resto_com_ansi(cru, i)
                if d == "\\" and cru[i + 1:i + 2] in ESCAPES_DAS_DUPLAS:
                    if cru[i + 1] != "\n":
                        saida.append(cru[i + 1])
                    i += 2
                    continue
                expande = expande or d == "$"
                saida.append(d)
                i += 1
        else:
            expande = expande or c == "$" or c in EXPANDE_FORA_DE_ASPAS
            saida.append(c)
            i += 1
    return None if expande else "".join(saida)


def texto_dividido_do_env(opcao, seguinte):
    """(texto, 1 se consumiu a palavra seguinte, certo) do `env` que divide o texto da opção `opcao` e roda o resultado,
    ou None se a palavra não tem o `S`. O teste do `S` é um só, para a leitura (`separar_lancadores`) e para a recusa
    (`achado_do_lancador`): palavra curta com `S` depois do `-` (o resto dela depois do primeiro `S`, ou `seguinte` se o
    resto é vazio) e `--` seguido de um prefixo de `split-string` (o resto depois do `=`, ou `seguinte`). `certo`: o `S`
    é a primeira letra (`-S`, `-Svalor`) ou a longa é inteira (`--split-string`): o `env` sempre divide, e a palavra tem
    uma leitura só; o grupo (`-iS'…'`) e a abreviação são leituras possíveis, e o hook não decide qual vale."""
    if opcao.startswith("--"):
        longa, igual, resto = opcao[2:].partition("=")
        if not longa or not "split-string".startswith(longa):
            return None
        return (resto, 0, longa == "split-string") if igual else (seguinte, 1, longa == "split-string")
    if "S" not in opcao[1:]:
        return None
    resto = opcao[opcao.index("S") + 1:]
    return (resto, 0, opcao[1] == "S") if resto else (seguinte, 1, opcao[1] == "S")


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
    """Saída 2: o Claude Code bloqueia a ferramenta (PreToolUse) ou mostra o motivo (PostToolUse). A decisão já está
    tomada: o vigia de prazo se desarma, para o alarme não trocar a recusa por um prazo vencido."""
    if hasattr(signal, "setitimer"):
        signal.setitimer(signal.ITIMER_REAL, 0)
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
        self.marcado = None  # o texto da ação tem o marcador crítico? None: ainda não se sabe (`marcado`)

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


def marcado(hook, critico, bruto):
    """O texto da ação tem o marcador crítico? Calculado uma vez e guardado em `hook.marcado`: é o primeiro passo da
    decisão, sob o vigia de prazo, e o prazo vencido só recusa com o marcador (`prazo_vencido`)."""
    if hook.marcado is None:
        hook.marcado = critico.search(texto_da_acao(hook, bruto)) is not None
    return hook.marcado


def falhar_fechado(hook, critico, bruto, clone_do_forge=False):
    """ADR 0009, seção 7: em erro interno, bloqueia só se o comando ou o caminho da ação tem marcador crítico e a
    sessão é vigiada (`sessao_vigiada`: pela raiz da sessão, não pela pasta corrente), e nunca depois da
    ferramenta, quando já não há o que impedir."""
    if (critico is None or hook.entrada.get("hook_event_name") == "PostToolUse"
            or not marcado(hook, critico, bruto) or not sessao_vigiada(hook, clone_do_forge)):
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
    if (hook.entrada.get("hook_event_name") != "PostToolUse" and marcado(hook, critico, bruto)
            and versao_sumiu() and not desligado_na_config(hook)):
        bloquear("R-CONFORMIDADE", TEXTO_DA_FALHA[motivo_da_falha()])


# O vigia de prazo (bloco T da revalidação 10): o Claude Code mata o hook aos 10 s (`timeout` de hooks.json) e libera a
# ação, então a decisão de um hook que recusa tem de vir antes. Um alarme do processo (`signal.setitimer`, na thread
# principal) interrompe qualquer passo lento, de hoje ou futuro, inclusive a busca do `re`; com o marcador crítico na
# chamada, o prazo vencido recusa, e sem o marcador nada muda. Não existe no Windows nativo (sem `SIGALRM`): lá a decisão
# fica com os tetos de custo (`excede_o_teto` e o de `DonosDosHeredocs.montar`), sem outro prazo.
PRAZO_DA_DECISAO_S = 3.0


class PrazoVencido(BaseException):
    """O vigia de prazo venceu no meio da decisão. `BaseException`: nenhum `except Exception` do hook a engole."""


def _vencer(signo, quadro):
    raise PrazoVencido()


@contextmanager
def vigia_de_prazo(segundos):
    """Arma o alarme de `segundos` s (None: não arma) e o desarma na saída, por qualquer caminho."""
    if not segundos or not hasattr(signal, "setitimer") or threading.current_thread() is not threading.main_thread():
        yield
        return
    anterior = signal.signal(signal.SIGALRM, _vencer)
    signal.setitimer(signal.ITIMER_REAL, segundos)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, anterior)


def prazo_vencido(hook, critico, bruto, clone_do_forge, regra):
    """O vigia venceu: com o marcador crítico (e `marcado` ainda desconhecido vale como marcado: a busca do próprio
    marcador passou do prazo), numa sessão vigiada e antes da ferramenta, recusa pela `regra` do hook; senão, libera,
    com a linha no erros.log. Roda fora do vigia, e não refaz a busca do marcador."""
    hook.registrar_erro(Aviso(f"prazo de {PRAZO_DA_DECISAO_S:g} s da decisão vencido"))
    if (critico is None or hook.entrada.get("hook_event_name") == "PostToolUse" or hook.marcado is False
            or not sessao_vigiada(hook, clone_do_forge)):
        return
    bloquear(regra, f"o hook não decidiu em {PRAZO_DA_DECISAO_S:g} s a chamada com ação crítica (texto longo ou lento "
                    f"demais, ou um `git` lento): recusa, em vez de deixar o timeout liberá-la. Corrigir: {CONTORNO_DO_TETO}")


def executar(nome, funcao, critico=None, clone_do_forge=False, regra_do_prazo=None):
    """Lê o JSON do stdin, chama `funcao(hook)` e sai com 0; `bloquear` sai com 2. `critico` (regex) liga a falha
    fechada seletiva (`clone_do_forge`: também no clone do Forge); `FORGE_GUARDA_ABERTA=1` no ambiente do processo
    (só o dono) abre a guarda desses hooks. `regra_do_prazo` (a regra que o hook cita ao recusar) liga o vigia de prazo:
    o marcador se calcula primeiro, e a decisão toda roda sob `PRAZO_DA_DECISAO_S`."""
    hook = Hook(nome)
    bruto = sys.stdin.read()
    if critico is not None and os.environ.get("FORGE_GUARDA_ABERTA") == "1":
        sys.exit(0)
    try:
        with vigia_de_prazo(PRAZO_DA_DECISAO_S if regra_do_prazo and critico is not None else None):
            entrada = json.loads(bruto or "{}")
            if isinstance(entrada, dict):
                hook.entrada = entrada
                if critico is not None:
                    marcado(hook, critico, bruto)
                    barrar_sem_versao(hook, critico, bruto)
                funcao(hook)
    except PrazoVencido:
        prazo_vencido(hook, critico, bruto, clone_do_forge, regra_do_prazo)
    except Exception as erro:  # noqa: BLE001 - ADR 0003: erro interno libera e fica no erros.log
        hook.registrar_erro(erro)
        falhar_fechado(hook, critico, bruto, clone_do_forge)
    sys.exit(0)
