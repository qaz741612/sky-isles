// Node geometry fixture only: omit image bindings because Node has no ImageBitmap.
// Browser integration tests load the byte-identical GLB with all real materials.
import fs from 'node:fs';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {buildTransport as build,transportEdgeSegments} from '../../src/world/transport.js';
const bytes=fs.readFileSync(new URL('../../public/prototypes/transport-elevated-station-v9/transport-station-v9-game-candidate.glb',import.meta.url));
const jsonLength=bytes.readUInt32LE(12),json=JSON.parse(bytes.subarray(20,20+jsonLength).toString());
for(const m of json.materials){for(const k of Object.keys(m))if(k.endsWith('Texture'))delete m[k];if(m.pbrMetallicRoughness){delete m.pbrMetallicRoughness.baseColorTexture;delete m.pbrMetallicRoughness.metallicRoughnessTexture;}}
const text=Buffer.from(JSON.stringify(json)),padded=Buffer.alloc(Math.ceil(text.length/4)*4,32);text.copy(padded);
const bin=bytes.subarray(20+jsonLength),header=Buffer.alloc(20);header.writeUInt32LE(0x46546c67,0);header.writeUInt32LE(2,4);header.writeUInt32LE(20+padded.length+bin.length,8);header.writeUInt32LE(padded.length,12);header.writeUInt32LE(0x4e4f534a,16);
const input=Buffer.concat([header,padded,bin]);
export const source=(await new GLTFLoader().parseAsync(input.buffer.slice(input.byteOffset,input.byteOffset+input.byteLength),'')).scene;
export const buildTransport=(home,makeSign)=>build(home,makeSign,source.clone(true));
export {transportEdgeSegments};
