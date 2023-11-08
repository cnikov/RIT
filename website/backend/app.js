const express = require("express");
let {PythonShell} = require('python-shell');
const fileUpload = require("express-fileupload");
const path = require("path");
const filesPayloadExists = require('./middleware/filesPayloadExists');
const fileExtLimiter = require('./middleware/fileExtLimiter');
const fileSizeLimiter = require('./middleware/fileSizeLimiter');
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
app.use(cors());
app.use(bodyParser.urlencoded({
    extended: true
  }));

app.get("/",(req,res) =>{
    res.sendFile(path.join(__dirname + "/index.html"));
});
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

app.post('/upload',
    fileUpload({  createParentPath: true  }),
    filesPayloadExists,
    fileExtLimiter(['.pdf','.zip','.rar']),
    fileSizeLimiter,
    
    (req, res) => {
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
        PythonShell.run("python/tree.py",options).then(results =>{
            // result is an array consisting of messages collected 
            const data = results
            console.log(data)
            return res.json({"data" : data})
            //during execution of script.
      });
        
        
    }
    )
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));