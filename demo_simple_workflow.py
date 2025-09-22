"""
Simple 2-Step Workflow Demo
============================
A demonstrable workflow that:
1. Extracts text from a document
2. Analyzes and summarizes the content

Perfect for client demonstrations!
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class SimpleWorkflowDemo:
    """Simple 2-step workflow for demonstration"""

    def __init__(self):
        self.workflow_name = "Simple Document Analyzer"
        self.start_time = None
        self.results = {}

    def run_workflow(self, input_text: str = None) -> Dict[str, Any]:
        """Execute the 2-step workflow"""

        print("\n" + "="*60)
        print(f"🚀 STARTING: {self.workflow_name}")
        print("="*60)

        self.start_time = datetime.now()

        # Default demo text if none provided
        if not input_text:
            input_text = """
            Project Status Report - Q4 2024

            Executive Summary:
            The development team has successfully delivered the new workflow automation system.
            Key achievements include improved processing speed by 40%, reduced manual errors
            by 75%, and increased user satisfaction scores to 4.8/5.0.

            Key Metrics:
            - Documents processed: 15,000+
            - Average processing time: 2.3 seconds
            - Accuracy rate: 99.2%
            - User adoption: 87%

            Next Steps:
            1. Deploy to production environment
            2. Conduct user training sessions
            3. Monitor system performance
            4. Gather feedback for v2.0 improvements
            """

        # STEP 1: Extract & Clean Document
        print("\n" + "-"*40)
        print("📄 STEP 1: Document Extraction")
        print("-"*40)

        extracted_data = self._step1_extract(input_text)
        print(f"✅ Extracted {extracted_data['word_count']} words")
        print(f"✅ Found {extracted_data['line_count']} lines")
        print(f"✅ Detected document type: {extracted_data['doc_type']}")

        # Simulate processing time
        time.sleep(1)

        # STEP 2: Analyze & Summarize
        print("\n" + "-"*40)
        print("🔍 STEP 2: Content Analysis")
        print("-"*40)

        analysis = self._step2_analyze(extracted_data)
        print(f"✅ Generated summary ({analysis['summary_length']} words)")
        print(f"✅ Identified {len(analysis['key_points'])} key points")
        print(f"✅ Sentiment: {analysis['sentiment']}")
        print(f"✅ Priority: {analysis['priority']}")

        # Calculate execution time
        execution_time = (datetime.now() - self.start_time).total_seconds()

        # Prepare final results
        self.results = {
            "workflow": self.workflow_name,
            "execution_time": f"{execution_time:.2f} seconds",
            "timestamp": datetime.now().isoformat(),
            "input_size": f"{len(input_text)} characters",
            "extraction": extracted_data,
            "analysis": analysis,
            "status": "SUCCESS"
        }

        # Display results
        self._display_results()

        return self.results

    def _step1_extract(self, text: str) -> Dict[str, Any]:
        """Step 1: Extract and clean document content"""

        # Clean the text
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        words = text.split()

        # Detect document type
        doc_type = "Report"
        if "summary" in text.lower():
            doc_type = "Status Report"
        elif "proposal" in text.lower():
            doc_type = "Proposal"
        elif "analysis" in text.lower():
            doc_type = "Analysis Document"

        return {
            "cleaned_text": ' '.join(lines),
            "lines": lines,
            "word_count": len(words),
            "line_count": len(lines),
            "doc_type": doc_type,
            "has_metrics": "%" in text or any(char.isdigit() for char in text)
        }

    def _step2_analyze(self, extracted_data: Dict) -> Dict[str, Any]:
        """Step 2: Analyze and summarize content"""

        text = extracted_data['cleaned_text']

        # Generate simple summary (first 2 lines)
        summary_lines = extracted_data['lines'][:2]
        summary = ' '.join(summary_lines)

        # Extract key points (lines with numbers or bullets)
        key_points = []
        for line in extracted_data['lines']:
            if any(marker in line for marker in ['1.', '2.', '3.', '-', '•', '%']):
                key_points.append(line[:50] + "..." if len(line) > 50 else line)

        # Simple sentiment analysis
        positive_words = ['success', 'achieved', 'improved', 'increased', 'delivered']
        negative_words = ['failed', 'delayed', 'decreased', 'error', 'issue']

        positive_count = sum(1 for word in positive_words if word in text.lower())
        negative_count = sum(1 for word in negative_words if word in text.lower())

        if positive_count > negative_count:
            sentiment = "Positive"
        elif negative_count > positive_count:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        # Determine priority
        priority = "Normal"
        if "urgent" in text.lower() or "critical" in text.lower():
            priority = "High"
        elif "executive" in text.lower() or "key" in text.lower():
            priority = "Medium-High"

        return {
            "summary": summary,
            "summary_length": len(summary.split()),
            "key_points": key_points[:5],  # Top 5 key points
            "sentiment": sentiment,
            "priority": priority,
            "has_action_items": "next steps" in text.lower() or "todo" in text.lower(),
            "metrics_found": extracted_data['has_metrics']
        }

    def _display_results(self):
        """Display formatted results"""

        print("\n" + "="*60)
        print("📊 WORKFLOW RESULTS")
        print("="*60)

        analysis = self.results['analysis']

        print(f"\n📝 Summary:")
        print(f"   {analysis['summary'][:100]}...")

        print(f"\n🎯 Key Points Identified:")
        for i, point in enumerate(analysis['key_points'], 1):
            print(f"   {i}. {point}")

        print(f"\n📈 Analysis Results:")
        print(f"   • Document Type: {self.results['extraction']['doc_type']}")
        print(f"   • Sentiment: {analysis['sentiment']}")
        print(f"   • Priority Level: {analysis['priority']}")
        print(f"   • Has Action Items: {'Yes' if analysis['has_action_items'] else 'No'}")
        print(f"   • Contains Metrics: {'Yes' if analysis['metrics_found'] else 'No'}")

        print(f"\n⏱️ Performance:")
        print(f"   • Total Execution Time: {self.results['execution_time']}")
        print(f"   • Input Size: {self.results['input_size']}")
        print(f"   • Status: ✅ {self.results['status']}")

        print("\n" + "="*60)
        print("✨ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*60)

    def save_results(self, output_dir: str = "demo_output"):
        """Save results to JSON file"""

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_path / f"workflow_results_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results saved to: {filename}")
        return filename


def main():
    """Run the demo workflow"""

    print("\n🎯 SIMPLE 2-STEP WORKFLOW DEMO")
    print("================================")
    print("This demo shows a basic document processing workflow:")
    print("  Step 1: Extract and clean document content")
    print("  Step 2: Analyze and summarize the information")

    # Create and run workflow
    demo = SimpleWorkflowDemo()

    # Option 1: Run with default demo text
    results = demo.run_workflow()

    # Option 2: Run with custom text (uncomment to use)
    # custom_text = "Your custom document text here..."
    # results = demo.run_workflow(custom_text)

    # Save results
    demo.save_results()

    print("\n👍 Demo complete! This workflow can be easily integrated")
    print("   into the Flow Portal for visual execution and monitoring.")

    return results


if __name__ == "__main__":
    # Run the demo
    results = main()

    # Show that results are available for further processing
    print(f"\n📦 Results object available with {len(results)} data points")
    print("   Ready for integration with larger workflow systems!")