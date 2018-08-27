var FileDiver = {
    
    // 指定Dirから潜行してブロックの実行
    // 内部イテレータとしての動作
    
    fsys: WScript.CreateObject("Scripting.FileSystemObject"),
    files: [],
    limit_depth: 5, // 最深でも5階層までになるように
    sort_as_windows: false,
    logger: null,


    init: function(logger){
        this.logger = (logger === undefined)?
            object(Logger).init() : this.logger = logger;
        return this;
    },

    set: function(root,depth){
        this.files = []; // initに記載しない内部保持類を初期化
        this.limit_depth = depth
        var dirObj = this.fsys.GetFolder(root);
        this.dive(dirObj,0,root,[root])
    },

    push: function(path,name,state,type,depth,chain,has_child){
        this.files.push({
            'path': path,
            'name': name,
            'state': state,
            'type': type,
            'depth': depth,
            'chain': chain, // Dirの連なり(階層順フルパス)
            'has_child': has_child
        })
    },

    dive: function(dirObj,c_depth,c_path,c_chain){
        var files = new Enumerator(dirObj.Files);
        for (; !files.atEnd(); files.moveNext()) {
            this.push( 
                    c_path+"\\"+files.item().Name,
                    files.item().Name,
                    'normal',
                    'file',
                    c_depth,
                    c_chain,
                    false
            );
        }
        
        var dirs = [];
        var subdirs = new Enumerator(dirObj.SubFolders);
        for (; !subdirs.atEnd(); subdirs.moveNext()) {
            dirs.push(subdirs.item());
        }
        if(this.sort_as_windows){
            dirs.sort(function(d1,d2){
                var name1 = d1["Name"].match(/^\d+/);
                var name2 = d2["Name"].match(/^\d+/);
                if(name1 && name2){
                    return (name1 - name2);
                }else if(name1 && !name2){
                    return -1; // 数値ファイル名優先
                }else if(!name1 && name2){
                    return 1;
                }else{
                    return d1["Name"].toString() - d2["Name"] .toString();
                }
            });
        }

        for(var i=0; i<dirs.length; i++){
            var path = c_path+"\\"+dirs[i].Name;
            this.push( 
                    path,
                    dirs[i].Name,
                    'normal',
                    'dir',
                    c_depth,
                    c_chain.concat([path]),
                    (dirs[i].SubFolders.count != 0)
            );
            if(this.limit_depth >= c_depth+1)
                this.dive(dirs[i], c_depth+1,path, c_chain.concat([path]));
        }
    },

    sort_as_windows: function(){
        this.sort_as_windows = true;
    },

    enum_dir: function(func){
        for(var i=0; i<this.files.length; i++){
            func(this.files[i])
            //var str = "----\n";
            //str = str+this.files[i]['path']+"\n";
            //str = str+this.files[i]['state']+",";
            //str = str+this.files[i]['type']+",";
            //str = str+this.files[i]['depth']+",";
            //for(var j=0; j<this.files[i]['parents'].length; j++){
            //    str = str+this.files[i]['parents'][j]+ ",";
            //}
            //WScript.echo(str);
        }
    }
};
