
import time
from datetime import datetime
from typing import List
from uuid import uuid4

from core.config import BatchWorkerConfig
from core.job_handler import JobHandler
from core.logger import get_logger
from core.processing.alignment import alignment
from core.processing.seamlessm4t import SeamlessM4T
from core.processing.whisper import Whisper
from models.job import AlignmentMethod, Job, JobResult, JobStatus, JobType


class BatchWorker:
    id = uuid4()
    logger = get_logger(f"{__name__} ({id})")
    running = True

    def __init__(self, config: BatchWorkerConfig, job_handler: JobHandler):
        self.config = config
        self.job_handler = job_handler
        self.allowed_types: List[JobType] = []

        if self.config.transcription_enabled:
            self.allowed_types.append(JobType.TRANSCRIPTION)
            self.allowed_types.append(JobType.ALIGNMENT)
        if self.config.translation_enabled:
            self.allowed_types.append(JobType.TRANSLATION)

    def initialize(self):
        if self.config.transcription_enabled:
            self.whisper = Whisper(self.config)
            self.whisper.initialize()
        
        if self.config.translation_enabled:
            self.seamlessm4t = SeamlessM4T(self.config)
            self.seamlessm4t.initialize()
            
    def run(self):
        self.logger.info("started")

        time.sleep(5)

        while self.running:
            try:
                job = self.job_handler.get_next_queue_job(self.allowed_types)

                if job:
                    self.process_job(job)
            except KeyboardInterrupt:
                self.logger.info("HERE: Keyboard interrupt received, shutting down...")
                self.running = False
                break
            except Exception as e:
                self.logger.exception(f"Error in worker loop: {e}")
            
            time.sleep(10)

        self.logger.info("Worker shutting down")

    def process_job(self, job: Job):
        self.logger.info(f"Processing job {job.id}")
        try:
            # Update job status
            job.status = JobStatus.IN_PROGRESS
            job.created_at = datetime.now()
            self.job_handler.update_job(job)

            result: JobResult = None
            if job.job_type == JobType.TRANSCRIPTION:
                result = self.whisper.transcribe(job.settings)
            elif job.job_type == JobType.ALIGNMENT:
                if job.settings.method == AlignmentMethod.BY_AUDIO:
                    result = self.whisper.align_transcript_to_audio(job.settings)
                elif job.settings.method == AlignmentMethod.BY_TRANSCRIPT:
                    transcript = alignment.align_by_transcript(job.settings.transcript_with_timings, job.settings.transcript)
                    result = JobResult(transcript=transcript, raw_result={})
                elif job.settings.method == AlignmentMethod.BY_TIME:
                    transcript = alignment.align_by_time(job.settings.start, job.settings.end, job.settings.transcript.text)
                    result = JobResult(transcript=transcript, raw_result={})
                else:
                    raise ValueError(f"Invalid alignment method: {job.settings.method}")
            elif job.job_type == JobType.TRANSLATION:
                result = self.seamlessm4t.translate(job.settings)

            # Save results
            self.job_handler.save_job_result(job, result)

            # Update job status
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            self.job_handler.update_job(job)

        except Exception as e:
            self.logger.error(f"Error processing job {job.id}: {e}")
            try:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.now()
                self.job_handler.update_job(job)
            except Exception as e:
                self.logger.error(f"Error updating job status {job.id}: {e}")
                

