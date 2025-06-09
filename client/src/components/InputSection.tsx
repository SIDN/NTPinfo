import '../styles/InputSection.css'
import React, { useState } from 'react';

interface InputProps {
    onClick: (query: string) => void;
    loading: boolean;
}

const InputSection: React.FC<InputProps> = ({ onClick, loading }) => {
    const [query, setQuery] = useState('');
    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setQuery(event.target.value);
    };

    const handleClick = () => {
        onClick(query.trim());
    };

    return (
        <div className="input-section">
            <div className="input-bar-text">
                <p>
                    Enter the domain name or IP address of the NTP server you want to measure.
                </p>
            </div>
            <div className="input-bar">
                <input
                    type="text"
                    value={query}
                    onChange={handleInputChange}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") {handleClick()}
                      }}
                    placeholder="time.google.com"
                />
                <button onClick={handleClick} disabled={!query.trim() || loading}>
                    Measure
                </button>
            </div>

        </div>
    );

};

export default InputSection;
