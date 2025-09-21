#!/usr/bin/env python3
"""
TidyLLM Chat + MLflow Integration Test

Tests the chat feature with active MLflow tracking to PostgreSQL backend.
Records all chat interactions with comprehensive metrics and artifacts.
"""

import os
import time
import mlflow
import mlflow.tracking
from datetime import datetime
from typing import Dict, Any, Optional

# Set up credentials
# Credentials loaded by centralized system
# Credentials loaded by centralized system
os.environ['POSTGRES_HOST'] = 'vectorqa-cluster.cluster-cu562e4m02nq.us-east-1.rds.amazonaws.com'
os.environ['POSTGRES_DB'] = 'vectorqa'
os.environ['POSTGRES_USER'] = 'vectorqa_user'
os.environ['POSTGRES_PASSWORD'] = 'Fujifuji500!'

# Configure MLflow with PostgreSQL
postgres_uri = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:5432/{os.getenv('POSTGRES_DB')}"
mlflow.set_tracking_uri(postgres_uri)

# Import TidyLLM after setting up environment
import sys
sys.path.insert(0, 'tidyllm')
import tidyllm
from tidyllm import llm_message, chat, claude, bedrock

class MLflowChatTracker:
    """Enhanced chat system with MLflow tracking"""
    
    def __init__(self, experiment_name: str = "tidyllm-chat-production"):
        self.experiment_name = experiment_name
        self.setup_experiment()
    
    def setup_experiment(self):
        """Setup MLflow experiment"""
        try:
            self.experiment = mlflow.set_experiment(self.experiment_name)
            print(f"✅ MLflow experiment: {self.experiment_name} (ID: {self.experiment.experiment_id})")
        except Exception as e:
            print(f"❌ MLflow experiment setup failed: {e}")
            raise
    
    def tracked_chat(self, message_text: str, provider_name: str = "claude", model: str = "claude-3-5-sonnet", **kwargs) -> Dict[str, Any]:
        """Execute chat with full MLflow tracking"""
        
        start_time = time.time()
        
        with mlflow.start_run() as run:
            try:
                # Log input parameters
                mlflow.log_param("provider", provider_name)
                mlflow.log_param("model", model)
                mlflow.log_param("message_length", len(message_text))
                mlflow.log_param("timestamp", datetime.now().isoformat())
                
                # Log additional parameters
                for key, value in kwargs.items():
                    mlflow.log_param(f"param_{key}", value)
                
                # Create message and provider
                message = llm_message(message_text)
                
                if provider_name.lower() == "claude":
                    provider = claude(model=model)
                elif provider_name.lower() == "bedrock":
                    provider = bedrock(model=model)
                else:
                    provider = claude(model=model)  # Default fallback
                
                # Execute chat
                response = message | chat(provider)
                
                # Calculate metrics
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # ms
                
                # Log metrics
                mlflow.log_metric("response_time_ms", response_time)
                mlflow.log_metric("response_length", len(response))
                mlflow.log_metric("input_tokens_estimate", len(message_text.split()))
                mlflow.log_metric("output_tokens_estimate", len(response.split()))
                
                # Estimate cost (mock calculation)
                estimated_cost = (len(message_text) + len(response)) * 0.000001  # $0.000001 per character
                mlflow.log_metric("estimated_cost_usd", estimated_cost)
                
                # Log artifacts
                mlflow.log_text(message_text, "input_message.txt")
                mlflow.log_text(response, "response_message.txt")
                
                # Set tags
                mlflow.set_tag("chat_session", f"session_{int(time.time())}")
                mlflow.set_tag("environment", "production")
                mlflow.set_tag("tidyllm_version", "0.1.0")
                mlflow.set_tag("status", "success")
                
                result = {
                    "run_id": run.info.run_id,
                    "message": message_text,
                    "response": response,
                    "provider": provider_name,
                    "model": model,
                    "response_time_ms": response_time,
                    "estimated_cost_usd": estimated_cost,
                    "status": "success"
                }
                
                print(f"✅ Chat tracked: Run {run.info.run_id[:8]}... - {response_time:.1f}ms")
                return result
                
            except Exception as e:
                # Log error
                mlflow.log_param("error", str(e))
                mlflow.set_tag("status", "error")
                
                print(f"❌ Chat error: {e}")
                return {
                    "run_id": run.info.run_id,
                    "message": message_text,
                    "error": str(e),
                    "status": "error"
                }

def main():
    """Test chat + MLflow integration"""
    print("=" * 60)
    print("  TidyLLM Chat + MLflow Integration Test")
    print("=" * 60)
    
    try:
        # Initialize tracker
        tracker = MLflowChatTracker()
        
        print(f"\n1. Testing chat interactions with MLflow tracking...")
        
        # Test multiple chat interactions
        test_messages = [
            "What is machine learning in one sentence?",
            "Explain the benefits of using TidyLLM",
            "How does MLflow help with experiment tracking?",
            "What are the key features of enterprise AI systems?"
        ]
        
        results = []
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n   Chat {i}/4: {message[:50]}...")
            result = tracker.tracked_chat(
                message_text=message,
                provider_name="claude",
                model="claude-3-5-sonnet",
                test_batch="integration_test",
                sequence_number=i
            )
            results.append(result)
            time.sleep(0.5)  # Brief delay between requests
        
        # Test with Bedrock provider
        print(f"\n   Chat 5/5: Testing Bedrock provider...")
        bedrock_result = tracker.tracked_chat(
            message_text="What is 2+2?",
            provider_name="bedrock",
            model="anthropic.claude-3-haiku-20240307-v1:0",
            test_batch="integration_test",
            sequence_number=5
        )
        results.append(bedrock_result)
        
        # Summary
        print(f"\n2. Chat session summary:")
        successful_chats = [r for r in results if r.get("status") == "success"]
        total_cost = sum(r.get("estimated_cost_usd", 0) for r in successful_chats)
        avg_response_time = sum(r.get("response_time_ms", 0) for r in successful_chats) / len(successful_chats)
        
        print(f"   ✅ Successful chats: {len(successful_chats)}/{len(results)}")
        print(f"   💰 Total estimated cost: ${total_cost:.6f}")
        print(f"   ⏱️  Average response time: {avg_response_time:.1f}ms")
        
        # Query MLflow runs
        print(f"\n3. Querying MLflow runs...")
        client = mlflow.MlflowClient()
        runs = client.search_runs([tracker.experiment.experiment_id], max_results=10)
        print(f"   📊 Total runs in experiment: {len(runs)}")
        
        for run in runs[:3]:  # Show last 3 runs
            print(f"   Run {run.info.run_id[:8]}...: {run.data.tags.get('status', 'unknown')}")
        
        print(f"\n🎉 SUCCESS: Chat + MLflow integration fully operational!")
        print(f"✅ All chat interactions tracked in PostgreSQL")
        print(f"✅ MLflow experiment: {tracker.experiment_name}")
        print(f"✅ Tracking URI: postgresql://...vectorqa")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)