"""Propriedades do lançador que o hook não modela (`env`, `-S`, opção fora da tabela) e da leitura a mais.

Os testes saíram da classe `CorpusHeredocVoltaUnica` de tests/test_hooks.py (HOOKS-CORPUS-RAPIDO); a base e o corpus estão em
tests/apoio_volta_unica.py."""
from pathlib import Path
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_volta_unica import (  # noqa: E402
    BaseVoltaUnica,
    HOOKS,
    MedidaDeCpu,
    modulos_dos_hooks,
    texto)
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class LancadorDaVoltaUnica(BaseVoltaUnica, unittest.TestCase):

    def test_lancador_fora_da_tabela_com_efeito_real(self):  # item 2 do critério de fim da opção A (caminho-rev12)
        """As formas das revalidações 12 (`FORMAS_DO_LANCADOR`) dão 2 em cada hook cujo marcador está no texto (os dois
        controles sem `-a`, só no `conformidade`). Com os hooks desligados, o `env` real roda o comando em cada forma, com
        cada `env` da máquina da família dela (GNU e uutils): a sonda está viva. Só o bash e os `env` locais (R-CUSTO)."""
        _comum, conformidade, parecer = modulos_dos_hooks()
        criticos = {"conformidade": conformidade.CRITICO, "parecer": parecer.CRITICO}
        textos = [(rotulo, hook, molde.replace("{C}", self.SENTINELAS[dono]))
                  for rotulo, molde, _ in self.FORMAS_DO_LANCADOR for dono in self.SENTINELAS
                  for hook in criticos if criticos[hook].search(self.SENTINELAS[dono])
                  and not ("controle" in rotulo and hook == "parecer")]
        decisoes = self.decisoes_dos_hooks([(hook, texto) for _, hook, texto in textos])
        for rotulo, hook, texto in textos:
            with self.subTest(rotulo=rotulo, hook=hook):
                self.assertEqual(decisoes[(hook, texto)], 2, f"o {hook} libera {texto!r}")
        self.assertGreaterEqual(len(textos), 75)
        bash = shutil.which("bash")
        envs = {self.familia_do_env(e): e for e in self.envs_da_maquina()}
        if not bash or " " in bash or not envs:
            self.skipTest("bash ou env ausente, ou num caminho com espaço")
        base = self._pasta_temporaria()
        vivas = 0
        com_argv0 = {f: self.env_aceita_argv0(e) for f, e in envs.items()}
        for k, (rotulo, molde, familia) in enumerate(self.FORMAS_DO_LANCADOR):
            alvos = {f: e for f, e in envs.items() if familia in (None, f)}
            if self.USA_ARGV0.search(molde):  # o GNU anterior ao 9.5 recusa `-a`: nele a forma não é comando
                alvos = {f: e for f, e in alvos.items() if com_argv0[f]}
            with self.subTest(rotulo=rotulo):
                if not alvos:
                    self.skipTest(f"sem o env {familia} (com `-a`, se a forma o usa) nesta máquina")
                for f, env_real in alvos.items():
                    self.assertTrue(self.rodou_com_o_env(bash, env_real, molde, base / f"{k}-{f}"),
                                    f"com os hooks desligados, o env {f} ({env_real}) não roda o comando de {molde!r}")
                vivas += 1
        # com um `env` que aceita `-a` (uutils, GNU 9.5 em diante) as formas vivas são 20 ou mais; só com o GNU 9.4
        # do runner (sem `-a`) sobram os dois controles, as demais formas já foram recusadas pelos dois hooks acima
        self.assertGreaterEqual(vivas, 20 if any(com_argv0.values()) else 2)

    USA_ARGV0 = re.compile(r"(?<!\S)-[A-Za-z]*a|--ar")

    @staticmethod
    def env_aceita_argv0(env_real):
        """Se o `env` roda `-a x true` (a opção `--argv0` entrou no GNU coreutils 9.5; o 9.4 do runner a recusa)."""
        r = subprocess.run([env_real, "-a", "x", "true"], capture_output=True, text=True, timeout=10,
                           stdin=subprocess.DEVNULL)
        return r.returncode == 0

    def test_env_nao_le_opcao_depois_do_comando(self):  # item 3 do critério de fim da opção A (sonda do S2)
        """Cada `env` da máquina (GNU e uutils) entrega ao comando, sem ler, a palavra com `-` que vem depois dele
        (`env X=1 printf %s -S`): a recusa só olha até o comando, e `env X=1 git commit -S` não é falso positivo. Se um
        `env` ler, este teste fica vermelho e a regra passa a olhar até o `--` (variante da segurança)."""
        envs = self.envs_da_maquina()
        if not envs:
            self.skipTest("sem env nesta máquina")
        for env_real in envs:
            with self.subTest(env=env_real):
                r = subprocess.run([env_real, "X=1", "printf", "%s|", "-S", "-S'x'", "--split-string=x", "-i", "-a",
                                    "x", "-f", "/dev/null"], capture_output=True, text=True, timeout=10,
                                   stdin=subprocess.DEVNULL)
                self.assertEqual((r.returncode, r.stdout), (0, "-S|-S'x'|--split-string=x|-i|-a|x|-f|/dev/null|"))
        _comum, _, _ = modulos_dos_hooks()
        self.assertIsNone(_comum.reavaliacao("env X=1 git commit -S -m x && git push origin feature/x"))

    def test_mutacoes_do_lancador_ficam_vermelhas(self):  # item 4 do critério de fim da opção A (caminho-rev12)
        """Cada mutação, numa cópia de `hooks/_comum.py` carregada à parte, deixa vermelha a parte do critério que a
        pega: aceitar a opção fora da tabela (voltar a "as demais são booleanas") deixa o alfabeto do item 1 passar; parar
        no 1.º `NOME=valor` deixa passar as formas do uutils do item 2. A terceira não tem alvo: não há mais tabela de
        `env` em que tirar o `a`."""
        _comum, _, _ = modulos_dos_hooks()
        fonte = (HOOKS / "_comum.py").read_text(encoding="utf-8")
        pasta = self._pasta_temporaria()

        def mutante(nome, velho, novo):
            self.assertEqual(fonte.count(velho), 1, f"a mutação {nome} não acha o trecho")
            caminho = pasta / f"{nome}.py"
            caminho.write_text(fonte.replace(velho, novo), encoding="utf-8")
            spec = importlib.util.spec_from_file_location(f"_comum_{nome}", caminho)
            modulo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modulo)
            return modulo

        booleanas = mutante("as_demais_sao_booleanas", "    return None  # fora da tabela\n", "    return 0\n")
        alfabeto = self.textos_do_alfabeto_de_opcoes(_comum.LANCADORES, {"conformidade": self.SENTINELAS["conformidade"]},
                                                     amostra=7)
        liberados = [t for t in alfabeto if not t[3] and booleanas.reavaliacao(t[5]) is None]
        self.assertGreaterEqual(len(liberados), len([t for t in alfabeto if not t[3]]) // 2, "a mutação 1 não é pega")
        parar = mutante("parar_no_nome_valor", """        if ATRIBUICAO.match(palavra):
            i += 1
            continue
        if not palavra.startswith("-"):
            break
        consome = opcao_modelada(nome, palavra)""", """        if ATRIBUICAO.match(palavra):
            break
        if not palavra.startswith("-"):
            break
        consome = opcao_modelada(nome, palavra)""")
        uutils = [molde.replace("{C}", self.SENTINELAS["conformidade"]) for _, molde, familia in self.FORMAS_DO_LANCADOR
                  if familia == "uutils"]
        self.assertEqual(len(uutils), 4)
        for texto in uutils:
            with self.subTest(mutacao="parar no NOME=valor", texto=texto):
                self.assertIsNotNone(_comum.reavaliacao(texto), "o código de hoje recusa")
        self.assertIn(None, [parar.reavaliacao(t) for t in uutils], "a mutação 2 não é pega")
        for nome in ("ENV_COM_VALOR_CURTA", "ENV_LONGAS_COM_VALOR", "env_divide_texto", "opcoes_do_lancador"):
            self.assertFalse(hasattr(_comum, nome), f"{nome} voltou: o hook imita um env de novo")
        self.assertIsNone(_comum.opcao_modelada("env", "-a"))
        self.assertIsNone(_comum.opcao_modelada("env", "--argv0"))

    def test_propriedade_sem_marcador_atras_de_lancador_com_opcao_fora_da_tabela(self):  # item 1 do critério de fim (rev13)
        """Para cada lançador de `LANCADORES`, a palavra com `-` fora da tabela antes do comando, sem o marcador crítico,
        nunca esconde a regra da linha: se o corpo sozinho (`CORPOS_SEM_MARCADOR`, com `cat .env` e `rm -rf .git`) dá 2
        no `conformidade`, a forma `L w C`, `L w X C` (a palavra seguinte como valor), depois de `NOME=valor` e de uma
        opção modelada, e as do `env` com o corpo colado ao `S` do grupo, depois dele ou na abreviação de
        `--split-string`, também dá 2. A verdade vem da construção, e não de um `env`. Fora das formas só ficam as
        palavras em que o `env` sempre divide o texto (`-S…`, `--split-string…`): nelas o corpo não é o comando de
        `L w X C`, e o `-S` por extenso tem os controles do item 2. O tempo (120 s de CPU) é do lote inteiro, na `Guarda`."""
        corpos = self.corpos_sem_marcador()
        for fixo in self.CORPOS_FIXOS + self.CORPOS_DE_LANCADOR_RECUSADO:
            self.assertIn(fixo, corpos, f"o corpo {fixo!r} não dá 2 sozinho no modelo: o oráculo não vale")
        self.assertGreaterEqual(len(corpos), 20)
        textos = self.textos_sem_marcador(corpos)
        with MedidaDeCpu() as medida:
            decisoes = self.decidir_na_guarda([texto for _, texto in textos])
        liberadas = [(rotulo, texto) for (rotulo, texto), (codigo, _, _) in zip(textos, decisoes) if codigo != 2]
        self.assertEqual(liberadas[:10], [], f"{len(liberadas)} de {len(textos)} formas dão 0 e o corpo dá 2 sozinho")
        nomes = {rotulo.split(" / ")[0] for rotulo, _ in textos}
        self.assertEqual(nomes, set(modulos_dos_hooks()[0].LANCADORES))
        self.assertGreaterEqual(len(textos), 10_000)
        self.assertLess(medida.cpu, 120, f"a propriedade gastou {medida.texto()} para {len(textos)} formas")

    def test_formas_do_s_do_env_sem_marcador_tem_o_texto_colado_e_separado(self):  # item 1, formas do `env`
        """O gerador da propriedade produz, para o `env`, o corpo colado ao `S` do grupo (`-iS'C'`), depois dele
        (`-iS 'C'`) e na abreviação de `--split-string` (`--spl='C'`), só para o corpo que o `env` lê como o shell, e as
        formas `L w C` e `L w X C` para o resto (sem as palavras em que o `env` sempre divide o texto)."""
        grande = 10 ** 9
        textos = dict(self.textos_sem_marcador(list(self.CORPOS_FIXOS) + ["git config user.name t", "echo x; cat .env"],
                                               passo_env=grande, passo_outros=grande, passo_posicoes=grande))
        self.assertEqual(textos["env / -iS'C' / cat .env"], "env -iS'cat .env'")
        self.assertEqual(textos["env / -iS 'C' / rm -rf .git"], "env -iS 'rm -rf .git'")
        self.assertEqual(textos["env / --spl='C' / cat .env"], "env --spl='cat .env'")
        self.assertEqual(textos["env / --split-string 'C' / cat .env"], "env --split-string 'cat .env'")
        self.assertEqual(textos["env / -S'C' / cat .env"], "env -S'cat .env'")  # sem o grupo, o `S` é a primeira letra
        self.assertEqual(textos["env / -iS'C' / git config user.name t"], "env -iS'git config user.name t'")
        self.assertNotIn("env / -iS'C' / echo x; cat .env", textos)  # o `env -S` não roda `;`: só os corpos simples
        self.assertEqual(textos["env / -iu / '' / L w C / echo x; cat .env"], "env -iu echo x; cat .env")
        self.assertEqual(textos["env / --un / '' / L w X C / git config user.name t"], "env --un X git config user.name t")
        self.assertEqual(textos["timeout / -iu / '' / L w C / git config user.name t"], "timeout -iu 5 git config user.name t")
        self.assertFalse([r for r in textos if r.startswith("env / -S")
                          and (r.endswith("L w C / cat .env") or r.endswith("L w X C / cat .env"))],
                         "as palavras em que o `env` sempre divide o texto ficam fora de `L w C` e `L w X C`")

    def test_separar_lancadores_devolve_as_leituras_possiveis(self):  # item 1 da opção A (rev13), a função
        """A palavra com `-` fora da tabela tem as leituras possíveis, a sem valor primeiro; a da tabela e o `-S` por
        extenso (o `env` sempre divide) têm uma só; só o `env` tem a do texto dividido; o texto dividido com aspas abertas
        é `ValueError`, e o excesso de palavras fora da tabela, `LancadorDemais` (que também é `ValueError`)."""
        _comum, _, _ = modulos_dos_hooks()
        separar = _comum.separar_lancadores
        self.assertEqual(separar(["env", "-i", "-u", "X", "cat", ".env"]), [(["cat", ".env"], [])])
        self.assertEqual(separar(["env", "-Scat .env"]), [(["cat", ".env"], [])])
        self.assertEqual(separar(["env", "-S", "cat .env"]), [(["cat", ".env"], [])])
        self.assertEqual(separar(["env", "--split-string=cat .env"]), [(["cat", ".env"], [])])
        self.assertEqual(separar(["env", "-iu", "X", "cat", ".env"]), [(["X", "cat", ".env"], []), (["cat", ".env"], [])])
        self.assertEqual(separar(["env", "-iScat .env"]), [([], []), (["cat", ".env"], [])])
        self.assertEqual(separar(["env", "-vS", "cat .env"]), [(["cat .env"], []), ([], []), (["cat", ".env"], [])])
        self.assertEqual(separar(["env", "--spl=cat .env", "x"]), [(["x"], []), ([], []), (["cat", ".env", "x"], [])])
        self.assertEqual(separar(["sudo", "-s", "cat", ".env"]), [(["cat", ".env"], []), ([".env"], [])])
        self.assertEqual(separar(["nice", "-Z", "-n", "5", "cat"]), [(["cat"], []), (["5", "cat"], [])])
        self.assertEqual(separar(["env", "X=1", "-iu", "Y", "Z=2", "cat"]),
                         [(["Y", "Z=2", "cat"], ["X=1"]), (["cat"], ["X=1", "Z=2"])])
        self.assertEqual(separar(["env", "-iScat", "-Z", "x"]), [(["x"], []), (["cat", "x"], []), (["cat"], []), ([], [])])
        self.assertEqual(separar(["sudo", "-u", "-s", "cat"]), [(["cat"], [])], "`-u` está na tabela e leva o `-s`")
        self.assertEqual(separar(["env", "--", "cat"]), [(["cat"], [])])
        self.assertEqual(separar(["cat", ".env"]), [(["cat", ".env"], [])])
        with self.assertRaises(ValueError):
            separar(["env", "-iScat .env \""])
        with self.assertRaises(ValueError):
            separar(["env", "-S", "cat .env \""])
        self.assertEqual(_comum.TETO_FORA_DA_TABELA, 3)
        self.assertEqual(separar(["env", "-a", "-b", "-c", "cat"]), [(["cat"], []), ([], [])])
        with self.assertRaises(_comum.LancadorDemais) as demais:
            separar(["env", "-a", "-b", "-c", "-d", "cat"])
        self.assertIsInstance(demais.exception, ValueError)
        with self.assertRaises(_comum.LancadorDemais):
            separar(["env", "-Z", "env", "-Z", "env", "-Z", "env", "-Z", "cat"])  # os lançadores encadeados contam juntos

    def test_o_teste_do_s_do_env_e_um_so(self):  # item 1 da opção A (rev13): `achado_do_lancador` e a leitura
        """A recusa (`achado_do_lancador`) e a leitura (`separar_lancadores`) usam o mesmo teste do `S`
        (`texto_dividido_do_env`): para toda palavra do alfabeto do `env` fora da tabela, é `env -S` exatamente quando a
        função acha o texto dividido, e o `sudo` e o resto nunca são `env -S`."""
        _comum, _, _ = modulos_dos_hooks()
        tabela = _comum.LANCADORES["env"]
        fora = [w for w in self.alfabeto_de_opcoes(tabela) if not self.na_tabela_do_lancador(tabela, w)]
        divide = 0
        for palavra in fora:
            achado = _comum.achado_do_lancador("env", palavra)
            tem_s = _comum.texto_dividido_do_env(palavra, "x") is not None
            self.assertEqual(achado == _comum.ACHADO_DO_ENV_S, tem_s, palavra)
            self.assertIsInstance(achado, str)
            self.assertNotEqual(_comum.achado_do_lancador("sudo", palavra), _comum.ACHADO_DO_ENV_S)
            divide += tem_s
        self.assertGreaterEqual(divide, 100)
        self.assertEqual(_comum.texto_dividido_do_env("-iS'cat", "x"), ("'cat", 0, False))
        self.assertEqual(_comum.texto_dividido_do_env("-S", "x"), ("x", 1, True))
        self.assertEqual(_comum.texto_dividido_do_env("--spl", "x"), ("x", 1, False))
        self.assertEqual(_comum.texto_dividido_do_env("--split-string=y", "x"), ("y", 0, True))
        self.assertIsNone(_comum.texto_dividido_do_env("-iu", "x"))
        self.assertIsNone(_comum.texto_dividido_do_env("--sig=S", "x"))

    def test_regressoes_sem_marcador_do_lancador_dao_2(self):  # item 2 do critério de fim da opção A (caminho-rev13)
        """As seis formas da tabela da seção 1 da proposta (a `develop` recusava as seis) e `-a`, `-f` e `--un` saem 2
        no `conformidade`, e os controles da tabela seguem 2. O texto dividido com aspas abertas segue como na `develop`
        (`ilegivel`, que só recusa o que aponta para o Forge), e a opção sobre o teto recusa pelo motivo dela."""
        textos = list(self.REGRESSOES_SEM_MARCADOR + self.CONTROLES_SEM_MARCADOR)
        decisoes = self.decidir_na_guarda(textos + ["env -S'cat .env \"'", "env -a -b -c -d ls"], motivo=True)
        for texto, (codigo, _, _) in zip(textos, decisoes):
            self.assertEqual(codigo, 2, f"o conformidade libera {texto!r}")
        self.assertEqual(decisoes[-2][0], 0, "o texto dividido sem aspas fechadas segue `ilegivel`, como na develop")
        self.assertEqual(decisoes[-1][0], 2)
        self.assertIn("opção de lançador que o hook não modela", decisoes[-1][2])

    def test_sonda_viva_do_lancador_sem_marcador(self):  # item 3 do critério de fim da opção A (caminho-rev13)
        """Com os hooks desligados, cada `env` da máquina (GNU e uutils) imprime o `.env` falso nas formas que o item 2
        manda recusar: a sonda está viva, e as formas rodam de verdade. `HOME` numa pasta do `$TMPDIR`, `.env` falso,
        sem rede e sem escrever nada (R-CUSTO). O uutils desta máquina não divide o `-iS'…'` (grupo com o `i`): essa
        forma é só do GNU, e o `-vS'…'` é dos dois."""
        envs = self.envs_da_maquina()
        if not envs:
            self.skipTest("sem env nesta máquina")
        pasta = self._pasta_temporaria()
        (pasta / "home").mkdir()
        (pasta / ".env").write_text("SEGREDO_FALSO=abc123\n", encoding="utf-8")
        ambiente = {"HOME": str(pasta / "home"), "PATH": os.environ.get("PATH", "/usr/bin:/bin")}
        formas = (("-iu X cat .env", ["-iu", "X", "cat", ".env"], None), ("-iC cat .env", ["-iC", str(pasta), "cat", ".env"], None),
                  ("-vS'cat .env'", ["-vScat .env"], None), ("-iS'cat .env'", ["-iScat .env"], "gnu"))
        vistas = 0
        for env_real in envs:
            familia = self.familia_do_env(env_real)
            for rotulo, argv, so_da in formas:
                if so_da not in (None, familia):
                    continue
                with self.subTest(env=env_real, familia=familia, forma=rotulo):
                    r = subprocess.run([env_real, *argv], cwd=pasta, env=ambiente, capture_output=True, text=True,
                                       timeout=10, stdin=subprocess.DEVNULL)
                    self.assertIn("SEGREDO_FALSO=abc123", r.stdout, f"o env {familia} não roda {rotulo}: {r.stderr!r}")
                    vistas += 1
        self.assertGreaterEqual(vistas, 3 * len(envs))

    def test_tempo_do_teto_das_leituras_do_lancador(self):  # item 4 do critério de fim da opção A (caminho-rev13)
        """Com `K` palavras fora da tabela e 50 lançadores encadeados, o `conformidade` decide em menos de 0,5 s na
        `Guarda` (o vigia de produção é 3 s) e libera (o corpo `ls` não tem regra); com `K + 1`, recusa pelo teto. `K` é
        3: no máximo 27 leituras, e a medida do lote está no `--numstat` e no relatório do pedido."""
        _comum, _, _ = modulos_dos_hooks()
        k = _comum.TETO_FORA_DA_TABELA
        self.assertEqual(k, 3)

        def linha(palavras):
            return " ".join(["env", "-Z"] * palavras + ["env"] * (50 - palavras) + ["ls"])

        (dentro, _, motivo_dentro), (acima, _, motivo_acima) = self.decidir_na_guarda([linha(k), linha(k + 1)], motivo=True)
        self.assertEqual(dentro, 0, motivo_dentro)
        self.assertEqual(acima, 2)
        self.assertIn("opção de lançador que o hook não modela", motivo_acima)
        medida = self.decidir_na_guarda([linha(k)] * 20)
        self.assertLess(max(segundos for _, segundos, _ in medida), 0.5, "o teto K não decide em 0,5 s")
        self.assertLess(sum(segundos for _, segundos, _ in medida) / 20, 0.05)

    def test_estado_da_leitura_a_mais_nao_segue_adiante(self):  # item 5 do critério de fim da opção A, teste de unidade
        """Depois de `env -Z X cd /tmp/y; rm -rf .forge`, a pasta que segue é a da leitura sem valor (o `X` é o comando, e
        o `cd` não roda): o `rm` apaga o `.forge` do projeto, e dá 2. A leitura com valor tem o `cd` e deixaria a pasta
        em `/tmp/y`, onde o `rm` libera (o controle, sem o `env`): o estado dela é descartado (ADR 0013, item 5)."""
        decisoes = self.decidir_na_guarda(["env -Z X cd /tmp/y; rm -rf .forge", "cd /tmp/y; rm -rf .forge",
                                           "env -Z X cd /tmp/y; true"])
        self.assertEqual([codigo for codigo, _, _ in decisoes], [2, 0, 0])

    def test_lancador_recusado_na_leitura_a_mais_soma_a_recusa(self):  # item 5 da opção A: o estado só soma recusa
        """O lançador que o hook não modela (`flock`, `ionice`, `script`...) recusa no fim da linha, e a leitura a mais, que
        descarta o ambiente, não descarta essa recusa: `env -iu X flock f true` e `env -iS'flock f true'` dão 2 como
        `flock f true` (com o `X` como comando, a leitura sem valor não vê o `flock`)."""
        textos = ["flock f true", "env -iu X flock f true", "env -iS'flock f true'", "env -a x ionice -c3 ls",
                  "env -iu X script -qc ls /dev/null", "env -iu X ls"]
        self.assertEqual([codigo for codigo, _, _ in self.decidir_na_guarda(textos)], [2, 2, 2, 2, 2, 0])

    def test_mutacoes_das_leituras_do_lancador_ficam_vermelhas(self):  # item 5 do critério de fim da opção A (rev13)
        """Cada mutação, numa cópia limpa dos hooks, deixa vermelha a forma que a pega (com o código de hoje, a forma dá
        2): tirar a leitura "com valor" libera `env -iu X cat .env`; tirar a do "texto dividido" libera
        `env -iS'cat .env'`; deixar o estado da leitura a mais seguir adiante libera `env -Z X cd /tmp/y; rm -rf .forge`;
        tirar o teto libera a linha com `K + 1` palavras fora da tabela. O regex `-[a-zA-Z]*[uC]` e as tabelas do `env`
        não voltam (`test_mutacoes_do_lancador_ficam_vermelhas` segue exigindo a ausência)."""
        _comum, _, _ = modulos_dos_hooks()
        k_mais_1 = " ".join(["env", "-Z"] * (_comum.TETO_FORA_DA_TABELA + 1) + ["ls"])
        alvos = {"com_valor": "env -iu X cat .env", "texto_dividido": "env -iS'cat .env'",
                 "estado": "env -Z X cd /tmp/y; rm -rf .forge", "teto": k_mais_1}
        textos = list(alvos.values())
        self.assertEqual([c for c, _, _ in self.decidir_na_guarda(textos)], [2, 2, 2, 2], "o código de hoje recusa")
        mutacoes = {
            "com_valor": [("_comum.py", "                adiadas.append((base, inicio, list(lancadas), gasto, (nome, i + 1, list(dividido))))  # com valor\n",
                           "")],
            "texto_dividido": [("_comum.py", "                if texto is not None:  # no `env`, o texto dividido que a palavra tem depois do `S`\n",
                                "                if False:\n")],
            "estado": [("conformidade.py", "                self.leitura_do_segmento(palavras, comando, lancadas, pasta, dict(ramos), nivel)\n",
                        "                depois = self.leitura_do_segmento(palavras, comando, lancadas, pasta, dict(ramos), nivel)\n")],
            "teto": [("_comum.py", "                if gasto >= TETO_FORA_DA_TABELA:\n", "                if False:\n")],
        }
        for nome, mudancas in mutacoes.items():
            with self.subTest(mutacao=nome):
                hooks = self.copia_do_plugin_com(*mudancas)
                codigos = [c for c, _, _ in self.decidir_na_guarda(textos, hooks=hooks)]
                self.assertEqual(codigos[list(alvos).index(nome)], 0, f"a mutação {nome} não é pega: {codigos}")
        for nome in ("ENV_COM_VALOR_CURTA", "ENV_LONGAS_COM_VALOR", "env_divide_texto", "valor_do_split_string"):
            self.assertFalse(hasattr(_comum, nome), f"{nome} voltou: o hook imita um env de novo")
        self.assertNotIn("[uC]", (HOOKS / "_comum.py").read_text(encoding="utf-8"))
        self.assertNotIn("[uC]", (HOOKS / "conformidade.py").read_text(encoding="utf-8"))

    def test_alvos_de_escrita_leem_a_uniao_das_leituras_do_lancador(self):  # a autoria atrás de lançador (rev13)
        """`alvos_de_escrita` (a autoria dos pareceres escritos pelo Bash) soma os alvos de cada leitura possível do
        lançador: o `tee` atrás de `env -iu X` e de `env -iS'…'` conta, e a linha acima do teto não dá o alvo do `tee`
        (só a autoria depende dele), mas guarda os redirecionamentos que vieram antes."""
        _, conformidade, _ = modulos_dos_hooks()
        alvo = "docs/reviews/x.md"
        for texto in (f"env -iu X tee {alvo}", f"env -iS'tee {alvo}'", f"env -a x tee {alvo}", f"env -S 'tee {alvo}'",
                      f"env -i tee {alvo}", f"sudo -s tee {alvo}", f"echo y > {alvo}"):
            with self.subTest(texto=texto):
                self.assertEqual(conformidade.alvos_de_escrita(texto), [alvo])
        acima = conformidade.alvos_de_escrita(f"echo y > a.md; env -a -b -c -d tee {alvo}")
        self.assertEqual(acima, ["a.md"])

    def test_propriedade_leitura_a_mais_que_falha_nao_tira_recusa(self):  # item 1 do critério de fim da opção B (rev14)
        """Sem o marcador, toda forma com uma palavra fora da tabela antes do texto dividido que não fecha aspas
        (`textos_do_texto_aberto`) dá 2, qualquer que seja o corpo, e, com corpo inofensivo, pelo motivo do texto que não
        fecha (o oráculo é a construção); o `env -S<F> C` sem palavra fora da tabela segue 0 (`ilegivel`, como na
        `develop`). A palavra de 1 caractere nunca é amostrada, e o tempo (120 s de CPU) é do lote inteiro, na `Guarda`."""
        corpos = list(self.CORPOS_FIXOS + self.CORPOS_INOFENSIVOS)
        textos = self.textos_do_texto_aberto(corpos)
        with MedidaDeCpu() as medida:
            decisoes = self.decidir_na_guarda([texto for _, texto, _ in textos], motivo=True)
        erradas = [(rotulo, texto, codigo) for (rotulo, texto, recusa), (codigo, _, _) in zip(textos, decisoes)
                   if codigo != (2 if recusa else 0)]
        self.assertEqual(erradas[:10], [], f"{len(erradas)} de {len(textos)} formas fora da verdade da construção")
        sem_motivo = [texto for (_, texto, recusa), (_, _, erro) in zip(textos, decisoes)
                      if recusa and texto.endswith(self.CORPOS_INOFENSIVOS) and self.MOTIVO_DO_TEXTO_ABERTO not in erro]
        self.assertEqual(sem_motivo[:10], [])
        um = [rotulo for rotulo, _, _ in textos if re.match(r"env -[A-Za-z0-9]S<F> / ", rotulo)]
        self.assertEqual(len(um), 61 * len(self.FRAGMENTOS_ABERTOS) * len(corpos), "a palavra de 1 letra sem amostra")
        nomes = {rotulo.split(" / ")[0] for rotulo, _, _ in textos}
        self.assertTrue(set(modulos_dos_hooks()[0].LANCADORES) <= nomes)
        self.assertGreaterEqual(len(textos), 10_000)
        print(f"\n[propriedade do texto aberto] {len(textos)} formas: {medida.texto()}", file=sys.stderr)
        self.assertLess(medida.cpu, 120, f"a propriedade gastou {medida.texto()} para {len(textos)} formas")

    def test_texto_dividido_aberto_com_mais_de_uma_leitura_recusa(self):  # item 2 do critério de fim da opção B (rev14)
        """As formas do A1 da revalidação 14 (o bug `lote-leitura-hook-3`), a variante do `-S` certo depois de outra
        opção (`env -iu -S\\' cat .env`) e o falso positivo do FD18 (`env -uS'"' make`) saem 2 pelo motivo do texto que
        não fecha; o controle `env -S'"' cat .env` (uma leitura só) segue 0, como na `develop`. A função levanta
        `TextoAbertoComLeituras` (da família de `LancadorDemais`) com mais de uma leitura e `TextoDivididoAberto` com uma,
        e a autoria dá o alvo do `tee` atrás do texto que não fecha."""
        _comum, conformidade, _ = modulos_dos_hooks()
        decisoes = self.decidir_na_guarda(list(self.TEXTO_ABERTO_RECUSA) + [self.TEXTO_ABERTO_CONTROLE], motivo=True)
        for texto, (codigo, _, erro) in zip(self.TEXTO_ABERTO_RECUSA, decisoes):
            self.assertEqual(codigo, 2, f"o conformidade libera {texto!r}")
            self.assertIn(self.MOTIVO_DO_TEXTO_ABERTO, erro, texto)
            self.assertIn("use o lançador só com as opções da lista", erro, texto)
        self.assertEqual(decisoes[-1][0], 0, "com uma leitura só, o texto que não fecha segue `ilegivel`")
        self.assertTrue(issubclass(_comum.TextoAbertoComLeituras, _comum.LancadorDemais))
        self.assertFalse(issubclass(_comum.TextoDivididoAberto, _comum.LancadorDemais))
        for palavras in (["env", "-uS'", "cat"], ["env", "-iu", "-S'", "cat"], ["env", "--spl='", "cat"]):
            with self.assertRaises(_comum.TextoAbertoComLeituras):
                _comum.separar_lancadores(palavras)
        with self.assertRaises(_comum.TextoDivididoAberto):
            _comum.separar_lancadores(["env", "-S'", "cat"])
        with self.assertRaises(_comum.LancadorDemais) as teto:  # o teto não é engolido pelo texto que não fecha
            _comum.separar_lancadores(["env", "-iSenv -a -b -c ls"])
        self.assertNotIsInstance(teto.exception, _comum.TextoAbertoComLeituras)
        self.assertEqual(conformidade.alvos_de_escrita("env -aS'\"' tee docs/reviews/x.md"), ["docs/reviews/x.md"])
        self.assertEqual(conformidade.alvos_de_escrita("env -S'\"' tee docs/reviews/x.md"), [])

    def test_sonda_viva_do_texto_dividido_aberto(self):  # item 4 do critério de fim da opção B (rev14)
        """Com os hooks desligados, cada `env` da máquina (GNU e uutils) imprime o `.env` falso em `env -uS\\' cat .env`
        (o `-u` tira a variável `S'` e roda o `cat`) e não roda nada em `env -S'"' cat .env` (o texto não fecha). `HOME`
        numa pasta do `$TMPDIR`, `.env` falso, sem rede e sem escrever nada (R-CUSTO)."""
        envs = self.envs_da_maquina()
        if not envs:
            self.skipTest("sem env nesta máquina")
        pasta = self._pasta_temporaria()
        (pasta / "home").mkdir()
        (pasta / ".env").write_text("SEGREDO_FALSO=abc123\n", encoding="utf-8")
        ambiente = {"HOME": str(pasta / "home"), "PATH": os.environ.get("PATH", "/usr/bin:/bin")}
        for env_real in envs:
            with self.subTest(env=env_real, familia=self.familia_do_env(env_real)):
                roda = subprocess.run([env_real, "-uS'", "cat", ".env"], cwd=pasta, env=ambiente, capture_output=True,
                                      text=True, timeout=10, stdin=subprocess.DEVNULL)
                self.assertIn("SEGREDO_FALSO=abc123", roda.stdout, roda.stderr)
                falha = subprocess.run([env_real, "-S\"", "cat", ".env"], cwd=pasta, env=ambiente, capture_output=True,
                                       text=True, timeout=10, stdin=subprocess.DEVNULL)
                self.assertNotIn("SEGREDO_FALSO", falha.stdout)
                self.assertNotEqual(falha.returncode, 0)

    def test_mutacoes_do_texto_dividido_aberto_ficam_vermelhas(self):  # item 5 do critério de fim da opção B (rev14)
        """Cada mutação, numa cópia limpa dos hooks, muda a decisão da forma que a pega: mandar o achado a `ilegivel`
        libera `env -uS\\' cat .env`; recusar só o texto da leitura adiada libera `env -iu -S\\' cat .env`; recusar também
        com uma leitura só recusa o controle `env -S'"' cat .env`; tirar a regra do `tee` perde o alvo de
        `env -aS'"' tee docs/reviews/x.md`. Com o código de hoje, as três primeiras dão 2, 2 e 0, e a última dá o alvo."""
        guarda = {nome: forma for nome, (_, _, _, forma) in self.MUTACOES_DO_TEXTO_ABERTO.items()
                  if nome != "sem_a_regra_do_tee"}
        hoje = {"ilegivel_em_vez_de_barrar": 2, "so_a_leitura_adiada": 2, "tambem_com_uma_leitura": 0}
        textos = list(guarda.values())
        self.assertEqual([c for c, _, _ in self.decidir_na_guarda(textos)], [hoje[n] for n in guarda])
        alvo, tee = "docs/reviews/x.md", self.MUTACOES_DO_TEXTO_ABERTO["sem_a_regra_do_tee"][3]
        self.assertEqual(self.alvos_de_escrita_em(HOOKS, tee), [alvo])
        for nome, (arquivo, de, para, forma) in self.MUTACOES_DO_TEXTO_ABERTO.items():
            with self.subTest(mutacao=nome):
                hooks = self.copia_do_plugin_com((arquivo, de, para))
                if nome == "sem_a_regra_do_tee":
                    self.assertEqual(self.alvos_de_escrita_em(hooks, forma), [], "a mutação sem o tee não é pega")
                    continue
                codigos = [c for c, _, _ in self.decidir_na_guarda(textos, hooks=hooks)]
                self.assertEqual(codigos[list(guarda).index(nome)], 2 - hoje[nome], f"a mutação {nome} não é pega")

    def test_alvos_do_tee_atras_do_texto_dividido_aberto(self):  # qa 7f378b0 A1: X5 e X6 da segunda spec de mutantes
        """Atrás de lançador com mais de uma leitura e texto dividido que não fecha aspas, todo alvo depois do `tee` é alvo
        da autoria (mais de um alvo) e a opção do `tee` (`-a`, `--append`, `-i`) não é alvo."""
        _, conformidade, _ = modulos_dos_hooks()
        abre = "env -aS'\"' tee"
        casos = {
            f"{abre} docs/reviews/x.md docs/reviews/y.md": ["docs/reviews/x.md", "docs/reviews/y.md"],
            f"{abre} -a docs/reviews/x.md": ["docs/reviews/x.md"],
            f"{abre} --append docs/reviews/x.md": ["docs/reviews/x.md"],
            f"{abre} -i docs/reviews/x.md docs/reviews/y.md": ["docs/reviews/x.md", "docs/reviews/y.md"],
            f"{abre} -a -i docs/reviews/x.md --append docs/reviews/y.md": ["docs/reviews/x.md", "docs/reviews/y.md"],
        }
        for texto, esperado in casos.items():
            with self.subTest(texto=texto):
                self.assertEqual(conformidade.alvos_de_escrita(texto), esperado)

    def test_propriedade_do_lancador_que_divide_texto_com_marcador(self):  # A1 da segurança, revalidação 11
        """Todo texto da dimensão "lançador que divide texto" (com a linha crítica direta e com a sentinela de cada
        hook) dá 2 nos dois hooks quando o marcador crítico do hook está no texto: o `env` com a opção de dividir
        recusa sem que o hook divida o valor. Sem o bash: a verdade vem da construção."""
        _comum, conformidade, parecer = modulos_dos_hooks()
        criticos = {"conformidade": conformidade.CRITICO, "parecer": parecer.CRITICO}
        textos = self.textos_da_divisao(self.LINHAS_DIRETAS) + self.textos_da_divisao(self.SENTINELAS)
        decisoes = self.decisoes_dos_hooks([(hook, texto) for _, _, texto, _ in textos for hook, critico in
                                            criticos.items() if critico.search(texto)])
        for rotulo, dono, texto, _ in textos:
            self.assertRegex(texto, criticos[dono], "o corpo tem o marcador do hook dele")
            for hook, critico in criticos.items():
                if critico.search(texto):
                    with self.subTest(rotulo=rotulo, hook=hook):
                        self.assertEqual(decisoes[(hook, texto)], 2, f"o {hook} libera {texto!r}")
        self.assertGreaterEqual(len(textos), 1700)


if __name__ == "__main__":
    unittest.main()
