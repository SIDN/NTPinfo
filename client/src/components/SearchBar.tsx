import '../styles/SearchBar.css'
import React, { useState } from 'react';

interface SearchBarProps {
    onSearch: (query: string) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
    const [query, setQuery] = useState('');

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setQuery(event.target.value);
    };

    const handleSearch = () => {
        onSearch(query);
    };

    return (
        <>
            <div className = "search-bar-text">
                <p>
                    Enter the domanin name or IP address of the NTP server you want to measure.
                </p>
            </div>
            <div className="search-bar">
                <input
                    type="text"
                    value={query}
                    onChange={handleInputChange}
                    placeholder="time.google.com"
                />
                <button onClick={handleSearch}>
                    Measure
                </button>
            </div>
        </>
    );
};

export default SearchBar;
