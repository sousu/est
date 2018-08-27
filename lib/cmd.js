var Cmd = {
    shell: WScript.CreateObject("WScript.Shell"),
    config: null,
    logger: null,
    gradual_mode: false,

    init: function(config,logger){
        this.config = config
        this.logger = (logger === undefined)?
            object(Logger).init() : logger;
        return this;
    },

    //TODO: 
    //  - 死活監視
    //     総ファイル数に対して余りにも時間がかかっている場合 KILL
    //     try/catchの利用など
    //  - パイプ詰まりTmpファイル対応はこっちに持ってくるべき
    //     in側パイプのsize4096詰まりが発生する
    //       但しOutと違い発行側の管理責任
    //     out側パイプのsize4096詰まりにより勝手に改行されてしまう

    exec: function(cmd,in_str){
        var output = ["",""];
        var exe = this.shell.Exec(cmd);
        if(in_str !== undefined){
            exe.StdIn.Write(in_str);
            exe.StdIn.Close();
        }
        while (!exe.StdOut.AtEndOfStream){
            var line = exe.StdOut.ReadLine()+"\n";
            if(this.gradual_mode) this.exe_gradual_func(line);
            output[0] += line;
        }
        while (!exe.StdErr.AtEndOfStream){
            var line = exe.StdErr.ReadLine()+"\n";
            if(this.gradual_mode) this.exe_gradual_func(line);
            output[1] += line;
        }
        return output;
    },

    gradual:function(func){
        this.gradual_mode = true;
        this.gradual_func = func;
    },

    exe_gradual_func: function(line){
        (this.gradual_func)? this.gradual_func(line) : print(line);
    },

    run: function(cmd){
        var ret = this.shell.run(cmd,0,true);
        return ret;
    }
};
