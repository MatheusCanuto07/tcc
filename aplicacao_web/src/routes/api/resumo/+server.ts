import { json } from '@sveltejs/kit';
import { obterResumo } from '#lib/server/estabelecimentos.js';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async () => {
	const resumo = await obterResumo();
	return json(resumo);
};
