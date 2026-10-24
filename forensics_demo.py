"""EP01 抓P圖：ELA、雜訊殘差、複製貼上偵測、EXIF 檢查（全部使用程式自製影像）"""
import cv2, numpy as np, os, io
from PIL import Image
D=os.path.dirname(os.path.abspath(__file__)); OUT=f"{D}/output"; os.makedirs(OUT,exist_ok=True)

def make_photo(w=1200,h=800,seed=7):
    """程式生成一張『風景照』：天空漸層、草地紋理、房子、樹，加感光雜訊。"""
    rng=np.random.default_rng(seed); img=np.zeros((h,w,3),np.float32)
    for y in range(h//2): img[y]=(235-y*0.3,190-y*0.2,120)            # 天空 BGR
    g=rng.normal(0,1,(h//2,w)); g=cv2.GaussianBlur(g,(0,0),3)*25
    img[h//2:]=np.dstack([60+g,140+g,70+g])                             # 草地
    cv2.rectangle(img,(300,280),(560,520),(90,110,170),-1)              # 房子
    pts=np.array([[280,280],[430,170],[580,280]]); cv2.fillPoly(img,[pts],(40,40,140))
    cv2.rectangle(img,(400,400),(460,520),(30,50,80),-1)
    for x in (800,950):
        cv2.rectangle(img,(x-12,380),(x+12,560),(30,60,90),-1); cv2.circle(img,(x,350),70,(40,120,40),-1)
    img+=rng.normal(0,4,img.shape)                                      # 感光雜訊
    return np.clip(img,0,255).astype(np.uint8)

def jpeg(img,q):
    ok,b=cv2.imencode(".jpg",img,[cv2.IMWRITE_JPEG_QUALITY,q]); return cv2.imdecode(b,1), b.tobytes()

def ela(img_bytes,q=90,scale=40):
    a=cv2.imdecode(np.frombuffer(img_bytes,np.uint8),1); r,_=jpeg(a,q)
    return np.clip(cv2.absdiff(a,r).astype(np.float32)*scale,0,255).astype(np.uint8)

def noise_map(img,k=16):
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32)
    res=g-cv2.medianBlur(g.astype(np.uint8),3).astype(np.float32)
    h,w=g.shape; m=np.zeros((h//k,w//k),np.float32)
    for i in range(h//k):
        for j in range(w//k): m[i,j]=res[i*k:(i+1)*k,j*k:(j+1)*k].std()
    m=cv2.normalize(m,None,0,255,cv2.NORM_MINMAX).astype(np.uint8)
    return cv2.applyColorMap(cv2.resize(m,(w,h),interpolation=cv2.INTER_NEAREST),cv2.COLORMAP_JET)

def copy_move(img):
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY); orb=cv2.ORB_create(20000,fastThreshold=5)
    kp,des=orb.detectAndCompute(g,None); bf=cv2.BFMatcher(cv2.NORM_HAMMING)
    out=img.copy(); pairs=[]
    for m in bf.knnMatch(des,des,k=3):
        for c in m[1:]:   # 跳過自己
            p,q=np.array(kp[c.queryIdx].pt),np.array(kp[c.trainIdx].pt)
            if c.distance<40 and np.linalg.norm(p-q)>60:
                if q[0]<p[0]: p,q=q,p
                pairs.append((p,q)); break
    # 複製貼上的特徵點會有「相同位移向量」：投票找最多的位移
    from collections import Counter
    votes=Counter(tuple((np.round((q-p)/8)).astype(int)) for p,q in pairs)
    n=0
    if votes:
        vec,cnt=votes.most_common(1)[0]
        if cnt>=50:
            for p,q in pairs:
                if tuple((np.round((q-p)/8)).astype(int))==vec:
                    cv2.line(out,tuple(map(int,p)),tuple(map(int,q)),(0,0,255),2)
                    cv2.circle(out,tuple(map(int,p)),5,(0,255,255),-1); cv2.circle(out,tuple(map(int,q)),5,(255,0,255),-1); n+=1
    return out,n

if __name__=="__main__":
    base=make_photo()
    # 原圖：相機式 JPEG q=92 + EXIF
    orig,_=jpeg(base,92)
    exif=Image.Exif(); exif[0x010F]="DemoCam"; exif[0x0110]="DemoCam X1"; exif[0x0132]="2026:10:20 09:15:00"
    buf=io.BytesIO(); Image.fromarray(cv2.cvtColor(orig,cv2.COLOR_BGR2RGB)).save(buf,"JPEG",quality=92,exif=exif)
    open(f"{OUT}/01_original.jpg","wb").write(buf.getvalue())
    # 竄改 1：用右邊的天空+草地蓋掉第二棵樹（copy-move 移除物件）；竄改 2：貼上低品質壓縮過的『UFO』
    fake=orig.copy(); fake[270:580,875:1030]=orig[270:580,1040:1195]
    ufo=np.full((90,200,3),(200,200,200),np.uint8); cv2.ellipse(ufo,(100,50),(95,30),0,0,360,(80,80,90),-1)
    cv2.ellipse(ufo,(100,35),(40,25),0,180,360,(160,200,220),-1); ufo,_=jpeg(cv2.GaussianBlur(ufo,(3,3),0),50)
    roi=fake[80:170,700:900]; mask=(np.abs(ufo.astype(int)-200).sum(2)>30)
    roi[mask]=ufo[mask]
    _,fb=jpeg(fake,92)
    im=Image.open(io.BytesIO(fb)); e=Image.Exif(); e[0x0131]="PhotoEditor 3.1"; e[0x0132]="2026:10:21 23:48:10"
    buf=io.BytesIO(); im.save(buf,"JPEG",quality=92,exif=e); open(f"{OUT}/02_fake.jpg","wb").write(buf.getvalue())
    fake_bytes=buf.getvalue(); fake_img=cv2.imdecode(np.frombuffer(fake_bytes,np.uint8),1)
    cv2.imwrite(f"{OUT}/03_ela_original.png",ela(open(f"{OUT}/01_original.jpg","rb").read()))
    cv2.imwrite(f"{OUT}/04_ela_fake.png",ela(fake_bytes))
    cv2.imwrite(f"{OUT}/05_noise_fake.png",noise_map(fake_img))
    cm,n=copy_move(fake_img); cv2.imwrite(f"{OUT}/06_copymove.png",cm)
    cm0,n0=copy_move(cv2.imread(f"{OUT}/01_original.jpg"))
    for name in ("01_original.jpg","02_fake.jpg"):
        ex=Image.open(f"{OUT}/{name}").getexif(); print(name,{Image.ExifTags.TAGS.get(k,k):v for k,v in ex.items()})
    print(f"copy-move matches: original={n0} fake={n}")
