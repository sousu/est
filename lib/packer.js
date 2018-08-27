var Packer = {
    fsys: WScript.CreateObject("Scripting.FileSystemObject"),
    dir: null,
    fd: null,
    im: null,
    genres: [],
    logger: null,

    init: function(dir,logger){
        this.fd = object(FileDiver).init(logger);
        this.fd.set(dir, 1);
        this.dir = dir;
        this.im = object(IdentMaker).init(logger);
        this.logger = (logger === undefined)?
            object(Logger).init() : this.logger = logger;
        return this;
    },

    del: function(genre_name){

        var id = this.im.make_id(genre_name);
        var path = false;
        this.fd.enum_dir(function(file){
            if((file.type == 'file') && (file.name).match(new RegExp('genre_'+id))){
                path = file.name;
            };
        });
        if(path){
            println("del "+path);
            this.fsys.DeleteFile(this.dir+"\\"+path, true);
        }
    },

    timestamp: function(name,time){
        println("");
        print("TimeStamp .. ");
        var id = this.im.make_id(name);
        var json = "{ \"ts\": \""+time.substr(0,(time.length-3))+"\" }"; // 秒は除く
        writeUTF8(this.dir+"\\"+"ts_"+id+".json", json);
        println("ok");
    },
    
    pack: function(list){
        print("genre packing .. ");
        var g = "";
        var path = false;
        for(i=0;i<list.length;i++){
            var id = this.im.make_id(list[i]);
            this.fd.enum_dir(function(file){
                if((file.type == 'file') && (file.name).match(new RegExp('genre_'+id))){
                    path = file.name;
                };
            });
            if(path){
                g += readUTF8(this.dir+"\\"+path) + "\n";
                path = false;
            }
        }
        writeUTF8(this.dir+"\\"+"genre", g);
        println("ok");
    }
};
