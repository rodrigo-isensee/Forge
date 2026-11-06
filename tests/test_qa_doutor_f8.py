"""QA do N-DOUTOR-F8-CAMINHO (pedido versao-033): roda o `bin/forge-doutor` completo de verdade, com `gh` falso e raiz descartável, e
confere qual caminho o aviso de branch sem proteção cita. Obrigação: cita o arquivo só se existe; sem nenhum, só a skill `ci-cd`."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_doutor_protecao_gh as tp  # noqa: E402

ENG, DOCS = "docs/engineering/protecao-de-branch.md", "docs/protecao-de-branch.md"


class CaminhoPontaAPonta(tp.Protecao):
    def aviso(self):
        r = self.doutor()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        return " ".join(r.stdout.split())

    def criar(self, caminho):
        arq = self.proj / caminho
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text("# passo a passo\n", encoding="utf-8")

    def test_nenhum_arquivo_cita_so_a_skill(self):  # fronteira: nenhum candidato existe
        self.sem_protecao("main")
        a = self.aviso()
        self.assertIn("seguindo a skill `ci-cd`.", a)
        self.assertNotIn("protecao-de-branch.md", a)

    def test_so_o_de_docs_engineering(self):
        self.sem_protecao("main")
        self.criar(ENG)
        a = self.aviso()
        self.assertIn(f"o passo a passo em {ENG} (skill `ci-cd`)", a)
        self.assertNotIn(f"em {DOCS}", a)

    def test_so_o_de_docs(self):
        self.sem_protecao("main")
        self.criar(DOCS)
        a = self.aviso()
        self.assertIn(f"o passo a passo em {DOCS} (skill `ci-cd`)", a)
        self.assertNotIn(ENG, a)

    def test_os_dois_existem_cita_so_o_de_engineering(self):  # ordem de precedência
        self.sem_protecao("main")
        self.criar(ENG)
        self.criar(DOCS)
        a = self.aviso()
        self.assertIn(f"em {ENG} (skill", a)
        self.assertNotIn(f"em {DOCS}", a)

    def test_diretorio_ou_link_quebrado_com_o_nome_do_arquivo_nao_conta(self):  # borda: existe o nome, não é arquivo
        self.sem_protecao("main")
        (self.proj / ENG).mkdir(parents=True)  # diretório
        (self.proj / "docs").mkdir(exist_ok=True)
        (self.proj / DOCS).symlink_to(self.proj / "nao-existe.md")  # link pendente
        a = self.aviso()
        self.assertIn("seguindo a skill `ci-cd`.", a)
        self.assertNotIn("protecao-de-branch.md", a)

    def test_o_caminho_vale_para_cada_branch_sem_protecao(self):  # as três branches citam o mesmo guia
        for ramo in ("develop", "homolog", "main"):
            self.sem_protecao(ramo)
        self.criar(ENG)
        a = self.aviso()
        self.assertEqual(a.count(f"o passo a passo em {ENG} (skill `ci-cd`)"), 3)
        for ramo in ("develop", "homolog", "main"):
            self.assertIn(f"A branch {ramo} no GitHub está sem proteção", a)

    def test_protegidas_continuam_em_silencio_mesmo_com_o_arquivo(self):  # o caminho não vaza sem problema
        self.criar(ENG)
        r = self.doutor()
        self.assertEqual((r.returncode, r.stdout), (0, ""))


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for nome in CaminhoPontaAPonta.__dict__:
        if nome.startswith("test_"):
            suite.addTest(CaminhoPontaAPonta(nome))
    return suite


if __name__ == "__main__":
    unittest.main()
