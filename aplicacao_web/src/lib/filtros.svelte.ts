/** Estado de filtros compartilhado entre Inventário e Mapa. */
export const filtros = $state({
	busca: '',
	cnae: '',
	porte: '',
	mei: '' as '' | '0' | '1',
	somente_coordenada: false
});

export function limparFiltros() {
	filtros.busca = '';
	filtros.cnae = '';
	filtros.porte = '';
	filtros.mei = '';
	filtros.somente_coordenada = false;
}
