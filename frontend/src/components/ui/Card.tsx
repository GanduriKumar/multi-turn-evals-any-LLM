import React from 'react'

type DivProps = React.HTMLAttributes<HTMLDivElement>

export function Card({ children, className = '', ...rest }: { children: React.ReactNode; className?: string } & DivProps) {
  return <div className={`bg-white border border-slate-200 rounded-xl shadow-sm ${className}`} {...rest}>{children}</div>
}

export function CardHeader({ children, className = '', ...rest }: { children: React.ReactNode; className?: string } & DivProps) {
  return <div className={`px-4 pt-4 ${className}`} {...rest}>{children}</div>
}

export function CardTitle({ children, className = '', ...rest }: { children: React.ReactNode; className?: string } & React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={`font-semibold text-slate-800 ${className}`} {...rest}>{children}</h3>
}

export function CardContent({ children, className = '', ...rest }: { children: React.ReactNode; className?: string } & DivProps) {
  return <div className={`px-4 pb-4 ${className}`} {...rest}>{children}</div>
}
