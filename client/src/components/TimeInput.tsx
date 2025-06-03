import '../styles/TimeInput.css'
interface TimeInputProps{
    options: string[]
    selectedOption: string
    customFrom: string
    customTo: string
    onSelectionChange: (value: string) => void
    onFromChange: (value: string) => void
    onToChange: (value: string) => void
}

export function TimeInput({options, selectedOption, customFrom, customTo,
        onSelectionChange, onFromChange, onToChange
}: TimeInputProps) {

   
    return (
    <div className="time-input">
        <div className = "time-dropdown label-and-input">
            <label htmlFor="dropdown" className='dropdown-label'>Time period</label>
            <select
                name="dropdown"
                value={selectedOption}
                onChange={(e) => onSelectionChange(e.target.value)}
                className="dropdown-select">
                    {options.map((opt) =>(
                    <option className="dropdown-values" key={opt} value={opt}>
                        {opt}
                    </option>
                    ))}
            </select>
        </div>

        {selectedOption === "Custom" && (
            <div className="custom-time-amount">
                <label className="dt-label">
                From:&nbsp;
                <input
                    type="datetime-local"
                    value={customFrom}
                    onChange={(e) => onFromChange(e.target.value)}
                    className="dt-input"
                />
                </label>
                <label className="dt-label">
                    To:&nbsp;
                <input
                    type="datetime-local"
                    value={customTo}
                    onChange={(e) => onToChange(e.target.value)}
                    className="dt-input"
                    />
                </label>
            </div>
        )}
   </div>)
}