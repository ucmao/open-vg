# Object Storage Configuration (Cloudflare R2 / AWS S3 / OSS)

VidGen stores generated AI images, video clips, and user avatars on S3-compatible Object Storage via an abstract storage service layer (`backend/app/services/storage.py`).

---

## ☁️ Cloudflare R2 Configuration (`backend/.env`)

Cloudflare R2 offers zero egress bandwidth fees, ideal for AI video and image hosting:

```bash
STORAGE_PROVIDER=r2
S3_BUCKET_NAME=vidgen-media
S3_ACCESS_KEY_ID=your_cloudflare_r2_access_key
S3_SECRET_ACCESS_KEY=your_cloudflare_r2_secret_key
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
STORAGE_CDN_URL=https://cdn.yourdomain.com
```

---

## ☁️ AWS S3 Configuration (`backend/.env`)

```bash
STORAGE_PROVIDER=s3
S3_BUCKET_NAME=vidgen-media-us-east-1
S3_ACCESS_KEY_ID=AKIA...
S3_SECRET_ACCESS_KEY=...
CDN_BASE_URL=https://vidgen-media-us-east-1.s3.amazonaws.com
```
