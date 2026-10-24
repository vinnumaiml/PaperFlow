import pytest
import io
import time
from fastapi.testclient import TestClient
import pymupdf

from app.main import app

client = TestClient(app)

def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "built_in_engines" in data
    assert data["built_in_engines"]["pypdf"] is True
    assert data["built_in_engines"]["pymupdf"] is True

def test_api_create_job_merge_and_download():
    # Create 2 simple PDFs in memory
    doc1 = pymupdf.open()
    doc1.new_page().insert_text((50, 50), "Doc 1 Page 1")
    pdf1_bytes = doc1.tobytes()
    doc1.close()
    
    doc2 = pymupdf.open()
    doc2.new_page().insert_text((50, 50), "Doc 2 Page 1")
    pdf2_bytes = doc2.tobytes()
    doc2.close()
    
    files = [
        ("files", ("file1.pdf", io.BytesIO(pdf1_bytes), "application/pdf")),
        ("files", ("file2.pdf", io.BytesIO(pdf2_bytes), "application/pdf")),
    ]
    data = {"tool": "merge-pdf"}
    
    # 1. Create job
    res = client.post("/api/jobs", data=data, files=files)
    assert res.status_code == 201
    job_data = res.json()
    job_id = job_data["id"]
    assert job_id is not None
    
    # Wait for completion (fast for small in-memory files)
    max_wait = 10
    start = time.time()
    completed = False
    
    while time.time() - start < max_wait:
        poll_res = client.get(f"/api/jobs/{job_id}")
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        if poll_data["status"] == "completed":
            completed = True
            assert len(poll_data["outputs"]) >= 1
            break
        elif poll_data["status"] == "failed":
            pytest.fail(f"Job failed: {poll_data.get('error')}")
        time.sleep(0.3)
        
    assert completed is True
    
    # 2. Download result
    dl_res = client.get(f"/api/jobs/{job_id}/download")
    assert dl_res.status_code == 200
    assert len(dl_res.content) > 0
    # Verify downloaded PDF has 2 pages
    res_doc = pymupdf.open("pdf", dl_res.content)
    assert len(res_doc) == 2
    res_doc.close()
