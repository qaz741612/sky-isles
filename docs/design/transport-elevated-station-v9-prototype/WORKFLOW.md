# 本輪只讀模型的重現流程

本輪禁止重新建模。固定使用ca94f48的BLEND、展示GLB與候選GLB；asset-lock.json列出精確SHA與Git blob ID。不得執行open_platform_elevated_station_v9.py、build_elevated_station_v9.py、finish_elevated_station_v9.py或optimize_elevated_station_v9_candidate.py來覆蓋本輪模型。這些程式僅保留為歷史可恢復來源。

工具：Blender/bpy4.3、Python3.11、Shapely、NumPy、Pillow，既有Three.js／Playwright／Khronos工具環境；未修改runtime依賴。文字輪廓採Noto Sans CJK（SIL OFL），原檔已有mesh與packed原創木紋；沿用專案MIT及既有授權。

```sh
python scripts/blender/render_elevated_station_v9.py
python scripts/blender/render_open_platform_before.py
python scripts/blender/audit_elevated_station_v9_source.py
python scripts/blender/audit_elevated_station_v9.py
python scripts/blender/audit_open_platform_v9.py
node scripts/blender/check_open_platform_camera_profile.mjs
node scripts/blender/validate_elevated_station_v9.mjs
```

Python使用已安裝bpy的工具虛擬環境，如work/parent-child-blender/render-env/bin/python。渲染不儲存修改原檔，逐圖來源與PNG SHA都吻合才續用；11張最終圖使用同一BLEND，原始樣本及解析度見render-record.json。

拆棚前來源固定為81f7408的BLEND，SHA a975409e16bf406b4fe1ae9981d632c527f85244387e3a88111baad4177f2abb。before/有明確舊來源標記。前後桌機／手機／45°／頂視相機位置、方向、鏡頭、正交尺度與像素尺寸都由報告工具assert；補充zoom28不代替手機預設。

等Cycles完成後再測量，避免與軟體GPU爭CPU：

```sh
npx vite --host 127.0.0.1 --port 4192 --strictPort
node scripts/blender/check_elevated_station_v9_webgl.mjs
npm run check
python scripts/blender/report_open_platform_v9.py
python scripts/blender/write_open_platform_acceptance.py
python scripts/blender/finalize_open_platform_delivery.py
```

WebGL只載入單一資產的本機viewer，不是正式遊戲；DPR1的1280×800及390×844，不宣稱真機GPU效能。Blender手機720×1280對應360×640 CSS／DPR2的原手機profile，並非720 CSS寬。

最後verify_elevated_station_v9_github.py以精確提交SHA下載manifest及每個檔案，比對byte數與SHA256。manifest本身直接與本地檔案逐byte比較；下載收據及DELIVERY另列，避免自我雜湊循環。全程保留ca94f48三個模型SHA不變，不合併或部署。
