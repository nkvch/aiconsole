import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aiconsole.core.assets.materials.material import Material, MaterialContentType
from aiconsole.core.assets.types import AssetLocation, AssetStatus
from aiconsole.core.database.models import Base
from aiconsole.core.database.storage import DatabaseStorageAdapter
from aiconsole.core.project.project import close_project, reinitialize_project

TEST_DATABASE_URL = "sqlite:///test.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
async def setup_test_environment():
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["AICONSOLE_PROJECT_DIR"] = temp_dir

        await reinitialize_project()

        yield temp_dir

        await close_project()


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def storage_adapter(setup_test_environment):
    adapter = DatabaseStorageAdapter()
    return adapter


@pytest.fixture
def sample_material():
    return Material(
        id="test_material",
        name="Test Material",
        version="0.0.1",
        usage="Test usage",
        defined_in=AssetLocation.PROJECT_DIR,
        content_type=MaterialContentType.STATIC_TEXT,
        content="Test content",
        default_status=AssetStatus.ENABLED,
        usage_examples=["Example 1", "Example 2"],
        override=False,
    )


@pytest.mark.asyncio
async def test_create_material(storage_adapter, sample_material):
    await storage_adapter.save_obj(sample_material)

    fetched_material = await storage_adapter.fetch_object("material", sample_material.id)
    assert fetched_material.id == sample_material.id
    assert fetched_material.name == sample_material.name
    assert fetched_material.content == sample_material.content
    assert fetched_material.usage_examples == sample_material.usage_examples


@pytest.mark.asyncio
async def test_fetch_materials(storage_adapter, sample_material):
    material1 = sample_material
    material2 = Material(
        id="test_material_2",
        name="Test Material 2",
        version="0.0.1",
        usage="Test usage 2",
        defined_in=AssetLocation.PROJECT_DIR,
        content_type=MaterialContentType.STATIC_TEXT,
        content="Test content 2",
        default_status=AssetStatus.ENABLED,
        usage_examples=["Example 3"],
        override=False,
    )

    await storage_adapter.save_obj(material1)
    await storage_adapter.save_obj(material2)

    materials = await storage_adapter.fetch_objects("material")
    assert len(materials) == 2
    material_ids = {m.id for m in materials}
    assert material_ids == {material1.id, material2.id}


@pytest.mark.asyncio
async def test_update_material(storage_adapter, sample_material):
    await storage_adapter.save_obj(sample_material)

    updated_material = Material(
        id=sample_material.id,
        name="Updated Material",
        version="0.0.2",
        usage="Updated usage",
        defined_in=AssetLocation.PROJECT_DIR,
        content_type=MaterialContentType.STATIC_TEXT,
        content="Updated content",
        default_status=AssetStatus.DISABLED,
        usage_examples=["Updated Example"],
        override=False,
    )

    await storage_adapter.save_obj(updated_material)

    # verify material was updated
    fetched_material = await storage_adapter.fetch_object("material", sample_material.id)
    assert fetched_material.name == "Updated Material"
    assert fetched_material.version == "0.0.2"
    assert fetched_material.content == "Updated content"
    assert fetched_material.usage_examples == ["Updated Example"]
    assert fetched_material.default_status == AssetStatus.DISABLED


@pytest.mark.asyncio
async def test_delete_material(storage_adapter, sample_material):
    await storage_adapter.save_obj(sample_material)

    # delete
    await storage_adapter.delete_obj(sample_material)

    with pytest.raises(KeyError):
        await storage_adapter.fetch_object("material", sample_material.id)


@pytest.mark.asyncio
async def test_material_not_found(storage_adapter):
    # try to fetch non-existent material
    with pytest.raises(KeyError):
        await storage_adapter.fetch_object("material", "non_existent")


@pytest.mark.asyncio
async def test_invalid_material_type(storage_adapter):
    # try to fetch with invalid type
    with pytest.raises(ValueError, match="Unsupported object type"):
        await storage_adapter.fetch_objects("invalid_type")


@pytest.mark.asyncio
async def test_material_data_integrity(storage_adapter, sample_material):
    await storage_adapter.save_obj(sample_material)

    fetched_material = await storage_adapter.fetch_object("material", sample_material.id)

    assert fetched_material.model_dump() == sample_material.model_dump()


@pytest.mark.asyncio
async def test_material_with_empty_usage_examples(storage_adapter):
    material = Material(
        id="empty_examples",
        name="Empty Examples Material",
        version="0.0.1",
        usage="Test usage",
        defined_in=AssetLocation.PROJECT_DIR,
        content_type=MaterialContentType.STATIC_TEXT,
        content="Test content",
        default_status=AssetStatus.ENABLED,
        usage_examples=[],
        override=False,
    )

    await storage_adapter.save_obj(material)

    fetched_material = await storage_adapter.fetch_object("material", material.id)
    assert fetched_material.usage_examples == []


@pytest.mark.asyncio
async def test_material_with_null_usage_examples(storage_adapter):
    material = Material(
        id="null_examples",
        name="Null Examples Material",
        version="0.0.1",
        usage="Test usage",
        defined_in=AssetLocation.PROJECT_DIR,
        content_type=MaterialContentType.STATIC_TEXT,
        content="Test content",
        default_status=AssetStatus.ENABLED,
        usage_examples=[],
        override=False,
    )

    await storage_adapter.save_obj(material)

    # verify material was saved correctly
    fetched_material = await storage_adapter.fetch_object("material", material.id)
    assert fetched_material.usage_examples == []
