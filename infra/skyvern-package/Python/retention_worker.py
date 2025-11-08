import os
import datetime
import psycopg2
import boto3
from privacy_utils import ttl_days

AWS_REGION = os.getenv('AWS_REGION', 'us-west-2')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT', '5432'))
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
RDS_IAM = os.getenv('RDS_IAM', 'true').lower() == 'true'

AUDIT_TTL = ttl_days('AUDIT_LOG_TTL_DAYS', 30)
OUTPUT_TTL = ttl_days('OUTPUT_RETENTION_DAYS', 90)
SCREENSHOT_TTL = ttl_days('SCREENSHOT_RETENTION_DAYS', 7)

S3_BUCKET = os.getenv('OBJECT_STORE_BUCKET')
S3_PREFIX = os.getenv('S3_PREFIX', '')

session = boto3.session.Session(region_name=AWS_REGION)
s3 = session.client('s3')
rds = session.client('rds')

def _db_connect():
    if RDS_IAM:
        token = rds.generate_db_auth_token(
            DBHostname=DB_HOST, Port=DB_PORT, DBUsername=DB_USER, Region=AWS_REGION
        )
        # Note: for stricter TLS validation, include sslrootcert='rds-combined-ca-bundle.pem'
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=token,
            sslmode='require'
        )
        return conn
    else:
        # Fallback to classic URL if needed (not recommended for prod)
        raise RuntimeError('Non-IAM DB auth not configured. Set RDS_IAM=false and provide DB_URL.')

def purge_s3_outputs(cutoff_days: int):
    if not S3_BUCKET:
        return
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=cutoff_days)
    paginator = s3.get_paginator('list_objects_v2')
    prefix = S3_PREFIX.rstrip('/') + '/' if S3_PREFIX else ''
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
        for obj in page.get('Contents', []):
            key = obj['Key']
            if '/outputs/' in key or '/artifacts/' in key:
                last_mod = obj['LastModified'].replace(tzinfo=None)
                if last_mod < cutoff:
                    s3.delete_object(Bucket=S3_BUCKET, Key=key)

def run():
    conn = _db_connect()
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM runs
        WHERE status IN ('success','fail')
          AND now() - end_ts > make_interval(days => %s)
          AND retain_until IS NULL
    """, (AUDIT_TTL,))
    cur.execute("""
        DELETE FROM outputs
        WHERE now() - created_at > make_interval(days => %s)
    """, (OUTPUT_TTL,))
    cur.execute("""
        DELETE FROM artifacts
        WHERE kind IN ('screenshot','dom_snapshot')
          AND now() - created_at > make_interval(days => %s)
    """, (SCREENSHOT_TTL,))

    purge_s3_outputs(OUTPUT_TTL)

    cur.close()
    conn.close()

if __name__ == '__main__':
    run()
