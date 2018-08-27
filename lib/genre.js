var Genre = {

    index_num: null,
    entries: null,
    logger: null,

    init: function(logger){
        this.entries =[];
        this.logger = (logger === undefined)?
            object(Logger).init() : logger;
        return this;
    },

    load_entrys: function(record){

        for (var i=0; i<record.length; i++){ 
            this.entries.push( object(GenreEntry).init(record[i],this.logger));
        }
        return this;
    },

    each_entry: function(func){
        for(var i=0; i<this.entries.length; i++){
            func(this.entries[i]);
        }
    }
};

// GenreEntryはRootに対応
var GenreEntry = {
    logger: null,

    init: function(src,logger){
        for (var prop in src) {
            if (this.check_include_regex(prop)) 
                src[prop] = this.convert_reg(src[prop]);
            this[prop] = src[prop];
        };
        this.logger = (logger === undefined)?
            object(Logger).init() : logger;
        return this;
    },

    check_include_regex: function(name){
        // 表現形式判定
        return name.match(/Regex/i);
    },

    convert_reg: function(src){
        return (src === undefined)? null : new RegExp(src);
    }
};
