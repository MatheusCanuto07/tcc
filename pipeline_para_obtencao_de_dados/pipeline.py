"""
Pipeline iterativo de obtenção, tratamento e geração de SQL
para a aplicação web do TCC (empresas de TI de Contagem/MG).

Arquitetura pensada para o ciclo: rodar -> falhar em alguma fonte ->
corrigir URL/código -> rodar de novo. Cada fonte é independente, o progresso
fica em pipeline_estado.json e artefatos em dados_tratados/cache_*.json.

Uso (na pasta deste arquivo):
    python pipeline.py --status
    python pipeline.py
    python pipeline.py --only cnae
    python pipeline.py --only cnpj,cnefe
    python pipeline.py --force --only cnpj
    python pipeline.py --unify
    python pipeline.py --reset-estado

Dependências sugeridas (instalar à parte):
    pip install requests openpyxl

Pastas mensais de CNPJ e caminhos do FTP do IBGE mudam com o tempo:
verifique CNPJ_PASTA_MES e os comentários "VERIFICAR URL".
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
import traceback
import zipfile
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional
from xml.etree import ElementTree as ET

import requests

# ---------------------------------------------------------------------------
# Constantes do recorte do trabalho
# ---------------------------------------------------------------------------

# Código IBGE do município de Contagem (MG).
CODIGO_IBGE_CONTAGEM = "3118601"

# Subclasses CNAE da divisão 62 (atividade principal) usadas no TCC.
CNAE_TI_DIVISAO_62 = {
    "6201501",  # desenvolvimento de programas sob encomenda
    "6201502",  # web design
    "6202300",  # programas customizáveis
    "6203100",  # programas não customizáveis
    "6204000",  # consultoria em TI
    "6209100",  # suporte técnico e outros serviços em TI
}

# Situação cadastral "ativa" no layout da Receita.
SITUACAO_ATIVA = "02"

# VERIFICAR URL: pasta datada dos ZIPs de CNPJ.
# O host oficial arquivos.receitafederal.gov.br passou a exigir autenticação/share
# (Nextcloud/SERPRO) e não lista mais pastas AAAA-MM abertas. Espelho público
# com os mesmos arquivos: https://dados-abertos-rf-cnpj.casadosdados.com.br/arquivos/
# Formato da pasta: AAAA-MM-DD (ex.: 2026-10-13). Confira o índice antes de rodar.
CNPJ_PASTA_MES = "2026-10-13"
CNPJ_BASE_URL = (
    "https://dados-abertos-rf-cnpj.casadosdados.com.br/arquivos/"
    f"{CNPJ_PASTA_MES}"
)

# CNAE-Subclasses 2.3 (CONCLA / IBGE) — XLSX oficial.
# VERIFICAR URL se a CONCLA mover o arquivo.
CNAE_XLSX_URL = (
    "https://concla.ibge.gov.br/images/concla/documentacao/"
    "CNAE_Subclasses_2_3_Estrutura_Detalhada.xlsx"
)

# CNEFE Contagem (CSV dentro de ZIP) — FTP IBGE, Censo 2022.
# VERIFICAR URL: listagem em .../CSV/Municipio/31_MG/
CNEFE_CONTAGEM_URL = (
    "https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/"
    "Censo_Demografico_2022/Arquivos_CNEFE/CSV/Municipio/31_MG/"
    "3118601_CONTAGEM.zip"
)

# Malha de bairros MG (Censo 2022) — shapefile em ZIP.
# VERIFICAR URL no geoftp se o IBGE publicar ano novo.
MALHAS_BAIRROS_MG_URL = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/"
    "malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/"
    "bairros/shp/UF/MG_bairros_CD2022.zip"
)

# Malha municipal MG 2024 (contorno) — caminho UFs/MG no geoftp.
# VERIFICAR URL: pastas anuais em malhas_municipais/.
# Nota: .../Brasil/BR/BR_Municipios_2024.zip retornou 404; o ZIP nacional
# válido está em .../municipio_2024/Brasil/BR_Municipios_2024.zip (sem /BR/).
MALHAS_MUNICIPIOS_URL = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/"
    "malhas_municipais/municipio_2024/UFs/MG/MG_Municipios_2024.zip"
)

# CEMPRE via API SIDRA — mesmo universo do CNPJ do TCC:
# município Contagem (n6/3118601) + divisão CNAE 62 (c12762/117594).
# Tabela 9528 (série a partir de 2022): unidades locais por seção/divisão/grupo/classe.
# VERIFICAR: https://sidra.ibge.gov.br/tabela/9528
# Código SIDRA da divisão 62: 117594 (descritor C12762 da tabela 9528).
# Classes da divisão 62 (para detalhe): 117596..117600.
CEMPRE_TABELA = "9528"
CEMPRE_VAR_UNIDADES_LOCAIS = "706"
CEMPRE_CNAE_DIVISAO_62 = "117594"
CEMPRE_CNAE_CLASSES_62 = "117596,117597,117598,117599,117600"
CEMPRE_SIDRA_URL = (
    f"https://apisidra.ibge.gov.br/values/t/{CEMPRE_TABELA}"
    f"/n6/{CODIGO_IBGE_CONTAGEM}"
    f"/v/{CEMPRE_VAR_UNIDADES_LOCAIS}"
    f"/p/last%201"
    f"/c12762/{CEMPRE_CNAE_DIVISAO_62}"
)
CEMPRE_SIDRA_URL_CLASSES = (
    f"https://apisidra.ibge.gov.br/values/t/{CEMPRE_TABELA}"
    f"/n6/{CODIGO_IBGE_CONTAGEM}"
    f"/v/{CEMPRE_VAR_UNIDADES_LOCAIS}"
    f"/p/last%201"
    f"/c12762/{CEMPRE_CNAE_CLASSES_62}"
)

HTTP_HEADERS = {
    "User-Agent": (
        "tcc-contagem-ti/1.0 (pesquisa academica; contato: aluno PUC Minas Contagem)"
    ),
    "Accept": "*/*",
}

# Diretórios locais de trabalho (criados sob demanda).
DIR_BASE = Path(__file__).resolve().parent
DIR_BRUTO = DIR_BASE / "dados_brutos"
DIR_TRATADO = DIR_BASE / "dados_tratados"
DIR_SQL = DIR_BASE / "sql_gerado"
ARQUIVO_ESTADO = DIR_BASE / "pipeline_estado.json"

# Nomes canônicos das etapas que o CLI aceita.
FONTES_DISPONIVEIS = ("cnpj", "cnae", "cnefe", "malhas", "cempre")
ETAPA_UNIFICAR = "unificar"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("pipeline_tcc")


# ---------------------------------------------------------------------------
# Erros acionáveis e estado entre execuções
# ---------------------------------------------------------------------------

class FonteErro(Exception):
    """Falha de uma fonte, com contexto para o próximo ajuste manual."""

    def __init__(
        self,
        fonte: str,
        mensagem: str,
        url: str = "",
        sugestao: str = "",
        causa: Optional[BaseException] = None,
    ) -> None:
        self.fonte = fonte
        self.mensagem = mensagem
        self.url = url
        self.sugestao = sugestao
        self.causa = causa
        super().__init__(mensagem)


def _agora_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def garantir_diretorios() -> None:
    """Cria pastas locais usadas pelo pipeline."""
    for pasta in (DIR_BRUTO, DIR_TRATADO, DIR_SQL):
        pasta.mkdir(parents=True, exist_ok=True)


def estado_vazio() -> dict[str, Any]:
    fontes = {
        nome: {
            "status": "pendente",
            "atualizado_em": None,
            "url_principal": "",
            "artefato": str(DIR_TRATADO / f"cache_{nome}.json"),
            "erro": None,
            "sugestao": None,
        }
        for nome in FONTES_DISPONIVEIS
    }
    fontes[ETAPA_UNIFICAR] = {
        "status": "pendente",
        "atualizado_em": None,
        "url_principal": "",
        "artefato": str(DIR_TRATADO / "estabelecimentos_ti_contagem.json"),
        "erro": None,
        "sugestao": None,
    }
    return {"atualizado_em": _agora_iso(), "fontes": fontes}


def carregar_estado() -> dict[str, Any]:
    """Lê pipeline_estado.json ou cria estrutura inicial."""
    garantir_diretorios()
    if not ARQUIVO_ESTADO.exists():
        estado = estado_vazio()
        salvar_estado(estado)
        return estado
    try:
        estado = json.loads(ARQUIVO_ESTADO.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        estado = estado_vazio()
    # Garante chaves novas se o arquivo for antigo.
    base = estado_vazio()
    fontes = estado.setdefault("fontes", {})
    for nome, meta in base["fontes"].items():
        fontes.setdefault(nome, meta)
    return estado


def salvar_estado(estado: dict[str, Any]) -> None:
    garantir_diretorios()
    estado["atualizado_em"] = _agora_iso()
    ARQUIVO_ESTADO.write_text(
        json.dumps(estado, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def caminho_cache(fonte: str) -> Path:
    return DIR_TRATADO / f"cache_{fonte}.json"


def salvar_cache_fonte(fonte: str, dados: dict[str, Any]) -> Path:
    garantir_diretorios()
    caminho = caminho_cache(fonte)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return caminho


def carregar_cache_fonte(fonte: str) -> Optional[dict[str, Any]]:
    caminho = caminho_cache(fonte)
    if not caminho.exists():
        return None
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Cache de %s ilegível (%s). Refaça a fonte.", fonte, exc)
        return None


def imprimir_erro_acionavel(
    fonte: str,
    url: str,
    mensagem: str,
    sugestao: str,
    detalhe: str = "",
) -> None:
    """Mensagem clara no stdout para o ciclo corrigir -> rerodar."""
    bloco = [
        "",
        "=" * 72,
        f"FALHA NA FONTE: {fonte}",
        f"URL / base: {url or '(não informada)'}",
        f"O que aconteceu: {mensagem}",
        f"Próximo passo sugerido: {sugestao}",
    ]
    if detalhe:
        bloco.append(f"Detalhe técnico: {detalhe}")
    bloco.extend(
        [
            f"Estado: {ARQUIVO_ESTADO}",
            f"Reexecutar só esta fonte: python pipeline.py --force --only {fonte}",
            "=" * 72,
            "",
        ]
    )
    print("\n".join(bloco), file=sys.stderr)


def marcar_fonte_ok(estado: dict[str, Any], fonte: str, url: str, artefato: Path) -> None:
    estado["fontes"][fonte] = {
        "status": "ok",
        "atualizado_em": _agora_iso(),
        "url_principal": url,
        "artefato": str(artefato),
        "erro": None,
        "sugestao": None,
    }
    salvar_estado(estado)


def marcar_fonte_erro(
    estado: dict[str, Any],
    fonte: str,
    url: str,
    erro: str,
    sugestao: str,
) -> None:
    estado["fontes"][fonte] = {
        "status": "erro",
        "atualizado_em": _agora_iso(),
        "url_principal": url,
        "artefato": str(caminho_cache(fonte)),
        "erro": erro,
        "sugestao": sugestao,
    }
    salvar_estado(estado)


# ---------------------------------------------------------------------------
# Schema comum consumido pela aplicação web
# ---------------------------------------------------------------------------

@dataclass
class EstabelecimentoTI:
    """Registro unificado que a aplicação web consulta."""

    cnpj_basico: str
    cnpj_completo: str
    razao_social: str
    nome_fantasia: str
    cnae_principal: str
    cnae_descricao: str
    porte: str
    capital_social: Optional[float]
    situacao_cadastral: str
    is_mei: bool
    logradouro: str
    numero: str
    bairro: str
    cep: str
    municipio_ibge: str
    latitude: Optional[float]
    longitude: Optional[float]
    # endereco_completo | somente_cep | sem_coordenada
    nivel_juncao_cnefe: str
    # valor bruto de NV_GEO_COORD do CNEFE, quando houver
    nivel_geo_cnefe: Optional[str]
    area_municipio: Optional[str]
    data_fotografia: str
    fonte_origem: str = "integracao_cnpj_cnefe_cnae"


# ---------------------------------------------------------------------------
# Utilitários de I/O e normalização
# ---------------------------------------------------------------------------

def baixar_arquivo(url: str, destino: Path, timeout: int = 120) -> Path:
    """
    Baixa um arquivo remoto com a biblioteca requests.
    Em falha HTTP, levanta requests.HTTPError / RequestException.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Baixando %s -> %s", url, destino)
    with requests.get(url, headers=HTTP_HEADERS, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()
        with open(destino, "wb") as saida:
            for bloco in resp.iter_content(chunk_size=1024 * 1024):
                if bloco:
                    saida.write(bloco)
    return destino


def extrair_zip(arquivo_zip: Path, destino_dir: Path) -> list[Path]:
    """Extrai um ZIP e devolve a lista de arquivos gerados."""
    destino_dir.mkdir(parents=True, exist_ok=True)
    gerados: list[Path] = []
    with zipfile.ZipFile(arquivo_zip, "r") as zf:
        zf.extractall(destino_dir)
        for nome in zf.namelist():
            gerados.append(destino_dir / nome)
    return gerados


def normalizar_cnae(codigo: str) -> str:
    """Remove máscara do CNAE (ex.: 6201-5/01 -> 6201501)."""
    return "".join(ch for ch in codigo if ch.isdigit())


def normalizar_cep(cep: str) -> str:
    """CEP com 8 dígitos, sem hífen."""
    digitos = "".join(ch for ch in str(cep) if ch.isdigit())
    return digitos.zfill(8)[-8:] if digitos else ""


def normalizar_texto_endereco(texto: str) -> str:
    """
    Padronização leve de logradouro para junção com o CNEFE:
    maiúsculas, sem acento e expansão de abreviações comuns.
    """
    if not texto:
        return ""
    mapa_acentos = str.maketrans(
        "ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇáàâãäéèêëíìîïóòôõöúùûüç",
        "AAAAAEEEEIIIIOOOOOUUUUCaaaaaeeeeiiiiooooouuuuc",
    )
    t = texto.translate(mapa_acentos).upper().strip()
    substituicoes = (
        (" R. ", " RUA "),
        (" AV. ", " AVENIDA "),
        (" TRAV. ", " TRAVESSA "),
        (" ROD. ", " RODOVIA "),
    )
    if not t.startswith(" "):
        t = f" {t} "
    for antigo, novo in substituicoes:
        t = t.replace(antigo, novo)
    return " ".join(t.split())


def mapear_porte(codigo: str) -> str:
    """Traduz o código de porte da Receita para rótulo legível."""
    return {
        "00": "NAO INFORMADO",
        "01": "MICRO EMPRESA",
        "03": "EMPRESA DE PEQUENO PORTE",
        "05": "DEMAIS",
    }.get(str(codigo).zfill(2), str(codigo))


# ---------------------------------------------------------------------------
# 1) Obtenção das fontes oficiais (cada uma independente)
# ---------------------------------------------------------------------------

def obter_cnpj_receita() -> dict[str, Any]:
    """
    Fonte: base pública de CNPJ da Receita Federal do Brasil.

    Origem: ZIPs mensais em
    https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/{AAAA-MM}/
    Formato interno: TXT/CSV sem cabeçalho, separador ';' , Latin-1.

    O que este passo faz:
    - baixa Municipios.zip, Simples.zip, Empresas*.zip e Estabelecimentos*.zip;
    - resolve o código de município da Receita para Contagem;
    - filtra estabelecimentos ativos de Contagem com CNAE da divisão 62;
    - junta razão social, porte, capital e flag MEI pelo CNPJ básico.

    Tratamento previsto na etapa de unificação:
    - normalizar CNAE/CEP/endereço;
    - geocodificar via CNEFE;
    - gravar schema EstabelecimentoTI.
    """
    pasta = DIR_BRUTO / "cnpj" / CNPJ_PASTA_MES
    pasta.mkdir(parents=True, exist_ok=True)
    resultado: dict[str, Any] = {
        "ok": False,
        "fonte": "cnpj",
        "url_principal": CNPJ_BASE_URL,
        "pasta": str(pasta),
        "codigo_municipio_receita": None,
        "estabelecimentos": [],
        "empresas": {},
        "simples": {},
        "erros": [],
        "avisos": [],
    }

    # --- Municípios: achar código Receita de Contagem ---
    url_mun = f"{CNPJ_BASE_URL}/Municipios.zip"
    try:
        mun_zip = baixar_arquivo(url_mun, pasta / "Municipios.zip")
        mun_files = extrair_zip(mun_zip, pasta / "extraido_municipios")
        codigo_contagem = None
        for arq in mun_files:
            if not arq.is_file():
                continue
            with open(arq, "r", encoding="latin-1", newline="") as fh:
                reader = csv.reader(fh, delimiter=";")
                for row in reader:
                    if len(row) < 2:
                        continue
                    if row[1].strip().upper() == "CONTAGEM":
                        codigo_contagem = row[0].zfill(4)
                        break
            if codigo_contagem:
                break
        if not codigo_contagem:
            raise FonteErro(
                "cnpj",
                "CONTAGEM não encontrada em Municipios.zip.",
                url=url_mun,
                sugestao=(
                    "Abra o arquivo extraído e confira o nome do município. "
                    f"Se a pasta {CNPJ_PASTA_MES} estiver errada, ajuste CNPJ_PASTA_MES."
                ),
            )
        resultado["codigo_municipio_receita"] = codigo_contagem
        logger.info("Código Receita de Contagem: %s", codigo_contagem)
    except FonteErro:
        raise
    except Exception as exc:  # noqa: BLE001
        raise FonteErro(
            "cnpj",
            f"Falha ao baixar/ler Municipios.zip: {exc}",
            url=url_mun,
            sugestao=(
                "Confira se CNPJ_PASTA_MES existe no índice da Receita. "
                "Teste a URL no navegador. Sem Municípios não dá para filtrar Contagem."
            ),
            causa=exc,
        ) from exc

    # --- Simples / MEI (falha parcial não aborta a fonte) ---
    url_simples = f"{CNPJ_BASE_URL}/Simples.zip"
    try:
        simples_zip = baixar_arquivo(url_simples, pasta / "Simples.zip")
        for arq in extrair_zip(simples_zip, pasta / "extraido_simples"):
            if not arq.is_file():
                continue
            with open(arq, "r", encoding="latin-1", newline="") as fh:
                reader = csv.reader(fh, delimiter=";")
                for row in reader:
                    if len(row) < 5:
                        continue
                    cnpj_basico = row[0].zfill(8)
                    opcao_mei = row[4].strip().upper() == "S"
                    resultado["simples"][cnpj_basico] = {"opcao_mei": opcao_mei}
    except Exception as exc:  # noqa: BLE001
        aviso = f"Simples.zip falhou (MEI fica False): {exc}"
        logger.error(aviso)
        resultado["avisos"].append(aviso)

    # --- Empresas ---
    for i in range(10):
        nome = f"Empresas{i}.zip"
        url_emp = f"{CNPJ_BASE_URL}/{nome}"
        try:
            emp_zip = baixar_arquivo(url_emp, pasta / nome)
            for arq in extrair_zip(emp_zip, pasta / f"extraido_empresas_{i}"):
                if not arq.is_file():
                    continue
                with open(arq, "r", encoding="latin-1", newline="") as fh:
                    reader = csv.reader(fh, delimiter=";")
                    for row in reader:
                        if len(row) < 6:
                            continue
                        cnpj_basico = row[0].zfill(8)
                        capital_raw = (row[4] or "0").replace(",", ".")
                        try:
                            capital = float(capital_raw)
                        except ValueError:
                            capital = None
                        resultado["empresas"][cnpj_basico] = {
                            "razao_social": row[1],
                            "porte": mapear_porte(row[5]),
                            "capital_social": capital,
                        }
        except Exception as exc:  # noqa: BLE001
            aviso = f"{nome} falhou: {exc}"
            logger.error("%s | URL: %s", aviso, url_emp)
            resultado["avisos"].append(aviso)

    # --- Estabelecimentos: filtra Contagem + ativa + CNAE 62 ---
    codigo_mun = resultado["codigo_municipio_receita"]
    estabelecimentos: list[dict[str, Any]] = []
    zips_ok = 0
    for i in range(10):
        nome = f"Estabelecimentos{i}.zip"
        url_est = f"{CNPJ_BASE_URL}/{nome}"
        try:
            est_zip = baixar_arquivo(url_est, pasta / nome, timeout=600)
            for arq in extrair_zip(est_zip, pasta / f"extraido_estabelecimentos_{i}"):
                if not arq.is_file():
                    continue
                with open(arq, "r", encoding="latin-1", newline="") as fh:
                    reader = csv.reader(fh, delimiter=";")
                    for row in reader:
                        if len(row) < 21:
                            continue
                        if row[20].zfill(4) != codigo_mun:
                            continue
                        if row[19].strip().upper() != "MG":
                            continue
                        if row[5].zfill(2) != SITUACAO_ATIVA:
                            continue
                        cnae = normalizar_cnae(row[11])
                        if cnae not in CNAE_TI_DIVISAO_62:
                            continue
                        cnpj_basico = row[0].zfill(8)
                        cnpj_ordem = row[1].zfill(4)
                        cnpj_dv = row[2].zfill(2)
                        tipo = (row[13] or "").strip()
                        logradouro = f"{tipo} {row[14]}".strip() if tipo else row[14]
                        estabelecimentos.append(
                            {
                                "cnpj_basico": cnpj_basico,
                                "cnpj_completo": f"{cnpj_basico}{cnpj_ordem}{cnpj_dv}",
                                "cnae_fiscal": cnae,
                                "situacao_cadastral": row[5],
                                "logradouro": logradouro,
                                "numero": row[15],
                                "bairro": row[17],
                                "cep": row[18],
                                "codigo_municipio_receita": codigo_mun,
                                "nome_fantasia": row[4] or "",
                            }
                        )
            zips_ok += 1
            logger.info(
                "Após %s: %s estabelecimentos TI Contagem acumulados",
                nome,
                len(estabelecimentos),
            )
        except Exception as exc:  # noqa: BLE001
            aviso = f"{nome} falhou: {exc}"
            logger.error("%s | URL: %s", aviso, url_est)
            resultado["avisos"].append(aviso)

    if zips_ok == 0:
        raise FonteErro(
            "cnpj",
            "Nenhum Estabelecimentos*.zip foi baixado/lido com sucesso.",
            url=f"{CNPJ_BASE_URL}/Estabelecimentos0.zip",
            sugestao=(
                "Confira CNPJ_PASTA_MES e espaço em disco (arquivos são grandes). "
                "Rode: python pipeline.py --force --only cnpj"
            ),
        )

    # Mantém só empresas/simples dos CNPJs do recorte (cache menor entre runs).
    basicos = {e["cnpj_basico"] for e in estabelecimentos}
    resultado["empresas"] = {
        k: v for k, v in resultado["empresas"].items() if k in basicos
    }
    resultado["simples"] = {
        k: v for k, v in resultado["simples"].items() if k in basicos
    }
    resultado["estabelecimentos"] = estabelecimentos
    resultado["ok"] = True
    return resultado


def _ler_xlsx_linhas(caminho: Path) -> list[list[str]]:
    """Lê a primeira planilha de um XLSX (openpyxl ou XML interno)."""
    try:
        from openpyxl import load_workbook  # type: ignore

        wb = load_workbook(caminho, read_only=True, data_only=True)
        ws = wb.active
        linhas: list[list[str]] = []
        for row in ws.iter_rows(values_only=True):
            linhas.append(["" if c is None else str(c) for c in row])
        wb.close()
        return linhas
    except ImportError:
        logger.warning("openpyxl não instalado; usando parser XML mínimo do XLSX.")

    with zipfile.ZipFile(caminho) as zf:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            for si in root.findall("m:si", ns):
                textos = [t.text or "" for t in si.findall(".//m:t", ns)]
                shared.append("".join(textos))
        sheet_name = "xl/worksheets/sheet1.xml"
        root = ET.fromstring(zf.read(sheet_name))
        ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        linhas = []
        for row in root.findall("m:sheetData/m:row", ns):
            vals: list[str] = []
            for c in row.findall("m:c", ns):
                ref = c.get("r", "A")
                col = 0
                for ch in ref:
                    if ch.isalpha():
                        col = col * 26 + (ord(ch.upper()) - 64)
                    else:
                        break
                while len(vals) < col - 1:
                    vals.append("")
                v = c.find("m:v", ns)
                texto = v.text if v is not None else ""
                if c.get("t") == "s" and texto.isdigit():
                    texto = shared[int(texto)]
                vals.append(texto or "")
            linhas.append(vals)
        return linhas


def obter_cnae_ibge() -> dict[str, Any]:
    """
    Fonte: CNAE-Subclasses 2.3 (IBGE / CONCLA), planilha oficial XLSX.

    Tratamento: normalizar código sem máscara; manter CNAE_TI_DIVISAO_62.
    """
    destino = DIR_BRUTO / "cnae" / "CNAE_Subclasses_2_3_Estrutura_Detalhada.xlsx"
    try:
        baixar_arquivo(CNAE_XLSX_URL, destino)
        linhas = _ler_xlsx_linhas(destino)
        cnaes: list[dict[str, str]] = []
        for row in linhas:
            if not row:
                continue
            codigo_bruto = ""
            descricao = ""
            for i, cel in enumerate(row):
                cel_s = str(cel).strip()
                if re.fullmatch(r"\d{4}-\d/\d{2}", cel_s) or re.fullmatch(r"\d{7}", cel_s):
                    codigo_bruto = cel_s
                    if i + 1 < len(row):
                        descricao = str(row[i + 1]).strip()
                    break
            if not codigo_bruto:
                continue
            codigo = normalizar_cnae(codigo_bruto)
            if codigo in CNAE_TI_DIVISAO_62:
                cnaes.append({"codigo": codigo_bruto, "descricao": descricao or codigo})
        existentes = {normalizar_cnae(c["codigo"]) for c in cnaes}
        for cod in CNAE_TI_DIVISAO_62:
            if cod not in existentes:
                cnaes.append({"codigo": cod, "descricao": ""})
        return {
            "ok": True,
            "fonte": "cnae",
            "url_principal": CNAE_XLSX_URL,
            "cnae": cnaes,
            "arquivo": str(destino),
            "erros": [],
        }
    except Exception as exc:  # noqa: BLE001
        raise FonteErro(
            "cnae",
            f"Falha ao baixar/ler a planilha CNAE: {exc}",
            url=CNAE_XLSX_URL,
            sugestao=(
                "Confira o link CONCLA. Instale openpyxl se o parser XML falhar: "
                "pip install openpyxl. Depois: python pipeline.py --force --only cnae"
            ),
            causa=exc,
        ) from exc


def obter_cnefe_ibge() -> dict[str, Any]:
    """
    Fonte: CNEFE Contagem (CSV no ZIP do FTP IBGE).

    Tratamento previsto na unificação: junção em cascata com o endereço do CNPJ.
    """
    pasta = DIR_BRUTO / "cnefe"
    zip_path = pasta / "3118601_CONTAGEM.zip"
    try:
        baixar_arquivo(CNEFE_CONTAGEM_URL, zip_path, timeout=300)
        extraidos = extrair_zip(zip_path, pasta / "extraido")
        csv_files = [p for p in extraidos if p.suffix.lower() == ".csv"]
        if not csv_files:
            csv_files = [p for p in extraidos if p.is_file()]
        enderecos: list[dict[str, Any]] = []
        for arq in csv_files:
            with open(arq, "r", encoding="utf-8-sig", newline="") as fh:
                amostra = fh.read(4096)
                fh.seek(0)
                delim = ";" if amostra.count(";") >= amostra.count(",") else ","
                reader = csv.DictReader(fh, delimiter=delim)
                if reader.fieldnames is None:
                    continue
                campos = {c.upper(): c for c in reader.fieldnames}

                def col(*nomes: str) -> Optional[str]:
                    for n in nomes:
                        if n.upper() in campos:
                            return campos[n.upper()]
                    return None

                c_cep = col("CEP", "COD_CEP", "CEP_LOGR")
                c_log = col("NOM_SEGLOGR", "NOM_LOGRADOURO", "LOGRADOURO", "NOME_LOGRADOURO")
                c_num = col("NUM_ENDERECO", "NUMERO", "NUM_LOGR")
                c_lat = col("LATITUDE", "LAT")
                c_lon = col("LONGITUDE", "LON", "LONG")
                c_nv = col("NV_GEO_COORD", "NIVEL_GEO", "NV_GEO")
                for row in reader:
                    try:
                        lat = float(str(row.get(c_lat, "")).replace(",", ".")) if c_lat else None
                        lon = float(str(row.get(c_lon, "")).replace(",", ".")) if c_lon else None
                    except ValueError:
                        lat, lon = None, None
                    enderecos.append(
                        {
                            "cep": row.get(c_cep, "") if c_cep else "",
                            "logradouro": row.get(c_log, "") if c_log else "",
                            "numero": row.get(c_num, "") if c_num else "",
                            "latitude": lat,
                            "longitude": lon,
                            "nv_geo_coord": row.get(c_nv, "") if c_nv else "",
                        }
                    )
        if not enderecos:
            raise FonteErro(
                "cnefe",
                "ZIP baixado, mas nenhum endereço foi lido do CSV.",
                url=CNEFE_CONTAGEM_URL,
                sugestao=(
                    "Confira os nomes das colunas no CSV extraído e ajuste o mapeamento "
                    "em obter_cnefe_ibge."
                ),
            )
        logger.info("CNEFE Contagem: %s endereços lidos", len(enderecos))
        return {
            "ok": True,
            "fonte": "cnefe",
            "url_principal": CNEFE_CONTAGEM_URL,
            "cnefe": enderecos,
            "arquivo": str(zip_path),
            "erros": [],
        }
    except FonteErro:
        raise
    except Exception as exc:  # noqa: BLE001
        raise FonteErro(
            "cnefe",
            f"Falha ao baixar/ler CNEFE Contagem: {exc}",
            url=CNEFE_CONTAGEM_URL,
            sugestao=(
                "Liste a pasta 31_MG no FTP do IBGE e confirme o nome "
                "3118601_CONTAGEM.zip. Depois: python pipeline.py --force --only cnefe"
            ),
            causa=exc,
        ) from exc


def obter_malhas_ibge() -> dict[str, Any]:
    """
    Fonte: malhas IBGE (municípios + bairros MG).

    Baixa e extrai shapefiles; a junção espacial completa (ponto-em-polígono)
    fica opcional para não exigir geopandas nesta iteração.
    """
    pasta = DIR_BRUTO / "malhas"
    arquivos: list[dict[str, Any]] = []
    erros: list[str] = []
    for rotulo, url, nome in (
        ("municipios", MALHAS_MUNICIPIOS_URL, "BR_Municipios_2024.zip"),
        ("bairros_mg", MALHAS_BAIRROS_MG_URL, "MG_bairros_CD2022.zip"),
    ):
        try:
            zip_path = baixar_arquivo(url, pasta / nome, timeout=300)
            extraidos = extrair_zip(zip_path, pasta / f"extraido_{rotulo}")
            shps = [str(p) for p in extraidos if p.suffix.lower() == ".shp"]
            arquivos.append({"rotulo": rotulo, "zip": str(zip_path), "shp": shps, "url": url})
        except Exception as exc:  # noqa: BLE001
            erros.append(f"{rotulo}: {exc} | URL: {url}")
            logger.error("Malhas/%s falhou: %s", rotulo, exc)

    if not arquivos:
        raise FonteErro(
            "malhas",
            "Nenhuma malha foi baixada.",
            url=MALHAS_MUNICIPIOS_URL,
            sugestao=(
                "Verifique as URLs no geoftp do IBGE (ano da malha municipal pode ter mudado). "
                "python pipeline.py --force --only malhas"
            ),
        )
    return {
        "ok": True,
        "fonte": "malhas",
        "url_principal": MALHAS_MUNICIPIOS_URL,
        "arquivos": arquivos,
        "erros": erros,
        "avisos": erros,
    }


def _sidra_lista_para_linhas(dados: Any) -> list[dict[str, Any]]:
    """Converte o JSON da API SIDRA (lista cabeçalho + linhas) em dicts nomeados."""
    linhas: list[dict[str, Any]] = []
    if isinstance(dados, list) and len(dados) >= 2:
        cab = dados[0]
        for item in dados[1:]:
            linhas.append({str(cab.get(k, k)): item.get(k) for k in item})
    return linhas


def _sidra_valor_unidades(linha: dict[str, Any]) -> Optional[float]:
    bruto = linha.get("Valor") or linha.get("V")
    try:
        return float(str(bruto).replace(",", "."))
    except (TypeError, ValueError):
        return None


def obter_cempre_sidra() -> dict[str, Any]:
    """
    Fonte: CEMPRE via API SIDRA (tabela 9528) — conferência agregada.

    Recorte alinhado ao CNPJ do TCC:
    - município Contagem (3118601);
    - apenas divisão CNAE 62 (TI), código SIDRA 117594;
    - variável 706 (número de unidades locais).

    Unidades locais do CEMPRE já são estabelecimentos no município
    (não misturam filiais de outras cidades neste nível geográfico).

    Não entra no mapa de pontos; serve ao critério de diferença relativa <= 30%.
    """
    pasta = DIR_BRUTO / "cempre"
    pasta.mkdir(parents=True, exist_ok=True)
    try:
        logger.info("Consultando SIDRA/CEMPRE (divisão 62): %s", CEMPRE_SIDRA_URL)
        resp = requests.get(CEMPRE_SIDRA_URL, headers=HTTP_HEADERS, timeout=120)
        resp.raise_for_status()
        dados = resp.json()
        json_path = pasta / "cempre_sidra_9528_contagem_cnae62.json"
        json_path.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        linhas = _sidra_lista_para_linhas(dados)

        # Detalhe por classe CNAE (opcional; não bloqueia se falhar).
        linhas_classes: list[dict[str, Any]] = []
        try:
            logger.info(
                "Consultando SIDRA/CEMPRE (classes 62): %s", CEMPRE_SIDRA_URL_CLASSES
            )
            resp_c = requests.get(
                CEMPRE_SIDRA_URL_CLASSES, headers=HTTP_HEADERS, timeout=120
            )
            resp_c.raise_for_status()
            dados_c = resp_c.json()
            (pasta / "cempre_sidra_9528_contagem_cnae62_classes.json").write_text(
                json.dumps(dados_c, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            linhas_classes = _sidra_lista_para_linhas(dados_c)
        except Exception as exc_cls:  # noqa: BLE001
            logger.error("Detalhe por classe CEMPRE falhou (segue com divisão): %s", exc_cls)

        total_divisao: Optional[float] = None
        for linha in linhas:
            cnae_txt = str(
                linha.get("Classificação Nacional de Atividades Econômicas (CNAE 2.0)")
                or linha.get("D4N")
                or ""
            )
            if cnae_txt.strip().startswith("62 ") or "117594" in str(
                linha.get("Classificação Nacional de Atividades Econômicas (CNAE 2.0) (Código)")
                or linha.get("D4C")
                or ""
            ):
                total_divisao = _sidra_valor_unidades(linha)
                if total_divisao is not None:
                    break
        if total_divisao is None and linhas:
            total_divisao = _sidra_valor_unidades(linhas[0])

        if total_divisao is None:
            raise FonteErro(
                "cempre",
                "Resposta SIDRA sem valor de unidades locais para Contagem/CNAE 62.",
                url=CEMPRE_SIDRA_URL,
                sugestao=(
                    "Confira a tabela 9528 e o código 117594 no descritor C12762. "
                    "python pipeline.py --force --only cempre"
                ),
            )

        soma_classes = 0.0
        for linha in linhas_classes:
            val = _sidra_valor_unidades(linha)
            if val is not None:
                soma_classes += val

        csv_path = pasta / "cempre_contagem_cnae62.csv"
        linhas_csv = linhas + linhas_classes
        if linhas_csv:
            with open(csv_path, "w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=list(linhas_csv[0].keys()))
                writer.writeheader()
                writer.writerows(linhas_csv)

        logger.info(
            "CEMPRE Contagem + CNAE 62: %s unidades locais (ano da foto SIDRA).",
            int(total_divisao) if total_divisao == int(total_divisao) else total_divisao,
        )
        return {
            "ok": True,
            "fonte": "cempre",
            "url_principal": CEMPRE_SIDRA_URL,
            "recorte": {
                "municipio_ibge": CODIGO_IBGE_CONTAGEM,
                "cnae": "divisao_62",
                "codigo_sidra_cnae": CEMPRE_CNAE_DIVISAO_62,
                "tabela": CEMPRE_TABELA,
                "variavel": CEMPRE_VAR_UNIDADES_LOCAIS,
            },
            "total_unidades_locais_divisao_62": total_divisao,
            "soma_classes_divisao_62": soma_classes if linhas_classes else None,
            "linhas": linhas,
            "linhas_classes": linhas_classes,
            "arquivo": str(csv_path if linhas_csv else json_path),
            "erros": [],
        }
    except FonteErro:
        raise
    except Exception as exc:  # noqa: BLE001
        raise FonteErro(
            "cempre",
            f"Falha na API SIDRA/CEMPRE (Contagem + CNAE 62): {exc}",
            url=CEMPRE_SIDRA_URL,
            sugestao=(
                "Confira https://sidra.ibge.gov.br/tabela/9528 e o código 117594 "
                "(divisão 62). Depois: python pipeline.py --force --only cempre"
            ),
            causa=exc,
        ) from exc


# Registro das fontes independentes (nome -> função + metadados de ajuda).
REGISTRO_FONTES: dict[str, dict[str, Any]] = {
    "cnpj": {
        "funcao": obter_cnpj_receita,
        "url": CNPJ_BASE_URL,
        "sugestao": f"Ajuste CNPJ_PASTA_MES (atual: {CNPJ_PASTA_MES}) se o índice mensal mudou.",
    },
    "cnae": {
        "funcao": obter_cnae_ibge,
        "url": CNAE_XLSX_URL,
        "sugestao": "Confira o XLSX na CONCLA e, se preciso, pip install openpyxl.",
    },
    "cnefe": {
        "funcao": obter_cnefe_ibge,
        "url": CNEFE_CONTAGEM_URL,
        "sugestao": "Confirme 3118601_CONTAGEM.zip na pasta 31_MG do FTP do IBGE.",
    },
    "malhas": {
        "funcao": obter_malhas_ibge,
        "url": MALHAS_MUNICIPIOS_URL,
        "sugestao": "Confira o ano em malhas_municipais/ no geoftp do IBGE.",
    },
    "cempre": {
        "funcao": obter_cempre_sidra,
        "url": CEMPRE_SIDRA_URL,
        "sugestao": (
            "Confira tabela 9528 e código CNAE 117594 (divisão 62) no descritor SIDRA."
        ),
    },
}


def executar_fonte(nome: str, *, forcar: bool = False) -> dict[str, Any]:
    """
    Executa uma única fonte de forma isolada.
    Se já estiver ok no estado e existir cache, pula (salvo --force).
    """
    if nome not in REGISTRO_FONTES:
        raise ValueError(f"Fonte desconhecida: {nome}. Use: {', '.join(FONTES_DISPONIVEIS)}")

    estado = carregar_estado()
    meta = estado["fontes"].get(nome, {})
    url = REGISTRO_FONTES[nome]["url"]

    if not forcar and meta.get("status") == "ok" and caminho_cache(nome).exists():
        logger.info("Fonte %s já ok — pulando (use --force para refazer).", nome)
        cache = carregar_cache_fonte(nome) or {"ok": True, "fonte": nome, "pulado": True}
        return {"status": "pulado", "dados": cache}

    logger.info("=== Executando fonte: %s ===", nome)
    try:
        dados = REGISTRO_FONTES[nome]["funcao"]()
        if not dados.get("ok", False):
            raise FonteErro(
                nome,
                "; ".join(dados.get("erros") or ["Fonte retornou ok=False"]),
                url=url,
                sugestao=REGISTRO_FONTES[nome]["sugestao"],
            )
        artefato = salvar_cache_fonte(nome, dados)
        marcar_fonte_ok(estado, nome, dados.get("url_principal") or url, artefato)
        logger.info("Fonte %s concluída. Cache: %s", nome, artefato)
        return {"status": "ok", "dados": dados, "artefato": str(artefato)}
    except FonteErro as exc:
        imprimir_erro_acionavel(exc.fonte, exc.url or url, exc.mensagem, exc.sugestao)
        marcar_fonte_erro(estado, nome, exc.url or url, exc.mensagem, exc.sugestao)
        return {"status": "erro", "erro": exc.mensagem}
    except Exception as exc:  # noqa: BLE001
        sugestao = REGISTRO_FONTES[nome]["sugestao"]
        mensagem = f"Erro inesperado: {exc}"
        imprimir_erro_acionavel(
            nome,
            url,
            mensagem,
            sugestao,
            detalhe=traceback.format_exc(limit=3),
        )
        marcar_fonte_erro(estado, nome, url, mensagem, sugestao)
        return {"status": "erro", "erro": mensagem}


def executar_fontes_selecionadas(
    nomes: Iterable[str],
    *,
    forcar: bool = False,
) -> dict[str, Any]:
    """Roda várias fontes; falha de uma não impede as seguintes."""
    garantir_diretorios()
    resultados: dict[str, Any] = {}
    for nome in nomes:
        resultados[nome] = executar_fonte(nome, forcar=forcar)
    return resultados


# ---------------------------------------------------------------------------
# 2) Montagem / unificação / SQL (usam caches das fontes)
# ---------------------------------------------------------------------------

def carregar_fontes_do_cache() -> dict[str, Any]:
    """Monta o dicionário de fontes a partir dos caches em disco + estado."""
    fontes: dict[str, Any] = {}
    estado = carregar_estado()
    for nome in FONTES_DISPONIVEIS:
        cache = carregar_cache_fonte(nome)
        if cache is not None:
            fontes[nome] = cache
        else:
            status = estado["fontes"].get(nome, {}).get("status")
            fontes[nome] = {
                "ok": False,
                "erros": [f"Sem cache local (status={status})"],
                "linhas": [],
                "cnae": [],
                "cnefe": [],
                "estabelecimentos": [],
            }
    return fontes


def montar_tabelas_para_unificacao(fontes: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """
    Converte o resultado das fontes oficiais no dicionário esperado por
    `unificar_fontes`. Não usa dados sintéticos.
    """
    cnpj = fontes.get("cnpj") or {}
    cnae = fontes.get("cnae") or {}
    cnefe = fontes.get("cnefe") or {}

    estabelecimentos = list(cnpj.get("estabelecimentos") or [])
    empresas_map = cnpj.get("empresas") or {}
    simples_map = cnpj.get("simples") or {}

    empresas: list[dict[str, Any]] = []
    basicos = {e["cnpj_basico"] for e in estabelecimentos}
    for basico in basicos:
        emp = empresas_map.get(basico, {})
        mei = bool((simples_map.get(basico) or {}).get("opcao_mei", False))
        empresas.append(
            {
                "cnpj_basico": basico,
                "razao_social": emp.get("razao_social", ""),
                "porte": emp.get("porte", ""),
                "capital_social": emp.get("capital_social"),
                "opcao_mei": mei,
            }
        )

    return {
        "estabelecimentos": estabelecimentos,
        "empresas": empresas,
        "cnae": list(cnae.get("cnae") or []),
        "cnefe": list(cnefe.get("cnefe") or []),
    }


def unificar_fontes(
    tabelas: dict[str, list[dict[str, Any]]],
    data_fotografia: Optional[str] = None,
) -> list[EstabelecimentoTI]:
    """
    Une CNPJ (estabelecimentos + empresas), CNAE e CNEFE em EstabelecimentoTI.

    Etapas: filtrar CNAE 62 e situação ativa; normalizar chaves; juntar empresa;
    geocodificar em cascata; preencher níveis CNEFE.
    """
    data_fotografia = data_fotografia or date.today().isoformat()

    mapa_cnae: dict[str, str] = {}
    for linha in tabelas.get("cnae") or []:
        codigo = normalizar_cnae(str(linha.get("codigo", "")))
        if codigo:
            mapa_cnae[codigo] = str(linha.get("descricao", ""))

    mapa_empresas = {e["cnpj_basico"]: e for e in (tabelas.get("empresas") or [])}

    cnefe_por_chave_completa: dict[tuple[str, str, str], dict[str, Any]] = {}
    cnefe_por_cep: dict[str, dict[str, Any]] = {}
    for end in tabelas.get("cnefe") or []:
        cep = normalizar_cep(end.get("cep", ""))
        log = normalizar_texto_endereco(str(end.get("logradouro", "")))
        num = str(end.get("numero", "")).strip().upper()
        if num and num not in {"S/N", "SN"}:
            cnefe_por_chave_completa[(cep, log, num)] = end
        if cep:
            cnefe_por_cep.setdefault(cep, end)

    unificados: list[EstabelecimentoTI] = []

    for est in tabelas.get("estabelecimentos") or []:
        cnae = normalizar_cnae(str(est.get("cnae_fiscal", "")))
        if cnae not in CNAE_TI_DIVISAO_62:
            continue
        if str(est.get("situacao_cadastral", "")).zfill(2) != SITUACAO_ATIVA:
            continue

        empresa = mapa_empresas.get(est["cnpj_basico"], {})
        cep = normalizar_cep(est.get("cep", ""))
        log = normalizar_texto_endereco(str(est.get("logradouro", "")))
        num_raw = str(est.get("numero", "")).strip().upper()
        num = "" if num_raw in {"", "S/N", "SN"} else num_raw

        latitude = None
        longitude = None
        nivel_juncao = "sem_coordenada"
        nivel_geo = None

        hit = None
        if num and (cep, log, num) in cnefe_por_chave_completa:
            hit = cnefe_por_chave_completa[(cep, log, num)]
            nivel_juncao = "endereco_completo"
        elif cep in cnefe_por_cep:
            hit = cnefe_por_cep[cep]
            nivel_juncao = "somente_cep"

        if hit:
            try:
                latitude = float(hit["latitude"]) if hit.get("latitude") is not None else None
                longitude = float(hit["longitude"]) if hit.get("longitude") is not None else None
            except (TypeError, ValueError):
                latitude, longitude = None, None
            nivel_geo = (
                str(hit.get("nv_geo_coord")) if hit.get("nv_geo_coord") not in (None, "") else None
            )

        unificados.append(
            EstabelecimentoTI(
                cnpj_basico=str(est["cnpj_basico"]),
                cnpj_completo=str(est["cnpj_completo"]),
                razao_social=str(empresa.get("razao_social", "")),
                nome_fantasia=str(est.get("nome_fantasia", "")),
                cnae_principal=cnae,
                cnae_descricao=mapa_cnae.get(cnae, ""),
                porte=str(empresa.get("porte", "")),
                capital_social=empresa.get("capital_social"),
                situacao_cadastral=str(est.get("situacao_cadastral", "")),
                is_mei=bool(empresa.get("opcao_mei", False)),
                logradouro=log,
                numero=num_raw,
                bairro=str(est.get("bairro", "")),
                cep=cep,
                municipio_ibge=CODIGO_IBGE_CONTAGEM,
                latitude=latitude,
                longitude=longitude,
                nivel_juncao_cnefe=nivel_juncao,
                nivel_geo_cnefe=nivel_geo,
                area_municipio=None,
                data_fotografia=data_fotografia,
            )
        )

    return unificados


def salvar_json_tratado(registros: Iterable[EstabelecimentoTI]) -> Path:
    """Persiste o schema comum em JSON para inspeção e para a etapa SQL."""
    garantir_diretorios()
    caminho = DIR_TRATADO / "estabelecimentos_ti_contagem.json"
    payload = [asdict(r) for r in registros]
    caminho.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return caminho


def conferir_criterio_cempre(
    n_app: int,
    fontes: dict[str, Any],
    limiar: float = 0.30,
) -> dict[str, Any]:
    """Aplica |N_app - N_CEMPRE| / N_CEMPRE <= 0,30 no recorte Contagem + CNAE 62."""
    resumo: dict[str, Any] = {
        "n_app": n_app,
        "n_cempre": None,
        "diferenca_relativa": None,
        "aceitou": None,
        "observacao": "",
        "recorte_cempre": (fontes.get("cempre") or {}).get("recorte"),
    }
    cempre = fontes.get("cempre") or {}
    n_cempre = cempre.get("total_unidades_locais_divisao_62")
    if n_cempre is None:
        for linha in cempre.get("linhas") or []:
            val = _sidra_valor_unidades(linha)
            if val is not None:
                n_cempre = val
                break
    if n_cempre is None or n_cempre == 0:
        resumo["observacao"] = (
            "CEMPRE indisponível ou sem valor numérico; critério não aplicado nesta execução."
        )
        return resumo
    diff = abs(n_app - float(n_cempre)) / float(n_cempre)
    resumo["n_cempre"] = float(n_cempre)
    resumo["diferenca_relativa"] = diff
    resumo["aceitou"] = diff <= limiar
    resumo["observacao"] = (
        "Comparação no mesmo recorte geográfico/setorial (Contagem + divisão CNAE 62). "
        "Diferenças restantes vêm sobretudo de ano de referência (CEMPRE anual vs "
        "fotografia mensal do CNPJ) e de regras de inclusão de MEI/situação cadastral."
    )
    return resumo


def _sql_escape(valor: Any) -> str:
    if valor is None:
        return "NULL"
    if isinstance(valor, bool):
        return "1" if valor else "0"
    if isinstance(valor, (int, float)):
        return str(valor)
    texto = str(valor).replace("\\", "\\\\").replace("'", "''")
    return f"'{texto}'"


def gerar_sql_aplicacao(registros: list[EstabelecimentoTI]) -> Path:
    """Gera sql_gerado/schema_aplicacao.sql (CREATE / INSERT / VIEW)."""
    garantir_diretorios()
    caminho = DIR_SQL / "schema_aplicacao.sql"

    linhas: list[str] = []
    linhas.append("-- SQL gerado pelo pipeline_para_obtencao_de_dados/pipeline.py")
    linhas.append("-- Destino: banco MySQL da aplicação web (Contagem / TI / divisão 62)")
    linhas.append(f"-- Fotografia CNPJ de referência: {CNPJ_PASTA_MES}")
    linhas.append("SET NAMES utf8mb4;")
    linhas.append("START TRANSACTION;")
    linhas.append("")
    linhas.append(
        """
CREATE TABLE IF NOT EXISTS carga (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    data_fotografia DATE NOT NULL,
    versao_bases VARCHAR(128) NULL,
    data_download DATE NULL,
    regras_filtro TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""".strip()
    )
    linhas.append("")
    linhas.append(
        """
CREATE TABLE IF NOT EXISTS cnae (
    codigo CHAR(7) PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""".strip()
    )
    linhas.append("")
    linhas.append(
        """
CREATE TABLE IF NOT EXISTS empresa (
    cnpj_basico CHAR(8) PRIMARY KEY,
    razao_social VARCHAR(255) NOT NULL,
    porte VARCHAR(64) NULL,
    capital_social DECIMAL(18,2) NULL,
    is_mei TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""".strip()
    )
    linhas.append("")
    linhas.append(
        """
CREATE TABLE IF NOT EXISTS estabelecimento (
    cnpj_completo CHAR(14) PRIMARY KEY,
    cnpj_basico CHAR(8) NOT NULL,
    nome_fantasia VARCHAR(255) NULL,
    cnae_principal CHAR(7) NOT NULL,
    situacao_cadastral VARCHAR(8) NULL,
    logradouro VARCHAR(255) NULL,
    numero VARCHAR(32) NULL,
    bairro VARCHAR(128) NULL,
    cep CHAR(8) NULL,
    municipio_ibge CHAR(7) NOT NULL,
    latitude DECIMAL(10,7) NULL,
    longitude DECIMAL(10,7) NULL,
    nivel_juncao_cnefe VARCHAR(32) NOT NULL,
    nivel_geo_cnefe VARCHAR(16) NULL,
    area_municipio VARCHAR(128) NULL,
    carga_id BIGINT NULL,
    CONSTRAINT fk_est_empresa FOREIGN KEY (cnpj_basico) REFERENCES empresa (cnpj_basico),
    CONSTRAINT fk_est_cnae FOREIGN KEY (cnae_principal) REFERENCES cnae (codigo),
    CONSTRAINT fk_est_carga FOREIGN KEY (carga_id) REFERENCES carga (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""".strip()
    )
    linhas.append("")
    linhas.append(
        """
CREATE OR REPLACE VIEW vw_dashboard_estabelecimentos AS
SELECT
    e.cnpj_completo,
    em.razao_social,
    e.nome_fantasia,
    e.cnae_principal,
    c.descricao AS cnae_descricao,
    em.porte,
    em.is_mei,
    e.latitude,
    e.longitude,
    e.nivel_juncao_cnefe,
    e.nivel_geo_cnefe,
    e.area_municipio,
    e.bairro,
    e.cep,
    cg.data_fotografia
FROM estabelecimento e
JOIN empresa em ON em.cnpj_basico = e.cnpj_basico
JOIN cnae c ON c.codigo = e.cnae_principal
LEFT JOIN carga cg ON cg.id = e.carga_id;
""".strip()
    )
    linhas.append("")

    if registros:
        data_foto = registros[0].data_fotografia
        linhas.append(
            "INSERT INTO carga (data_fotografia, versao_bases, data_download, regras_filtro) VALUES ("
            f"{_sql_escape(data_foto)}, "
            f"{_sql_escape(f'cnpj-{CNPJ_PASTA_MES}+cnefe2022+cnae2.3')}, "
            f"{_sql_escape(date.today().isoformat())}, "
            f"{_sql_escape('Contagem IBGE 3118601; CNAE divisao 62; situacao ativa 02')}"
            ");"
        )
        linhas.append("SET @carga_id = LAST_INSERT_ID();")
        linhas.append("")

        cnaes_vistos: set[str] = set()
        empresas_vistas: set[str] = set()

        for r in registros:
            if r.cnae_principal not in cnaes_vistos:
                linhas.append(
                    "INSERT INTO cnae (codigo, descricao) VALUES ("
                    f"{_sql_escape(r.cnae_principal)}, {_sql_escape(r.cnae_descricao or r.cnae_principal)}"
                    ") ON DUPLICATE KEY UPDATE descricao = VALUES(descricao);"
                )
                cnaes_vistos.add(r.cnae_principal)

            if r.cnpj_basico not in empresas_vistas:
                linhas.append(
                    "INSERT INTO empresa (cnpj_basico, razao_social, porte, capital_social, is_mei) VALUES ("
                    f"{_sql_escape(r.cnpj_basico)}, "
                    f"{_sql_escape(r.razao_social)}, "
                    f"{_sql_escape(r.porte)}, "
                    f"{_sql_escape(r.capital_social)}, "
                    f"{_sql_escape(r.is_mei)}"
                    ") ON DUPLICATE KEY UPDATE "
                    "razao_social = VALUES(razao_social), "
                    "porte = VALUES(porte), "
                    "capital_social = VALUES(capital_social), "
                    "is_mei = VALUES(is_mei);"
                )
                empresas_vistas.add(r.cnpj_basico)

            linhas.append(
                "INSERT INTO estabelecimento ("
                "cnpj_completo, cnpj_basico, nome_fantasia, cnae_principal, situacao_cadastral, "
                "logradouro, numero, bairro, cep, municipio_ibge, latitude, longitude, "
                "nivel_juncao_cnefe, nivel_geo_cnefe, area_municipio, carga_id"
                ") VALUES ("
                f"{_sql_escape(r.cnpj_completo)}, "
                f"{_sql_escape(r.cnpj_basico)}, "
                f"{_sql_escape(r.nome_fantasia)}, "
                f"{_sql_escape(r.cnae_principal)}, "
                f"{_sql_escape(r.situacao_cadastral)}, "
                f"{_sql_escape(r.logradouro)}, "
                f"{_sql_escape(r.numero)}, "
                f"{_sql_escape(r.bairro)}, "
                f"{_sql_escape(r.cep)}, "
                f"{_sql_escape(r.municipio_ibge)}, "
                f"{_sql_escape(r.latitude)}, "
                f"{_sql_escape(r.longitude)}, "
                f"{_sql_escape(r.nivel_juncao_cnefe)}, "
                f"{_sql_escape(r.nivel_geo_cnefe)}, "
                f"{_sql_escape(r.area_municipio)}, "
                "@carga_id"
                ") ON DUPLICATE KEY UPDATE "
                "nome_fantasia = VALUES(nome_fantasia), "
                "latitude = VALUES(latitude), "
                "longitude = VALUES(longitude), "
                "nivel_juncao_cnefe = VALUES(nivel_juncao_cnefe), "
                "nivel_geo_cnefe = VALUES(nivel_geo_cnefe), "
                "carga_id = VALUES(carga_id);"
            )

    linhas.append("")
    linhas.append("COMMIT;")
    linhas.append("")
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return caminho


def executar_unificacao() -> dict[str, Any]:
    """Lê caches das fontes, unifica, gera JSON tratado e SQL."""
    estado = carregar_estado()
    fontes = carregar_fontes_do_cache()

    faltando = [
        n for n in ("cnpj", "cnae", "cnefe")
        if not (fontes.get(n) or {}).get("ok")
    ]
    if faltando:
        msg = (
            "Unificação precisa de cache ok em: "
            + ", ".join(faltando)
            + ". Rode essas fontes antes."
        )
        imprimir_erro_acionavel(
            ETAPA_UNIFICAR,
            "",
            msg,
            "Ex.: python pipeline.py --only cnpj,cnae,cnefe  e depois  python pipeline.py --unify",
        )
        marcar_fonte_erro(estado, ETAPA_UNIFICAR, "", msg, "Complete as fontes obrigatórias.")
        return {"status": "erro", "erro": msg, "faltando": faltando}

    tabelas = montar_tabelas_para_unificacao(fontes)
    registros = unificar_fontes(tabelas, data_fotografia=f"{CNPJ_PASTA_MES}-01")
    json_path = salvar_json_tratado(registros)
    sql_path = gerar_sql_aplicacao(registros)
    criterio = conferir_criterio_cempre(len(registros), fontes)

    marcar_fonte_ok(estado, ETAPA_UNIFICAR, "", json_path)
    return {
        "status": "ok",
        "n_estabelecimentos": len(registros),
        "json_tratado": str(json_path),
        "sql_aplicacao": str(sql_path),
        "criterio_cempre": criterio,
    }


# ---------------------------------------------------------------------------
# CLI — ponto de entrada para o ciclo iterativo
# ---------------------------------------------------------------------------

def imprimir_status() -> None:
    estado = carregar_estado()
    print(f"Estado: {ARQUIVO_ESTADO}")
    print(f"Atualizado em: {estado.get('atualizado_em')}")
    print("-" * 72)
    for nome, meta in estado.get("fontes", {}).items():
        print(
            f"{nome:12} | {meta.get('status', '?'):8} | "
            f"{meta.get('atualizado_em') or '-':25} | "
            f"{(meta.get('erro') or '-')[:40]}"
        )
    print("-" * 72)
    print("Fontes: " + ", ".join(FONTES_DISPONIVEIS))
    print("Ex.: python pipeline.py --only cnae")
    print("Ex.: python pipeline.py --force --only cnpj")
    print("Ex.: python pipeline.py --unify")


def parse_only(valor: Optional[str]) -> list[str]:
    if not valor:
        return list(FONTES_DISPONIVEIS)
    nomes = [p.strip().lower() for p in valor.split(",") if p.strip()]
    invalidos = [n for n in nomes if n not in FONTES_DISPONIVEIS]
    if invalidos:
        raise SystemExit(
            f"Fonte(s) inválida(s): {invalidos}. Válidas: {', '.join(FONTES_DISPONIVEIS)}"
        )
    return nomes


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Pipeline iterativo TCC Contagem/TI. "
            "Rode, corrija a fonte que falhou, rode de novo."
        )
    )
    p.add_argument(
        "--only",
        metavar="FONTES",
        help="Lista separada por vírgula (ex.: cnpj ou cnae,cnefe). Padrão: todas.",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Refaz mesmo fontes já marcadas como ok no estado.",
    )
    p.add_argument(
        "--unify",
        action="store_true",
        help="Só unifica caches existentes e gera JSON/SQL (não baixa).",
    )
    p.add_argument(
        "--status",
        action="store_true",
        help="Mostra pipeline_estado.json e sai.",
    )
    p.add_argument(
        "--reset-estado",
        action="store_true",
        help="Zera o estado (não apaga dados_brutos).",
    )
    p.add_argument(
        "--sem-unificar",
        action="store_true",
        help="Após baixar fontes, não executa a unificação automática.",
    )
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = construir_parser().parse_args(argv)
    garantir_diretorios()

    if args.reset_estado:
        salvar_estado(estado_vazio())
        print(f"Estado reiniciado em {ARQUIVO_ESTADO}")
        return 0

    if args.status:
        imprimir_status()
        return 0

    if args.unify:
        saida = executar_unificacao()
        print(json.dumps(saida, ensure_ascii=False, indent=2))
        return 0 if saida.get("status") == "ok" else 1

    nomes = parse_only(args.only)
    resultados = executar_fontes_selecionadas(nomes, forcar=args.force)

    resumo = {
        nome: {"status": r.get("status"), "erro": r.get("erro")}
        for nome, r in resultados.items()
    }
    print(json.dumps({"fontes": resumo}, ensure_ascii=False, indent=2))

    if not args.sem_unificar:
        # Unifica se as fontes obrigatórias tiverem cache ok (mesmo que
        # esta execução só tenha rodado uma fonte).
        saida_u = executar_unificacao()
        print(json.dumps({"unificar": saida_u}, ensure_ascii=False, indent=2))

    erros = [n for n, r in resultados.items() if r.get("status") == "erro"]
    return 1 if erros else 0


if __name__ == "__main__":
    # Atenção: Estabelecimentos*.zip pode passar de vários GB.
    raise SystemExit(main())
