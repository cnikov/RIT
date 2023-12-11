const express = require("express");
let {PythonShell} = require('python-shell');
const fileUpload = require("express-fileupload");
const path = require("path");
const filesPayloadExists = require('./middleware/filesPayloadExists');
const fileExtLimiter = require('./middleware/fileExtLimiter');
const cors = require('cors');
const fs = require('fs');
var bodyParser = require('body-parser')
 
// create application/json parser
var jsonParser = bodyParser.json()
 var finalPath = ""
 
// create application/x-www-form-urlencoded parser
var urlencodedParser = bodyParser.urlencoded({ extended: true })
const PORT = process.env.PORT || 3500;
const app = express();
let status = null
app.use(cors());
app.use(bodyParser.urlencoded({
    extended: true
  }));

app.get("/",(req,res) =>{
    res.sendFile(path.join(__dirname + "/index.html"));
});
app.get('/check-status',(req,res)=>{
  console.log(status);

  if (!status)
  {
    return res.json({'data': "Loading"})
  }
  else{
    return res.json({'data' : status})
  }
})
// ENDPOINT TO GET THE RIGHT FILES FROM THE BACKEND
app.post("/file",jsonParser,urlencodedParser,(req,res) =>{
    data = req.body["data"];
    let Mypath = path.join("myfolder",finalPath, data[0]) + ".yaml"
    let Mypath2 = path.join("myfolder",finalPath, data[1]) + ".yaml"
    let myData = {"name1":data[0],"name2":data[1]}
    if(!(data[2].includes("Relation"))){
        myData["overlap"] = data[2]
    }
    fs.readFile(Mypath, 'utf8', (err, data) => {
        if (err) {
          res.status(500).send('Error reading the file');
        } else {
          myData["0"] = data;
          fs.readFile(Mypath2, 'utf8', (err, data2) => {
            if (err) {
              res.status(500).send('Error reading the file');
            } else {
              myData["1"] = data2;
              return res.json({'data' : myData})
            }
          });
        }
      });

      
});


// ENDPOINT TO UPLOAD THE ZIP FILE AND THEN RUN THE PYTHON ALOGRITHM ON IT
app.post('/upload',
    fileUpload({  createParentPath: true  }),
    filesPayloadExists,
    fileExtLimiter(['.pdf','.zip','.rar']),
    
    async (req, res) => {
        const files = req.files
        let filename = "";
        Object.keys(files).forEach(key =>{
            const filepath = path.join(__dirname,'files',files[key].name)
            filename = filepath
            finalPath = (files[key].name).slice(0,-4)
            files[key].mv(filepath, (err) =>{
                if (err) return res.status(500).json({status: "error", message:err})
            })
        })
        let options = {
            args:[filename]
        
          }
        await executeTask(options)
        res.json({"data" : "Loading" })
        });


function executeTask(options){
  console.log("execturing task")
PythonShell.run("python/tree.py",options).then(results =>{
    // result is an array consisting of messages collected 
    const data = results
    console.log(data)
    const contentToWrite = 'This is the content that will be written to the file.';
    const item = data;
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
    itemList = my_rules
    let varList = [];
    for (let i in itemList) {
      let cond = true;
      if (varList.length === 0) {
        varList.push(itemList[i]);
      } else {
        for (let j in varList) {
          if (
            (itemList[i][1] === varList[j][0] &&
              itemList[i][0] === varList[j][1]) ||
            (itemList[i][0] === varList[j][0] && itemList[i][1] === varList[j][1])
          ) {
            cond = false;
          }
        }
        if (cond) {
          varList.push(itemList[i]);
        }
      }
    }
    console.log(varList)
    let txt = ""
    for (let i in varList){
      txt += varList[i]
      txt +="\n"
    }
    // Specify the file path
    const filePath = 'result.txt';

    // Write to the file
    fs.writeFile(filePath, txt, (err) => {
      if (err) {
        console.error('Error writing to file:', err);
      } else {
        console.log('File successfully written:', filePath);
      }
    });
    status = data
    //during execution of script.
});}
        
        
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));