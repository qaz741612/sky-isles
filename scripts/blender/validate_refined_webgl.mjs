// Ephemeral browser harness only; does not modify or serve the game. MIT.
import fs from 'node:fs';
import path from 'node:path';
import {build} from 'esbuild';
import {chromium} from '@playwright/test';
const out='docs/design/parent-child-blender-refinement-v2';
const entry=`import * as THREE from 'three';import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
window.inspectModel=async(base64)=>{
 const raw=atob(base64),bytes=Uint8Array.from(raw,c=>c.charCodeAt(0));const gltf=await new GLTFLoader().parseAsync(bytes.buffer,'');
 const scene=new THREE.Scene();scene.background=new THREE.Color('#e3e4e0');scene.add(gltf.scene);scene.add(new THREE.HemisphereLight('#f2f7ff','#a79b83',2));
 const key=new THREE.DirectionalLight('#fff1dc',3.2);key.position.set(-8,15,10);scene.add(key);const fill=new THREE.DirectionalLight('#e2f1ff',1.2);fill.position.set(9,8,-4);scene.add(fill);
 const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(1120,768);renderer.setPixelRatio(1);renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.1;document.body.appendChild(renderer.domElement);
 const camera=new THREE.OrthographicCamera(-12.9,12.9,12.9*768/1120,-12.9*768/1120,.05,150);camera.position.set(17.25,19.47,27.4);camera.lookAt(-.75,1.25,-.1);
 renderer.render(scene,camera);await new Promise(r=>requestAnimationFrame(r));renderer.render(scene,camera);
 let missing=0,meshes=0,triangles=0;const roles={};gltf.scene.updateMatrixWorld(true);
 gltf.scene.traverse(o=>{if(!o.isMesh)return;meshes++;if(!o.material)missing++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;});
 for(const role of gltf.scene.children[0]?.children??[]){const b=new THREE.Box3().setFromObject(role);if(!b.isEmpty())roles[role.name]={min:b.min.toArray(),max:b.max.toArray(),sizeXYZ:b.getSize(new THREE.Vector3()).toArray()};}
 const context=renderer.getContext();const error=context.getError();const debug=context.getExtension('WEBGL_debug_renderer_info');const driver=debug?context.getParameter(debug.UNMASKED_RENDERER_WEBGL):null;
 return{loaded:true,missingMaterials:missing,meshes,modelTriangles:triangles,renderCalls:renderer.info.render.calls,renderedTrianglesIncludingTransmissionPasses:renderer.info.render.triangles,geometries:renderer.info.memory.geometries,textures:renderer.info.memory.textures,webglError:error,roles,renderer:context.getParameter(context.RENDERER),unmaskedRenderer:driver,note:'Standalone GLB validation under software Chromium; not game integration or real-device performance certification.'};
};`;
const bundled=await build({stdin:{contents:entry,resolveDir:process.cwd(),sourcefile:'standalone-glb-validation.js'},bundle:true,write:false,format:'iife',minify:true});
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1120,height:768}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.setContent('<!doctype html><meta charset=utf-8><style>body{margin:0;overflow:hidden}</style>');await page.addScriptTag({content:bundled.outputFiles[0].text});
 const data=await page.evaluate(b=>window.inspectModel(b),fs.readFileSync(path.join(out,'parent-child-centre.glb')).toString('base64'));
 if(errors.length||data.missingMaterials||data.webglError)throw Error(JSON.stringify({errors,data}));
 await page.screenshot({path:path.join(out,'three-webgl-validation.png')});fs.writeFileSync(path.join(out,'three-webgl-validation.json'),JSON.stringify({...data,pageErrors:errors},null,2)+'\n');console.log(JSON.stringify(data));
}finally{await browser.close();}
