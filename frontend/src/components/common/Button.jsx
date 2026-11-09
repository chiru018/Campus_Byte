import React from 'react';
import './Button.scss';

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  icon: Icon,
  ...props
}) {
  return (
    <button
      className={`btn btn--${variant} btn--${size} ${className}`}
      {...props}
    >
      {Icon && <Icon className="btn__icon" size={size === 'sm' ? 16 : 18} />}
      <span className="btn__text">{children}</span>
    </button>
  );
}
