import { json } from '@sveltejs/kit';
import { listarEstabelecimentos } from '#lib/server/estabelecimentos.js';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url }) => {
	const q = url.searchParams.get('q') ?? '';
	const cnae = url.searchParams.get('cnae') ?? '';
	const porte = url.searchParams.get('porte') ?? '';

	const dados = await listarEstabelecimentos({ q, cnae, porte });
	return json({ total: dados.length, dados });
};
