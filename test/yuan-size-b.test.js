import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { URL } from 'node:url';
const read=p=>JSON.parse(fs.readFileSync(new URL(p,import.meta.url)));
test('playable layout is exactly approved B without an additional coordinate or radius transform',()=>{
 assert.deepEqual(read('../src/data/yuan-plan.json'),read('../docs/design/yuan-size-comparison-v1/b/yuan-plan.json'));
 assert.deepEqual(read('../src/data/yuan-layout.json'),read('../docs/design/yuan-size-comparison-v1/b/yuan-layout.json'));
 assert.deepEqual(read('../src/data/yuan-surface.json'),read('../docs/design/yuan-size-comparison-v1/b/yuan-surface.json'));
 assert.equal(read('../src/data/yuan-layout.json').width,4.8);
});
