var EstTable = {
    // Est構成ファイル
    //   Excel読み込み管理と自身での保有
    //   ある程度必要形式へ形式変更もを行うが責任を持ちすぎないように
    
    excel: null,
    logger: null,

    init: function(path,logger){
        this.path = path;
        this.excel = object(Excel).init(path,logger);
        this.logger = (logger === undefined)?
            object(Logger).init() : logger;
        return this;
    },

    load_config: function(){
        var config_hash = this.excel.select("config",function(so){
            return so.makeHash(1);
        });
        return config_hash;
    },

    each_sheet: function(func){
        this.excel.each_sheet(function(s){
            if(s.name != 'config') func(s);
        });
    },

    genre_exists: function(name){
        var flg = false;
        var n = name
        this.each_sheet(function(s,name){
            if(s.name == n) flg = true;
        });
        return flg;
    },

    get_genre: function(name){
        var genre = object(Genre).init(this.logger);
        var record = [];

        this.excel.select(name,function(so){
            genre.index_num = so.getIndex();
            record = so.getTable(2,5);
        });
        genre.load_entrys(record);
        return genre;
    }
};
