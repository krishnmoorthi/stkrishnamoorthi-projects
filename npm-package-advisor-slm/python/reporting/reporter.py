import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os
from jinja2 import Template
from typing import List, Dict, Any

class ReportGenerator:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'smtp_server': os.getenv('SMTP_SERVER'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'smtp_user': os.getenv('SMTP_USER'),
            'smtp_password': os.getenv('SMTP_PASSWORD'),
            'email_from': os.getenv('EMAIL_FROM', 'npm-advisor@example.com')
        }
        
        # Load HTML template
        self.template = Template('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>NPM Package Update Report - {{ report.project }}</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .critical { background-color: #ffdddd; }
                .major { background-color: #fff3d6; }
                .minor { background-color: #e7f5e8; }
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
                .priority-1 { color: #d32f2f; font-weight: bold; }
                .priority-2 { color: #ff9800; }
                .priority-3 { color: #4caf50; }
            </style>
        </head>
        <body>
            <h1>NPM Package Update Report</h1>
            <h2>{{ report.project }}</h2>
            <p>Generated on: {{ report.timestamp }}</p>
            
            <div class="summary">
                <h3>Summary</h3>
                <ul>
                    <li>Total Dependencies: {{ report.summary.total_dependencies }}</li>
                    <li>Outdated Packages: {{ report.summary.outdated }}</li>
                    <li>Critical Updates: <span class="priority-1">{{ report.summary.critical }}</span></li>
                    <li>Major Updates: <span class="priority-2">{{ report.summary.major }}</span></li>
                    <li>Minor Updates: <span class="priority-3">{{ report.summary.minor }}</span></li>
                    <li>Vulnerabilities: {{ report.summary.vulnerabilities }}</li>
                </ul>
            </div>
            
            <div class="recommendations">
                <h3>Update Recommendations</h3>
                <table>
                    <tr>
                        <th>Package</th>
                        <th>Type</th>
                        <th>Current</th>
                        <th>Available</th>
                        <th>Priority</th>
                        <th>Risk</th>
                        <th>Action</th>
                    </tr>
                    {% for rec in report.recommendations %}
                    <tr class="{% if rec.priority == 1 %}critical{% elif rec.priority == 2 %}major{% else %}minor{% endif %}">
                        <td>{{ rec.package }}</td>
                        <td>{{ rec.type }}</td>
                        <td>{{ rec.current }}</td>
                        <td>{{ rec.available }}</td>
                        <td class="priority-{{ rec.priority }}">{{ rec.priority }}</td>
                        <td>{{ rec.risk }}</td>
                        <td>
                            <code>{{ rec.update_command }}</code><br>
                            <small>{{ rec.changelog_summary }}</small>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="footer">
                <p>This report was generated automatically by NPM Package Advisor SLM</p>
            </div>
        </body>
        </html>
        ''')

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate HTML report from analysis"""
        return self.template.render(report=analysis)
    
    def save_report(self, analysis: Dict[str, Any], output_dir: str = 'reports') -> str:
        """Save report to HTML file"""
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/npm_update_{analysis['project']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        with open(filename, 'w') as f:
            html = self.generate_report(analysis)
            f.write(html)
        
        return filename
    
    def send_report(self, analysis: Dict[str, Any], recipients: List[str]) -> bool:
        """Send report via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email_from']
            msg['Subject'] = f"NPM Update Report - {analysis['project']} - {datetime.now().strftime('%Y-%m-%d')}"
            
            # HTML content
            html = self.generate_report(analysis)
            msg.attach(MIMEText(html, 'html'))
            
            # Text alternative
            text = f"NPM Package Update Report for {analysis['project']}\n\n"
            text += f"Outdated packages: {analysis['summary']['outdated']}\n"
            text += f"Critical updates: {analysis['summary']['critical']}\n"
            text += "Recommendations:\n"
            for rec in analysis['recommendations']:
                text += f"- {rec['package']}: {rec['current']} → {rec['available']} (Priority {rec['priority']})\n"
            
            msg.attach(MIMEText(text, 'plain'))
            
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['smtp_user'], self.config['smtp_password'])
                for recipient in recipients:
                    msg['To'] = recipient
                    server.sendmail(self.config['email_from'], recipient, msg.as_string())
            
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False