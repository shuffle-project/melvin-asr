import asyncio
import multiprocessing
import signal
import sys
from typing import List

import uvicorn
from app import app as app_fastapi
from core import cleanup
from core.config import BatchWorkerConfig, config
from core.job_handler import JobHandler
from core.logger import LOGGING_CONFIG, get_logger
from worker.batch_worker import BatchWorker

logger = get_logger(__name__)

# Global list to track all worker processes and their status
worker_processes: List[multiprocessing.Process] = []
worker_status_queue = multiprocessing.Queue()

def start_batch_worker(config: BatchWorkerConfig, status_queue: multiprocessing.Queue, job_handler: JobHandler):
    logger.info(f"Starting batch worker")
    worker = BatchWorker(config, job_handler)

    try:
        worker.initialize()
        status_queue.put((True, None))
        worker.run()
    except Exception as e:
        logger.exception(f"Error initializing worker: {e}")
        status_queue.put((False, str(e)))
        sys.exit(1)


def terminate_processes():
    global worker_processes
    
    logger.info(f"Terminating {len(worker_processes)} processes")
    for process in worker_processes:
        if process and process.is_alive():
            logger.info(f"Terminating process {process.pid}")
            process.terminate()
    
    # Give processes time to terminate gracefully
    for process in worker_processes:
        if process:
            process.join(timeout=3)
        
    # Force kill any remaining processes
    for process in worker_processes:
        if process and process.is_alive():
            logger.info(f"Force killing process {process.pid}")
            process.kill()
    
    logger.info("All worker processes terminated")

def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, shutting down...")
    terminate_processes()
    sys.exit(0)

def start_workers_sequentially(job_handler: JobHandler):
    global worker_processes, worker_status_queue

    for i, batch_worker_config in enumerate(config.batch_workers):
        logger.info(f"Starting worker {i} with device {batch_worker_config.device}")

        worker_process = multiprocessing.Process(
            target=start_batch_worker, 
            args=(batch_worker_config, worker_status_queue, job_handler),
            name=f"worker-{i}"
        )
        worker_process.start()
        worker_processes.append(worker_process)
        logger.info(f"Started worker process {i} with PID {worker_process.pid}")

        logger.info(f"Waiting for worker to initialize...")
        try:
            success, error = worker_status_queue.get(timeout=600)
            if not success:
                logger.error(f"Worker failed to initialize: {error}")
                terminate_processes()
                return False
        except worker_status_queue.empty():
            logger.error(f"Workerinitialization timed out")
            # Terminate all started processes
            terminate_processes()
            return False
        
    logger.info("All workers initialized successfully")
    return True

class Server(uvicorn.Server):
    def handle_exit(self, sig: int, frame) -> None:
        return super().handle_exit(sig, frame)
    
async def main():
    logger.info("Starting main application")

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:   
        # Start worker processes
        job_handler = JobHandler()
        start_workers_sequentially(job_handler)
        
        # Run the FastAPI server in the main thread
        logger.info(f"Starting FastAPI server on {config.host}:{config.port}")

        server = Server(config=uvicorn.Config(app_fastapi, workers=1, host=config.host, port=config.port, loop="asyncio", log_config=LOGGING_CONFIG))
        fastapi = asyncio.create_task(server.serve())
        scheduler = asyncio.create_task(cleanup.periodic_cleanup(job_handler))

        await asyncio.wait([fastapi, scheduler])
    except KeyboardInterrupt:
        logger.info("Caught KeyboardInterrupt, shutting down...")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
    finally:
        # Ensure all processes are terminated
        logger.info("Cleaning up in finally block")
        terminate_processes()

if __name__ == "__main__":
    # TODO: handle shutdown correctly
    asyncio.run(main())
