import { describe, expect, it } from "vitest";
import { createCommandContext, matchCommand, parseCommand } from "./index.js";

describe("parser", () => {
    it("parses a simple command", () => {
        expect(parseCommand(["hello", "world"])).toEqual({
            name: "hello",
            args: ["world"]
        });
    });

    it("creates a command context", () => {
        const context = createCommandContext(["hello"], [
            { name: "hello", description: "Say hello", usage: "subforge hello" }
        ]);

        expect(context).toEqual({
            argv: ["hello"],
            command: { name: "hello", args: [] },
            definitions: [
                { name: "hello", description: "Say hello", usage: "subforge hello" }
            ]
        });
    });

    it("matches a known command definition", () => {
        const context = createCommandContext(["hello"], [
            { name: "hello", description: "Say hello", usage: "subforge hello" }
        ]);

        expect(matchCommand(context)).toEqual({
            definition: { name: "hello", description: "Say hello", usage: "subforge hello" },
            isKnown: true
        });
    });

    it("marks unknown commands as not known", () => {
        const context = createCommandContext(["unknown"], [
            { name: "hello", description: "Say hello", usage: "subforge hello" }
        ]);

        expect(matchCommand(context)).toEqual({
            definition: undefined,
            isKnown: false
        });
    });
});
