import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  site: 'https://el-j.github.io/run-zero',
  base: '/run-zero',
  output: 'static',
  build: {
    format: 'directory'
  }
});
