import { useEffect, useState } from "react";
import '../styles/ConsentPopup.css'
export default function ConsentPopup() {

    const [showPopup, setShowPopup] = useState(false)

    useEffect(() => {
        const consentGiven = sessionStorage.getItem('consentGiven')
        if (consentGiven === 'false' || !consentGiven)
            setShowPopup(true)
    }, [setShowPopup])

    const handleConsent = () => {
    sessionStorage.setItem('consentGiven', 'true');
    setShowPopup(false);
    }

    return (
        showPopup && (
            <div className="popup">
                <div className="popup-card">
                    <h2>Privacy notice</h2>
                    <p>Our application may need to use your IP address to get more accurate geolocation data.<br></br>Your IP is masked and will never be stored.</p>
                    <button onClick={handleConsent}>I consent</button>
                </div>
            </div>
        )
    )

}