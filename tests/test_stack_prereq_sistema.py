"""Pacote da stack node-react: pré-requisitos de sistema (STACK-PREREQ-SISTEMA), mutação e varredura de rede (OK-12)."""
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACOTE = Path(__file__).resolve().parent.parent / "stacks" / "node-react"
PRONTO = PACOTE / "pronto.md"
SUPERFICIE = PACOTE / "skills" / "node-backend" / "superficie-de-rede.py"


def secao(texto, titulo):
    achado = re.search(rf"^## {re.escape(titulo)}\n(.*?)(?=^## |\Z)", texto, re.S | re.M)
    return achado.group(1) if achado else ""


class PreRequisitosDoSistema(unittest.TestCase):
    def setUp(self):
        self.corpo = secao(PRONTO.read_text(encoding="utf-8"), "Pré-requisitos do sistema")

    def test_secao_existe(self):
        self.assertTrue(self.corpo.strip(), "falta a seção '## Pré-requisitos do sistema' em pronto.md")

    def test_comando_de_instalacao_e_do_usuario(self):
        self.assertIn("npx playwright install --with-deps chromium", self.corpo)
        self.assertIn("sudo", self.corpo)
        self.assertIn("R-CONFORMIDADE", self.corpo)

    def test_pre_voo_so_leitura_antes_da_primeira_suite(self):
        self.assertIn("ldd", self.corpo)
        self.assertIn("PLAYWRIGHT_BROWSERS_PATH", self.corpo)
        self.assertIn("not found", self.corpo)
        self.assertIn("qa-engineer", self.corpo)
        self.assertIn("primeira suíte", self.corpo)

    def test_frase_para_pedir_ao_usuario(self):
        self.assertRegex(self.corpo, r"(?m)^> .*npx playwright install --with-deps chromium")



class MutacaoIncremental(unittest.TestCase):
    """M-4 (versao-041 E3a): o Stryker roda em modo incremental e a meta começa na primeira rodada."""

    def setUp(self):
        texto = secao(PRONTO.read_text(encoding="utf-8"), "Vermelho antes do verde, mutação e contrato")
        self.linha = next((l for l in texto.splitlines() if l.startswith("- Mutação")), "")

    def test_comando_do_stryker_e_incremental(self):
        self.assertIn("pnpm stryker run --incremental --mutate", self.linha)

    def test_meta_comeca_na_primeira_rodada_e_so_sobe(self):
        self.assertIn("começa pela pontuação da primeira rodada e só sobe", self.linha)


