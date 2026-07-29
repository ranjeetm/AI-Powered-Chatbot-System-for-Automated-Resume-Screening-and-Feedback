"use client"

import type {
  ButtonHTMLAttributes,
  CSSProperties,
  InputHTMLAttributes,
  ReactNode,
  TextareaHTMLAttributes
} from "react"


export const C = {
  bg: "#0b0c10",
  surface: "#13141a",
  surface2: "#1c1d26",
  border: "#252630",
  borderHover: "#353648",
  accent: "#6c63ff",
  accentDim: "rgba(108,99,255,0.15)",
  accentBorder: "rgba(108,99,255,0.4)",
  green: "#2dd4a0",
  greenDim: "rgba(45,212,160,0.12)",
  greenBorder: "rgba(45,212,160,0.35)",
  amber: "#f5a623",
  amberDim: "rgba(245,166,35,0.12)",
  red: "#f0595a",
  redDim: "rgba(240,89,90,0.12)",
  text: "#e4e5f0",
  muted: "#6b6d8a"
} as const


export function scoreColor(
  score: number
) {

  if (score >= 80) {

    return C.green
  }

  if (score >= 60) {

    return C.amber
  }

  return C.red
}


export function scoreBg(
  score: number
) {

  if (score >= 80) {

    return C.greenDim
  }

  if (score >= 60) {

    return C.amberDim
  }

  return C.redDim
}


export function normalizeScore(
  value?: number
) {

  if (!value) {

    return 0
  }

  return value > 1
    ? Math.round(value)
    : Math.round(value * 100)
}


export function Tag({
  children,
  color = C.accent
}: {
  children: ReactNode
  color?: string
}) {

  return (
    <span
      className="inline-flex shrink-0 items-center rounded-full border px-2.5 py-0.5 font-mono text-[11px] leading-5"
      style={{
        background: `${color}18`,
        borderColor: `${color}40`,
        color
      }}
    >
      {children}
    </span>
  )
}


export function ScoreBadge({
  score
}: {
  score: number
}) {

  const normalized = Math.round(score)

  return (
    <span
      className="inline-flex items-center rounded-lg border px-2.5 py-1 font-mono text-[13px] font-bold"
      style={{
        background: scoreBg(normalized),
        borderColor: `${scoreColor(normalized)}50`,
        color: scoreColor(normalized)
      }}
    >
      {normalized}%
    </span>
  )
}


export function ScoreBar({
  value,
  max = 1,
  color
}: {
  value: number
  max?: number
  color?: string
}) {

  const pct = Math.min(
    100,
    Math.max(
      0,
      Math.round((value / max) * 100)
    )
  )
  const activeColor = color || scoreColor(pct)

  return (
    <div
      className="h-1.5 overflow-hidden rounded"
      style={{
        background: C.border
      }}
    >
      <div
        className="h-full rounded transition-[width] duration-500"
        style={{
          width: `${pct}%`,
          background: activeColor
        }}
      />
    </div>
  )
}


type ButtonProps =
  ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: "primary" | "secondary" | "ghost" | "danger" | "success"
    size?: "sm" | "md" | "lg"
  }


export function Button({
  children,
  variant = "primary",
  size = "md",
  className = "",
  style,
  ...props
}: ButtonProps) {

  const variants: Record<string, CSSProperties> = {
    primary: {
      background: C.accent,
      color: "#fff"
    },
    secondary: {
      background: C.surface2,
      borderColor: C.border,
      color: C.text
    },
    ghost: {
      background: "transparent",
      borderColor: C.border,
      color: C.muted
    },
    danger: {
      background: C.redDim,
      borderColor: `${C.red}40`,
      color: C.red
    },
    success: {
      background: C.greenDim,
      borderColor: `${C.green}40`,
      color: C.green
    }
  }

  const sizes = {
    sm: "px-3.5 py-1.5 text-xs",
    md: "px-5 py-2.5 text-[13px]",
    lg: "px-7 py-3.5 text-[15px]"
  }

  return (
    <button
      className={`inline-flex items-center justify-center gap-1.5 rounded-[10px] border border-transparent font-semibold transition duration-150 disabled:cursor-not-allowed disabled:opacity-50 ${sizes[size]} ${className}`}
      style={{
        ...variants[variant],
        ...style
      }}
      {...props}
    >
      {children}
    </button>
  )
}


