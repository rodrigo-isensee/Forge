"""Capacidades que o sandbox dos agentes tira (ENVIO-DO-SANDBOX, correção A; pedido v0457, E11).

No sandbox do Bash (bubblewrap), o root não troca o dono de um arquivo para outro usuário (o uid não está mapeado:
o `chown` dá EINVAL) e o /proc montado é o de outro namespace de pid (`/proc/self` não é o pid do processo; `ps`,
grupo de processo e `/proc/<pid>` leem outros processos). O teste que precisa de uma delas chama
`exigir(self, "chown")` ou `exigir(self, "proc")` logo antes de usá-la:
- capacidade presente: segue;
- falta de fato, detectada aqui, e CI vazio ou ausente: pula, com o motivo e a contagem em stderr;
- falta com CI definido: reprova. No CI nada pula, e o `teto_pulados` de tests/config.json não sobe.
CI definido é `CI` ou `GITHUB_ACTIONS` com qualquer valor não vazio (`CI=false` também), no processo da suíte: o que
ele tinha ao carregar este módulo ou tem na hora da chamada; o ambiente que o teste passa aos filhos não conta.
Só pode chamar `exigir` um teste de `PODEM_PULAR` (lista fechada; o teste estrutural de tests/test_apoio_sandbox.py
reprova a chamada fora dela). Lista que cresce passa por review, parecer de segurança e `afrouxa-regra`.
Afrouxamento listado no fragmento de changelog da branch (diretriz 3 do dono).
"""
import ast
import errno
import functools
import os
import sys
import tempfile
from pathlib import Path

UID_ALHEIO = 65534  # nobody: o mesmo que os testes de dono alheio usam
SINAIS_DE_CI = ("CI", "GITHUB_ACTIONS")
CI_NA_CARGA = frozenset(nome for nome in SINAIS_DE_CI if os.environ.get(nome))  # antes de um teste mexer no ambiente
PODEM_PULAR = frozenset({  # IDs sem o prefixo `tests.`
    "test_atualizar.AtualizarSemPergunta.test_claude_ancestral_com_sim_recusa",
    "test_atualizar.Dentro.test_ancestral_chamado_claude_recusa_mesmo_com_pty_e_sem_variavel",
    "test_atualizar.Dentro.test_o_lancador_dos_testes_nao_esconde_um_claude_abaixo_do_teste",
    "test_hooks.Hooks.test_registro_de_agente_solta_so_com_prova_de_sessao_morta",
    "test_hooks.TravaPesadaEmSegundoPlano.test_c1_sentinela_do_cmdline_nao_sai_e_volta_so_bool",
    "test_hooks.TravaPesadaEmSegundoPlano.test_c4_argv0_absoluto_casa_pelo_nome_sem_pasta",
    "test_hooks.TravaPesadaEmSegundoPlano.test_c4_script_do_shebang_casa_pelo_argv1_e_morto_nao_casa",
    "test_hooks.TravaPesadaEmSegundoPlano.test_c5_cmdline_fora_de_utf8_nao_quebra",
    "test_pre_push_trava.PrePushTrava.test_duracoes_de_outro_dono_nao_e_tocado",
    "test_prepush_so_docs.AncestralMorto.test_kill_9_no_agente_encerra_a_checagem_e_o_hook",
    "test_prepush_so_docs.AncestralMorto.test_pid_reusado_conta_como_ancestral_morto",
    "test_prepush_so_docs.GrupoDaEtapa.test_etapa_em_grupo_proprio_e_saida_repassada",
    "test_prepush_so_docs.GrupoDaEtapa.test_grupo_nao_criado_ou_pgid_ilegivel_sinaliza_so_a_etapa",
    "test_prepush_so_docs.GrupoDaEtapa.test_term_no_hook_encerra_o_grupo_e_poupa_o_irmao",
    "test_prepush_so_docs.LimiteDaEtapa.test_estouro_encerra_com_os_filhos_e_barra",
    "test_prepush_so_docs.TravaDaChecagem.test_pasta_de_outro_dono_recua_ou_e_recusada",
    "test_prepush_so_docs.TravaDaChecagem.test_trava_link_pasta_ou_alheia_recusada",
    "test_testes_tocados.MedidaDaVagaPesada.test_conta_a_pesada_viva_sem_gravar_a_linha_de_comando_dela",
})
pulados = 0


def falta_chown(pasta=None):
    """Motivo se o root não consegue dar um arquivo a outro usuário; None se consegue ou se não é root."""
    if os.geteuid() != 0:
        return None  # quem não é root nem tenta: os testes têm ramo próprio para isso
    with tempfile.TemporaryDirectory(dir=pasta) as tmp:
        alvo = Path(tmp) / "dono"
        alvo.touch()
        try:
            os.chown(alvo, UID_ALHEIO, UID_ALHEIO)
        except OSError as erro:
            if erro.errno != errno.EINVAL:  # só o uid fora do mapa do namespace; EPERM e o resto são erro do teste
                raise
            return f"chown para o uid {UID_ALHEIO} em {tmp} falhou (EINVAL): uid fora do namespace"
    return None


def falta_proc(proc=Path("/proc"), pid=None):
    """Motivo se o /proc não é o do namespace de pid deste processo; None se é."""
    pid = os.getpid() if pid is None else pid
    try:
        visto = os.readlink(proc / "self")
    except OSError as erro:
        return f"sem {proc}/self ({erro.strerror})"
    if visto != str(pid):
        return f"{proc} de outro namespace de pid ({proc}/self={visto}, pid={pid}): ps, grupo e /proc/<pid> não servem"
    return None