class SuperficieDeRede(unittest.TestCase):
    """OK-12 (versao-074 E4): varredura determinística da superfície de rede, sem rede e sem dependência."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name) / "projeto"
        self.raiz.mkdir()

    def escrever(self, relativo, texto):
        caminho = self.raiz / relativo
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(texto, encoding="utf-8")
        return caminho

    def rodar(self, *args):
        r = subprocess.run([sys.executable, "-I", str(SUPERFICIE), *(args or (str(self.raiz),))],
                           capture_output=True, text=True, timeout=60)
        return r

    def achados(self):
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stderr)
        return [l.removeprefix("superficie: ") for l in r.stdout.splitlines()[:-1]]

    def test_rota_com_autenticacao_some_e_a_sem_aparece_com_arquivo_e_linha(self):
        self.escrever("src/rotas.ts", "app.get('/privada', { preHandler: [app.authenticate] }, h)\n"
                                      "app.get('/aberta', h)\n")
        self.assertIn("src/rotas.ts:2 GET /aberta | sem autenticação reconhecida | confirmar", self.achados())
        self.assertFalse([l for l in self.achados() if "/privada" in l])

    def test_prehandler_sem_nome_de_autenticacao_nao_conta(self):
        self.escrever("a.js", "fastify.delete('/x/:id', { preHandler: [registrarAcesso] }, h)\n")
        self.assertIn("a.js:1 DELETE /x/:id | sem autenticação reconhecida | confirmar", self.achados())

    def test_gancho_de_autenticacao_no_arquivo_cobre_as_rotas_dele(self):
        self.escrever("privado.ts", "app.addHook('onRequest', app.verifyJwt)\napp.get('/conta', h)\n")
        self.escrever("publico.ts", "app.get('/saude', h)\n")
        self.assertEqual([l for l in self.achados() if "autenticação" in l],
                         ["publico.ts:1 GET /saude | sem autenticação reconhecida | confirmar"])

    def test_route_com_metodo_e_url(self):
        self.escrever("r.mjs", "server.route({\n  method: 'POST',\n  url: '/pedidos',\n  handler: h\n})\n")
        self.assertIn("r.mjs:1 POST /pedidos | sem validação na borda reconhecida | confirmar", self.achados())

    def test_pastas_de_fora_e_link_simbolico_sao_ignorados(self):
        fora = Path(self.tmp.name) / "fora"
        fora.mkdir()
        (fora / "f.js").write_text("app.get('/de-fora', h)\n", encoding="utf-8")
        for pasta in ("node_modules/pkg", "dist", "build", ".git"):
            self.escrever(f"{pasta}/i.js", "app.get('/ignorada', h)\n")
        os.symlink(fora, self.raiz / "link-pasta")
        os.symlink(fora / "f.js", self.raiz / "link.js")
        self.escrever("src/a.cjs", "app.get('/aqui', h)\n")
        saida = self.rodar().stdout
        self.assertNotIn("/de-fora", saida)
        self.assertNotIn("/ignorada", saida)
        self.assertIn("src/a.cjs:1 GET /aqui", saida)
        self.assertIn("superficie: 1 rotas,", saida)

    def test_texto_do_projeto_sai_sem_controle_e_cortado(self):
        self.escrever("a.ts", "app.get('/x\x1b[31m\u202e" + "y" * 290 + "', h)\n")
        linha = next(l for l in self.rodar().stdout.splitlines() if "/x" in l)
        self.assertNotIn("\x1b", linha)
        self.assertNotIn("\u202e", linha)
        self.assertIn("/x?[31m?y", linha)
        self.assertEqual(len(linha), 200)

    def test_duas_execucoes_dao_a_mesma_saida_e_arquivo_grande_e_pulado(self):
        self.escrever("b.ts", "app.post('/b', h)\n")
        self.escrever("a.ts", "app.get('/a', h)\n")
        self.escrever("grande.js", "app.get('/grande', h)\n" + "x" * (2 << 20))
        primeira, segunda = self.rodar().stdout, self.rodar().stdout
        self.assertEqual(primeira, segunda)
        self.assertIn("pulado: grande.js (mais de 1 MB)", primeira)
        self.assertLess(primeira.index("a.ts:1"), primeira.index("b.ts:1"))
        self.assertNotIn("/grande", primeira)

    def test_cors_aberto_com_credenciais(self):
        self.escrever("a.ts", "app.register(cors, { origin: '*', credentials: true })\n"
                              "app.register(cors, {\n  origin: true,\n  credentials: true,\n})\n"
                              "app.register(cors, { origin: ['https://a.example'], credentials: true })\n"
                              "app.register(cors, { origin: '*' })\n")
        cors = [l for l in self.achados() if "cors" in l]
        self.assertEqual(cors, ["a.ts:1 - - | cors com origin aberta e credentials | confirmar",
                                "a.ts:2 - - | cors com origin aberta e credentials | confirmar"])

    def test_limite_de_taxa_global_por_rota_e_desligado(self):
        self.escrever("rotas.ts", "app.get('/a', { config: { rateLimit: { max: 5 } } }, h)\napp.get('/b', h)\n")
        limite = [l for l in self.achados() if "limite de taxa" in l]
        self.assertEqual(limite, ["rotas.ts:2 GET /b | rota pública sem limite de taxa reconhecido | confirmar"])
        self.escrever("app.ts", "import rateLimit from '@fastify/rate-limit'\napp.register(rateLimit, { max: 100 })\n")
        self.assertFalse([l for l in self.achados() if "limite de taxa" in l])
        self.escrever("app.ts", "import rateLimit from '@fastify/rate-limit'\napp.register(rateLimit, { global: false })\n")
        self.assertEqual(len([l for l in self.achados() if "limite de taxa" in l]), 1)

    def test_rota_autenticada_nao_pede_limite_de_taxa(self):
        self.escrever("a.ts", "app.get('/conta', { onRequest: [app.auth] }, h)\n")
        self.assertEqual(self.achados(), [])

    def test_validacao_na_borda(self):
        self.escrever("a.ts", "app.post('/sem', { onRequest: auth }, h)\n"
                              "app.put('/com', { onRequest: auth, schema: { body: Corpo } }, h)\n"
                              "app.patch('/parse', { onRequest: auth }, async (request) => Corpo.parse(request.body))\n"
                              "app.get('/ler', { onRequest: auth }, h)\n")
        self.assertEqual(self.achados(), ["a.ts:1 POST /sem | sem validação na borda reconhecida | confirmar"])

    def test_metodo_de_mapa_nao_e_rota(self):
        self.escrever("a.ts", "const v = mapa.get('chave')\nconst w = cache.delete(`k`)\n")
        self.assertEqual(self.rodar().stdout.splitlines()[-1].split(";")[0], "superficie: 0 rotas, 0 achados")

    def test_ultima_linha_manda_reexecutar_e_erro_de_uso_e_2(self):
        ultima = self.rodar().stdout.splitlines()[-1]
        self.assertEqual(ultima, f"superficie: 0 rotas, 0 achados; reexecute: python3 -I {SUPERFICIE} {self.raiz}")
        self.assertEqual(self.rodar(str(self.raiz / "nao-existe")).returncode, 2)
        self.assertEqual(subprocess.run([sys.executable, "-I", str(SUPERFICIE)], capture_output=True).returncode, 2)

    def test_o_pacote_manda_rodar_e_anexar_ao_parecer(self):
        sast = secao((PACOTE / "seguranca.md").read_text(encoding="utf-8"), "SAST da stack")
        self.assertIn("stacks/node-react/skills/node-backend/superficie-de-rede.py", sast)
        self.assertIn("anexe a saída ao parecer", sast)
        self.assertTrue(SUPERFICIE.is_file())


if __name__ == "__main__":
    unittest.main()
