"""Apoio da classe do corpus da volta única (LOTE-LEITURA-HOOK): o corpus, as constantes, o gerador e os auxiliares
que os módulos `tests/test_hooks_volta_*.py` compartilham. Não é módulo de teste (HOOKS-CORPUS-RAPIDO)."""

import concurrent.futures
import contextlib
import functools
import itertools
import json
import os
import re
import shlex
import shutil
import signal
import string
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import RAIZ, ambiente_limpo  # noqa: E402
from test_hooks import (  # noqa: E402,F401  (os módulos test_hooks_volta_* importam daqui)
    FIXTURES,
    Fixture,
    HOOKS,
    Hooks,
    PRAZO_DA_DECISAO_NOS_TESTES,
    PRAZO_DO_CLAUDE_CODE_S,
    PRAZO_GIT_NOS_TESTES,
    modulos_dos_hooks,
    montar_proc,
    rodar,
    texto)


# LOTE-LEITURA-HOOK, volta única (docs/propostas/lote-leitura-hook-volta-unica.md, seções 3 a 5): o corpus das classes
# R, N, S, H, V, L e F nos dois hooks, o oráculo das redireções (T6) e o enumerador de programas (T7). A marca `fecha`
# de um caso é a regra (M1 a M5) em cujo commit ele passa a dar o resultado esperado: até lá o teste exige o resultado
# errado (o vermelho continua provado) e falha se a marca sobra. A classe X do desenho fica fora (cartão N-HOOK1).
CORPUS_VOLTA_UNICA = Path(__file__).resolve().parent / "fixtures" / "heredoc-volta-unica.json"
REGRAS_DA_VOLTA_UNICA = frozenset({"M1", "M2", "M3", "M4", "M5", "D", "A", "B", "B2", "C", "T"})  # D, A, B e B2: as opções (RET-LEITURA-HOOK-D, -A, -B, -C); C e T: a opção C e o bloco T da revalidação 10 (RET-LEITURA-HOOK-E)
EXIGE_NENHUMA_MARCA = True  # passo (7) do desenho e opções D, A, B e B2: todas as regras entraram, nenhuma marca `fecha` sobra
# A marca `nao_promete` (o cartão): a forma está na linha "Não promete" da frase de parada (RET-LEITURA-HOOK-CAMINHO4); a
# célula é o código de hoje, para o conserto futuro aparecer como mudança de teste, e o T9b registra que o bash a roda.
CARTOES_DO_NAO_PROMETE = frozenset({"N-HOOK1", "R5A-COPROC", "A6"})
NAO_PROMETE = "não promete"
MINIMO_POR_CLASSE = {"R": 32, "N": 12, "S": 34, "H": 8, "V": 13, "L": 12, "F": 12}
IDS_DA_VOLTA_UNICA = ("R8", "R9", "R18", "R19a", "R19b", "R19c", "R19d", "R19e", "R20a", "R20b", "R20c", "S5", "S15",
                      "S17a", "S17b", "S17c", "S17d", "S17e", "S17f", "S18a", "S18b", "S18c", "F7a", "F7b", "F8a", "F8b",
                      # opção A (RET-LEITURA-HOOK-A): as sondas da revalidação 7 e os falsos positivos medidos
                      "G1", "G2", "G3", "G3c", "G3d", "G4", "G5", "G6", "G7", "G8", "GL1", "GL2", "GL3", "GL4", "GL5",
                      "GL6", "B1", "B2", "BL1", "HC1", "HC2", "HC3", "HC4", "HC5", "FD9", "FD9b", "FD10", "FD10b", "FD11",
                      "FD11b",
                      # opção B (RET-LEITURA-HOOK-B): as sondas da revalidação 8 e os falsos positivos FD12 e FD13
                      "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "QC1", "QC2", "BL2", "FD12", "FD12b", "FD13a", "FD13b", "FD13c",
                      "FD13d", "FD13e", "QP1",
                      # opção B da revalidação 9 (RET-LEITURA-HOOK-C): as sondas CO, AN, NR, VA, o FD14 e o "não promete"
                      "CO1", "CO2", "CO3", "AN1", "AN2", "AN3", "AN4", "AN5", "NR1", "NR2", "NR3", "VA1", "FD14a",
                      "FD14b", "FD14c", "FD14d", "CO4", "CO5", "CN1", "CN2", "CN3", "VA2", "PE1", "ST1", "ST2", "ST3",
                      # opção C e bloco T da revalidação 10 (RET-LEITURA-HOOK-E): `\x{…}`, `$"…"`, 20 mil palavras e o FD15
                      "AN34", "AN34b", "AN34c", "AN34d", "AN34e", "AN34f", "AN34g", "AN35a", "AN35b", "AN35c", "AN35d",
                      "OT1", "OT2", "FD15a", "FD15b", "FD15c", "FD15d", "FD15e", "FD15f", "FD15g", "FD15h", "FD15i",
                      # A1 da segurança na revalidação 11 (RET-LEITURA-HOOK-E): o lançador que divide texto (`env -S`)
                      *(f"ES{k}" for k in range(1, 18)), "FD16a", "FD16b", "FD16c", "FD16d")


def corpus_da_volta_unica():
    """O corpus, com `{REPETE:<texto>:<n>}` no `comando` trocado pelo texto repetido n vezes (a sonda de 20 mil
    palavras não cabe escrita no JSON)."""
    texto = re.sub(r"\{REPETE:([^:}]+):(\d+)\}", lambda m: m.group(1) * int(m.group(2)),
                   CORPUS_VOLTA_UNICA.read_text(encoding="utf-8"))
    return json.loads(texto)


