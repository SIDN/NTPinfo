import '../styles/DownloadButton.css'
function DownloadButton({ name, onclick }:{ name: String, onclick: (data : Object) => void; }) {

    return (
        <>
        <button className="download-btn" onClick={onclick}>
              {name}
        </button>
        </>
    )
}

export default DownloadButton
