import { useState, useRef} from "react";
import '../styles/Popup.css'
import { NTPData } from "../utils/types.ts";
import LineChart from "./LineGraph";
import { Measurement } from "../utils/types.ts";
import { TimeInput } from "./TimeInput.tsx";

interface DropdownConfig {
    options: string[];
    selectedValue: string;
    onSelect: (value: string) => void;
}

interface PopupDropdownProps{
    isOpen: boolean
    onClose: () => void
    dropdown: DropdownConfig
    data: Map<string, NTPData[]> | null
}

export default function VisualizationPopup({isOpen, onClose, dropdown, data}: PopupDropdownProps ) {
    const popupRef = useRef(null)

    const [selMeasurement, setSelMeasurement] = useState<Measurement>("RTT")
    const [selOption, setSelOption] = useState("Last Day")

    // “from” & “to” values for custom range
    const [customFrom, setCustomFrom] = useState<string>("")
    const [customTo,   setCustomTo]   = useState<string>("")

    const handleMeasurementChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelMeasurement(event.target.value as Measurement);
      };

    if (!isOpen) return null;

    return (
        <div ref = {popupRef} className="visualization-popup">
            <div className="popup-content">
                {/*button for closing the popup*/}
                <button className="close-btn" onClick={onClose}>X</button>
                <div className="form-row">
                    {/*Dropdown for the base time duration options*/}
                    <TimeInput
                        options = {dropdown.options}
                        selectedOption={selOption}
                        onSelectionChange={setSelOption}
                        customFrom={customFrom}
                        customTo={customTo}
                        onFromChange={setCustomFrom}
                        onToChange={setCustomTo}
                    />
                  
                    <div className="radio-group">
                        {/*Radio for showing offset data*/}
                        <label className="radio-measurement-label">
                            <input
                                type="radio"
                                name="measurement-popup"
                                value="offset"
                                checked={selMeasurement === "offset"}
                                onChange={handleMeasurementChange}
                            />
                            Offset
                        </label>
                        {/*Radio for showing delay data*/}
                        <label className="radio-measurement-label">
                            <input
                                type="radio"
                                name="measurement-popup"
                                value="RTT"
                                checked={selMeasurement === "RTT"}
                                onChange={handleMeasurementChange}
                            />
                            Round-trip time
                        </label>
                    </div>
                </div>
                <div className="chart-box">
                    <LineChart
                        data={data}
                        selectedMeasurement={selMeasurement}
                        selectedOption={selOption}
                        customRange={{ from: customFrom, to: customTo }}
                    />
                </div>
            </div>
        </div>
    );
};