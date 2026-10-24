import logging
import io
import asyncio
from datetime import datetime
from minio import Minio
from minio.error import S3Error
from autosoc_schemas.events.raw import RawSecurityEvent
from typing import Optional

logger = logging.getLogger("ingestion.archive.minio")

class MinioArchiveService:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket_name: str = "autosoc-raw-events", secure: bool = False):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        self.bucket_name = bucket_name
        self._bucket_ensured = False

    def _ensure_bucket(self):
        if not self._bucket_ensured:
            try:
                if not self.client.bucket_exists(self.bucket_name):
                    self.client.make_bucket(self.bucket_name)
                self._bucket_ensured = True
            except Exception as e:
                logger.error(f"Failed to ensure MinIO bucket {self.bucket_name}: {e}")
                raise

    def _archive_sync(self, event: RawSecurityEvent) -> str:
        self._ensure_bucket()
        
        # Suggested key pattern: raw-events/YYYY/MM/DD/source-type/source-id/event-id.json
        dt = event.received_at
        key = f"raw-events/{dt.year}/{dt.month:02d}/{dt.day:02d}/{event.source_type}/{event.source_id}/{event.event_id}.json"
        
        payload_bytes = event.model_dump_json().encode('utf-8')
        data = io.BytesIO(payload_bytes)
        
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=key,
                data=data,
                length=len(payload_bytes),
                content_type="application/json",
                metadata={"payload_hash": event.payload_hash}
            )
            return key
        except S3Error as e:
            logger.error(f"S3 Error archiving event {event.event_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error archiving event {event.event_id}: {e}")
            raise

    async def archive_event(self, event: RawSecurityEvent) -> str:
        """
        Asynchronously archives the raw event to MinIO.
        Returns the object key on success.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._archive_sync, event)
