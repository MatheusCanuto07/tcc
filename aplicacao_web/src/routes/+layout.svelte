<script lang="ts">
	import '../app.css';
	import Navbar from '#lib/components/Navbar.svelte';
	import favicon from '#lib/assets/favicon.svg';
	import { formatarData, pct } from '#lib/formatacao.js';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

	let desvioPct = $derived(
		data.resumo.desvio_cempre == null ? null : 100 * data.resumo.desvio_cempre
	);
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link
		href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Libre+Baskerville:wght@400;700&display=swap"
		rel="stylesheet"
	/>
	<meta
		name="description"
		content="Inventário e mapa de estabelecimentos de TI (CNAE 62) em Contagem/MG"
	/>
</svelte:head>

<div class="app">
	<div class="topo">
		<Navbar />
		<p class="contexto">
			Base CNPJ (fotografia {formatarData(data.resumo.data_fotografia)}), município IBGE 3118601,
			CNAE divisão 62, comparado ao CEMPRE.
		</p>
		<ul class="leituras">
			<li>
				<span>Na aplicação</span>
				<strong>{data.resumo.total}</strong>
			</li>
			<li>
				<span>Com coordenada</span>
				<strong>
					{data.resumo.com_coordenada}
					<small>{pct(data.resumo.com_coordenada, data.resumo.total)}</small>
				</strong>
			</li>
			<li>
				<span>CEMPRE (ref.)</span>
				<strong>{data.resumo.cempre_ref}</strong>
			</li>
			<li
				class={{
					alerta: data.resumo.atende_criterio_30 === false,
					ok: data.resumo.atende_criterio_30 === true
				}}
			>
				<span>Desvio vs CEMPRE</span>
				<strong>
					{desvioPct == null ? '—' : `${desvioPct.toFixed(0)}%`}
					<small>{data.resumo.atende_criterio_30 ? 'dentro de 30%' : 'acima de 30%'}</small>
				</strong>
			</li>
		</ul>
	</div>

	<div class="conteudo">
		{@render children()}
	</div>
</div>

<style>
	.app {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	.topo {
		width: min(100%, var(--max));
		margin: 0 auto;
		padding: 0.35rem 1.25rem 0;
		background: #fff;
	}

	.contexto {
		margin: 0.75rem 0 0;
		font-size: 0.88rem;
		color: var(--ink-soft);
		max-width: 62ch;
		line-height: 1.45;
	}

	.leituras {
		list-style: none;
		margin: 0.9rem 0 0;
		padding: 0.85rem 0 0;
		border-top: 1px solid var(--line);
		display: grid;
		grid-template-columns: repeat(4, minmax(0, 1fr));
		gap: 0.75rem 1rem;
	}

	.leituras li {
		display: grid;
		gap: 0.15rem;
		min-width: 0;
	}

	.leituras span {
		font-size: 0.74rem;
		color: var(--ink-soft);
	}

	.leituras strong {
		font-family: var(--font-display);
		font-weight: 700;
		font-size: 1.2rem;
		font-variant-numeric: tabular-nums;
		display: flex;
		align-items: baseline;
		gap: 0.35rem;
		flex-wrap: wrap;
	}

	.leituras small {
		font-family: var(--font-body);
		font-weight: 500;
		font-size: 0.72rem;
		color: var(--ink-soft);
	}

	.leituras .alerta strong {
		color: var(--warn);
	}

	.leituras .ok strong {
		color: var(--ok);
	}

	.conteudo {
		flex: 1;
		width: min(100%, var(--max));
		margin: 0 auto;
		padding: 1.15rem 1.25rem 2.75rem;
		display: flex;
		flex-direction: column;
		min-height: 0;
		border-top: 1px solid var(--line);
		margin-top: 1rem;
	}

	@media (max-width: 720px) {
		.leituras {
			grid-template-columns: 1fr 1fr;
		}
	}
</style>
