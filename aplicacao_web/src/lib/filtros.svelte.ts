/** Estado de filtros compartilhado entre Inventário e Mapa. */
export const filtros = $state({
	busca: '',
	cnae: '',
	porte: '',
	somente_coordenada: false,
	excluir_micro: false
});

export function limparFiltros() {
	filtros.busca = '';
	filtros.cnae = '';
	filtros.porte = '';
	filtros.somente_coordenada = false;
	filtros.excluir_micro = false;
}
