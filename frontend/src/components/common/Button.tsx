import React from 'react';
import classNames from 'classnames';
import '../styles/Button.css';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  children: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      disabled = false,
      loading = false,
      fullWidth = false,
      onClick,
      type = 'button',
      children,
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || loading}
        onClick={onClick}
        className={classNames('btn', `btn-${variant}`, `btn-${size}`, {
          'btn-full-width': fullWidth,
          'btn-loading': loading,
        })}
      >
        {loading ? <span className="spinner"></span> : null}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
export default Button;