SONDAS = {"chown": falta_chown, "proc": falta_proc}


@functools.lru_cache(maxsize=None)
def falta(capacidade):
    """Motivo da falta da capacidade neste processo (sondada uma vez), ou None."""
    if capacidade not in SONDAS:
        raise ValueError(f"capacidade desconhecida: {capacidade!r} (conheço {sorted(SONDAS)})")
    return SONDAS[capacidade]()


def sinais_de_ci():
    """Sinais de CI não vazios do processo da suíte: os da carga deste módulo e os de agora."""
    return sorted(CI_NA_CARGA | {nome for nome in SINAIS_DE_CI if os.environ.get(nome)})


def exigir(teste, capacidade):
    """Segue com a capacidade; sem ela, pula fora do CI (motivo e contagem em stderr) e reprova com CI definido."""
    ident = teste.id().removeprefix("tests.")
    if ident not in PODEM_PULAR:
        teste.fail(f"{ident} chamou exigir fora de PODEM_PULAR (tests/apoio_sandbox.py)")
    motivo = falta(capacidade)
    if motivo is None:
        return
    ci = sinais_de_ci()
    if ci:
        teste.fail(f"falta a capacidade {capacidade!r} com CI definido ({', '.join(ci)}; no CI nada pula): {motivo}")
    global pulados
    pulados += 1
    print(f"sandbox: pulado {pulados} · {teste.id()} · {capacidade}: {motivo}", file=sys.stderr, flush=True)
    teste.skipTest(f"sandbox fora do CI, sem {capacidade}: {motivo}")


# A4: quem confere a lista fechada (tests/test_apoio_sandbox.py, ListaFechada, roda sobre tests/).
def _nome(no):
    return no.id if isinstance(no, ast.Name) else no.attr if isinstance(no, ast.Attribute) else None


def _chama_self(funcao, metodo):
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == metodo
               and _nome(n.func.value) == "self" for n in ast.walk(funcao))


def usos_fora_da_lista(fonte, modulo, lista):
    """(linha, queixa) de cada uso de `exigir` fora de `lista` (A4): só vale `exigir(self, ...)` como comando (no
    máximo dentro de `if`) num método de classe do módulo; num `test_*`, o ID está na lista; noutro método
    (auxiliar, setUp, mixin), todo `test_*` da classe que o chama está na lista e há ao menos um."""
    arvore = ast.parse(fonte)
    pai = {filho: no for no in ast.walk(arvore) for filho in ast.iter_child_nodes(no)}
    queixas = []
    for no in ast.walk(arvore):
        if isinstance(no, ast.alias) and no.name == "exigir" and no.asname not in (None, "exigir"):
            queixas.append((no.lineno, "exigir com outro nome"))
        if isinstance(no, ast.Constant) and no.value == "exigir":
            queixas.append((no.lineno, "exigir por nome em texto"))
        if _nome(no) != "exigir":
            continue
        chamada = pai.get(no)
        comando = pai.get(chamada)
        if not (isinstance(chamada, ast.Call) and chamada.func is no and isinstance(comando, ast.Expr)
                and chamada.args and _nome(chamada.args[0]) == "self"):
            queixas.append((no.lineno, "exigir fora de uma chamada exigir(self, ...) como comando"))
            continue
        funcao = pai.get(comando)
        while isinstance(funcao, ast.If):
            funcao = pai.get(funcao)
        classe = pai.get(funcao)
        if not (isinstance(funcao, ast.FunctionDef) and isinstance(classe, ast.ClassDef)
                and isinstance(pai.get(classe), ast.Module)):
            queixas.append((no.lineno, "exigir fora do corpo de um método de teste ou auxiliar de classe"))
            continue
        if funcao.name.startswith("test_"):
            ids = [f"{modulo}.{classe.name}.{funcao.name}"]
        else:
            ids = [f"{modulo}.{classe.name}.{f.name}" for f in classe.body
                   if isinstance(f, ast.FunctionDef) and f.name.startswith("test_") and _chama_self(f, funcao.name)]
        fora = [i for i in ids if i not in lista]
        if fora or not ids:
            onde = f"{classe.name}.{funcao.name}"
            queixas.append((no.lineno, f"exigir em {onde}, fora de PODEM_PULAR: {fora or 'nenhum teste'}"))
    return queixas


def orfaos(lista, pasta):
    """IDs da lista cujo método não existe ou não chama exigir (direto ou por auxiliar da classe ou de uma base)."""
    sem = []
    for ident in sorted(lista):
        modulo, classe, metodo = ident.split(".")
        arquivo = pasta / f"{modulo}.py"
        classes = {} if not arquivo.exists() else {
            c.name: c for c in ast.parse(arquivo.read_text(encoding="utf-8")).body if isinstance(c, ast.ClassDef)}
        cadeia, nome = [], classe
        while nome in classes and nome not in [c.name for c in cadeia]:
            cadeia.append(classes[nome])
            nome = next((_nome(b) for b in classes[nome].bases), None)
        metodos = {}
        for c in reversed(cadeia):
            metodos.update({g.name: g for g in c.body if isinstance(g, ast.FunctionDef)})
        chamam = {n for n, f in metodos.items()
                  if any(isinstance(x, ast.Call) and _nome(x.func) == "exigir" for x in ast.walk(f))}
        alvo = metodos.get(metodo)
        if alvo is None or not (metodo in chamam or any(_chama_self(alvo, h) for h in chamam)):
            sem.append(ident)
    return sem
