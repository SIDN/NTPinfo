import '../styles/Hero.css'
import github from '../assets/github-logo.png'
function Hero() {
    return (
        <>
         <div className="hero">
            <div className="text-hero">
               <h1 id="title">Are your time servers on time?</h1>
               <p>A tool to evaluate the accuracy of publicly available NTP servers</p>
            </div>
            <nav className="navbar">
                <a href="#">About</a>
                <div className="img-and-text">
                    <a href="#">Github</a>
                    <a href="">
                        <img src={github}  alt="GitHub Logo" />
                    </a>
                </div>
                
            </nav>
         </div>
        </>
    );
}

export default Hero