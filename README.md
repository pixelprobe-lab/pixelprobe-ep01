# EP01：這張照片被 P 過嗎？用 Python 做 4 種照片鑑識

[English below](#english)

**照妖鏡實驗室 PixelProbe** YouTube 影片〈這張照片被 P 過嗎？〉的完整程式碼。影片中只展示關鍵幾行，這裡是可直接執行的完整版本。

## 內容
程式會先**自行生成**一張示範風景照，再做出竄改版本（貼上 UFO、抹掉一棵樹），接著用 4 種方法分析：

| 方法 | 函式 | 輸出 |
|---|---|---|
| ELA 錯誤等級分析 | `ela()` | `03_ela_original.png`、`04_ela_fake.png` |
| 雜訊分析 | `noise_map()` | `05_noise_fake.png` |
| 複製貼上偵測（ORB + 位移向量投票） | `copy_move()` | `06_copymove.png` |
| EXIF 檔案資訊 | 主程式（PIL `getexif()`） | 終端機輸出 |

所有圖片皆由程式生成，不含任何真實照片。

## 執行
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python forensics_demo.py
```
結果存在 `output/`。

## 重要限制
- ELA 只適用於 JPEG，邊緣與高對比區本來就會偏亮。
- 複製貼上偵測的參數（距離門檻、投票數 50）是針對示範圖調整的，用在真實照片可能誤判或漏判。
- EXIF 容易被清除或偽造，社群平台上傳時通常會移除。
- **沒有任何單一工具能證明照片造假**，請以多種證據交叉比對並追查原始來源。

## 授權
MIT License，見 `LICENSE`。

---

<a id="english"></a>
# EP01: Was this photo edited? 4 photo-forensics techniques in Python

Full source code for the **PixelProbe** (照妖鏡實驗室) YouTube episode. The video shows only the key lines; this is the complete, runnable version.

## What it does
The script **generates its own synthetic** landscape photo, creates a tampered copy (pastes a UFO, removes a tree), then analyzes it with:

| Technique | Function | Output |
|---|---|---|
| Error Level Analysis (ELA) | `ela()` | `03_ela_original.png`, `04_ela_fake.png` |
| Noise residual map | `noise_map()` | `05_noise_fake.png` |
| Copy-move detection (ORB + displacement voting) | `copy_move()` | `06_copymove.png` |
| EXIF metadata | main script (PIL `getexif()`) | console |

No real photos are used.

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python forensics_demo.py
```
Results are written to `output/`.

## Limitations
- ELA works on JPEG only; edges and high-contrast areas are naturally bright.
- Copy-move thresholds (distance, 50-vote minimum) are tuned for the demo image and may misfire on real photos.
- EXIF is easily stripped or forged; most social platforms strip it on upload.
- **No single tool proves an image is fake.** Combine evidence and trace the original source.

## License
MIT, see `LICENSE`.
