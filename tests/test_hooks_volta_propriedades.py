"""Propriedades da volta única: a reavaliação com marcador (G1, alfabeto de escapes, redução da palavra, bloco T) e o alfabeto de opções do lançador.

Os testes saíram da classe `CorpusHeredocVoltaUnica` de tests/test_hooks.py (HOOKS-CORPUS-RAPIDO); a base e o corpus estão em
tests/apoio_volta_unica.py."""
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_volta_unica import (  # noqa: E402
    BaseVoltaUnica,
    MedidaDeCpu,
    PRAZO_DO_CLAUDE_CODE_S,
    corpus_da_volta_unica,
    modulos_dos_hooks,
    texto)
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class PropriedadesDaVoltaUnica(BaseVoltaUnica, unittest.TestCase):

    def test_propriedade_da_reavaliacao_com_marcador(self):  # (5) da opção B, sobre G1 (RET-LEITURA-HOOK-B e -C)
        """Para todo texto de G1 (com a linha crítica direta e com a sentinela de cada hook), cada hook cujo marcador
        crítico (`CRITICO`) o texto tem roda e dá 2. No corpus, o caso com marcador e reavaliação
        (`REAVALIACAO_DO_TESTE`, fora das formas "não promete") tem a célula 2 (o `test_corpus_nos_dois_hooks` prova o
        código)."""
        _comum, conformidade, parecer = modulos_dos_hooks()
        criticos = {"conformidade": conformidade.CRITICO, "parecer": parecer.CRITICO}
        dados = corpus_da_volta_unica()
        no_corpus = 0
        for caso in dados["casos"]:
            for hook, critico in criticos.items():
                texto = caso.get("comando", "").replace("{CORPO}", dados["corpos"][hook])
                if caso[hook] is not None and not caso.get("nao_promete") and critico.search(texto) \
                        and self.REAVALIACAO_DO_TESTE.search(texto):
                    no_corpus += 1
                    with self.subTest(caso=f"{caso['id']}/{hook}"):
                        self.assertEqual(caso[hook], 2, f"reavaliação com marcador e célula {caso[hook]}: {texto!r}")
        textos = self.textos_de_g1(self.LINHAS_DIRETAS) + self.textos_de_g1(self.SENTINELAS)
        pedidos = [(hook, texto) for _, _, texto, _ in textos for hook, critico in criticos.items()
                   if critico.search(texto)]
        decisoes = self.decisoes_dos_hooks(pedidos)
        for rotulo, dono, texto, _ in textos:
            self.assertRegex(texto, criticos[dono], "o corpo de G1 tem o marcador do hook dele")
            for hook, critico in criticos.items():
                if critico.search(texto):
                    with self.subTest(rotulo=rotulo, hook=hook):
                        self.assertEqual(decisoes[(hook, texto)], 2, f"o {hook} libera {texto!r}")
        self.assertGreaterEqual(no_corpus, 25)
        self.assertGreaterEqual(len(textos), 4000)

    def test_propriedade_do_alfabeto_de_escapes_com_marcador(self):  # item 1 do critério de fim da opção C
        """Com o marcador crítico, toda palavra com `$'` ou `$"` fora de aspas recusa, qualquer que seja o escape. Todo
        texto gerado (`textos_do_alfabeto`) é reconhecido por `reavaliacao`, o reconhecedor que os dois hooks usam, e
        uma amostra dos escapes, em cada posição, dá 2 nos DOIS hooks reais: a propriedade separa os hooks (a mutação que
        tira a recusa de um só deixa essa parte vermelha)."""
        _comum, conformidade, parecer = modulos_dos_hooks()
        criticos = {"conformidade": conformidade.CRITICO, "parecer": parecer.CRITICO}
        todos = self.textos_do_alfabeto(self.LINHAS_DIRETAS)
        self.assertGreaterEqual(len(todos), 40_000)
        for rotulo, hook, texto in todos:
            self.assertRegex(texto, criticos[hook], "o texto tem o marcador do hook dele")
            if _comum.reavaliacao(texto) is None:
                self.fail(f"o reconhecedor libera {rotulo}: {texto!r}")
        amostra = self.ESCAPES_DO_ALFABETO[::9] + ("\\x{65}", "\\x{0000065}", "\\x{65", "\\'", '\\"', "\\$")
        reais = self.textos_do_alfabeto(self.LINHAS_DIRETAS, amostra, ("nenhum",), (("bash", "-c"), ("eval", None)))
        decisoes = self.decisoes_dos_hooks([(hook, texto) for _, hook, texto in reais])
        for rotulo, hook, texto in reais:
            with self.subTest(rotulo=rotulo):
                self.assertEqual(decisoes[(hook, texto)], 2, f"o {hook} libera {texto!r}")
        self.assertGreaterEqual(len(reais), 800)

    def test_reducao_da_palavra_como_o_bash(self):  # item 4 do critério de fim da opção B (proposta caminho-rev9)
        """A redução do hook (`_comum.reduzida`) é a do bash: para cada grafia de G1 de cada palavra de G1 que não usa
        `$'` nem `$"`, e para as bordas, a palavra reduzida é igual à que o `printf '%s'` do bash imprime (`env -i`,
        `HOME` no `$TMPDIR`, sem rede; só o bash, R-CUSTO). A palavra com expansão não se reduz (None: fica no N-HOOK1),
        e a com `$'` ou `$"` fora de aspas é INDECIDIVEL (opção C da revalidação 10). Por último, o teste exaustivo por par
        (`conferir_os_pares_contra_o_bash`)."""
        _comum, _, _ = modulos_dos_hooks()
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("bash ausente")
        todas = [grafia(w) for w in self.PALAVRAS_DE_G1 for grafia in self.GRAFIAS.values()]
        crus = [cru for cru in todas if "$'" not in cru and '$"' not in cru] + list(self.BORDAS_DA_REDUCAO)
        script = "".join(f"printf '%s\\036' {cru}\n" for cru in crus)
        casa = self._pasta_temporaria()
        saida = subprocess.run([bash, "--noprofile", "--norc", "-c", script], env={"HOME": str(casa), "LC_ALL": "C.UTF-8"},
                               cwd=casa, capture_output=True, timeout=30)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        do_bash = saida.stdout.decode("utf-8", "surrogateescape").split("\036")[:-1]
        self.assertEqual(len(do_bash), len(crus))
        for cru, valor in zip(crus, do_bash):
            with self.subTest(cru=cru):
                self.assertEqual(_comum.reduzida(cru), valor)
        for w in self.PALAVRAS_DE_G1:
            for nome, grafia in self.GRAFIAS.items():
                cru = grafia(w)
                if "$'" in cru or '$"' in cru:
                    self.assertIs(_comum.reduzida(cru), _comum.INDECIDIVEL, f"{nome} de {w}")
                else:
                    self.assertEqual(_comum.reduzida(cru), w, f"{nome} de {w}")
        for cru in self.INDECIDIVEIS:
            with self.subTest(indecidivel=cru):
                self.assertIs(_comum.reduzida(cru), _comum.INDECIDIVEL)
        for cru in self.NAO_SE_REDUZEM:
            with self.subTest(cru=cru):
                self.assertIsNone(_comum.reduzida(cru))
        self.assertGreaterEqual(len(crus), 60)
        self.conferir_os_pares_contra_o_bash()

    def test_t_orcamento_por_numero_de_palavras(self):  # item 1 do critério de fim do bloco T (proposta caminho-rev10)
        """Para cada tipo de palavra de `TIPOS_DO_ORCAMENTO` e cada tamanho, os dois hooks reais, com o vigia de
        produção, recusam a chamada com o marcador (código 2, com a regra) em menos de 3 s, e não deixam o timeout de
        10 s do Claude Code liberá-la. O texto é `: <palavras>; <linha crítica direta>`."""
        _comum, conformidade, parecer = modulos_dos_hooks()
        montados = self.modelos_montados()
        corpos = corpus_da_volta_unica()["corpos"]
        tamanhos = {"1 mil": 1000, "o teto": _comum.TETO_DE_PALAVRAS, "o teto + 1": _comum.TETO_DE_PALAVRAS + 1,
                    "o teto de caracteres": None}
        pior = 0.0
        for tipo, (unidade, por_unidade, curta) in self.TIPOS_DO_ORCAMENTO.items():
            for nome, n in tamanhos.items():
                if n is None:
                    palavras = f": {curta * ((_comum.TETO_DE_CARACTERES_DA_CHAMADA - 200) // len(curta))}"
                else:
                    palavras = f": {unidade * (n // por_unidade)}"
                for hook in ("conformidade", "parecer"):
                    texto = f"{palavras}; {corpos[hook]}"
                    with self.subTest(tipo=tipo, tamanho=nome, hook=hook):
                        codigo, erro, segundos = self.decidir_com_prazo(montados, hook, texto)
                        pior = max(pior, segundos)
                        self.assertEqual(codigo, 2, f"{codigo}: {erro.strip()}")
                        self.assertRegex(erro, r"^R-[A-Z]+: ")
                        self.assertLess(segundos, 3.0, f"{len(texto)} caracteres")
                        if n != 1000:  # `:`, o corpo e as palavras passam de 5 mil: quem recusa é o teto, não a regra do corpo
                            self.assertRegex(erro, "o teto é|linha longa demais")  # o 2.o: o teto antigo do conformidade
        print(f"\n[T] pior tempo de decisão: {pior:.2f} s", file=sys.stderr)

    def test_t_reconhecedor_da_reavaliacao_e_linear(self):  # item 2 do critério de fim do bloco T
        """`reavaliacao_das_palavras` e `separar_lancadores` sozinhas, com 50 mil palavras, rodam em menos de 2 s de CPU (a
        versão quadrática levava 8,3 s com 10 mil): o limite é do custo, e não da fila da máquina."""
        _comum, _, _ = modulos_dos_hooks()
        casos = {"shell": ["bash"] * 50_000, "shell com opção": ["bash"] * 49_999 + ["-c"], "env": ["env"] * 50_000,
                 "env -S": ["env", "-S", "x"] * 16_000, "não se reduz": [None] * 50_000, "inerte": ["x"] * 50_000,
                 "lançador com valor": ["sudo", "-u"] * 25_000, "env com NOME=valor": ["env", "X=1"] * 25_000}
        for nome, palavras in casos.items():
            with self.subTest(nome=nome), self.limite_de_tempo(5):
                with MedidaDeCpu() as medida:
                    _comum.reavaliacao_das_palavras(palavras)
                    _comum.separar_lancadores([p or "" for p in palavras])
                self.assertLess(medida.cpu, 2.0, f"{nome}: {medida.texto()}")

    def test_t_vigia_de_prazo_recusa_com_marcador_e_libera_sem(self):  # item 3 do critério de fim do bloco T
        """Um passo lento injetado (`lancador(lento=True)`: o 2.o `Hook.campo`, depois do marcador, dorme 60 s) faz os dois hooks
        recusarem a chamada com o marcador antes de 10 s, com a regra do hook (R-CONFORMIDADE, R-REVIEW), e liberarem a
        sem marcador. Sem o passo lento, a mesma chamada com marcador passa: o que recusa é o vigia, e é por construção,
        para qualquer passo lento, e não só para os que o teste 1 gera."""
        montados = self.modelos_montados()
        linhas = {"conformidade": ("git push origin feature/x", "R-CONFORMIDADE"),
                  "parecer": ("gh pr create --draft --base develop --title x --body y", "R-REVIEW")}
        for hook, (critica, regra) in linhas.items():
            with self.subTest(hook=hook, caso="sem passo lento"):
                self.assertEqual(self.decidir_com_prazo(montados, hook, critica)[0], 0)
            with self.subTest(hook=hook, caso="com marcador"):
                codigo, erro, segundos = self.decidir_com_prazo(montados, hook, critica, lento=True)
                self.assertEqual(codigo, 2, erro)
                self.assertRegex(erro, f"^{regra}: ")
                self.assertGreater(segundos, 2.5, "o vigia vence aos 3 s")
                self.assertLess(segundos, PRAZO_DO_CLAUDE_CODE_S)
            with self.subTest(hook=hook, caso="sem marcador"):
                codigo, erro, segundos = self.decidir_com_prazo(montados, hook, "echo oi", lento=True)
                self.assertEqual((codigo, erro), (0, ""))
                self.assertLess(segundos, PRAZO_DO_CLAUDE_CODE_S)

    def test_t_vigia_cobre_a_busca_do_proprio_marcador(self):
        """O marcador é um regex com `.*`, e o texto de propósito o faz levar mais de 10 s (`pr pr … api`). O vigia o
        interrompe, e o marcador desconhecido vale como marcado: recusa, em vez de o timeout liberar a chamada."""
        montados = self.modelos_montados()
        textos = {"parecer": "pr " * 20_000 + "api", "conformidade": "git " * 20_000 + "--no-verify"}
        for hook, texto in textos.items():
            with self.subTest(hook=hook):
                codigo, erro, segundos = self.decidir_com_prazo(montados, hook, texto)
                self.assertEqual(codigo, 2, erro)
                self.assertLess(segundos, PRAZO_DO_CLAUDE_CODE_S)




    def test_propriedade_do_alfabeto_de_opcoes_do_lancador(self):  # item 1 do critério de fim da opção A (caminho-rev12)
        """Com o marcador crítico, toda palavra com `-` fora da tabela de um lançador, antes do comando, recusa. Todo
        texto do alfabeto (`textos_do_alfabeto_de_opcoes`, os 12 lançadores) com a palavra fora da tabela é reconhecido
        por `reavaliacao`, o reconhecedor que os dois hooks usam; uma amostra dá 2 nos DOIS hooks reais, e toda palavra
        da tabela, antes do `git push` da sentinela, dá 2 no `conformidade` pela regra específica (R-MAIN). A palavra da
        tabela antes do `gh pr merge` sai 0 no `parecer`, que não pula lançador (A3 da segurança na revalidação 12,
        cartão R5A-COP, fora desta volta)."""
        _comum, conformidade, parecer = modulos_dos_hooks()
        criticos = {"conformidade": conformidade.CRITICO, "parecer": parecer.CRITICO}
        self.assertEqual(set(_comum.LANCADORES), {"env", "sudo", "command", "nohup", "time", "exec", "builtin", "nice",
                                                  "setsid", "stdbuf", "timeout", "xargs"})
        todos = self.textos_do_alfabeto_de_opcoes(_comum.LANCADORES, self.SENTINELAS)
        fora = [t for t in todos if not t[3]]
        self.assertGreaterEqual(len(fora), 150_000)
        for rotulo, _, _, _, hook, texto in fora:
            self.assertRegex(texto, criticos[hook], "o texto tem o marcador do hook dele")
            if _comum.reavaliacao(texto) is None:
                self.fail(f"o reconhecedor libera {rotulo}: {texto!r}")
        amostra = self.textos_do_alfabeto_de_opcoes(_comum.LANCADORES, self.SENTINELAS, amostra=199)
        reais = [t for t in amostra if not t[3]]
        explicitas = {(nome, o) for nome, tabela in _comum.LANCADORES.items() for grupo in ("booleanas", "com_valor")
                      for o in tabela.get(grupo, ())} | {(nome, "--") for nome in _comum.LANCADORES}
        na_amostra = set(amostra)
        da_tabela = list(dict.fromkeys(t for t in todos if t[3] and t[4] == "conformidade"
                                       and ((t[1], t[2]) in explicitas or t in na_amostra)))
        self.assertGreaterEqual(len(da_tabela), 200)
        pedidos = [(hook, texto) for _, _, _, _, _, texto in reais for hook, critico in criticos.items()
                   if critico.search(texto)]
        pedidos += [(hook, texto) for _, _, _, _, hook, texto in da_tabela]
        decisoes = self.decisoes_dos_hooks(pedidos)
        for rotulo, _, _, _, _, texto in reais:
            for hook, critico in criticos.items():
                if critico.search(texto):
                    with self.subTest(rotulo=rotulo, hook=hook):
                        self.assertEqual(decisoes[(hook, texto)], 2, f"o {hook} libera {texto!r}")
        for rotulo, _, _, _, hook, texto in da_tabela:
            with self.subTest(rotulo=rotulo, hook=hook):
                self.assertEqual(decisoes[(hook, texto)], 2, f"o {hook} libera {texto!r}, com a palavra da tabela")
        self.assertGreaterEqual(len(reais), 800)


if __name__ == "__main__":
    unittest.main()
