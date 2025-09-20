#!/usr/bin/env python3
"""
Document Processing Service
===========================

Compliance-specific document processing that wraps TidyLLM's VectorQA capabilities.
This is a domain service that adds compliance-specific rules and workflows.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
import pandas as pd
from pathlib import Path
import sys

# Add tidyllm to path for VectorQA capabilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'packages' / 'tidyllm'))

try:
    # Try to import TidyLLM's document processing
    from services.unified_rag_manager import UnifiedRAGManager
    TIDYLLM_AVAILABLE = True
except ImportError:
    TIDYLLM_AVAILABLE = False

@dataclass
class DocumentResult:
    """Result from document processing."""
    file_name: str
    file_type: str
    processing_status: str
    basic_stats: Dict[str, Any]
    compliance_metadata: Optional[Dict[str, Any]] = None
    vectorqa_chunks: Optional[List[Dict[str, Any]]] = None

class DocumentProcessor:
    """Compliance-specific document processor using TidyLLM VectorQA."""

    def __init__(self, use_vectorqa: bool = False):
        """Initialize with optional VectorQA integration."""
        self.use_vectorqa = use_vectorqa and TIDYLLM_AVAILABLE

        if self.use_vectorqa:
            try:
                # Initialize TidyLLM's UnifiedRAGManager for VectorQA
                self.rag_manager = UnifiedRAGManager(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                print("VectorQA initialized successfully")
            except Exception as e:
                print(f"VectorQA initialization failed: {e}")
                self.use_vectorqa = False
                self.rag_manager = None
        else:
            self.rag_manager = None

    def process_files(self, file_path: str) -> DocumentResult:
        """Process a file with compliance-specific rules and optional VectorQA."""
        path = Path(file_path)
        file_type = path.suffix.lower()

        # First, do basic processing
        if file_type == '.json':
            result = self._process_json(path)
        elif file_type in ['.xlsx', '.xls']:
            result = self._process_excel(path)
        elif file_type == '.pdf':
            result = self._process_pdf(path)
        else:
            result = DocumentResult(
                file_name=path.name,
                file_type='unsupported',
                processing_status='SKIPPED',
                basic_stats={'error': f'Unsupported file type: {file_type}'}
            )

        # Add VectorQA processing if available and successful
        if self.use_vectorqa and result.processing_status == 'SUCCESS':
            result = self._add_vectorqa_processing(path, result)

        return result

    def _add_vectorqa_processing(self, path: Path, result: DocumentResult) -> DocumentResult:
        """Enhance result with VectorQA processing."""
        try:
            # Use TidyLLM's RAG manager to process document
            chunks = self.rag_manager.process_document(str(path))

            # Add VectorQA metadata
            result.vectorqa_chunks = [
                {
                    'chunk_id': i,
                    'text': chunk.get('text', '')[:200] + '...',  # Preview
                    'metadata': chunk.get('metadata', {})
                }
                for i, chunk in enumerate(chunks[:3])  # First 3 chunks as preview
            ]

            result.basic_stats['vectorqa_chunks_total'] = len(chunks)
            result.basic_stats['vectorqa_enabled'] = True

        except Exception as e:
            result.basic_stats['vectorqa_error'] = str(e)
            result.basic_stats['vectorqa_enabled'] = False

        return result

    def _process_json(self, path: Path) -> DocumentResult:
        """Process JSON compliance documents."""
        try:
            if path.exists():
                with open(path, 'r') as f:
                    data = json.load(f)

                stats = {
                    'top_level_keys': len(data.keys()),
                    'content_size_chars': len(json.dumps(data)),
                    'nested_levels': self._get_json_depth(data),
                    'sample_keys': list(data.keys())[:5]
                }

                # Add compliance metadata
                compliance_meta = {
                    'document_type': data.get('type', 'unknown'),
                    'compliance_status': data.get('status', 'pending'),
                    'requires_mvr_check': 'mvr' in str(data).lower(),
                    'requires_vst_check': 'vst' in str(data).lower()
                }

                return DocumentResult(
                    file_name=path.name,
                    file_type='json',
                    processing_status='SUCCESS',
                    basic_stats=stats,
                    compliance_metadata=compliance_meta
                )
            else:
                return DocumentResult(
                    file_name=path.name,
                    file_type='json',
                    processing_status='ERROR',
                    basic_stats={'error': 'File not found'}
                )
        except Exception as e:
            return DocumentResult(
                file_name=path.name,
                file_type='json',
                processing_status='ERROR',
                basic_stats={'error': str(e)}
            )

    def _process_excel(self, path: Path) -> DocumentResult:
        """Process Excel compliance checklists."""
        try:
            if path.exists():
                df = pd.read_excel(path, sheet_name=None)
                first_sheet = list(df.values())[0] if df else None

                stats = {
                    'sheet_count': len(df),
                    'first_sheet_rows': len(first_sheet) if first_sheet is not None else 0,
                    'first_sheet_columns': len(first_sheet.columns) if first_sheet is not None else 0,
                    'column_names': list(first_sheet.columns) if first_sheet is not None else []
                }

                # Check for compliance checklist indicators
                compliance_meta = None
                if first_sheet is not None:
                    columns_lower = [str(c).lower() for c in first_sheet.columns]
                    compliance_meta = {
                        'is_checklist': any('check' in c for c in columns_lower),
                        'has_status': any('status' in c for c in columns_lower),
                        'has_priority': any('priority' in c for c in columns_lower)
                    }

                return DocumentResult(
                    file_name=path.name,
                    file_type='excel',
                    processing_status='SUCCESS',
                    basic_stats=stats,
                    compliance_metadata=compliance_meta
                )
            else:
                return DocumentResult(
                    file_name=path.name,
                    file_type='excel',
                    processing_status='ERROR',
                    basic_stats={'error': 'File not found'}
                )
        except Exception as e:
            return DocumentResult(
                file_name=path.name,
                file_type='excel',
                processing_status='ERROR',
                basic_stats={'error': str(e)}
            )

    def _process_pdf(self, path: Path) -> DocumentResult:
        """Process PDF compliance documents."""
        if self.use_vectorqa and path.exists():
            # Try to use TidyLLM's PDF processing
            try:
                chunks = self.rag_manager.process_document(str(path))
                return DocumentResult(
                    file_name=path.name,
                    file_type='pdf',
                    processing_status='SUCCESS',
                    basic_stats={
                        'chunks_extracted': len(chunks),
                        'vectorqa_processed': True
                    },
                    vectorqa_chunks=[
                        {'chunk_id': i, 'preview': chunk.get('text', '')[:100] + '...'}
                        for i, chunk in enumerate(chunks[:3])
                    ]
                )
            except Exception as e:
                return DocumentResult(
                    file_name=path.name,
                    file_type='pdf',
                    processing_status='LIMITED',
                    basic_stats={'note': f'PDF processing error: {e}'}
                )
        else:
            return DocumentResult(
                file_name=path.name,
                file_type='pdf',
                processing_status='LIMITED',
                basic_stats={'note': 'PDF processing requires TidyLLM VectorQA integration'}
            )

    def _get_json_depth(self, obj, depth=0):
        """Get maximum depth of JSON structure."""
        if not isinstance(obj, dict):
            return depth
        if not obj:
            return depth
        return max(self._get_json_depth(v, depth + 1) for v in obj.values())