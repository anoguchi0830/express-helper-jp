import React, { useState } from 'react';

export default function SearchBar({ value, onChange, placeholder }) {
  const [focused, setFocused] = useState(false);

  return (
    <div style={styles.wrap}>
      <div style={styles.inputWrap}>
        <span style={styles.searchIcon}>🔍</span>
        <input
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          style={{
            ...styles.input,
            ...(focused ? styles.inputFocused : {})
          }}
        />
        {value && (
          <button style={styles.clearBtn} onClick={() => onChange('')}>✕</button>
        )}
      </div>
    </div>
  );
}

const styles = {
  wrap: {
    padding: '12px 16px',
    backgroundColor: '#F5F7FA',
    borderBottom: '1px solid #E0E0E0'
  },
  inputWrap: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center'
  },
  searchIcon: {
    position: 'absolute',
    left: '12px',
    fontSize: '14px',
    pointerEvents: 'none',
    zIndex: 1
  },
  input: {
    width: '100%',
    padding: '10px 36px 10px 36px',
    fontSize: '14px',
    border: '2px solid #E0E0E0',
    borderRadius: '8px',
    boxSizing: 'border-box',
    outline: 'none',
    fontFamily: 'inherit',
    backgroundColor: '#FFFFFF',
    transition: 'border-color 0.18s, box-shadow 0.18s'
  },
  inputFocused: {
    borderColor: '#5258E4',
    boxShadow: '0 0 0 3px rgba(82, 88, 228, 0.12)'
  },
  clearBtn: {
    position: 'absolute',
    right: '10px',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    color: '#999',
    fontSize: '13px',
    padding: '4px',
    lineHeight: 1
  }
};
