import { describe, expect, it, vi } from "vitest";
import { VERSION, run } from "./index.js";

describe("cli", () => {
    it("prints version for version command", () => {
        const log = vi.spyOn(console, "log").mockImplementation(() => undefined);

        const exitCode = run(["--version"]);

        expect(exitCode).toBe(0);
        expect(log).toHaveBeenCalledWith(VERSION);

        log.mockRestore();
    });

    it("prints hello for hello command", () => {
        const log = vi.spyOn(console, "log").mockImplementation(() => undefined);

        const exitCode = run(["hello"]);

        expect(exitCode).toBe(0);
        expect(log).toHaveBeenCalledWith("Hello from SubForge");

        log.mockRestore();
    });
});

