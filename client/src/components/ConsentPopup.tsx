import { useEffect, useState } from "react";
import '../styles/ConsentPopup.css'
export default function ConsentPopup() {

    const [showPopup, setShowPopup] = useState(false)

    useEffect(() => {
        const consentGiven = localStorage.getItem('consentGiven')
        if (!consentGiven)
            setShowPopup(true)
    }, [setShowPopup])

    const handleConsent = () => {
    localStorage.setItem('consentGiven', 'true');
    setShowPopup(false);
    }

    return (
        showPopup && (
            <div className="popup">
                <div className="popup-card">
                    <h2>Privacy notice</h2>
                    <p>Our application may need to use your IP to get more accurate location data.</p>
                    <button onClick={handleConsent}>I consent</button>
                </div>
            </div>
        )
    )

}