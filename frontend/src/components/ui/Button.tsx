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
      return 'bg-blue-600 text-white hover:bg-blue-700'
    case 'secondary':
      return 'bg-gray-800 text-white hover:bg-gray-900'
    case 'outline':
      return 'border border-gray-300 hover:bg-gray-50'
    case 'danger':
      return 'bg-red-600 text-white hover:bg-red-700'
    default:
      return ''
  }
}

function sizeClasses(size: Size) {
  switch (size) {
    case 'sm':
      return 'px-2 py-1 text-sm rounded'
    case 'md':
      return 'px-3 py-2 rounded'
    case 'lg':
      return 'px-4 py-2 text-lg rounded'
    default:
      return 'px-3 py-2 rounded'
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
  const classes = cx(variantClasses(variant), sizeClasses(size), 'disabled:opacity-50', className)

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
