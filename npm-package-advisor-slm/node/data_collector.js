const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function getNpmDependencies(projectPath = process.cwd()) {
    try {
        const packageJsonPath = path.join(projectPath, 'package.json');
        if (!fs.existsSync(packageJsonPath)) {
            throw new Error(`package.json not found in ${projectPath}`);
        }

        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));

        let outdated = {};
        try {
            const outdatedOutput = execSync('npm outdated --json --silent', {
                encoding: 'utf-8',
                cwd: projectPath,
                stdio: ['pipe', 'pipe', 'ignore']
            });
            outdated = outdatedOutput ? JSON.parse(outdatedOutput) : {};
        } catch (outdatedError) {
            if (outdatedError.stdout) {
                outdated = JSON.parse(outdatedError.stdout);
            }
        }

        let vulnerabilities = {};
        try {
            const auditOutput = execSync('npm audit --json --silent', {
                encoding: 'utf-8',
                cwd: projectPath,
                stdio: ['pipe', 'pipe', 'ignore']
            });
            vulnerabilities = auditOutput ? JSON.parse(auditOutput) : {};
        } catch (auditError) {
            if (auditError.stdout) {
                vulnerabilities = JSON.parse(auditError.stdout);
            }
        }

        return {
            project: path.basename(projectPath),
            timestamp: new Date().toISOString(),
            dependencies: packageJson.dependencies || {},
            devDependencies: packageJson.devDependencies || {},
            peerDependencies: packageJson.peerDependencies || {},
            outdated: outdated,
            vulnerabilities: vulnerabilities
        };
    } catch (error) {
        return {
            error: error.message,
            stack: error.stack,
            additionalInfo: {
                projectPath,
                nodeVersion: process.version,
                npmVersion: execSync('npm -v').toString().trim()
            }
        };
    }
}

if (require.main === module) {
    const projectPath = process.argv[2] || process.cwd();
    // Only output pure JSON (no debug messages)
    process.stdout.write(JSON.stringify(getNpmDependencies(projectPath)));
}

module.exports = { getNpmDependencies };