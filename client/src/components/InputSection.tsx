import '../styles/InputSection.css'
import React, { useState } from 'react';

interface InputProps {
    onClick: (query: string, useIPv6: boolean) => void;
    loading: boolean;
}

const InputSection: React.FC<InputProps> = ({ onClick, loading }) => {
    const [query, setQuery] = useState('');
    const [useIPv6, setUseIPv6] = useState(false)
    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setQuery(event.target.value);
    };

    const handleClick = () => {
        onClick(query.trim(), useIPv6);
    };

    return (
        <div className="input-section">
            <div className="input-bar-text">
                <p>
                    Enter the domain name or IP address of the NTP server you want to measure.
                </p>
            </div>
            <div className="input-and-options">
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
                <form className="ip-options" onSubmit={(e) => e.preventDefault()}>
                <label className="custom-checkbox">
                    <input type="checkbox"
                           id="ipv6-check"
                           checked={useIPv6}
                           onChange={(e) => setUseIPv6(e.target.checked)}
                    />
                    <span className="checkmark"></span>
                        Measure using IPv6
                    </label>
                </form>
            </div>
           

        </div>
    );

};

export default InputSection
