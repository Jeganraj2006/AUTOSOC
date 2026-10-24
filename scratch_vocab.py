import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from autosoc_api.core.config import settings
from autosoc_api.db.models.attack import AttackTechnique

async def generate_vocab():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    vocab = {"<PAD>": 0, "<UNK>": 1}
    idx = 2
    async with async_session() as session:
        result = await session.execute(select(AttackTechnique))
        techniques = result.scalars().all()
        for t in techniques:
            if t.external_id not in vocab:
                vocab[t.external_id] = idx
                idx += 1
                
    import json
    with open("d:/PROJECT WORKKKKKKKKKK/ml/autosoc_ml/progression/features/vocab.json", "w") as f:
        json.dump(vocab, f, indent=2)
    print(f"Generated vocabulary with {len(vocab)} items.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(generate_vocab())
