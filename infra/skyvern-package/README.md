# ClauseBot / MiltmonNDT Use-Keep-Dump Package (OpenAI + Aurora + S3)

- Enforces minimal LLM snippets, strong redaction, vendor contract guard.
- Stores outputs/artifacts in S3 with KMS encryption.
- Uses Aurora Postgres with IAM auth (TLS).

## Quickstart

1) Copy files; create `.env` from `.env.example`.

2) Node
- `npm i express axios @aws-sdk/client-s3 jest nock`
- Run API: `node server.js`
- Test: `npx jest`

3) Python worker
- `pip install psycopg2-binary boto3`
- Optional: Download RDS CA bundle for stricter TLS:  
  `curl -o rds-combined-ca-bundle.pem https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem`
- Run: `python retention_worker.py`

4) DB
- Apply `schema.sql` to Aurora.

5) AWS
- Attach the IAM policy in this README to roles used by the API/worker.
- Prefer role-based auth (ECS/EKS/EC2/Lambda) over static keys.

## S3 Layout
- outputs: `s3://$OBJECT_STORE_BUCKET/$S3_PREFIX/outputs/YYYY/MM/DD/<run_hash>.json`
- artifacts: `.../artifacts/YYYY/MM/DD/<run_hash>/<kind>-N.png`

## OpenAI Enterprise
- Contract: no training, no retention.
- Set `LLM_DATA_USAGE=none`. Keep prompts transient.

## IAM Policy (least privilege)
Replace account, region, bucket, and KMS key as needed.
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3OutputsMinimal",
      "Effect": "Allow",
      "Action": ["s3:PutObject","s3:GetObject","s3:ListBucket","s3:DeleteObject"],
      "Resource": [
        "arn:aws:s3:::skyvern-outputs",
        "arn:aws:s3:::skyvern-outputs/*"
      ]
    },
    {
      "Sid": "KMSForBucket",
      "Effect": "Allow",
      "Action": ["kms:Encrypt","kms:Decrypt","kms:GenerateDataKey","kms:DescribeKey"],
      "Resource": ["arn:aws:kms:us-west-2:123456789012:key/abcd"]
    }
  ]
}
```

## Vendor swap notes
- Anthropic: swap `LLM_API_URL` + adjust request shape in `llmClient.js`.
- Self-hosted: set `LLM_API_URL=http://host/v1/chat/completions`; block egress if needed.
- GCS: replace `s3Storage.js` and S3 bits in worker with GCS libs.
