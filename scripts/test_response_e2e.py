import asyncio
from sqlalchemy.future import select
import sys

from autosoc_api.db.session import AsyncSessionLocal
from autosoc_api.db.models.incident import Incident
from autosoc_api.db.models.response import ResponseRecommendation, ResponseApproval, ResponseExecution
from autosoc_response.policy.engine import policy_engine
from autosoc_response.policy.types import ExecutionMode
from autosoc_response.executors.registry import get_executor

async def run_e2e():
    async with AsyncSessionLocal() as db:
        # Get an incident
        result = await db.execute(select(Incident))
        incident = result.scalars().first()
        
        if not incident:
            print('No incident found.')
            return

        print(f'Using Incident: {incident.id}')

        # Create recommendation
        rec = ResponseRecommendation(
            incident_id=incident.id,
            source='analyst',
            playbook_id='pb_002_block_ip',
            action_type='block_ip',
            target_type='ip',
            target_reference='198.51.100.24',
            rationale='Suspected C2 activity',
            impact='high',
            reversibility='reversible',
            created_by='soc_analyst',
            status='proposed'
        )
        db.add(rec)
        await db.commit()
        await db.refresh(rec)
        print(f'Created Recommendation: {rec.id}')

        # Request Approval
        rec.status = 'pending_review'
        approval = ResponseApproval(
            recommendation_id=rec.id,
            incident_id=incident.id,
            requested_by='soc_analyst'
        )
        db.add(approval)
        await db.commit()
        await db.refresh(approval)
        print(f'Requested Approval: {approval.id}')

        # Approve
        approval.decision = 'approved'
        approval.reviewer = 'soc_manager'
        rec.status = 'approved'
        await db.commit()
        print('Approved Recommendation.')

        # Execute via Policy Engine & Executor directly (Simulating Worker)
        is_allowed, reason = policy_engine.evaluate(
            action_type=rec.action_type,
            target=rec.target_reference,
            impact=rec.impact,
            mode=ExecutionMode.ANALYST_APPROVED_EXECUTION,
            approval_status='approved'
        )
        print(f'Policy Engine Evaluation: {is_allowed} ({reason})')

        if is_allowed:
            executor = get_executor('mock_firewall', rec.target_reference)
            result = executor.run(ExecutionMode.ANALYST_APPROVED_EXECUTION)
            print(f'Execution Result: {result}')
            
            exec_record = ResponseExecution(
                recommendation_id=rec.id,
                approval_id=approval.id,
                playbook_id=rec.playbook_id,
                action_type=rec.action_type,
                mode=ExecutionMode.ANALYST_APPROVED_EXECUTION,
                target=rec.target_reference,
                executor='mock_firewall',
                idempotency_key=f'{rec.id}_exec_1',
                status='succeeded',
                result=result
            )
            db.add(exec_record)
            await db.commit()
            print('Recorded execution in DB.')

if __name__ == '__main__':
    asyncio.run(run_e2e())
