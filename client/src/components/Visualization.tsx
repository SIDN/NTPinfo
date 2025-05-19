import { useState, useRef } from "react";
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

    const [isCustomChecked, setCustomChecked] = useState(false)
    const [isOffsetChecked, setOffsetChecked] = useState(true)
    const [isDelayChecked, setDelayChecked] = useState(false)
    const [textVal, setTextVal] = useState("")
    const [selMeasurement, setSelMeasurement] = useState<Measurement>("RTT");

    const handleMeasurementChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelMeasurement(event.target.value as Measurement);
      };

    // useEffect(() => {
    //     function handleClickOutside(event: MouseEvent) {
    //         if (popupRef.current && !popupRef.current.contains(event.target as Node)){
    //             onClose();
    //         }
    //     }

    //     document.addEventListener("mousedown", handleClickOutside);

    //     return () => {
    //         document.addEventListener("mousedown", handleClickOutside);
    //     };
    // }, [isOpen, onClose]);

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
                            selectedValue={dropdowns[0].selectedValue}
                            onSelect={dropdowns[0].onSelect}
                            className={dropdowns[0].className}/>
                    
                    {/*Checkbox for having a custom time duration*/} 
                    <label className="checkbox-custom-label">
                        <input
                        type = "checkbox"
                        checked = {isCustomChecked}
                        onChange={() => setCustomChecked(!isCustomChecked)}/>
                        Custom
                    </label>

                    {isCustomChecked && (
                        <div className="custom-time-amount">

                            {/*Imput for the custom duration of time*/} 
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
                    {/*Radio for showing offset data*/} 
                    <label className="radio-measurement-label">
                        <input
                            type="radio"
                            name="measurement"
                            value="offset"
                            checked={selMeasurement === 'offset'}
                            onChange={handleMeasurementChange}
                        />
                        Offset
                    </label>
                    {/*Radio for showing delay data*/} 
                    <label className="radio-measurement-label">
                        <input
                            type="radio"
                            name="measurement"
                            value="RTT"
                            checked={selMeasurement === 'RTT'}
                            onChange={handleMeasurementChange}
                        />
                        Delay
                    </label>

                    
                    {/*<label className="checkbox-measurement-label">
                        <input
                        type = "radio"
                        name = "measurement-type"
                        checked = {isOffsetChecked}
                        onChange={() => setOffsetChecked(!isOffsetChecked)}/>
                        Offset
                    </label>

                    
                    <label className="checkbox-measurement-label">
                        <input
                        type = "radio"
                        name = "measurement-type"
                        checked = {isDelayChecked}
                        onChange={() => setDelayChecked(!isDelayChecked)}/>
                        Delay
                    </label>*/}
                </div>
                <div className="chart-box">
                    <LineChart data = {data} selectedMeasurement = {selMeasurement}/>
                </div>
            </div>
        </div>
    );
};