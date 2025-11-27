// Simple script to start Vite
const { spawn } = require('child_process');

console.log('Starting Vite...');
const vite = spawn('npx', ['vite', '--host'], {
  stdio: 'inherit',
  shell: true,
  cwd: __dirname
});

vite.on('error', (err) => {
  console.error('Failed to start Vite:', err);
  process.exit(1);
});

vite.on('exit', (code) => {
  process.exit(code);
});

