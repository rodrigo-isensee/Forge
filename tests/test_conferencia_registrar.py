"""S-18: `forge-check conferencia registrar` grava a conferência em formato fixo e o leitor da T-1 a lê."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402
from test_voltas import FORGE_CHECK, Raiz  # noqa: E402

ARQ = "docs/kanban/conferencias.md"
BASE = ["conferencia", "registrar", "--pedido", "xpto", "--brief", "xpto-tech-lead-1", "--modo", "brief",
        "--rodada", "1", "--resultado", "aprovado", "--merito", "—"]


def com(base, **troca):
    args = list(base)
    for chave, valor in troca.items():
        args[args.index("--" + chave) + 1] = valor
    return args


class Registrar(Raiz):
    # S-SUITE-RAPIDA: as dezenas de recusas por campo rodam o forge-check pelo bytecode em cache (apoio_forge_check_rapido);
    # `Tardio` e `SalvarArea` seguem pelo script, de ponta a ponta
    SCRIPT_DIRETO = False

    def setUp(self):
        super().setUp()
        self.gravar("KANBAN.md", "# Quadro\n")  # sem quadro o registro recusa (FC-PEDIDO-FORA)

    def lido(self):
        return (self.tmp / ARQ).read_text(encoding="utf-8")

    def test_cria_o_arquivo_com_cabecalho_e_grava_linha_de_10_colunas_com_hora_real(self):
        cod, saida, _ = self.rodar(*BASE, "--nota", "tudo certo")
        self.assertEqual(cod, 0)
        linhas = self.lido().splitlines()
        self.assertTrue(linhas[0].startswith("| data-hora | pedido | brief | modo | rodada | resultado |"))
        self.assertEqual(linhas[1], "|---|---|---|---|---|---|---|---|---|---|")
        self.assertRegex(linhas[2], r"^\| \d{4}-\d{2}-\d{2} \d{2}:\d{2} \| xpto \| xpto-tech-lead-1 \| brief \| 1 \| "
                                    r"aprovado \| — \| tudo certo \| — \| jarvis \|$")
        self.assertEqual(saida, [linhas[2]])
        self.assertEqual(len(linhas), 3)

    def test_acrescenta_sem_mexer_no_que_existe_e_conserta_falta_de_quebra(self):
        antigo = "# Registro\n\n| h | p |\n|---|---|\n| 2026-10-15 21:20 | a | b | brief | 1 | aprovado | — | |"
        self.gravar(ARQ, antigo)
        self.assertEqual(self.rodar(*com(BASE, rodada="2"))[0], 0)
        texto = self.lido()
        self.assertTrue(texto.startswith(antigo + "\n| "))
        self.assertEqual(len(texto.splitlines()), len(antigo.splitlines()) + 1)

    def test_recusas_nao_gravam(self):
        casos = [com(BASE, modo="outro"), com(BASE, merito="talvez"), com(BASE, rodada="1.5"), com(BASE, rodada="x"),
                 com(BASE, rodada="0"), com(BASE, rodada="-1"), com(BASE, resultado="a|b"),
                 com(BASE, resultado="a\nb"), com(BASE, brief="x|y"), com(BASE, pedido="p\nq"),
                 BASE + ["--nota", "a|b"], BASE + ["--nota", "a\nb"], com(BASE, resultado="  ")]
        for args in casos:
            with self.subTest(args=args):
                cod, saida, _ = self.rodar(*args)
                self.assertNotEqual(cod, 0)
                self.assertTrue(saida and saida[0].startswith("conferencia:"), saida)
                self.assertFalse((self.tmp / ARQ).exists())

    def test_recusa_separadores_de_linha_unicode_em_cada_campo(self):
        # O leitor usa str.splitlines(); U+2028, U+2029, U+0085 e afins partiriam a linha gravada (S-18-R1).
        # Cada subcaso tem o diretório próprio, para a falha de um não cair nos outros.
        separadores = {"U+2028": "\u2028", "U+2029": "\u2029", "U+0085": "\x85", "U+000B": "\x0b", "U+000C": "\x0c",
                       "U+001C": "\x1c", "U+001D": "\x1d", "U+001E": "\x1e"}
        for nome, sep in separadores.items():
            for campo in ("pedido", "brief", "resultado", "nota"):
                with self.subTest(separador=nome, campo=campo), tempfile.TemporaryDirectory() as pasta:
                    self.tmp = Path(pasta)
                    args = com(BASE, **{campo: f"a{sep}b"}) if campo != "nota" else BASE + ["--nota", f"a{sep}b"]
                    cod, saida, _ = self.rodar(*args)
                    self.assertNotEqual(cod, 0)
                    self.assertTrue(saida and saida[0].startswith("conferencia:"), saida)
                    self.assertFalse((Path(pasta) / ARQ).exists())

    def test_vocabulario_aceito(self):
        for modo in ("brief", "entrega"):
            for rodada, merito in enumerate(("s", "n", "parcial", "—"), 1):  # 0.43.3: a mesma chave duas vezes é recusada
                self.assertEqual(self.rodar(*com(BASE, modo=modo, merito=merito, rodada=str(rodada)))[0], 0)
        self.assertEqual(len(self.lido().splitlines()), 2 + 8)

    def test_mesma_chave_duas_vezes_e_recusada_sem_gravar(self):  # 0.43.3: EJ 72/78
        self.assertEqual(self.rodar(*BASE)[0], 0)
        cod, saida, _ = self.rodar(*com(BASE, resultado="reprovado", merito="n") + ["--classe", "forma"])
        self.assertEqual((cod, saida[0].startswith("conferencia: já há veredito")), (1, True))
        self.assertEqual(len(self.lido().splitlines()), 3)
        self.assertEqual(self.rodar(*com(BASE, rodada="2"))[0], 0)  # a rodada seguinte grava
        self.assertEqual(self.rodar(*com(BASE, modo="entrega"))[0], 0)  # o outro modo também

    def test_recusa_link_simbolico(self):
        alvo = self.tmp / "fora.md"
        alvo.write_text("x\n", encoding="utf-8")
        (self.tmp / ARQ).parent.mkdir(parents=True)
        (self.tmp / ARQ).symlink_to(alvo)
        self.assertNotEqual(self.rodar(*BASE)[0], 0)
        self.assertEqual(alvo.read_text(encoding="utf-8"), "x\n")

    def test_o_voltas_e_a_soma_de_rodadas_leem_a_linha_gravada(self):
        self.assertEqual(self.rodar(*com(BASE, resultado="reprovado", merito="s"), "--classe", "forma")[0], 0)
        self.assertEqual(self.rodar(*com(BASE, rodada="2"))[0], 0)
        self.assertEqual(self.rodar(*com(BASE, modo="entrega"))[0], 0)  # entrega não conta como rodada de brief
        cod, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertEqual(cod, 0)
        self.assertTrue(any(re.match(r"voltas: xpto brief inicio=\S+ \S+ minutos=\S+ ref=xpto-tech-lead-1", l)
                            for l in linhas), linhas)
        pasta = self.tmp / "sessoes"
        pasta.mkdir()
        (pasta / "a.jsonl").write_text(
            '{"type": "assistant", "timestamp": "2026-10-17T10:00:00Z", "sessionId": "s", "isSidechain": false, '
            '"message": {"id": "m1", "model": "m", "usage": {"input_tokens": 1, "output_tokens": 1}}}\n',
            encoding="utf-8")
        cod, linhas, _ = self.rodar("transcricao", "custo", str(pasta), "--entregas", "--entrega", "xpto")
        self.assertEqual(cod, 0)
        self.assertIn("| 2 |", linhas[0])
        self.assertIn("fonte=conferencias", linhas[0])


class Tardio(Raiz):  # B14 (E8): `--tardio sim|nao` mede o achado tardio, como prefixo da nota e sem coluna nova
    REPROVA2 = com(BASE, rodada="2", resultado="reprovado", merito="s") + ["--classe", "forma", "--nota", "faltou PQ"]

    def setUp(self):
        super().setUp()
        self.gravar("KANBAN.md", "# Quadro\n")

    def test_rodada_2_que_reprova_sem_tardio_recusa_sem_gravar(self):
        for resultado in ("reprovado", "não cumpriu"):
            with self.subTest(resultado=resultado):
                cod, saida, _ = self.rodar(*com(self.REPROVA2, resultado=resultado))
                self.assertEqual((cod, saida), (1, ["conferencia: --tardio sim|nao é obrigatório quando a rodada 2 ou mais não aprova"]))
                self.assertFalse((self.tmp / ARQ).exists())

    def test_com_tardio_grava_o_prefixo_na_nota_sem_coluna_nova(self):
        for valor, rodada in (("sim", "2"), ("nao", "3")):
            self.assertEqual(self.rodar(*com(self.REPROVA2, rodada=rodada), "--tardio", valor)[0], 0)
        linhas = (self.tmp / ARQ).read_text(encoding="utf-8").splitlines()
        self.assertTrue(linhas[2].endswith("| 2 | reprovado | s | tardio: sim · faltou PQ | forma | jarvis |"), linhas[2])
        self.assertTrue(linhas[3].endswith("| 3 | reprovado | s | tardio: nao · faltou PQ | forma | jarvis |"), linhas[3])
        self.assertEqual(len(linhas[2].split("|")), 12)
        self.assertEqual(self.rodar(*com(self.REPROVA2[:-2], rodada="4"), "--tardio", "sim")[0], 0)  # sem nota, só o prefixo
        self.assertIn("| s | tardio: sim | forma |", (self.tmp / ARQ).read_text(encoding="utf-8").splitlines()[4])

    def test_tardio_fora_da_reprovacao_de_rodada_2_ou_com_outro_valor_recusa(self):
        casos = {"rodada 1": com(self.REPROVA2, rodada="1") + ["--tardio", "sim"],
                 "aprovado": com(BASE, rodada="2") + ["--tardio", "nao"],
                 "outro valor": self.REPROVA2 + ["--tardio", "talvez"]}
        for nome, args in casos.items():
            with self.subTest(caso=nome):
                cod, saida, _ = self.rodar(*args)
                self.assertNotEqual(cod, 0)
                self.assertTrue(saida and saida[0].startswith("conferencia:"), saida)
                self.assertFalse((self.tmp / ARQ).exists())

    def test_rodada_1_que_reprova_e_rodada_2_que_aprova_dispensam_tardio(self):
        self.assertEqual(self.rodar(*com(self.REPROVA2, rodada="1"))[0], 0)
        self.assertEqual(self.rodar(*com(BASE, rodada="2"))[0], 0)
        self.assertNotIn("tardio:", (self.tmp / ARQ).read_text(encoding="utf-8"))


class SalvarArea(Raiz):  # E7 (FILA-23): a entrega conferida salva a área só em origin area-salva (HOME e remoto bare temporários)
    ENTREGA = com(BASE, modo="entrega", resultado="cumpriu")

    def setUp(self):
        super().setUp()
        self.home, self.bare = self.tmp / "home", self.tmp / "remoto.git"
        self.gravar("home/.gitconfig", "[user]\nname = t\nemail = t@t\n[init]\ndefaultBranch = main\n")
        self.tmp = self.area = self.home / ".forge-contrib"
        self.git(self.home, "init", "-q", "--bare", str(self.bare))
        remoto_sem_manutencao(self.bare)
        self.git(self.home, "init", "-q", str(self.area))
        self.gravar(".gitignore", "/*\n!/.gitignore\n!/docs/\n!/KANBAN.md\n!/wt/\n*.tmp\n")  # `!/wt/` alargado: só a lista branca entra
        self.gravar("KANBAN.md", "# Quadro\n")
        self.git(self.area, "remote", "add", "origin", str(self.bare))

    def git(self, pasta, *args):
        env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")} | {"HOME": str(self.home)})
        return subprocess.run(["git", "-C", str(pasta), *args], capture_output=True, text=True, env=env).stdout.strip()

    def registrar(self, *args, raiz=None, **env):
        env = {k: v for k, v in os.environ.items() if k != "FORGE_AREA_SALVAR"} | {"HOME": str(self.home)} | env
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(raiz or self.area), *(args or self.ENTREGA)],
                           capture_output=True, text=True, env=env)
        return r.returncode, r.stdout

    def salvos(self):
        return self.git(self.bare, "for-each-ref", "--format=%(refname)")

    def test_entrega_conferida_salva_so_a_lista_branca_em_area_salva(self):
        self.gravar("docs/pedidos/xpto.md", "# p\n")
        self.gravar("wt/x/arq.txt", "worktree\n")
        self.gravar("docs/ignorado.tmp", "x\n")
        cod, saida = self.registrar(GIT_DIR=str(self.tmp / "nao-existe"))  # C-1: GIT_* herdada não desvia o git da área
        self.assertEqual((cod, self.salvos()), (0, "refs/heads/area-salva"))
        self.assertIn(f"área: salva em origin/area-salva {self.git(self.area, 'rev-parse', '--short=7', 'HEAD')}", saida)
        self.assertEqual(self.git(self.bare, "log", "-1", "--format=%s", "area-salva"), "area: xpto xpto-tech-lead-1 conferida")
        arquivos = self.git(self.bare, "ls-tree", "-r", "--name-only", "area-salva").splitlines()
        self.assertLessEqual({"docs/pedidos/xpto.md", ARQ}, set(arquivos))
        self.assertFalse([a for a in arquivos if a.startswith("wt/") or a.endswith(".tmp")])  # nem -f nem add sem pathspec

    def test_nao_salva_fora_da_entrega_aprovada_desligado_ou_fora_da_area(self):
        self.gravar("../projeto/KANBAN.md", "# Quadro\n")
        projeto = self.home / "projeto"
        for args, extra in ((BASE, {}), (com(self.ENTREGA, resultado="reprovado") + ["--classe", "forma"], {}),
                            (com(self.ENTREGA, rodada="2"), {"FORGE_AREA_SALVAR": "0"}), (self.ENTREGA, {"raiz": projeto})):
            with self.subTest(args=args, extra=extra):
                cod, saida = self.registrar(*args, **extra)
                self.assertEqual((cod, "área:" in saida, self.salvos()), (0, False, ""))

    def test_avisa_sem_commit_e_sem_mudar_o_rc(self):
        token = "ghp_" + "a1" * 18
        casos = {"cópia do Forge": (".claude-plugin/plugin.json", '{"name": "forge"}'),
                 "segredo em docs/pedidos/xpto.md:2 (GitHub)": ("docs/pedidos/xpto.md", f"# p\nt {token}\n")}
        for rodada, (motivo, (rel, texto)) in enumerate(casos.items(), 1):
            with self.subTest(motivo=motivo):
                self.gravar(rel, texto)
                cod, saida = self.registrar(*com(self.ENTREGA, rodada=str(rodada)))
                self.assertEqual((cod, self.salvos()), (0, ""))
                self.assertTrue(motivo in saida and token not in saida, saida)
                (self.area / rel).unlink()

    def test_origin_do_forge_ou_com_credencial_nao_recebe(self):  # C-3, pela mesma regra do hook
        forge = json.loads((Path(FORGE_CHECK).parents[1] / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["repository"]
        for rodada, url in enumerate((forge + ".git", "https://u:segredo@exemplo.invalid/x.git"), 1):
            self.git(self.area, "remote", "set-url", "origin", url)
            self.assertIn("o origin falta, diverge, traz credencial ou é o Forge; nada enviado",
                          self.registrar(*com(self.ENTREGA, rodada=str(rodada)))[1])

    def test_remoto_que_recusa_avisa_e_o_registro_fica(self):
        shutil.rmtree(self.bare)
        cod, saida = self.registrar()
        self.assertEqual((cod, self.git(self.area, "rev-list", "--count", "HEAD")), (0, "1"))
        self.assertIn("área: aviso: remoto inacessível; nada enviado", saida)
        self.assertIn("| entrega |", (self.area / ARQ).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
