/** Referência CEMPRE Contagem — unidades locais, divisão 62, ano 2024 (SIDRA 9528). */
export const CEMPRE_TOTAL_REF = 535;

export type CempreClasse = {
	codigo_grupo: string;
	rotulo: string;
	cempre: number;
	/** Prefixos/códigos CNAE 7 dígitos equivalentes no CNPJ. */
	cnaes_app: string[];
};

export const CEMPRE_CLASSES: CempreClasse[] = [
	{
		codigo_grupo: '62.01',
		rotulo: 'Desenvolvimento de programas sob encomenda',
		cempre: 134,
		cnaes_app: ['6201501', '6201502']
	},
	{
		codigo_grupo: '62.02',
		rotulo: 'Programas customizáveis',
		cempre: 66,
		cnaes_app: ['6202300']
	},
	{
		codigo_grupo: '62.03',
		rotulo: 'Programas não customizáveis',
		cempre: 22,
		cnaes_app: ['6203100']
	},
	{
		codigo_grupo: '62.04',
		rotulo: 'Consultoria em TI',
		cempre: 111,
		cnaes_app: ['6204000']
	},
	{
		codigo_grupo: '62.09',
		rotulo: 'Suporte técnico e outros serviços em TI',
		cempre: 202,
		cnaes_app: ['6209100']
	}
];

export function desvioRelativo(nApp: number, nRef: number): number | null {
	if (nRef <= 0) return null;
	return Math.abs(nApp - nRef) / nRef;
}

export function atendeCriterio30(desvio: number | null): boolean | null {
	if (desvio === null) return null;
	return desvio <= 0.3;
}
