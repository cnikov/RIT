const express = require("express");
const fileUpload = require("express-fileupload");
const path = require("path");
const filesPayloadExists = require('./middleware/filesPayloadExists');
const fileExtLimiter = require('./middleware/fileExtLimiter');
const fileSizeLimiter = require('./middleware/fileSizeLimiter');
const cors = require('cors');

const PORT = process.env.PORT || 3500;

const app = express();
app.use(cors());

app.get("/",(req,res) =>{
    res.sendFile(path.join(__dirname + "/index.html"));
});

app.post('/upload',
    fileUpload({  createParentPath: true  }),
    filesPayloadExists,
    fileExtLimiter(['.pdf','.zip','.rar']),
    fileSizeLimiter,
    (req, res) => {
        const files = req.files
        console.log(files)
        console.log(res)
        Object.keys(files).forEach(key =>{
            const filepath = path.join(__dirname,'files',files[key].name)
            files[key].mv(filepath, (err) =>{
                if (err) return res.status(500).json({status: "error", message:err})
            })
        })
        res.send("ok")
    }
    )
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));