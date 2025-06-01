import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from node.data_collector import getNpmDependencies
from analysis.analyzer import UpdateAnalyzer
from reporting.reporter import ReportGenerator
from config.settings import Settings

def main():
    print("🚀 Starting NPM Package Advisor SLM")
    
    try:
        # 1. Collect NPM data
        print("🔍 Collecting NPM package information...")
        npm_data = getNpmDependencies(Settings.SCAN_PROJECT_PATH)
        
        if 'error' in npm_data:
            print(f"❌ Error collecting data: {npm_data['error']}")
            return 1
        
        # 2. Analyze with AI
        print("🧠 Analyzing dependencies with AI...")
        analyzer = UpdateAnalyzer()
        analysis = analyzer.analyze_dependencies(npm_data)
        
        if 'error' in analysis:
            print(f"❌ Analysis failed: {analysis['error']}")
            return 1
        
        # 3. Generate and save report
        print("📊 Generating report...")
        reporter = ReportGenerator()
        report_path = reporter.save_report(analysis, Settings.REPORT_OUTPUT_DIR)
        print(f"✅ Report saved to: {report_path}")
        
        # 4. Send email if enabled
        if Settings.EMAIL_ENABLED and Settings.EMAIL_RECIPIENTS:
            print(f"📧 Sending report to {len(Settings.EMAIL_RECIPIENTS)} recipients...")
            success = reporter.send_report(analysis, Settings.EMAIL_RECIPIENTS)
            if success:
                print("✅ Email sent successfully")
            else:
                print("❌ Failed to send email")
        
        return 0
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())