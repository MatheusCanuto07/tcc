import type { Estabelecimento } from '#lib/types.js';

export function formatarCnpj(cnpj: string): string {
	const d = cnpj.replace(/\D/g, '');
	if (d.length !== 14) return cnpj;
	return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5, 8)}/${d.slice(8, 12)}-${d.slice(12)}`;
}

export function nomeExibicao(e: Estabelecimento): string {
	return e.nome_fantasia?.trim() || e.razao_social?.trim() || e.cnpj_completo;
}

export function pct(n: number, d: number): string {
	if (!d) return '—';
	return `${((100 * n) / d).toFixed(0)}%`;
}

export function formatarData(valor: string | Date | null): string {
	if (!valor) return '—';
	const bruto = valor instanceof Date ? valor.toISOString() : String(valor);
	const iso = bruto.match(/^(\d{4}-\d{2}-\d{2})/);
	if (iso) return iso[1];
	const parseado = new Date(bruto);
	if (!Number.isNaN(parseado.getTime())) {
		return parseado.toISOString().slice(0, 10);
	}
	return bruto;
}
