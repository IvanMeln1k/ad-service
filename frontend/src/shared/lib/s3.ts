const S3_PUBLIC_URL = 'http://localhost:9000/ad-photos';

export function getPhotoUrl(s3Key: string): string {
  return `${S3_PUBLIC_URL}/${s3Key}`;
}
