var Builder = {
    im: null,
    config: null,
    cnt: null,            
    root_cnt: null, 
    root_menu_html: "",
    sub_menu_html: "",
    json: "",
    logger: null,
    reg:[],

    markups: {
        genre_href:     "estseek.cgi",
        root_id_head:   "root",
        dir_id_head:    "d"
    },
    fnames: {
        genre_head:     "genre",
        entry_roots:    "entry_roots",
        entry_ids:      "ids.json"
    },

    init: function(config,logger){
        this.im = object(IdentMaker).init(logger);
        this.config = config;
        this.cnt = 1;
        this.root_menu_html = "";
        this.sub_menu_html = "";
        this.json = "{ \n";
        this.logger = (logger === undefined)?
            object(Logger).init() : logger;
        return this;
    },

    root_li_tag: function(name,path){
        this.root_cnt = this.cnt;
        this.root_menu_html += 
            "<li>\n "+
                this.li_inner(name,this.im.make_id(path)) + "\n "+
               "<span id=\""+ this.markups["root_id_head"]+this.root_cnt +
                  "\" class=\"pop_button quickmenu_pop normal\">&nbsp;</span>\n "+
            "</li>\n";
    },

    sub_ul_tag_start: function(){
        this.sub_menu_html += 
            "<ul class=\"quickmenu-data\" stlye=\"display:none\">\n";
    },

    sub_ul_tag_open: function(file){
        this.sub_menu_html += "<ul>\n";
    },

    sub_li_tag_open: function(name,path,depth){
        var padding = new Array(depth+2).join(" ");
        this.sub_menu_html += 
            padding+"<li>"+this.li_inner(name,this.im.make_id(path));
    },

    li_inner: function(name,id_val){
        var d = this.markups["dir_id_head"] + this.cnt;
        var inner =  "<label for=\""+ d +"\" class=\"dir_check\">"+
                       "<input type=\"checkbox\" name=\""+ d +"\" "+
                         "id=\""+ d +"\" class=\"dir\" />"+
                         name 
                    +"</label>";
        this.json += "\""+ d +"\" : \""+ id_val+"\",\n";
        this.cnt +=1;
        return inner;
    },

    sub_li_tag_close: function(){
        this.sub_menu_html += "</li>\n";
    },

    sub_ul_li_tag_close: function(num,depth){
        for (var i=0; i<num; ++i) {
            var padding = new Array(depth-i+1).join(" ");
            this.sub_menu_html += 
                padding + "</ul></li>\n";
        }
    },

    sub_ul_tag_end: function(){
        this.sub_menu_html += 
            "</ul>\n";
    },

    flush_genre: function(genre_name){
        var gid = this.im.make_id(genre_name);
        var a =
            "<a href=\""+ this.markups["genre_href"] +
               "\" id=\""+ gid +"\" class=\"genre_link\">"+
                genre_name
            +"</a>\n";
        this.flush(this.fnames['genre_head']+"_"+gid, a);
    },

    flush_root_menu: function(genre_name){
        this.flush(
                this.im.make_id(genre_name)+ "_"+this.fnames["entry_roots"],
                this.root_menu_html
        );
        this.root_menu_html="";
    },

    flush_sub_menu: function(genre_name){
        //!issue root_cntが正常であることに依存
        this.flush(
                this.im.make_id(genre_name)+ "_"+this.markups["root_id_head"]+this.root_cnt,
                this.sub_menu_html
        );
        this.sub_menu_html="";
    },

    flush_json: function(genre_name){
        this.json += "\"end\" : \"end\"\n}"; //!issue 最終セミコロン処置
        this.flush(
                this.im.make_id(genre_name)+ "_"+this.fnames["entry_ids"],
                this.json
        );
        this.json="";
    },

    flush: function(name,str){
        var dir = this.config["BASEDIR"]+"\\"+this.config["PARTSDIR"];
        writeUTF8(dir+"\\"+name, str); 
    },

    //!issue gathererと機能重複 委譲化すべき
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
