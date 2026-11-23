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

export type CenarioMitigacao = {
	id: string;
	rotulo: string;
	descricao: string;
	total: number;
	desvio: number | null;
	atende_30: boolean | null;
	/** Como aplicar o cenário nos filtros da UI. */
	aplicar: {
		mei?: '' | '0' | '1';
		porte?: string;
		excluir_micro?: boolean;
		somente_coordenada?: boolean;
	};
};

export type ComparativoClasseCempre = {
	codigo_grupo: string;
	rotulo: string;
	cempre: number;
	app: number;
	desvio: number | null;
	atende_30: boolean | null;
};

export type MitigacaoCempre = {
	cempre_ref: number;
	cempre_ano: string;
	nota: string;
	cenarios: CenarioMitigacao[];
	por_classe: ComparativoClasseCempre[];
};

export type ResumoDashboard = {
	total: number;
	com_coordenada: number;
	sem_coordenada: number;
	mei: number;
	data_fotografia: string | null;
	cempre_ref: number;
	desvio_cempre: number | null;
	atende_criterio_30: boolean | null;
	por_cnae: CnaeAgg[];
	por_porte: PorteAgg[];
	mitigacao: MitigacaoCempre;
};

export type FiltrosEstabelecimento = {
	q?: string;
	cnae?: string;
	porte?: string;
	mei?: '0' | '1' | '';
};
