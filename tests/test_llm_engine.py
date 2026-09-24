import pytest
from app.services.llm_engine import LLMEngine


@pytest.mark.asyncio
async def test_llm_engine_pr_analysis():
    engine = LLMEngine()
    diff = """
diff --git a/service.py b/service.py
+def connect():
+    return pymysql.connect(host="localhost", user="root", password="password123")
"""
    trivy_report = '{"Results": [{"Vulnerabilities": [{"VulnerabilityID": "CVE-2023-1234"}]}]}'

    result = await engine.analyze_pr(
        diff=diff,
        pr_title="feat: database connection",
        pr_description="Added MySQL connection",
        trivy_report=trivy_report,
    )

    assert result["status"] == "success"
    assert "markdown_review" in result
    assert len(result["markdown_review"]) > 50


@pytest.mark.asyncio
async def test_llm_engine_log_diagnostic():
    engine = LLMEngine()
    logs = """
Step 4/8 : RUN pip install -r requirements.txt
gcc: error: no such file or directory
error: command 'gcc' failed with exit status 1
The command '/bin/sh -c pip install -r requirements.txt' returned a non-zero code: 1
"""
    result = await engine.diagnose_pipeline_failure(
        logs=logs,
        workflow_name="Docker Build",
        failed_step="Build Image",
    )

    assert result["status"] == "success"
    assert "markdown_diagnosis" in result
    assert "Root Cause" in result["markdown_diagnosis"] or "Failure" in result["markdown_diagnosis"]
