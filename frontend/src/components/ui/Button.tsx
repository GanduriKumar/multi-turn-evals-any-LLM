import React from 'react'
import { Link, type To } from 'react-router-dom'

type Variant = 'primary' | 'secondary' | 'outline' | 'danger'
type Size = 'sm' | 'md' | 'lg'

function cx(...classes: Array<string | undefined | false>) {
  return classes.filter(Boolean).join(' ')
}

function variantClasses(variant: Variant) {
  switch (variant) {
    case 'primary':
      return 'bg-brand-500 text-white hover:bg-brand-600 shadow-sm'
    case 'secondary':
      return 'bg-slate-800 text-white hover:bg-slate-900 shadow-sm'
    case 'outline':
      return 'border border-slate-300 text-slate-700 bg-white hover:bg-slate-50'
    case 'danger':
      // Outline-style danger to match design image (Abort button)
      return 'border border-red-300 text-red-600 bg-white hover:bg-red-50'
    default:
      return ''
  }
}

function sizeClasses(size: Size) {
  switch (size) {
    case 'sm':
      return 'px-3 py-1.5 text-sm rounded-md'
    case 'md':
      return 'px-3.5 py-2 rounded-md'
    case 'lg':
      return 'px-5 py-2.5 text-lg rounded-md'
    default:
      return 'px-3.5 py-2 rounded-md'
  }
}

type BaseProps = {
  children: React.ReactNode
  className?: string
  variant?: Variant
  size?: Size
  'data-testid'?: string
}

type ButtonAsButton = BaseProps & React.ButtonHTMLAttributes<HTMLButtonElement> & {
  to?: undefined
  href?: undefined
}

type ButtonAsLink = BaseProps & {
  to: To
  href?: undefined
  onClick?: React.MouseEventHandler<HTMLAnchorElement>
}

type ButtonAsAnchor = BaseProps & React.AnchorHTMLAttributes<HTMLAnchorElement> & {
  href: string
  to?: undefined
}

export type ButtonProps = ButtonAsButton | ButtonAsLink | ButtonAsAnchor

export default function Button(props: ButtonProps) {
  const { children, className, variant = 'outline', size = 'md' } = props
  const classes = cx(
    variantClasses(variant),
    sizeClasses(size),
    'disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500/30',
    className,
  )

  if ('to' in props && props.to) {
    const { to, onClick, ...rest } = props as ButtonAsLink
    return (
      <Link to={to} onClick={onClick as any} className={classes} {...(rest as any)}>
        {children}
      </Link>
    )
  }

  if ('href' in props && props.href) {
    const { href, ...rest } = props as ButtonAsAnchor
    return (
      <a href={href} className={classes} {...(rest as any)}>
        {children}
      </a>
    )
  }

  const { type = 'button', ...rest } = props as ButtonAsButton
  return (
    <button type={type} className={classes} {...rest}>
      {children}
    </button>
  )
}
