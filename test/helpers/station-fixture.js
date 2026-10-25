// All synchronous transport fixtures now use the actual supplied GLB.
import fs from 'node:fs';
import {URL} from 'node:url';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {buildTransport as build,transportEdgeSegments} from '../../src/world/transport.js';
const bytes=fs.readFileSync(new URL('../../public/prototypes/transport-station/transport-station.glb',import.meta.url));
export const source=(await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'')).scene;
export const buildTransport=(home,makeSign)=>build(home,makeSign,source);
export {transportEdgeSegments};
