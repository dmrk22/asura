import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const webDir = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repoDir = resolve(webDir, "..", "..");

/**
 * Run the product as one local demo instead of requiring two terminals.
 * The Next app needs the FastAPI service for every interactive feature.
 */
const services = [
  {
    name: "API",
    command: "uv",
    args: [
      "run",
      "--project",
      "apps/api",
      "uvicorn",
      "daari.main:app",
      "--app-dir",
      "apps/api",
      "--host",
      "127.0.0.1",
      "--port",
      "8000",
      "--reload",
    ],
    cwd: repoDir,
  },
  {
    name: "Web",
    command: "pnpm",
    args: ["dev", "--hostname", "127.0.0.1", "--port", "3000"],
    cwd: webDir,
  },
];

let stopping = false;
const children = [];

function stop(exitCode = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of children) {
    if (!child.killed) child.kill("SIGTERM");
  }
  process.exitCode = exitCode;
}

for (const service of services) {
  const child = spawn(service.command, service.args, {
    cwd: service.cwd,
    stdio: "inherit",
  });
  children.push(child);

  child.on("error", (error) => {
    console.error(`\n${service.name} could not start: ${error.message}`);
    stop(1);
  });

  child.on("exit", (code, signal) => {
    if (stopping) return;
    const reason = signal ? `signal ${signal}` : `exit code ${code ?? 1}`;
    console.error(
      `\n${service.name} stopped unexpectedly (${reason}). Stopping the demo.`,
    );
    stop(code ?? 1);
  });
}

console.log("\nDAARI demo is starting. Open http://localhost:3000/en/onboard");
console.log(
  "Keep this terminal open while presenting. Press Ctrl+C to stop both services.\n",
);

process.on("SIGINT", () => stop());
process.on("SIGTERM", () => stop());
