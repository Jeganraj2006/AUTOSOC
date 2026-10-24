import asyncio
from autosoc_api.db.session import AsyncSessionLocal
from autosoc_api.services.incident import IncidentService

async def test():
    async with AsyncSessionLocal() as db:
        service = IncidentService(db)
        incidents = await service.get_all()

        print("SERVICE RETURNED:", len(incidents))

        for inc in incidents[:3]:
            print(inc.title, inc.severity, inc.status)

asyncio.run(test())
