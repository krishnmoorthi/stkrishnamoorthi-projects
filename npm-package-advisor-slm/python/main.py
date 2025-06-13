import sys
import json
import os
from pathlib import Path
from datetime import datetime
import subprocess

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from analysis.analyzer import UpdateAnalyzer
from reporting.reporter import ReportGenerator
from config.settings import Settings

def verify_npm_installation():
    try:
        # Try both with and without shell=True
        result = subprocess.run(
            ['npm', '-v'],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            print(f"✅ Found npm version: {result.stdout.strip()}")
            return True
        
        # Try alternative approach if first failed
        npm_path = r"C:\Program Files\nodejs\npm.cmd" if os.name == 'nt' else 'npm'
        result = subprocess.run(
            [npm_path, '-v'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Found npm version: {result.stdout.strip()} at {npm_path}")
            return True
            
        print(f"❌ NPM check failed: {result.stderr}")
        return False
    except Exception as e:
        print(f"❌ NPM check error: {str(e)}")
        return False

def getNpmDependencies(project_path=None):
    try:
        project_path = project_path or Settings.SCAN_PROJECT_PATH
        project_path = os.path.normpath(project_path)
        
        print(f"[DEBUG] Using project path: {project_path}")
        
        if not os.path.exists(project_path):
            raise FileNotFoundError(f"Path does not exist: {project_path}")
        
        package_json = os.path.join(project_path, 'package.json')
        if not os.path.exists(package_json):
            raise FileNotFoundError(f"package.json not found in {project_path}")

        command = ['node', 'node/data_collector.js', project_path]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent),
            timeout=30,
            shell=True
        )
        
        # Filter out any non-JSON output lines
        json_output = '\n'.join(
            line for line in result.stdout.split('\n') 
            if line.strip().startswith('{') or line.strip().startswith('[')
        )
        
        if not json_output:
            raise ValueError("No valid JSON output received from Node process")
            
        return json.loads(json_output)
    except subprocess.TimeoutExpired:
        return {'error': 'Node process timed out after 30 seconds'}
    except json.JSONDecodeError as e:
        return {
            'error': f"Invalid JSON from Node process: {str(e)}",
            'output': result.stdout if 'result' in locals() else 'No output'
        }
    except Exception as e:
        return {
            'error': f"Unexpected error: {str(e)}",
            'type': type(e).__name__
        }
    
def main():
    print("🚀 Starting NPM Package Advisor SLM")
    
    if not verify_npm_installation():
        sys.exit(1)
    
    try:
        # 1. Collect NPM data
        print("🔍 Collecting NPM package information...")
        npm_data = getNpmDependencies(Settings.SCAN_PROJECT_PATH)
        
        if 'error' in npm_data:
            print(f"❌ Error collecting data: {npm_data['error']}")
            if 'additionalInfo' in npm_data:
                print("Additional info:", npm_data['additionalInfo'])
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