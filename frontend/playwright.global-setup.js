import { execSync } from 'child_process';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default async () => {
  const dbPath = path.join(__dirname, '..', '..', 'backend', 'data', 'gym_trac_e2e.db');
  try {
    fs.unlinkSync(dbPath);
  } catch (e) {
    // Ignore if file doesn't exist
  }
};
