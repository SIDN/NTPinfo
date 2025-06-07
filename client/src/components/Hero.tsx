import '../styles/Hero.css'
import github from '../assets/github-mark-high-res-blue.png'

function Hero() {
    return (
        <div className="hero">
            <div className="text-hero">
                <h1 id="title">Are your time servers on time?</h1>
                <p>A tool to evaluate the accuracy of publicly available NTP servers</p>
            </div>
            <nav className="navbar">
                {/* <a href="#" aria-label="About">About</a> */}
                <div className="img-and-text">
                    <a href="#" aria-label="GitHub Repository">Github</a>
                    <a href="https://github.com/your-repo" target="_blank" rel="noopener noreferrer" aria-label="GitHub Repository">
                        <img src={github} alt="GitHub Logo" />
                    </a>
                </div>
            </nav>
        </div>
    );
}

export default Hero