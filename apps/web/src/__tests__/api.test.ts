import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// Isolate the module from the real fetch
const mockFetch = vi.fn();

describe("api client", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", mockFetch);
    vi.stubGlobal("localStorage", {
      getItem: vi.fn().mockReturnValue("test-token"),
      removeItem: vi.fn(),
      setItem: vi.fn(),
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("attaches Authorization header when token exists", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ id: "1" }),
    });

    const { api } = await import("@/lib/api");
    await api.get("/patients");

    const [, opts] = mockFetch.mock.calls[0] as [string, RequestInit];
    const headers = opts.headers as Record<string, string>;
    expect(headers["Authorization"]).toBe("Bearer test-token");
  });

  it("GET calls the correct URL", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => [],
    });

    const { api } = await import("@/lib/api");
    await api.get("/patients?limit=10");

    const [url] = mockFetch.mock.calls[0] as [string];
    expect(url).toContain("/patients?limit=10");
  });

  it("POST sends JSON body with correct method", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ access_token: "tok" }),
    });

    const { api } = await import("@/lib/api");
    await api.post("/auth/login", { email: "a@b.com", password: "s" });

    const [, opts] = mockFetch.mock.calls[0] as [string, RequestInit];
    expect(opts.method).toBe("POST");
    expect(JSON.parse(opts.body as string)).toMatchObject({ email: "a@b.com" });
  });

  it("throws on non-ok response with detail message", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 422,
      json: async () => ({ detail: "Validation error" }),
    });

    const { api } = await import("@/lib/api");
    await expect(api.get("/patients")).rejects.toThrow("Validation error");
  });
});
