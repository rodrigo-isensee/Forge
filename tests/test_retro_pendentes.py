"""AE5.1 (v0478 E58.61): `forge-check retro --pendentes` lista as tags vX.Y.Z da main com mais de 24 h em `--agora` que nenhuma
retrospectiva cobre (`Cobre:` no cabeçalho); um teste por guarda, com o ramo de falha. O relógio é argumento: nada aqui depende da hora."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_git_herdado  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")
MODELO = RAIZ / "docs" / "retrospectivas" / "_modelo.md"
AGORA = "2026-11-13T09:00:00-03:00"  # v0.3.0 tem 23 h; v0.1.0 e v0.2.0, mais de 24 h
CHEIA = ("# Retro\n\nCobre: {cobre}\n\n## 1. Dados do pedido\nlead 10 min.\n\n## 2. O que funcionou\nx.\n\n"
         "## 3. O que atrapalhou (fatos)\ny.\n\n## 4. Causa nova e a proposta\nz.\n")
PENDENTES_12 = ["retro: pendente v0.1.0 tag=2026-11-10T10:00-03:00 horas=71",
                "retro: pendente v0.2.0 tag=2026-11-11T10:00-03:00 horas=47"]


class RetroPendentes(unittest.TestCase):
    """c1 (v0.1.0, 10/11 10h) → c2 (v0.2.0 e v0.2.0-rc, 11/11 10h) → c3 (v0.3.0, 12/11 10h) em origin/main; c4 (v0.9.0, 11/11) fora da main."""

    @classmethod
    def setUpClass(cls):
        cls._pasta = tempfile.TemporaryDirectory()
        cls.raiz = Path(cls._pasta.name) / "repo"
        cls.raiz.mkdir()
        cls.git("init", "-q", "-b", "main")
        shas = {}
        for nome, dia in (("c1", "10"), ("c2", "11"), ("c3", "12")):
            shas[nome] = cls.commit(nome, f"2026-11-{dia}T10:00:00-03:00")
        cls.git("switch", "-q", "-c", "lateral", shas["c3"])
        shas["c4"] = cls.commit("c4", "2026-11-11T12:00:00-03:00")
        for tag, sha in (("v0.1.0", "c1"), ("v0.2.0", "c2"), ("v0.2.0-rc", "c2"), ("v0.3.0", "c3"), ("v0.9.0", "c4")):
            cls.git("tag", tag, shas[sha])
        cls.git("update-ref", "refs/remotes/origin/main", shas["c3"])

    @classmethod
    def tearDownClass(cls):
        cls._pasta.cleanup()

    @classmethod
    def git(cls, *args, data=None):
        env = sem_git_herdado(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
                              **({"GIT_AUTHOR_DATE": data, "GIT_COMMITTER_DATE": data} if data else {}))
        return subprocess.run(["git", "-C", str(cls.raiz), *args], check=True, capture_output=True, text=True, env=env).stdout.strip()

    @classmethod
    def commit(cls, nome, data):
        (cls.raiz / nome).write_text(nome, encoding="utf-8")
        cls.git("add", nome)
        cls.git("commit", "-q", "-m", nome, data=data)
        return cls.git("rev-parse", "HEAD")

    def setUp(self):
        self.retros = self.raiz / "docs" / "retrospectivas"
        self.retros.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.raiz / "docs")  # o link da pasta sai como link; o alvo fica

    def gravar(self, nome, texto):
        (self.retros / nome).write_text(texto, encoding="utf-8")

    def rodar(self, *args, agora=AGORA):
        env = {"HOME": str(Path(self._pasta.name) / "home"), "PATH": "/usr/bin:/bin"}  # ambiente limpo: nada de GIT_* nem CI herdado
        cmd = [sys.executable, "-I", FORGE_CHECK, "--raiz", str(self.raiz), "retro", "--pendentes", *(["--agora", agora] if agora else []), *args]
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return r.returncode, r.stdout.splitlines(), r.stderr.splitlines()

    def test_sem_retro_lista_so_as_tags_vxyz_da_main_com_mais_de_24h(self):
        self.assertEqual(self.rodar(), (1, PENDENTES_12 + ["retro: pendentes=2"], []))

    def test_24h_exatas_nao_e_pendente_e_25h_e(self):
        cod, linhas, _ = self.rodar(agora="2026-11-13T10:00:00-03:00")  # a tupla inteira: a base, de saída vazia, falha por asserção
        self.assertEqual((cod, linhas), (1, [l.replace("=71", "=72").replace("=47", "=48") for l in PENDENTES_12] + ["retro: pendentes=2"]))
        cod, linhas, _ = self.rodar(agora="2026-11-13T11:00:00-03:00")
        self.assertEqual((cod, linhas[-2:]), (1, ["retro: pendente v0.3.0 tag=2026-11-12T10:00-03:00 horas=25", "retro: pendentes=3"]))

    def test_retro_completa_cobre_varias_versoes(self):
        self.gravar("2026-11-12-p.md", CHEIA.format(cobre="v0.1.0, v0.2.0,"))  # a vírgula do fim não vira versão vazia
        self.assertEqual(self.rodar(), (0, ["retro: pendentes=0"], []))

    def test_retros_vem_do_raiz_pedidos_quando_dado(self):
        controle = self.raiz / "docs" / "controle" / "docs" / "retrospectivas"
        controle.mkdir(parents=True)
        (controle / "p.md").write_text(CHEIA.format(cobre="v0.1.0"), encoding="utf-8")
        self.gravar("p.md", CHEIA.format(cobre="v0.2.0"))  # a da raiz do git fica fora com --raiz-pedidos
        self.assertEqual(self.rodar("--raiz-pedidos", str(self.raiz / "docs" / "controle")), (1, [PENDENTES_12[1], "retro: pendentes=1"], []))

    def test_cobre_com_versao_que_nao_existe_avisa_e_nao_cobre(self):
        self.gravar("p.md", CHEIA.format(cobre="v0.1.0, v0.7.0"))
        cod, linhas, erros = self.rodar()
        self.assertEqual((cod, linhas), (1, [PENDENTES_12[1], "retro: pendentes=1"]))
        self.assertEqual(erros, ['retro: aviso: "p.md": Cobre: "v0.7.0" nao e tag vX.Y.Z da main; nao cobre'])

    def test_tag_fora_da_main_nao_e_pendente_nem_cobre(self):
        self.gravar("p.md", CHEIA.format(cobre="v0.9.0"))
        cod, linhas, erros = self.rodar()
        self.assertEqual((cod, linhas), (1, PENDENTES_12 + ["retro: pendentes=2"]))
        self.assertEqual(erros, ['retro: aviso: "p.md": Cobre: "v0.9.0" nao e tag vX.Y.Z da main; nao cobre'])

    def test_retro_so_com_o_cabecalho_do_modelo_nao_cobre(self):
        self.gravar("p.md", MODELO.read_text(encoding="utf-8").replace("Cobre: vX.Y.Z, vX.Y.Z", "Cobre: v0.1.0, v0.2.0"))
        cod, linhas, erros = self.rodar()
        self.assertEqual((cod, linhas[-1]), (1, "retro: pendentes=2"))
        self.assertEqual(erros, ['retro: aviso: "p.md": secao sem corpo: dados do pedido, o que funcionou, o que atrapalhou, causa nova; nao cobre'])

    def test_modelo_preenchido_cobre_e_os_dois_modelos_sao_iguais(self):
        texto = MODELO.read_text(encoding="utf-8")
        self.assertEqual(texto, (RAIZ / "templates/projeto/docs/retrospectivas/_modelo.md").read_text(encoding="utf-8"))
        preenchido = "\n".join("texto." if l.startswith("<!--") else l for l in texto.splitlines())
        self.gravar("p.md", preenchido.replace("Cobre: vX.Y.Z, vX.Y.Z", "Cobre: v0.1.0, v0.2.0"))
        self.assertEqual(self.rodar(), (0, ["retro: pendentes=0"], []))

    def test_secao_sem_corpo_nao_cobre(self):
        self.gravar("p.md", CHEIA.format(cobre="v0.1.0").replace("x.\n", ""))
        cod, _, erros = self.rodar()
        self.assertEqual((cod, erros), (1, ['retro: aviso: "p.md": secao sem corpo: o que funcionou; nao cobre']))

    def test_retro_sem_cobre_nao_avisa(self):
        self.gravar("antiga.md", "# Retro antiga\n\n## Notas\n")
        self.assertEqual(self.rodar(), (1, PENDENTES_12 + ["retro: pendentes=2"], []))

    def test_cobre_depois_da_primeira_secao_nao_vale(self):
        self.gravar("p.md", CHEIA.format(cobre="v0.1.0") + "Cobre: v0.2.0\n")
        self.assertEqual(self.rodar(), (1, [PENDENTES_12[1], "retro: pendentes=1"], []))

    def test_arquivo_com_sublinhado_fica_fora(self):
        self.gravar("_rascunho.md", CHEIA.format(cobre="v0.1.0, v0.2.0"))
        self.assertEqual(self.rodar(), (1, PENDENTES_12 + ["retro: pendentes=2"], []))

    def test_link_e_arquivo_grande_nao_cobrem(self):
        fora = Path(self._pasta.name) / "fora.md"
        fora.write_text(CHEIA.format(cobre="v0.1.0"), encoding="utf-8")
        (self.retros / "link.md").symlink_to(fora)
        self.gravar("grande.md", CHEIA.format(cobre="v0.2.0") + "x" * 1_000_000)
        cod, linhas, erros = self.rodar()
        self.assertEqual((cod, linhas), (1, PENDENTES_12 + ["retro: pendentes=2"]))
        self.assertEqual(erros, [f'retro: aviso: "{n}": link, pasta ou acima de 1000000 bytes; nao cobre' for n in ("grande.md", "link.md")])

    def test_pasta_de_retros_que_e_link_fica_fora(self):
        fora = Path(self._pasta.name) / "outras"
        fora.mkdir(exist_ok=True)
        (fora / "p.md").write_text(CHEIA.format(cobre="v0.1.0, v0.2.0"), encoding="utf-8")
        self.retros.rmdir()
        self.retros.symlink_to(fora)
        self.assertEqual(self.rodar(), (1, PENDENTES_12 + ["retro: pendentes=2"], []))

    def test_fifo_e_pasta_nao_cobrem_nem_travam(self):
        os.mkfifo(self.retros / "fifo.md")  # sem escritor: abrir sem O_NONBLOCK travaria o forge-check
        (self.retros / "pasta.md").mkdir()
        cod, linhas, erros = self.rodar()
        self.assertEqual((cod, linhas), (1, PENDENTES_12 + ["retro: pendentes=2"]))
        self.assertEqual(erros, [f'retro: aviso: "{n}": link, pasta ou acima de 1000000 bytes; nao cobre' for n in ("fifo.md", "pasta.md")])

    def test_pasta_docs_que_e_link_fica_fora(self):
        controle = self.raiz / "controle"  # --raiz-pedidos só vale dentro da raiz do repositório ou de ~/.forge-contrib
        (Path(self._pasta.name) / "docs-de-fora" / "retrospectivas").mkdir(parents=True, exist_ok=True)
        (Path(self._pasta.name) / "docs-de-fora" / "retrospectivas" / "p.md").write_text(CHEIA.format(cobre="v0.1.0, v0.2.0"), encoding="utf-8")
        controle.mkdir(exist_ok=True)
        if not (controle / "docs").is_symlink():
            (controle / "docs").symlink_to(Path(self._pasta.name) / "docs-de-fora")
        self.assertEqual(self.rodar("--raiz-pedidos", str(controle)), (1, PENDENTES_12 + ["retro: pendentes=2"], []))

    def test_desde_ignora_as_tags_anteriores(self):
        self.assertEqual(self.rodar("--desde", "v0.2.0"), (1, [PENDENTES_12[1], "retro: pendentes=1"], []))

    def test_entrada_ilegivel_da_2(self):
        for args, agora in (((), None), ((), "ontem"), (("--main", "origin/main~0"), AGORA), (("--desde", "0.1"), AGORA),
                            (("--main", "nao-existe"), AGORA)):
            with self.subTest(args=args, agora=agora):
                cod, linhas, _ = self.rodar(*args, agora=agora)
                self.assertEqual((cod, linhas), (2, []))

    def test_main_local_com_outra_ponta(self):
        self.assertEqual(self.rodar("--main", "lateral"),  # a lateral alcança também a v0.9.0 (11/11 12h); a ordem é a da versão
                         (1, PENDENTES_12 + ["retro: pendente v0.9.0 tag=2026-11-11T12:00-03:00 horas=45", "retro: pendentes=3"], []))

    def test_pendentes_e_pedido_sao_exclusivos(self):
        r = subprocess.run([sys.executable, "-I", FORGE_CHECK, "--raiz", str(self.raiz), "retro", "--pendentes", "--pedido", "x"],
                           capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "HOME": os.devnull})
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
