import React from 'react';
import { Search } from '@swc-react/search';

export default function SearchBar({ value, onChange, placeholder }) {
  return (
    <div style={styles.wrap}>
      <Search
        value={value}
        placeholder={placeholder}
        style={{ width: '100%' }}
        onInput={(e) => onChange(e.target.value || '')}
        onSubmit={(e) => e.preventDefault()}
      />
    </div>
  );
}

const styles = {
  wrap: {
    padding: '10px 16px',
    backgroundColor: 'var(--spectrum-gray-100, #F5F7FA)',
    borderBottom: '1px solid var(--spectrum-gray-300, #E0E0E0)'
  }
};
