import { json } from '@sveltejs/kit';
import { listarEstabelecimentos } from '#lib/server/estabelecimentos.js';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url }) => {
	const q = url.searchParams.get('q') ?? '';
	const cnae = url.searchParams.get('cnae') ?? '';
	const porte = url.searchParams.get('porte') ?? '';
	const meiRaw = url.searchParams.get('mei') ?? '';
	const mei = meiRaw === '0' || meiRaw === '1' ? meiRaw : '';

	const dados = await listarEstabelecimentos({ q, cnae, porte, mei });
	return json({ total: dados.length, dados });
};
