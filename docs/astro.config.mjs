import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://10clouds.github.io',
	base: '/aiconsole',
	integrations: [
		starlight({
			title: 'AIConsole Documentation',
			logo: {
				src: './src/assets/logo.png',
			},
			social: {
				github: 'https://github.com/10clouds/aiconsole',
			},
			customCss: [
				'./src/styles/custom.css',
			],
			sidebar: [
				{
					label: 'Guides',
					autogenerate: { directory: 'guides' },
				},
				{
					label: 'Reference',
					autogenerate: { directory: 'reference' },
				},
			],
		}),
	],
});
