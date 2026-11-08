// MIT. Same final world and assets; switch only the local query backend for a CPU comparison.
import {defineConfig,mergeConfig} from 'vite';
import {fileURLToPath} from 'node:url';
import base from '../../vite.config.js';
export default mergeConfig(base,defineConfig({resolve:{alias:[{find:/(?:^|\/)r21-triangle-index\.js$/,replacement:fileURLToPath(new URL('./native-r21-query.mjs',import.meta.url))}]}}));
