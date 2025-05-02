import '../styles/Hero.css'

function Hero() {
    return (
        <>
         <div className="hero">
            <div className="text-hero">
               <h1 id="title">Are your time servers on time?</h1>
               <h2>A tool to evaluate the accuracy of publicly available NTP servers</h2>
            </div>
            <nav className="navbar">
                <a href="#">About</a>
                <a href="#">Github</a>
            </nav>
         </div>
        </>
    );
}

export default Hero