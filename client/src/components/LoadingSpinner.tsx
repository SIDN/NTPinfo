import '../styles/LoadingSpinner.css'
interface LoadingSpinnerProps {
    size: "small" | "medium" | "large"
}

export default function LoadingSpinner({size}: LoadingSpinnerProps) {
    return <div className={`loading-spinner ${size}`}> </div>
}