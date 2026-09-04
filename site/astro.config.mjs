// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import catppuccin from '@catppuccin/starlight';

export default defineConfig({
  site: 'https://ghchinoy.github.io',
  base: '/audio-tools-for-agents',
  integrations: [
    starlight({
      title: 'Audio Tools for Agents',
      description: 'Deterministic audio manipulation and local deep-learning stem separation for AI agents',
      logo: {
        src: './public/favicon.svg',
      },
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/ghchinoy/audio-tools-for-agents',
        },
      ],
      plugins: [
        catppuccin({
          dark: { flavor: 'mocha', accent: 'mauve' },
          light: { flavor: 'latte', accent: 'mauve' },
        }),
      ],
      sidebar: [
        {
          label: 'Getting Started',
          items: [
            { label: 'Quickstart', slug: 'getting-started/quickstart' },
            { label: 'Configuration', slug: 'getting-started/configuration' },
          ],
        },
        {
          label: 'Delivery Surfaces',
          items: [
            { label: 'Agent-Aware CLI', slug: 'surfaces/cli' },
            { label: 'Model Context Protocol (MCP)', slug: 'surfaces/mcp' },
            { label: 'Agent Skills', slug: 'surfaces/skills' },
            { label: 'Agent Plugins Spec', slug: 'surfaces/plugins' },
          ],
        },
        {
          label: 'Architecture',
          items: [
            { label: 'HTDemucs Neural DSP', slug: 'architecture/htdemucs' },
            { label: 'Memory & Telemetry', slug: 'architecture/telemetry' },
          ],
        },
        {
          label: 'Reference',
          items: [
            { label: 'Model Selection Matrix', slug: 'reference/models' },
            { label: 'Error Code Catalog', slug: 'reference/error-codes' },
          ],
        },
      ],
    }),
  ],
});
