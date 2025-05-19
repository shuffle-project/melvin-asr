import asyncio
from datetime import datetime, timedelta

from core.job_handler import JobHandler
from core.logger import get_logger
from core.upload_handler import upload_handler

logger = get_logger(__name__)
async def periodic_cleanup(job_handler: JobHandler):
    # Initial delay before starting cleanup
    await asyncio.sleep(30)
      
    while True:
        try:
            logger.info("Running periodic cleanup...")

            max_age = datetime.now() - timedelta(days=7)

            jobs = job_handler.list_jobs()
            upload_files = upload_handler.list_files()
            upload_files_to_keep = set()
            upload_files_to_remove = set()

            jobs_to_remove: list[str] = []
            for job in jobs:
                if job.completed_at and job.completed_at < max_age:
                    jobs_to_remove.append(job.id)
                elif "audio_filename" in job.settings:
                    upload_files_to_keep.add(job.settings.audio_filename)

            for filename in upload_files:
                if filename in upload_files_to_keep:
                    continue
                created_at = upload_handler.get_file_created_at(filename)
                if created_at < max_age:
                    upload_files_to_remove.add(filename)
                    
            for job in jobs_to_remove:
                logger.info(f"Deleting job: {job}")
                job_handler.delete_job(job)

            for filename in upload_files_to_remove:
                logger.info(f"Deleting upload file: {filename}")
                upload_handler.remove_file(filename)
        except asyncio.CancelledError:
            logger.info("Periodic cleanup cancelled.")
        except Exception as e:
            logger.error(f"Error during periodic cleanup: {e}")

        # Run every 24 hours
        await asyncio.sleep(86400)