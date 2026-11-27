import type { Estabelecimento } from '#lib/types.js';

export type FiltrosCliente = {
	busca: string;
	cnae: string;
	porte: string;
	mei: '' | '0' | '1';
	somente_coordenada?: boolean;
};

export function filtrarEstabelecimentos(
	lista: Estabelecimento[],
	f: FiltrosCliente
): Estabelecimento[] {
	const q = f.busca.trim().toLowerCase();
	return lista.filter((e) => {
		if (f.cnae && e.cnae_principal !== f.cnae) return false;
		if (f.porte && (e.porte ?? '') !== f.porte) return false;
		if (f.mei === '0' && e.is_mei !== 0) return false;
		if (f.mei === '1' && e.is_mei !== 1) return false;
		if (f.somente_coordenada && (e.latitude == null || e.longitude == null)) return false;
		if (!q) return true;
		const hay = [e.razao_social, e.nome_fantasia, e.cnpj_completo, e.bairro, e.cnae_descricao]
			.filter(Boolean)
			.join(' ')
			.toLowerCase();
		return hay.includes(q);
	});
}
