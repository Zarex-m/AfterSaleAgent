from app.services.document_service import list_documents, get_document_by_id,create_document_record
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.document import DocumentResponse
from app.api.dependencies import get_current_user
from pathlib import Path
from uuid import uuid4
ALLOWED_EXTENSIONS = {".txt", ".md"}

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/",response_model=DocumentResponse)
async def upload_document(
    title:str,
    file:UploadFile=File(...),
    db:AsyncSession=Depends(get_db),
    current_user=Depends(get_current_user)
):
    original_name = file.filename or "document"
    suffix = Path(original_name).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .txt and .md files are allowed.")

    storage_dir = Path("storage/documents")
    storage_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid4().hex}{suffix}"
    file_path = storage_dir / safe_name

    content = await file.read()
    file_path.write_bytes(content)
    
    document = await create_document_record(
    db=db,
    title=title or original_name,
    file_path=str(file_path),
    uploaded_by=current_user.id,
)
    return DocumentResponse.model_validate(document)

@router.get("/",response_model=list[DocumentResponse])
async def list_documents_api(
    db:AsyncSession=Depends(get_db),
    current_user=Depends(get_current_user)
):
    documents=await list_documents(db)
    return [DocumentResponse.model_validate(doc) for doc in documents]

@router.get("/{document_id}",response_model=DocumentResponse)
async def get_document_detail(
    document_id:int,
    db:AsyncSession=Depends(get_db),
    current_user=Depends(get_current_user)
):
    document=await get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.model_validate(document)