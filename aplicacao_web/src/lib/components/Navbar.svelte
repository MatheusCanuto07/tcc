<script lang="ts">
	import { page } from '$app/state';

	const rota = $derived(page.url.pathname);
</script>

<header class="navbar">
	<a class="marca" href="/">
		Contagem · CNAE 62
		<small>Trabalho de conclusão de curso</small>
	</a>
	<nav aria-label="Seções">
		<a href="/" class={{ ativo: rota === '/' }} data-sveltekit-preload-data="hover">Inventário</a>
		<span class="sep" aria-hidden="true">|</span>
		<a
			href="/mapa"
			class={{ ativo: rota.startsWith('/mapa') }}
			data-sveltekit-preload-data="hover"
		>
			Mapa
		</a>
	</nav>
</header>

<style>
	.navbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1.25rem;
		padding: 0.95rem 0;
		background: #fff;
		border-bottom: 1px solid var(--line-strong);
	}

	.marca {
		font-family: var(--font-display);
		font-weight: 700;
		font-size: 1.05rem;
		line-height: 1.25;
		color: var(--ink);
		text-decoration: none;
	}

	.marca small {
		display: block;
		margin-top: 0.2rem;
		font-family: var(--font-body);
		font-weight: 500;
		font-size: 0.72rem;
		color: var(--ink-soft);
	}

	nav {
		display: flex;
		align-items: center;
		gap: 0.15rem;
		flex-shrink: 0;
	}

	nav a {
		font-family: var(--font-body);
		font-weight: 500;
		font-size: 0.92rem;
		text-decoration: none;
		color: var(--ink-soft);
		padding: 0.35rem 0.55rem;
	}

	nav a:hover {
		color: var(--ink);
	}

	nav a.ativo {
		color: var(--accent);
		box-shadow: inset 0 -2px 0 var(--accent);
	}

	.sep {
		color: #c4c9d0;
		padding: 0 0.1rem;
		user-select: none;
	}

	@media (max-width: 560px) {
		.navbar {
			flex-direction: column;
			align-items: flex-start;
		}
	}
</style>
