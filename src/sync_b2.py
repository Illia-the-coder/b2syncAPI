import argparse
import sys
from datetime import datetime, timedelta
from utils import parse_size, parse_age, get_b2_files, upload_file_to_b2
import os
import logging

# Configure logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description='Enhanced B2 Sync Tool with Bidirectional Sync, Age and Size Filtering.')
    parser.add_argument('source_dir', help='Local source directory to sync from.')
    parser.add_argument('b2_bucket', help='B2 bucket URL to sync to.')
    parser.add_argument('--max-age', type=str, help='Maximum age of files to sync (e.g., 1d, 1y).')
    parser.add_argument('--min-size', type=str, help='Minimum size of files to sync (e.g., 1MB).')
    parser.add_argument('--threads', type=int, default=10, help='Number of concurrent threads.')

    args = parser.parse_args()

    max_age_delta = parse_age(args.max_age) if args.max_age else None
    min_size_bytes = parse_size(args.min_size) if args.min_size else 0

    try:
        files_to_sync = get_b2_files(args.source_dir, args.b2_bucket, max_age_delta, min_size_bytes)
        logging.info(f"Found {len(files_to_sync)} files to sync.")
        upload_file_to_b2(files_to_sync, args.b2_bucket, args.threads)
        logging.info("Synchronization complete.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
