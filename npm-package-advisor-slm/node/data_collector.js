const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function getNpmDependencies(projectPath = process.cwd()) {
  try {
    // Read package.json
    const packageJsonPath = path.join(projectPath, 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
    
    // Get outdated packages (silent mode for clean JSON output)
    const outdated = execSync('npm outdated --json --silent', { 
      encoding: 'utf-8',
      cwd: projectPath
    });
    
    // Get npm audit results
    const audit = execSync('npm audit --json --silent', {
      encoding: 'utf-8',
      cwd: projectPath
    }).toString();

    return {
      project: path.basename(projectPath),
      timestamp: new Date().toISOString(),
      dependencies: packageJson.dependencies || {},
      devDependencies: packageJson.devDependencies || {},
      peerDependencies: packageJson.peerDependencies || {},
      outdated: outdated ? JSON.parse(outdated) : {},
      vulnerabilities: audit ? JSON.parse(audit) : {}
    };
  } catch (error) {
    console.error('Error collecting NPM data:', error.message);
    return {
      error: error.message,
      stack: error.stack
    };
  }
}

module.exports = { getNpmDependencies };