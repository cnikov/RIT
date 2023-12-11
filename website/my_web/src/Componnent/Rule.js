import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import Editor from "@monaco-editor/react";

function Rule() {
  const [overlap, setOverlap] = useState(null);
  const location = useLocation();
  const [file, setFileContent] = useState(null);
  const [file2, setFile2Content] = useState(null);
  const [name, setName] = useState(null);
  const [name2, setName2] = useState(null);
  const monacoEditorRef = useRef(null);
  const monacoEditor2Ref = useRef(null);
  const decorationsRef = useRef([]);
  const decorationsRef2 = useRef([]);

  function Reset(){
    const editor = monacoEditorRef.current;
    const existingDecorations = decorationsRef.current;
    decorationsRef.current = editor.deltaDecorations(existingDecorations, []);
    editor.layout();
    monacoEditorRef.current = editor;
    highlight();
  }

  function Reset2(){
    const editor = monacoEditor2Ref.current;
    const existingDecorations = decorationsRef2.current;
    decorationsRef2.current = editor.deltaDecorations(existingDecorations, []);
    editor.layout();
    monacoEditor2Ref.current = editor;
    highlight2();
  }

  // Simplify the overlap string to make it more readable while we have logic condition and the end of the string is ) we can reduce the string
  function Simplify(string){
    let  i = 0
    let tmp =""
    while (i < string.length-2){
        tmp += string[i]
        if (tmp === "AND(" || tmp === "OR("){
          if((string[i+1] === 'A' || string[i+1]=== "O") && (string[string.length-1] === ')' && string[string.length-2] === ')')){  
            string = string.substr(i+1)
            string = string.slice(0,-1)
            tmp =""
            i = 0
          }
          else{i++}  
        }
        else{i++}
    }
    return string
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        const { from } = location.state;
        console.log(from)
        if (!from) return;
        const val = { data: from };
        const response = await fetch("http://localhost:3500/file", {
          method: "POST",
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(val),
        });

        if (!response.ok) {
          throw new Error(response.statusText);
        }
        //waiting the files from backend
        const data = await response.json();
        setFileContent(data.data[0]);
        setName(data.data.name1);
        setName2(data.data.name2);
        setFile2Content(data.data[1]);
        if (data.data.overlap !== undefined && !data.data.overlap.includes("Connection")) {
          let variable = Simplify(data.data.overlap)
          setOverlap(variable);
        }
      } catch (error) {
        console.error(error);
      }
    };
    fetchData();
  }, [location.state]);

  const handleSaveFile = (content, name) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = name + '.yaml';
    a.click();
    URL.revokeObjectURL(url);
  };

  // Escape special characters except for "$" and "n"
  function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\$/g, '$').replace(/n/g, 'n');
  }

  //check which part of the overlap match the files content 
  function findSub(string1, string2) {
    let list = [];
    let tmp = "";
    let unescape = "";
    for (let i = 0; i < string1.length; i++) {
      tmp += escapeRegExp(string1[i]);
      unescape += string1[i];
      console.log(unescape)
      if (!string2.includes(tmp)) {
        tmp = tmp.slice(0, -1);
        unescape = unescape.slice(0, -1);
        if (unescape.length > 2 && !["OR", "AND", "NOT"].includes(unescape)) {
          list.push(unescape);
        }
        tmp = escapeRegExp(string1[i]);
        unescape = string1[i];
      }
    }
    if (unescape.length > 2 && !["OR", "AND", "NOT"].includes(unescape)) {
      list.push(unescape);
    }
    return list;
  }

  //generate a text decoration for the part of the file that match part of the overlap
  const highlight = () => {
    if (overlap && monacoEditorRef.current) {
      const editor = monacoEditorRef.current;
      const model = editor.getModel();
      if (model) {
        const matchList = findSub(overlap, model.getValue());
        const decorations = matchList.flatMap(match => {
          const matches = model.findMatches(match);
          const decorationOptions = {
            isWholeLine: false,
            className: 'highlighted-text',
          };
          return matches.map(match => ({
            range: match.range,
            options: decorationOptions,
          }));
        });
        decorationsRef.current = editor.deltaDecorations(decorationsRef.current, decorations);
        editor.layout();
        monacoEditorRef.current = editor
      }
    }
  };


  //generate a text decoration for the part of the file that match part of the overlap
  const highlight2 = () => {
    if (overlap && monacoEditor2Ref.current) {
      const editor = monacoEditor2Ref.current;
      const model = editor.getModel();
      if (model) {
        const matchList = findSub(overlap, model.getValue());
        const decorations = matchList.flatMap(match => {
          const matches = model.findMatches(match);
          const decorationOptions = {
            isWholeLine: false,
            className: 'highlighted-text',
          };
          return matches.map(match => ({
            range: match.range,
            options: decorationOptions,
          }));
        });
        decorationsRef2.current = editor.deltaDecorations(decorationsRef2.current, decorations);
        editor.layout();
        monacoEditor2Ref.current = editor
      }
    }
  };
  useEffect(()=>{
    highlight();
    highlight2();
}) 

  const handleEditorChange = (value) => {
    setFileContent(value);
    Reset();
  };

  const handleEditor2Change = (value) => {
    setFile2Content(value);
    Reset2();
  };

  return (
    <div id="editor">
      <code>{overlap}</code>
      <div className="App2">
        <div>
          <Editor
            height="60vh"
            width="50vw"
            language="yaml"
            theme="vs-dark"
            value={file}
            onChange={handleEditorChange}
            beforeMount={(editor) => {
              monacoEditorRef.current = editor;
            }}
            onMount={(editor) => {
              monacoEditorRef.current = editor;
            }}
          />
          <button onClick={() => handleSaveFile(file, name)}>Save 1</button>
        </div>
        <div>
          <Editor
            id="editor2"
            height="60vh"
            width="50vw"
            language="yaml"
            theme="vs-dark"
            value={file2}
            onChange={handleEditor2Change}
            beforeMount={(editor) => {
              console.log(editor);
              monacoEditor2Ref.current = editor;
            }}
            onMount={(editor) => {
              console.log(editor);
              monacoEditor2Ref.current = editor;
            }}
          />
          <button onClick={() => handleSaveFile(file2, name2)}>Save 2</button>
        </div>
      </div>
    </div>
  );
}

export default Rule;
