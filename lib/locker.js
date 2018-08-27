var Locker = {
    fsys: WScript.CreateObject("Scripting.FileSystemObject"),
    lockfile: null,
    logger: null,

    init: function(file,logger){
        this.lockfile = file;
        this.logger = (logger === undefined)?
            object(Logger).init() : this.logger = logger;
        return this;
    },

    lock: function(){
        if(this.fsys.FileExists(this.lockfile)){
            return false;
        }else{
            writeUTF8(this.lockfile,"true")
            return true;
        }
    },

    unlock: function(){
         this.fsys.DeleteFile(this.lockfile, true);
    }
};
