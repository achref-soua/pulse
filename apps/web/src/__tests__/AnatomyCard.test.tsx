import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { AnatomyCard } from "@/components/ui/AnatomyCard";

const baseProps = {
  aneurysmType: "AAA",
  location: "Infrarenal",
  maxDiameterMm: 50,
  neckLengthMm: 20,
  neckAngulationDeg: 30,
  neckDiameterMm: 22,
  iliacAccessMinMm: 7,
  iliacAccessMaxMm: 9,
  tortuosity: "Moderate",
  ctScanDate: "2024-03-01",
};

describe("AnatomyCard", () => {
  it("renders the section heading", () => {
    render(<AnatomyCard {...baseProps} />);
    expect(screen.getByText("Aortic Anatomy")).toBeTruthy();
  });

  it("displays all field values", () => {
    render(<AnatomyCard {...baseProps} />);
    expect(screen.getByText("AAA")).toBeTruthy();
    expect(screen.getByText("Infrarenal")).toBeTruthy();
    expect(screen.getByText("50")).toBeTruthy();
    expect(screen.getByText("Moderate")).toBeTruthy();
    expect(screen.getByText("2024-03-01")).toBeTruthy();
  });

  it("shows N/A for null fields", () => {
    render(
      <AnatomyCard
        {...baseProps}
        aneurysmType={null}
        location={null}
        ctScanDate={null}
      />
    );
    const nas = screen.getAllByText("N/A");
    expect(nas.length).toBeGreaterThanOrEqual(3);
  });

  it("highlights max diameter ≥ 55mm in amber", () => {
    render(<AnatomyCard {...baseProps} maxDiameterMm={60} />);
    const diameter = screen.getByText("60");
    expect(diameter.className).toContain("amber");
  });

  it("does not highlight max diameter < 55mm", () => {
    render(<AnatomyCard {...baseProps} maxDiameterMm={54} />);
    const diameter = screen.getByText("54");
    expect(diameter.className).not.toContain("amber");
  });

  it("highlights neck angulation > 60° in amber", () => {
    render(<AnatomyCard {...baseProps} neckAngulationDeg={75} />);
    const ang = screen.getByText("75");
    expect(ang.className).toContain("amber");
  });

  it("does not highlight neck angulation ≤ 60°", () => {
    render(<AnatomyCard {...baseProps} neckAngulationDeg={60} />);
    const ang = screen.getByText("60");
    expect(ang.className).not.toContain("amber");
  });

  it("renders unit labels for numeric fields", () => {
    render(<AnatomyCard {...baseProps} />);
    const mms = screen.getAllByText("mm");
    expect(mms.length).toBeGreaterThanOrEqual(5);
  });
});
