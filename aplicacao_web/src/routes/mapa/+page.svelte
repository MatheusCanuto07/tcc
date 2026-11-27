<script lang="ts">
	import MapaLeaflet from '#lib/components/MapaLeaflet.svelte';
	import { filtrarEstabelecimentos } from '#lib/filtrar.js';
	import { filtros } from '#lib/filtros.svelte.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let filtrados = $derived(filtrarEstabelecimentos(data.estabelecimentos, filtros));
	let noMapa = $derived(filtrados.filter((e) => e.latitude != null && e.longitude != null));
</script>

<svelte:head>
	<title>Mapa — Contagem · CNAE 62</title>
</svelte:head>

<main class="mapa-pagina">
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
