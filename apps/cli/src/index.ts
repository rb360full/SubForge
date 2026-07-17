import { fileURLToPath } from "node:url";
import { resolve } from "node:path";
import { parseCommand } from "@subforge/core";

export const VERSION = "0.1.0";

export function run(argv: string[] = process.argv.slice(2)): number {
    const { name } = parseCommand(argv);

    if (argv.includes("--version") || argv.includes("-v")) {
        console.log(VERSION);
        return 0;
    }

    if (name === "hello") {
        console.log("Hello from SubForge");
        return 0;
    }

    console.log("SubForge CLI");
    console.log(`Version ${VERSION}`);
    return 0;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === resolve(process.argv[1])) {
    run();
}
