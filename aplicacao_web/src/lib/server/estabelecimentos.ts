import { getPool } from '#lib/server/db.js';
import type {
	Estabelecimento,
	FiltrosEstabelecimento,
	ResumoDashboard
} from '#lib/types.js';

function montarWhere(filtros: FiltrosEstabelecimento): {
	sql: string;
	params: Record<string, string>;
} {
	const partes: string[] = [];
	const params: Record<string, string> = {};

	if (filtros.q?.trim()) {
		partes.push(
			`(v.razao_social LIKE :q OR v.nome_fantasia LIKE :q OR v.cnpj_completo LIKE :q OR v.bairro LIKE :q)`
		);
		params.q = `%${filtros.q.trim()}%`;
	}

	if (filtros.cnae?.trim()) {
		partes.push(`v.cnae_principal = :cnae`);
		params.cnae = filtros.cnae.trim();
	}

	if (filtros.porte?.trim()) {
		partes.push(`v.porte = :porte`);
		params.porte = filtros.porte.trim();
	}

	return {
		sql: partes.length ? `WHERE ${partes.join(' AND ')}` : '',
		params
	};
}

/** Lista estabelecimentos da view do dashboard, com filtros opcionais. */
export async function listarEstabelecimentos(
	filtros: FiltrosEstabelecimento = {}
): Promise<Estabelecimento[]> {
	const pool = getPool();
	const { sql, params } = montarWhere(filtros);
	const [rows] = await pool.query(
		`
		SELECT
			v.cnpj_completo,
			v.razao_social,
			v.nome_fantasia,
			v.cnae_principal,
			v.cnae_descricao,
			v.porte,
			v.latitude,
			v.longitude,
			v.nivel_juncao_cnefe,
			v.nivel_geo_cnefe,
			v.bairro,
			v.cep,
			v.data_fotografia
		FROM vw_dashboard_estabelecimentos v
		${sql}
		ORDER BY v.razao_social ASC
		LIMIT 2000
		`,
		params
	);
	return rows as Estabelecimento[];
}

/** Agrega KPIs e séries para o painel inicial. */
export async function obterResumo(): Promise<ResumoDashboard> {
	const pool = getPool();

	const [totaisRows] = await pool.query(
		`
		SELECT
			COUNT(*) AS total,
			SUM(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) AS com_coordenada,
			SUM(CASE WHEN latitude IS NULL OR longitude IS NULL THEN 1 ELSE 0 END) AS sem_coordenada,
			DATE_FORMAT(MAX(data_fotografia), '%Y-%m-%d') AS data_fotografia
		FROM vw_dashboard_estabelecimentos
		`
	);
	const totais = (totaisRows as Array<{
		total: number;
		com_coordenada: number;
		sem_coordenada: number;
		data_fotografia: string | null;
	}>)[0];

	const [porCnae] = await pool.query(
		`
		SELECT
			cnae_principal,
			cnae_descricao,
			COUNT(*) AS total
		FROM vw_dashboard_estabelecimentos
		GROUP BY cnae_principal, cnae_descricao
		ORDER BY total DESC
		`
	);

	const [porPorte] = await pool.query(
		`
		SELECT
			COALESCE(porte, 'Não informado') AS porte,
			COUNT(*) AS total
		FROM vw_dashboard_estabelecimentos
		GROUP BY COALESCE(porte, 'Não informado')
		ORDER BY total DESC
		`
	);

	return {
		total: Number(totais.total),
		com_coordenada: Number(totais.com_coordenada),
		sem_coordenada: Number(totais.sem_coordenada),
		data_fotografia: totais.data_fotografia,
		por_cnae: porCnae as ResumoDashboard['por_cnae'],
		por_porte: porPorte as ResumoDashboard['por_porte']
	};
}
