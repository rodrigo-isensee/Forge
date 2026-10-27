"""Corpus da volta única, oráculos (redireções, enumerador, bash) e conferências do próprio corpus.

Os testes saíram da classe `CorpusHeredocVoltaUnica` de tests/test_hooks.py (HOOKS-CORPUS-RAPIDO); a base e o corpus estão em
tests/apoio_volta_unica.py."""
from pathlib import Path
from unittest import mock
import collections
import concurrent.futures
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_volta_unica import (  # noqa: E402
    BaseVoltaUnica,
    CARTOES_DO_NAO_PROMETE,
    EXIGE_NENHUMA_MARCA,
    FIXTURES,
    IDS_DA_VOLTA_UNICA,
    MINIMO_POR_CLASSE,
    NAO_PROMETE,
    RAIZ,
    REGRAS_DA_VOLTA_UNICA,
    corpus_da_volta_unica,
    modulos_dos_hooks,
    rodar,
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

        trabalhadores = max(1, min(4, (os.cpu_count() or 2) // 2))
        with concurrent.futures.ThreadPoolExecutor(max_workers=trabalhadores) as pool:
            reais = list(pool.map(pelo_hook, pedidos))
        no_lote = self.decidir_em_lote(pedidos, montados)
        for pedido, real, lote in zip(pedidos, reais, no_lote):
            with self.subTest(hook=pedido[0], texto=pedido[1][:80]):
                self.assertEqual(lote, real, f"o lote dá {lote} e o hook real dá {real}: {pedido[1]!r}")
        self.assertEqual(set(reais), {0, 2}, "a amostra tem de ter recusa e liberação")

    def test_corpus_nos_dois_hooks(self):
        inicio = time.monotonic()
        casos = self.fixtures_do_corpus()
        self.assertEqual(self.executar_em_lote(casos), len(casos))
        self.assertLess(time.monotonic() - inicio, 60, "o corpus roda em paralelo, como os fixtures")

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


if __name__ == "__main__":
    unittest.main()
