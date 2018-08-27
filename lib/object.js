// object.js 
//
//  - OSS的function生成
//  - 基本クラスの独自拡張
//  - logger設定

function object(o){
    var f = object.f,i,len,n,prop;
    f.prototype = o;
    n = new f;
    // Mixin
    for(i=1,len=arguments.length; i<len; ++i){
        for(prop in arguments[i]){
            n[prop] = arguments[i][prop];
        }
    }
    return n;
}
object.f = function(){};

Array.prototype.indexOf = function(v){
    for(var i in this) {
        if( this.hasOwnProperty(i) && this[i] == v){
            return i;
        }
    }
    return -1;
};

// 参照状態は参照状態のままとするシャロー(浅い)コピー
function naiveClone(obj){
    var n = {};
    for (var p in obj) {
        n[p] = obj[p];
    };
    return n;
}
