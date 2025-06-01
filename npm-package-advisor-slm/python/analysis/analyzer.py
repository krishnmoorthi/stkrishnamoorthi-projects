import json
import os
from typing import Dict, Any
from openai import OpenAI
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UpdateAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('AI_MODEL', 'gpt-4-1106-preview')
        
    def analyze_dependencies(self, npm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze NPM dependencies and provide update recommendations"""
        try:
            prompt = self._build_analysis_prompt(npm_data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return self._format_analysis(analysis, npm_data)
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                "error": str(e),
                "recommendations": [],
                "summary": {}
            }
    
    def _build_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Construct the AI prompt for analysis"""
        return f"""
        You are an expert NPM package dependency analyzer. Analyze this project's dependencies:
        
        Project: {data.get('project', 'Unknown')}
        Collected at: {data.get('timestamp', datetime.utcnow().isoformat())}
        
        Current Dependencies: {json.dumps(data.get('dependencies', {}), indent=2)}
        Dev Dependencies: {json.dumps(data.get('devDependencies', {}), indent=2)}
        Outdated Packages: {json.dumps(data.get('outdated', {}), indent=2)}
        Vulnerabilities: {json.dumps(data.get('vulnerabilities', {}), indent=2)}
        
        Provide recommendations with:
        1. Critical security updates (priority 1 - red)
        2. Major version updates (priority 2 - orange)
        3. Minor/patch updates (priority 3 - yellow)
        
        For each recommendation, include:
        - Current and available versions
        - Risk assessment (low/medium/high)
        - Brief changelog summary
        - Testing recommendations
        - Security implications
        
        Format response as JSON with this structure:
        {{
            "project": "project_name",
            "timestamp": "iso_timestamp",
            "recommendations": [
                {{
                    "package": "package_name",
                    "type": "dependency|devDependency",
                    "current": "1.0.0",
                    "available": "2.1.3",
                    "priority": 1|2|3,
                    "risk": "low|medium|high",
                    "changelog_summary": "brief summary",
                    "testing_required": ["unit", "integration", "e2e"],
                    "security_impact": "none|low|high",
                    "vulnerabilities": ["CVE-XXXX-XXXX"],
                    "update_command": "npm install package@version"
                }}
            ],
            "summary": {{
                "total_dependencies": 0,
                "outdated": 0,
                "critical": 0,
                "major": 0,
                "minor": 0,
                "vulnerabilities": 0
            }}
        }}
        """
    
    def _format_analysis(self, analysis: Dict[str, Any], original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process the AI analysis"""
        # Add additional metadata
        analysis['original_data'] = {
            'dependencies_count': len(original_data.get('dependencies', {})),
            'devDependencies_count': len(original_data.get('devDependencies', {})),
            'outdated_count': len(original_data.get('outdated', {})),
            'vulnerabilities_count': original_data.get('vulnerabilities', {}).get('metadata', {}).get('vulnerabilities', {}).get('total', 0)
        }
        
        # Generate update commands
        for rec in analysis.get('recommendations', []):
            rec['update_command'] = f"npm install {rec['package']}@{rec['available']}" + \
                                   (" --save-dev" if rec.get('type') == 'devDependency' else "")
        
        return analysis