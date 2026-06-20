import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RiskBadge, news2ToRiskLevel, responseToRiskLevel } from "@/components/ui/RiskBadge";

describe("RiskBadge", () => {
  it("renders default label for each level", () => {
    const { rerender } = render(<RiskBadge level="low" />);
    expect(screen.getByText("Low")).toBeTruthy();

    rerender(<RiskBadge level="medium" />);
    expect(screen.getByText("Medium")).toBeTruthy();

    rerender(<RiskBadge level="high" />);
    expect(screen.getByText("High")).toBeTruthy();

    rerender(<RiskBadge level="critical" />);
    expect(screen.getByText("Critical")).toBeTruthy();
  });

  it("renders custom label when provided", () => {
    render(<RiskBadge level="high" label="Elevated" />);
    expect(screen.getByText("Elevated")).toBeTruthy();
  });

  it("applies the correct colour class for each level", () => {
    const { rerender, container } = render(<RiskBadge level="low" />);
    expect(container.firstChild?.toString()).toBeTruthy();
    const span = () => container.querySelector("span")!;

    rerender(<RiskBadge level="low" />);
    expect(span().className).toContain("emerald");

    rerender(<RiskBadge level="medium" />);
    expect(span().className).toContain("amber");

    rerender(<RiskBadge level="high" />);
    expect(span().className).toContain("orange");

    rerender(<RiskBadge level="critical" />);
    expect(span().className).toContain("rose");
  });
});

describe("news2ToRiskLevel", () => {
  it("maps score 0 → low", () => expect(news2ToRiskLevel(0)).toBe("low"));
  it("maps score 1 → medium", () => expect(news2ToRiskLevel(1)).toBe("medium"));
  it("maps score 4 → medium", () => expect(news2ToRiskLevel(4)).toBe("medium"));
  it("maps score 5 → high", () => expect(news2ToRiskLevel(5)).toBe("high"));
  it("maps score 6 → high", () => expect(news2ToRiskLevel(6)).toBe("high"));
  it("maps score 7 → critical", () => expect(news2ToRiskLevel(7)).toBe("critical"));
  it("maps score 12 → critical", () => expect(news2ToRiskLevel(12)).toBe("critical"));
});

describe("responseToRiskLevel", () => {
  it('maps "High" → critical', () => expect(responseToRiskLevel("High")).toBe("critical"));
  it('maps "Medium" → high', () => expect(responseToRiskLevel("Medium")).toBe("high"));
  it('maps anything else → low', () => expect(responseToRiskLevel("Low")).toBe("low"));
});
