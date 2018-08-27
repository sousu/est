var Gatherer = {
    cmd: null,
    config: null,
    genre: null,
    elements: [], // 1つのDirに対する登録集合とidを持つ,1つのコマンド発行に対応
    reg:[],
    im: null,
    fsys: WScript.CreateObject("Scripting.FileSystemObject"),
    logger: null,

    init: function(config,logger){
        this.cmd = object(Cmd).init(config,logger)
        this.im = object(IdentMaker).init(logger);
        this.config = config;
        this.elements = [];
        this.reg = [];
        this.logger = (logger === undefined)?
            object(Logger).init() : logger;
        return this;
    },

    //事前登録コマンド
    regist_genre: function(name){
        this.genre = name
    },
    regist_dir: function(chain,path){
        if(!this.match(path)) return;
        var tmp = this.config["BASEDIR"]+"\\"+this.config["TMP_FOLDER"]+"\\"+"list";
        var scan = this.config["BASEDIR"]+"\\"+this.config["CMD_SCAN"]+" \"" + path + "\"";

        // 大量リストでのexecパイプ破壊対策
        //   全体をscanコマンド頼みにしなければ
        //   tmpファイル依存をなくせる
        this.cmd.run("%comspec% /c "+scan+">"+tmp);

        var target = [];
        var record = "";
        var file = this.fsys.OpenTextFile(tmp);
        while(!file.AtEndOfStream){
            record = file.ReadLine();
            if(this.match(record) && (record != "")) target.push(record);
        }
        if(target.length) this.regist(chain,target.join("\n"));

        // リスト内容を上書削除
        this.cmd.run("%comspec% /c echo empty>"+tmp);
    },
    regist_file: function(chain,path){
        if(!this.match(path)) return;
        this.regist(chain,path);
    },
    regist: function(chain,target){
        var hashed_id = this.im.make_id(chain);
        var key = hashed_id.join("_");

        if(this.elements[key]){
        // 登録が無ければ新規登録
            this.elements[key].target += "\n"+target;
        }else{
        // 登録済みならtarget追記
            this.elements[key] = {
                "id":hashed_id,
                "name":chain[chain.length-1], 
                "target": target
            };
        }
    },
    
    //実行
    gather: function(){
        for(var k in this.elements){
            if(this.elements[k].id !== undefined){ 
                print(this.elements[k].name+" ");

                var list = this.elements[k].target.split("\n");
                var input = "";
                var exe = function(cmd,c,input){
                    var out = cmd.exec(c,input); 
                    if(out[1]) println("\n**ERR**\n"+out[1]+"**STDOUT**\n"+out[0]+"** **");
                };
                // exe loop 
                for(var i=0;i<list.length;i++){
                    print('.');
                    if(input.length+list[i].length+1 >= this.config['CMD_GATHER_STDINCNT']){
                        exe(this.cmd,this.cmd_str(this.elements[k].id),input);
                        input = "";
                        print(' ');
                    }
                    if(list[i].match(/&/)){
                        //安定稼働させるにはここをコメントアウト
                        //実行OSにより&含みファイル時に止まる場合がある
                        exe(this.cmd,this.cmd_str(this.elements[k].id,list[i]));
                        println("");
                        print(" ->contain & skip ["+list[i]+"]");
                    }else{
                        input += list[i]+"\n";
                    }
                }
                exe(this.cmd,this.cmd_str(this.elements[k].id),input);
                println(""); 
            }
        }
    },
    cmd_str: function(id,path){
        var s = this.config["BASEDIR"]+"\\"+
                this.config["CMD_GATHER1"]+" "+this.config["CMD_GATHER_EXETS"]+" "+
                this.config["CMD_GATHER_FILT"]+" "+
                this.config["CMD_GATHER2"]+" "+this.id_str(id)+" "+
                this.config["CMD_GATHER3"]+" "+this.config["CASKET"]+"\\"+this.genre;
        s = path ? s+" "+"\""+path+"\"" : s+" -" ;
        return s;
    },
    cmd_test_str: function(path){
        var s = this.config["BASEDIR"]+"\\"+
                this.config["CMD_GATHER1"]+" "+this.config["CMD_GATHER_EXETS"]+" "+
                this.config["CMD_GATHER_FILT"]+" "+
                this.config["CMD_GATHER2"]+" "+
                this.config["CMD_GATHER3"]+" "+this.config["TMP_FOLDER"]+"/casket_test";
        s = path ? s+" "+"\""+path+"\"" : s+" -" ;
        return s;
    },
    id_str: function(id){
        var s = "";
        s += this.config['CMD_GATHER_AAGENRE']+" "+this.im.make_id(this.genre)+" ";
        for(var i=0;i<id.length;i++){
            if(i == 0){ s += this.config['CMD_GATHER_AAROOT']+" "+id[i]+" ";
            }else{      s += this.config['CMD_GATHER_AADEP']+i+" "+id[i]+" ";
            }
        }
        return s
    },

    test: function(path){
        var exe = function(cmd,c){
            cmd.gradual();
            var out = cmd.exec(c); 
            //if(out[0]) println(out[0]);
            //if(out[1]) println("\n**ERR**\n"+out[1]);
        };
        exe(this.cmd,this.cmd_test_str(path));
    },
    each_element: function(func){
        for(var k in this.elements){
            if(this.elements[k].id !== undefined){ 
                func(this.elements[k]);
            }
        }
    },
    regex: function(white,black){
        this.reg[0] = white;
        this.reg[1] = black;
    },
    match: function(path){
        // ホワイトリストに記載がない 
        // ブラックリストに記載がある 場合は不採用 
        if(this.reg[0] && !path.match(this.reg[0])) return false;
        if(this.reg[1] && path.match(this.reg[1])) return false;
        return true;
    }
};
