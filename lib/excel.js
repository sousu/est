var Excel = {
    // Excelの基礎操作を管轄
    
    app: null,
    path: "",
    book: null,
    sheetoperator: null,
    logger: null,

    init: function(path,logger){
        this.app = new ActiveXObject("Excel.Application");
        this.path = path;
        this.logger = (logger === undefined)?
            object(Logger).init() : logger;
        return this;
    },

    open: function(func){
        try{
            this.logger.debug("workbook open ["+this.path+"]");
            return func(this.app.Workbooks.Open(this.path),this.logger);
        }catch(e){
            println("excel err\n"+e.description+"\nmsg->"+e.message);
        }finally{
            this.app.Workbooks.close();
        }
    },

    each_sheet: function(func){
        return this.open(function(app){
            for (var i = 0; i < app.Sheets.Count; i++) {
                func(app.Sheets.Item(i+1));
            }
        });
    },

    select: function(name,func){
        return this.open(function(app,logr){
            this.sheetoperator = object(SheetOperator).init(app.Sheets(name),logr);
            logr.debug("select sheet ["+name+"]");
            return func(this.sheetoperator);
        });
    }
};

var SheetOperator = {
    // Excelのシート操作を管轄
    sheet: null,
    logger: null,

    init: function(sheet,logger){
        this.sheet = sheet;
        this.logger = (logger === undefined)?
            object(Logger).init() : logger;
        return this;
    },

    getIndex: function(){
        return this.sheet.Index;
    },

    // 1列目をkey,2列目をvalueとして配列を返す
    //  start_row -> 開始行数
    makeHash: function(start_row){
        var hash = {};
        var v = "";
        var k,v;
        for(var row=start_row;;row++){
            k = this.sheet.Cells(row,1).value; 
            v = this.sheet.Cells(row,2).value; 
            if ((!k || k == "") && (!v || v == "")) break;
            hash[k] = v;
        }
        return hash;
    },

    // 指定した行の行方向にセルを配列化
    //  numを指定する場合は当該列数まで
    getRowAry: function(row,col_num){
        var ary = [];
        var v = "";
        for(var column=1;;column++){
            v = this.sheet.Cells(row,column).value; 
            if (column > col_num) break;
            // col_numを定義していない場合は値で判断
            if (!col_num && (!v || v == "")) break;
            ary.push(v);
        }
        return ary;
    },

    // 1行目をヘッダとして行ごとのHashの配列を返す
    getTable: function(start_row,col_num){
        var table = [];
        var header = this.getRowAry(1,col_num)
        for(var r=start_row;;r++){
            //this.logger.debug("row_num ->"+r);
            var hash = {};
            var ary = this.getRowAry(r,col_num); //終了条件
            if (!ary[1] || ary[1] == "") break;
            for(var i=0;i<col_num;i++){
               // this.logger.debug("key:"+header[i]+" val:"+ary[i]);
                hash[header[i]] = ary[i];
            }
            table.push(hash);
        }
        return table;
    }
};
