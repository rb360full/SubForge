import { describe, expect, it } from "vitest";
import { type Result } from "./index.js";

describe("common", () => {
    it("supports the result shape", () => {
        const result: Result<number> = { success: true, value: 1 };

        expect(result).toEqual({ success: true, value: 1 });
    });
});

