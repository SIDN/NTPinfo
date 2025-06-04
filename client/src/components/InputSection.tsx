import '../styles/InputSection.css'
import React, { useState } from 'react';

interface InputProps {
    onClick: (query: string, jitterFlag: boolean, measurementsNo: number) => void;
    loading: boolean;
}

const InputSection: React.FC<InputProps> = ({ onClick, loading }) => {
    const [query, setQuery] = useState('');
    const [jitterFlag, setJitterFlag] = useState(false);
    const [measurementsNo, setMeasurementsNo] = useState(1);

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setQuery(event.target.value);
    };

    const handleClick = () => {
        onClick(query.trim(), jitterFlag, measurementsNo);
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
            <form className="jitter-options" onSubmit={(e) => e.preventDefault()}>
                <label className="custom-checkbox">
                    <input type="checkbox"
                           id="jitter-check"
                           checked={jitterFlag}
                           onChange={(e) => setJitterFlag(e.target.checked)}
                />
                <span className="checkmark"></span>
                    Perform extra measurements to calculate jitter
                </label>

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

export default InputSection;
