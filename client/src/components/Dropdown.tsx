import React from "react";

interface DropdownProps {
    label: string;
    options: string[];
    selectedValue: string;
    onSelect: (value: string) => void;
    className: string;
}

const Dropdown: React.FC<DropdownProps> = ({label, options, selectedValue, onSelect, className}) => {
    return (
        <div className = {className}>
            <label className="dropdown-label">{label}</label>
            <select
            value={selectedValue}
            onChange={(e) => onSelect(e.target.value)}
            className="dropdown-select">
                {options.map((opt) =>(
                    <option className="dropdown-values" key={opt} value={opt}>
                        {opt}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default Dropdown;