export function Card({
  children,
  className = "",
  hover = false,
  style,
  ...props
}: {
  children: ReactNode
  className?: string
  hover?: boolean
  style?: CSSProperties
  onClick?: () => void
}) {

  return (
    <div
      className={`rounded-[14px] border px-[22px] py-5 transition duration-200 ${hover ? "cursor-pointer hover:shadow-[0_0_0_1px_rgba(108,99,255,0.4)]" : ""} ${className}`}
      style={{
        background: C.surface,
        borderColor: C.border,
        ...style
      }}
      onMouseEnter={(event) => {
        if (hover) {

          event.currentTarget.style.borderColor = C.accentBorder
        }
      }}
      onMouseLeave={(event) => {
        if (hover) {

          event.currentTarget.style.borderColor = C.border
        }
      }}
      {...props}
    >
      {children}
    </div>
  )
}


export function Input({
  className = "",
  style,
  ...props
}: InputHTMLAttributes<HTMLInputElement>) {

  return (
    <input
      className={`w-full rounded-[10px] border px-3.5 py-2.5 text-[13px] outline-none transition placeholder:text-[#6b6d8a] focus:border-[#6c63ff] ${className}`}
      style={{
        background: C.surface2,
        borderColor: C.border,
        color: C.text,
        ...style
      }}
      {...props}
    />
  )
}


export function Textarea({
  className = "",
  style,
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement>) {

  return (
    <textarea
      className={`w-full resize-y rounded-[10px] border px-3.5 py-3 text-[13px] leading-6 outline-none transition placeholder:text-[#6b6d8a] focus:border-[#6c63ff] ${className}`}
      style={{
        background: C.surface2,
        borderColor: C.border,
        color: C.text,
        ...style
      }}
      {...props}
    />
  )
}


export function Select({
  children,
  className = "",
  style,
  ...props
}: InputHTMLAttributes<HTMLSelectElement> & {
  children: ReactNode
}) {

  return (
    <select
      className={`w-full rounded-[10px] border px-3.5 py-2.5 text-[13px] outline-none transition focus:border-[#6c63ff] ${className}`}
      style={{
        background: C.surface2,
        borderColor: C.border,
        color: C.text,
        ...style
      }}
      {...props}
    >
      {children}
    </select>
  )
}


export function Modal({
  open,
  onClose,
  title,
  width = 700,
  children
}: {
  open: boolean
  onClose: () => void
  title: ReactNode
  width?: number
  children: ReactNode
}) {

  if (!open) {

    return null
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-6"
      onClick={onClose}
    >
      <div
        className="max-h-[88vh] w-full overflow-y-auto rounded-[18px] border px-7 py-6 shadow-2xl"
        style={{
          maxWidth: width,
          background: C.surface,
          borderColor: C.border
        }}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-5 flex items-center justify-between gap-4">
          <div
            className="text-lg font-bold"
            style={{
              color: C.text
            }}
          >
            {title}
          </div>

          <button
            className="text-xl transition hover:text-white"
            style={{
              color: C.muted
            }}
            onClick={onClose}
            type="button"
          >
            x
          </button>
        </div>

        {children}
      </div>
    </div>
  )
}


export function Eyebrow({
  children,
  color = C.accent
}: {
  children: ReactNode
  color?: string
}) {

  return (
    <div
      className="mb-1.5 font-mono text-[10px] uppercase tracking-[0.3em]"
      style={{
        color
      }}
    >
      {children}
    </div>
  )
}


export function FieldLabel({
  children
}: {
  children: ReactNode
}) {

  return (
    <label
      className="mb-2 block font-mono text-[11px] uppercase tracking-[0.1em]"
      style={{
        color: C.muted
      }}
    >
      {children}
    </label>
  )
}


export function Stat({
  label,
  value,
  sub,
  color = C.accent
}: {
  label: ReactNode
  value: ReactNode
  sub?: ReactNode
  color?: string
}) {

  return (
    <div
      className="rounded-xl border px-4 py-3.5"
      style={{
        background: C.surface2,
        borderColor: C.border
      }}
    >
      <div
        className="mb-1.5 font-mono text-[11px] uppercase tracking-[0.1em]"
        style={{
          color: C.muted
        }}
      >
        {label}
      </div>

      <div
        className="font-mono text-[26px] font-bold leading-tight"
        style={{
          color
        }}
      >
        {value}
      </div>

      {sub ? (
        <div
          className="mt-1 text-[11px]"
          style={{
            color: C.muted
          }}
        >
          {sub}
        </div>
      ) : null}
    </div>
  )
}


export function EmptyState({
  title,
  children
}: {
  title: string
  children: ReactNode
}) {

  return (
    <Card className="flex min-h-52 flex-col items-center justify-center text-center">
      <div
        className="mb-2 text-lg font-bold"
        style={{
          color: C.text
        }}
      >
        {title}
      </div>

      <div
        className="max-w-md text-sm leading-6"
        style={{
          color: C.muted
        }}
      >
        {children}
      </div>
    </Card>
  )
}
