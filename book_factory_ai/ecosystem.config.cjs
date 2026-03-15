/**
 * PM2: BackEbook (worker + servidor HTTP en puerto 9753)
 * Uso en el servidor: pm2 start ecosystem.config.cjs
 */
const path = require("path");

const appDir = __dirname;

module.exports = {
  apps: [
    {
      name: "backebook",
      script: "server.py",
      cwd: appDir,
      interpreter: path.join(appDir, "venv", "bin", "python"),
      interpreter_args: "",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "2G",
      env: {},
      error_file: path.join(appDir, "logs", "pm2-error.log"),
      out_file: path.join(appDir, "logs", "pm2-out.log"),
      merge_logs: true,
      time: true,
    },
  ],
};
