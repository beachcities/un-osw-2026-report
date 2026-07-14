#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配布用自己完結HTMLビルド。正本(master)は外部参照のまま＝base64禁止は正本ルール。
これはスクリプトが吐く配布物であり、手で編集しないこと。"""
import re, io, base64, os
from PIL import Image, ImageOps

PREMIUM = {"IMG_2863.jpeg","IMG_8761.jpeg","IMG_2942.jpeg","IMG_2945.jpeg","IMG_2859.jpeg"}
STD_W, STD_Q = 1200, 78      # 配布プロファイル（画面閲覧用）
PRM_W, PRM_Q = 1800, 85

def data_uri(name):
    path = f"images/{name}"
    if name.endswith(".png"):                      # スクリーンショットはPNG維持
        im = Image.open(path)
        if im.width > 1000:
            im = im.resize((1000, round(im.height*1000/im.width)), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    w, q = (PRM_W, PRM_Q) if name in PREMIUM else (STD_W, STD_Q)
    im = ImageOps.exif_transpose(Image.open(path))
    if im.mode != "RGB": im = im.convert("RGB")
    if im.width > w:
        im = im.resize((w, round(im.height*w/im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

h = open("public_v1.html", encoding="utf-8").read()
refs = sorted(set(re.findall(r'src="images/([^"]+)"', h)) | set(re.findall(r"url\('images/([^']+)'\)", h)))
uris = {n: data_uri(n) for n in refs}
for n, u in uris.items():
    h = h.replace(f'src="images/{n}"', f'src="{u}"')
    h = h.replace(f"url('images/{n}')", f"url('{u}')")
assert "images/" not in h, "未置換の参照が残存"
out = "UN_OSW_2026_Report_public_dist.html"
open(out, "w", encoding="utf-8").write(h)
print(f"{len(refs)}枚焼き込み → {out}: {os.path.getsize(out)/1e6:.1f} MB")
