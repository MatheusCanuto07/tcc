export type Estabelecimento = {
	cnpj_completo: string;
	razao_social: string | null;
	nome_fantasia: string | null;
	cnae_principal: string;
	cnae_descricao: string | null;
	porte: string | null;
	is_mei: number | null;
	latitude: number | null;
	longitude: number | null;
	nivel_juncao_cnefe: string | null;
	nivel_geo_cnefe: string | null;
	bairro: string | null;
	cep: string | null;
	data_fotografia: string | null;
};

export type CnaeAgg = {
	cnae_principal: string;
	cnae_descricao: string | null;
	total: number;
};

export type PorteAgg = {
	porte: string;
	total: number;
};

export type ResumoDashboard = {
	total: number;
	com_coordenada: number;
	sem_coordenada: number;
	mei: number;
	data_fotografia: string | null;
	por_cnae: CnaeAgg[];
	por_porte: PorteAgg[];
};

export type FiltrosEstabelecimento = {
	q?: string;
	cnae?: string;
	porte?: string;
	mei?: '0' | '1' | '';
};
