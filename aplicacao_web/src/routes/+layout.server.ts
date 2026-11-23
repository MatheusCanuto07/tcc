import {
	listarEstabelecimentos,
	obterResumo
} from '#lib/server/estabelecimentos.js';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async () => {
	const [resumo, estabelecimentos] = await Promise.all([
		obterResumo(),
		listarEstabelecimentos()
	]);

	return { resumo, estabelecimentos };
};
