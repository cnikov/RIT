const MB = 10; //5MB
const FILE_SIZE_LIMIT = MB * 1024 * 1024;
const fileSizeLimiter = (req,res,next) =>{
    const files = req.files
    const filesOverLimit = []
    Object.keys(files).forEach(key =>{
        if (files[key].size > FILE_SIZE_LIMIT){
            filesOverLimit.push(files[key].name)
        }
    })
    if (filesOverLimit.length){
        const error = `Upload failed`
        return res.status(413).json({status:"error",message:error});
    }
    next()
}
module.exports = fileSizeLimiter