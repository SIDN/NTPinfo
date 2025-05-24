import { useState, useRef} from "react";
import Dropdown from "./Dropdown";
import '../styles/Popup.css'
import { NTPData } from "../utils/types.ts";
import LineChart from "./LineGraph";
import { Measurement } from "../utils/types.ts";

interface DropdownConfig {
    label: string;
    options: string[];
    selectedValue: string;
    onSelect: (value: string) => void;
    className: string;
}

interface PopupDropdownProps{
    isOpen: boolean
    onClose: () => void
    dropdowns: DropdownConfig[]
    data: NTPData[] | null
}

export default function VisualizationPopup({isOpen, onClose, dropdowns, data}: PopupDropdownProps ) {
    const popupRef = useRef(null)

    const [textVal, setTextVal] = useState("")
    const [selMeasurement, setSelMeasurement] = useState<Measurement>("RTT")
    const [selOption, setSelOption] = useState("Last Day")

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
                    <Dropdown
                            label = {dropdowns[0].label}
                            options = {dropdowns[0].options}
                            selectedValue={selOption}
                            onSelect={setSelOption}
                            className={dropdowns[0].className}/>
                    
                    {selOption === "Custom" && (
                        <div className="custom-time-amount">
                            {/*TODO*/}
                            {/* This will be replaced with a custom interval*/}
                            {/*Input for the custom duration of time*/} 
                            <input
                            type = "text"
                            value = {textVal}
                            onChange={(e) => setTextVal(e.target.value)}
                            placeholder="Input duration"
                            className="custom-duration-input"/>

                            {/*Dropdown for the unit of time for custom time durations*/} 
                            <Dropdown
                            label = {dropdowns[1].label}
                            options = {dropdowns[1].options}
                            selectedValue={dropdowns[1].selectedValue}
                            onSelect={dropdowns[1].onSelect}
                            className={dropdowns[1].className}/>
                        </div>
                    )}
                    
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
                    <LineChart data = {data} selectedMeasurement = {selMeasurement} selectedOption = {selOption}/>
                </div>
            </div>
        </div>
    );
};