import os
import logging
from datetime import datetime, timedelta
from b2sdk.v1 import B2Api, InMemoryAccountInfo, UploadSourceLocalFile
from concurrent.futures import ThreadPoolExecutor

def parse_size(size_str):
    size_str = size_str.upper()
    units = {"KB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12}
    for unit in units:
        if size_str.endswith(unit):
            return int(float(size_str[:-len(unit)]) * units[unit])
    return int(size_str)  # Assume bytes if no unit

def parse_age(age_str):
    amount = int(age_str[:-1])
    unit = age_str[-1].lower()
    if unit == 'd':
        return timedelta(days=amount)
    elif unit == 'y':
        return timedelta(days=365 * amount)
    elif unit == 'h':
        return timedelta(hours=amount)
    elif unit == 'm':
        return timedelta(minutes=amount)
    else:
        raise ValueError("Invalid age unit. Use 'd' for days, 'y' for years, etc.")

def get_b2_files(source_dir, b2_bucket, max_age_delta, min_size_bytes):
    files_to_sync = []
    current_time = datetime.now()
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                stat = os.stat(file_path)
                file_age = current_time - datetime.fromtimestamp(stat.st_mtime)
                if (max_age_delta is None or file_age <= max_age_delta) and stat.st_size >= min_size_bytes:
                    files_to_sync.append(file_path)
            except Exception as e:
                logging.error(f"Error accessing {file_path}: {e}")
    return files_to_sync

def upload_file_to_b2(files, b2_bucket, threads):
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    
    # Initialize B2 API with environment variables
    try:
        b2_api.authorize_account("production", os.environ["B2_KEY_ID"], os.environ["B2_APP_KEY"])
        logging.info("Successfully authorized B2 account.")
    except Exception as e:
        logging.error(f"Failed to authorize B2 account: {e}")
        raise

    bucket_name = b2_bucket.split("://")[1]
    try:
        bucket = b2_api.get_bucket_by_name(bucket_name)
    except Exception as e:
        logging.error(f"Failed to get bucket '{bucket_name}': {e}")
        raise

    def upload(file_path):
        try:
            relative_path = os.path.relpath(file_path, start=os.path.commonpath([file_path, '/']))
            upload_source = UploadSourceLocalFile(file_path)
            bucket.upload(
                upload_source=upload_source,
                file_name=relative_path
            )
            logging.info(f"Uploaded {file_path}")
        except Exception as e:
            logging.error(f"Failed to upload {file_path}: {e}")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(upload, files)