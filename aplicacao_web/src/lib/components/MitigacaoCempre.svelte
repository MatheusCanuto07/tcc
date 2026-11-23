<script lang="ts">
	import { aplicarCenario } from '#lib/filtros.svelte.js';
	import type { MitigacaoCempre } from '#lib/types.js';

	type Props = {
		mitigacao: MitigacaoCempre;
	};

	let { mitigacao }: Props = $props();

	function pct(desvio: number | null): string {
		if (desvio == null) return '—';
		return `${(100 * desvio).toFixed(0)}%`;
	}
</script>

<section class="mitigacao" aria-labelledby="titulo-mitigacao">
	<header>
		<h2 id="titulo-mitigacao">Alinhamento com o CEMPRE</h2>
		<p>
			Referência: {mitigacao.cempre_ref} unidades locais (Contagem, CNAE 62, {mitigacao.cempre_ano}).
			{mitigacao.nota}
		</p>
	</header>

	<div class="bloco">
		<h3>Cenários de recorte</h3>
		<div class="tabela-wrap">
			<table>
				<thead>
					<tr>
						<th>Cenário</th>
						<th>N no app</th>
						<th>Desvio</th>
						<th>≤ 30%</th>
						<th></th>
					</tr>
				</thead>
				<tbody>
					{#each mitigacao.cenarios as c (c.id)}
						<tr class={{ ok: c.atende_30 === true, nok: c.atende_30 === false }}>
							<td>
								<strong>{c.rotulo}</strong>
								<span class="desc">{c.descricao}</span>
							</td>
							<td class="num">{c.total}</td>
							<td class="num">{pct(c.desvio)}</td>
							<td>{c.atende_30 ? 'sim' : 'não'}</td>
							<td>
								<button type="button" onclick={() => aplicarCenario(c.aplicar)}>
									Aplicar na lista
								</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>

	<div class="bloco">
		<h3>Composição por classe CNAE (app × CEMPRE)</h3>
		<div class="tabela-wrap">
			<table>
				<thead>
					<tr>
						<th>Grupo</th>
						<th>App</th>
						<th>CEMPRE</th>
						<th>Desvio</th>
						<th>≤ 30%</th>
					</tr>
				</thead>
				<tbody>
					{#each mitigacao.por_classe as c (c.codigo_grupo)}
						<tr class={{ ok: c.atende_30 === true, nok: c.atende_30 === false }}>
							<td>
								<strong>{c.codigo_grupo}</strong>
								<span class="desc">{c.rotulo}</span>
							</td>
							<td class="num">{c.app}</td>
							<td class="num">{c.cempre}</td>
							<td class="num">{pct(c.desvio)}</td>
							<td>{c.atende_30 ? 'sim' : 'não'}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</section>

<style>
	.mitigacao {
		display: grid;
		gap: 1rem;
		padding: 1rem 0 0.25rem;
		border-top: 1px solid var(--line);
	}

	header h2 {
		margin: 0;
		font-family: var(--font-display);
		font-size: 1.05rem;
		font-weight: 700;
	}

	header p {
		margin: 0.4rem 0 0;
		font-size: 0.86rem;
		color: var(--ink-soft);
		max-width: 75ch;
		line-height: 1.45;
	}

	.bloco h3 {
		margin: 0 0 0.55rem;
		font-family: var(--font-display);
		font-size: 0.95rem;
		font-weight: 700;
	}

	.tabela-wrap {
		overflow: auto;
		border: 1px solid var(--line);
		background: #fff;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.84rem;
	}

	th,
	td {
		padding: 0.55rem 0.65rem;
		border-bottom: 1px solid #e5e7eb;
		text-align: left;
		vertical-align: top;
	}

	th {
		background: #f3f4f6;
		font-size: 0.74rem;
		font-weight: 600;
		color: var(--ink-soft);
	}

	.num {
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
	}

	.desc {
		display: block;
		margin-top: 0.15rem;
		font-size: 0.75rem;
		font-weight: 400;
		color: var(--ink-soft);
		max-width: 42ch;
	}

	tr.ok td:nth-child(4),
	tr.ok td:nth-child(5) {
		color: var(--ok);
		font-weight: 600;
	}

	tr.nok td:nth-child(4) {
		color: var(--warn);
		font-weight: 600;
	}

	button {
		border: 1px solid var(--line);
		background: #fff;
		color: var(--accent);
		padding: 0.3rem 0.55rem;
		font: inherit;
		font-size: 0.78rem;
		font-weight: 600;
		cursor: pointer;
		border-radius: var(--radius);
		white-space: nowrap;
	}

	button:hover {
		background: var(--accent-soft);
		border-color: var(--accent);
	}
</style>
