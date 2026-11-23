<script lang="ts">
	import { filtrarEstabelecimentos } from '#lib/filtrar.js';
	import { filtros, limparFiltros } from '#lib/filtros.svelte.js';
	import { formatarCnpj, nomeExibicao } from '#lib/formatacao.js';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let filtrados = $derived(filtrarEstabelecimentos(data.estabelecimentos, filtros));

	let portes = $derived(
		[...new Set(data.estabelecimentos.map((e) => e.porte).filter(Boolean) as string[])].sort()
	);

	let maxCnae = $derived(Math.max(...data.resumo.por_cnae.map((c) => Number(c.total)), 1));
</script>

<svelte:head>
	<title>Inventário — Contagem · CNAE 62</title>
</svelte:head>

<main class="inventario">
	<header class="intro">
		<h1>Inventário</h1>
		<p>Busque, filtre pela lateral e consulte a lista de estabelecimentos.</p>
	</header>

	<section class="busca-faixa" aria-label="Busca e filtros">
		<label class="campo cresce">
			<span>Buscar</span>
			<input type="search" bind:value={filtros.busca} placeholder="Nome, CNPJ ou bairro" />
		</label>
		<label class="campo">
			<span>CNAE</span>
			<select bind:value={filtros.cnae}>
				<option value="">Todos</option>
				{#each data.resumo.por_cnae as item (item.cnae_principal)}
					<option value={item.cnae_principal}>{item.cnae_principal} ({item.total})</option>
				{/each}
			</select>
		</label>
		<label class="campo">
			<span>Porte</span>
			<select bind:value={filtros.porte} disabled={filtros.excluir_micro}>
				<option value="">Todos</option>
				{#each portes as p (p)}
					<option value={p}>{p}</option>
				{/each}
			</select>
		</label>
		<label class="campo">
			<span>MEI</span>
			<select bind:value={filtros.mei}>
				<option value="">Todos</option>
				<option value="1">Somente MEI</option>
				<option value="0">Exceto MEI</option>
			</select>
		</label>
		<label class="check">
			<input type="checkbox" bind:checked={filtros.somente_coordenada} />
			Só com coordenada
		</label>
		<label class="check">
			<input type="checkbox" bind:checked={filtros.excluir_micro} />
			Exceto micro
		</label>
		<button type="button" class="ghost" onclick={limparFiltros}>Limpar</button>
	</section>

	<section class="grade">
		<aside class="lateral">
			<h2>Por CNAE</h2>
			<ul class="barras">
				{#each data.resumo.por_cnae as item (item.cnae_principal)}
					<li>
						<button
							type="button"
							class={{ ativo: filtros.cnae === item.cnae_principal }}
							onclick={() =>
								(filtros.cnae =
									filtros.cnae === item.cnae_principal ? '' : item.cnae_principal)}
						>
							<span class="codigo">{item.cnae_principal}</span>
							<span class="qtd">{item.total}</span>
							<span class="trilha" aria-hidden="true">
								<span
									class="preenchimento"
									style:width="{(100 * Number(item.total)) / maxCnae}%"
								></span>
							</span>
							<span class="desc">{item.cnae_descricao}</span>
						</button>
					</li>
				{/each}
			</ul>

			<h2 class="sub">Porte</h2>
			<ul class="portes">
				{#each data.resumo.por_porte as item (item.porte)}
					<li>
						<button
							type="button"
							class={{ ativo: filtros.porte === item.porte }}
							onclick={() =>
								(filtros.porte = filtros.porte === item.porte ? '' : item.porte)}
						>
							{item.porte}
							<strong>{item.total}</strong>
						</button>
					</li>
				{/each}
			</ul>
		</aside>

		<section class="lista">
			<div class="lista-cab">
				<h2>Estabelecimentos</h2>
				<p>{filtrados.length} registros</p>
			</div>
			<div class="tabela-wrap">
				<table>
					<thead>
						<tr>
							<th>Nome</th>
							<th>CNPJ</th>
							<th>CNAE</th>
							<th>Porte</th>
							<th>Bairro</th>
							<th>Coord.</th>
						</tr>
					</thead>
					<tbody>
						{#each filtrados.slice(0, 200) as e (e.cnpj_completo)}
							<tr>
								<td>{nomeExibicao(e)}</td>
								<td class="cnpj">{formatarCnpj(e.cnpj_completo)}</td>
								<td title={e.cnae_descricao ?? ''}>{e.cnae_principal}</td>
								<td>{e.porte ?? '—'}</td>
								<td>{e.bairro ?? '—'}</td>
								<td>{e.latitude != null ? 'sim' : 'não'}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			{#if filtrados.length > 200}
				<p class="nota">Mostrando os primeiros 200 de {filtrados.length}.</p>
			{/if}
			{#if filtrados.length === 0}
				<p class="nota">Nenhum estabelecimento com esses filtros. Limpe a busca para ver a lista.</p>
			{/if}
		</section>
	</section>
</main>

<style>
	.inventario {
		display: grid;
		gap: 1.1rem;
		flex: 1;
	}

	.intro h1 {
		margin: 0;
		font-family: var(--font-display);
		font-weight: 700;
		font-size: clamp(1.45rem, 2.4vw, 1.85rem);
		line-height: 1.25;
		color: var(--ink);
	}

	.intro p {
		margin: 0.4rem 0 0;
		color: var(--ink-soft);
		max-width: 52ch;
	}

	.busca-faixa {
		display: grid;
		grid-template-columns: 1.5fr 0.9fr 0.9fr 0.75fr auto auto auto;
		gap: 0.65rem;
		align-items: end;
		padding: 0.85rem 0;
		border-block: 1px solid var(--line);
	}

	.check {
		display: flex;
		align-items: center;
		gap: 0.35rem;
		font-size: 0.8rem;
		color: var(--ink-soft);
		padding-bottom: 0.45rem;
		white-space: nowrap;
	}

	.campo {
		display: grid;
		gap: 0.25rem;
		font-size: 0.78rem;
		color: var(--ink-soft);
	}

	.campo input,
	.campo select {
		width: 100%;
		border: 1px solid var(--line);
		border-radius: var(--radius);
		padding: 0.5rem 0.6rem;
		font: inherit;
		color: var(--ink);
		background: #fff;
	}

	.ghost {
		border: 1px solid var(--line);
		background: #fff;
		color: var(--ink-soft);
		padding: 0.5rem 0.8rem;
		font: inherit;
		font-size: 0.85rem;
		border-radius: var(--radius);
		cursor: pointer;
		height: fit-content;
	}

	.ghost:hover {
		color: var(--ink);
		border-color: var(--ink-soft);
	}

	.grade {
		display: grid;
		grid-template-columns: minmax(230px, 0.85fr) minmax(0, 1.7fr);
		gap: 1.25rem;
		align-items: start;
	}

	.lateral,
	.lista {
		min-width: 0;
	}

	h2 {
		margin: 0 0 0.7rem;
		font-family: var(--font-display);
		font-size: 1rem;
		font-weight: 700;
	}

	.sub {
		margin-top: 1.25rem;
	}

	.barras,
	.portes {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		gap: 0.3rem;
	}

	.barras button,
	.portes button {
		width: 100%;
		border: 1px solid transparent;
		background: transparent;
		padding: 0.45rem 0.35rem;
		border-radius: var(--radius);
		cursor: pointer;
		font: inherit;
		color: inherit;
		text-align: left;
	}

	.barras button {
		display: grid;
		grid-template-columns: auto 1fr;
		grid-template-areas:
			'codigo qtd'
			'trilha trilha'
			'desc desc';
		gap: 0.12rem 0.55rem;
	}

	.barras button:hover,
	.barras button.ativo,
	.portes button:hover,
	.portes button.ativo {
		background: var(--surface);
		border-color: var(--line);
	}

	.barras button.ativo,
	.portes button.ativo {
		border-color: var(--accent);
		background: var(--accent-soft);
	}

	.codigo {
		grid-area: codigo;
		font-weight: 600;
		font-variant-numeric: tabular-nums;
		font-size: 0.86rem;
	}

	.qtd {
		grid-area: qtd;
		justify-self: end;
		font-variant-numeric: tabular-nums;
		font-weight: 600;
		color: var(--accent);
	}

	.trilha {
		grid-area: trilha;
		display: block;
		height: 3px;
		background: #e5e7eb;
		overflow: hidden;
	}

	.preenchimento {
		display: block;
		height: 100%;
		background: var(--accent);
	}

	.desc {
		grid-area: desc;
		font-size: 0.74rem;
		color: var(--ink-soft);
		line-height: 1.35;
	}

	.portes button {
		display: flex;
		justify-content: space-between;
		gap: 0.75rem;
	}

	.portes strong {
		font-variant-numeric: tabular-nums;
		color: var(--accent);
	}

	.lista-cab {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 1rem;
		margin-bottom: 0.5rem;
	}

	.lista-cab h2 {
		margin: 0;
	}

	.lista-cab p {
		margin: 0;
		font-size: 0.82rem;
		color: var(--ink-soft);
		font-variant-numeric: tabular-nums;
	}

	.tabela-wrap {
		overflow: auto;
		max-height: min(66vh, 680px);
		border: 1px solid var(--line);
		background: #fff;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.86rem;
	}

	th,
	td {
		padding: 0.55rem 0.7rem;
		border-bottom: 1px solid #e5e7eb;
		text-align: left;
		vertical-align: top;
	}

	th {
		position: sticky;
		top: 0;
		background: #f3f4f6;
		z-index: 1;
		font-size: 0.74rem;
		font-weight: 600;
		color: var(--ink-soft);
	}

	tbody tr:hover td {
		background: var(--accent-soft);
	}

	.cnpj {
		font-variant-numeric: tabular-nums;
		font-size: 0.8rem;
		white-space: nowrap;
	}

	.nota {
		margin: 0.55rem 0 0;
		font-size: 0.82rem;
		color: var(--ink-soft);
	}

	@media (max-width: 960px) {
		.busca-faixa,
		.grade {
			grid-template-columns: 1fr;
		}

		.ghost {
			justify-self: start;
		}
	}
</style>
