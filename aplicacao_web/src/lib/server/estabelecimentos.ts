import { CEMPRE_REF } from '$app/env/private';
import {
	atendeCriterio30,
	CEMPRE_CLASSES,
	CEMPRE_TOTAL_REF,
	desvioRelativo
} from '#lib/cempre.js';
import { getPool } from '#lib/server/db.js';
import type {
	CenarioMitigacao,
	ComparativoClasseCempre,
	Estabelecimento,
	FiltrosEstabelecimento,
	MitigacaoCempre,
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

	if (filtros.mei === '0' || filtros.mei === '1') {
		partes.push(`v.is_mei = :mei`);
		params.mei = filtros.mei;
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
			v.is_mei,
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
	const cempreRef = Number(CEMPRE_REF);

	const [totaisRows] = await pool.query(
		`
		SELECT
			COUNT(*) AS total,
			SUM(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) AS com_coordenada,
			SUM(CASE WHEN latitude IS NULL OR longitude IS NULL THEN 1 ELSE 0 END) AS sem_coordenada,
			SUM(CASE WHEN is_mei = 1 THEN 1 ELSE 0 END) AS mei,
			DATE_FORMAT(MAX(data_fotografia), '%Y-%m-%d') AS data_fotografia
		FROM vw_dashboard_estabelecimentos
		`
	);
	const totais = (totaisRows as Array<{
		total: number;
		com_coordenada: number;
		sem_coordenada: number;
		mei: number;
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

	const total = Number(totais.total);
	const desvio = desvioRelativo(total, cempreRef);
	const mitigacao = await obterMitigacao(
		cempreRef,
		porCnae as ResumoDashboard['por_cnae']
	);

	return {
		total,
		com_coordenada: Number(totais.com_coordenada),
		sem_coordenada: Number(totais.sem_coordenada),
		mei: Number(totais.mei),
		data_fotografia: totais.data_fotografia,
		cempre_ref: cempreRef,
		desvio_cempre: desvio,
		atende_criterio_30: atendeCriterio30(desvio),
		por_cnae: porCnae as ResumoDashboard['por_cnae'],
		por_porte: porPorte as ResumoDashboard['por_porte'],
		mitigacao
	};
}

function montarCenario(
	id: string,
	rotulo: string,
	descricao: string,
	total: number,
	cempreRef: number,
	aplicar: CenarioMitigacao['aplicar']
): CenarioMitigacao {
	const desvio = desvioRelativo(total, cempreRef);
	return {
		id,
		rotulo,
		descricao,
		total,
		desvio,
		atende_30: atendeCriterio30(desvio),
		aplicar
	};
}

/** Cenários de recorte e comparação por classe CNAE frente ao CEMPRE. */
export async function obterMitigacao(
	cempreRef = Number(CEMPRE_REF) || CEMPRE_TOTAL_REF,
	porCnae?: ResumoDashboard['por_cnae']
): Promise<MitigacaoCempre> {
	const pool = getPool();

	const [linhas] = await pool.query(
		`
		SELECT
			COUNT(*) AS todos,
			SUM(CASE WHEN is_mei = 0 THEN 1 ELSE 0 END) AS sem_mei,
			SUM(CASE WHEN is_mei = 1 THEN 1 ELSE 0 END) AS so_mei,
			SUM(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) AS com_coord,
			SUM(CASE WHEN COALESCE(porte, '') <> 'MICRO EMPRESA' THEN 1 ELSE 0 END) AS sem_micro,
			SUM(CASE WHEN porte IN ('EMPRESA DE PEQUENO PORTE', 'DEMAIS') THEN 1 ELSE 0 END) AS epp_demais,
			SUM(
				CASE
					WHEN latitude IS NOT NULL
						AND longitude IS NOT NULL
						AND COALESCE(porte, '') <> 'MICRO EMPRESA'
					THEN 1 ELSE 0
				END
			) AS coord_sem_micro
		FROM vw_dashboard_estabelecimentos
		`
	);
	const row = (linhas as Array<Record<string, number>>)[0];

	const cenarios: CenarioMitigacao[] = [
		montarCenario(
			'todos',
			'Todos (recorte atual)',
			'Estabelecimentos ativos, Contagem, CNAE 62.',
			Number(row.todos),
			cempreRef,
			{}
		),
		montarCenario(
			'sem_mei',
			'Excluir MEI (flag CNPJ)',
			'Remove is_mei = 1. Se o flag estiver pouco preenchido, o efeito é pequeno.',
			Number(row.sem_mei),
			cempreRef,
			{ mei: '0' }
		),
		montarCenario(
			'com_coord',
			'Somente com coordenada',
			'Mantém apenas registros georreferenciados via CNEFE.',
			Number(row.com_coord),
			cempreRef,
			{ somente_coordenada: true }
		),
		montarCenario(
			'sem_micro',
			'Exceto microempresa',
			'Remove porte MICRO EMPRESA (proxy de formalidade mais próxima do CEMPRE).',
			Number(row.sem_micro),
			cempreRef,
			{ excluir_micro: true }
		),
		montarCenario(
			'epp_demais',
			'Só EPP e demais',
			'Recorte mais restrito por porte.',
			Number(row.epp_demais),
			cempreRef,
			{ excluir_micro: true }
		),
		montarCenario(
			'coord_sem_micro',
			'Com coordenada e sem micro',
			'Combina georreferência e exclusão de microempresa.',
			Number(row.coord_sem_micro),
			cempreRef,
			{ somente_coordenada: true, excluir_micro: true }
		)
	];

	let aggCnae = porCnae;
	if (!aggCnae) {
		const [rowsCnae] = await pool.query(
			`
			SELECT cnae_principal, cnae_descricao, COUNT(*) AS total
			FROM vw_dashboard_estabelecimentos
			GROUP BY cnae_principal, cnae_descricao
			`
		);
		aggCnae = rowsCnae as ResumoDashboard['por_cnae'];
	}

	const mapaApp = new Map<string, number>();
	for (const item of aggCnae) {
		mapaApp.set(item.cnae_principal, Number(item.total));
	}

	const por_classe: ComparativoClasseCempre[] = CEMPRE_CLASSES.map((classe) => {
		const app = classe.cnaes_app.reduce((acc, cod) => acc + (mapaApp.get(cod) ?? 0), 0);
		const desvio = desvioRelativo(app, classe.cempre);
		return {
			codigo_grupo: classe.codigo_grupo,
			rotulo: classe.rotulo,
			cempre: classe.cempre,
			app,
			desvio,
			atende_30: atendeCriterio30(desvio)
		};
	});

	return {
		cempre_ref: cempreRef,
		cempre_ano: '2024',
		nota:
			'O CEMPRE (SIDRA 9528) conta unidades locais em 2024; o app usa estabelecimentos CNPJ (fotografia mais recente). Diferença de conceito e de ano explica parte do desvio. O critério ≤ 30% é meta de alinhamento de recorte.',
		cenarios,
		por_classe
	};
}
