// err
function argument_check(max_num){
    return (WScript.Arguments.length > max_num)? false : true;
}
function argcntr(){
    if(WScript.Arguments.length < 2){
        return undefined;
    }else{ // 配列化
        var ary = new Array();
        for (var i=1; i<WScript.Arguments.length; i++) {
            ary.push(WScript.Arguments(i));
        }
        return ary;
    }
}
function err(s){
    throw new Error(0,s);
}
// filesystem
function getFullName(path){
    dir = String(WScript.ScriptFullName).replace(WScript.ScriptName,"");
    return dir+path;
}
function cd(){
    var fso    = WScript.CreateObject("Scripting.FileSystemObject");
    var wshell = WScript.CreateObject("WScript.Shell");
    wshell.CurrentDirectory = fso.GetFile(WScript.ScriptFullName).ParentFolder.Path;
}
// String
function println(s){
	WScript.echo(s);
}
function print(s){
    WScript.StdOut.Write(s);
}
function print_header(s){
	WScript.echo("");
    var len = 50;
    var join = function(s,n){
        var r = [];
        for(var i=n;--i>=0;) r.push(s);
        return r.join('');
    }
	WScript.echo("=== "+s+" "+join("=",len-s.length));
}
function print_mini_header(s){
    WScript.echo("---- "+s+" ----");
}
function concatString(){
    var str = "";
    return function(s){
        if(s!==undefined) str = str+s+"\n";
        return str;
    }
}
function now(){
    var date = new Date();
    var y = date.getYear();
    var m = date.getMonth() + 1;
    var d = date.getDate();
    var hour = date.getHours();
    var minuite = date.getMinutes();
    var sec = date.getSeconds();
    if(m < 10) m = '0' + m; 
    if(d < 10) d = '0' + d; 
    if(hour < 10) hour = '0' +hour; 
    if(minuite < 10) minuite = '0' +minuite;
    if(sec < 10) sec = '0' +sec;
    var n = y + "/" + m + "/" + d + " " + hour + ":" + minuite + ":" + sec;
    return n;
}
