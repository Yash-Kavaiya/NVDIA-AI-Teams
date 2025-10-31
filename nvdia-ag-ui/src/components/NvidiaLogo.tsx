export function NvidiaLogo({ className = "w-32 h-8" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 200 50"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* NVIDIA Logo SVG */}
      <g>
        {/* Green accent bar */}
        <rect x="0" y="15" width="4" height="20" fill="#76B900" />
        
        {/* NVIDIA text */}
        <text
          x="12"
          y="35"
          fontFamily="Arial, sans-serif"
          fontSize="28"
          fontWeight="bold"
          fill="currentColor"
          letterSpacing="-1"
        >
          NVIDIA
        </text>
        
        {/* Eye symbol */}
        <circle cx="165" cy="25" r="8" fill="none" stroke="#76B900" strokeWidth="2" />
        <circle cx="165" cy="25" r="3" fill="#76B900" />
      </g>
    </svg>
  );
}
