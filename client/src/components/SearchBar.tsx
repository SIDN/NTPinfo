import '../styles/SearchBar.css'
import React, { useState } from 'react';

interface SearchBarProps {
    onSearch: (query: string, jitterFlag: boolean, measurementsNo: number) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
    const [query, setQuery] = useState('');
    const [jitterFlag, setJitterFlag] = useState(false);
    const [measurementsNo, setMeasurementsNo] = useState(1);

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setQuery(event.target.value);
    };

    const handleSearch = () => {
        onSearch(query, jitterFlag, measurementsNo);
    };

    return (
        <div className="search-section">
            <div className="search-bar-text">
                <p>
                    Enter the domain name or IP address of the NTP server you want to measure.
                </p>
            </div>
            <div className="search-bar">
                <input
                    type="text"
                    value={query}
                    onChange={handleInputChange}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") {handleSearch()}
                      }}
                    placeholder="time.google.com"
                />
                <button onClick={handleSearch}>
                    Measure
                </button>
            </div>
            <form className="jitter-options" onSubmit={(e) => e.preventDefault()}>
                <input
                    type="checkbox"
                    id="jitter-check"
                    checked={jitterFlag}
                    onChange={(e) => setJitterFlag(e.target.checked)}
                />
                <label htmlFor="jitter-check"> Perform extra measurements to calculate jitter (max. 10) </label>

                 {jitterFlag && (<input
                    id="measurements-no-box"
                    type="number"
                    min={1}
                    max={10}
                    value={measurementsNo}
                    onChange={(e) => setMeasurementsNo(Math.min(10, Number(e.target.value.replace(/^0+/, ''))))}
                    className="jitter-count-input"
                />)}
            </form>
        </div>
    );

};

export default SearchBar;
