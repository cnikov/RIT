import './App.css';
import { BsFillCloudUploadFill, BsCheckLg } from "react-icons/bs";
import {  AiFillFileText  } from "react-icons/ai";
import { useState } from "react";
import {Watch} from "react-loader-spinner";

function App() {
  const [ file, setFile ] = useState(null);
  let [loading, setLoading] = useState(true);
  const [ msg, setMsg ] = useState(null);



  function handleUpload() {
    if(!file){
    setMsg("No file Selected");
    return;
    }
    const fd = new FormData();
    fd.append('file',file);

    setMsg("Uploading...");
    setLoading(!loading)
    fetch("http://localhost:3500/upload",{
      method: "POST",
      body: fd,
    })
    .then(res=> {
      if(!res.ok){
        throw res.statusText;
      }

      console.log(res)

      setMsg("Upload successful");
      document.getElementById("check").style.display = "block";
      setLoading(!loading)

      return res;

    })
    .then(data => console.log(data))
    .catch(err=>{
      setMsg("Upload failed");
      console.error(err);
    });
  }
  return (
    <div className="App">
    <div className='wrapper'>
      <h1>Uploading Files</h1>
      <div onClick={()=>{
          const fileInput = document.querySelector("input");
          fileInput.click();
      }} className='wrapper2'>
          <BsFillCloudUploadFill style={{
            fontSize:"50px",
            color:"black",
            }}></BsFillCloudUploadFill>

          <input hidden='true' onChange={(e)=> {setFile(e.target.files[0])
          setLoading(!loading) 
          document.querySelector("section").style.display = "block";
          document.querySelector(".name").innerText= e.target.files[0].name;  
          
          
          } } type="file"/>
      </div>
      <section hidden='true' >
        <li className='rows'>
          <AiFillFileText style={{
            fontSize:"30px",
          }}></AiFillFileText>
          <div className='content'>
            <div className='detail'>
              <span className='name'>fikjdejefhjlfcjlchejklle_01</span>
            </div>
          </div>
          <div  hidden='true' id="check">
          <BsCheckLg style={{
            fontSize:"30px",
            color:"green",
          }}></BsCheckLg>
          </div>
          
        </li>
      </section>
      <div style={{
        display:'flex',
        alignContent:'center',
        justifyContent:'center',
      }}>
      <Watch
                height="80"
                width="80"
                radius="48"
                ariaLabel="watch-loading"
                wrapperStyle={{}}
                wrapperClassName=""
                color='black'
                visible={!loading}
              />
      </div>
      <div style={{
        display:'flex',
        alignContent:'center',
        justifyContent:'center',
      }}> <button className="upload" onClick={ handleUpload }>Upload</button></div>
     
   <div style={{
        display:'flex',
        alignContent:'center',
        justifyContent:'center',
      }}>
   { msg && <span style={{
    marginTop:"15px",
    color:'black',
   }}>{msg}</span> }
   </div>
       

    </div>
      
    </div>
  );
}

export default App;
