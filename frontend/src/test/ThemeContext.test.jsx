import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../context/ThemeContext';

// Helper component to test theme
function ThemeTestConsumer() {
  const { theme, toggleTheme, setTheme } = useTheme();
  return (
    <div>
      <span data-testid="theme-value">{theme}</span>
      <button data-testid="toggle-btn" onClick={toggleTheme}>Toggle</button>
      <button data-testid="set-light-btn" onClick={() => setTheme('light')}>Light</button>
      <button data-testid="set-dark-btn" onClick={() => setTheme('dark')}>Dark</button>
    </div>
  );
}

function renderWithTheme(ui, options) {
  return render(<ThemeProvider>{ui}</ThemeProvider>, options);
}

describe('ThemeContext', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
  });

  it('defaults to dark theme when no localStorage value', () => {
    renderWithTheme(<ThemeTestConsumer />);
    expect(screen.getByTestId('theme-value').textContent).toBe('dark');
  });

  it('reads theme from localStorage on mount', () => {
    localStorage.setItem('gymtrac_theme', 'light');
    renderWithTheme(<ThemeTestConsumer />);
    expect(screen.getByTestId('theme-value').textContent).toBe('light');
  });

  it('toggles theme from dark to light', () => {
    renderWithTheme(<ThemeTestConsumer />);
    expect(screen.getByTestId('theme-value').textContent).toBe('dark');
    fireEvent.click(screen.getByTestId('toggle-btn'));
    expect(screen.getByTestId('theme-value').textContent).toBe('light');
  });

  it('toggles theme from light to dark', () => {
    localStorage.setItem('gymtrac_theme', 'light');
    renderWithTheme(<ThemeTestConsumer />);
    expect(screen.getByTestId('theme-value').textContent).toBe('light');
    fireEvent.click(screen.getByTestId('toggle-btn'));
    expect(screen.getByTestId('theme-value').textContent).toBe('dark');
  });

  it('sets theme to light via setTheme', () => {
    renderWithTheme(<ThemeTestConsumer />);
    fireEvent.click(screen.getByTestId('set-light-btn'));
    expect(screen.getByTestId('theme-value').textContent).toBe('light');
  });

  it('sets theme to dark via setTheme', () => {
    localStorage.setItem('gymtrac_theme', 'light');
    renderWithTheme(<ThemeTestConsumer />);
    fireEvent.click(screen.getByTestId('set-dark-btn'));
    expect(screen.getByTestId('theme-value').textContent).toBe('dark');
  });

  it('persists theme to localStorage', () => {
    renderWithTheme(<ThemeTestConsumer />);
    fireEvent.click(screen.getByTestId('toggle-btn'));
    expect(localStorage.getItem('gymtrac_theme')).toBe('light');
  });

  it('sets data-theme attribute on document element', () => {
    renderWithTheme(<ThemeTestConsumer />);
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    fireEvent.click(screen.getByTestId('toggle-btn'));
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
  });
});
