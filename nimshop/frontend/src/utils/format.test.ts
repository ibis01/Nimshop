import { describe, it, expect } from "vitest";
import { lunaToNim, formatNim } from "./format";

describe("lunaToNim", () => {
  it("converts 100,000 Luna to 1.00000 NIM", () => {
    expect(lunaToNim(100_000)).toBe("1.00000");
  });

  it("converts 4,200,000 Luna to 42.00000 NIM", () => {
    expect(lunaToNim(4_200_000)).toBe("42.00000");
  });

  it("converts 0 Luna to 0.00000 NIM", () => {
    expect(lunaToNim(0)).toBe("0.00000");
  });

  it("throws on negative Luna", () => {
    expect(() => lunaToNim(-100)).toThrow();
  });

  it("throws on non-integer Luna", () => {
    expect(() => lunaToNim(100.5)).toThrow();
  });
});

describe("formatNim", () => {
  it("formats with NIM suffix", () => {
    expect(formatNim(4_200_000)).toBe("42.00000 NIM");
  });
});
