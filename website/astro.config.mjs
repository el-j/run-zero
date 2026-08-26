import { defineConfig } from 'astro/config';

// https://astro.build/config
const site = process.env.DEPLOY_SITE || 'https://el-j.github.io/run-zero';
const base = process.env.DEPLOY_BASE || '/run-zero';

export default defineConfig({
  site,
  base,
  output: 'static',
  build: {
    format: 'directory'
  }
});
