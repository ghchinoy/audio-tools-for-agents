import logging
import os
import shutil
import time
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def is_cloud_uri(path_or_uri: str) -> bool:
    """Returns True if the path is a cloud storage URI (e.g. gs://)."""
    return path_or_uri.startswith("gs://") or path_or_uri.startswith("s3://")


def parse_gs_uri(gs_uri: str) -> tuple[str, str]:
    """Parses gs://bucket/path into (bucket_name, blob_name)."""
    parsed = urlparse(gs_uri)
    bucket_name = parsed.netloc
    blob_name = parsed.path.lstrip("/")
    return bucket_name, blob_name


def retry_with_backoff(
    fn,
    *args,
    max_attempts: int = 3,
    initial_delay_sec: float = 1.0,
    backoff_multiplier: float = 2.0,
    op_name: str = "operation",
    **kwargs,
):
    """Executes a callable with exponential backoff for transient I/O failures."""
    delay = initial_delay_sec
    last_exc: Optional[Exception] = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_exc = e
            if attempt == max_attempts:
                break
            logger.warning(
                "%s failed on attempt %d/%d (%s); retrying in %.1fs",
                op_name,
                attempt,
                max_attempts,
                e,
                delay,
            )
            time.sleep(delay)
            delay *= backoff_multiplier
    raise last_exc


def resolve_input_file(source_path_or_uri: str, local_dest_path: str) -> str:
    """Ensures the input file is available on the local filesystem.

    If source is already a local file, returns its path directly or copies it.
    If source is a GCS URI, downloads it to local_dest_path.
    """
    if not is_cloud_uri(source_path_or_uri):
        if not os.path.exists(source_path_or_uri):
            raise FileNotFoundError(f"Input file not found: {source_path_or_uri}")
        return os.path.abspath(source_path_or_uri)

    if source_path_or_uri.startswith("gs://"):
        from google.cloud import storage

        def _download():
            client = storage.Client()
            bucket_name, blob_name = parse_gs_uri(source_path_or_uri)
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.download_to_filename(local_dest_path)

        retry_with_backoff(_download, op_name=f"download({source_path_or_uri})")
        logger.info("Downloaded %s to %s", source_path_or_uri, local_dest_path)
        return local_dest_path

    raise ValueError(f"Unsupported storage scheme in URI: {source_path_or_uri}")


def export_output_file(local_path: str, destination_path_or_prefix: str) -> str:
    """Exports a generated local output file to its destination (local directory or cloud URI).

    Returns the final resolved path or URI.
    """
    if not is_cloud_uri(destination_path_or_prefix):
        os.makedirs(destination_path_or_prefix, exist_ok=True)
        dest_file = os.path.join(destination_path_or_prefix, os.path.basename(local_path))
        if os.path.abspath(local_path) != os.path.abspath(dest_file):
            shutil.copy2(local_path, dest_file)
        return os.path.abspath(dest_file)

    if destination_path_or_prefix.startswith("gs://"):
        from google.cloud import storage

        filename = os.path.basename(local_path)
        prefix = destination_path_or_prefix.rstrip("/")
        target_uri = f"{prefix}/{filename}"
        bucket_name, blob_name = parse_gs_uri(target_uri)

        def _upload():
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(local_path)

        retry_with_backoff(_upload, op_name=f"upload({target_uri})")
        logger.info("Uploaded %s to %s", local_path, target_uri)
        return target_uri

    raise ValueError(f"Unsupported storage scheme in destination: {destination_path_or_prefix}")
