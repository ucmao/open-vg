""""""
import asyncio
from celery import Task

from ..celery_app import celery_app
from ..models.base import SessionLocal
from ..models.work import Work, WorkStatus
from ..models.workflow import Workflow
from ..models.generation_model import GenerationModel
from ..services.workflow_executor import WorkflowExecutor
from ..services.realtime import publish_user_event
from ..utils.logger import logger


class WorkflowCallbackTask(Task):
    """，"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """"""
        work_id = kwargs.get('work_id')
        logger.error(
            f"Task {task_id} failed for work {work_id}: {exc}\n"
            f"Traceback: {einfo}"
        )
        
        if work_id:
            db = SessionLocal()
            try:
                work = db.query(Work).filter(Work.id == work_id).first()
                if work and work.status == WorkStatus.GENERATING:
                    from ..services.work_failed_service import mark_work_failed, notify_generation_failed
                    mark_work_failed(db, work, f"Task failed: {type(exc).__name__}: {exc}")
                    db.commit()
                    notify_generation_failed(db, work.user_id)
                    publish_user_event(work.user_id, {
                        "type": "generation_complete",
                        "work_id": work_id,
                        "status": "failed",
                        "error_message": work.error_message,
                    })
                    
            except Exception as e:
                logger.error(f"Error in on_failure callback: {e}")
            finally:
                db.close()


@celery_app.task(
    base=WorkflowCallbackTask,
    bind=True,                   #  self（task ）
    name="execute_workflow",     #
    max_retries=3,               #  3
    default_retry_delay=60,      #  60
    autoretry_for=(Exception,),  #
    retry_backoff=True,          #
    retry_backoff_max=600,       #  10
    retry_jitter=True,           # （）
)
def execute_workflow_task(self, work_id: int, user_id: int):
    """
    
     Celery Worker
     API
    
    Args:
        self: Celery Task （bind=True ）
        work_id: Work  ID
        user_id:  ID（）
    
    Returns:
        dict:  {"status": "success", "work_id": xxx}
    """
    logger.info(f"[Celery] Starting workflow task for work {work_id}")
    
    from ..services.mock_generation_service import is_mock_generation_enabled, process_mock_generation
    if is_mock_generation_enabled():
        db = SessionLocal()
        try:
            return process_mock_generation(db, work_id)
        finally:
            db.close()

    db = SessionLocal()
    try:
        # 1.  Work
        work = db.query(Work).filter(Work.id == work_id).first()
        if not work:
            raise ValueError(f"Work {work_id} not found")
        
        # 2.  GenerationModel  Workflow
        generation_model = db.query(GenerationModel).filter(
            GenerationModel.model_key == work.model_key
        ).first()
        
        if not generation_model:
            raise ValueError(f"GenerationModel not found for model_key: {work.model_key}")
        
        if not generation_model.workflow_id:
            raise ValueError(f"Model {work.model_key} has no workflow configured")
        
        workflow = db.query(Workflow).filter(
            Workflow.id == generation_model.workflow_id
        ).first()
        
        if not workflow:
            raise ValueError(f"Workflow {generation_model.workflow_id} not found")
        
        # 3.  GENERATING
        if work.status != WorkStatus.GENERATING:
            logger.warning(f"Work {work_id} status is {work.status}, expected GENERATING")
            return {"status": "skipped", "reason": f"Work status is {work.status}"}
        
        # 4.
        user_input = {
            "prompt": work.prompt,
            "negative_prompt": work.negative_prompt,
            **(work.params.get("_user_input") if work.params and "_user_input" in work.params else work.params or {})
        }
        
        # 5.
        logger.info(f"[Celery] Executing workflow {workflow.id} for work {work_id}")
        
        import os
        BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
        webhook_url = f"{BACKEND_URL}/api/webhook/replicate/{work_id}"
        
        executor = WorkflowExecutor(db_session=db)
        
        #  asyncio
        result = asyncio.run(executor.execute(
            workflow=workflow,
            user_input=user_input,
            work_id=work_id,
            webhook_url=webhook_url
        ))
        
        logger.info(f"[Celery] Workflow execution initiated for work {work_id}: {result}")
        
        #  ID ，
        prediction_id = result.get("prediction_id")
        node_id = result.get("node_id")
        
        if prediction_id:
            work.replicate_id = prediction_id
            if node_id:
                if not work.params:
                    work.params = {}
                work.params["_workflow_nodes"] = work.params.get("_workflow_nodes") or {}
                work.params["_workflow_nodes"][node_id] = {
                    "prediction_id": prediction_id,
                    "status": "processing"
                }
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(work, "params")
            db.commit()
            logger.info(f"[Celery] Updated DB with prediction_id: {prediction_id} for work {work_id}")
        
        return {
            "status": "submitted",
            "work_id": work_id,
            "prediction_id": prediction_id
        }
        
    except Exception as e:
        logger.error(f"[Celery] Task failed for work {work_id}: {str(e)}")
        
        # （）
        retry_count = self.request.retries
        if retry_count < self.max_retries:
            # ：60s, 120s, 240s
            countdown = 60 * (2 ** retry_count)
            logger.info(f"[Celery] Retrying task for work {work_id} in {countdown}s (attempt {retry_count + 1}/{self.max_retries})")
            raise self.retry(exc=e, countdown=countdown)
        else:
            # ，
            # on_failure （、）
            logger.error(f"[Celery] Task failed permanently for work {work_id} after {self.max_retries} retries")
            raise
            
    finally:
        db.close()
