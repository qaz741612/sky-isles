# 重現與工具

遊戲沒有新增套件，仍為既有 Three.js／Vite。媒體與碰撞工具使用 Python 3.11.17、bpy 4.3.0、Shapely 2.2.0、Pillow 13.0.0、ffmpeg／ffprobe；它們不是瀏覽器 runtime 依賴。

## 地面與碰撞

```sh
npm ci
npm run generate:yuan -- --report-dir docs/previews/parent-child-glb-integration-v1
python scripts/build-parent-child-collision.py
node scripts/audit-parent-child-integration.mjs
npm run check
```

Python 需要在已安裝上述 bpy／Shapely 的隔離環境執行；沒有寫回 Blender 原檔。此容器的 bpy interpreter 在清理時會異常，因此實際生成採以下 wrapper：`run_path` 完整成功後才結束程序；若生成中有錯誤仍會拋出失敗。

```python
import runpy, sys, os
runpy.run_path('scripts/build-parent-child-collision.py', run_name='__main__')
sys.stdout.flush()
os._exit(0)
```

來源 SHA 有強制保護。更換核准來源前不要隨意更新 SHA 來繞過檢查。

## 正式建置與瀏覽器

```sh
npm run build
npx vite preview --host 0.0.0.0 --port 4187 --strictPort
PLAYWRIGHT_BASE_URL=http://127.0.0.1:4187 BROWSER_QA_SCALE=1 npx playwright test test/parent-child.e2e.js test/walkways.e2e.js test/station-headroom.e2e.js test/panorama.e2e.js test/responsive.e2e.js --retries=0
```

完整實際測試分批結果與早期超時見 TEST-REPORT.md。`BROWSER_QA_SCALE=1` 是明示的功能測試 profile；純 DOM／工程物理檢查停下重複光柵化，不代表完整 DPR 下 FPS。

## 真正遊戲截圖、效能與錄影

```sh
node scripts/capture-parent-child-integration.mjs http://127.0.0.1:4187
node scripts/benchmark-parent-child-integration.mjs
node scripts/record-parent-child-integration.mjs
ffmpeg -y -f concat -safe 0 -i work/parent-child-integration/recording/frames.txt -fps_mode vfr -c:v libx264 -preset fast -crf 20 -bf 0 -pix_fmt yuv420p -movflags +faststart docs/previews/parent-child-glb-integration-v1/native-operation.mp4
python scripts/parent-child-media-manifest.py
```

效能腳本另需將 `ac433fd5d23f00d3aab9470d96349114e1a37b24` 的原程式／public 檔案在獨立暫存目錄 build，於 4186 跑 Vite preview；不重設目前工作目錄。測量期間停止其他瀏覽器與測試。

錄影每 15 個 compositor frame 擷取一張原始 JPEG；`frames.txt` 由 CDP 原始時間戳形成，沒有時間加速。容器平均幀率不是遊戲的 rAF FPS。影片無音軌。要錄音或驗收手機手感，需後續真人實機。

## GitHub 原檔核對

```sh
python scripts/verify-parent-child-github.py <包含最終媒體的完整40字commit>
```

這會由 GitHub raw 下載每張最終 PNG、MP4 及公開 GLB，核對 bytes 與 SHA256；沒有使用聊天附件。驗證報告另以文件提交保存，不必重建相同 runtime Preview。
