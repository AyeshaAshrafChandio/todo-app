#!/usr/bin/env node

/**
 * Production Validation Script
 * Validates the codebase for production readiness
 *
 * Checks:
 * - No console.log statements in production code
 * - No hardcoded secrets or API keys
 * - All API calls use the apiClient (JWT token handling)
 * - Error handling is implemented
 * - Environment variables are properly used
 */

const fs = require('fs');
const path = require('path');

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

// Validation results
const results = {
  passed: [],
  warnings: [],
  errors: [],
};

/**
 * Recursively get all files in a directory
 */
function getAllFiles(dirPath, arrayOfFiles = [], extensions = ['.ts', '.tsx', '.js', '.jsx']) {
  const files = fs.readdirSync(dirPath);

  files.forEach((file) => {
    const filePath = path.join(dirPath, file);

    if (fs.statSync(filePath).isDirectory()) {
      // Skip node_modules and .next directories
      if (file !== 'node_modules' && file !== '.next' && file !== 'dist' && file !== 'build') {
        arrayOfFiles = getAllFiles(filePath, arrayOfFiles, extensions);
      }
    } else {
      const ext = path.extname(file);
      if (extensions.includes(ext)) {
        arrayOfFiles.push(filePath);
      }
    }
  });

  return arrayOfFiles;
}

/**
 * Check for console.log statements
 */
function checkConsoleLogs(files) {
  console.log(`${colors.cyan}Checking for console.log statements...${colors.reset}`);

  let foundIssues = false;

  files.forEach((file) => {
    // Skip examples folder and error boundary
    if (file.includes('examples') || file.includes('ErrorBoundary')) {
      return;
    }

    const content = fs.readFileSync(file, 'utf8');
    const lines = content.split('\n');

    lines.forEach((line, index) => {
      // Skip comments
      if (line.trim().startsWith('//') || line.trim().startsWith('*')) {
        return;
      }

      if (line.includes('console.log') || line.includes('console.error') || line.includes('console.warn')) {
        foundIssues = true;
        results.warnings.push({
          file: path.relative(process.cwd(), file),
          line: index + 1,
          message: 'Console statement found',
          code: line.trim(),
        });
      }
    });
  });

  if (!foundIssues) {
    results.passed.push('No console statements found');
  }
}

/**
 * Check for hardcoded secrets
 */
function checkHardcodedSecrets(files) {
  console.log(`${colors.cyan}Checking for hardcoded secrets...${colors.reset}`);

  const secretPatterns = [
    /api[_-]?key\s*=\s*['"][^'"]+['"]/i,
    /secret\s*=\s*['"][^'"]+['"]/i,
    /password\s*=\s*['"][^'"]+['"]/i,
    /token\s*=\s*['"][^'"]+['"]/i,
    /bearer\s+[a-zA-Z0-9_-]{20,}/i,
    /sk_live_[a-zA-Z0-9]+/,
    /pk_live_[a-zA-Z0-9]+/,
  ];

  let foundIssues = false;

  files.forEach((file) => {
    // Skip examples folder
    if (file.includes('examples')) {
      return;
    }

    const content = fs.readFileSync(file, 'utf8');
    const lines = content.split('\n');

    lines.forEach((line, index) => {
      // Skip comments, environment variable usage, and validation messages
      if (line.trim().startsWith('//') ||
          line.trim().startsWith('*') ||
          line.includes('process.env') ||
          line.includes('NEXT_PUBLIC_') ||
          line.includes('newErrors.') ||
          line.includes('errors.') ||
          line.includes('is required') ||
          line.includes('must be at least')) {
        return;
      }

      secretPatterns.forEach((pattern) => {
        if (pattern.test(line)) {
          foundIssues = true;
          results.errors.push({
            file: path.relative(process.cwd(), file),
            line: index + 1,
            message: 'Potential hardcoded secret found',
            code: line.trim().substring(0, 80) + '...',
          });
        }
      });
    });
  });

  if (!foundIssues) {
    results.passed.push('No hardcoded secrets found');
  }
}

/**
 * Check for proper API client usage
 */
function checkApiClientUsage(files) {
  console.log(`${colors.cyan}Checking API client usage...${colors.reset}`);

  let foundIssues = false;

  files.forEach((file) => {
    // Skip the API client file itself and examples folder
    if (file.includes('api/client.ts') || file.includes('examples')) {
      return;
    }

    const content = fs.readFileSync(file, 'utf8');
    const lines = content.split('\n');

    lines.forEach((line, index) => {
      // Check for direct fetch calls to API
      if (line.includes('fetch(') &&
          (line.includes('API_URL') || line.includes('localhost:8000') || line.includes('/api/'))) {
        // Check if it's importing or using apiClient
        if (!content.includes('apiClient') && !content.includes('from \'@/lib/api/client\'')) {
          foundIssues = true;
          results.warnings.push({
            file: path.relative(process.cwd(), file),
            line: index + 1,
            message: 'Direct fetch call found - should use apiClient for JWT token handling',
            code: line.trim(),
          });
        }
      }
    });
  });

  if (!foundIssues) {
    results.passed.push('All API calls use apiClient');
  }
}

