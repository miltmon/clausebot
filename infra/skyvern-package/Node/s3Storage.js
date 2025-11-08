const { S3Client, PutObjectCommand, DeleteObjectCommand } = require('@aws-sdk/client-s3');
const path = require('path');

const s3 = new S3Client({
  region: process.env.AWS_REGION || 'us-west-2',
  credentials: process.env.AWS_ACCESS_KEY_ID
    ? { accessKeyId: process.env.AWS_ACCESS_KEY_ID, secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY }
    : undefined
});

const BUCKET = process.env.OBJECT_STORE_BUCKET;

async function uploadJSON(keyPath, jsonObj) {
  const key = path.posix.join(process.env.S3_PREFIX || '', keyPath);
  const cmd = new PutObjectCommand({
    Bucket: BUCKET,
    Key: key,
    Body: JSON.stringify(jsonObj),
    ContentType: 'application/json',
    ServerSideEncryption: 'aws:kms',
    SSEKMSKeyId: process.env.AWS_KMS_KEY_ARN || undefined
  });
  await s3.send(cmd);
  return `s3://${BUCKET}/${key}`;
}

async function deleteObject(keyPath) {
  const key = path.posix.join(process.env.S3_PREFIX || '', keyPath);
  const cmd = new DeleteObjectCommand({ Bucket: BUCKET, Key: key });
  await s3.send(cmd);
}

module.exports = { uploadJSON, deleteObject };
