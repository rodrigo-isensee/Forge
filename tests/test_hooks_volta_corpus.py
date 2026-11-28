"""Corpus da volta única, oráculos (redireções, enumerador, bash) e conferências do próprio corpus.

Os testes saíram da classe `CorpusHeredocVoltaUnica` de tests/test_hooks.py (HOOKS-CORPUS-RAPIDO); a base e o corpus estão em
tests/apoio_volta_unica.py."""
from pathlib import Path
from unittest import mock
import ast
import collections
import concurrent.futures
import inspect
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import types
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_volta_unica import (  # noqa: E402
    BaseVoltaUnica,
    CARTOES_DO_NAO_PROMETE,
    ContadorDeTrabalho,
    EXIGE_NENHUMA_MARCA,
    FIXTURES,
    HOOKS,
    IDS_DA_VOLTA_UNICA,
    MedidaDeCpu,
    MINIMO_POR_CLASSE,
    chamadas_do_executar,
    referencias_ao_executar_fora_de_chamada,
    NAO_PROMETE,
    RAIZ,
    REGRAS_DA_VOLTA_UNICA,
    MEDIDA_DO_CORPUS,
    PASSOS_POR_NIVEL_DO_TMP,
    RUIDO_DO_CORPUS,
    corpus_da_volta_unica,
    excessos_de_trabalho,
    profundidade_do_tmp,
    execucoes_do_corpus,
    modulos_dos_hooks,
    rodar,
    nucleos_do_processo,
    trabalhadores_do_pool,
    texto)
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class CorpusDaVoltaUnica(BaseVoltaUnica, unittest.TestCase):

    def amostra_da_equivalencia(self):
        """Os pedidos (hook, texto) da amostra fixa de `test_decisao_em_lote_igual_ao_subprocesso_do_hook`: os casos do corpus
        nos dois hooks e uma fatia, de passo fixo, de G1 e do alfabeto de escapes."""
        _comum, conformidade, parecer = modulos_dos_hooks()
        criticos = {"conformidade": conformidade.CRITICO, "parecer": parecer.CRITICO}
        dados = corpus_da_volta_unica()
        do_corpus = sorted({(hook, caso["comando"].replace("{CORPO}", dados["corpos"][hook]))
                            for caso in dados["casos"] if caso.get("comando") for hook in criticos})
        do_corpus = [p for p in do_corpus if len(p[1]) <= self.TEXTO_DO_PRAZO_DO_CLAUDE_CODE]
        g1 = sorted({(hook, texto) for _, hook, texto, _ in self.textos_de_g1(self.LINHAS_DIRETAS)})
        alfabeto = sorted({(hook, texto) for _, hook, texto in self.textos_do_alfabeto(self.LINHAS_DIRETAS)})
        return do_corpus[::max(1, len(do_corpus) // 150)] + g1[::max(1, len(g1) // 100)] \
            + alfabeto[::max(1, len(alfabeto) // 100)]

    def test_decisao_em_lote_igual_ao_subprocesso_do_hook(self):
        """A decisão no processo (`decidir_em_lote`, que as propriedades usam) é a do subprocesso do hook real (`rodar`):
        numa amostra fixa de pelo menos 200 textos, com recusa (2) e liberação (0), o código é o mesmo."""
        montados = self.modelos_montados()
        pedidos = list(dict.fromkeys(self.amostra_da_equivalencia()))
        self.assertGreaterEqual(len(pedidos), 200)

        def pelo_hook(pedido):
            hook, texto = pedido
            raiz, entrada, proc = montados[hook]
            entrada = json.loads(json.dumps(entrada))
            entrada["tool_input"]["command"] = texto
            return rodar(hook, entrada, raiz, proc, {"FORGE_NPROC": "8"}).returncode

        trabalhadores = trabalhadores_do_pool(nucleos_do_processo())
        with concurrent.futures.ThreadPoolExecutor(max_workers=trabalhadores) as pool:
            reais = list(pool.map(pelo_hook, pedidos))
        no_lote = self.decidir_em_lote(pedidos, montados)
        for pedido, real, lote in zip(pedidos, reais, no_lote):
            with self.subTest(hook=pedido[0], texto=pedido[1][:80]):
                self.assertEqual(lote, real, f"o lote dá {lote} e o hook real dá {real}: {pedido[1]!r}")
        self.assertEqual(set(reais), {0, 2}, "a amostra tem de ter recusa e liberação")

    def test_driver_do_lote_chama_o_executar_como_o_main_de_cada_hook(self):  # A2 da segurança, E1
        """O driver do lote (`DRIVER_DOS_HOOKS`) passa a `_comum.executar` os mesmos argumentos do `__main__` de cada hook:
        o nome, `principal`, o marcador crítico do hook (não `None`; o conformidade usa `MARCADOR`, o da política, e o
        parecer `CriticoOuAlias`), `clone_do_forge` e `regra_do_prazo`; e roda na pasta do hook."""
        def chamada(arvore):
            achadas = [n for n in ast.walk(arvore) if isinstance(n, ast.Call) and isinstance(n.func, (ast.Name, ast.Attribute))
                       and getattr(n.func, "attr", getattr(n.func, "id", None)) == "executar"]
            self.assertEqual(len(achadas), 1)
            return achadas[0]

        driver = ast.parse(self.DRIVER_DOS_HOOKS)
        no_driver = chamada(driver)
        self.assertEqual([ast.unparse(a) for a in no_driver.args], ["hook", "modulo.principal", "getattr(modulo, marcador)"])
        self.assertEqual([ast.unparse(k) for k in no_driver.keywords], ["**argumentos", "**PRAZO_LONGO.get(hook, {})"])
        execucao = next(n.value for n in ast.walk(driver) if isinstance(n, ast.Assign)
                        and any(getattr(t, "id", None) == "EXECUCAO" for t in n.targets))
        argumentos = {ast.literal_eval(k): ast.literal_eval(v.elts[2]) for k, v in zip(execucao.keys, execucao.values)}
        marcadores = {ast.literal_eval(k): ast.literal_eval(v.elts[1]) for k, v in zip(execucao.keys, execucao.values)}
        modulos = {ast.literal_eval(k): v.elts[0].id for k, v in zip(execucao.keys, execucao.values)}
        longo = next(n.value for n in ast.walk(driver) if isinstance(n, ast.Assign)
                     and any(getattr(t, "id", None) == "PRAZO_LONGO" for t in n.targets))
        nomes = {ast.literal_eval(k): {ast.literal_eval(a): ast.unparse(b) for a, b in zip(v.keys, v.values)}
                 for k, v in zip(longo.keys, longo.values)}  # v0455: o argumento que é um nome do módulo do hook
        self.assertEqual(set(argumentos), {"conformidade", "parecer"})
        self.assertEqual(marcadores, {"conformidade": "MARCADOR", "parecer": "CriticoOuAlias"})
        for hook in argumentos:
            with self.subTest(hook=hook):
                principal = chamada(ast.parse((HOOKS / f"{hook}.py").read_text(encoding="utf-8")))
                self.assertEqual([ast.literal_eval(principal.args[0]), ast.unparse(principal.args[1]), ast.unparse(principal.args[2])],
                                 [hook, "principal", marcadores[hook]])
                literais = {k.arg: ast.literal_eval(k.value) for k in principal.keywords if not isinstance(k.value, ast.Name)}
                self.assertEqual(literais, argumentos[hook])
                self.assertEqual({k.arg: f"{hook}.{k.value.id}" for k in principal.keywords if isinstance(k.value, ast.Name)},
                                 nomes.get(hook, {}))
                self.assertEqual(modulos[hook], hook)
        self.assertIn('os.chdir(dados["raizes"][hook])', self.DRIVER_DOS_HOOKS)  # a pasta de cada hook, não a do conformidade

    def test_hooks_reais_e_driver_nao_passam_relogio_nem_armar(self):  # BP1, E37.16
        """`relogio`, `armar` e `idade` do `_comum.executar` são só por palavra-chave, com o relógio, o alarme e a idade do
        processo reais por padrão, e só um teste em processo os troca: nenhuma chamada a `executar` dos hooks os passa, nem
        por `**`, e o driver do lote (`DRIVER_DOS_HOOKS`) não os tem nos argumentos que repassa."""
        _comum, _, _ = modulos_dos_hooks()
        assinatura = inspect.signature(_comum.executar).parameters
        self.assertEqual([(assinatura[n].kind, assinatura[n].default) for n in ("relogio", "armar", "idade")],
                         [(inspect.Parameter.KEYWORD_ONLY, time.monotonic), (inspect.Parameter.KEYWORD_ONLY, signal.setitimer),
                          (inspect.Parameter.KEYWORD_ONLY, None)])
        chamadas = []
        for script in sorted(HOOKS.glob("*.py")):
            arvore = ast.parse(script.read_text(encoding="utf-8"))
            for n in chamadas_do_executar(arvore):
                chamadas.append(script.name)
                with self.subTest(hook=script.name):
                    self.assertEqual([k.arg for k in n.keywords if k.arg is None or k.arg in ("relogio", "armar", "idade")], [])
        self.assertGreaterEqual(len(chamadas), 10, "chamadas a `executar` nos hooks")
        self.assertEqual(len(chamadas), len(set(chamadas)), "uma chamada por hook")
        driver = ast.parse(self.DRIVER_DOS_HOOKS)
        repassados = {ast.literal_eval(k) for n in ast.walk(driver) if isinstance(n, ast.Dict) for k in n.keys
                      if isinstance(k, ast.Constant)}
        self.assertTrue({"regra_do_prazo", "prazo_longo"} <= repassados, repassados)
        self.assertEqual(repassados & {"relogio", "armar", "idade"}, set())

    def test_chamada_com_apelido_do_import_e_pega_com_relogio(self):  # BP1, A1 da segurança (E37.31)
        """Um hook de exemplo que importa `executar` com apelido, ou chama `c.executar` pelo módulo, e passa `relogio=` ou
        `armar=` é achado pela mesma resolução de nomes que confere os hooks reais."""
        exemplos = {
            "apelido": "from _comum import executar as rodar\nrodar('x', f, g, relogio=r)\n",
            "modulo com apelido": "import _comum as c\nc.executar('x', f, g, armar=a)\n",
            "modulo": "import _comum\n_comum.executar('x', f, g, **k)\n",
        }
        for nome, fonte in exemplos.items():
            with self.subTest(exemplo=nome):
                achadas = chamadas_do_executar(ast.parse(fonte))
                self.assertEqual(len(achadas), 1)
                self.assertTrue([k.arg for k in achadas[0].keywords if k.arg is None or k.arg in ("relogio", "armar")])
        self.assertEqual(chamadas_do_executar(ast.parse("from outro import executar as rodar\nc.executar(1)\nrodar(2)\n")), [])

    def test_chamada_de_outro_nome_do_comum_nao_e_do_executar(self):  # BP1, E37.36: as guardas do import e da chamada
        """Só o `executar` de `_comum` conta: outro nome importado de `_comum`, outro módulo com apelido e outra função do
        módulo `_comum` não são chamadas a ele."""
        for nome, fonte in {
            "outro nome de _comum": "from _comum import bloquear as b\nb(1)\n",
            "outro módulo com apelido": "import os as o\no.executar(1)\n",
            "outra função de _comum": "import _comum\n_comum.bloquear(1)\n",
        }.items():
            with self.subTest(exemplo=nome):
                self.assertEqual(chamadas_do_executar(ast.parse(fonte)), [])

    def test_referencia_ao_executar_fora_de_chamada_e_achada(self):  # BP1, A2 da segurança (E37.36)
        """Reatribuição, `getattr`, `importlib.import_module(...).executar` e `functools.partial(executar, ...)` levam o
        `relogio=` e o `armar=` sem uma chamada direta: o teste de AST os acha, pelo nome, pelo apelido e pelo atributo."""
        formas = {
            "reatribuição": "from _comum import executar\nx = executar\nx('h', p, m, relogio=r)\n",
            "reatribuição pelo apelido": "from _comum import executar as rodar\nx = rodar\n",
            "getattr": "import _comum\ngetattr(_comum, 'executar')('h', p, m, armar=a)\n",
            "import_module": "import importlib\nimportlib.import_module('_comum').executar('h', p, m, relogio=r)\n",
            "atributo sem chamada": "import _comum as c\nx = c.executar\n",
            "partial": "import functools\nfrom _comum import executar\nfunctools.partial(executar, relogio=r)('h', p, m)\n",
        }
        for nome, fonte in formas.items():
            with self.subTest(forma=nome):
                self.assertTrue(referencias_ao_executar_fora_de_chamada(ast.parse(fonte)))
        diretas = {
            "nome": "from _comum import executar\nexecutar('h', p, m)\n",
            "apelido": "from _comum import executar as rodar\nrodar('h', p, m)\n",
            "módulo": "import _comum as c\nc.executar('h', p, m)\n",
            "outro nome": "from _comum import bloquear\nx = bloquear\n",
            "outro atributo": "import _comum\nx = _comum.bloquear\n",
            "outra cadeia": "x = 'bloquear'\n",
        }
        for nome, fonte in diretas.items():
            with self.subTest(direta=nome):
                self.assertEqual(referencias_ao_executar_fora_de_chamada(ast.parse(fonte)), [])

    def test_hooks_reais_e_driver_so_chamam_o_executar_direto(self):  # BP1, A2 da segurança (E37.36)
        """Nos hooks reais e no driver do lote, toda menção ao `executar` de `_comum` é a chamada direta."""
        fontes = {script.name: script.read_text(encoding="utf-8") for script in sorted(HOOKS.glob("*.py"))}
        self.assertGreaterEqual(len(fontes), 10, "hooks lidos")
        fontes["driver"] = self.DRIVER_DOS_HOOKS
        for nome, fonte in fontes.items():
            with self.subTest(hook=nome):
                self.assertEqual([ast.unparse(n) for n in referencias_ao_executar_fora_de_chamada(ast.parse(fonte))], [])

    def test_corpus_nos_dois_hooks(self):
        """O corpus nos dois hooks cabe no teto de trabalho (CORPUS-CUSTO-CONTADOR): cada caso roda o hook uma vez por
        passo declarado, sem sono, com os subprocessos e os passos do interpretador (chamadas, funções e voltas de laço
        do código do hook) até a medida mais o ruído (`MEDIDA_DO_CORPUS`, `RUIDO_DO_CORPUS`). Conta, e não cronometra:
        a CPU do mesmo lote variou de 127 s a 185 s no CI com a disputa da máquina, e as contagens não variam com ela. A
        CPU segue na mensagem, só como informação."""
        casos = self.fixtures_do_corpus()
        self.contador_de_trabalho = ContadorDeTrabalho(self._pasta_temporaria())
        with MedidaDeCpu() as medida:
            self.assertEqual(self.executar_em_lote(casos), len(casos))
        trabalho = self.contador_de_trabalho.ler()
        self.assertEqual(excessos_de_trabalho(trabalho, execucoes_do_corpus(casos)), [],
                         f"trabalho do corpus: {trabalho}, em {len(casos)} casos (informativo: {medida.texto()})")

    def test_oraculo_das_redirecoes(self):  # T6
        """Para cada redireção das classes R e N e cada prefixo (P0 a P4), o bash roda `<P>cat <redireção> <<'EOF'⏎x⏎EOF`
        numa pasta vazia; se ele criou ou mudou um arquivo ali, `grava_arquivo` dá verdadeiro, e para a classe N, com
        todo prefixo, falso. Só roda `cat` e `echo`, sem rede (R-CUSTO)."""
        bash = shutil.which("bash")
        versao = None
        if bash:
            r = subprocess.run([bash, "--noprofile", "--norc", "-c", 'echo "${BASH_VERSINFO[0]}"'], capture_output=True,
                               text=True, env={"PATH": "/usr/bin:/bin"}, stdin=subprocess.DEVNULL, timeout=5)
            versao = r.stdout.strip()
        if not bash or not (versao or "").isdigit() or int(versao) < 4:
            self.skipTest(f"bash ausente ou anterior ao 4 (BASH_VERSINFO={versao}): {{fd}}> e &>> não existem")
        _comum, _, _ = modulos_dos_hooks()
        oraculo = corpus_da_volta_unica()["oraculo"]
        for redirecao in oraculo["redirecoes"]:
            for nome, prefixo in oraculo["prefixos"].items():
                texto = f"{prefixo}cat {redirecao['op']} <<'EOF'\nx\nEOF"
                with self.subTest(texto=texto), tempfile.TemporaryDirectory(prefix="forge-redirecao-") as tmp:
                    subprocess.run([bash, "--noprofile", "--norc", "-c", texto], cwd=tmp, env={"PATH": "/usr/bin:/bin"},
                                   stdin=subprocess.DEVNULL, capture_output=True, timeout=5)
                    gravou = any(Path(tmp).iterdir())
                    resto, _ = _comum.tirar_heredocs(texto)
                    grava = _comum.grava_arquivo(resto)
                    passou = (grava or not gravou) and (redirecao["classe"] != "N" or not grava)
                    self.conferir_marca(redirecao.get("fecha", {}).get(nome), passou,
                                        f"bash gravou: {gravou}; grava_arquivo: {grava}")
        self.assertGreaterEqual(len(oraculo["redirecoes"]), 28)

    def test_enumerador_nao_engole_programa(self):  # T7
        """A redireção completa (operador e alvo colado) não consome a palavra seguinte, nem depois de atribuição ou de
        `!`; o operador que pede alvo separado consome só o alvo."""
        _comum, _, _ = modulos_dos_hooks()
        enumerador = corpus_da_volta_unica()["enumerador"]
        casos = [(item, forma, f"{forma}{item['op']} ./x.sh", "./x.sh", None)
                 for item in enumerador["completos"] for forma in enumerador["formas"]]
        casos += [(item, "", f"{item['op']} alvo ./x.sh", "./x.sh", "alvo") for item in enumerador["pedem_alvo"]]
        for item, forma, texto, programa, alvo in casos:
            with self.subTest(texto=texto):
                programas = [p for p, _, _ in _comum.programas_e_atribuicoes(texto)]
                passou = programa in programas and alvo not in programas
                self.conferir_marca(item.get("fecha", {}).get(forma), passou, f"programas: {programas}")
        self.assertGreaterEqual(len(casos), 70)

    def test_t8_mutacao_da_gramatica_da_opcao_d(self):  # T8 (RET-LEITURA-HOOK-D e -A)
        """A classe "leitor" acaba quando a gramática decide pelo texto que o bash roda. Para cada caso L que ela aceita
        (com o corpo de cada hook): (1) cada caractere fora do alfabeto e cada abridor (`$(`, `$((`, `<(`, `>(`, crase,
        `${`, `$'`, `$"`) inserido em cada posição recusa, salvo dentro de aspas simples, dentro de aspas duplas se a
        inserção não tem `$`, crase, `\\` nem `!`, e no corpo; dentro da palavra `"$(cat <<'X'…X⏎)"` e do operador,
        qualquer inserção recusa. (2) Por palavra: a palavra entre aspas só passa se ela passa sem as aspas (opção A,
        item 1; o contrário é só recusa a mais, como `'cat' > arq` na K1, lida crua). (3) Por nível: o caso dentro de cada
        reavaliação de `NIVEIS`, com o `<<` em cada forma de `FORMAS_DO_HEREDOC`, recusa (item 2 e opção A da
        revalidação 8). (4) Por corpo:
        uma linha `X)`, `X )`, `X x)`, `X;)` ou `Xfoo` no corpo recusa (item 3). As zonas vêm de uma varredura própria."""
        _comum, _, _ = modulos_dos_hooks()
        inseridos = list("#{}<>()*?[]!|$`\\") + ["$(", "$((", "<(", ">(", "${", "$'", '$"']
        contagem = collections.Counter()
        usados = set()
        for id, hook, texto in self.casos_aceitos():
            usados.add(id)
            zona = self.zonas_do_teste(texto)
            for i in range(len(texto) + 1):
                if zona[i] in ("corpo", "simples"):
                    continue
                for inserido in inseridos:
                    if zona[i] == "duplas" and not set(inserido) & _comum.DUPLAS_RECUSA:
                        continue
                    mutada = texto[:i] + inserido + texto[i:]
                    if mutada.replace("cat >>", "cat >") == texto.replace("cat >>", "cat >") and mutada != texto:
                        continue  # `cat >` mais `>` é a forma K1 com `>>`, também aceita
                    if not self.HEREDOC_DO_TESTE.search(mutada):
                        continue  # o sinal partiu o `<<` (`<#<`): sem `<<` que o bash forme a gramática não vale (opção A)
                    contagem["caractere"] += 1
                    self.assertIsNotNone(_comum.fora_da_gramatica_com_heredoc(mutada),
                                         f"{id}/{hook}: passou com {inserido!r} em {i}: {mutada!r}")
            for rotulo, envolto in self.mutacoes_de_nivel(texto):
                contagem["nivel"] += 1
                self.assertIsNotNone(_comum.fora_da_gramatica_com_heredoc(envolto),
                                     f"{id}/{hook} em {rotulo}: passou {envolto!r}")
            for _, _, corpo, fim_do_corpo, _, delimitador in self.heredocs_do_teste(texto):
                pontos = [corpo] + [k + 1 for k in range(corpo, fim_do_corpo) if texto[k] == "\n"]
                for ponto in dict.fromkeys(pontos):
                    for linha in self.LINHAS_QUE_FECHAM:
                        mutada = texto[:ponto] + linha.format(X=delimitador) + "\n" + texto[ponto:]
                        contagem["corpo"] += 1
                        self.assertIsNotNone(_comum.fora_da_gramatica_com_heredoc(mutada),
                                             f"{id}/{hook}: passou com {linha!r} no corpo: {mutada!r}")
        for rotulo, simples, entre_aspas in self.mutacoes_de_palavra():
            contagem["palavra"] += 1
            if _comum.fora_da_gramatica_com_heredoc(entre_aspas) is None:  # a K1 é lida crua: `'cat' > a` só recusa
                self.assertIsNone(_comum.fora_da_gramatica_com_heredoc(simples),
                                  f"{rotulo}: passou entre aspas e recusa sem elas: {entre_aspas!r}")
        self.assertLessEqual({"L1", "L2", "L3", "L11", "K1a", "K1b", "K2", "K3a", "K3b"}, usados)
        self.assertGreaterEqual(contagem["caractere"], 1000)
        self.assertGreaterEqual(contagem["palavra"], 500)
        self.assertGreaterEqual(contagem["nivel"], 43 * len(usados))
        self.assertGreaterEqual(contagem["corpo"], 5 * len(usados))

    def test_t9_oraculo_de_bash(self):  # T9 (RET-LEITURA-HOOK-A, seção 3 da proposta caminho-rev7)
        """O que a gramática libera com o marcador crítico e `<<` roda no bash exatamente o que ela listou. Para cada
        texto do corpus e das mutações de palavra do T8 que a gramática aceita, o bash roda o texto como `env -i bash
        --noprofile --norc -c` (o ambiente só com `PATH` e `REG`), numa pasta de `$TMPDIR`, com o `PATH` só com
        registradores (um script do próprio bash por nome que aparece no texto: grava o argv e a entrada em `REG`, sem
        rede); a sequência gravada tem de ser a de `esperado_no_bash`, e nenhum programa pode faltar ao `PATH`. Só
        roda o bash (R-CUSTO)."""
        bash = shutil.which("bash")
        if not bash or " " in bash:
            self.skipTest("bash ausente ou num caminho com espaço")
        _comum, conformidade, parecer = modulos_dos_hooks()
        dados = corpus_da_volta_unica()
        textos = {}
        for caso in dados["casos"]:
            for hook, corpo in dados["corpos"].items():
                if "comando" in caso:
                    textos.setdefault(caso["comando"].replace("{CORPO}", corpo), f"{caso['id']}/{hook}")
        for rotulo, simples, entre_aspas in self.mutacoes_de_palavra():
            textos.setdefault(simples, rotulo)
            textos.setdefault(entre_aspas, rotulo)
        rodados, ids = 0, set()
        with tempfile.TemporaryDirectory(prefix="forge-t9-") as tmp:
            for n, (texto, rotulo) in enumerate(textos.items()):
                if not (conformidade.CRITICO.search(texto) or parecer.CRITICO.search(texto)):
                    continue
                lida = _comum.gramatica_com_heredoc(texto)
                if not isinstance(lida, _comum.Gramatica):
                    continue
                base = Path(tmp) / str(n)
                registradores, pasta, registro = base / "bin", base / "pasta", base / "registro"
                registradores.mkdir(parents=True)
                pasta.mkdir()
                esperado = self.esperado_no_bash(lida, pasta)
                if esperado is None:
                    continue
                for nome in set(re.findall(r"[A-Za-z_][\w.+-]*", texto)) | {"cat", "git", "gh", "mkdir", "sh"}:
                    arquivo = registradores / nome
                    arquivo.write_text(self.REGISTRADOR.format(bash=bash), encoding="utf-8")
                    arquivo.chmod(0o755)
                r = subprocess.run([bash, "--noprofile", "--norc", "-c", texto], cwd=pasta, stdin=subprocess.DEVNULL,
                                   env={"PATH": str(registradores), "REG": str(registro)}, capture_output=True,
                                   text=True, timeout=10)
                gravado = registro.read_text(encoding="utf-8") if registro.exists() else ""
                rodou = []
                for item in gravado.split("\036")[:-1]:
                    argv, entrada = item.split("\035", 1)
                    argv = argv.split("\037")[:-1]
                    rodou.append((argv[0], argv[1:], entrada))
                with self.subTest(rotulo=rotulo):
                    self.assertNotIn("command not found", r.stderr, f"{texto!r}: o bash rodou um programa fora do PATH")
                    self.assertEqual(rodou, esperado, f"{texto!r}: o bash rodou outra coisa ({r.stderr.strip()})")
                rodados += 1
                ids.add(rotulo.split("/")[0].split(":")[0])
        self.assertLessEqual({"K1a", "K1b", "K2", "K3a", "K3b", "L1", "L3"}, ids)
        self.assertGreaterEqual(rodados, 200)

    def test_t9b_oraculo_do_gatilho(self):  # T9b (RET-LEITURA-HOOK-B, seção 3 da proposta caminho-rev8)
        """O que o hook libera com o marcador crítico, o bash não roda escondido. Para cada texto de `textos_do_t9b` que
        o hook dono da sentinela libera (código 0), o bash roda o texto (`rodar_no_bash_do_t9b`) com cada `env` da
        máquina (`envs_da_maquina`: GNU e uutils), e nenhum registrador pode gravar a linha sentinela: o hook liberou, e
        o bash rodou a linha que ele não viu. Com a marca `fecha`, o caso ainda tem de mostrar a sentinela rodada (o
        vermelho continua provado). Só roda o bash e os `env` locais (R-CUSTO)."""
        bash = shutil.which("bash")
        if not bash or " " in bash:
            self.skipTest("bash ausente ou num caminho com espaço")
        base = self._pasta_temporaria()
        textos = self.textos_do_t9b(base)
        decisoes = self.decisoes_dos_hooks([(hook, texto) for _, hook, texto, _, _ in textos])
        ids = set()
        for rotulo, hook, texto, pasta, marca in textos:
            if decisoes[(hook, texto)] != 0:
                if marca and marca != NAO_PROMETE:
                    with self.subTest(rotulo=rotulo):
                        self.conferir_marca(marca, True, f"o {hook} já recusa {texto!r}")
                continue
            sentinela = shlex.split(self.SENTINELAS[hook])
            for env_real in self.envs_da_maquina() or (None,):
                shutil.rmtree(pasta, ignore_errors=True)  # a pasta do texto (`/tmp/x` do Z1 está nela), nova por `env`
                self.montar_registradores_do_t9b(bash, texto, pasta, env_real)
                rodou = self.rodar_no_bash_do_t9b(bash, texto, pasta)
                if marca == NAO_PROMETE:  # o código de hoje: o hook libera e o bash roda a sentinela (cartão)
                    with self.subTest(rotulo=rotulo, env=env_real):
                        self.assertIn((sentinela[0], sentinela[1:]), rodou, f"{rotulo}: o bash não roda a sentinela")
                    continue
                with self.subTest(rotulo=rotulo, env=env_real):
                    self.conferir_marca(marca, (sentinela[0], sentinela[1:]) not in rodou,
                                        f"o {hook} libera {texto!r} e o bash roda {' '.join(sentinela)} com o "
                                        f"{env_real}: {rodou}")
                ids.add(rotulo.split("/")[0])
        self.assertLessEqual({"K1a", "K1b"}, ids, "o T9b roda no bash o que o hook libera")
        self.assertGreaterEqual(len(textos), 500)

    def test_divisao_esta_na_classe(self):  # o oráculo do oráculo da dimensão "lançador que divide texto"
        """Com os hooks desligados e o `env` GNU, o bash roda a sentinela em cada texto da dimensão: um gerador que não
        produz a divisão de verdade fica vermelho. Roda como o T9b (`rodar_no_bash_do_t9b`); só o bash e o `env`
        locais (R-CUSTO)."""
        bash = shutil.which("bash")
        if not bash or " " in bash or not self.env_gnu():
            self.skipTest("bash ausente ou sem o env GNU nesta máquina")
        base = self._pasta_temporaria()
        textos = self.textos_da_divisao(self.SENTINELAS)
        rodados = self.rodar_em_paralelo_no_t9b(bash, ((texto, base / f"dv-{k}")
                                                       for k, (_, _, texto, _) in enumerate(textos)))
        for (rotulo, hook, texto, _), rodou in zip(textos, rodados):
            sentinela = shlex.split(self.SENTINELAS[hook])
            with self.subTest(rotulo=rotulo):
                self.assertIn((sentinela[0], sentinela[1:]), rodou, f"o bash não roda a sentinela em {texto!r}")
        self.assertGreaterEqual(len(textos), 400)

    def test_spec_de_mutantes_do_lote_e_valida(self):  # item 7 do critério de fim da opção B (rev14) e A4 do QA
        """`tests/mutantes/lote-leitura-hook.json` tem a forma da spec do `forge-mutante` (pedido, executor e de 1 a 8
        mutantes, cada um com id, guarda, arquivo, de, para e testes; a validação da ferramenta roda no QA, e o
        `test_hooks` não lê o `bin/`), cada `de` aparece uma vez no arquivo de hoje, e ela declara os quatro mutantes do
        item 5 com as trocas deste teste."""
        specs = [json.loads((RAIZ / "tests" / "mutantes" / f"{nome}.json").read_text(encoding="utf-8"))
                 for nome in ("lote-leitura-hook", "lote-leitura-hook-volta")]  # a segunda, pelo teto de 8 mutantes
        for spec in specs:
            self.assertEqual(set(spec), {"pedido", "executor", "mutantes"})
            self.assertTrue(1 <= len(spec["mutantes"]) <= 8)
            self.assertEqual(len({m["id"] for m in spec["mutantes"]}), len(spec["mutantes"]))
            for m in spec["mutantes"]:
                self.assertEqual(set(m), {"id", "guarda", "arquivo", "de", "para", "testes"}, m.get("id"))
                self.assertTrue(m["arquivo"].startswith("hooks/") and m["testes"] and m["de"] != m["para"], m["id"])
                self.assertEqual((RAIZ / m["arquivo"]).read_text(encoding="utf-8").count(m["de"]), 1, m["id"])
        spec = {"mutantes": specs[0]["mutantes"]}
        trocas = {(f"hooks/{arquivo}", de, para) for arquivo, de, para, _ in self.MUTACOES_DO_TEXTO_ABERTO.values()}
        self.assertLessEqual(trocas, {(m["arquivo"], m["de"], m["para"]) for m in spec["mutantes"]})

    def test_fixtures_libera_nao_tem_lancador_com_opcao_fora_da_tabela(self):  # item 7 do critério de fim (rev13)
        """O registro do item 5 da rev12: a busca de lançador com opção fora da tabela nos fixtures `-libera` dos dois
        hooks e nos casos do corpus que algum hook libera. Não há nenhum: o que o `segmento` lê a mais (a opção com valor
        e o texto dividido) só soma recusa, e nenhum caso liberado muda. Os dois fixtures com lançador e opção
        (`lancador-sudo-u-npm-test-libera.json`, `lancador-nice-git-status-libera.json`) têm opção da tabela. Se um
        caso novo com lançador e opção fora da tabela entrar como liberado, este teste o mostra e o autor decide."""
        achados, lancadores, lidos = [], 0, 0
        for hook in ("conformidade", "parecer"):
            for caminho in sorted((FIXTURES / hook).glob("*-libera*.json")):
                for comando in self.comandos_de_um_fixture(caminho):
                    lidos += 1
                    fora, quantos = self.lancadores_com_opcao_fora_da_tabela(comando)
                    achados += [(f"{hook}/{caminho.name}", comando, *f) for f in fora]
                    lancadores += quantos
        corpus = corpus_da_volta_unica()
        for caso in corpus["casos"]:
            if 0 in (caso.get("conformidade"), caso.get("parecer")):
                for comando in caso.get("passos", [caso.get("comando")]):
                    lidos += 1
                    fora, quantos = self.lancadores_com_opcao_fora_da_tabela(comando.replace("{CORPO}", "ls"))
                    achados += [(caso["id"], comando, *f) for f in fora]
                    lancadores += quantos
        self.assertEqual(achados, [])
        self.assertGreaterEqual(lidos, 200)
        self.assertGreaterEqual(lancadores, 5, "a busca acha os lançadores com opção da tabela")

    def test_t9b_monta_os_registradores_antes_de_rodar(self):  # item 2 do critério de fim do caminho 1 (caminho-rev12)
        """O arnês do T9b só grava na thread principal, antes do pool (`rodar_em_paralelo_no_t9b`): com `Path.write_text`
        e `Path.chmod` levantando erro fora dela, os textos rodam e a sentinela aparece. Voltar a gravar dentro do pool
        deixa este teste vermelho. Só o bash (R-CUSTO)."""
        bash = shutil.which("bash")
        if not bash or " " in bash:
            self.skipTest("bash ausente ou num caminho com espaço")
        base = self._pasta_temporaria()
        textos = self.textos_de_g1(self.SENTINELAS, so_nativos=True)[:16]
        principal = threading.main_thread()

        def so_na_principal(nome, original):
            def gravar(caminho, *args, **kwargs):
                if threading.current_thread() is not principal:
                    raise AssertionError(f"{nome} de {caminho} na fase de rodar, dentro do pool")
                return original(caminho, *args, **kwargs)
            return gravar

        with mock.patch.object(Path, "write_text", so_na_principal("write_text", Path.write_text)), \
                mock.patch.object(Path, "chmod", so_na_principal("chmod", Path.chmod)):
            rodados = self.rodar_em_paralelo_no_t9b(bash, ((texto, base / f"m-{k}")
                                                           for k, (_, _, texto, _) in enumerate(textos)))
        for (rotulo, hook, texto, _), rodou in zip(textos, rodados):
            sentinela = shlex.split(self.SENTINELAS[hook])
            with self.subTest(rotulo=rotulo):
                self.assertIn((sentinela[0], sentinela[1:]), rodou, f"o bash não roda a sentinela em {texto!r}")
        self.assertEqual(len(rodados), 16)

    def test_t9b_registrador_que_nao_roda_e_falha_do_arnes(self):  # item 3 do critério de fim do caminho 1
        """O registrador que o bash não consegue rodar (rc 126) faz o oráculo falhar com "falha do arnês" e o stderr do
        bash, e não com "o bash não roda a sentinela". Só o bash (R-CUSTO)."""
        bash = shutil.which("bash")
        if not bash or " " in bash:
            self.skipTest("bash ausente ou num caminho com espaço")
        base = self._pasta_temporaria() / "t"
        texto = self.SENTINELAS["conformidade"]
        self.montar_registradores_do_t9b(bash, texto, base)
        self.assertEqual(self.rodar_no_bash_do_t9b(bash, texto, base), [("git", ["push", "origin", "SENTINELA:main"])])
        (base / "bin" / "git").chmod(0o644)  # o bash acha o registrador e não consegue rodá-lo: rc 126
        with self.assertRaisesRegex(AssertionError, r"falha do arnês, não do gerador: .*rc 126.*stderr: .*git"):
            self.rodar_no_bash_do_t9b(bash, texto, base)

    def test_t9b_bash_que_passa_do_prazo_e_falha_do_arnes(self):  # FLAKY-G1-CARGA
        """O bash que passa do prazo (carga da máquina) faz o oráculo falhar com "falha do arnês" e o prazo, e não com
        um `TimeoutExpired` solto. Só o bash (R-CUSTO)."""
        bash = shutil.which("bash")
        if not bash or " " in bash:
            self.skipTest("bash ausente ou num caminho com espaço")
        base = self._pasta_temporaria() / "t"
        texto = "while :; do :; done"
        self.montar_registradores_do_t9b(bash, texto, base)
        with mock.patch.object(self, "PRAZO_DO_BASH_DO_T9B_S", 0.5):
            with self.assertRaisesRegex(AssertionError, r"falha do arnês, não do gerador: o bash passou de 0.5 s \(prazo\)"):
                self.rodar_no_bash_do_t9b(bash, texto, base)

    def test_g1_esta_na_classe(self):  # item 3 do critério de fim da opção B (proposta caminho-rev9): o oráculo do oráculo
        """Com os hooks desligados, o bash roda a sentinela em cada texto de G1 de prefixo nativo: G1 só tem reavaliação
        de verdade, e um gerador que não a produz fica vermelho. Roda como o T9b (`rodar_no_bash_do_t9b`: `env -i`,
        `HOME` no `$TMPDIR`, sem rede, os shells são o próprio bash); só o bash (R-CUSTO)."""
        bash = shutil.which("bash")
        if not bash or " " in bash:
            self.skipTest("bash ausente ou num caminho com espaço")
        base = self._pasta_temporaria()
        textos = self.textos_de_g1(self.SENTINELAS, so_nativos=True)
        rodados = self.rodar_em_paralelo_no_t9b(bash, ((texto, base / f"g1-{k}")
                                                       for k, (_, _, texto, _) in enumerate(textos)))
        for (rotulo, hook, texto, _), rodou in zip(textos, rodados):
            sentinela = shlex.split(self.SENTINELAS[hook])
            with self.subTest(rotulo=rotulo):
                self.assertIn((sentinela[0], sentinela[1:]), rodou, f"o bash não roda a sentinela em {texto!r}")
        self.assertGreaterEqual(len(textos), 1500)

    def test_corpus_cobre_as_classes(self):
        dados = corpus_da_volta_unica()
        casos = dados["casos"]
        ids = [c["id"] for c in casos]
        self.assertEqual(len(ids), len(set(ids)), "ID repetido no corpus")
        for classe, minimo in MINIMO_POR_CLASSE.items():
            self.assertGreaterEqual(sum(c["classe"] == classe for c in casos), minimo, f"classe {classe}")
        self.assertLessEqual({c["classe"] for c in casos}, set(MINIMO_POR_CLASSE), "a classe X não entra no corpus")
        for id in IDS_DA_VOLTA_UNICA:
            self.assertIn(id, ids)
        marcas = [m for c in casos for m in (c["fecha"].values() if isinstance(c.get("fecha"), dict)
                                             else [c["fecha"]] if "fecha" in c else [])]
        for secao in (dados["oraculo"]["redirecoes"], dados["enumerador"]["completos"], dados["enumerador"]["pedem_alvo"]):
            marcas += [m for item in secao for m in item.get("fecha", {}).values()]
        self.assertLessEqual(set(marcas), REGRAS_DA_VOLTA_UNICA)
        if EXIGE_NENHUMA_MARCA:
            self.assertEqual(marcas, [], "o passo (7) não aceita marca `fecha`")
        for caso in casos:
            self.assertTrue(caso["conformidade"] is not None or caso["parecer"] is not None, caso["id"])
            self.assertEqual(sum(chave in caso for chave in ("comando", "passos")), 1, caso["id"])
            if "nao_promete" in caso:
                self.assertIn(caso["nao_promete"], CARTOES_DO_NAO_PROMETE, caso["id"])
                self.assertNotIn("fecha", caso, f"{caso['id']}: não promete e fecha ao mesmo tempo")


class ContadorDeTrabalhoDoCorpus(unittest.TestCase):
    """CORPUS-CUSTO-CONTADOR (v0478 E41.1): o contador e o teto do custo do corpus, sem rodar o corpus."""

    def test_contador_anota_execucao_subprocesso_e_sono_de_cada_filho(self):
        with tempfile.TemporaryDirectory(prefix="forge-contador-") as tmp:
            contador = ContadorDeTrabalho(tmp)
            # Sem `-I`: ele ignora o PYTHONPATH, que é por onde o hook carrega o contador (como no `rodar`). O ambiente
            # herdado sai inteiro (só o PATH e o do contador) e a pasta de trabalho é a temporária.
            env = {"PATH": "/usr/bin:/bin", **contador.ambiente()}
            codigo = "import subprocess, time; subprocess.run(['true']); subprocess.run(['true']); time.sleep(0.01)"
            for _ in range(2):
                subprocess.run([sys.executable, "-c", codigo], env=env, cwd=tmp, check=True, timeout=60,
                               stdin=subprocess.DEVNULL, capture_output=True)
            trabalho = contador.ler()
        self.assertEqual((trabalho["execucoes"], trabalho["subprocessos"]), (2, 4))
        self.assertAlmostEqual(trabalho["sono"], 0.02)

    def passos_do_interpretador(self, voltas, codigo_contado=True):
        """Os passos contados de um script com `voltas` voltas de laço, cada uma com uma chamada a uma função dele e um
        `if` com `else` (um salto para a frente), com a pasta do script como o código do hook, ou não."""
        with tempfile.TemporaryDirectory(prefix="forge-contador-") as tmp:
            contador, codigo = ContadorDeTrabalho(tmp), Path(tmp) / "codigo"
            codigo.mkdir()
            script = codigo / "hook.py"
            script.write_text("def f(i):\n    if i % 2:\n        x = 1\n    else:\n        x = 2\n    i += x\n    return i\n\n"
                              f"for i in range({voltas}):\n    f(i)\n"
                              "import os\nprint(len(os.environ))\n", encoding="utf-8")
            env = {"PATH": "/usr/bin:/bin", **contador.ambiente(),
                   "FORGE_TESTE_TRABALHO_CODIGO": str(codigo if codigo_contado else Path(tmp) / "outra")}
            r = subprocess.run([sys.executable, str(script)], env=env, cwd=tmp, check=True, timeout=60,
                               stdin=subprocess.DEVNULL, capture_output=True, text=True)
            trabalho = contador.ler()
            if codigo_contado:
                self.assertEqual(trabalho["ambiente"], int(r.stdout))  # as variáveis que o próprio processo viu
            return trabalho["interpretador"]

    def test_contador_anota_os_passos_do_interpretador_do_codigo_do_hook(self):
        # Cada volta a mais é uma chamada, um início de função e um salto para trás: 3 passos, em qualquer versão; o
        # salto para a frente do `else` não conta.
        self.assertEqual(self.passos_do_interpretador(20) - self.passos_do_interpretador(10), 30)
        self.assertEqual(self.passos_do_interpretador(10, codigo_contado=False), 0)  # fora do código do hook

    def test_decisao_que_vai_ate_o_prazo_de_producao_conta_sem_o_interpretador(self):
        """O caso com `prazo_de_producao` anda até o prazo, tanto quanto a máquina deixa: a entrada principal dele roda
        sem os passos do interpretador; os passos antes dela e os outros casos, com eles."""
        with tempfile.TemporaryDirectory(prefix="forge-contador-") as tmp:
            tmp, ambientes = Path(tmp), []

            def rodar_falso(hook, entrada, raiz, proc, extra, **_):
                ambientes.append(dict(extra))
                return subprocess.CompletedProcess([], 0, "", "")

            for prazo in (True, False):
                pasta = tmp / str(prazo)
                pasta.mkdir()
                caso = CorpusDaVoltaUnica("test_corpus_nos_dois_hooks")
                caso.contador_de_trabalho = ContadorDeTrabalho(pasta)
                fixture = types.SimpleNamespace(hook="conformidade", dados={"prazo_de_producao": prazo, "esperado": {"codigo": 0}},
                                                montar=lambda t, o: (t, {}), executar_passos=lambda raiz, rodar_hook: rodar_hook({}))
                with mock.patch("apoio_volta_unica.rodar", rodar_falso):
                    caso.executar_fixture(fixture, pasta, 0)
        codigo = [("FORGE_TESTE_TRABALHO_CODIGO" in e, "FORGE_TESTE_TRABALHO" in e) for e in ambientes]
        self.assertEqual(codigo, [(True, True), (False, True), (True, True), (True, True)])  # passo e entrada, com e sem prazo

    def test_execucoes_do_corpus_contam_cada_passo_e_a_entrada(self):
        casos = [("a", types.SimpleNamespace(dados={})), ("b", types.SimpleNamespace(dados={"passos": [{}, {}]}))]
        self.assertEqual(execucoes_do_corpus(casos), 4)

    def trabalho(self, **mudado):
        """O trabalho no teto (a medida mais o ruído) em tudo, com `mudado` por cima."""
        no_teto = {nome: MEDIDA_DO_CORPUS[nome] + ruido for nome, ruido in RUIDO_DO_CORPUS.items()}
        return {"execucoes": MEDIDA_DO_CORPUS["execucoes"], "sono": 0.0, "ambiente": MEDIDA_DO_CORPUS["variaveis_do_ambiente"],
                **no_teto, **mudado}

    def excessos(self, trabalho, execucoes=MEDIDA_DO_CORPUS["execucoes"], python=MEDIDA_DO_CORPUS["python"]):
        """`excessos_de_trabalho` no Python e na profundidade do tmp da medida (o resultado não depende de quem roda)."""
        return excessos_de_trabalho(trabalho, execucoes, python, MEDIDA_DO_CORPUS["profundidade_do_tmp"])

    def test_no_teto_nao_ha_excesso(self):
        self.assertEqual(self.excessos(self.trabalho()), [])

    def test_execucoes_a_mais_ou_a_menos_reprovam(self):  # o driver que roda cada caso duas vezes, ou pula um
        execucoes = MEDIDA_DO_CORPUS["execucoes"]
        for contadas in (2 * execucoes, execucoes - 1):
            with self.subTest(contadas=contadas):
                excessos = self.excessos(self.trabalho(execucoes=contadas))
                self.assertEqual(excessos, [f"{contadas} execuções do hook, e o corpus declara {execucoes}"])

    def test_corpus_diferente_do_medido_reprova(self):  # o teto vale para o corpus medido; outro corpus mede de novo
        execucoes = MEDIDA_DO_CORPUS["execucoes"] + 1
        excessos = self.excessos(self.trabalho(execucoes=execucoes), execucoes)
        self.assertEqual(len(excessos), 1)
        self.assertIn(f"o corpus declara {execucoes} execuções, e a medida do teto é de", excessos[0])

    def test_um_acima_do_teto_reprova(self):  # S2 do review: um git a mais por decisão também reprova
        execucoes = MEDIDA_DO_CORPUS["execucoes"]
        for nome, ruido in RUIDO_DO_CORPUS.items():
            for acima in (1, execucoes):
                with self.subTest(nome=nome, acima=acima):
                    contado = MEDIDA_DO_CORPUS[nome] + ruido + acima
                    self.assertEqual(self.excessos(self.trabalho(**{nome: contado})),
                                     [f"{contado} {nome}, acima do teto de {MEDIDA_DO_CORPUS[nome] + ruido} "
                                      f"(medida {MEDIDA_DO_CORPUS[nome]} mais o ruído {ruido})"])

    def test_passos_do_interpretador_valem_so_no_python_da_medida(self):  # o bytecode muda com a versão
        trabalho = self.trabalho(interpretador=10 * MEDIDA_DO_CORPUS["interpretador"])
        self.assertEqual(self.excessos(trabalho, python="0.0"), [])

    def test_medida_do_interpretador_acerta_pela_profundidade_do_tmp(self):
        """Cada nível a mais do tmp soma `PASSOS_POR_NIVEL_DO_TMP` à medida dos passos, e cada nível a menos tira; os
        subprocessos não mudam. Sem a profundidade, vale a do tmp de quem roda."""
        base, ruido = MEDIDA_DO_CORPUS["profundidade_do_tmp"], RUIDO_DO_CORPUS["interpretador"]
        for niveis in (-1, 1, 3):
            medida = MEDIDA_DO_CORPUS["interpretador"] + PASSOS_POR_NIVEL_DO_TMP * niveis
            with self.subTest(niveis=niveis):
                no_teto = self.trabalho(interpretador=medida + ruido)
                self.assertEqual(excessos_de_trabalho(no_teto, MEDIDA_DO_CORPUS["execucoes"], "3.12", base + niveis), [])
                acima = self.trabalho(interpretador=medida + ruido + 1)
                self.assertEqual(excessos_de_trabalho(acima, MEDIDA_DO_CORPUS["execucoes"], "3.12", base + niveis),
                                 [f"{medida + ruido + 1} interpretador, acima do teto de {medida + ruido} "
                                  f"(medida {medida} mais o ruído {ruido})"])
        fundo = "/" + "/".join(["n"] * (base + 1))
        with mock.patch("tempfile.gettempdir", return_value=fundo), mock.patch("os.path.realpath", lambda c: c):
            self.assertEqual(profundidade_do_tmp(), base + 1)
            no_teto = self.trabalho(interpretador=MEDIDA_DO_CORPUS["interpretador"] + PASSOS_POR_NIVEL_DO_TMP + ruido)
            self.assertEqual(excessos_de_trabalho(no_teto, MEDIDA_DO_CORPUS["execucoes"], "3.12"), [])

    def test_ambiente_diferente_do_da_medida_reprova(self):
        """O hook roda com o ambiente completado até `variaveis_do_ambiente`; mais variáveis em quem roda (o contador não
        tira nenhuma) ou o completar que não rodou (0) reprovam, mesmo com o interpretador dentro da medida."""
        medida = MEDIDA_DO_CORPUS["variaveis_do_ambiente"]
        for ambiente in (0, medida - 1, medida + 1):
            with self.subTest(ambiente=ambiente):
                self.assertEqual(self.excessos(self.trabalho(ambiente=ambiente)),
                                 [f"o hook viu {ambiente} variáveis no ambiente, e a medida é com {medida}: o ambiente "
                                  "de quem roda passa delas"])

    def passos_com_o_ambiente(self, variaveis, voltas=0):
        """O trabalho de um hook de mentira que copia o ambiente num filho Python (como o `git` do `forge-check`, variável
        por variável) e dá `voltas` voltas de laço a mais, rodado com `variaveis` variáveis herdadas de quem roda."""
        with tempfile.TemporaryDirectory(prefix="forge-contador-") as tmp:
            contador, codigo = ContadorDeTrabalho(tmp), Path(tmp) / "codigo"
            codigo.mkdir()
            filho = "import os\nenv = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}\n"
            (codigo / "filho.py").write_text(filho, encoding="utf-8")
            (codigo / "hook.py").write_text(
                f"import os, subprocess, sys\n{filho}for i in range({voltas}):\n    pass\n"
                "subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'filho.py')], check=True)\n",
                encoding="utf-8")
            # Sem `-I`: ele ignora o PYTHONPATH, por onde o contador entra (como no `rodar`); o herdado sai inteiro.
            herdado = {"PATH": "/usr/bin:/bin", **{f"HERDADA_{i}": "x" for i in range(variaveis - 1)}}
            env = {**herdado, **contador.ambiente(), "FORGE_TESTE_TRABALHO_CODIGO": str(codigo)}
            subprocess.run([sys.executable, str(codigo / "hook.py")], env=env, cwd=tmp, check=True, timeout=60,
                           stdin=subprocess.DEVNULL, capture_output=True)
            return contador.ler()

    def test_trabalho_nao_muda_com_as_variaveis_de_quem_roda(self):
        """E45.73: o runner do CI deu 132 e 133 variáveis no ambiente, e o custo de copiar o ambiente mudava o teto. O
        contador completa o ambiente do hook (só dele: o filho herda e não completa de novo) até `variaveis_do_ambiente`:
        com 132 ou 133 herdadas, o mesmo ambiente e os mesmos passos, e o veredito é o mesmo. Uma volta de laço a mais
        (custo real) segue contada."""
        com_132, com_133 = self.passos_com_o_ambiente(132), self.passos_com_o_ambiente(133)
        self.assertEqual(com_132["ambiente"], MEDIDA_DO_CORPUS["variaveis_do_ambiente"])
        self.assertEqual(com_132, com_133)
        self.assertEqual((com_132["execucoes"], com_132["subprocessos"]), (2, 1))
        self.assertGreater(com_132["interpretador"], 2 * MEDIDA_DO_CORPUS["variaveis_do_ambiente"])  # as duas cópias
        self.assertEqual(self.passos_com_o_ambiente(133, voltas=1)["interpretador"] - com_133["interpretador"], 1)
        with mock.patch.dict(MEDIDA_DO_CORPUS, interpretador=com_132["interpretador"]):
            vereditos = [self.excessos({**t, "execucoes": MEDIDA_DO_CORPUS["execucoes"], "sono": 0.0})
                         for t in (com_132, com_133, {**com_133, "interpretador": com_133["interpretador"] + 1})]
        self.assertEqual(vereditos[:2], [[], []])
        self.assertEqual(len(vereditos[2]), 1)
        self.assertIn("interpretador, acima do teto", vereditos[2][0])

    def test_sono_do_hook_reprova(self):
        self.assertEqual(self.excessos(self.trabalho(sono=0.001)), ["0.001 s de sono pedidos pelo hook"])


if __name__ == "__main__":
    unittest.main()
