/**
 * Centralized Color Theme - Darker Shades
 * 
 * Replaces bright colors with darker, more professional shades
 */

export const colors = {
  // Primary colors - darker shades
  blue: '#1e5f8c',        // Darker blue (was #3498db)
  green: '#1e7e45',       // Darker green (was #2ecc71)
  red: '#a93226',         // Darker red (was #e74c3c)
  orange: '#c77c11',      // Darker orange (was #f39c12)
  purple: '#6c3483',      // Darker purple (was #9b59b6)
  teal: '#117864',        // Darker teal (was #1abc9c)
  
  // Additional darker colors
  darkBlue: '#16425b',
  darkGreen: '#155724',
  darkRed: '#7b241c',
  darkOrange: '#9c640c',
  
  // Semantic colors
  success: '#1e7e45',     // Darker green
  warning: '#c77c11',     // Darker orange
  error: '#a93226',       // Darker red
  info: '#1e5f8c',        // Darker blue
  
  // Grays
  gray: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#eeeeee',
    300: '#e0e0e0',
    400: '#bdbdbd',
    500: '#9e9e9e',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
  },
  
  // Text colors
  text: {
    primary: '#2c3e50',
    secondary: '#5d6d7e',
    disabled: '#95a5a6',
  },
  
  // Background colors with opacity
  backgrounds: {
    blue: '#1e5f8c15',
    green: '#1e7e4515',
    red: '#a9322615',
    orange: '#c77c1115',
    purple: '#6c348315',
    teal: '#11786415',
  }
};

// Legacy color mappings for backward compatibility
export const legacyColors = {
  '#3498db': colors.blue,
  '#2ecc71': colors.green,
  '#e74c3c': colors.red,
  '#f39c12': colors.orange,
  '#9b59b6': colors.purple,
  '#1abc9c': colors.teal,
};
