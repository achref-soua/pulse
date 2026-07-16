import { cn } from "@pulse/ui";

/** The Pulse mark: an ECG waveform (signature pulse-red) + a wordmark that
 *  inherits the surrounding text colour, so it reads on light and dark alike. */
export function PulseLogo({
  className,
  showWordmark = true,
}: {
  className?: string;
  showWordmark?: boolean;
}) {
  return (
    <svg
      viewBox={showWordmark ? "0 0 220 56" : "0 0 48 56"}
      fill="none"
      role="img"
      aria-label="Pulse"
      className={cn("h-7 w-auto text-foreground", className)}
      xmlns="http://www.w3.org/2000/svg"
    >
      <polyline
        points="0,28 10,28 15,28 19,12 23,44 27,8 31,40 35,28 45,28"
        stroke="#e11d48"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {showWordmark && (
        <>
          <line x1="57" y1="10" x2="57" y2="46" stroke="currentColor" strokeWidth="1.5" opacity="0.25" />
          <text
            x="67"
            y="40"
            fontFamily="var(--font-sans), system-ui, sans-serif"
            fontSize="32"
            fontWeight="700"
            letterSpacing="-1.5"
            fill="currentColor"
          >
            Pulse
          </text>
        </>
      )}
    </svg>
  );
}
