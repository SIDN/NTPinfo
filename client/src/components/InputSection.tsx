import '../styles/InputSection.css'
import React, { useState } from 'react';
import { RipeStatus } from '../utils/types';

interface InputProps {
    onClick: (query: string, useIPv6: boolean) => void;
    loading: boolean;
    ipv6Selected: boolean;
    onIPv6Toggle: (value: boolean) => void;
    ripeMeasurementStatus?: RipeStatus | null;
    measurementSessionActive?: boolean;
}

const InputSection: React.FC<InputProps> = ({ onClick, loading, ipv6Selected, onIPv6Toggle, ripeMeasurementStatus, measurementSessionActive }) => {
    const [query, setQuery] = useState('');
    const useIPv6 = ipv6Selected;

    // Check if any measurement is in progress
    const isMeasurementInProgress = (loading ||
        ripeMeasurementStatus === "pending" ||
        ripeMeasurementStatus === "partial_results") && measurementSessionActive;

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
                    Enter the NTP server you want to evaluate (IP or domain name).
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
                        disabled={isMeasurementInProgress}
                    />
                    <button onClick={handleClick} disabled={!query.trim() || isMeasurementInProgress}>
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
                        disabled={isMeasurementInProgress}
                    />
                    <label htmlFor="ipv4">IPv4</label>

                    <input
                        type="radio"
                        name="ip-version"
                        id="ipv6"
                        checked={useIPv6}
                        onChange={() => onIPv6Toggle(true)}
                        disabled={isMeasurementInProgress}
                    />
                    <label htmlFor="ipv6">IPv6</label>
                </form>
            </div>
        </div>
    );

};

export default InputSection