/**
 * Check for proper error handling
 */
function checkErrorHandling(files) {
  console.log(`${colors.cyan}Checking error handling...${colors.reset}`);

  let foundIssues = false;

  files.forEach((file) => {
    // Skip examples folder
    if (file.includes('examples')) {
      return;
    }

    const content = fs.readFileSync(file, 'utf8');

    // Check for async functions without try-catch
    const asyncFunctionRegex = /async\s+function\s+\w+\s*\([^)]*\)\s*{/g;
    const matches = content.match(asyncFunctionRegex);

    if (matches) {
      matches.forEach((match) => {
        const functionStart = content.indexOf(match);
        const functionContent = content.substring(functionStart, functionStart + 500);

        if (!functionContent.includes('try') && !functionContent.includes('catch')) {
          foundIssues = true;
          results.warnings.push({
            file: path.relative(process.cwd(), file),
            message: 'Async function without try-catch block',
            code: match.trim(),
          });
        }
      });
    }
  });

  if (!foundIssues) {
    results.passed.push('Error handling appears adequate');
  }
}

/**
 * Check environment variables
 */
function checkEnvironmentVariables() {
  console.log(`${colors.cyan}Checking environment variables...${colors.reset}`);

  const envExamplePath = path.join(process.cwd(), '.env.local.example');
  const envPath = path.join(process.cwd(), '.env.local');

  if (!fs.existsSync(envExamplePath)) {
    results.warnings.push({
      message: '.env.local.example file not found',
    });
  } else {
    results.passed.push('.env.local.example file exists');
  }

  if (!fs.existsSync(envPath)) {
    results.warnings.push({
      message: '.env.local file not found - make sure to create it for local development',
    });
  } else {
    results.passed.push('.env.local file exists');
  }
}

/**
 * Print results
 */
function printResults() {
  console.log('\n' + '='.repeat(80));
  console.log(`${colors.blue}VALIDATION RESULTS${colors.reset}`);
  console.log('='.repeat(80) + '\n');

  // Passed checks
  if (results.passed.length > 0) {
    console.log(`${colors.green}✓ PASSED (${results.passed.length})${colors.reset}`);
    results.passed.forEach((msg) => {
      console.log(`  ${colors.green}✓${colors.reset} ${msg}`);
    });
    console.log('');
  }

  // Warnings
  if (results.warnings.length > 0) {
    console.log(`${colors.yellow}⚠ WARNINGS (${results.warnings.length})${colors.reset}`);
    results.warnings.forEach((warning) => {
      console.log(`  ${colors.yellow}⚠${colors.reset} ${warning.message}`);
      if (warning.file) {
        console.log(`    File: ${warning.file}${warning.line ? `:${warning.line}` : ''}`);
      }
      if (warning.code) {
        console.log(`    Code: ${warning.code}`);
      }
      console.log('');
    });
  }

  // Errors
  if (results.errors.length > 0) {
    console.log(`${colors.red}✗ ERRORS (${results.errors.length})${colors.reset}`);
    results.errors.forEach((error) => {
      console.log(`  ${colors.red}✗${colors.reset} ${error.message}`);
      if (error.file) {
        console.log(`    File: ${error.file}${error.line ? `:${error.line}` : ''}`);
      }
      if (error.code) {
        console.log(`    Code: ${error.code}`);
      }
      console.log('');
    });
  }

  // Summary
  console.log('='.repeat(80));
  console.log(`${colors.blue}SUMMARY${colors.reset}`);
  console.log('='.repeat(80));
  console.log(`Passed:   ${colors.green}${results.passed.length}${colors.reset}`);
  console.log(`Warnings: ${colors.yellow}${results.warnings.length}${colors.reset}`);
  console.log(`Errors:   ${colors.red}${results.errors.length}${colors.reset}`);
  console.log('');

  if (results.errors.length === 0) {
    console.log(`${colors.green}✓ Production validation passed!${colors.reset}`);
    process.exit(0);
  } else {
    console.log(`${colors.red}✗ Production validation failed. Please fix the errors above.${colors.reset}`);
    process.exit(1);
  }
}

/**
 * Main execution
 */
function main() {
  console.log(`${colors.blue}Starting production validation...${colors.reset}\n`);

  const srcPath = path.join(process.cwd(), 'src');

  if (!fs.existsSync(srcPath)) {
    console.error(`${colors.red}Error: src directory not found${colors.reset}`);
    process.exit(1);
  }

  const files = getAllFiles(srcPath);
  console.log(`Found ${files.length} files to validate\n`);

  // Run all checks
  checkConsoleLogs(files);
  checkHardcodedSecrets(files);
  checkApiClientUsage(files);
  checkErrorHandling(files);
  checkEnvironmentVariables();

  // Print results
  printResults();
}

// Run the script
main();