class BaseVoltaUnica:
    """A base do corpus da volta única: o que os testes dos módulos `test_hooks_volta_*` usam (era a classe
    `CorpusHeredocVoltaUnica`). Os casos de `tests/fixtures/heredoc-volta-unica.json`, cada um no modelo de fixture do hook (`modelos`), com
    `{CORPO}` trocado pela linha crítica dele (`corpos`). Em cada caso, o código esperado por hook (`null`: a célula não
    roda) e a marca `fecha`: a regra, ou `{hook: regra}` quando o outro hook já dá o esperado (pelo item 2 da ADR 0011,
    por exemplo). `passos` são chamadas anteriores do Bash, a última é a principal."""
    executar_em_lote = Hooks.executar_em_lote
    _pasta_temporaria = Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(Hooks.depende_de_pid_ou_trava)

    def conferir_marca(self, fecha, passou, saida):
        """Sem marca, o caso tem de passar; com marca, tem de falhar (a regra da marca ainda não entrou)."""
        if fecha:
            self.assertIn(fecha, REGRAS_DA_VOLTA_UNICA)
            self.assertFalse(passou, f"marca sobrando: o caso já passa; tire a marca {fecha} neste commit ({saida})")
        else:
            self.assertTrue(passou, saida)

    def executar_fixture(self, f, tmp, outro_pid, montado=None):
        raiz, entrada = montado or f.montar(tmp, outro_pid)
        proc = montar_proc(tmp, None)
        extra = {"FORGE_NPROC": "8"}
        f.executar_passos(raiz, lambda e: rodar(f.hook, e, raiz, proc, extra))
        r = rodar(f.hook, entrada, raiz, proc, extra, como_o_claude_code=bool(f.dados.get("prazo_de_producao")))
        codigo = f.dados["esperado"]["codigo"]
        if codigo == 0:
            passou = r.returncode == 0 and r.stderr == ""
        else:
            passou = r.returncode == codigo and re.match(r"^R-[A-Z]+: ", r.stderr) is not None
        self.conferir_marca(f.dados.get("fecha"), passou, f"código {r.returncode}: {r.stderr.strip()}")

    def fixtures_do_corpus(self):
        dados = corpus_da_volta_unica()
        fixtures = []
        for caso in dados["casos"]:
            for hook, modelo in dados["modelos"].items():
                if caso[hook] is None:
                    continue
                caminho = FIXTURES / hook / f"{modelo}.json"
                base = json.loads(caminho.read_text(encoding="utf-8"))
                comandos = [c.replace("{CORPO}", dados["corpos"][hook]) for c in caso.get("passos", [caso.get("comando")])]

                def entrada(comando):
                    e = json.loads(json.dumps(base["entrada"]))
                    e["tool_input"]["command"] = comando
                    return e

                base["passos"] = [{"entrada": entrada(c)} for c in comandos[:-1]]
                base["entrada"] = entrada(comandos[-1])
                base["esperado"] = {"codigo": caso[hook]}
                if caso.get("prazo_de_producao"):  # a decisão tem de vir antes do timeout do Claude Code (bloco T)
                    base["prazo_de_producao"] = True
                fecha = caso.get("fecha")  # a regra, ou {hook: regra} quando só um dos hooks ainda falha
                fecha = fecha.get(hook) if isinstance(fecha, dict) else fecha
                if fecha:
                    base["fecha"] = fecha
                fixtures.append((f"{hook}/{caso['id']}", Fixture(caminho, base)))
        return fixtures

    # T8 e T9 (opções D e A): as zonas do texto saem de uma varredura própria, sem `_comum.heredocs` nem o leitor do hook.
    K3_DO_TESTE = re.compile(r"\"\$\(cat[ \t]+<<'(\w+)'\n(.*?\n)?\1\n\)\"", re.S)
    LINHAS_QUE_FECHAM = ("{X})", "{X} )", "{X} x)", "{X};)", "{X}foo")  # o bash 5.3 fecha as quatro primeiras em `$(`
    TROCAS_DE_PALAVRA = ("-c", "--config-env=core.fsmonitor=X", "--exec-path=/tmp/x", "sh")

    @classmethod
    def heredocs_do_teste(cls, texto):
        """Os heredocs `<<'X'` de um caso L, sem o hook: (início do operador, fim do operador, início do corpo, depois da
        linha do delimitador, delimitador). Os casos L têm um heredoc por linha e o corpo acaba na linha igual a X."""
        achados = []
        for m in re.finditer(r"<<'(\w+)'", texto):
            corpo = texto.index("\n", m.end()) + 1
            fim = re.compile(rf"^{m[1]}(?:\n|$)", re.M).search(texto, corpo)
            achados.append((m.start(), m.end(), corpo, fim.start(), min(fim.end(), len(texto)), m[1]))
        assert len(achados) == texto.count("<<"), texto
        return achados

    @classmethod
    def zonas_do_teste(cls, texto):
        """A zona de cada ponto de inserção (0 a len): corpo, k (recusa sempre), simples, duplas ou fora."""
        zona = [None] * (len(texto) + 1)
        for operador, fim_do_operador, corpo, _, fim, _ in cls.heredocs_do_teste(texto):
            for i in range(operador + 1, fim_do_operador):
                zona[i] = "k"
            for i in range(corpo, fim + 1):
                zona[i] = "corpo"
        for m in cls.K3_DO_TESTE.finditer(texto):
            for i in range(m.start() + 1, m.end()):
                zona[i] = zona[i] or "k"
        estado = "fora"
        for i, c in enumerate(texto):
            zona[i] = zona[i] or estado
            if zona[i] in ("corpo", "k"):
                continue
            if c == "'" and estado != "duplas":
                estado = "fora" if estado == "simples" else "simples"
            elif c == '"' and estado != "simples":
                estado = "fora" if estado == "duplas" else "duplas"
        zona[len(texto)] = zona[len(texto)] or estado
        return zona

    def casos_aceitos(self, corpos=None):
        """(id, hook, texto) de cada caso L com heredoc que a gramática aceita, com o corpo de cada hook (`corpos`, ou os
        do corpus)."""
        _comum, _, _ = modulos_dos_hooks()
        dados = corpus_da_volta_unica()
        aceitos = []
        for caso in dados["casos"]:
            if caso["classe"] != "L" or "comando" not in caso:
                continue
            for hook, corpo in (corpos or dados["corpos"]).items():
                texto = caso["comando"].replace("{CORPO}", corpo)
                if caso[hook] == 0 and isinstance(_comum.gramatica_com_heredoc(texto), _comum.Gramatica):
                    aceitos.append((caso["id"], hook, texto))
        return aceitos

    # T8 por nível (seção 3 da proposta caminho-rev8): o texto do nível 1 dentro de cada reavaliação que o hook segue,
    # escrito para o nível 0, e o `<<` dele em cada forma que o nível 0 apaga até `<<` (`HEREDOC_DO_TESTE`). Só o T8 a usa:
    # no T9b e na propriedade da opção B, G1 (`textos_de_g1`) a substitui (RET-LEITURA-HOOK-C).
    NIVEIS = (("eval '{}'", "simples"), ('eval "{}"', "duplas"), ("eval {}", "sem aspas"), ("bash -c '{}'", "simples"),
              ('sh -c "{}"', "duplas"), ("env X=1 bash -c '{}'", "simples"), ("command eval '{}'", "simples"))
    FORMAS_DO_HEREDOC = ("<<", "<''<", '<""<', "\\<\\<", "<\\\n<", "<'\\''<", "<$(:)<")
    HEREDOC_DO_TESTE = re.compile(r"<(?:['\"\\]|\\\n|\$\([^()]*\))*<")  # o que o bash pode juntar em `<<` num nível de cima

    @staticmethod
    def para_o_nivel_0(texto, aspas):
        """O texto que o nível 0 entrega ao `eval`/`bash -c` como `texto`: entre aspas simples, duplas ou sem aspas (cada
        sinal com `\\`, a quebra de linha entre aspas duplas, como no Q4)."""
        if aspas == "simples":
            return texto.replace("'", "'\\''")
        if aspas == "duplas":
            return re.sub(r'([\\"$`])', r"\\\1", texto)
        return "".join(c if re.fullmatch(r"[\w./:=@,+%^-]", c) else '"\n"' if c == "\n" else "\\" + c for c in texto)

    @classmethod
    def mutacoes_de_nivel(cls, texto):
        """(rótulo, texto do nível 0) do caso dentro de cada reavaliação de `NIVEIS`, com o `<<` em cada forma de
        `FORMAS_DO_HEREDOC` (sem aspas, só a forma `\\<\\<` da própria escrita)."""
        saida = []
        for nivel, aspas in cls.NIVEIS:
            escrito = cls.para_o_nivel_0(texto, aspas)
            formas = ("\\<\\<",) if aspas == "sem aspas" else cls.FORMAS_DO_HEREDOC
            for forma in formas:
                na_forma = escrito if aspas == "sem aspas" else escrito.replace("<<", forma)
                saida.append((f"{nivel.format('…')} {forma!r}", nivel.format(na_forma)))
        return saida

    def mutacoes_de_palavra(self):
        """T8 por palavra: (rótulo, texto com a palavra simples, texto com a mesma palavra entre aspas). Cada palavra
        fora de aspas, de corpo e das formas K, e cada troca de `TROCAS_DE_PALAVRA` no lugar dela, em `'…'`, `"…"` e
        partida (`-'c'`): o bash entrega ao programa a mesma palavra."""
        saida = []
        for id, hook, texto in self.casos_aceitos():
            zona = self.zonas_do_teste(texto)
            for m in re.finditer(r"[\w./:=@,+%~^-]+", texto):
                antes, depois = texto[m.start() - 1:m.start()], texto[m.end():m.end() + 1]
                if any(zona[i] != "fora" for i in range(m.start(), m.end() + 1)) or antes not in ("", " ", "\n", ";", "&") \
                        or depois not in ("", " ", "\n", ";", "&"):
                    continue
                for troca in (m[0],) + self.TROCAS_DE_PALAVRA:
                    simples = texto[:m.start()] + troca + texto[m.end():]
                    for aspas in (f"'{troca}'", f'"{troca}"', f"{troca[0]}'{troca[1:]}'" if len(troca) > 1 else None):
                        if aspas:
                            saida.append((f"{id}/{hook}: {m[0]!r} -> {aspas!r}", simples,
                                          texto[:m.start()] + aspas + texto[m.end():]))
        return saida

    REGISTRADOR = """#!{bash}
e=
while IFS= read -r l; do e+="$l"$'\\n'; done
e+="$l"
{{ printf '%s\\037' "${{0##*/}}" "$@"; printf '\\035%s\\036' "$e"; }} >> "$REG"
[[ ${{0##*/}} == cat ]] && printf '%s' "$e"
exit 0
"""
    EMBUTIDOS = frozenset({"cd", "echo", "true"})  # da lista da gramática, o bash os roda sem processo

    @classmethod
    def esperado_no_bash(cls, lida, pasta):
        """A sequência (programa, argumentos, entrada) que o bash tem de rodar para o que a gramática aceitou: os comandos
        simples sem aspas, na ordem, cada `"$(cat <<'X'…)"` antes do comando dele (um `cat` com o corpo na entrada, e o
        corpo sem as quebras do fim no lugar da palavra), o corpo de `-F - <<'X'` na entrada do `git`, e o `cat` da K1.
        Os embutidos não abrem processo; as pastas de `cd` são criadas em `pasta`. None se um `cd` sai da pasta ou leva
        opção (o bash para a lista no `cd` que falha)."""
        _comum, _, _ = modulos_dos_hooks()
        if lida.k1:
            return [("cat", [], lida.corpos[0])]
        eventos, corpos, atual = [], iter(lida.corpos), Path(pasta)
        for palavras in lida.comandos:
            argumentos, entrada = [], ""
            for palavra in palavras:
                if palavra == _comum.OPERADOR_K:
                    entrada = next(corpos)
                elif palavra == _comum.PALAVRA_K3:
                    corpo = next(corpos)
                    eventos.append(("cat", [], corpo))
                    argumentos.append(corpo.rstrip("\n"))
                else:
                    argumentos.append(palavra)
            if argumentos[0] == "cd":
                if len(argumentos) != 2 or argumentos[1].startswith(("/", "-")) or ".." in argumentos[1].split("/"):
                    return None
                atual = atual / argumentos[1]
                atual.mkdir(parents=True, exist_ok=True)
            if argumentos[0] not in cls.EMBUTIDOS:
                eventos.append((argumentos[0], argumentos[1:], entrada))
        return eventos

    # T9b (seção 3 da proposta caminho-rev8): o oráculo do gatilho. O T9 só roda o que a gramática aceitou; aqui entra o
    # que o hook libera, com a linha sentinela no `{CORPO}`.
    SENTINELAS = {"conformidade": "git push origin SENTINELA:main", "parecer": "gh pr merge SENTINELA --merge"}
    SHELLS_DO_T9B = ("bash", "sh", "dash", "zsh", "ksh", "rbash")  # no `PATH` do T9b, o próprio bash: a reavaliação roda
    # Os prefixos que só repassam o comando, no T9b, sem o programa real (R3 da segurança, revalidação 9): o resto roda.
    REPASSADORES_DO_T9B = {
        "sudo": 'while [[ $1 == -* ]]; do shift; done\nexec "$@"\n',
        "nohup": 'exec "$@"\n',
        "nice": '[[ $1 == -n ]] && shift 2\nexec "$@"\n',
        "timeout": 'shift\nexec "$@"\n',
        "flock": 'while [[ $1 == -* ]]; do shift; done\nshift\nexec "$@"\n',
        "find": ('while [[ $# -gt 0 && $1 != -exec ]]; do shift; done\nshift\na=()\n'
                 'while [[ $# -gt 0 && $1 != ";" ]]; do a+=("${1//\\{\\}/.}"); shift; done\nexec "${a[@]}"\n'),
    }
    DECISOES = {}  # (hook, texto) -> código, de `decisoes_dos_hooks`
    DECIDIDOS = {}  # teste -> quantos textos distintos ele pediu a `decisoes_dos_hooks`

    def modelos_montados(self):
        """{hook: (raiz, entrada, proc)}: um repositório por hook, no modelo do corpus, montado uma vez."""
        montados = {}
        for hook, modelo in corpus_da_volta_unica()["modelos"].items():
            caminho = FIXTURES / hook / f"{modelo}.json"
            base = json.loads(caminho.read_text(encoding="utf-8"))
            base["passos"] = []
            tmp = self._pasta_temporaria()
            raiz, entrada = Fixture(caminho, base).montar(tmp, os.getpid())
            montados[hook] = (raiz, entrada, montar_proc(tmp, None))
        return montados

    def decidir_com_prazo(self, montados, hook, texto, **como):
        """(código, stderr, segundos) do hook real sobre `texto`, no modelo do corpus, com o vigia de produção."""
        raiz, entrada, proc = montados[hook]
        entrada = json.loads(json.dumps(entrada))
        entrada["tool_input"]["command"] = texto
        inicio = time.monotonic()
        r = rodar(hook, entrada, raiz, proc, {"FORGE_NPROC": "8"}, producao=True, **como)
        return r.returncode, r.stderr, time.monotonic() - inicio

    # A decisão dos hooks em lote (HOOKS-CORPUS-RAPIDO): um subprocesso por fatia de textos, e não um por texto. O filho
    # importa os dois hooks uma vez e, para cada texto, chama `_comum.executar` com os mesmos argumentos do `__main__`
    # de cada hook (stdin com a entrada, `SystemExit` com o código), no mesmo ambiente que `rodar` monta. O teste
    # `test_decisao_em_lote_igual_ao_subprocesso_do_hook` prova, numa amostra fixa, que o lote decide como o hook real.
    DRIVER_DOS_HOOKS = """
import contextlib, io, json, os, sys
dados = json.loads(sys.stdin.read())
sys.path.insert(0, dados["hooks"])
import _comum, conformidade, parecer
_comum.forge_check().GIT_TIMEOUT_S = dados["prazo_git"]
_comum.PRAZO_DA_DECISAO_S = float(dados["prazo_da_decisao"])
EXECUCAO = {"conformidade": (conformidade, {"regra_do_prazo": "R-CONFORMIDADE"}),
            "parecer": (parecer, {"clone_do_forge": True, "regra_do_prazo": "R-REVIEW"})}
saida = []
for hook, texto in dados["pedidos"]:
    modulo, argumentos = EXECUCAO[hook]
    os.chdir(dados["raizes"][hook])
    os.environ["FORGE_PROC"] = dados["procs"][hook]
    entrada = json.loads(json.dumps(dados["entradas"][hook]))
    entrada["tool_input"]["command"] = texto
    sys.stdin, codigo = io.StringIO(json.dumps(entrada)), None
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
        try:
            _comum.executar(hook, modulo.principal, modulo.CRITICO, **argumentos)
        except SystemExit as saiu:
            codigo = saiu.code
    saida.append(0 if codigo is None else codigo)
print(json.dumps(saida))
"""
    TEXTO_DO_PRAZO_DO_CLAUDE_CODE = 50_000  # texto maior que isto vale como o Claude Code o trata: passou de 10 s, liberou

    def decidir_em_lote(self, pedidos, montados=None):
        """[código] de cada (hook, texto) de `pedidos`, num subprocesso só (o que o hook dá com `_comum.executar`), sobre
        o modelo do corpus. Os textos de dezenas de KB não vão no lote: vão pelo subprocesso do hook, com o prazo de 10 s."""
        montados = montados or self.modelos_montados()
        env = ambiente_limpo()
        env.pop("FORGE_GUARDA_ABERTA", None)
        env.pop("FORGE_CARGA_LIVRE", None)
        env.update(FORGE_NPROC="8")
        dados = {"hooks": str(HOOKS), "raizes": {h: str(montados[h][0]) for h in montados},
                 "procs": {h: str(montados[h][2]) for h in montados}, "pedidos": [list(p) for p in pedidos],
                 "entradas": {hook: montados[hook][1] for hook in ("conformidade", "parecer")},
                 "prazo_git": PRAZO_GIT_NOS_TESTES, "prazo_da_decisao": PRAZO_DA_DECISAO_NOS_TESTES}
        r = subprocess.run([sys.executable, "-c", self.DRIVER_DOS_HOOKS], input=json.dumps(dados), cwd=montados["conformidade"][0], env=env,
                           capture_output=True, text=True, timeout=900)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        codigos = json.loads(r.stdout.splitlines()[-1])
        self.assertEqual(len(codigos), len(pedidos))
        return codigos

    def decisoes_dos_hooks(self, pedidos):
        """{(hook, texto): código} de cada hook, no modelo do corpus (um repositório por hook, montado uma vez), em
        lotes, em paralelo. O hook cujo marcador (`CRITICO`) o texto não tem não roda: ele libera sem ler (0). Os códigos
        ficam em `DECISOES`, da classe: o T9b e a propriedade da opção B leem os mesmos textos. `DECIDIDOS` conta os
        textos que cada chamada decidiu de fato (com o hook ou com o marcador que o libera)."""
        _comum, conformidade, parecer = modulos_dos_hooks()
        criticos = {"conformidade": conformidade.CRITICO, "parecer": parecer.CRITICO}
        faltam = [pedido for pedido in dict.fromkeys(pedidos) if pedido not in self.DECISOES]
        liberados = [p for p in faltam if not criticos[p[0]].search(p[1])]
        self.DECISOES.update({p: 0 for p in liberados})
        a_rodar = [p for p in faltam if criticos[p[0]].search(p[1])]
        grandes = [p for p in a_rodar if len(p[1]) > self.TEXTO_DO_PRAZO_DO_CLAUDE_CODE]
        em_lote = [p for p in a_rodar if len(p[1]) <= self.TEXTO_DO_PRAZO_DO_CLAUDE_CODE]
        montados = self.modelos_montados()
        trabalhadores = max(1, min(4, (os.cpu_count() or 2) // 2))
        fatias = [em_lote[i::trabalhadores] for i in range(trabalhadores) if em_lote[i::trabalhadores]]
        with concurrent.futures.ThreadPoolExecutor(max_workers=trabalhadores) as pool:
            for fatia, codigos in zip(fatias, pool.map(lambda f: self.decidir_em_lote(f, montados), fatias)):
                self.DECISOES.update(zip(fatia, codigos))
        for hook, texto in grandes:  # a sonda de tempo: passou de 10 s, o Claude Code liberou
            raiz, entrada, proc = montados[hook]
            entrada = json.loads(json.dumps(entrada))
            entrada["tool_input"]["command"] = texto
            self.DECISOES[(hook, texto)] = rodar(hook, entrada, raiz, proc, {"FORGE_NPROC": "8"},
                                                 como_o_claude_code=True).returncode
        self.DECIDIDOS[self._testMethodName] = len(set(pedidos))
        return {pedido: self.DECISOES[pedido] for pedido in pedidos}

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def env_gnu():
        """O caminho do `env` que divide o valor separado do `-S` como o GNU (`-S 'echo a  b'`), ou None: o gerador da
        dimensão "lançador que divide texto" usa essa forma. O uutils 0.8.0 divide o `-S` colado (`-S'…'`), também
        depois de `NOME=valor`, de `-` e de `-f`, mas não o valor separado. Programa local, sem rede (R-CUSTO)."""
        for nome in ("env", "gnuenv", "genv"):
            caminho = shutil.which(nome)
            if caminho and " " not in caminho:
                r = subprocess.run([caminho, "-S", "echo a  b"], capture_output=True, text=True, timeout=10,
                                   stdin=subprocess.DEVNULL)
                if r.returncode == 0 and r.stdout == "a b\n":
                    return caminho
        return None

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def envs_da_maquina():
        """Os caminhos de cada `env` desta máquina (GNU, uutils, …: `env`, `gnuenv` e `genv` no `PATH`, um por arquivo
        real), que rodam `env X=1 printf`. O T9b roda o corpus com cada um, e a recusa não depende de qual está
        instalado (opção A da proposta caminho-rev12). Programas locais, sem rede (R-CUSTO)."""
        achados = {}
        for nome in ("env", "gnuenv", "genv"):
            caminho = shutil.which(nome)
            if caminho and " " not in caminho and os.path.realpath(caminho) not in achados:
                r = subprocess.run([caminho, "X=1", "printf", "%s", "ok"], capture_output=True, text=True, timeout=10,
                                   stdin=subprocess.DEVNULL)
                if r.returncode == 0 and r.stdout == "ok":
                    achados[os.path.realpath(caminho)] = caminho
        return tuple(achados.values())

    def montar_registradores_do_t9b(self, bash, texto, base, env_real=None):
        """Monta a pasta do T9b para o texto (RET-LEITURA-HOOK-F, caminho 1 da proposta caminho-rev12): `HOME` e a
        pasta em `base`, no `$TMPDIR`, com registradores no `PATH` e em `base/x0` (o `PATH` que o Z1 monta:
        `PATH=<base>/x$(( cat ))`), onde o `cat` roda a entrada como o bash (o B1 da revalidação 7). Os shells são o
        próprio bash, e o `env` é `env_real` (o GNU, se None e se houver). Grava e dá `chmod`: roda antes de qualquer pool
        (`rodar_em_paralelo_no_t9b`), porque o executável gravado por uma thread enquanto outra faz `fork` sai com
        `ETXTBSY` (bug `lote-leitura-hook-1`)."""
        env_real = env_real or self.env_gnu()
        registradores, pasta, casa, z1 = base / "bin", base / "pasta", base / "casa", base / "x0"
        for d in (registradores, pasta, casa, z1):
            d.mkdir(parents=True)
        # os shells e os repassadores entram sempre: a grafia do nome (`b''ash`, `$'\x62'ash`) não o mostra no texto
        nomes = set(re.findall(r"[A-Za-z_][\w.+-]*", texto)) | {"cat", "git", "gh", "mkdir", "env"}
        for nome in nomes | set(self.SHELLS_DO_T9B) | set(self.REPASSADORES_DO_T9B):
            for d in (registradores, z1):
                arquivo = d / nome
                if nome in self.SHELLS_DO_T9B:
                    arquivo.write_text(f'#!{bash}\nexec {bash} --noprofile --norc "$@"\n', encoding="utf-8")
                elif nome in self.REPASSADORES_DO_T9B:
                    arquivo.write_text(f"#!{bash}\n{self.REPASSADORES_DO_T9B[nome]}", encoding="utf-8")
                elif nome == "env" and env_real:  # o `env` real: divide o `-S` como o bash vai ver
                    arquivo.write_text(f'#!{bash}\nexec {env_real} "$@"\n', encoding="utf-8")
                elif nome == "env":  # sem `env` real: o `env X=1 prog`, sem o `-S`
                    arquivo.write_text(f'#!{bash}\nwhile [[ $1 == *=* ]]; do export "$1"; shift; done\nexec "$@"\n',
                                       encoding="utf-8")
                elif nome == "cat" and d == z1:
                    arquivo.write_text(f"#!{bash}\nexec {bash} --noprofile --norc -s\n", encoding="utf-8")
                else:
                    arquivo.write_text(self.REGISTRADOR.format(bash=bash), encoding="utf-8")
                arquivo.chmod(0o755)

    def rodar_no_bash_do_t9b(self, bash, texto, base):
        """Roda o texto como no T9 (`env -i bash --noprofile --norc -c`, sem rede) na pasta que
        `montar_registradores_do_t9b` montou em `base`, sem gravar nada. Devolve os (programa, argumentos) gravados.
        O bash que não consegue rodar um registrador (rc 126 ou "Text file busy" no stderr) é falha do arnês, e não do
        gerador: o teste falha com a causa e o stderr, sem repetir. Nenhum programa real além do bash (R-CUSTO)."""
        registradores, pasta, registro, casa = base / "bin", base / "pasta", base / "registro", base / "casa"
        r = subprocess.run([bash, "--noprofile", "--norc", "-c", texto], cwd=pasta, stdin=subprocess.DEVNULL,
                           env={"PATH": str(registradores), "REG": str(registro), "HOME": str(casa)}, capture_output=True,
                           text=True, timeout=10)
        if r.returncode == 126 or "Text file busy" in r.stderr:
            raise AssertionError(f"falha do arnês, não do gerador: o bash não rodou um registrador (rc {r.returncode}) "
                                 f"em {texto!r}; stderr: {r.stderr.strip()}")
        gravado = registro.read_text(encoding="utf-8") if registro.exists() else ""
        rodou = []
        for item in gravado.split("\036")[:-1]:
            argv = item.split("\035", 1)[0].split("\037")[:-1]
            rodou.append((argv[0], argv[1:]))
        return rodou

    def rodar_em_paralelo_no_t9b(self, bash, itens):
        """Os (programa, argumentos) gravados de cada (texto, pasta) de `itens`, na ordem: monta todas as pastas na
        thread principal, antes de abrir o pool, e só então roda em paralelo (nenhum descritor de escrita fica aberto
        durante um `fork`)."""
        itens = list(itens)
        for texto, base in itens:
            self.montar_registradores_do_t9b(bash, texto, base)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(4, (os.cpu_count() or 2) // 2))) as pool:
            return list(pool.map(lambda item: self.rodar_no_bash_do_t9b(bash, *item), itens))

    def textos_do_t9b(self, base):
        """(rótulo, hook, texto, pasta, marca) dos textos do corpus com `{CORPO}` (a sentinela do hook no lugar, e
        `/tmp/x` do Z1 numa pasta de `base`) e dos textos de G1 com a sentinela (`textos_de_g1`, RET-LEITURA-HOOK-C: G1
        substitui as mutações de `NIVEIS`)."""
        dados = corpus_da_volta_unica()
        textos = []
        for caso in dados["casos"]:
            if "{CORPO}" not in caso.get("comando", ""):
                continue
            for hook, sentinela in self.SENTINELAS.items():
                if caso[hook] is None:
                    continue
                pasta = base / f"{caso['id']}-{hook}"
                marca = caso.get("fecha")
                marca = marca.get(hook) if isinstance(marca, dict) else marca
                marca = NAO_PROMETE if caso.get("nao_promete") else marca
                texto = caso["comando"].replace("{CORPO}", sentinela).replace("/tmp/x", f"{pasta}/x")
                textos.append((f"{caso['id']}/{hook}", hook, texto, pasta, marca))
        for k, (rotulo, hook, texto, _) in enumerate(self.textos_de_g1(self.SENTINELAS)):
            textos.append((rotulo, hook, texto, base / f"g1-{k}", None))
        for k, (rotulo, hook, texto, _) in enumerate(self.textos_da_divisao(self.SENTINELAS) if self.env_gnu() else ()):
            textos.append((rotulo, hook, texto, base / f"dv-{k}", None))
        return textos

    # G1, o gerador da classe "nível" (proposta caminho-rev9, 3B): o texto com uma reavaliação pelo shell, por produto
    # de prefixos × grafias (`GRAFIAS`, no nome e na opção) × reavaliadores × corpos. A verdade vem da construção: o
    # teste pôs a reavaliação ali, e `test_g1_esta_na_classe` prova no bash (hooks desligados) que ela roda o corpo.
    # Prefixo: (nome, molde com `{R}` no lugar da reavaliação, nativo, para quem). Nativo: o bash o executa sozinho
    # (palavra reservada, builtin), e o texto entra na prova de G1. Para quem: "eval", "shell" ou None (os dois); o que
    # só repassa a um programa (`env`, `sudo`, `find -exec`) não roda o builtin `eval`. O `xprefixo` (programa
    # desconhecido) só prova a regra do hook: no T9b, é um registrador (S6 da proposta).
    PREFIXOS_DE_G1 = (
        ("nenhum", "{R}", True, None),
        ("coproc", "coproc {R}", True, None),
        ("coproc NOME {", "coproc x { {R}; }", True, None),
        ("time", "time {R}", True, None),
        ("time -p", "time -p {R}", True, None),
        ("!", "! {R}", True, None),
        ("if", "if {R}; then :; fi", True, None),
        ("{", "{ {R}; }", True, None),
        ("$(…)", "x=$({R})", True, None),
        ("pipeline", "true | {R}", True, None),
        ("command", "command {R}", True, None),
        ("builtin", "builtin {R}", True, "eval"),
        ("exec", "exec {R}", True, "shell"),
        ("env X=1", "env X=1 {R}", False, "shell"),
        ("sudo", "sudo {R}", False, "shell"),
        ("flock f", "flock f {R}", False, "shell"),
        ("find -exec", "find . -maxdepth 0 -exec {R} \\;", False, "shell"),
        ("xprefixo", "xprefixo {R}", False, None),
    )
    GRAFIAS_DE_G1 = ("direta", "simples", "duplas", "barra", "ansi", "hexa", "ansi no meio", "vazio no meio")
    REAVALIADORES_DE_G1 = (("eval", None), ("bash", "-c"), ("sh", "-c"), ("zsh", "-c"), ("dash", "-c"), ("ksh", "-c"),
                           ("rbash", "-c"), ("bash", "-ec"), ("bash", "-lc"))
    LINHAS_DIRETAS = {"conformidade": "git push origin feature/x",
                      "parecer": "gh pr create --draft --base develop --title t --body x"}

    @classmethod
    def textos_de_g1(cls, corpos_por_hook, so_nativos=False):
        """(rótulo, hook, texto, nativo) de G1 com o corpo de cada hook (`corpos_por_hook`: hook -> linha), entre aspas
        simples como argumento da reavaliação. A grafia vale para o nome e para a opção do shell."""
        saida = []
        for prefixo, molde, nativo, para in cls.PREFIXOS_DE_G1:
            if so_nativos and not nativo:
                continue
            for grafia in cls.GRAFIAS_DE_G1:
                escrever = cls.GRAFIAS[grafia]
                for nome, opcao in cls.REAVALIADORES_DE_G1:
                    if para and para != ("eval" if opcao is None else "shell"):
                        continue
                    reavaliador = escrever(nome) + (f" {escrever(opcao)}" if opcao else "")
                    for hook, corpo in corpos_por_hook.items():
                        texto = molde.replace("{R}", f"{reavaliador} '{corpo}'")
                        rotulo = f"G1 {prefixo} / {grafia} / {nome}{' ' + opcao if opcao else ''} / {hook}"
                        saida.append((rotulo, hook, texto, nativo))
        return saida

    # A dimensão "lançador que divide texto" de G1 (A1 da segurança, revalidação 11): o `env` com a opção de dividir
    # (`-S`, `-S` colado, `-vS`, `--split-string` com e sem `=`, e as abreviações `--split`, `--spl=` e `--s`) × o
    # separador das palavras do valor (espaço e `\_`) × o lado do `-c` (dentro do valor ou depois dele) × o shell × o
    # que vem antes do shell dentro do valor × o molde. A verdade vem da construção: `test_divisao_esta_na_classe` prova,
    # com o `env` GNU e os hooks desligados, que o bash roda a sentinela em cada texto.
    OPCOES_DE_DIVISAO = {"-S": "-S '{V}'", "-S colado": "-S'{V}'", "-vS": "-vS '{V}'", "-u X -S": "-u X -S '{V}'",
                         "--split-string": "--split-string '{V}'", "--split-string=": "--split-string='{V}'",
                         "--split": "--split '{V}'", "--spl=": "--spl='{V}'", "--s": "--s '{V}'"}
    SEPARADORES_DE_DIVISAO = {"espaço": " ", "barra-sublinhado": "\\_"}
    LADOS_DO_C = ("dentro", "fora")
    SHELLS_DA_DIVISAO = (("bash", "-c"), ("sh", "-ec"), ("bash", "-lc"))
    ANTES_DO_SHELL = ("", "timeout 5")
    MOLDES_DA_DIVISAO = ("{R}", "sudo {R}")

    @classmethod
    def textos_da_divisao(cls, corpos_por_hook):
        """(rótulo, hook, texto, nativo) da dimensão "lançador que divide texto" de G1 (o nativo é sempre verdadeiro:
        com o `env` GNU o bash roda o corpo)."""
        saida = []
        for grafia, modelo in cls.OPCOES_DE_DIVISAO.items():
            for sep_nome, sep in cls.SEPARADORES_DE_DIVISAO.items():
                for lado in cls.LADOS_DO_C:
                    for shell, opcao in cls.SHELLS_DA_DIVISAO:
                        for antes in cls.ANTES_DO_SHELL:
                            for molde in cls.MOLDES_DA_DIVISAO:
                                palavras = [*antes.split(), shell] + ([opcao] if lado == "dentro" else [])
                                for hook, corpo in corpos_por_hook.items():
                                    resto = f"'{corpo}'" if lado == "dentro" else f"{opcao} '{corpo}'"
                                    reavaliador = "env " + modelo.replace("{V}", sep.join(palavras)) + " " + resto
                                    rotulo = (f"G1 divide / {grafia} / {sep_nome} / -c {lado} / {shell} {opcao} / "
                                              f"{antes or 'sem antes'} / {molde} / {hook}")
                                    saida.append((rotulo, hook, molde.replace("{R}", reavaliador), True))
        return saida

    # A classe "opção de lançador que o hook não modela" (opção A da proposta caminho-rev12, RET-LEITURA-HOOK-F): com o
    # marcador crítico, o lançador de `LANCADORES` só passa com as opções da tabela, por extenso e uma por palavra. A
    # verdade vem da construção: a palavra gerada está ou não está na tabela (`na_tabela_do_lancador`, lida aqui
    # direto dos conjuntos, sem o código do hook), e o teste não depende de nenhum `env`.
    LONGAS_FORA_DA_TABELA = ("split-string", "argv0", "file", "preserve-env", "shell", "login")

    @staticmethod
    def na_tabela_do_lancador(tabela, palavra):
        """A palavra é uma opção que a tabela do lançador modela? (Dela não sai nada: só os conjuntos.)"""
        com_valor = tabela.get("com_valor", ())
        return (palavra == "--" or palavra in tabela.get("booleanas", ()) or palavra in com_valor
                or (palavra.startswith("--") and "=" in palavra and palavra.split("=", 1)[0] in com_valor)
                or (len(palavra) > 2 and palavra[:2] in tabela.get("coladas", ())))

    @classmethod
    def alfabeto_de_opcoes(cls, tabela):
        """As palavras do item 1 do critério de fim da opção A: `-` mais cada caractere de 0x21 a 0x7E, cada par de
        letras (`-xy`), cada prefixo de cada opção longa da tabela e de `LONGAS_FORA_DA_TABELA`, com e sem `=`, e o `-`
        sozinho."""
        longas = sorted({o[2:] for grupo in ("booleanas", "com_valor") for o in tabela.get(grupo, ())
                         if o.startswith("--")} | set(cls.LONGAS_FORA_DA_TABELA))
        palavras = ["-" + chr(c) for c in range(0x21, 0x7F)]
        palavras += ["-" + a + b for a in string.ascii_letters for b in string.ascii_letters]
        palavras += [f"--{longa[:k]}{igual}" for longa in longas for k in range(1, len(longa) + 1) for igual in ("", "=x")]
        return list(dict.fromkeys(palavras + ["-"]))

    @classmethod
    def textos_do_alfabeto_de_opcoes(cls, lancadores, comandos, amostra=None):
        """(rótulo, lançador, palavra, na tabela, texto): cada palavra do alfabeto de cada lançador, logo depois dele,
        depois de `NOME=valor` e depois de uma opção modelada, antes de cada comando de `comandos`. A palavra entra
        entre aspas simples (`shlex.quote`: o bash a recebe como foi gerada); a da tabela com valor leva `X`. O
        `timeout` leva a duração antes do comando. `amostra`: passo para tomar só uma parte das palavras."""
        saida = []
        for nome, tabela in sorted(lancadores.items()):
            modeladas = sorted(tabela.get("booleanas", ())) or sorted(f"{o} X" for o in tabela.get("com_valor", ()))
            posicoes = {"logo depois": "", "depois de NOME=valor": "X=1 "}
            if modeladas:
                posicoes["depois de opção modelada"] = modeladas[0] + " "
            palavras = cls.alfabeto_de_opcoes(tabela)
            for palavra in palavras[::amostra] if amostra else palavras:
                na_tabela = cls.na_tabela_do_lancador(tabela, palavra)
                valor = " X" if na_tabela and palavra in tabela.get("com_valor", ()) else ""
                for onde, antes in posicoes.items():
                    for hook, comando in comandos.items():
                        duracao = "5 " if nome == "timeout" else ""
                        texto = f"{nome} {antes}{shlex.quote(palavra)}{valor} {duracao}{comando}"
                        saida.append((f"{nome} / {palavra} / {onde} / {hook}", nome, palavra, na_tabela, hook, texto))
        return saida

    # Item 2 do critério de fim da opção A: as formas das revalidações 12 (rótulo, molde com `{C}`, família do `env` em
    # que a forma roda com os hooks desligados: None é qualquer `env` da máquina). `-a`: as 11 formas do A1 da segurança
    # e as 12 do `-a` sem `-S` (duas são os controles dela, sem `-a`: `env {C}` e `env -u x {C}`, que o `parecer` não
    # pula, cartão R5A-COP). uutils: as 4 do A2 do review (o `-S` colado depois de `NOME=valor`, de `-` e de `-f`).
    FORMAS_DO_LANCADOR = (
        ("seg A1 E1", "env -a x -S 'X=1 bash' -c '{C}'", "gnu"), ("seg A1 E2", "env -a x -S 'bash\\_-c' '{C}'", "gnu"),
        ("seg A1 E3", "env -ia x -S 'bash -c' '{C}'", "gnu"),
        ("seg A1 E4", "env -a x --split-string='bash -c' '{C}'", "gnu"),
        ("seg A1 E4b", "env -a x -S'bash -c' '{C}'", None), ("seg A1 E4c", "env -i -a x -S 'bash -c' '{C}'", "gnu"),
        ("seg A1 E37", "timeout 5 env -a x -S 'bash -c' '{C}'", "gnu"),
        ("seg A1 E40", "x=$(env -a x -S 'bash -c' '{C}')", "gnu"), ("seg A1 E41", "env -a x -v -S 'bash -c' '{C}'", "gnu"),
        ("seg A1 E42", "env -a\tx -S 'bash -c' '{C}'", "gnu"), ("seg A1 E43", "env -a '' -S 'bash -c' '{C}'", "gnu"),
        ("rev A2 X=1", "env X=1 -S'bash -c \"{C}\"'", "uutils"), ("rev A2 -", "env - -S'bash -c \"{C}\"'", "uutils"),
        ("rev A2 -i X=1", "env -i X=1 -S'bash -c \"{C}\"'", "uutils"),
        ("rev A2 -f", "env -f /dev/null -S'bash -c \"{C}\"'", "uutils"),
        ("seg A2 A1 (env -a x git push)", "env -a x {C}", None), ("seg A2 A2", "env --argv0 x {C}", None),
        ("seg A2 A3", "env --ar x {C}", None), ("seg A2 A4", "env -ia x {C}", None), ("seg A2 A5", "env -a x X=1 {C}", None),
        ("seg A2 A6 controle", "env {C}", None), ("seg A2 A7 controle", "env -u x {C}", None),
        ("seg A2 A8", "env -ax {C}", None), ("seg A2 A9", "env --argv0=x {C}", None),
        ("seg A2 A10", "sudo env -a x {C}", None), ("seg A2 A11", "env -a x bash -c '{C}'", None),
        ("seg A2 A12", "x=$(env -a x {C})", None),
    )

    def familia_do_env(self, caminho):
        """`gnu`, `uutils` ou o nome do arquivo, pelo `--version` do `env` (local, sem rede)."""
        r = subprocess.run([caminho, "--version"], capture_output=True, text=True, timeout=10, stdin=subprocess.DEVNULL)
        return "uutils" if "uutils" in r.stdout else "gnu" if "GNU coreutils" in r.stdout else Path(caminho).name

    def rodou_com_o_env(self, bash, env_real, molde, base):
        """Hooks desligados: o bash roda o molde com o `env` real, e o `{C}` é um registrador de caminho absoluto que
        grava sem depender do ambiente (o `-i` limpa o `PATH` e o `REG`). Devolve se ele rodou."""
        self.montar_registradores_do_t9b(bash, molde, base, env_real)
        marca, rodou = base / "marca", base / "rodou"
        marca.write_text(f'#!{bash}\nprintf "%s\\n" "$*" >> {shlex.quote(str(rodou))}\n', encoding="utf-8")
        marca.chmod(0o755)
        texto = molde.replace("{C}", f"{marca} SENTINELA")
        self.rodar_no_bash_do_t9b(bash, texto, base)
        return rodou.exists() and "SENTINELA" in rodou.read_text(encoding="utf-8")

    # RET-LEITURA-HOOK-G (opção A da proposta caminho-rev13): a classe "regra sem o marcador atrás de lançador com opção
    # fora da tabela". Sem o marcador, as regras da linha (segredo, apagar o `.git`, o rótulo, a autoria) leem todas as
    # leituras possíveis de cada palavra com `-` que `LANCADORES` não modela (sem valor; com a palavra seguinte como valor;
    # no `env`, o texto dividido do `S`) e recusam se qualquer uma recusa. O oráculo é a leitura sem o lançador: se o
    # corpo sozinho dá 2 no `conformidade`, a forma com o lançador também dá 2. As decisões vêm da `Guarda` real, no mesmo
    # processo (`DRIVER_DA_GUARDA`: um processo por lote, e não um por texto), sobre o modelo do corpus.
    DRIVER_DA_GUARDA = """
import contextlib, io, json, os, sys, time
dados = json.loads(sys.stdin.read())
sys.path.insert(0, dados["hooks"])
import _comum, conformidade
_comum.forge_check().GIT_TIMEOUT_S = 120
os.environ.clear()
os.environ.update(dados["env"])
os.chdir(dados["raiz"])
saida = []
for texto in dados["textos"]:
    hook = _comum.Hook("conformidade")
    hook.entrada = {**dados["entrada"], "tool_input": {**dados["entrada"]["tool_input"], "command": texto}}
    erro, codigo, inicio = io.StringIO(), 0, time.perf_counter()
    with contextlib.redirect_stderr(erro), contextlib.redirect_stdout(io.StringIO()):
        try:
            conformidade.principal(hook)
        except SystemExit as saiu:
            codigo = saiu.code
    saida.append([codigo, time.perf_counter() - inicio, erro.getvalue()[:300] if dados["motivo"] else ""])
print(json.dumps(saida))
"""
    CORPOS_FIXOS = ("cat .env", "rm -rf .git")  # `env-cat-bloqueia.json` e o `.git` da raiz (`trava-rm-*-bloqueia.json`)
    # O lançador que o hook não modela (`LANCADORES_RECUSADOS`) recusa no fim da linha, e a leitura a mais só soma essa recusa.
    CORPOS_DE_LANCADOR_RECUSADO = ("flock f true", "ionice -c3 ls", "script -qc ls /dev/null")
    # O corpo que muda o estado do próprio shell (`cd`, `export`...) não o muda atrás de lançador (o `env cd` roda outro
    # processo): a pasta e as variáveis que seguem são as da leitura sem valor (ADR 0013, item 5), e não valem o oráculo.
    MUDA_O_ESTADO_DO_SHELL = frozenset({"cd", "export", "pushd", "popd", "read", "declare", "typeset", "unset", "set"})
    NO_FIXTURE_DE_OUTRO_DIA = ("{tmp}", "{raiz}", "{marca", "{HEAD}", "{pid")  # o texto só vale depois do `Fixture.montar`
    SO_PALAVRAS = re.compile(r"[\w./=:@%+,-]+(?: [\w./=:@%+,-]+)*")  # corpo que o `env -S` divide como o shell o leria

    def decidir_na_guarda(self, textos, hooks=HOOKS, motivo=False):
        """[(código, segundos, stderr)] da `Guarda` do `conformidade` de `hooks`, no mesmo processo (um filho só), sobre o
        modelo do corpus e com o ambiente limpo dos testes (`HOME` e `PATH` herdados do teste, sem rede)."""
        raiz, entrada, proc = self.modelos_montados()["conformidade"]
        env = ambiente_limpo()
        env.update(FORGE_PROC=str(proc), FORGE_NPROC="8")
        dados = {"hooks": str(hooks), "raiz": str(raiz), "entrada": entrada, "env": env, "textos": list(textos),
                 "motivo": motivo}
        r = subprocess.run([sys.executable, "-I", "-c", self.DRIVER_DA_GUARDA], input=json.dumps(dados), cwd=raiz,
                           env=env, capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        return json.loads(r.stdout.splitlines()[-1])

    def corpos_sem_marcador(self):
        """`CORPOS_SEM_MARCADOR` (item 1 do critério de fim da opção A, caminho-rev13): `cat .env` e `rm -rf .git` mais o
        comando de cada fixture `tests/hooks/conformidade/*-bloqueia.json` sem passos, sem o marcador do `conformidade` e
        sem lançador, que dá 2 sozinho no modelo do corpus (o oráculo: a leitura sem o lançador)."""
        _comum, conformidade, _ = modulos_dos_hooks()
        candidatos = list(self.CORPOS_FIXOS + self.CORPOS_DE_LANCADOR_RECUSADO)
        for caminho in sorted((FIXTURES / "conformidade").glob("*-bloqueia.json")):
            dados = json.loads(caminho.read_text(encoding="utf-8"))
            comando = dados.get("entrada", {}).get("tool_input", {}).get("command")
            if (dados.get("passos") or not isinstance(comando, str) or "\n" in comando
                    or any(marca in comando for marca in self.NO_FIXTURE_DE_OUTRO_DIA)
                    or conformidade.CRITICO.search(comando)
                    or any(Path(w).name in _comum.LANCADORES for w in re.split(r"[\s;&|()`'\"]+", comando))):
                continue
            if comando.split()[0] not in self.MUDA_O_ESTADO_DO_SHELL:
                candidatos.append(comando)
        candidatos = list(dict.fromkeys(candidatos))
        decisoes = self.decidir_na_guarda(candidatos)
        return [c for c, (codigo, _, _) in zip(candidatos, decisoes) if codigo == 2]

    @staticmethod
    def divide_sempre(nome, palavra):
        """O `env` sempre divide o texto desta palavra (`-S`, `-Svalor`, `--split-string[=valor]`)? Lida da palavra, sem o
        código do hook: nelas o texto é o comando, e "palavra com valor, e o comando depois" não é uma leitura dela."""
        return nome == "env" and (palavra.startswith("-S") or (palavra.startswith("--")
                                                              and palavra[2:].partition("=")[0] == "split-string"))

    def textos_sem_marcador(self, corpos, passo_env=5, passo_outros=29, passo_posicoes=97):
        """[(rótulo, texto)] da propriedade: para cada lançador, as palavras do alfabeto fora da tabela
        (`alfabeto_de_opcoes`, a do gerador com marcador; `passo_*`: uma em cada tantas) antes de cada corpo fixo, como
        `L w C` e `L w X C`, também depois de `NOME=valor` e de uma opção modelada (o `timeout` leva a duração), e algumas
        palavras antes de cada um dos outros corpos. No `env`, mais, com cada grupo de 0 a 2 letras antes do `S`:
        `env -<g>S'C'`, `env -<g>S 'C'` e `env --<prefixo de split-string>='C'`, só com os corpos que ele lê como o shell."""
        _comum, _, _ = modulos_dos_hooks()
        fixos = [c for c in self.CORPOS_FIXOS if c in corpos]
        outros = [c for c in corpos if c not in fixos]
        saida = []

        def formas(nome, antes, palavra, corpo):
            if self.divide_sempre(nome, palavra):
                return
            quotada, duracao = shlex.quote(palavra), "5 " if nome == "timeout" else ""
            saida.append((f"{nome} / {palavra} / {antes!r} / L w C / {corpo}", f"{nome} {antes}{quotada} {duracao}{corpo}"))
            saida.append((f"{nome} / {palavra} / {antes!r} / L w X C / {corpo}",
                          f"{nome} {antes}{quotada} X {duracao}{corpo}"))

        for nome, tabela in sorted(_comum.LANCADORES.items()):
            fora = [w for w in self.alfabeto_de_opcoes(tabela) if not self.na_tabela_do_lancador(tabela, w)]
            modeladas = sorted(tabela.get("booleanas", ())) or sorted(f"{o} X" for o in tabela.get("com_valor", ()))
            posicoes = ["X=1 "] + ([modeladas[0] + " "] if modeladas else [])
            for k, palavra in enumerate(fora):
                for corpo in fixos if k % (passo_env if nome == "env" else passo_outros) == 0 else ():
                    formas(nome, "", palavra, corpo)
                for corpo in fixos if k % passo_posicoes == 0 else ():
                    for antes in posicoes:
                        formas(nome, antes, palavra, corpo)
            for palavra in ("-iu", "--un"):
                if palavra in fora:
                    for corpo in outros:
                        formas(nome, "", palavra, corpo)
        letras = string.ascii_letters.replace("S", "")
        grupos = [""] + list(letras) + [a + b for a in letras for b in letras][::7]
        recusados = [c for c in self.CORPOS_DE_LANCADOR_RECUSADO if c in corpos]
        lidos_como_o_shell = fixos + recusados + [c for c in outros if c not in recusados
                                                  and self.SO_PALAVRAS.fullmatch(c)][:2]
        prefixos = ["split-string"[:k] for k in range(1, len("split-string") + 1)]
        for corpo in lidos_como_o_shell:
            quotado = shlex.quote(corpo)
            for g in grupos:
                saida.append((f"env / -{g}S'C' / {corpo}", f"env -{g}S{quotado}"))
                saida.append((f"env / -{g}S 'C' / {corpo}", f"env -{g}S {quotado}"))
            for prefixo in prefixos:
                saida.append((f"env / --{prefixo}='C' / {corpo}", f"env --{prefixo}={quotado}"))
                saida.append((f"env / --{prefixo} 'C' / {corpo}", f"env --{prefixo} {quotado}"))
        return saida

    REGRESSOES_SEM_MARCADOR = (
        "env -iu X cat .env", "env -iC / cat .env", "env -iu X rm -rf .git", "env -iS'cat .env'", "env -vS'cat .env'",
        "env -iS\"rm -rf .git\"", "env -a x cat .env", "env -f /dev/null cat .env", "env --un X cat .env")
    CONTROLES_SEM_MARCADOR = ("env -u X cat .env", "env -S'cat .env'", "env -i cat .env")

    def copia_do_plugin_com(self, *mudancas):
        """A pasta `hooks` de uma cópia limpa do plugin (`bin`, `templates` e o resto por link, para o `PLUGIN` do hook
        achar o que lê), com cada (arquivo, velho, novo) aplicado uma vez: uma mutação, sem tocar o código de hoje."""
        pasta = self._pasta_temporaria() / "plugin"
        pasta.mkdir()
        shutil.copytree(HOOKS, pasta / "hooks", ignore=shutil.ignore_patterns("__pycache__"))
        for item in RAIZ.iterdir():
            if item.name not in {"hooks", ".git", "tests", "__pycache__", "changelog.d"}:
                (pasta / item.name).symlink_to(item)
        for arquivo, velho, novo in mudancas:
            alvo = pasta / "hooks" / arquivo
            fonte = alvo.read_text(encoding="utf-8")
            self.assertEqual(fonte.count(velho), 1, f"a mutação não acha o trecho de {arquivo}: {velho!r}")
            alvo.write_text(fonte.replace(velho, novo), encoding="utf-8")
        return pasta / "hooks"

    # RET-LEITURA-HOOK-H, opção B da proposta caminho-rev14: a dimensão "leitura a mais que falha não tira recusa".
    FRAGMENTOS_ABERTOS = ("'", '"', "'\"", "\"'", "x'", "' y")  # o texto dividido, depois da remoção de aspas do shell
    CORPOS_INOFENSIVOS = ("make", "echo ok")  # só a recusa do texto que não fecha os leva a 2
    MOTIVO_DO_TEXTO_ABERTO = "texto dividido que não fecha aspas"
    TEXTO_ABERTO_RECUSA = (
        "env -uS\\' cat .env", "env -uS\\' rm -rf .git", "env -uS'\"' cat .env", "env -vuS\"'\" cat .env",
        "env --spl='\"' cat .env", "env -iu X env -uS\\' cat .env", "env -iu -S\\' cat .env", "env -aS'\"' cat .env",
        "env -aS'\"' rm -rf .git", "env -iS'\"' cat .env", "env -uS'\"' make")  # o último é o falso positivo do FD18
    TEXTO_ABERTO_CONTROLE = "env -S'\"' cat .env"  # uma leitura só: `ilegivel`, como na `develop`

    def textos_do_texto_aberto(self, corpos):
        """[(rótulo, texto, deve recusar)] da propriedade da dimensão: o grupo `-<g>S<F>` (colado e com o texto na palavra
        seguinte), com cada `g` de 1 caractere de `[A-Za-z0-9]` sem amostra e os de 2 numa amostra (um em 3); o `-S` certo
        depois de cada palavra de 1 caractere fora da tabela e de grupos de 2 (um em 11); cada prefixo de `--split-string` (sem o inteiro);
        cada forma logo depois do `env`, depois de `NOME=valor`, de `-i` e atrás de `env -iu X`; e cada lançador `L` com
        cada palavra de 1 caractere fora da tabela dele antes de `env -<g>S<F> C`. Os corpos giram pelas formas. O
        controle (`env -S<F> C`, uma leitura só) não recusa; atrás de `env -iu X`, recusa."""
        _comum, _, _ = modulos_dos_hooks()
        alnum = string.ascii_letters + string.digits
        um = [g for g in alnum if g != "S"]
        dois = [a + b for a in alnum for b in alnum if a != "S"]
        tabela_do_env = _comum.LANCADORES["env"]
        de_um_caractere = [w for w in ("-" + chr(c) for c in range(0x21, 0x7F))
                           if not self.na_tabela_do_lancador(tabela_do_env, w) and not self.divide_sempre("env", w)]
        prefixos = ["split-string"[:k] for k in range(1, len("split-string"))]
        formas, k = [], itertools.count()

        def corpo(todos=False):
            return corpos if todos else [corpos[next(k) % len(corpos)]]

        for f in self.FRAGMENTOS_ABERTOS:
            for g in um:
                formas += [(f"-{g}S<F>", [f"-{g}S{f}"], c) for c in corpo(todos=True)]
                formas += [(f"-{g}S <F>", [f"-{g}S", f], c) for c in corpo()]
            formas += [(f"-{g}S<F>", [f"-{g}S{f}"], c) for g in dois[::3] for c in corpo()]
            formas += [("w -S<F>", [w, f"-S{f}"], c) for w in de_um_caractere for c in corpo()]
            formas += [("-gg -S<F>", [f"-{g}", f"-S{f}"], c) for g in dois[::11] for c in corpo()]
            for p in prefixos:
                formas += [(f"--{p}=<F>", [f"--{p}={f}"], c) for c in corpo()]
                formas += [(f"--{p} <F>", [f"--{p}", f], c) for c in corpo()]
        saida = []
        for rotulo, palavras, c in formas:
            texto = " ".join(shlex.quote(p) for p in palavras) + " " + c
            for antes in ("", "X=1 ", "-i ", "-iu X env "):
                saida.append((f"env {antes}{rotulo} / {palavras} / {c}", f"env {antes}{texto}", True))
        for f in self.FRAGMENTOS_ABERTOS:
            for c in corpos:
                certo = f"env {shlex.quote('-S' + f)} {c}"
                saida.append((f"controle / -S<F> / {f!r} / {c}", certo, False))
                saida.append((f"env -iu X / controle / {f!r} / {c}", certo.replace("env ", "env -iu X env ", 1), True))
        for nome, tabela in sorted(_comum.LANCADORES.items()):
            fora = [w for w in ("-" + chr(c) for c in range(0x21, 0x7F)) if not self.na_tabela_do_lancador(tabela, w)
                    and not self.divide_sempre(nome, w)]
            for i, w in enumerate(fora):
                f, g, c = self.FRAGMENTOS_ABERTOS[i % 6], um[i % len(um)], corpo()[0]
                duracao = "5 " if nome == "timeout" else ""
                saida.append((f"{nome} / {w} / env -{g}S<F> / {c}",
                              f"{nome} {shlex.quote(w)} {duracao}env {shlex.quote(f'-{g}S{f}')} {c}", True))
        return saida

    def alvos_de_escrita_em(self, hooks, texto):
        """`alvos_de_escrita(texto)` do `conformidade` de `hooks` (uma cópia mutada), num filho só, sem rede."""
        codigo = ("import json, sys; sys.path.insert(0, sys.argv[1]); import conformidade; "
                  "print(json.dumps(conformidade.alvos_de_escrita(sys.argv[2])))")
        r = subprocess.run([sys.executable, "-I", "-c", codigo, str(hooks), texto], env=ambiente_limpo(),
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        return json.loads(r.stdout.splitlines()[-1])

    MUTACOES_DO_TEXTO_ABERTO = {  # item 5 do critério de fim da opção B (rev14): (arquivo, de, para) e a forma que a pega
        "ilegivel_em_vez_de_barrar": (
            "conformidade.py",
            "            self.barrar(\"R-CONFORMIDADE\", f\"`{achado}` na chamada: opção de lançador que o hook não modela, "
            "com texto \"\n",
            "            return self.ilegivel(\" \".join(palavras), pasta) or pasta\n            (\"R-CONFORMIDADE\", "
            "f\"`{achado}` na chamada: opção de lançador que o hook não modela, com texto \"\n",
            "env -uS\\' cat .env"),
        "so_a_leitura_adiada": (
            "_comum.py", "                dividido += _dividir(texto[0], gasto, f\"{nome} {opcao}\")\n",
            "                dividido += _dividir(texto[0], 0, f\"{nome} {opcao}\")\n", "env -iu -S\\' cat .env"),
        "tambem_com_uma_leitura": (
            "_comum.py", "        if gasto:\n            raise TextoAbertoComLeituras(achado) from None\n",
            "        if True:\n            raise TextoAbertoComLeituras(achado) from None\n", "env -S'\"' cat .env"),
        "sem_a_regra_do_tee": (
            "conformidade.py",
            "                alvos += [a for a in palavras[tees[0] + 1:] if not a.startswith(\"-\")] if tees else []\n",
            "                alvos += []\n", "env -aS'\"' tee docs/reviews/x.md"),
    }

    def comandos_de_um_fixture(self, caminho):
        """Os comandos do Bash de um fixture (os `passos` e a `entrada`)."""
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        entradas = [p["entrada"] for p in dados.get("passos", []) if "entrada" in p] + [dados.get("entrada", {})]
        return [e["tool_input"]["command"] for e in entradas
                if isinstance(e.get("tool_input"), dict) and isinstance(e["tool_input"].get("command"), str)]

    def lancadores_com_opcao_fora_da_tabela(self, comando):
        """[(lançador, palavra)] de cada lançador do comando, em qualquer leitura da linha, seguido de palavra com `-` que
        `LANCADORES` não modela antes do comando."""
        _comum, _, _ = modulos_dos_hooks()
        achados, lancadores = [], 0
        try:
            lidas = _comum.leituras(_comum.tirar_heredocs(comando)[0])
        except ValueError:
            return achados, lancadores
        for partes in lidas.partes:
            for palavras, _, _ in partes:
                for k, palavra in enumerate(palavras):
                    nome = Path(palavra).name
                    if nome in _comum.LANCADORES and (k == 0 or _comum.sem_atribuicoes(palavras[:k]) == []):
                        lancadores += 1
                        fora = _comum.opcao_fora_da_tabela(list(palavras), k + 1, nome)
                        if fora is not None:
                            achados.append((nome, fora))
        return achados, lancadores

    # Propriedade da opção B ((5) da seção 4B da proposta caminho-rev8, item 2 do critério da caminho-rev9), sem bash:
    # com o marcador crítico e uma reavaliação pelo shell, o hook recusa. No corpus, a reavaliação é reconhecida por uma
    # leitura própria do teste (`REAVALIACAO_DO_TESTE`); em G1, pela construção.
    REAVALIACAO_DO_TESTE = re.compile(r"(?<![\w.-])(?:eval|(?:bash|sh|zsh|dash|ksh)(?:\s+-\w+)*?\s+-[A-Za-z]*c[A-Za-z]*)(?=\s)")

    # Propriedade da opção C (item 1 do critério de fim, proposta caminho-rev10, 3C): o `$'` e o `$"` entram em cada
    # posição da palavra do reavaliador e da opção de G1, com cada escape do alfabeto inteiro (`\` e cada caractere de
    # 0x20 a 0x7E, a quebra de linha e o `\x{…}` do bash 5.3, com e sem a chave de fecho). A verdade vem da construção:
    # a palavra gerada tem `$'` ou `$"` fora de aspas, e o teste não depende do que o bash faz com o escape.
    ESCAPES_DO_ALFABETO = tuple("\\" + chr(c) for c in range(0x20, 0x7F)) + (
        "\\\n", "\\x{65}", "\\x{0000065}", "\\x{65", "\\x{}", "\\x{zz}", "\\u{65}", "\\U", "\\c", "\\c\\'")
    FORMAS_ANSI = (("$'", "'"), ('$"', '"'))
    PREFIXOS_DO_ALFABETO = ("nenhum", "coproc", "env X=1", "$(…)", "pipeline")

    @classmethod
    def textos_do_alfabeto(cls, corpos_por_hook, escapes=None, prefixos=None, reavaliadores=None):
        """(rótulo, hook, texto) de G1 com o `$'` ou o `$"` e um escape em cada posição do nome do reavaliador e da opção."""
        saida = []
        escapes = cls.ESCAPES_DO_ALFABETO if escapes is None else escapes
        for prefixo, molde, _, para in cls.PREFIXOS_DE_G1:
            if prefixo not in (prefixos or cls.PREFIXOS_DO_ALFABETO):
                continue
            for nome, opcao in (reavaliadores or cls.REAVALIADORES_DE_G1):
                if para and para != ("eval" if opcao is None else "shell"):
                    continue
                for onde, palavra in (("nome", nome), ("opção", opcao)):
                    if palavra is None:
                        continue
                    for posicao in range(len(palavra) + 1):
                        for (abre, fecha), escape in itertools.product(cls.FORMAS_ANSI, escapes):
                            nova = palavra[:posicao] + abre + escape + fecha + palavra[posicao:]
                            reavaliador = (nova if onde == "nome" else nome) + (f" {nova if onde == 'opção' else opcao}" if opcao else "")
                            for hook, corpo in corpos_por_hook.items():
                                rotulo = f"alfabeto {prefixo} / {nome} {opcao or ''} / {onde}@{posicao} / {abre}{escape}{fecha} / {hook}"
                                saida.append((rotulo, hook, molde.replace("{R}", f"{reavaliador} '{corpo}'")))
        return saida

    def conferir_os_pares_contra_o_bash(self):  # item 2 do critério de fim da opção C
        """Parte de `test_reducao_da_palavra_como_o_bash`. Para toda `\\` seguida de cada caractere de 0x20 a 0x7E e da quebra de linha, e depois de cada sufixo (nada, `{`,
        `}`, dígito octal, dígito hexadecimal, `'`, fim), fora de aspas e entre aspas duplas: a `reduzida` dá o mesmo que o
        `printf '%s'` do bash, ou `None` (expansão ou aspas sem par). Nunca um literal diferente, nunca um literal onde
        o bash recusa a palavra. Cobre o alfabeto inteiro, e não uma tabela. Só o bash (R-CUSTO)."""
        _comum, _, _ = modulos_dos_hooks()
        bash = shutil.which("bash")
        casa = self._pasta_temporaria()
        casos = []
        for c in [chr(x) for x in range(0x20, 0x7F)] + ["\n"]:
            for sufixo in ("b", "{b", "}b", "7b", "fb", "'b", ""):
                miolo = f"a\\{c}{sufixo}"
                casos += [("fora", miolo), ("duplas", f'"{miolo}"')]

        def do_bash(caso):
            return subprocess.run([bash, "--noprofile", "--norc", "-c", f"printf '%s' {caso[1]}"], cwd=casa,
                                  env={"HOME": str(casa), "LC_ALL": "C.UTF-8"}, capture_output=True, timeout=30)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(8, (os.cpu_count() or 2)))) as pool:
            do_bash_de = list(pool.map(do_bash, casos))
        for (contexto, cru), r in zip(casos, do_bash_de):
            valor = _comum.reduzida(cru)
            com_expansao = any(ch in cru for ch in "$`*?[{~")
            with self.subTest(contexto=contexto, cru=cru):
                self.assertIsNot(valor, _comum.INDECIDIVEL, "a barra e um caractere não formam `$'` nem `$\"`")
                if valor is None:
                    self.assertTrue(com_expansao or r.returncode != 0, f"None sem expansão nem erro do bash: {cru!r}")
                else:
                    self.assertEqual(r.returncode, 0, f"o bash recusa {cru!r} e o hook o reduz a {valor!r}")
                    self.assertEqual(r.stdout.decode("utf-8", "surrogateescape"), valor)
        self.assertGreaterEqual(len(casos), 1300)

    # As grafias de G1 (proposta caminho-rev9, 3B): a mesma palavra escrita pelos mecanismos de aspas do bash, que a
    # entrega igual ao programa. O teste de diferença (`test_reducao_da_palavra_como_o_bash`) prova cada uma no bash.
    GRAFIAS = {
        "direta": lambda w: w,
        "simples": lambda w: f"'{w}'",
        "duplas": lambda w: f'"{w}"',
        "barra": lambda w: "\\" + w,
        "ansi": lambda w: f"$'{w}'",
        "hexa": lambda w: f"$'\\x{ord(w[0]):02x}'{w[1:]}",
        "ansi no meio": lambda w: f"{w[0]}$'{w[1:]}'",
        "vazio no meio": lambda w: f"{w[0]}''{w[1:]}",
        "locale": lambda w: f'$"{w}"',
        "octal": lambda w: f"$'\\{ord(w[0]):03o}'{w[1:]}",
        "unicode": lambda w: f"$'\\u{ord(w[0]):04x}'{w[1:]}",
    }
    PALAVRAS_DE_G1 = ("eval", "bash", "sh", "zsh", "dash", "ksh", "rbash", "-c", "-ec", "-lc")
    # As bordas da remoção de aspas do POSIX que G1 não gera (a redução não tem tabela de escapes: o `$'…'` e o `$"…"` são
    # INDECIDIVEL, sem ler o escape). Cada uma entra na comparação com o bash.
    BORDAS_DA_REDUCAO = ('"a\\b"', '"a\\$b"', '"a\\`b"', '"a\\"b"', '"a\\\nb"', "e\\\nval", "\\e\\v\\a\\l", "é'v'al",
                         "'$'", "a''b", '""', "\\\\", '"\\\\"', "'\\'", '"\\\nx"')
    # Com `$'` ou `$"` fora de aspas, em qualquer posição e com qualquer escape (o bash 5.3 lê `\x{65}`, o 5.2 não): o
    # hook não lê o escape e não decide.
    INDECIDIVEIS = ("$'eval'", "e$'val'", "$'\\x{65}'val", "$'\\x{0000065}'val", "$'\\x{65'val", "$'ev\\0al'x", "$'\\545val'",
                    "$'\\cA'", "$'\\c\\''", "$'\\u'", "$'\\U00110000'", "$'a\\'b'", "$'ev", "$\"eval\"", "e$\"val\"",
                    "$\"e\\$\"", "$\"ev", "$x$'a'", "$(x)$'a'", "${x}$\"a\"", "`x`$'a'", "\"$(x)\"$'y'", "\"`x`\"$'y'")
    NAO_SE_REDUZEM = ("$x", "${x}", "$(echo eval)", "`echo eval`", "e*", "ev?l", "[e]val", "{e,}val", "~", "\"$x\"",
                      '"a`b`"', "'ev", '"ev', "$((1))", "e$x", "\"$'a'\"", "\"$\\\"\"x", "x\"$(y)\"z", "\"${x}\"")

    # Bloco T da revalidação 10 (proposta caminho-rev10, seção 2): o orçamento de tempo. Os tipos de palavra que mais
    # custam (a unidade, quantas palavras ela tem e a forma de 2 a 3 caracteres, para o teto de caracteres), e o
    # tamanho: 1 mil palavras, o teto de palavras, o teto + 1 e o teto de caracteres com as palavras curtas.
    TIPOS_DO_ORCAMENTO = {
        "nome de shell": ("bash ", 1, "sh "),
        "env": ("env ", 1, "env "),
        "env -S": ("env -S 'x' ", 3, "env -S x "),
        "$'…' longo": ("$'" + "a" * 40 + "' ", 1, "$'a' "),
        "-c": ("-c ", 1, "-c "),
        "inerte": ("x ", 1, "x "),
    }

    @staticmethod
    @contextlib.contextmanager
    def limite_de_tempo(segundos):
        """Falha o teste (AssertionError) se o bloco passa de `segundos` s: o alarme interrompe a conta lenta."""
        def estourar(signo, quadro):
            raise AssertionError(f"passou de {segundos} s")
        anterior = signal.signal(signal.SIGALRM, estourar)
        signal.setitimer(signal.ITIMER_REAL, segundos)
        try:
            yield
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, anterior)
