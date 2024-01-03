import React, { useState, useEffect } from "react";
import { BsFillCloudUploadFill, BsCheckLg } from "react-icons/bs";
import { AiFillFileText } from "react-icons/ai";
import { Watch } from "react-loader-spinner";
import ItemList from "./List_item";


function Home() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState(null);
  const [itemz, setItem] = useState(null);

  useEffect(() => {
    const storedData = JSON.parse(sessionStorage.getItem("rules"));
    setItem(storedData || null);
    if (storedData) {
      document.querySelector("section").style.display = "block";
      document.getElementById("first").style.display = "none";
    }
  }, []);




  async function checkStatus(id){
    const response = await fetch("http://localhost:3500/check-status", {
      method: "GET",
    });

    const data = await response.json();
    const item = data["data"];
    console.log(item)
    if( item === "Loading"){
      setMsg("Uploading...");
    }
    else{
      setMsg("Upload successful");
      setLoading(!loading);
      let my_rules = [];
      let tmp_dic = [];
      // BUILD THE LIST BY TAKING ONLY 3 ELEMENTS RULE 1, RULE2 AND RELATION
      for (let i in item) {
        if (i % 3 === 0 || i % 3 === 1) {
          tmp_dic.push(item[i]);
        } else {
          tmp_dic.push(item[i]);
          my_rules.push(tmp_dic);
          tmp_dic = [];
        }
      }
      setItem(my_rules);
      sessionStorage.setItem("rules", JSON.stringify(my_rules));
      let elem = document.getElementById("first")
      if (elem) {
      elem.style.display = "none";}
      setLoading(true);
      clearInterval(id);
    }
  }



  async function handleUpload() {
    setItem(null);

    if (!file) {
      setMsg("No file Selected");
      return;
    }

    const fd = new FormData();
    fd.append("file", file);

    setMsg("Uploading...");
    setLoading(!loading);

    try {
      const response = await fetch("http://localhost:3500/upload", {
        method: "POST",
        body: fd,
      });

      if (!response.ok) {
        throw response.statusText;
      }
      const intervalId = setInterval(() => {
        checkStatus(intervalId)
      },10000);

      
    } catch (err) {
      setMsg("Upload failed");
      console.error(err);
    }
  }

  const handleFileInputChange = (e) => {
    setFile(e.target.files[0]);
    document.querySelector("section").style.display = "block";
    if (e.target.files[0]?.name) {
      document.querySelector(".name").innerText = e.target.files[0].name;
    }
  };

  return (
    <div className="App">
      <div className="wrapper">
        <h1>Uploading Files</h1>
        <div
          onClick={() => {
            const fileInput = document.querySelector("input");
            fileInput.click();
          }}
          className="wrapper2"
        >
          <BsFillCloudUploadFill
            style={{
              fontSize: "50px",
              color: "black",
            }}
          ></BsFillCloudUploadFill>
          <input
            hidden={true}
            onChange={handleFileInputChange}
            type="file"
          />
        </div>
        <section hidden={true}>
          <div id="span-list">
            <ItemList itemList={itemz} />
            <li className="rows" id="first">
              <AiFillFileText
                style={{
                  fontSize: "30px",
                }}
              ></AiFillFileText>
              <div className="content">
                <div className="detail" style={{ overflowY: "scroll" }}>
                  <span className="name">fikjdejefhjlfcjlchejklle_01</span>
                </div>
              </div>
              <div hidden={true} id="check">
                <BsCheckLg
                  style={{
                    fontSize: "30px",
                    color: "green",
                  }}
                ></BsCheckLg>
              </div>
            </li>
          </div>
        </section>
        <div
          style={{
            display: "flex",
            alignContent: "center",
            justifyContent: "center",
          }}
        >
          <Watch
            height="80"
            width="80"
            radius="48"
            ariaLabel="watch-loading"
            wrapperStyle={{}}
            wrapperClassName=""
            color="black"
            visible={!loading}
          />
        </div>
        <div
          style={{
            display: "flex",
            alignContent: "center",
            justifyContent: "center",
          }}
        >
          <button className="upload" onClick={handleUpload}>
            Upload
          </button>
        </div>
        <div
          style={{
            display: "flex",
            alignContent: "center",
            justifyContent: "center",
          }}
        >
          {msg && (
            <span
              style={{
                marginTop: "15px",
                color: "black",
              }}
            >
              {msg}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default Home;
