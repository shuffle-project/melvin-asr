import multiprocessing
import os
import shutil
from typing import List, Optional

from core import paths
from models.job import Job, JobResult, JobStatus, JobType
from pydantic import TypeAdapter

from .logger import get_logger

logger = get_logger(__name__)

class JobHandler():
    _jobs_directory = paths.jobs_path
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobHandler, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._queues = {
                job_type: multiprocessing.Queue() for job_type in JobType
            }
            self._initialized = True

    def initialise(self):
        if not os.path.exists(self._jobs_directory):
            os.makedirs(self._jobs_directory)

        jobs = self.list_jobs()
        for job in jobs:
            if job.status == JobStatus.PENDING:
                logger.info(f"resume job from last time: {job.id}")
                self._queues[job.job_type].put(job.id)
            elif job.status == JobStatus.IN_PROGRESS:
                logger.info(f"restart job from last time: {job.id}")
                job.status = JobStatus.PENDING
                self.update_job(job)
                self._queues[job.job_type].put(job.id)

    def get_next_queue_job(self, allowed_types: List[JobType], timeout: float = 1.0) -> Optional[Job]:
        try:
            for job_type in allowed_types:
                if not self._queues[job_type].empty():
                    job_id = self._queues[job_type].get(timeout=timeout)
                    return self.get_job(job_id)
            return None
        except multiprocessing.queues.Empty:
            return None

    def list_jobs(self) -> List[Job]:
        jobs = []
        for job_id in os.listdir(self._jobs_directory):
            status_path = os.path.join(self._jobs_directory, job_id, "status.json")
            if os.path.exists(status_path):
                try:
                    job = self.get_job(job_id)
                    jobs.append(job)
                except Exception as e:
                    logger.error(f"Error loading job status file {e}")
        return jobs
    
    def get_job(self, job_id: str) -> Job:
        file_path = os.path.join(self._jobs_directory, f"{job_id}", f"status.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Job {job_id} not found.")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                adapter = TypeAdapter(Job)
                job = adapter.validate_json(f.read())
            return job
        except Exception as e:
            raise RuntimeError(f"Failed to load job {job_id}: {e}")
        
    def create_job(self, job: Job) -> Job:
        job_path = os.path.join(self._jobs_directory, f"{job.id}")
        if os.path.exists(job_path):
            raise FileExistsError(f"Job {job.id} already exists.")
        
        os.makedirs(job_path)
        
        file_path = os.path.join(job_path, f"status.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(job.model_dump_json())
            logger.info(f"Added new {job.job_type} job to queue")
            self._queues[job.job_type].put(job.id)
            return job
        except Exception as e:
            raise RuntimeError(f"Failed to create job {job.id}: {e}")
        
    def delete_job(self, job_id: str) -> None:
        job_path = os.path.join(self._jobs_directory, f"{job_id}")
        if not os.path.exists(job_path):
            raise FileNotFoundError(f"Job {job_id} not found.")
        
        try:
            shutil.rmtree(job_path)
        except Exception as e:
            raise RuntimeError(f"Failed to delete job {job_id}: {e}")
        
    def update_job(self, job: Job) -> None:
        file_path = os.path.join(self._jobs_directory, f"{job.id}", f"status.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Job {job.id} not found.")
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(job.model_dump_json())
        except Exception as e:
            raise RuntimeError(f"Failed to update job {job.id}: {e}")
    
    def save_job_result(self, job: Job, result: JobResult):
        file_path = os.path.join(self._jobs_directory, f"{job.id}", f"result.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result.model_dump_json())
        except Exception as e:
            raise RuntimeError(f"Failed to write job result {job.id}: {e}")
        
    def get_job_result(self, job_id: str) -> JobResult:
        file_path = os.path.join(self._jobs_directory, f"{job_id}", f"result.json")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Job result {job_id} not found.")

        with open(file_path, "r", encoding="utf-8") as f:
            result = JobResult.model_validate_json(f.read())
        return result
