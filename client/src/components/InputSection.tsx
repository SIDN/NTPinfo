import '../styles/InputSection.css'
import React, { useState } from 'react';

interface InputProps {
    onClick: (query: string, useIPv6: boolean) => void;
    loading: boolean;
    ipv6Selected: boolean;
    onIPv6Toggle: (value: boolean) => void;
}

const InputSection: React.FC<InputProps> = ({ onClick, loading, ipv6Selected, onIPv6Toggle }) => {
    const [query, setQuery] = useState('');
    const useIPv6 = ipv6Selected;
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
                <p className="measure-text">Measure using: </p>
                <form className="ip-options" onSubmit={(e) => e.preventDefault()}>
                    <input
                        type="radio"
                        name="ip-version"
                        id="ipv4"
                        checked={!useIPv6}
                        onChange={() => onIPv6Toggle(false)}
                    />
                    <label htmlFor="ipv4">IPv4</label>

                    <input
                        type="radio"
                        name="ip-version"
                        id="ipv6"
                        checked={useIPv6}
                        onChange={() => onIPv6Toggle(true)}
                    />
                    <label htmlFor="ipv6">IPv6</label>
                </form>
            </div>
        </div>
    );

};

export default InputSection
