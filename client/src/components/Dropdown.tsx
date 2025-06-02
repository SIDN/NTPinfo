import React from "react";

/**
 * Interface containing all data which should be sent to the custom dropdown
 */
interface DropdownProps {
    label: string;
    options: string[];
    selectedValue: string;
    onSelect: (value: string) => void;
    className: string;
}

/**
 * Custom component for creating a dropdown menu with all the data necessary
 * @param label name of the dropdown
 * @param options list of options which should appear in the dropdown
 * @param selectedValue default value which should be chosed when the dropdown first appears
 * @param onSelect function given for changing states where the dropdown is used
 * @param className class name to be given to this specific dropdown
 * @returns 
 */
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