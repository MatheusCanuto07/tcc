<script lang="ts">
	import MapaLeaflet from '#lib/components/MapaLeaflet.svelte';
	import { filtrarEstabelecimentos } from '#lib/filtrar.js';
	import { filtros, limparFiltros } from '#lib/filtros.svelte.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let filtrados = $derived(filtrarEstabelecimentos(data.estabelecimentos, filtros));
	let noMapa = $derived(filtrados.filter((e) => e.latitude != null && e.longitude != null));

	let temFiltro = $derived(
		Boolean(
			filtros.busca ||
				filtros.cnae ||
				filtros.porte ||
				filtros.somente_coordenada ||
				filtros.excluir_micro
		)
	);
</script>

<svelte:head>
	<title>Mapa — Contagem · CNAE 62</title>
</svelte:head>

<main class="mapa-pagina">
	<header class="intro">
		<div>
			<h1>Mapa</h1>
			<p>
				{noMapa.length} estabelecimentos com coordenada
				{#if temFiltro}
					(filtro atual: {filtrados.length})
				{/if}.
				Posições derivadas do CNEFE — em geral por CEP, não pela porta do estabelecimento.
			</p>
		</div>
		{#if temFiltro}
			<button type="button" class="ghost" onclick={limparFiltros}>Limpar filtros</button>
		{/if}
	</header>

	<section class="palco" aria-label="Mapa de Contagem">
		<div class="legenda">
			<span class="ponto" aria-hidden="true"></span>
			Distribuição aproximada em Contagem
			{#if filtros.cnae}
				<span class="tag">CNAE {filtros.cnae}</span>
			{/if}
			{#if filtros.porte}
				<span class="tag">{filtros.porte}</span>
			{/if}
		</div>
		<MapaLeaflet pontos={noMapa} />
	</section>
</main>

<style>
	.mapa-pagina {
		display: flex;
		flex-direction: column;
		gap: 0.9rem;
		flex: 1;
		min-height: 0;
	}

	.intro {
		display: flex;
		justify-content: space-between;
		align-items: end;
		gap: 1rem;
	}

	.intro h1 {
		margin: 0;
		font-family: var(--font-display);
		font-weight: 700;
		font-size: clamp(1.45rem, 2.4vw, 1.85rem);
		line-height: 1.25;
	}

	.intro p {
		margin: 0.35rem 0 0;
		color: var(--ink-soft);
		font-size: 0.9rem;
		max-width: 58ch;
		font-variant-numeric: tabular-nums;
	}

	.ghost {
		border: 1px solid var(--line);
		background: #fff;
		color: var(--ink-soft);
		padding: 0.45rem 0.75rem;
		font: inherit;
		font-size: 0.85rem;
		border-radius: var(--radius);
		cursor: pointer;
		white-space: nowrap;
	}

	.ghost:hover {
		color: var(--ink);
		border-color: var(--ink-soft);
	}

	.palco {
		flex: 1;
		display: flex;
		flex-direction: column;
		min-height: min(70vh, 640px);
		border: 1px solid var(--line);
		background: #fff;
		overflow: hidden;
	}

	.legenda {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 0.45rem 0.65rem;
		padding: 0.55rem 0.85rem;
		border-bottom: 1px solid var(--line);
		font-size: 0.82rem;
		color: var(--ink-soft);
		background: var(--surface);
		z-index: 2;
	}

	.ponto {
		width: 0.5rem;
		height: 0.5rem;
		border-radius: 50%;
		background: var(--accent);
		box-shadow: 0 0 0 2px rgb(29 78 137 / 0.2);
	}

	.tag {
		display: inline-block;
		padding: 0.1rem 0.4rem;
		background: var(--accent-soft);
		color: var(--accent);
		border: 1px solid rgb(29 78 137 / 0.2);
		font-size: 0.74rem;
		font-weight: 600;
	}

	.palco :global(.mapa) {
		flex: 1;
		min-height: 480px;
	}
</style>
