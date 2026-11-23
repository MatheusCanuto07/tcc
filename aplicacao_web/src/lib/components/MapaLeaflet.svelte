<script lang="ts">
	import type { Estabelecimento } from '#lib/types.js';

	type Props = {
		pontos: Estabelecimento[];
	};

	let { pontos }: Props = $props();

	let container: HTMLDivElement | undefined = $state();

	const centroContagem: [number, number] = [-19.921, -44.051];

	$effect(() => {
		const el = container;
		const lista = pontos;
		if (!el) return;

		let cancelado = false;
		let mapa: import('leaflet').Map | null = null;

		async function iniciar() {
			const L = await import('leaflet');
			await import('leaflet/dist/leaflet.css');
			if (cancelado || !el) return;

			mapa = L.map(el, {
				zoomControl: true,
				attributionControl: true
			}).setView(centroContagem, 12);

			L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
				attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
				maxZoom: 19
			}).addTo(mapa);

			const camada = L.layerGroup().addTo(mapa);
			const coords: [number, number][] = [];

			for (const p of lista) {
				if (p.latitude == null || p.longitude == null) continue;
				const lat = Number(p.latitude);
				const lng = Number(p.longitude);
				if (!Number.isFinite(lat) || !Number.isFinite(lng)) continue;

				coords.push([lat, lng]);
				const nome = p.nome_fantasia || p.razao_social || p.cnpj_completo;
				L.circleMarker([lat, lng], {
					radius: 5,
					color: '#163a66',
					fillColor: '#1d4e89',
					fillOpacity: 0.78,
					weight: 1
				})
					.bindPopup(
						`<div class="popup-academico">` +
							`<strong>${escapeHtml(nome)}</strong>` +
							`<p>CNAE ${escapeHtml(p.cnae_principal)}<br>${escapeHtml(p.cnae_descricao ?? '')}</p>` +
							`<p>${escapeHtml(formatarCnpj(p.cnpj_completo))}</p>` +
							`<p class="aviso">Posição aproximada (CNEFE)</p>` +
							`</div>`
					)
					.addTo(camada);
			}

			if (coords.length > 0) {
				mapa.fitBounds(L.latLngBounds(coords), { padding: [28, 28], maxZoom: 14 });
			}

			requestAnimationFrame(() => mapa?.invalidateSize());
		}

		iniciar();

		return () => {
			cancelado = true;
			mapa?.remove();
			mapa = null;
		};
	});

	function escapeHtml(texto: string): string {
		return texto
			.replaceAll('&', '&amp;')
			.replaceAll('<', '&lt;')
			.replaceAll('>', '&gt;')
			.replaceAll('"', '&quot;');
	}

	function formatarCnpj(cnpj: string): string {
		const d = cnpj.replace(/\D/g, '');
		if (d.length !== 14) return cnpj;
		return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5, 8)}/${d.slice(8, 12)}-${d.slice(12)}`;
	}
</script>

<div
	class="mapa"
	bind:this={container}
	role="img"
	aria-label="Mapa de estabelecimentos de TI em Contagem"
></div>

<style>
	.mapa {
		width: 100%;
		height: 100%;
		min-height: 420px;
		overflow: hidden;
		background: #e5e7eb;
	}

	.mapa :global(.leaflet-container) {
		width: 100%;
		height: 100%;
		font: inherit;
		background: #e5e7eb;
	}

	.mapa :global(.leaflet-popup-content-wrapper) {
		border-radius: 2px;
		box-shadow: 0 6px 18px rgb(17 24 39 / 0.14);
		border: 1px solid #d1d5db;
	}

	.mapa :global(.leaflet-popup-content) {
		margin: 0.7rem 0.85rem;
		font-family: 'IBM Plex Sans', 'Segoe UI', sans-serif;
		font-size: 0.84rem;
		line-height: 1.4;
		color: #111827;
	}

	.mapa :global(.popup-academico strong) {
		font-family: 'Libre Baskerville', 'Times New Roman', serif;
		font-size: 0.95rem;
	}

	.mapa :global(.popup-academico p) {
		margin: 0.35rem 0 0;
		color: #4b5563;
	}

	.mapa :global(.popup-academico .aviso) {
		font-size: 0.72rem;
		color: #1d4e89;
	}

	.mapa :global(.leaflet-control-zoom a) {
		border-radius: 0 !important;
		color: #111827 !important;
	}
</style>
