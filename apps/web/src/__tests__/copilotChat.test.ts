import { describe, it, expect } from "vitest";
import { reduceMessage, type ChatMessage } from "@/components/ai/useCopilotChat";

const blank: ChatMessage = { role: "assistant", content: "", steps: [], sources: [] };

describe("reduceMessage — SSE event folding", () => {
  it("folds a full agent turn into steps, sources, and content", () => {
    let m = blank;
    m = reduceMessage(m, { type: "router", content: "agent" });
    m = reduceMessage(m, { type: "tool_call", name: "calculate_risk_score" });
    m = reduceMessage(m, { type: "tool_result", name: "calculate_risk_score" });
    m = reduceMessage(m, { type: "sources", content: [{ title: "ESVS 2024", source: "doi:1" }] });
    m = reduceMessage(m, { type: "token", content: "RCRI " });
    m = reduceMessage(m, { type: "token", content: "is 2." });

    expect(m.steps.map((s) => [s.kind, s.status])).toEqual([
      ["router", "done"],
      ["tool", "done"], // tool_result flipped the running chip to done
    ]);
    expect(m.steps[1].label).toBe("Calculating risk score");
    expect(m.sources).toHaveLength(1);
    expect(m.content).toBe("RCRI is 2.");
  });

  it("marks a tool running until its result arrives", () => {
    const m = reduceMessage(blank, { type: "tool_call", name: "get_patient" });
    expect(m.steps[0].status).toBe("running");
    expect(m.steps[0].label).toBe("Reading patient record");
  });

  it("deduplicates sources by title", () => {
    let m = reduceMessage(blank, { type: "sources", content: [{ title: "A" }, { title: "B" }] });
    m = reduceMessage(m, { type: "sources", content: [{ title: "A" }, { title: "C" }] });
    expect(m.sources.map((s) => s.title)).toEqual(["A", "B", "C"]);
  });

  it("routes direct answers without a tool label", () => {
    const m = reduceMessage(blank, { type: "router", content: "direct" });
    expect(m.steps[0].label).toBe("Answering directly");
  });
});
