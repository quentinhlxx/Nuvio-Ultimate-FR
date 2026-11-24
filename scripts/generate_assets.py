#!/usr/bin/env python3
"""Create cinematic category covers, animated GIFs, and Nuvio JSON."""
import json, math, random, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
OWNER = "quentinhlxx"
REPO = "Nuvio-Ultimate-FR"
BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/assets"
W,H=960,540
CATS=[
 ("films-recents","Films récents",("FILMS","RÉCENTS"),(37,124,238),"FILM","2026"),
 ("series-recentes","Séries récentes",("SÉRIES","RÉCENTES"),(141,87,244),"SÉRIE","NEW"),
 ("tendances","Populaires",("POPULAIRES",),(239,83,125),"TOP","TREND"),
 ("incontournables","Les mieux notés",("LES MIEUX","NOTÉS"),(236,177,71),"TOP","9.8"),
 ("france","Films et séries français",("FILMS ET SÉRIES","FRANÇAIS"),(54,125,224),"FR","CINÉ"),
 ("marvel-chronologie","Marvel — Ordre chronologique",("MARVEL","CHRONOLOGIE"),(222,62,71),"MCU","∞"),
]
def font(size,bold=True):
    names=["/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for name in names:
        try:return ImageFont.truetype(name,size)
        except OSError:pass
    return ImageFont.load_default()
def rect_soft(draw, xy, fill, radius=18, outline=None, width=1):
    draw.rounded_rectangle(tuple(map(int,xy)),radius,fill,outline,width)
def make(cat,phase=0):
    slug,title,lines,accent,label,small=cat
    img=Image.new("RGB",(W,H))
    pix=img.load()
    for y in range(H):
        for x in range(W):
            light=max(0,(x/W-.20))*.21+max(0,(y/H-.38))*.055
            wave=math.sin((x/W)*6.3+phase*.35)*.025
            a=tuple(int(v*(.07+light+wave)) for v in accent)
            pix[x,y]=(max(5,9+a[0]),max(7,12+a[1]),max(12,22+a[2]))
    glow=Image.new("RGBA",(W,H),(0,0,0,0));g=ImageDraw.Draw(glow)
    shift=round(12*math.sin(phase/12*math.tau))
    g.ellipse((560+shift,60,1100+shift,540),fill=(*accent,88))
    glow=glow.filter(ImageFilter.GaussianBlur(125))
    img=Image.alpha_composite(img.convert("RGBA"),glow)
    d=ImageDraw.Draw(img)
    d.rounded_rectangle((26,25,W-26,H-25),radius=25,outline=(*accent,75),width=2)
    d.line((70,90,70,440),fill=(*accent,225),width=7)
    d.text((101,93),"NUVIO  /  ULTIMATE FR",font=font(20),fill=(176,196,220,255))
    y=187 if len(lines)==2 else 233
    for word in lines:
        fs=64 if len(word)<12 else (49 if len(word)<16 else 41)
        d.text((96,y),word,font=font(fs),fill=(255,255,255,255),stroke_width=1,stroke_fill=(24,27,36,180))
        y+=74
    d.rounded_rectangle((101,398,300,439),radius=18,fill=(*accent,210))
    d.text((122,406),"DÉCOUVRIR",font=font(21),fill=(255,255,255,255))
    # Three independent, stylized poster cards (not borrowed copyrighted posters).
    colors=[(39,47,76),(31,30,52),(39,37,64)]
    for i,(px,py,ang) in enumerate(((560,142,-12),(660,96,7),(740,128,17))):
        poster=Image.new("RGBA",(172,266),(0,0,0,0));p=ImageDraw.Draw(poster)
        p.rounded_rectangle((4,5,168,260),radius=14,fill=(*colors[i],255),outline=(*accent,185),width=3)
        for j in range(4):
            xx=26+j*35
            p.line((xx,23,xx,238),fill=(*accent,25+j*12),width=2)
        cy=119+int(math.sin(phase*.5+i)*8)
        p.ellipse((43,cy-35,140,cy+62),outline=(*accent,210),width=9)
        p.polygon([(83,cy-29),(124,cy+12),(83,cy+54)],fill=(*accent,245))
        p.text((20,25),label,font=font(23),fill=(255,255,255,255))
        p.text((22,219),small,font=font(22),fill=(240,244,255,255))
        rotated=poster.rotate(ang,resample=Image.Resampling.BICUBIC,expand=True)
        img.alpha_composite(rotated,(px,py))
    # a fine cinemascope light leak at the edge
    d=ImageDraw.Draw(img)
    d.line((70,466,890,466),fill=(*accent,85),width=2)
    return img.convert("RGB")
def save_assets():
    for cat in CATS:
        slug=cat[0]
        frames=[make(cat,i).resize((640,360),Image.Resampling.LANCZOS) for i in range(12)]
        full=make(cat)
        full.save(ASSETS/f"{slug}.jpg",quality=88,optimize=True)
        full.save(ASSETS/f"{slug}-fond.jpg",quality=83,optimize=True)
        frames[0].save(ASSETS/f"{slug}.gif",save_all=True,append_images=frames[1:],duration=105,loop=0,optimize=True)
        print(slug,"JPG+GIF generated")
def source(provider,title,typ,sort,filters=None):
    return {"provider":"tmdb","tmdbSourceType":"DISCOVER","title":title,"mediaType":typ,"sortBy":sort,"filters":filters or {}}
def folder(slug,title,sources):
    return {"id":slug,"title":title,"tileShape":"LANDSCAPE","hideTitle":False,
            "focusGifEnabled":True,"focusGlowEnabled":True,
            "coverImageUrl":f"{BASE}/{slug}.jpg",
            "focusGifUrl":f"{BASE}/{slug}.gif",
            "heroBackdropUrl":f"{BASE}/{slug}-fond.jpg",
            "sources":sources}
def build_collection():
    recent={"voteCountGte":10,"primaryReleaseDateLte":"2026-11-24"}
    recent_tv={"voteCountGte":10,"firstAirDateLte":"2026-11-24"}
    folders=[
        folder("films-recents","Films récents",[source("tmdb","Derniers films","MOVIE","primary_release_date.desc",recent)]),
        folder("series-recentes","Séries récentes",[source("tmdb","Dernières séries","TV","first_air_date.desc",recent_tv)]),
        folder("tendances","Populaires",[source("tmdb","Films","MOVIE","popularity.desc"),source("tmdb","Séries","TV","popularity.desc")]),
        folder("incontournables","Les mieux notés",[source("tmdb","Films","MOVIE","vote_average.desc",{"voteCountGte":1000}),source("tmdb","Séries","TV","vote_average.desc",{"voteCountGte":500})]),
        folder("france","Films et séries français",[source("tmdb","Films","MOVIE","popularity.desc",{"withOriginalLanguage":"fr"}),source("tmdb","Séries","TV","popularity.desc",{"withOriginalLanguage":"fr"})]),
        folder("marvel-chronologie","Marvel — Ordre chronologique",[{"provider":"addon","addonId":"aio-metadata","type":"Movie","catalogId":"mdblist.197831"}])
    ]
    custom={"id":"ultimate-fr","title":"Nuvio Ultimate FR","hideTitle":False,
            "pinToTop":True,"focusGlowEnabled":True,"viewMode":"TABBED_GRID",
            "showAllTab":True,"folders":folders}
    existing=[]
    urls=["https://nuvio-assets.xnzxflix.workers.dev/collections.json",
          "https://raw.githubusercontent.com/xnzx07/nuvio-assets/main/collections.json"]
    for url in urls:
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Nuvio-Ultimate-FR/1.0"})
            with urllib.request.urlopen(req,timeout=20) as response:
                value=json.load(response)
            if isinstance(value,list) and len(value)>=4:
                existing=[c for c in value if c.get("id") not in ("plateformes-streaming","ultimate-fr")]
                print("Loaded external collections from",url)
                break
        except Exception as exc:
            print("Reference not available",str(exc)[:160])
    output=[custom]+existing
    path=ROOT/"Nuvio-Ultimate-FR.json"
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Saved",path,"collection count",len(output))
if __name__=="__main__":
    save_assets()
    build_collection()
