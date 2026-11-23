/** Estado de filtros compartilhado entre Inventário e Mapa. */
export const filtros = $state({
	busca: '',
	cnae: '',
	porte: '',
	mei: '' as '' | '0' | '1',
	somente_coordenada: false,
	excluir_micro: false
});

export function limparFiltros() {
	filtros.busca = '';
	filtros.cnae = '';
	filtros.porte = '';
	filtros.mei = '';
	filtros.somente_coordenada = false;
	filtros.excluir_micro = false;
}

export function aplicarCenario(aplicar: {
	mei?: '' | '0' | '1';
	porte?: string;
	excluir_micro?: boolean;
	somente_coordenada?: boolean;
}) {
	limparFiltros();
	if (aplicar.mei) filtros.mei = aplicar.mei;
	if (aplicar.porte) filtros.porte = aplicar.porte;
	if (aplicar.excluir_micro) filtros.excluir_micro = true;
	if (aplicar.somente_coordenada) filtros.somente_coordenada = true;
}
