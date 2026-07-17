import { describe, expect, it } from "vitest";
import { parseCommand } from "./index.js";

describe("parser", () => {
    it("parses a simple command", () => {
        expect(parseCommand(["hello", "world"])).toEqual({
            name: "hello",
            args: ["world"]
        });
    });
});

