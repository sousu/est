// 
// 汎用logger
// 

var Log = {
    level: "info",
    file: null,
    anonymous: "",

    init: function(f,lv){
        this.level = lv || this.level;
        switch(typeof f){
            case "string":
                //!issue file open
                break;
            case "object":
                this.file = f;
                break;
            default:
                this.file = WScript.StdErr;
                break;
        };
        return this;
    },

    log: function(lv,msg){
        var levels = ['debug','info ','warn ','error','fatal'];
        if(levels.indexOf(lv) <= levels.indexOf(this.level)){
            //!issue write file
            WScript.echo("["+ lv +"] "+ msg);
        }
    },

    format: function(msg,func){
        return func + ": " + msg;
    },

    testfunc: function(f){
        // どこで呼ばれているかを評価する
        //  arguments.callee
        //    - 呼出位置そのもの・現状これが無名関数だと特定出来ない問題
        //
        var s = (f.toString()).match(/function\s*(\w*)/)[1];
        return isEmpty(s) ? this.anonymous : s;
        function isEmpty(s){
            return (s==null) || (s.length == 0);
        }
    },

    debug: function(msg){ this.log('debug',
            this.format(msg,this.testfunc(arguments.callee.caller))); },
    info:  function(msg){ this.log('info ',
            this.format(msg,this.testfunc(arguments.callee.caller))); },
    warn:  function(msg){ this.log('warn',
            this.format(msg,this.testfunc(arguments.callee.caller))); },
    error: function(msg){ this.log('error',
            this.format(msg,this.testfunc(arguments.callee.caller))); },
    fatal: function(msg){ this.log('fatal',
            this.format(msg,this.testfunc(arguments.callee.caller))); },

    _test: function(){
        return "object[Logger] method called";
    }
};

//var Loggable = {
//    logger: function(){
//        this.logger = object(Log).init();
//        return this;
//    }
//}
