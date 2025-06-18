import '../styles/DownloadButton.css'
function DownloadButton({ name, onclick }:{ name: string, onclick: (data : object) => void; }) {

    return (
        <>
        <button className="download-btn" onClick={onclick}>
              {name}
        </button>
        </>
    )
}

export default DownloadButton
