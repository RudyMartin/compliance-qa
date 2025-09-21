#!/usr/bin/env python3
"""
AI Chat Feature Testing with Real Interactions
==============================================

Comprehensive testing of AI chat features across different workflow types
with real usage metrics, timestamps, and cost tracking.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import uuid

class ChatSessionMetrics:
    """Track metrics for a chat session."""

    def __init__(self, user_id: str, workflow_type: str):
        self.session_id = str(uuid.uuid4())[:8]
        self.user_id = user_id
        self.workflow_type = workflow_type
        self.start_time = datetime.now()
        self.interactions = []
        self.total_tokens_used = 0
        self.total_cost_estimate = 0.0

    def add_interaction(self, question: str, response: str, tokens_used: int = 0, cost: float = 0.0):
        """Add an interaction to the session."""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "response": response,
            "tokens_used": tokens_used,
            "cost_estimate": cost,
            "response_time_ms": 0  # Will be calculated
        }
        self.interactions.append(interaction)
        self.total_tokens_used += tokens_used
        self.total_cost_estimate += cost

    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "workflow_type": self.workflow_type,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_interactions": len(self.interactions),
            "total_tokens_used": self.total_tokens_used,
            "total_cost_estimate": self.total_cost_estimate,
            "average_response_time": sum(i.get("response_time_ms", 0) for i in self.interactions) / max(len(self.interactions), 1),
            "interactions": self.interactions
        }

class WorkflowChatTester:
    """Test AI chat functionality across different workflow types."""

    def __init__(self):
        self.test_sessions = []
        self.test_workflows = self._load_test_workflows()

    def _load_test_workflows(self) -> Dict[str, Dict]:
        """Load the created workflows for testing."""
        workflows = {}

        workflow_paths = [
            ("model_validation", "tidyllm/workflows/definitions/workflows/model_validation/model_validation_flow.json"),
            ("model_monitoring", "tidyllm/workflows/definitions/workflows/model_monitoring/model_monitoring_flow.json"),
            ("regulatory_compliance", "tidyllm/workflows/definitions/workflows/regulatory_compliance/regulatory_compliance_flow.json"),
            ("model_documentation", "tidyllm/workflows/definitions/workflows/model_documentation/model_documentation_flow.json"),
            ("stress_testing", "tidyllm/workflows/definitions/workflows/stress_testing/stress_testing_flow.json")
        ]

        for workflow_type, path in workflow_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    workflows[workflow_type] = json.load(f)
            except Exception as e:
                print(f"Could not load {workflow_type}: {e}")

        return workflows

    def test_model_validation_chat(self) -> ChatSessionMetrics:
        """Test chat interactions for model validation workflow."""
        print("\\n=== Testing Model Validation Workflow Chat ===")

        session = ChatSessionMetrics("test_user_001", "model_validation")
        workflow = self.test_workflows.get("model_validation", {})

        # Test scenarios for model validation
        test_questions = [
            "How can I ensure my credit risk model validation meets SR 11-7 requirements?",
            "What are the key documentation elements needed for model validation?",
            "My model validation is taking too long - how can I optimize the process?",
            "What confidence threshold should I use for validation findings?"
        ]

        print(f"Session ID: {session.session_id}")
        print(f"Testing {len(test_questions)} questions...")

        for i, question in enumerate(test_questions, 1):
            print(f"\\nQuestion {i}: {question}")

            # Simulate real AI advisor call
            try:
                start_time = time.time()

                # Import the actual workflow advisor
                from workflow_advisor import workflow_advisor

                # Get real workflow criteria
                criteria = self._load_workflow_criteria("model_validation")
                template_fields = workflow.get("template_fields", {})

                # Make real AI call
                response_data = workflow_advisor.get_workflow_advice(
                    criteria=criteria,
                    template_fields=template_fields,
                    recent_activity=[],
                    final_results={},
                    user_question=question
                )

                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms

                if response_data.get("success", False):
                    response = response_data["advice"]
                    rag_enhanced = response_data.get("context_analyzed", {}).get("rag_enhanced", False)

                    # Estimate tokens and cost (rough estimates)
                    estimated_tokens = len(question.split()) + len(response.split()) * 2  # Input + output tokens
                    estimated_cost = estimated_tokens * 0.00003  # Rough Claude cost estimate

                    session.add_interaction(question, response, estimated_tokens, estimated_cost)
                    session.interactions[-1]["response_time_ms"] = response_time
                    session.interactions[-1]["rag_enhanced"] = rag_enhanced

                    print(f"Response received ({response_time:.1f}ms, ~{estimated_tokens} tokens, RAG: {rag_enhanced})")
                    print(f"Response preview: {response[:150]}...")

                else:
                    error_msg = response_data.get("advice", "Unknown error occurred")
                    session.add_interaction(question, f"ERROR: {error_msg}", 0, 0)
                    print(f"Error: {error_msg}")

            except Exception as e:
                error_msg = f"Exception during AI call: {str(e)}"
                session.add_interaction(question, error_msg, 0, 0)
                print(f"Exception: {e}")

        self.test_sessions.append(session)
        return session

    def test_performance_monitoring_chat(self) -> ChatSessionMetrics:
        """Test chat interactions for performance monitoring workflow."""
        print("\\n=== Testing Performance Monitoring Workflow Chat ===")

        session = ChatSessionMetrics("test_user_002", "model_monitoring")
        workflow = self.test_workflows.get("model_monitoring", {})

        test_questions = [
            "How do I set up automated alerts for model performance degradation?",
            "What monitoring frequency should I use for credit risk models?",
            "My model performance dashboard shows anomalies - what should I investigate?",
            "Can you help me optimize the parallel processing in monitoring workflows?"
        ]

        print(f"Session ID: {session.session_id}")

        for i, question in enumerate(test_questions, 1):
            print(f"\\nQuestion {i}: {question}")

            try:
                start_time = time.time()

                from workflow_advisor import workflow_advisor

                criteria = self._load_workflow_criteria("model_monitoring")
                template_fields = workflow.get("template_fields", {})

                response_data = workflow_advisor.get_workflow_advice(
                    criteria=criteria,
                    template_fields=template_fields,
                    recent_activity=[],
                    final_results={},
                    user_question=question
                )

                end_time = time.time()
                response_time = (end_time - start_time) * 1000

                if response_data.get("success", False):
                    response = response_data["advice"]
                    rag_enhanced = response_data.get("context_analyzed", {}).get("rag_enhanced", False)

                    estimated_tokens = len(question.split()) + len(response.split()) * 2
                    estimated_cost = estimated_tokens * 0.00003

                    session.add_interaction(question, response, estimated_tokens, estimated_cost)
                    session.interactions[-1]["response_time_ms"] = response_time
                    session.interactions[-1]["rag_enhanced"] = rag_enhanced

                    print(f"Response received ({response_time:.1f}ms, ~{estimated_tokens} tokens, RAG: {rag_enhanced})")
                    print(f"Response preview: {response[:150]}...")

                else:
                    error_msg = response_data.get("advice", "Unknown error occurred")
                    session.add_interaction(question, f"ERROR: {error_msg}", 0, 0)
                    print(f"Error: {error_msg}")

            except Exception as e:
                error_msg = f"Exception during AI call: {str(e)}"
                session.add_interaction(question, error_msg, 0, 0)
                print(f"Exception: {e}")

        self.test_sessions.append(session)
        return session

    def test_compliance_chat(self) -> ChatSessionMetrics:
        """Test chat interactions for regulatory compliance workflow."""
        print("\\n=== Testing Regulatory Compliance Workflow Chat ===")

        session = ChatSessionMetrics("test_user_003", "regulatory_compliance")
        workflow = self.test_workflows.get("regulatory_compliance", {})

        test_questions = [
            "What are the key differences between SR 11-7 and CCAR compliance requirements?",
            "How do I prioritize compliance gaps in my remediation plan?",
            "My compliance assessment is showing critical findings - what immediate actions should I take?",
            "Can you help me understand the multi-framework compliance approach?"
        ]

        print(f"Session ID: {session.session_id}")

        for i, question in enumerate(test_questions, 1):
            print(f"\\nQuestion {i}: {question}")

            try:
                start_time = time.time()

                from workflow_advisor import workflow_advisor

                criteria = self._load_workflow_criteria("regulatory_compliance")
                template_fields = workflow.get("template_fields", {})

                response_data = workflow_advisor.get_workflow_advice(
                    criteria=criteria,
                    template_fields=template_fields,
                    recent_activity=[],
                    final_results={},
                    user_question=question
                )

                end_time = time.time()
                response_time = (end_time - start_time) * 1000

                if response_data.get("success", False):
                    response = response_data["advice"]
                    rag_enhanced = response_data.get("context_analyzed", {}).get("rag_enhanced", False)

                    estimated_tokens = len(question.split()) + len(response.split()) * 2
                    estimated_cost = estimated_tokens * 0.00003

                    session.add_interaction(question, response, estimated_tokens, estimated_cost)
                    session.interactions[-1]["response_time_ms"] = response_time
                    session.interactions[-1]["rag_enhanced"] = rag_enhanced

                    print(f"Response received ({response_time:.1f}ms, ~{estimated_tokens} tokens, RAG: {rag_enhanced})")
                    print(f"Response preview: {response[:150]}...")

                else:
                    error_msg = response_data.get("advice", "Unknown error occurred")
                    session.add_interaction(question, f"ERROR: {error_msg}", 0, 0)
                    print(f"Error: {error_msg}")

            except Exception as e:
                error_msg = f"Exception during AI call: {str(e)}"
                session.add_interaction(question, error_msg, 0, 0)
                print(f"Exception: {e}")

        self.test_sessions.append(session)
        return session

    def _load_workflow_criteria(self, workflow_type: str) -> Dict:
        """Load criteria for a specific workflow type."""
        try:
            criteria_path = f"tidyllm/workflows/definitions/workflows/{workflow_type}/criteria/criteria.json"
            with open(criteria_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            # Fallback to template criteria
            try:
                with open("tidyllm/workflows/definitions/workflows/templates/criteria/criteria.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}

    def generate_comprehensive_report(self):
        """Generate comprehensive test report with metrics."""
        print("\\n" + "="*80)
        print("COMPREHENSIVE AI CHAT TESTING REPORT")
        print("="*80)

        total_interactions = sum(len(session.interactions) for session in self.test_sessions)
        total_tokens = sum(session.total_tokens_used for session in self.test_sessions)
        total_cost = sum(session.total_cost_estimate for session in self.test_sessions)

        print(f"\\nOverall Test Summary:")
        print(f"Total Sessions: {len(self.test_sessions)}")
        print(f"Total Interactions: {total_interactions}")
        print(f"Total Tokens Used: {total_tokens:,}")
        print(f"Total Estimated Cost: ${total_cost:.4f}")

        print(f"\\nPer-Session Breakdown:")
        for i, session in enumerate(self.test_sessions, 1):
            summary = session.get_session_summary()
            print(f"\\n{i}. {summary['workflow_type'].title()} Session:")
            print(f"   Session ID: {summary['session_id']}")
            print(f"   User ID: {summary['user_id']}")
            print(f"   Duration: {summary['duration_seconds']:.1f} seconds")
            print(f"   Interactions: {summary['total_interactions']}")
            print(f"   Tokens Used: {summary['total_tokens_used']:,}")
            print(f"   Estimated Cost: ${summary['total_cost_estimate']:.4f}")
            print(f"   Avg Response Time: {summary['average_response_time']:.1f}ms")

            # Show successful vs failed interactions
            successful = sum(1 for i in summary['interactions'] if not i['response'].startswith('ERROR:'))
            failed = summary['total_interactions'] - successful
            print(f"   Success Rate: {successful}/{summary['total_interactions']} ({successful/max(summary['total_interactions'],1)*100:.1f}%)")

        # Save detailed report
        report_file = Path("tidyllm/workflows/ai_advisor/chat_test_report.json")
        report_file.parent.mkdir(exist_ok=True)

        full_report = {
            "test_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_sessions": len(self.test_sessions),
                "total_interactions": total_interactions,
                "total_tokens_used": total_tokens,
                "total_estimated_cost": total_cost
            },
            "sessions": [session.get_session_summary() for session in self.test_sessions]
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)

        print(f"\\nDetailed report saved to: {report_file}")

        return full_report

def run_comprehensive_chat_tests():
    """Run all chat tests and generate report."""
    print("Starting Comprehensive AI Chat Feature Testing")
    print("=" * 50)

    tester = WorkflowChatTester()

    # Test each workflow type
    tester.test_model_validation_chat()
    tester.test_performance_monitoring_chat()
    tester.test_compliance_chat()

    # Generate comprehensive report
    return tester.generate_comprehensive_report()

if __name__ == "__main__":
    run_comprehensive_chat_tests()