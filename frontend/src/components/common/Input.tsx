import React from 'react';
import classNames from 'classnames';
import '../styles/Input.css';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      fullWidth = false,
      icon,
      className,
      ...props
    },
    ref
  ) => {
    return (
      <div className={classNames('input-group', { 'input-full-width': fullWidth })}>
        {label && <label className="input-label">{label}</label>}
        <div className={classNames('input-wrapper', { 'input-with-icon': icon })}>
          {icon && <div className="input-icon">{icon}</div>}
          <input
            ref={ref}
            className={classNames('input', className, {
              'input-error': error,
            })}
            {...props}
          />
        </div>
        {error && <span className="input-error-text">{error}</span>}
        {helperText && <span className="input-helper-text">{helperText}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';
export default Input;